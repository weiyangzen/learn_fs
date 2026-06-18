<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc.h

## Purpose
`bfa_ioc.h` is the central IOC-facing contract header for the QLogic/Brocade BR-series Fibre Channel driver. It defines generic BFA timer, DMA/memory-segment, scatter-gather, PCI, mailbox, callback, notification, IOC state-machine, IOCPF state-machine, firmware-image, debug, and hardware-interface abstractions. It also declares the module-private interfaces for IOC-attached services such as SFP, flash, diagnostics, PHY, FRU, driver configuration, and ASIC block configuration.

## Important APIs, Types, And Functions
Important generic types include `struct bfa_timer_s`, `struct bfa_timer_mod_s`, `struct bfa_sge_s`, `struct bfa_mem_dma_s`, `struct bfa_mem_kva_s`, `struct bfa_meminfo_s`, `struct bfa_pcidev_s`, `struct bfa_dma_s`, `struct bfa_ioc_regs_s`, `struct bfa_mbox_cmd_s`, `struct bfa_ioc_mbox_mod_s`, `struct bfa_ioc_notify_s`, `struct bfa_reqq_wait_s`, and `struct bfa_cb_qe_s`. The IOC core is modeled by `struct bfa_ioc_s`, `struct bfa_iocpf_s`, `struct bfa_ioc_hwif_s`, `enum ioc_event`, `enum iocpf_event`, and `enum bfa_ioc_event_e`.

The header exposes the mailbox API (`bfa_ioc_mbox_queue()`, `bfa_ioc_mbox_register()`, `bfa_ioc_mbox_isr()`, `bfa_ioc_mbox_send()`, `bfa_ioc_msgget()`, `bfa_ioc_mbox_regisr()`), IOC lifecycle and query APIs (`bfa_ioc_attach()`, `bfa_ioc_detach()`, `bfa_ioc_pci_init()`, `bfa_ioc_enable()`, `bfa_ioc_disable()`, `bfa_ioc_boot()`, `bfa_ioc_isr()`, `bfa_ioc_error_isr()`, `bfa_ioc_is_operational()`, `bfa_ioc_get_state()`, `bfa_ioc_get_attr()`), debug/statistics APIs (`bfa_ioc_debug_fwsave()`, `bfa_ioc_debug_fwtrc()`, `bfa_ioc_debug_fwcore()`, `bfa_ioc_fw_stats_get()`, `bfa_ioc_fw_stats_clear()`), and ASIC-specific binding functions (`bfa_ioc_set_cb_hwif()`, `bfa_ioc_set_ct_hwif()`, `bfa_ioc_set_ct2_hwif()`, PLL init variants, and `bfa_ioc_ct2_poweron()`).

The service sections define state and prototypes for `struct bfa_ablk_s`, `struct bfa_sfp_s`, `struct bfa_flash_s`, `struct bfa_diag_s`, `struct bfa_phy_s`, `struct bfa_fru_s`, and `struct bfa_dconf_mod_s`. Firmware-image access is provided by extern image pointers/sizes and inline chunk helpers for CB, CT, and CT2 images.

## Control Flow
The header has no standalone executable flow, but it establishes the flow used by the IOC implementation. Driver attach initializes `bfa_ioc_s`, selects a hardware-interface table through the CB/CT/CT2 setters, maps PCI BAR registers into `bfa_ioc_regs_s`, claims DMA memory for attributes/debug state, and registers mailbox callbacks. Enable/disable/reset paths drive `ioc->fsm` and `ioc->iocpf.fsm` with `IOC_E_*` and `IOCPF_E_*` events, while the hardware-interface callbacks abstract firmware locking, PLL init, firmware-state reads/writes, cross-function failure synchronization, ownership reset, and interrupt-mode handling.

Mailbox flow is centralized around `struct bfa_mbox_cmd_s` queues and per-message-class handlers in `bfa_ioc_mbox_mod_s`. Service modules build BFI mailbox commands, queue them through IOC, and receive firmware responses through the registered message-class callback. Completion back into upper layers is represented by callback types such as `bfa_ioc_enable_cbfn_t`, `bfa_cb_flash_t`, `bfa_cb_diag_t`, `bfa_cb_phy_t`, and `bfa_cb_fru_t`.

## State And Persistence
Most state is volatile kernel driver state: queue heads, pending mailbox commands, callback pointers, DMA cursors, per-module busy flags, firmware heartbeat counters, saved firmware trace/core buffers, adapter attributes, current port mode/configuration, and AEN sequence counters. Hardware-visible persistence is limited to MMIO registers selected through `bfa_ioc_regs_s`, firmware-state scratch registers, semaphore/use-count registers, and flash/FRU/SFP/PHY operations delegated to firmware. `struct bfa_dconf_s` describes a persistent driver-configuration blob with signature/version, LUN masking, and throttle settings, but this header only defines the layout and API; flash access is implemented elsewhere.

DMA helpers require aligned, preclaimed memory. `bfa_mem_dma_setup()` and `bfa_mem_kva_setup()` append non-empty segments to `bfa_meminfo_s` lists, and tag-to-buffer macros compute request buffer addresses from segment tags. Endianness conversion helpers (`bfa_sge_to_be()`, `bfa_sge_to_le()`, `bfa_dma_be_addr_set()`, `bfa_alen_set()`) are part of the persistence contract between host memory and firmware ABI.

## Dependencies And Integration Points
The header depends on `bfad_drv.h`, `bfa_cs.h`, and `bfi.h`, and indirectly on the BFA definitions, firmware BFI ABI, PCI BAR mapping, Linux lists, timers, and endian helpers. It is included by the CB/CT chip-specific files, port/CEE services, module aggregation header, and many BFA service modules. `struct bfa_ioc_hwif_s` is the main integration point between generic IOC state machines and ASIC-generation-specific register policy in `bfa_ioc_cb.c` and `bfa_ioc_ct.c`.

## Risks And Test Signals
Risks are concentrated in ABI-sensitive layout, endianness, and state-machine contracts. The packed DCONF structures, firmware image chunk offsets, DMA address formatting, and BFI mailbox payload assumptions must remain synchronized with firmware. Misconfigured hardware-interface callbacks can leave semaphores locked, report the wrong firmware state, or break cross-function failure recovery. Busy flags and callback fields in the service modules are single-outstanding-operation contracts; callers that assume concurrency can receive `BFA_STATUS_DEVBUSY` or lose completion ordering.

Good test signals include clean builds across endian configurations, IOC enable/disable/reset under all CB/CT/CT2 paths, mailbox registration and response dispatch by message class, DMA segment alignment checks, firmware-version mismatch handling, heartbeat failure recovery, debug trace/core extraction, flash/FRU/PHY/SFP operation completion, and no stale callbacks after IOC disable/failure notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc.h -->
