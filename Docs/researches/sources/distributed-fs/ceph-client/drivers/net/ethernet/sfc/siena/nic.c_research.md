# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic.c

## Purpose

`nic.c` provides generic Siena/Falcon-architecture NIC support that is not tied to one queue operation: coherent DMA buffer helpers, interrupt request/free, self-test event/IRQ triggers, ethtool register dump sizing and collection, generic stats description/conversion, and correction of no-descriptor drop statistics.

## Important APIs, Types, and Functions

`efx_siena_alloc_buffer()` and `efx_siena_free_buffer()` allocate/free coherent DMA buffers used by interrupt status, stats, PTP sync flags, and similar firmware/hardware shared areas. Self-test helpers are `efx_siena_event_present()`, `efx_siena_event_test_start()`, and `efx_siena_irq_test_start()`.

Interrupt lifecycle is handled by `efx_siena_init_interrupt()` and `efx_siena_fini_interrupt()`. Register dump support is built from local `struct efx_nic_reg`, `struct efx_nic_reg_table`, `efx_nic_regs[]`, and `efx_nic_reg_tables[]`, with public `efx_siena_get_regs_len()` and `efx_siena_get_regs()`. Stats helpers are `efx_siena_describe_stats()`, `efx_siena_update_stats()`, and `efx_siena_fix_nodesc_drop_stat()`.

## Control Flow

Interrupt initialization first distinguishes legacy from MSI/MSI-X. Legacy mode requests one shared IRQ using the NIC type's legacy handler. MSI/MSI-X mode optionally allocates an RX CPU rmap for accelerated RFS, then requests one IRQ per channel using stable `efx_msi_context` entries. On failure, it frees the rmap and any IRQs already hooked. Finalization mirrors that path and clears `efx->irqs_hooked`.

Register dumping computes length by filtering static register and register-table lists against `efx->type->revision`. Collection reads single oword registers and table rows using access size implied by the table stride: 32-bit SRAM, 64-bit SRAM, 128-bit table entries, or interleaved 128-bit entries.

Stats conversion iterates an enabled mask, skips unnamed or width-zero entries as appropriate, reads little-endian 16/32/64-bit DMA fields from a stats buffer, and either stores or accumulates into caller-provided counters. No-descriptor drop correction subtracts drops observed while the netdev is down or on the first update after coming up.

## State and Persistence Behavior

This file mutates coherent buffer descriptors, `efx->irqs_hooked`, `net_dev->rx_cpu_rmap`, `last_irq_cpu`, per-channel `event_test_cpu`, and no-descriptor drop accounting fields. Register dump state is read-only hardware state. Stats conversion writes caller-owned arrays but does not allocate. Interrupt handlers themselves are supplied by the NIC type table.

## Dependencies and Integration Points

It depends on PCI DMA APIs, Linux IRQ APIs, optional `CONFIG_RFS_ACCEL` CPU rmap APIs, local bitfield/register definitions, `io.h` register accessors, and `struct efx_nic_type` callbacks. It integrates with self-tests, ethtool `get_regs`, stats collection, probe/open/close interrupt setup, and MCDI MAC stats allocation.

## Risks and Test Signals

Interrupt setup can partially succeed; failure unwind must match exactly the IRQ count already requested. RFS rmap setup adds another failure point after IRQ registration. Register dump tables intentionally skip write-only/read-clear/huge regions; changes to hardware register definitions need revision guards updated. Stats DMA width mismatches can corrupt ethtool output. Tests should cover legacy/MSI/MSI-X request failures, RFS rmap failures, ethtool register length vs payload size, stats conversion for all widths, and no-descriptor drops across interface down/up transitions.
