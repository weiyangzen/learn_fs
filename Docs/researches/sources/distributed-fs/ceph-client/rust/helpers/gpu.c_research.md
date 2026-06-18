# sources/distributed-fs/ceph-client/rust/helpers/gpu.c

## Purpose
Exposes GPU buddy allocator block inspection helpers to Rust when GPU buddy is enabled.

## APIs, Types, and Functions
Under `CONFIG_GPU_BUDDY`, wraps `gpu_buddy_block_offset()` and `gpu_buddy_block_order()`.

## Control Flow, State, and Persistence
No local state; reads properties from caller-owned `gpu_buddy_block` objects.

## Dependencies and Integration
Depends on `linux/gpu_buddy.h` and Rust graphics memory-manager code.

## Risks and Test Signals
Risks include config-dependent availability and stale block pointers after allocator mutations. Test signals are GPU buddy allocation/free tests and disabled-config builds.
