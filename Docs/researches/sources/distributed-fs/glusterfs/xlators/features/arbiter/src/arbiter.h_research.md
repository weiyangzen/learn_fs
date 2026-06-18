<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.h -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.h

## Purpose
Private arbiter translator header defining the per-inode context shape.

## APIs, Types, and Functions
Includes `glusterfs/iatt.h` and defines `arbiter_inode_ctx_t`, which currently stores only one `struct iatt iattbuf`.

## Control Flow, State, and Persistence
No control flow. The struct is allocated in inode ctx on lookup, read by short-circuit write-like FOPs, and freed during forget. It is volatile memory state only.

## Dependencies and Integration
Used by `arbiter.c` and paired with `arbiter-mem-types.h` for allocation accounting.

## Risks and Test Signals
Risk is that a single cached stat buffer may be insufficient if future FOPs need richer metadata or xdata. Build coverage and behavior of cached pre/post attributes in arbiter write replies are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.h -->
