<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/switchtec.h -->
# sources/distributed-fs/ceph-client/include/linux/switchtec.h

## Purpose

`switchtec.h` defines register layouts and core device state for the Microsemi/Microchip Switchtec PCIe switch driver. It covers management RPC registers, software events, system/flash information, NTB registers, partition config, PFF CSR windows, DMA MRPC output, and the driver’s top-level `switchtec_dev`.

## Important APIs, types, and functions

Important constants include MRPC payload size, GAS region offsets, event bits, DMA MRPC enable, MRPC command IDs, NTB control bits, and event masks. Register structs include `mrpc_regs`, `sw_event_regs`, generation-specific `sys_info_regs_*`, `flash_info_regs_*`, `ntb_info_regs`, `part_cfg_regs`, `ntb_ctrl_regs`, `ntb_dbmsg_regs`, and `pff_csr_regs`, mostly packed to match MMIO layouts. `struct switchtec_dev` binds the PCI device, character device, generation, partition state, MMIO pointers, MRPC queue/work/timer state, event waitqueue/counters, link notifier, NTB state, and DMA MRPC buffer. `to_stdev()` converts from embedded `struct device`.

## Control flow

The driver maps GAS regions, initializes typed MMIO pointers, queues MRPC commands under `mrpc_mutex`, drives command work and timeout handling, receives event/interrupt indications from software or partition event registers, wakes waiters, and exposes management through a character device and optional NTB integration.

## State and persistence behavior

Hardware state persists in PCIe switch MMIO registers and flash partitions. Software state includes queue membership, `mrpc_busy`, delayed timeout work, `alive`, event counters, link event counts, and DMA buffer ownership. Flash/sys-info structs represent persistent firmware/configuration partitions.

## Dependencies and integration points

It depends on PCI and character-device infrastructure. It integrates with the Switchtec PCI driver, userspace management char device, DMA MRPC support, interrupt/event handling, and Switchtec NTB support.

## Risks and test signals

Risks include packed layout drift from hardware documentation, endian/MMIO access mistakes, MRPC queue races, timeout cleanup while device removal is in progress, generation-specific sys/flash layout confusion, and event bit clearing mistakes. Tests should validate structure offsets/sizes, MRPC success/error/timeout/interrupted paths, event masking/clearing, Gen3/Gen4/Gen5 identification, DMA MRPC, char-device lifetime, hot removal, and NTB register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/switchtec.h -->
