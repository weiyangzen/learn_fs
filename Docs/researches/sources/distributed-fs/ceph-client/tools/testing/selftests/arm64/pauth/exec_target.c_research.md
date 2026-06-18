# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/exec_target.c

## Purpose

`exec_target` is the worker process used by `pac.c` to sign a value after `exec()`. Its output lets the parent compare pointer-authentication keys before and after exec.

## Important APIs, Types, and Functions

`main()` reads one `size_t` from stdin, checks `AT_HWCAP`, signs the value with `keyia_sign()`, `keyib_sign()`, `keyda_sign()`, `keydb_sign()`, and optionally `keyg_sign()`, then writes `struct signatures` to stdout.

## Control Flow and Data Flow

The parent sends a value through a pipe. The child reads it, signs it with all supported keys, fills unsupported generic output with zero, and writes the binary structure back. There is no text protocol.

## State and Persistence Behavior

The program is stateless beyond process-local PAC keys created by the kernel during exec. It stores no files.

## Dependencies and Integration Points

It depends on `helper.h`, auxv `HWCAP_PACA` and `HWCAP_PACG`, stdin/stdout pipes, and the parent `exec_sign_all()` routine in `pac.c`.

## Risks and Edge Cases

The caller is expected to have checked feature support; missing `HWCAP_PACA` leaves four structure fields uninitialized before write, though the normal parent skips without PACA. Short input causes a failure exit.

## Test Signals

The parent treats nonzero exit, short read/write, or unchanged signatures across exec as failure signals.
