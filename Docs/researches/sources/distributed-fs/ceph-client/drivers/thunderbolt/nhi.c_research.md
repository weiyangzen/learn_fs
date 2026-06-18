<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.c` is the PCI driver for the Thunderbolt/USB4 Native Host Interface. It owns host-controller probing, interrupt setup, NHI DMA rings, NHI mailbox commands, controller quirks, host-router reset, and system/runtime PM handoff to the Thunderbolt domain. The source was read as a complete 1585-line file.

## Important APIs, Types, and Functions

Exported ring APIs are `tb_ring_alloc_tx()`, `tb_ring_alloc_rx()`, `tb_ring_start()`, `tb_ring_stop()`, `tb_ring_free()`, `__tb_ring_enqueue()`, `tb_ring_poll()`, and `tb_ring_poll_complete()`. Firmware mailbox APIs are `nhi_mailbox_cmd()` and `nhi_mailbox_mode()`. Internal ring plumbing includes `ring_write_descriptors()`, `ring_work()`, `ring_interrupt_active()`, `ring_msix()`, `nhi_interrupt_work()`, `ring_request_msix()`, and `nhi_alloc_hop()`. PCI/PM flow is rooted in `nhi_probe()`, `nhi_remove()`, `nhi_init_msi()`, `nhi_reset()`, `nhi_select_cm()`, and the `nhi_pm_ops` callbacks. Static state includes the `host_reset` module parameter and NHI-local quirk bits `QUIRK_AUTO_CLEAR_INT` and `QUIRK_E2E`.

## Control Flow

Probe rejects invalid firmware images, enables the PCI function, maps BAR0, reads `REG_CAPS` for hop count, allocates TX/RX ring pointer arrays, applies quirks, checks DMA protection, optionally resets the host router, initializes MSI-X or MSI, sets a 64-bit DMA mask, runs generation-specific ops, selects either native software connection management or ICM, and finally adds the Thunderbolt domain. Ring allocation builds coherent descriptor memory, optionally requests an MSI-X vector, and reserves a HopID. Starting a ring writes descriptor base/count/options registers, enables raw or frame mode, optionally enables end-to-end flow control, unmasks interrupts, and marks the ring running.

At interrupt time MSI-X handlers clear only the ring-specific source and drive `__ring_interrupt()`, while shared MSI schedules `nhi_interrupt_work()` to scan TX, RX, and RX-overflow notify bitfields. Rings either schedule `ring_work()` for callback-driven completion or call a polling starter and mask the interrupt until `tb_ring_poll_complete()`. `ring_work()` moves completed descriptors from `in_flight` to a local done list, posts queued descriptors, then invokes callbacks outside the spinlock. Stop disables the hardware ring, clears descriptor/options registers, marks queued/in-flight frames canceled, and flushes work.

## State and Persistence Behavior

Runtime state lives in `struct tb_nhi`, per-ring `struct tb_ring`, coherent descriptor arrays, IDA-allocated MSI-X vectors, and PCI/MMIO registers. There is no file-backed persistence. State crosses sleep through PM callbacks that delegate to `tb_domain_*` and optional `tb_nhi_ops`; resume re-enables interrupt throttling and handles controllers that disappear while suspended by setting `going_away`. The `host_reset` module parameter persists for the loaded module lifetime and controls whether v2+ host routers are reset during probe.

## Dependencies and Integration Points

This file integrates with Linux PCI, DMA, IRQ, runtime PM, IOMMU/property APIs, `tb_domain_*`, `tb_probe()`, `icm_probe()`, ACPI native control checks, and generation-specific `icl_nhi_ops`. Register definitions come from `nhi_regs.h`; public IDs/ops come from `nhi.h`; domain and ring data structures come from `tb.h`. Consumers of ring APIs include Thunderbolt control, XDomain, DMA tunnels, and other protocol paths that exchange frames over NHI HopIDs.

## Risks and Edge Cases

High-risk areas are interrupt masking/clearing differences between Intel auto-clear and other routers, the Falcon Ridge E2E HopID workaround, concurrent callback and stop/free ordering, controllers disappearing during suspend, host-router reset timing, and fallback from MSI-X to single MSI. DMA protection detection is heuristic and segment based. Ring callbacks may reenqueue or free frames, so holding frame pointers after callbacks is unsafe. HopID allocation must avoid reserved IDs and must unwind on failures.

## Test Signals

Useful signals include boot/probe on supported PCI IDs, MSI-X and MSI fallback coverage, ring enqueue/completion under TX/RX load, `start_poll` polling users, suspend/resume/runtime PM with connected and disconnected devices, hot-unplug during sleep, `host_reset=0/1`, DMA/IOMMU protection logging, and fault injection around IRQ allocation, DMA allocation, mailbox timeout, and domain add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.c -->
