# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_private.h

Purpose: Provides the private GSI interface shared only between `gsi.c` and `gsi_trans.c`. It exposes transaction state transitions, ring helpers, doorbell/update helpers, and TX accounting hooks without making them public to the wider IPA driver.

Important APIs/types: Defines `GSI_RING_ELEMENT_SIZE` as 16 bytes, used for both channel TREs and event entries. Declares transaction transitions `gsi_trans_move_complete()`, `gsi_trans_move_polled()`, `gsi_trans_complete()`, mapping/lookup helpers, pending cancellation, transaction init/exit, `gsi_channel_doorbell()`, `gsi_channel_update()`, `gsi_ring_virt()`, and TX accounting hooks `gsi_trans_tx_committed()`/`gsi_trans_tx_queued()`.

Control flow and integration: `gsi_trans.c` uses the doorbell and update hooks implemented in `gsi.c` when committing or querying transactions. `gsi.c` uses transaction lookup and state transition helpers when handling events and NAPI polling. The header is the contract that keeps transaction mechanics and hardware event processing coordinated.

State and persistence: No state is defined here beyond the shared element-size constant. The declared functions mutate `struct gsi_channel` transaction cursors, ring indices, mapped transaction pointers, and TX accounting counters.

Dependencies: Includes only Linux types and forward declarations for GSI structs. It intentionally limits include spread and documents that only `gsi.c` and `gsi_trans.c` should include it.

Risks: This file’s boundary is fragile: exposing these helpers beyond the two implementation files would let callers bypass transaction invariants. `GSI_RING_ELEMENT_SIZE` must match hardware event/TRE struct sizes; mismatch is guarded by build-time checks in implementation files.

Test signals: Build should fail if event/TRE sizes diverge. Runtime signals include correct mapping from completion events to transactions, clean cancellation on channel reset, and TX queue/complete accounting matching network stack expectations.
