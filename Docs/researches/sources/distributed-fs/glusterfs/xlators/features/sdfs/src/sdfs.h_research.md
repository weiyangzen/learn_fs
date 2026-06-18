# sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs.h

## Purpose
`sdfs.h` declares the private call-state structures and stack-destroy helper used by the `sdfs` dentry serializer translator.

## Important APIs, types, and functions
`SDFS_LOCK_COUNT_MAX` fixes the maximum number of entry locks at two, matching rename-style operations. `sdfs_entry_lock_t` stores a parent `loc_t`, a basename, and a small `locked` array. `sdfs_lock_t` contains up to two entry-lock records and the active count. `sdfs_local_t` is the per-frame context: original `main_frame`, copied target and parent locations, pending `call_stub_t`, optional lock array, operation status, and atomic callback count. `SDFS_STACK_DESTROY(frame)` detaches `frame->local`, unreferences the client, destroys the stack root, and calls `sdfs_local_cleanup()`.

## Control flow and state
This header is tightly coupled to `sdfs.c`: public FOPs allocate `sdfs_local_t` from `this->local_pool`; callbacks inspect `stub`, `main_frame`, and `call_cnt`; cleanup frees copied locations, stubs, lock arrays, and the local object. No persistent state is declared here.

## Dependencies and integration points
It includes `glusterfs/call-stub.h`, `glusterfs/atomic.h`, and `sdfs-messages.h`, and assumes GlusterFS core types such as `loc_t`, `call_frame_t`, and `gf_atomic_t`.

## Risks and test signals
The nested `locked[SDFS_LOCK_COUNT_MAX]` array inside each entry record is unusual because common callback code indexes through `locks->entrylk->locked[index]`; reviewers should verify that this models intended per-lock status. `SDFS_STACK_DESTROY` assumes a valid `frame->root->client`, so callers must not install NULL clients in copied frames. Tests should target cleanup after partial lock acquisition and ensure all copied loc/stub resources are released.
