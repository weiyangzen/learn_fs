# sources/distributed-fs/ceph-client/drivers/ntb/msi.c

## Purpose
Provides a generic NTB MSI helper library. It reserves peer and inbound memory windows so a peer can trigger local MSI interrupts by writing the MSI data value into an NTB-mapped address, and it exposes helpers for clients to allocate IRQs, exchange descriptors, and trigger peer interrupts.

## Important APIs, Types, And Functions
- `struct ntb_msi` holds the mapped peer MSI windows, local accepted MSI address range, and an optional descriptor-change callback.
- `ntb_msi_init()` allocates `ntb->msi`, stores the callback, and maps the last peer MW for each peer.
- `ntb_msi_setup_mws()` reserves the highest inbound MW for every peer, aligns the first local MSI descriptor address to all peer MW constraints, programs translations, and records `[base_addr, end_addr)`.
- `ntb_msi_clear_mws()` clears those reserved inbound translations.
- `ntbm_msi_request_threaded_irq()` finds an unused PCI MSI descriptor, requests a managed IRQ, fills `struct ntb_msi_desc`, and installs a `write_msi_msg` hook to update the descriptor if the PCI MSI message changes.
- `ntb_msi_peer_trigger()` writes descriptor data into the mapped peer MSI window at `addr_offset / sizeof(u32)`.

## Control Flow
A client first calls `ntb_msi_init()`. On link up or after MSI allocation is valid, it calls `ntb_msi_setup_mws()` to make local MSI target addresses reachable from peers. The helper reads the first associated MSI descriptor under the MSI descriptor lock, aligns it for all peer highest-MW constraints, then programs each peer's highest inbound MW. Clients then allocate one or more IRQs through `ntbm_msi_request_threaded_irq()`, exchange the generated `ntb_msi_desc` out of band, and call `ntb_msi_peer_trigger()` with a peer descriptor to raise a remote interrupt.

If the PCI core rewrites an MSI message, `ntb_msi_write_msg()` refreshes the exported descriptor and calls the client's `desc_changed` callback, allowing the new descriptor to be sent to peers.

## State And Persistence
The library attaches transient state to `ntb->msi` using devm allocation. It persists peer MW ioremaps and the local MSI address window while the NTB device is alive. IRQ requests and callback resources are devres-managed. Descriptor contents are volatile and must be re-exchanged after setup, message changes, or link reset.

## Dependencies And Integration Points
Depends on the generic NTB MW APIs, PCI MSI descriptors, managed IRQ allocation, and `linux/msi.h`. It is used by `ntb_transport.c` when `CONFIG_NTB_MSI` and `use_msi` are enabled, and by `ntb_msi_test.c`.

## Risks And Edge Cases
- `ntb_msi_setup_mws()` assumes at least one associated MSI descriptor exists; a missing descriptor would make `msi_first_desc()` unsafe.
- The error unwind loop uses `ntb_peer_highest_mw_idx(ntb, peer)` while iterating `i`, which appears suspicious because `peer` is the failed peer value, not the cleanup index.
- `ntb_msi_peer_trigger()` does not range-check `peer`, descriptor offset, or peer window mapping; clients must validate exchanged descriptors.
- Stale descriptors after PCI MSI rewrites can trigger the wrong address/data unless the client handles `desc_changed`.
- The helper reserves highest MWs, so clients must subtract or avoid those MWs.

## Test Signals
`ntb_msi_test` is the direct functional test: peers should exchange descriptors through scratchpads and debugfs `trigger` should increment peer interrupt occurrence counters. `ntb_transport` with `use_msi=1` validates integration with queue interrupts. Build coverage needs `CONFIG_NTB_MSI`.
