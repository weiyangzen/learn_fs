<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_via.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_via.c

## Purpose

This is the libata PCI driver for VIA VT6420, VT6421, and VT8251 SATA/PATA controllers. It handles multiple register layouts, optional VT6420 hotplug, VT6421 mixed SATA/PATA ports, VT8251 master/slave SATA slots, and known VIA/drive FIFO workarounds.

## Important APIs, types, and functions

`struct svia_priv` records whether the WD FIFO watermark workaround is active. Port operations are split across `svia_base_ops`, `vt6420_sata_ops`, `vt6421_pata_ops`, `vt6421_sata_ops`, and `vt8251_ops`. Important helpers include `svia_scr_read/write()`, `vt8251_scr_read/write()`, `svia_tf_load()`, `svia_noop_freeze()`, `vt6420_prereset()`, `vt6420_bmdma_start()`, VT6421 PATA mode/cable helpers, `vt642x_interrupt()`, `vt6421_error_handler()`, `svia_configure()`, and the three prepare-host functions.

## Control flow

Probe validates BAR sizes, selects a host-preparation path by board ID, allocates `svia_priv`, programs channel enable, interrupt gate, native mode, hotplug, and FIFO workaround bits, then activates with either generic BMDMA IRQ handling or `vt642x_interrupt()` for hotplug-capable paths. VT6420 carefully restricts SCR access to a boot-time prereset sequence to avoid hangs. VT6421 maps two SATA ports and one PATA port from six BARs. VT8251 exposes two channels with slave links and reads SCRs from packed PCI config bytes/dwords.

## State and persistence behavior

Runtime state is PCI config programming, optional module parameter `vt6420_hotplug`, private WD workaround state, and libata port/link state. Resume reapplies the WD workaround when it had been enabled. There is no durable state.

## Dependencies and integration points

The file depends on PCI config access, generic libata BMDMA/SFF helpers, SCSI command metadata for ATAPI DMA workaround, and `linux/string_choices.h` for link-state messages. It integrates mixed PATA/SATA ports under one PCI driver.

## Risks

VT6420 SCR access can hang hardware if used outside the safe sequence; enabling hotplug mutates the shared operations table and should be treated carefully. VT6421 WD-drive errors enable a throughput-reducing FIFO workaround after detecting a specific SError. Interrupt handling reads SError for hotplug only after generic BMDMA returns unhandled. PCI BAR validation is strict and can reject odd firmware layouts.

## Test signals

Exercise all board IDs, VT6420 with and without `vt6420_hotplug`, VT6421 SATA plus PATA timing/cable detection, VT8251 slave-link enumeration, suspend/resume with workaround state, ATAPI burner DMA writes, and hotplug PHYRDY events. Expected signals include safe VT6420 probing, correct link-up/down dmesg, and no machine hangs from SCR access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_via.c -->
