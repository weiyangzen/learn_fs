# Research: subset-b-005244

This grouped report covers the exact source files assigned to `subset-b-005244`. Each section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_cb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_cb.c

## Purpose
`bfa_ioc_cb.c` supplies the Crossbow/CB ASIC-specific implementation of the generic IOC hardware-interface table. It maps PCI function and port registers, checks firmware compatibility for multi-function coexistence, drives per-port firmware-state scratch registers, handles synchronized IOC failure cleanup through join bits, and initializes the CB PLL/reset state.

## Important APIs, Types, And Functions
The exported entry points are `bfa_ioc_set_cb_hwif()` and `bfa_ioc_cb_pll_init()`. `bfa_ioc_set_cb_hwif()` populates the static `hwif_cb` `struct bfa_ioc_hwif_s` with CB-specific callbacks. Internal callbacks include `bfa_ioc_cb_firmware_lock()`, `bfa_ioc_cb_firmware_unlock()`, `bfa_ioc_cb_reg_init()`, `bfa_ioc_cb_map_port()`, `bfa_ioc_cb_isr_mode_set()`, `bfa_ioc_cb_notify_fail()`, `bfa_ioc_cb_ownership_reset()`, `bfa_ioc_cb_sync_start()`, `bfa_ioc_cb_sync_join()`, `bfa_ioc_cb_sync_leave()`, `bfa_ioc_cb_sync_ack()`, `bfa_ioc_cb_sync_complete()`, and current/alternate firmware-state get/set helpers.

Static register maps `iocreg_fnreg[]` and `iocreg_mbcmd[]` translate PCI functions 0 and 1 to host/LPU mailbox windows, command/status registers, and host page-number registers. `bfa_ioc_cb_join_pos()` and `BFA_IOC_CB_JOIN_MASK`-based operations preserve failure-join bits in the same registers that carry `BFI_IOC_*` firmware states.

## Control Flow
Attach-time flow calls `bfa_ioc_set_cb_hwif()`, then generic IOC code invokes `ioc_map_port()` and `ioc_reg_init()`. CB maps `port_id` directly from the PCI function, selects heartbeat/current/alternate firmware-state registers by port, and maps the mailbox, PSS, PLL, semaphore, SRAM-page, and error-notification registers from BAR0.

Firmware lock flow reads current and alternate firmware states. If the current state is `BFI_IOC_UNINIT`, this driver can initialize firmware. Otherwise it reads the running firmware header with `bfa_ioc_fwver_get()` and compares it with the driver image through `bfa_ioc_fwver_cmp()`. A mismatch blocks initialization unless the alternate IOC is disabled.

Failure synchronization flow stores join/ack state in the high bits of the firmware-state registers. `sync_start()` clears stale join bits left by an unclean prior driver exit, otherwise delegates to `sync_complete()`. `sync_join()` sets this IOC's join bit, `sync_leave()` clears it, `sync_ack()` marks the current state as `BFI_IOC_FAIL`, and `sync_complete()` allows reset/recovery when this IOC or the alternate IOC is in a safe state such as `UNINIT`, `INITING`, `DISABLED`, `MEMTEST`, `OP`, or `FAIL` depending on the path.

`bfa_ioc_cb_pll_init()` clears firmware states while preserving join bits, masks and clears host interrupts, pulses SCLK/LCLK soft-reset and bypass bits, programs PLL control values, waits with `udelay()`, clears pending interrupts again, and releases PLL logic reset. It returns `BFA_STATUS_OK`.

## State And Persistence
The file persists no kernel-owned long-term state beyond assigning `ioc->ioc_hwif` and filling `ioc->ioc_regs`. Persistent coordination is through hardware registers: per-IOC firmware-state registers, join bits, host semaphores, mailbox windows, interrupt mask/status registers, PLL control registers, and the error-set register. `bfa_ioc_cb_ownership_reset()` carefully reads the semaphore before writing `1` so it clears a held semaphore instead of accidentally acquiring an unlocked one.

## Dependencies And Integration Points
This file depends on `bfad_drv.h`, `bfa_ioc.h`, `bfi_reg.h`, and `bfa_defs.h` for kernel helpers, IOC definitions, and register offsets/bit masks. It integrates directly with the generic IOC by filling `struct bfa_ioc_hwif_s`, and with firmware compatibility logic through `bfa_ioc_fwver_get()` and `bfa_ioc_fwver_cmp()`. Hardware notification of heartbeat failure is emitted by writing all ones to `err_set`.

## Risks And Test Signals
Key risks include stale join bits blocking later driver loads, firmware-state writes clobbering join bits, incorrect PCI-function indexing into two-entry register maps, and PLL sequencing regressions that leave the ASIC or firmware in an unbootable state. `bfa_ioc_cb_isr_mode_set()` is intentionally empty, so generic callers must tolerate no-op interrupt-mode switching on CB.

Good test signals include CB attach on both PCI functions, firmware mismatch detection when another function is active, recovery after unclean driver unload with join bits set, heartbeat failure propagation through `ERR_SET_REG`, semaphore cleanup correctness, firmware boot after `bfa_ioc_cb_pll_init()`, and mailbox command/response operation on both function register maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_ct.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_ct.c

## Purpose
`bfa_ioc_ct.c` implements Catapult/CT and Catapult2/CT2 ASIC-specific IOC hardware-interface behavior. It handles firmware usage-count locking, firmware-state and failure-sync registers shared across functions, port and mailbox register mapping, interrupt-mode selection for CT, CT2 LPU read-status handling, CT2 MSI-X vector-table workaround, and PLL/clock/NFC/flash/MAC/memory reset sequences.

## Important APIs, Types, And Functions
The exported hardware-interface entry points are `bfa_ioc_set_ct_hwif()`, `bfa_ioc_set_ct2_hwif()`, `bfa_ioc_ct2_poweron()`, `bfa_ioc_ct_pll_init()`, and `bfa_ioc_ct2_pll_init()`. Shared CT-family callbacks include `bfa_ioc_ct_firmware_lock()`, `bfa_ioc_ct_firmware_unlock()`, `bfa_ioc_ct_notify_fail()`, `bfa_ioc_ct_ownership_reset()`, `bfa_ioc_ct_sync_start()`, `bfa_ioc_ct_sync_join()`, `bfa_ioc_ct_sync_leave()`, `bfa_ioc_ct_sync_ack()`, `bfa_ioc_ct_sync_complete()`, and firmware-state get/set helpers.

CT-specific helpers are `bfa_ioc_ct_reg_init()`, `bfa_ioc_ct_map_port()`, and `bfa_ioc_ct_isr_mode_set()`. CT2-specific helpers are `bfa_ioc_ct2_reg_init()`, `bfa_ioc_ct2_map_port()`, `bfa_ioc_ct2_lpu_read_stat()`, `bfa_ioc_ct2_sclk_init()`, `bfa_ioc_ct2_lclk_init()`, `bfa_ioc_ct2_mem_init()`, `bfa_ioc_ct2_mac_reset()`, `bfa_ioc_ct2_enable_flash()`, NFC halt/resume/wait helpers, `bfa_ioc_ct2_clk_reset()`, and `bfa_ioc_ct2_nfc_clk_reset()`.

Static tables `ct_fnreg[]`, `ct_p0reg[]`, `ct_p1reg[]`, and `ct2_reg[]` map PCI functions or logical ports to mailbox and command/status offsets. The `ioc_fail_sync` register is split into low acknowledge bits and high required bits via `bfa_ioc_ct_get_sync_ackd()`, `bfa_ioc_ct_get_sync_reqd()`, and `bfa_ioc_ct_sync_reqd_pos()`.

## Control Flow
Attach-time flow for CT calls `bfa_ioc_set_ct_hwif()`, which first fills shared CT-family operations through `bfa_ioc_set_ctx_hwif()` and then assigns CT PLL, register-init, port-map, and ISR-mode callbacks. CT maps port ID from the function-personality register and maps mailbox command/status to LPU0 or LPU1 depending on the resolved port. CT2 follows the same shared setup but uses CT2 register offsets, maps the port from `CT2_HOSTFN_PERSONALITY0`, installs `bfa_ioc_ct2_lpu_read_stat()`, and leaves `ioc_isr_mode_set` as `NULL`.

Firmware locking serializes on `ioc_usage_sem_reg`. If use count is zero, the first driver sets use count to one, releases the semaphore, clears failure-sync state, and can initialize firmware. If firmware is already in use, the code rejects mismatched firmware images and increments the use count only when `bfa_ioc_fwver_cmp()` succeeds. Unlock decrements the use count under the same semaphore and warns on invalid counts.

Failure synchronization uses `ioc_fail_sync`. `sync_join()` records that this function requires coordinated failure handling; `sync_ack()` records that this function has acknowledged failure; `sync_complete()` waits until required and acknowledged masks match, then clears acknowledged bits and writes `BFI_IOC_FAIL` to both current and alternate firmware states. It also handles a race where another function reinitialized and failed again while this IOC was waiting for the hardware semaphore by reasserting this function's ack bit.

CT PLL init programs FC or FCoE operating mode, resets firmware-state registers, masks/clears interrupts, enables SCLK/LCLK PLLs, optionally resets PMM for non-FC mode, releases LMEM reset, and runs EDRAM BIST. CT2 PLL init branches on WGN/NFC state: it may reset clocks directly, enable flash, reset MACs, wait for NFC firmware to run and ask it to reset PLLs, or halt NFC and perform manual clock/MAC reset. It also applies an ATC DMA-read workaround, masks mailbox interrupts, clears stale command status after prior initialization, initializes memory, and marks both CT2 IOC states uninitialized.

## State And Persistence
Persistent coordination is almost entirely in hardware registers: firmware use count, usage/init semaphores, failure-sync bitmaps, firmware-state registers, mailbox windows, LPU halt registers, personality registers, PLL controls, NFC status/control registers, flash GPIO controls, interrupt masks/status, and SRAM-page registers. Kernel-side state is the selected static hardware-interface table and register pointers stored in `ioc->ioc_regs`.

The use-count lock is a reference-counting contract across PCI functions sharing firmware. Failure-sync bits persist across unclean exits until `sync_start()` or ownership reset clears them. `bfa_ioc_ct2_poweron()` persists MSI-X vector count/offset defaults in host function vector-table registers when firmware/ASIC block configuration did not set them.

## Dependencies And Integration Points
The file depends on the same IOC and register headers as the CB implementation: `bfad_drv.h`, `bfa_ioc.h`, `bfi_reg.h`, and `bfa_defs.h`. It integrates with generic IOC state machines through `struct bfa_ioc_hwif_s`, with firmware-image validation through `bfa_ioc_fwver_get()`/`bfa_ioc_fwver_cmp()`, and with IOC personality through `bfa_ioc_is_cna()` and `bfa_ioc_pcifn()`. It is the chip-policy layer that lets generic mailbox, heartbeat, and boot code operate against CT/CT2 register layouts.

## Risks And Test Signals
Risks include use-count leaks on failed attach/detach, firmware mismatch handling races under the usage semaphore, failure-sync bit races across multiple PFs, incorrect CT port mapping from personality bits, CT2 register-table indexing by port rather than function, and PLL/NFC reset paths that depend on exact hardware status values. The CT2 ATC workaround and MSI-X vector workaround are hardware errata-sensitive and should not be reordered casually. Several waits use fixed `udelay()` polling with `WARN_ON()` rather than recoverable errors, so failures may surface as boot instability rather than clean status codes.

Good test signals include CT attach on PF0-PF3, CT2 attach on both ports, concurrent function firmware sharing with matching and mismatched images, use-count decrement on detach, failure recovery when one function fails while another is active, CT interrupt-mode switching between INTx/MSI-X, CT2 LPU read-status clearing, CT/CT2 firmware boot after PLL init in FC and FCoE/CNA modes, and recovery from stale `ioc_fail_sync` bits after an unclean prior unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_modules.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_modules.h

## Purpose
`bfa_modules.h` defines the aggregate BFA driver object and the collection of service modules embedded in it. It is the structural bridge between IOC/IOCFC core state, Fibre Channel service modules, port services, diagnostics, configuration, and the upper `bfad` driver instance.

## Important APIs, Types, And Functions
`struct bfa_modules_s` embeds instances of the driver's major modules: FC diagnostics, FC port, FC exchange, login services, unsolicited frame handling, remote port handling, FCP initiator, SG page management, physical port, ASIC block config, CEE, SFP, flash, diagnostics, PHY, driver config, and FRU. `struct bfa_s` is the top-level BFA object and contains the `bfad` back pointer, port log pointer, trace module, `struct bfa_ioc_s`, `struct bfa_iocfc_s`, timer module, embedded modules, completion queue, request-queue wait queues, FCS attachment flag, MSI-X information, AEN sequence, and interrupt-enabled state.

The header also declares module attach, memory-info, start, and IOC-disable functions for DCONF, FCP, FCPIM, FCPORT, FCXP, FCDIAG, IOIM low-memory init, LPS, RPORT, SGPG, and UF modules. `bfa_auto_recover` is declared as an external module-level policy flag.

## Control Flow
The header has no executable control flow, but it defines initialization ordering and ownership. The enclosing driver allocates or embeds one `struct bfa_s`, initializes IOC/IOCFC/timer/completion state, calls each module's `*_meminfo()` to size memory, claims memory, attaches modules with shared `struct bfa_iocfc_cfg_s` and PCI information, and then starts selected services. On IOC disable/failure, the aggregate object lets the driver notify modules through their `*_iocdisable()` functions.

## State And Persistence
All state is in-memory driver state. Persistent hardware or firmware state is reached through embedded module objects rather than by this header directly. `struct bfa_s` preserves runtime queues, module pending state, callback-bearing module instances, and adapter event sequencing for the lifetime of a BFA instance. The declared trace enum values are version-sensitive because the comments require appending only, preserving trace utility compatibility.

## Dependencies And Integration Points
The file includes `bfa_cs.h`, `bfa.h`, `bfa_svc.h`, `bfa_fcpim.h`, and `bfa_port.h`, which bring in the service-module definitions that are embedded in `struct bfa_modules_s`. It is included wherever the driver needs the complete `struct bfa_s` layout. Integration points are the attach/meminfo/iocdisable APIs consumed by the BFA initialization and teardown paths.

## Risks And Test Signals
Risks include structure-layout churn affecting modules that assume embedded ownership, initialization-order mistakes where a module uses IOC or DMA memory before attach/memclaim, and trace enum reordering that breaks external trace interpretation. Since `struct bfa_s` aggregates many modules, broad changes here have a high build and runtime blast radius.

Good test signals include full driver probe/remove, IOC disable/failure fanout to all declared modules, memory sizing/claiming for minimal and full configurations, MSI-X setup with request queues, trace decoding compatibility, and no uninitialized embedded module use during attach failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_modules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_plog.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_plog.h

## Purpose
`bfa_plog.h` defines the fixed-size per-port circular log used by the BFA driver to capture driver, HAL, FCS, login, FC exchange, unsolicited-frame, IOC, port, CT, RSCN, FIP, trunking, and debug events. It provides record formats, module/event IDs, string-length contracts, and logging function prototypes.

## Important APIs, Types, And Functions
Important constants are `BFA_PL_NLOG_ENTS` (256 records), `BFA_PL_STRING_LOG_SZ` (32 bytes), `BFA_PL_INT_LOG_SZ` (8 integers), `BFA_PL_SIG_LEN`, and `BFA_PL_SIG_STR`. `enum bfa_plog_log_type` distinguishes invalid, integer, and string log records. `struct bfa_plog_rec_s` is the fixed record layout with timestamp, source port, module ID, event ID, log type, integer count, misc field, and a union of string or integer payload. `enum bfa_plog_mid` and `enum bfa_plog_eid` define stable numeric IDs for log producers and events.

`struct bfa_plog_s` is the ring buffer: signature, enabled flag, ticks, head/tail indexes, and 256 records. Public APIs are `bfa_plog_init()`, `bfa_plog_str()`, `bfa_plog_intarr()`, `bfa_plog_fchdr()`, and `bfa_plog_fchdr_and_pl()`.

## Control Flow
The header establishes the expected logging flow. Initialization writes the signature and clears/sets ring state. Producers call the string, integer-array, FC-header, or FC-header-plus-payload helper with a module ID, event ID, misc value, and payload. The ring advances through `BFA_PL_LOG_REC_INCR()`, which wraps indexes modulo `BFA_PL_NLOG_ENTS`.

## State And Persistence
Port-log state is volatile in-memory state attached to `struct bfa_s` through `bfa->plog`. The buffer is fixed-size and circular, so old records are overwritten as head/tail advance. The signature and ID/string enum ordering form a compatibility contract with BFAL or other user/debug tooling that decodes numeric module and event values.

## Dependencies And Integration Points
The header includes `bfa_fc.h` for FC header structures and `bfa_defs.h` for shared driver definitions. Logging helpers integrate with FC frame paths, IOCTL/debug paths, FCS, LPS, and HAL modules that pass module/event IDs. The comments explicitly require appending new module/event IDs and defining corresponding strings in BFAL, indicating an external decoder dependency.

## Risks And Test Signals
Risks include enum reordering/removal breaking log decoders, string payload truncation to 32 bytes, integer payload truncation to eight words, ring overwrite hiding older failures, and concurrent producers needing implementation-side synchronization not visible in this header. FC header logging must respect byte ordering and structure layout when implemented.

Good test signals include plog initialization signature checks, wraparound at 256 records, logging while disabled/enabled, decoder compatibility for existing module/event IDs, string and integer record boundary tests, and FC header logging from TX/RX paths with expected misc length fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_plog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.c

## Purpose
`bfa_port.c` implements the physical port service module and the CEE service module for the BFA driver. The physical port half handles firmware mailbox requests for port enable, port disable, port statistics retrieval, statistics clearing, IOC event cleanup, DMA-backed stats buffers, and D-port/PBC gating. The CEE half handles firmware mailbox requests for CEE attributes, CEE statistics, and CEE statistics reset.

## Important APIs, Types, And Functions
Physical port public APIs are `bfa_port_meminfo()`, `bfa_port_mem_claim()`, `bfa_port_enable()`, `bfa_port_disable()`, `bfa_port_get_stats()`, `bfa_port_clear_stats()`, `bfa_port_notify()`, `bfa_port_attach()`, and `bfa_port_set_dportenabled()`. Internal helpers include `bfa_port_stats_swap()`, enable/disable/stat ISR completion helpers, and `bfa_port_isr()`.

CEE public APIs are `bfa_cee_meminfo()`, `bfa_cee_mem_claim()`, `bfa_cee_get_attr()`, `bfa_cee_get_stats()`, `bfa_cee_reset_stats()`, and `bfa_cee_attach()`. Internal CEE helpers include `bfa_cee_get_attr_isr()`, `bfa_cee_get_stats_isr()`, `bfa_cee_reset_stats_isr()`, `bfa_cee_isr()`, and `bfa_cee_notify()`.

The file uses BFI mailbox payloads such as `struct bfi_port_generic_req_s`, `struct bfi_port_get_stats_req_s`, `union bfi_port_i2h_msg_u`, `struct bfi_cee_get_req_s`, `struct bfi_cee_reset_stats_s`, `struct bfi_cee_get_rsp_s`, and `union bfi_cee_i2h_msg_u`. It exchanges data through DMA objects embedded in `struct bfa_port_s` and `struct bfa_cee_s`.

## Control Flow
Port attach initializes `struct bfa_port_s`, registers `bfa_port_isr()` for `BFI_MC_PORT`, adds an IOC notification callback, and initializes the stats reset timestamp. Memory setup computes one aligned stats buffer with `bfa_port_meminfo()` and stores its KVA/physical address in `bfa_port_mem_claim()`.

Port enable and disable first reject operations if PBC disabled, IOC disabled, IOC non-operational, D-port enabled, or another enable/disable is pending. On success they fill `port->endis_mb`, store callback context, set `endis_pending`, build a `BFI_PORT_H2I_ENABLE_REQ` or `BFI_PORT_H2I_DISABLE_REQ` header with the IOC port ID, and queue the mailbox through `bfa_ioc_mbox_queue()`. Firmware responses enter `bfa_port_isr()`, which ignores stale responses if the pending flag is already clear, then clears the flag and invokes the stored callback.

Stats retrieval checks IOC operational state and `stats_busy`, stores the caller's stats buffer and callback context, writes the DMA address into the request, and queues `BFI_PORT_H2I_GET_STATS_REQ`. Completion copies from the module's DMA buffer into the caller's buffer, swaps 32-bit pairs to host order with `bfa_port_stats_swap()`, computes `secs_reset` from `ktime_get_seconds()` and `stats_reset_time`, clears busy, and calls back. Stats clear queues `BFI_PORT_H2I_CLEAR_STATS_REQ`; completion refreshes `stats_reset_time`, clears busy, and calls back.

IOC disable/failure notification fails any outstanding port stats or enable/disable operation with `BFA_STATUS_FAILED`, clears callbacks and pending flags, and clears D-port state. CEE attach similarly registers `bfa_cee_isr()` for `BFI_MC_CEE` and adds an IOC notification callback. CEE get-attr/get-stats/reset-stats each enforce IOC operational state and one outstanding operation of the same type, fill the appropriate mailbox command, set callback context, and queue it. CEE ISR dispatches firmware responses by message ID, copies DMA payloads on success, performs limited endian conversion, clears pending state, and invokes callbacks.

## State And Persistence
The port module maintains pending-operation state in `stats_busy`, `endis_pending`, callback fields, status fields, `stats_reset_time`, `pbc_disabled`, and `dport_enabled`. DMA-backed stats are transient: firmware writes into `port->stats_dma.kva`, and completion copies into the caller-supplied `union bfa_port_stats_u`. `secs_reset` is derived from kernel time and is not firmware-persistent.

CEE state tracks independent pending flags and statuses for get-attr, get-stats, and reset-stats, plus callback contexts and DMA buffers for attributes/statistics. The implementation has no on-disk persistence; firmware/adapter state is reached through BFI mailbox commands.

## Dependencies And Integration Points
The file includes `bfad_drv.h`, `bfa_defs_svc.h`, `bfa_port.h`, `bfi.h`, and `bfa_ioc.h`. It integrates tightly with IOC mailbox dispatch (`bfa_ioc_mbox_regisr()`, `bfa_ioc_mbox_queue()`), IOC health checks (`bfa_ioc_is_disabled()`, `bfa_ioc_is_operational()`), IOC notification queues, DMA address formatting (`bfa_dma_be_addr_set()`), and BFI message classes `BFI_MC_PORT` and `BFI_MC_CEE`.

## Risks And Test Signals
Risks include stale firmware responses after local timeout/failure, callbacks invoked while upper layers are tearing down, incorrect endianness conversion for port and CEE stats, single-pending-operation busy semantics surprising callers, null callback handling for enable/disable paths, and inconsistent cleanup if IOC failure races with mailbox ISR completion. `bfa_cee_get_attr()` and `bfa_cee_get_stats()` overwrite `cee->attr` and `cee->stats` with caller buffers after `bfa_cee_mem_claim()` initially points them at DMA memory; the ISR copies from DMA KVA into those caller buffers, so callers must keep buffers valid until callback.

Good test signals include enable/disable success and failure callbacks, PBC-disabled and D-port-enabled rejection, IOC disabled/non-operational rejection, duplicate request `BFA_STATUS_DEVBUSY`, stale response ignored after failure cleanup, stats DMA copy and endian conversion validation, `secs_reset` behavior after clear, IOC failure completing all pending port and CEE operations with `BFA_STATUS_FAILED`, and CEE LLDP field endian conversion for `time_to_live` and `enabled_system_cap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.h

## Purpose
`bfa_port.h` declares the physical port and CEE service-module interfaces used by the BFA driver. It defines callback types, per-module state structures, DMA memory accessor macros, and public operations for port stats, port enable/disable, D-port state, CEE attributes, CEE statistics, and CEE stats reset.

## Important APIs, Types, And Functions
Physical port callback types are `bfa_port_stats_cbfn_t` and `bfa_port_endis_cbfn_t`. `struct bfa_port_s` stores the device pointer, IOC pointer, trace module, message tag, stats busy/callback/status fields, stats reset timestamp, caller stats buffer, stats DMA memory, enable/disable pending/callback/status fields, IOC notification entry, PBC/D-port flags, and module DMA segment descriptor. Public port prototypes are `bfa_port_attach()`, `bfa_port_notify()`, `bfa_port_get_stats()`, `bfa_port_clear_stats()`, `bfa_port_enable()`, `bfa_port_disable()`, `bfa_port_meminfo()`, `bfa_port_mem_claim()`, and `bfa_port_set_dportenabled()`.

CEE callback types are `bfa_cee_get_attr_cbfn_t`, `bfa_cee_get_stats_cbfn_t`, and `bfa_cee_reset_stats_cbfn_t`. `struct bfa_cee_cbfn_s` groups callback pointers and arguments. `struct bfa_cee_s` stores device and IOC pointers, pending/status fields for each operation, callbacks, IOC notification, trace module, caller/DMA pointers for attributes and stats, mailbox commands, and module DMA segment descriptor. Public CEE prototypes are `bfa_cee_meminfo()`, `bfa_cee_mem_claim()`, `bfa_cee_attach()`, `bfa_cee_get_attr()`, `bfa_cee_get_stats()`, and `bfa_cee_reset_stats()`.

## Control Flow
The header establishes asynchronous flow. Callers attach each module to an IOC, claim DMA memory sized by the `*_meminfo()` functions, then issue one operation at a time per busy flag. Operations return immediate `bfa_status_t` values for admission failures and later invoke callbacks for firmware completions. IOC events enter `bfa_port_notify()` and the CEE notify helper in the implementation to fail pending work.

## State And Persistence
All state is runtime memory owned by `struct bfa_port_s` and `struct bfa_cee_s`. Persistent adapter effects are indirect: port enable/disable changes firmware port state, stats clear resets firmware counters, and CEE reset clears firmware-side CEE stats. The header's timestamp field records when port stats were last reset in host time.

## Dependencies And Integration Points
The header includes `bfa_defs_svc.h`, `bfa_ioc.h`, and `bfa_cs.h`. It integrates with `struct bfa_modules_s` through `BFA_MEM_PORT_DMA()` and `BFA_MEM_CEE_DMA()` macros and with the IOC through mailbox commands, notification entries, and DMA address structures. Service data types such as `union bfa_port_stats_u`, `struct bfa_cee_attr_s`, and `struct bfa_cee_stats_s` come from the service definitions header.

## Risks And Test Signals
Risks include caller lifetime mistakes for asynchronous buffers/callback arguments, assuming multiple concurrent stats or enable/disable operations are supported, stale `pbc_disabled`/`dport_enabled` policy flags blocking expected port operations, and DMA memory not being claimed before issuing firmware requests. Since the header exposes internal module structures, layout changes can affect many compile units.

Good test signals include compile coverage of all module users, attach/memclaim before operation, one-operation-at-a-time admission behavior, callback invocation on success and IOC failure, D-port/PBC gating, CEE attr/stats/reset workflows, and DMA alignment matching `bfa_port.c` and CEE implementation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.h -->
