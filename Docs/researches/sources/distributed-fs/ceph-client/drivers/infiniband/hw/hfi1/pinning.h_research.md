# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pinning.h

## Purpose
`pinning.h` is the small public header for the HFI1 system-memory pinning layer. It exposes the queue lifecycle hooks and packet-population helper used by user SDMA code without leaking the private mmu-rb cache node layout.

## Important APIs, Types, And Functions
The header forward-declares `hfi1_user_sdma_pkt_q`, `user_sdma_request`, `user_sdma_txreq`, and `user_sdma_iovec`. `hfi1_init_system_pinning()` installs per-queue MMU invalidation support, `hfi1_free_system_pinning()` removes it, and `hfi1_add_pages_to_sdma_packet()` pins/maps bytes from user iovecs into an SDMA tx request while updating request progress.

## Control Flow
Callers initialize pinning when a user SDMA packet queue is created, call `hfi1_add_pages_to_sdma_packet()` while building each packet from user iovecs, and free pinning during queue teardown. The header intentionally keeps all cache, kref, and eviction details private to `pin_system.c`.

## State And Persistence
No state is defined in the header. State lives in the queue's hidden handler and private cache nodes created by the implementation. The API implies lifecycle ordering: packet additions are valid only after init and before free.

## Dependencies And Integration Points
This header integrates user SDMA request building with the system pinning implementation and is included by code that needs to submit user-backed pages to SDMA. It depends on `u32` being visible from prior includes or kernel type headers.

## Risks
Because the header only forward declares types, misuse is mostly lifecycle-related: calling the packet helper without a registered handler or after teardown would fail in implementation paths. The `u32 *pkt_data_remaining` output contract must remain synchronized with user SDMA callers.

## Test Signals
Compile coverage should catch prototype drift. Runtime tests should verify queue init/free ordering, packet helper error propagation, and correct progress updates across partial iovec consumption.
