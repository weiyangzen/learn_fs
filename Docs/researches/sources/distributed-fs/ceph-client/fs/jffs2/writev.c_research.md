# sources/distributed-fs/ceph-client/fs/jffs2/writev.c

## Purpose

`writev.c` provides direct MTD write helpers for JFFS2 when no write buffer is needed, and it also records summary metadata for direct writes. It is the direct-write backend selected by `os-linux.h` or by `wbuf.c` when write-buffering is disabled.

## Important APIs, Types, And Functions

`jffs2_flash_direct_writev()` optionally calls `jffs2_sum_add_kvec()` for non-writebuffered summary collection, then writes the kvec array through `mtd_writev()`. `jffs2_flash_direct_write()` writes a contiguous buffer through `mtd_write()` and, when summaries are active, wraps the buffer in a single `struct kvec` and records it through `jffs2_sum_add_kvec()`.

## Control Flow

Callers normally use `jffs2_flash_writev()` or `jffs2_flash_write()`. In non-writebuffered builds those names are macros to these direct helpers; in write-buffered builds, `wbuf.c` may still delegate here when `jffs2_is_writebuffered(c)` is false. Summary collection occurs before `mtd_writev()` in the vector path and after `mtd_write()` in the single-buffer path.

## State And Persistence Behavior

The direct helpers persist bytes immediately to MTD and set the caller-provided `retlen`. They do not themselves link raw node refs or adjust eraseblock accounting; callers in `write.c`, `summary.c`, and nodemgmt do that after checking write success. Summary collection updates in-memory `c->summary` state for the current eraseblock.

## Dependencies And Integration Points

Dependencies are minimal: MTD `mtd_writev()`/`mtd_write()`, `struct kvec`, `jffs2_sum_active()`, and `jffs2_sum_add_kvec()`. The helpers are declared in `os-linux.h` and used by write and summary paths.

## Risks And Edge Cases

The order of summary collection differs between vector and single-buffer writes. In `jffs2_flash_direct_writev()`, summary collection can succeed and then the physical write can fail, leaving summary state for a node that did not persist unless higher layers disable/reset appropriately. In direct single writes, the helper can return a summary-add error after the MTD write has already occurred. These paths rely on callers' failure handling and summary reset/disable behavior.

## Test Signals

Tests should cover direct vector and single writes with summary enabled/disabled, MTD write errors and short writes, summary-add failures, and consistency between summary collection and raw-node accounting after higher-level retry or failure handling.
