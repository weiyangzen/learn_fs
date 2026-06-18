# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-mem-types.h

## Purpose

This header defines the POSIX translator memory accounting type IDs used with Gluster's `GF_MALLOC`, `GF_CALLOC`, and related allocation tracking.

## Important APIs, Types, and Functions

`enum gf_posix_mem_types_` starts at `gf_common_mt_end + 1` and includes allocation buckets for `posix_fd`, generic chars, `posix_private`, trash paths, POSIX AIO control blocks, inode contexts, mdata attributes, io_uring contexts, disk xlator structures, and the terminal `gf_posix_mt_end`.

## Control Flow

There is no runtime flow in this file. The enum is included by POSIX sources so allocations can be tagged for memory accounting and leak diagnostics.

## State and Persistence Behavior

No persistent state is written. The enum affects in-memory accounting and observability.

## Dependencies and Integration Points

It includes `glusterfs/mem-types.h` and must remain consistent with `mem_acct_init` in the translator. Allocation sites in the researched files use `gf_posix_mt_posix_fd`, `gf_posix_mt_char`, `gf_posix_mt_mdata_attr`, and `gf_posix_mt_uring_ctx`.

## Risks

IDs must not collide with common memory types and should not be reordered casually because memory accounting reports and downstream assumptions may depend on stable names. New POSIX allocation families need matching enum entries and mem accounting initialization.

## Test Signals

Build with memory accounting enabled, run POSIX translator allocation-heavy paths, and inspect stated allocation buckets for fd, xattr buffer, metadata, and io_uring context usage.
