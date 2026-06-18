# Research: subset-b-005247

This grouped report covers the QLogic/Broadcom FCoE offload driver and one adjacent BFA register header. Each section is source-path aligned for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi_reg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi_reg.h

## Purpose

`bfi_reg.h` is a hardware register definition header for QLogic/Brocade BR-series Fibre Channel adapter ASICs. It contains MMIO offsets and bit-field masks/shifts for host function interrupt registers, PLL control, host semaphores, LPU command/status and mailbox registers, PSS control, personality registers, Catapult-2 register remaps, interrupt bit assignments, firmware heartbeat/state semaphores, queue-number helpers, and PSS scratch-memory paging helpers.

The file has no executable functions. Its purpose is to be a stable hardware ABI map consumed by the BFA/BNA low-level driver code that reads and writes adapter registers.

## Important APIs, Types, and Definitions

Important groups include `HOSTFN*_INT_STATUS`, `HOSTFN*_INT_MSK`, and `HOST_PAGE_NUM_FN*` for per-function interrupt and paging control; `APP_PLL_LCLK_CTL_REG`, `APP_PLL_SCLK_CTL_REG`, and `CT2_APP_PLL_*` with masks for PLL reset/load/lock/rate fields; `HOST_SEM*` and `HOST_SEM*_INFO_REG` for firmware/driver semaphore state; `HOSTFN*_LPU*_CMD_STAT`, `LPU*_HOSTFN*_CMD_STAT`, and mailbox register offsets for host-to-LPU command exchange; `PSS_CTL_REG`, `PSS_ERR_STATUS_REG`, GPIO, LMEM, and LPU reset bits for processor subsystem control; `FNC_PERS_REG` and `CT2_HOSTFN_PERSONALITY*` for function mode, VF/PF, port mapping, INTx, and FC personality fields; and `__HFN_INT_*` masks for CPE/RME queues, mailbox interrupts, and error sources.

The only function-like macros are field composers such as `__APP_PLL_LCLK_RESET_TIMER(_v)`, `__F3_PORT_MAP(_v)`, `CPE_Q_NUM(__fn, __q)`, `RME_Q_NUM(__fn, __q)`, `PSS_SMEM_PGNUM(_pg0, _ma)`, and `PSS_SMEM_PGOFF(_ma)`.

## Control Flow

There is no local control flow. Runtime users choose ASIC-family-specific offsets, program PLL/reset registers, poll lock/ready bits, claim semaphores, post mailbox commands, map function interrupts to CPE/RME queues, and page into PSS scratch memory through these constants. The comments mark older `cb/ct` registers versus `ct` or `ct2`-specific registers, so caller control flow must select the correct family before issuing MMIO.

## State and Persistence Behavior

The file stores no state. It names persistent hardware state held in adapter registers: firmware heartbeat and state semaphores, firmware use count, fail synchronization state, queue interrupt state, mailbox state, PLL lock state, NFC/flash controller state, and PSS memory paging. These values persist in the device until firmware, reset, or power-cycle changes them.

## Dependencies and Integration Points

The header integrates with BFA IOC initialization, reset, interrupt, mailbox, firmware-state, and memory-window code. It depends only on preprocessor definitions and does not include Linux headers. Because it represents register layout, it indirectly depends on the ASIC programming guide and firmware expectations.

## Risks and Edge Cases

The main risk is silent hardware breakage from a wrong offset, mask, or shift. Several names are reused across ASIC generations, and CT2 moved semaphore and interrupt registers, so callers must not mix CT and CT2 constants. Some masks use raw register-endian numeric values; users must handle MMIO access width and endian conversion consistently. The `__APP_PLL_LCLK_FBCNT(_v)` macro references the SCLK shift name, which may be intentional if shifts match but deserves caution because PLL programming mistakes can prevent firmware startup.

## Test Signals

Useful validation is hardware probe on each supported ASIC family, firmware boot completion, heartbeat/state register transitions, mailbox round trips, interrupt delivery for each function and queue group, CT2-specific semaphore reads, PLL lock polling, PSS scratch-memory access, and fault injection for LPU/PSS/LL halt interrupt bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/57xx_hsi_bnx2fc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/57xx_hsi_bnx2fc.h

## Purpose

`57xx_hsi_bnx2fc.h` defines the host-side interface shared by the `bnx2fc` driver and 57xx/B577xx FCoE firmware. It describes the exact little-endian work-queue elements, completion entries, doorbells, task context entries, scatter-gather contexts, connection database, hash-table entries, and statistics records used for FCoE offload.

This is a firmware ABI header. The driver fills these structures in `bnx2fc_hwi.c`, passes KWQEs to CNIC, maps task contexts and queues for DMA, and decodes CQ/KCQ entries returned by firmware.

## Important APIs, Types, and Definitions

Core hardware-visible types include `struct b577xx_doorbell_hdr`, `struct b577xx_doorbell_set_prod`, and `struct b577xx_fcoe_rx_doorbell` for SQ/CQ doorbells; `struct regpair` for 64-bit DMA addresses split into little-endian low/high fields; `struct fcoe_bd_ctx` for DMA buffer descriptors; `struct fcoe_sqe`, `struct fcoe_cqe`, `struct fcoe_xfrqe`, and `struct fcoe_confqe` for SQ, CQ, transfer, and confirmation queues; `struct fcoe_conn_db` for per-connection producer/arm state; and `struct fcoe_task_ctx_entry` for the firmware task context.

Slow-path firmware messages are represented by `struct fcoe_kwqe_init1/2/3`, `struct fcoe_kwqe_conn_offload1/2/3/4`, `struct fcoe_kwqe_conn_enable_disable`, `struct fcoe_kwqe_conn_destroy`, `struct fcoe_kwqe_destroy`, `struct fcoe_kwqe_stat`, and `union fcoe_kwqe`. Completion messages use `struct fcoe_kcqe`.

FCP and ELS payload context is described by `struct fcoe_fc_hdr`, `struct fcoe_fcp_rsp_payload`, `union fcoe_comp_flow_info`, `union fcoe_tx_wr_rx_rd_union_ctx`, `union fcoe_rx_wr_union_ctx`, `struct fcoe_tce_tx_wr_rx_rd`, `struct fcoe_tce_rx_wr_tx_rd`, and related cached/multiple SGE context structures. Statistics use `struct fcoe_statistics_params`.

## Control Flow

During adapter initialization, the driver fills init KWQEs with queue sizes, task-context PBL addresses, hash-table addresses, HSI version, and error bitmaps. During session offload, it submits four connection-offload KWQEs that point firmware at SQ/RQ/CQ/XFERQ/CONFQ/LCQ/connection database memory and describe FC IDs, VLAN, MAC addresses, payload sizes, sequence counts, and recovery support. Enable, disable, destroy, and stat operations each use their corresponding KWQE.

Fast-path I/O uses a task context entry indexed by XID. The driver initializes FCP command, SGL, task type, device type, class, context ID, expected RX state, and sequence state, posts an SQE with the XID/toggle bit, and rings the doorbell. Firmware returns CQEs referencing task IDs, unsolicited frames, or error reports; higher-level code decodes the union fields according to task type and RX state.

## State and Persistence Behavior

No software state is stored in this header, but the structures define persistent DMA state visible to firmware: task contexts, per-connection queues, producer/consumer indices, request buffers, hash-table chains, and statistics buffers. Endianness annotations are part of the persistence contract; firmware expects little-endian values even on big-endian host builds with conditional struct layout for doorbells and connection database fields.

## Dependencies and Integration Points

This header is included by `bnx2fc.h` and consumed mainly by `bnx2fc_hwi.c`, `bnx2fc_io.c`, `bnx2fc_tgt.c`, and `bnx2fc_els.c`. It integrates with CNIC KWQ/KCQ submission, PCI DMA coherent allocations, libfc/libfcoe FCP and ELS flows, and bnx2x doorbell MMIO. Constants in `bnx2fc_constants.h` provide opcode and state values used with these layouts.

## Risks and Edge Cases

Any structure size, field order, bit shift, or endian mistake can desynchronize driver and firmware. The ABI uses many packed bitfields expressed as masks over integers, so callers must use the correct shift and must not assume CPU-endian interpretation. Several unions overlay unrelated contexts; the active interpretation depends on task type and completion state. Queue toggle-bit handling and ring wrap must match firmware exactly. DMA address truncation would be catastrophic because many call sites cast 64-bit DMA addresses into low/high fields manually.

## Test Signals

Useful validation includes firmware init completion with HSI 2.1, successful session offload/enable/disable/destroy KCQEs, correct SQ/CQ/RQ wrap and toggle behavior under load, FCP read/write with one, two, and many SGEs, ELS and task-management middle-path commands, unsolicited ELS frames, error-report CQEs, statistics requests, big-endian build coverage, and DMA API debugging for all coherent buffers referenced by these structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/57xx_hsi_bnx2fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/Kconfig

## Purpose

`Kconfig` declares the `SCSI_BNX2X_FCOE` tristate option, displayed as `QLogic FCoE offload support`. It enables building the `bnx2fc` offload initiator driver for QLogic/Broadcom NetXtreme II devices.

## Important APIs, Types, and Definitions

The option depends on `PCI`, `LIBFC`, and `LIBFCOE`. It selects `NETDEVICES`, `ETHERNET`, `NET_VENDOR_BROADCOM`, and `CNIC`. The help text states that the driver supports FCoE offload for QLogic devices.

## Control Flow

There is no runtime control flow. Build-system control flow is simple: when `CONFIG_SCSI_BNX2X_FCOE` is set to `m` or `y`, the Makefile builds the `bnx2fc` composite object and the driver can register as an FCoE transport and CNIC ULP.

## State and Persistence Behavior

The file persists only kernel configuration state. That state controls whether the driver is absent, built into the kernel, or built as a module.

## Dependencies and Integration Points

This config entry integrates the SCSI, Fibre Channel, FCoE, PCI, Ethernet, Broadcom, and CNIC subsystems. The `select CNIC` is important because runtime firmware communication is through the Broadcom CNIC ULP interface.

## Risks and Edge Cases

The option depends on libfc/libfcoe but selects lower networking prerequisites. If CNIC or bnx2x runtime support is unavailable even though the option builds, probe/create paths still fail. Because the symbol name contains `BNX2X` while the module is `bnx2fc`, users may miss the association when configuring kernels.

## Test Signals

Build matrix coverage should include `n`, `m`, and built-in configurations, with `LIBFC`, `LIBFCOE`, and `CNIC` dependency resolution. Runtime signals include module load, CNIC registration, and successful FCoE controller creation on a supported bnx2x netdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/Makefile

## Purpose

`Makefile` wires the `SCSI_BNX2X_FCOE` configuration symbol to the `bnx2fc` kernel object and lists the source objects that form the driver.

## Important APIs, Types, and Definitions

`obj-$(CONFIG_SCSI_BNX2X_FCOE) += bnx2fc.o` declares the composite module/object. `bnx2fc-y` includes `bnx2fc_els.o`, `bnx2fc_fcoe.o`, `bnx2fc_hwi.o`, `bnx2fc_io.o`, `bnx2fc_tgt.o`, and `bnx2fc_debug.o`.

## Control Flow

The kernel build system links the listed objects into `bnx2fc.o` when the config symbol is enabled. The object order puts ELS and lifecycle code before hardware, I/O, target, and debug objects, but Linux symbol resolution does not require source-order execution.

## State and Persistence Behavior

No runtime state is stored. The file persists build composition and therefore controls whether cross-file symbols such as `bnx2fc_queuecommand`, `bnx2fc_rport_event_handler`, hardware helpers, and debug functions are present in the final module.

## Dependencies and Integration Points

The Makefile integrates the driver with the SCSI driver build tree. It assumes the six listed source files plus headers in the directory and relative network-driver headers are available.

## Risks and Edge Cases

Omitting any object breaks link-time dependencies: `bnx2fc_fcoe.o` supplies module init, CNIC callbacks, and SCSI/libfc templates; `bnx2fc_hwi.o` supplies firmware and queue handling; `bnx2fc_io.o` and `bnx2fc_tgt.o` supply SCSI and rport behavior; `bnx2fc_els.o` supplies ELS helpers; and `bnx2fc_debug.o` supplies variadic debug functions. Any new source file must be added here or its symbols will be missing.

## Test Signals

Useful validation is `make M=drivers/scsi/bnx2fc`, allmodconfig/link coverage, module load/unload, and ensuring `modinfo bnx2fc` reflects the metadata from `bnx2fc_fcoe.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc.h

## Purpose

`bnx2fc.h` is the central private header for the QLogic/Broadcom FCoE offload driver. It gathers Linux, SCSI, libfc, libfcoe, FC, firmware-HSI, CNIC, and bnx2x firmware request headers; defines driver limits and constants; declares global state; defines the main HBA, interface, remote-port, command, command-manager, middle-path, and work structures; and exposes cross-file function prototypes.

## Important APIs, Types, and Definitions

Driver identity and limits include `BNX2FC_NAME`, `BNX2FC_VERSION`, queue sizes, maximum BDs, maximum sessions, NPIV limits, FCoE payload/MFS sizes, XID ranges, LUN/target limits, command length, task-management timeout, firmware timeout, retry counts, and logging/statistics helpers.

`struct bnx2fc_hba` is per-adapter state: CNIC/PPCI/netdev pointers, command manager, locks, adapter flags, XID/task limits, firmware task-context and hash-table DMA memory, dummy/statistics buffers, active offloaded target list, firmware stats, destroy/shutdown waits, and NPIV vport list.

`struct bnx2fc_interface` binds an FCoE controller to a netdev/HBA and stores packet handlers, timer workqueue, VLAN/enabled state, and task-management timeout. `bnx2fc_from_ctlr()` and `bnx2fc_to_ctlr()` convert between the interface and embedded `fcoe_ctlr`.

`struct bnx2fc_rport` is per-offloaded remote-port/session state: libfc rport pointers, context doorbell base, connection/context IDs, source address, queue sizes and DMA-backed SQ/CQ/RQ/XFERQ/CONFQ/LCQ/connection DB memory, locks, active queues, flags, timers, and wait queues.

`struct bnx2fc_cmd` is the per-XID command object for SCSI, TMF, ABTS, ELS, cleanup, and sequence cleanup. It owns the SCSI command pointer, middle-path buffers, callback, timer work, completions, XID, firmware task pointer, BD table, FCP response state, retry counters, flags, and status fields.

The header declares the driver’s major interfaces: SCSI queueing and error handlers, firmware init/destroy/session KWQE helpers, doorbell and CQ processing, command allocation, ELS helpers, cleanup/ABTS/REC/SRR flows, task initialization, statistics, rport event handling, and debug functions.

## Control Flow

The header expresses the driver layering. `bnx2fc_fcoe.c` manages module lifecycle, FCoE controller creation, libfc/libfcoe callbacks, CNIC registration, and netdev events. `bnx2fc_hwi.c` uses HSI structures to allocate firmware resources, send KWQEs, initialize task contexts, process KCQ/CQ completions, ring doorbells, and handle unsolicited frames. `bnx2fc_io.c` and `bnx2fc_tgt.c` allocate commands and service SCSI/rport flows. `bnx2fc_els.c` issues ELS middle-path commands and recovery exchanges.

At runtime, libfc/SCSI callbacks obtain an HBA/interface/rport, allocate a `bnx2fc_cmd`, initialize a firmware task context through the helpers declared here, post an SQE, and complete via CQ/KCQ callbacks back into SCSI/libfc.

## State and Persistence Behavior

State is in-memory and DMA-visible, not disk-persistent. HBA state persists for a CNIC device lifetime, interface state persists for an FCoE controller/netdev lifetime, rport state persists while a remote session is offloaded, and command state persists for an XID lifetime. Flags in `adapter_state`, `hba->flags`, `interface->if_flags`, `tgt->flags`, and `io_req->req_flags` are central to coordination among timers, completions, link events, and teardown.

## Dependencies and Integration Points

The header integrates with the Linux SCSI mid-layer, FC transport, libfc exchange/discovery/FCP services, libfcoe FIP/FCoE encapsulation, netdevice packet handlers, PCI/DMA APIs, kernel threads/workqueues/timers, CNIC ULP callbacks, and bnx2x firmware capability headers. Relative includes into `../../net/ethernet/broadcom/...` bind this SCSI driver to Broadcom network-driver interfaces.

## Risks and Edge Cases

The broad shared state makes locking and lifetime rules critical. `hba_lock`, `hba_mutex`, `tgt_lock`, `cq_lock`, per-CPU work locks, refcounts, and wait queues must agree during link-down, session upload, error recovery, and CPU hotplug. Queue size constants must match firmware HSI limits. XID partitioning between FCP and ELS/TMF must stay within `max_tasks`. Several flags are numeric bit indexes, not masks, which is easy to misuse. The command structure combines SCSI, ELS, ABTS, and cleanup lifetimes, so callback paths must not double-release references.

## Test Signals

Useful validation includes module load/unload, FCoE controller create/destroy, link up/down, NPIV creation/destruction, session offload/upload, SCSI queueing with max SG and queue-depth limits, TMF/ABTS/cleanup paths, ELS recovery flows, CPU hotplug while completions are pending, debug logging by bitmask, and DMA leak/race checking under teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_constants.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_constants.h

## Purpose

`bnx2fc_constants.h` defines firmware HSI constants used by the FCoE offload flows. It pairs with `57xx_hsi_bnx2fc.h`: that file defines structure layout, while this file defines HSI version, KWQE/KCQE opcodes, completion status values, task states, task types, protocol constants, timer resolution, hash-table sizing, connection type, capability limits, and firmware error codes.

## Important APIs, Types, and Definitions

The HSI version is `FCOE_HSI_MAJOR_VERSION` 2 and `FCOE_HSI_MINOR_VERSION` 1. KWQE opcodes cover function init, connection offload parts 1-4, enable, disable, destroy connection, destroy function, and statistics. KCQE opcodes cover init/destroy/stat completions, offload/enable/disable/destroy connection completions, CQ event notification, and FCoE error events. Completion statuses include success, generic error, invalid opcode, context allocation/free failure, NIC error, wrong HSI version, and parity error.

Task constants define TX and RX states for normal operation, abort, warning/error, ABTS, exchange cleanup, sequence cleanup, and completion. Task types distinguish write, read, middle path, unsolicited, ABTS, exchange cleanup, and sequence cleanup. Device/class constants distinguish disk/tape and class 2/3. Error-code constants identify XFER, FCP_RSP, FCP_DATA, middle-path, ABTS, common, unsolicited, read/write, and timer faults.

## Control Flow

These constants drive switch statements and bitfield composition in `bnx2fc_hwi.c`, `bnx2fc_els.c`, and the I/O/target files. Init code places HSI version and opcodes in KWQEs; KCQE handling switches on response opcodes and status values; task initialization writes TX/RX task states and task types into firmware contexts; unsolicited error processing maps firmware error bits to REC/SRR/ABTS recovery decisions.

## State and Persistence Behavior

The constants themselves hold no state. They define the legal values for firmware-visible persistent DMA state in task contexts, queue entries, and completion records. Changing any value changes the hardware ABI.

## Dependencies and Integration Points

The file is included by `bnx2fc.h`, which makes the constants available to all driver objects. It depends conceptually on 57xx firmware and CNIC semantics. The error code values integrate with `fcoe_err_report_entry` bitmaps and recovery code in the completion path.

## Risks and Edge Cases

The largest risk is numeric drift from firmware. Wrong opcodes prevent initialization or session state changes. Wrong task states can strand commands in firmware or misclassify completions. Error-code handling is sparse: tape devices get REC/SRR recovery for selected errors, while disk or unrecognized errors fall back to ABTS. Timer resolution constants must match firmware expectations for E_D_TOV and REC_TOV. The HSI version must stay synchronized with firmware accepted by CNIC/bnx2x.

## Test Signals

Useful signals include wrong-HSI-version rejection, successful KWQE/KCQE handshakes for all opcodes, task-state transitions for read/write/TMF/ELS/ABTS/cleanup, REC/SRR behavior for tape error codes, fallback ABTS for unhandled errors, and firmware statistics/error reporting under injected FCoE protocol faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_debug.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_debug.c

## Purpose

`bnx2fc_debug.c` implements the driver’s formatted debug logging helpers for I/O, target/session, and HBA contexts. These helpers are gated by the global `bnx2fc_debug_level` module parameter and print through `shost_printk()` when enough SCSI host context is available.

## Important APIs, Types, and Functions

`BNX2FC_IO_DBG(const struct bnx2fc_cmd *io_req, const char *fmt, ...)` logs command-scoped messages when `LOG_IO` is enabled and prefixes them with the command XID. `BNX2FC_TGT_DBG(const struct bnx2fc_rport *tgt, const char *fmt, ...)` logs target/session messages when `LOG_TGT` is enabled and prefixes them with the remote port ID. `BNX2FC_HBA_DBG(const struct fc_lport *lport, const char *fmt, ...)` logs host/lport messages when `LOG_HBA` is enabled. All three use `struct va_format` and are annotated in the header with `__printf`.

## Control Flow

Each helper first checks the relevant bit in `bnx2fc_debug_level` with a likely-not-enabled fast path. If enabled, it formats the caller’s varargs. If the nested context has a valid `Scsi_Host`, it emits through `shost_printk(KERN_INFO, ...)`; otherwise it falls back to `pr_info("NULL ...")`. The helpers do not allocate memory or alter driver state.

## State and Persistence Behavior

The only state read is `bnx2fc_debug_level`, defined in `bnx2fc_fcoe.c` as a module parameter. Messages go to the kernel log; no driver state is persisted.

## Dependencies and Integration Points

The file includes `bnx2fc.h`, which supplies structures, log-bit definitions through `bnx2fc_debug.h`, `PFX`, and Linux printk APIs. It is linked by the Makefile and called throughout ELS, FCoE lifecycle, hardware completion, I/O, and target code.

## Risks and Edge Cases

Debug calls can run in atomic or lock-held contexts, so the functions must remain lightweight. They avoid dereferencing partial context by checking nested pointers, but they still read fields from objects whose lifetime must be protected by callers. Overly verbose debug logging can flood the kernel log, especially with `LOG_IO` under heavy I/O.

## Test Signals

Validation includes enabling each debug bit through the module parameter, confirming XID/port/host prefixes, calling helpers with NULL or partial contexts, checking no output when bits are disabled, and running under dynamic debug or lockdep to ensure logging does not introduce sleeping behavior in atomic paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_debug.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_debug.h

## Purpose

`bnx2fc_debug.h` declares the driver logging bitmask, lightweight ELS/MISC debug macros, and printf-checked debug helper prototypes.

## Important APIs, Types, and Definitions

Log bits are `LOG_IO`, `LOG_TGT`, `LOG_HBA`, `LOG_ELS`, `LOG_MISC`, and `LOG_ALL`. `bnx2fc_debug_level` is declared as an external module parameter. `BNX2FC_ELS_DBG(fmt, ...)` and `BNX2FC_MISC_DBG(fmt, ...)` are inline macros that call `pr_info()` only when their bits are enabled. Prototypes for `BNX2FC_IO_DBG`, `BNX2FC_TGT_DBG`, and `BNX2FC_HBA_DBG` use `__printf` attributes for format checking.

## Control Flow

The macros are simple conditional logging gates. The function prototypes route richer context-aware logging to `bnx2fc_debug.c`. The header is included at the end of `bnx2fc.h`, making all logging helpers available to the driver.

## State and Persistence Behavior

No state is owned here. The header exposes `bnx2fc_debug_level`, whose value persists as module/global runtime configuration until changed through sysfs/module parameter mechanisms.

## Dependencies and Integration Points

The header assumes kernel printk and compiler format-check support are available through earlier includes in `bnx2fc.h`. It is used across all bnx2fc implementation files for debugging session lifecycle, link events, I/O recovery, ELS exchanges, and miscellaneous FCoE L2 handling.

## Risks and Edge Cases

The ELS and MISC macros use raw `pr_info()` without host context, so messages may be harder to correlate on multi-adapter systems. Because they evaluate varargs only inside the conditional block, disabled logging is cheap. Format string mismatches for the function helpers are compile-time checked, but macro call sites rely on normal printk checking.

## Test Signals

Useful checks include building with `W=1` for format warnings, toggling each log bit, confirming `LOG_ALL` enables all categories, and exercising multi-HBA logs to ensure context-bearing helpers are used where correlation matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_els.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_els.c

## Purpose

`bnx2fc_els.c` implements ELS and middle-path recovery helpers for the offloaded FCoE driver. It sends selected ELS requests through firmware for offloaded sessions, converts firmware responses back into libfc frames, handles RRQ/REC/SRR recovery for aborted or lost exchanges, and hooks FLOGI/FDISC/LOGO responses to maintain FCoE source MAC state.

## Important APIs, Types, and Functions

Externally used functions include `bnx2fc_send_rrq()`, `bnx2fc_send_adisc()`, `bnx2fc_send_logo()`, `bnx2fc_send_rls()`, `bnx2fc_send_rec()`, `bnx2fc_send_srr()`, `bnx2fc_process_els_compl()`, and `bnx2fc_elsct_send()`. The central internal routine is `bnx2fc_initiate_els()`, which allocates an ELS command, allocates middle-path request/response buffers, fills FC headers, initializes firmware task context, starts optional timers, posts the SQE, links the command on `tgt->els_queue`, and rings the doorbell.

Completion callbacks include `bnx2fc_rrq_compl()`, `bnx2fc_l2_els_compl()`, `bnx2fc_srr_compl()`, and `bnx2fc_rec_compl()`. Fabric login/logout response wrappers are `bnx2fc_flogi_resp()` and `bnx2fc_logo_resp()`.

## Control Flow

ADISC, LOGO, and RLS frames intercepted from libfc are sent as firmware middle-path ELS commands. On completion, `bnx2fc_l2_els_compl()` builds a temporary FC frame from the firmware response header and payload, restores the original L2 OXID, and passes it to `bnx2fc_process_l2_frame_compl()` for libfc receive processing.

RRQ is used to retire resources for an aborted exchange. REC probes target exchange state for tape error recovery. If REC indicates a lost command, the code can allocate a replacement command and repost the same SCSI command after initiating cleanup of the original. If sequence initiative is local and data or response is missing, REC completion may trigger sequence cleanup and SRR. SRR completion accepts success, initiates ABTS on LS_RJT, and retries or aborts on timeout.

`bnx2fc_process_els_compl()` is called from the CQ completion path. It cancels command timers, removes the ELS command from active lists, copies firmware response header/payload length from the task context, invokes the registered callback, and drops the command reference.

`bnx2fc_elsct_send()` wraps libfc ELS/CT send. For FLOGI/FDISC it updates the FCoE data MAC from granted MAC, selected FCF FC-MAP, or default FC-FCoE MAC derivation before passing the response to libfc. For fabric LOGO it clears the MAC on successful response.

## State and Persistence Behavior

State is transient per ELS command and per original I/O reference. `struct bnx2fc_els_cb_arg` links a firmware ELS command with the original I/O, L2 OXID, retry offset, and callback. Original commands gain references while REC/SRR/RRQ is outstanding. Flags such as `BNX2FC_FLAG_ELS_TIMEOUT`, `BNX2FC_FLAG_SRR_SENT`, `BNX2FC_FLAG_CMD_LOST`, `BNX2FC_FLAG_ISSUE_ABTS`, and `BNX2FC_FLAG_IO_COMPL` coordinate recovery. FLOGI/LOGO response hooks update the persistent `fcoe_port->data_src_addr` via the FIP controller.

## Dependencies and Integration Points

The file integrates with libfc ELS structures and exchange callbacks, libfcoe FIP MAC selection, firmware task setup in `bnx2fc_hwi.c`, command allocation and cleanup/ABTS helpers from I/O/target code, SCSI command state for recovery decisions, and driver debug logging. It relies on `tgt->tgt_lock` around queue and reference transitions.

## Risks and Edge Cases

Timeout and completion races are high-risk. A timed-out ELS may already be completing, requiring flags and reference counts to prevent double cleanup. Several callbacks allocate frames or buffers in atomic context and may drop responses on allocation failure. REC/SRR behavior is specialized for tape and must avoid reposting commands after SCSI completion or ABTS initiation. `bnx2fc_initiate_els()` validates opcodes by range, but callers must provide payloads matching the opcode. Locking deliberately drops `tgt_lock` around recursive REC/SRR sends; state can change while unlocked.

## Test Signals

Useful tests include ADISC/LOGO/RLS on offloaded sessions, FLOGI granted-MAC and FC-MAP handling, fabric LOGO clearing MAC, ELS timeout with cleanup, RRQ after abort, tape REC/SRR recovery for lost FCP_RSP and lost data, SRR rejection fallback to ABTS, allocation-failure handling, link-down/session-not-ready rejection, and refcount leak checks under repeated recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_els.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_fcoe.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_fcoe.c

## Purpose

`bnx2fc_fcoe.c` is the lifecycle and integration core of the driver. It registers the FCoE transport and CNIC ULP callbacks, creates and destroys FCoE controllers over bnx2x netdevs, configures libfc/libfcoe and SCSI hosts, handles FIP/FCoE L2 transmit and receive for non-offloaded traffic, responds to netdev link events, manages NPIV vports, starts/stops firmware, maintains global HBA/interface lists, and owns module parameters and transport templates.

## Important APIs, Types, and Functions

Major entry points include module init/exit (`bnx2fc_mod_init()`, `bnx2fc_mod_exit()`), CNIC callbacks (`bnx2fc_ulp_init()`, `bnx2fc_ulp_exit()`, `bnx2fc_ulp_start()`, `bnx2fc_ulp_stop()`, `bnx2fc_indicate_netevent()`), FCoE transport operations (`bnx2fc_create()`, `bnx2fc_destroy()`, `bnx2fc_enable()`, `bnx2fc_disable()`, `bnx2fc_ctlr_alloc()`, `bnx2fc_match()`), and SCSI/FC transport callbacks through `bnx2fc_shost_template`, `bnx2fc_transport_function`, `bnx2fc_vport_xport_function`, `bnx2fc_fcoe_sysfs_templ`, and `bnx2fc_libfc_fcn_templ`.

Important helpers include `bnx2fc_xmit()`, `bnx2fc_rcv()`, `bnx2fc_l2_rcv_thread()`, `bnx2fc_recv_frame()`, `bnx2fc_percpu_io_thread()`, `bnx2fc_get_host_stats()`, `bnx2fc_net_config()`, `bnx2fc_interface_setup()`, `bnx2fc_hba_create()`, `bnx2fc_interface_create()`, `bnx2fc_if_create()`, `bnx2fc_fw_init()`, `bnx2fc_fw_destroy()`, and vport create/destroy/disable helpers.

Module parameters include `debug_logging`, `devloss_tmo`, `max_luns`, `queue_depth`, and `log_fka`. The host sysfs attribute `tm_timeout` reads/writes `interface->tm_timeout`.

## Control Flow

Module init attaches the FCoE transport, attaches FC transport templates, allocates a workqueue, starts one global L2 receive thread, initializes per-CPU completion work lists, registers CPU hotplug callbacks to start per-CPU I/O threads, and registers as a CNIC FCoE ULP. CNIC init creates an HBA for supported bnx2x-class devices, fills firmware capability fields, adds it to `adapter_list`, and registers with CNIC.

FCoE controller creation validates fabric FIP mode and bnx2x backing netdev, finds the HBA, creates an interface/FIP controller, registers FIP and FCoE packet handlers, creates a timer workqueue, creates a libfc lport/SCSI host, configures networking, libfc, exchange manager, and discovery, adds the interface to `if_list`, and optionally marks it enabled/link-up.

Firmware start binds adapter DMA resources, sends FCoE init KWQEs, waits for `ADAPTER_STATE_UP` from KCQE completion, and marks `BNX2FC_FLAG_FW_INIT_DONE`. Firmware stop logs off all lports, waits for offloaded sessions to upload, sends firmware destroy, waits for destroy completion or timer, and frees DMA resources.

Transmit first lets FIP handle ELS requests when appropriate, then checks whether the destination is an offloaded session. Selected ELS/BLS frames for offloaded sessions go through firmware ELS helpers; other frames are encapsulated into FCoE Ethernet frames with CRC/EOF and sent through the netdev queue. Receive queues FCoE skbs to a global L2 thread, which validates MAC, FCoE/FC headers, CRC, vport destination, source FCF, and drops FCP data/ABTS before passing accepted frames to `fc_exch_recv()`.

Netdev events update adapter link state, call libfcoe link up/down, clear FC port types, clean queues, and wait for session upload on link down. Vport operations create/destroy/disable NPIV lports and can create static NPIV ports from CNIC NVRAM data.

## State and Persistence Behavior

Global state includes `adapter_list`, `if_list`, `adapter_count`, `bnx2fc_dev_lock`, `bnx2fc_wq`, `bnx2fc_global`, per-CPU `bnx2fc_percpu`, and transport template pointers. Per-HBA state persists across interfaces and CNIC callbacks. Per-interface state persists for an FCoE controller. Lport, vport, packet-handler, and workqueue state persists until destroy. Firmware init state is tracked by `BNX2FC_FLAG_FW_INIT_DONE`, `ADAPTER_STATE_UP`, `ADAPTER_STATE_READY`, and link-down/going-down bits.

## Dependencies and Integration Points

The file integrates with libfcoe controller sysfs and transport operations, libfc exchange/discovery/FCP hooks, SCSI host registration, FC transport attributes, CNIC ULP APIs, bnx2x netdev/ethtool metadata, Linux netdevice packet handlers, VLAN helpers, CPU hotplug, kthreads, workqueues, timers, PCI/DMA resource setup in `bnx2fc_hwi.c`, and SCSI I/O routines from other objects.

## Risks and Edge Cases

Lock ordering is delicate: comments note CNIC registration interactions with rtnl and `bnx2fc_dev_lock`. Several deprecated enable/disable paths coexist with sysfs controller state. `bnx2fc_destroy()` computes `ctlr = bnx2fc_to_ctlr(interface)` before checking `interface`, which would be unsafe if lookup returned NULL. Link-down waits can be interrupted and then signals are flushed. Receive path linearizes non-linear skbs but does not check the return from `skb_linearize()`. Controller creation has many staged resources; cleanup must match partial initialization. CPU hotplug can process pending completion work while target teardown is in progress.

## Test Signals

Test signals include module load/unload, CNIC device init/exit/start/stop, FCoE controller create/destroy via sysfs and legacy transport, VLAN and non-VLAN creation, link up/down with session upload, FIP discovery and FLOGI, L2 receive CRC/MAC/drop paths, NPIV vport create/delete/disable including NVRAM-created vports, host statistics requests, `tm_timeout` sysfs bounds, CPU online/offline while I/O completes, and teardown under pending FCoE skbs and offloaded sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_fcoe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_hwi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_hwi.c

## Purpose

`bnx2fc_hwi.c` is the firmware and hardware-interface implementation for the bnx2fc offload driver. It builds FCoE KWQEs for function/session operations, processes KCQE and per-session CQ completions, handles unsolicited frames and firmware error reports, rings SQ/CQ doorbells, maps per-session doorbell BAR space, initializes firmware task contexts for SCSI, ELS, task-management, ABTS, exchange cleanup, and sequence cleanup, and allocates/frees DMA resources required by firmware.

## Important APIs, Types, and Functions

Firmware request functions include `bnx2fc_send_stat_req()`, `bnx2fc_send_fw_fcoe_init_msg()`, `bnx2fc_send_fw_fcoe_destroy_msg()`, `bnx2fc_send_session_ofld_req()`, `bnx2fc_send_session_enable_req()`, `bnx2fc_send_session_disable_req()`, and `bnx2fc_send_session_destroy_req()`.

Completion and event functions include `bnx2fc_indicate_kcqe()`, `bnx2fc_process_new_cqes()`, `bnx2fc_process_cq_compl()`, `bnx2fc_process_l2_frame_compl()`, and internal handlers for fastpath notification, offload/enable/disable/destroy completion, firmware init failure, and unsolicited completion.

Queue and task helpers include `bnx2fc_add_2_sq()`, `bnx2fc_ring_doorbell()`, `bnx2fc_arm_cq()`, `bnx2fc_map_doorbell()`, `bnx2fc_get_next_rqe()`, `bnx2fc_return_rqe()`, `bnx2fc_init_task()`, `bnx2fc_init_mp_task()`, `bnx2fc_init_cleanup_task()`, and `bnx2fc_init_seq_cleanup_task()`.

Resource helpers include `bnx2fc_setup_task_ctx()`, `bnx2fc_free_task_ctx()`, `bnx2fc_setup_fw_resc()`, `bnx2fc_free_fw_resc()`, and hash-table allocation/free helpers.

## Control Flow

Firmware initialization sends three KWQEs with task-context PBL, dummy buffer, queue sizes, MTU, HSI version, hash-table addresses, free-list count, and error bitmap. Session offload sends four KWQEs that provide SQ/RQ/CQ/XFERQ/CONFQ/LCQ/connection database addresses, FC IDs, VLAN, sequence settings, recovery flags, MAC addresses, and timers. Enable, disable, destroy, stat, and function destroy use single KWQEs.

KCQE processing dispatches global events: CQ event notifications call `bnx2fc_process_new_cqes()`, session completions update rport flags and wake waiters, init completion marks the adapter up, destroy completion wakes firmware teardown, and stat completion completes the stats wait.

Per-session CQ processing consumes CQEs while toggle bits indicate new entries. Unsolicited CQEs route to frame/error/warning handling. Pending-work CQEs locate the task context by XID, copy response RQ data, return RQEs, and either queue work to a per-CPU I/O thread or process inline. `bnx2fc_process_cq_compl()` then dispatches by command type and firmware RX state to SCSI completion, ELS completion, TM completion, ABTS completion, cleanup completion, or sequence-cleanup completion.

Task initialization writes firmware-visible context fields. SCSI tasks build FCP_CMND, SGL/cached SGE state, data length, task type, device type, class, context ID, RX state, sequence count, and RX ID. Middle-path tasks set FC headers and request/response BDs. Cleanup and sequence cleanup tasks reference original XIDs and, for sequence cleanup, compute the BD and offset where recovery should resume.

## State and Persistence Behavior

This file manages most firmware-visible persistent DMA state: HBA task-context pages and BDT, hash tables and PBLs, T2 hash tables, dummy buffer, statistics buffer, per-rport queues and connection DB, SQ/CQ/RQ indices and toggle bits, and MMIO doorbell mappings. It also mutates rport flags (`OFFLOADED`, `ENABLED`, `DISABLED`, `DESTROYED`, completion bits), HBA adapter flags, command task pointers, and per-command recovery state.

## Dependencies and Integration Points

The file depends on HSI structures from `57xx_hsi_bnx2fc.h`, constants from `bnx2fc_constants.h`, CNIC `submit_kwqes`, PCI DMA and ioremap APIs, per-CPU worker state from `bnx2fc_fcoe.c`, libfc frame helpers, SCSI command structures, and completion handlers in `bnx2fc_io.c`, `bnx2fc_tgt.c`, and `bnx2fc_els.c`.

## Risks and Edge Cases

DMA and endian correctness are critical. Many fields are assigned with casts to low/high 32-bit values; missing `cpu_to_le*` conversion or truncation can break firmware. Queue wrap/toggle logic must be exact for SQ/CQ/RQ. `bnx2fc_get_next_rqe()` returns NULL if a multi-entry read would cross the ring boundary, forcing callers to copy one RQE at a time; mistakes here corrupt unsolicited frames. Completion processing may run on per-CPU threads while teardown frees target queues, so `cq_lock`, target locks, and worker shutdown are important. Firmware error reports for tape can trigger REC/SRR, while other errors start ABTS; wrong classification can lose data or hang commands. Doorbell mappings use only four bytes per context and must be unmapped by target teardown code outside this file.

## Test Signals

Useful validation includes firmware init/destroy KWQE/KCQE exchange, session offload/enable/disable/destroy with waiters, doorbell MMIO mapping and writes, SQ/CQ/RQ wrap and toggle stress, FCP reads/writes with cached and multi-SGE contexts, ELS/TMF/ABTS/cleanup/sequence-cleanup task completions, unsolicited ELS frames, firmware error/warning reports, REC/SRR tape recovery, stats requests, DMA API debug, CPU hotplug completion processing, and teardown during pending CQEs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_hwi.c -->
