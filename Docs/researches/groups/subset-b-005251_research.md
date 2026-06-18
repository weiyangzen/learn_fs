# Research: subset-b-005251 Chelsio SCSI/FCoE/iSCSI driver files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_scsi.c

## Purpose

This file implements the Chelsio FCoE SCSI mid-layer bridge for csiostor. It accepts Linux SCSI commands, maps them into firmware SCSI work requests, tracks those requests through a small state machine, handles completions/errors/task management, exposes FCoE host sysfs controls, and owns allocation of SCSI request/response/DDP buffers.

## Important APIs, Types, And Functions

The file exports module tunables such as `csio_scsi_eqsize`, `csio_scsi_iqlen`, `csio_scsi_ioreqs`, `csio_lun_qdepth`, and scan-timeout values. Core entry points are `csio_queuecommand()`, `csio_scsi_cmpl_handler()`, `csio_scsim_cleanup_io()`, `csio_scsim_cleanup_io_lnode()`, `csio_scsim_init()`, and `csio_scsim_exit()`. It also defines `csio_fcoe_shost_template` and `csio_fcoe_shost_vport_template` for SCSI host registration.

Important helpers build firmware requests: `csio_scsi_fcp_cmnd()`, `csio_scsi_init_cmd_wr()`, `csio_scsi_init_read_wr()`, `csio_scsi_init_write_wr()`, `csio_scsi_init_ultptx_dsgl()`, and `csio_scsi_init_abrt_cls_wr()`. Error handling flows through `csio_scsi_err_handler()`, `csio_scsi_cbfn()`, `csio_eh_abort_handler()`, `csio_tm_cbfn()`, and `csio_eh_lun_reset_handler()`. State functions are `csio_scsis_uninit()`, `csio_scsis_io_active()`, `csio_scsis_tm_active()`, `csio_scsis_aborting()`, `csio_scsis_closing()`, and `csio_scsis_shost_cmpl_await()`.

## Control Flow

Normal I/O starts in `csio_queuecommand()`. The function checks FC rport and hardware readiness, DMA-maps the SCSI scatterlist, rejects requests above `CSIO_SCSI_MAX_SGE`, obtains a preallocated `csio_ioreq`, fills lnode/rnode/queue/data-direction fields, stores the command in `scratch1`, and posts `CSIO_SCSIE_START_IO`. The uninitialized state chooses a command, read, or write WR, optionally routes reads through DDP setup, adds the request to `active_q`, and rings the selected egress queue.

Completions enter through `csio_scsi_cmpl_handler()`, which validates `CPL_FW6_MSG`, decodes WR opcode/status, recovers the `csio_ioreq` from the firmware cookie, and returns it to the caller. State completion usually moves the request out of `active_q`; special I-T nexus-loss statuses can move it to the rnode host completion wait queue until remote-node loss is reported. Callback processing maps firmware/FCP status to Linux `cmnd->result`, copies autosense, unmaps DMA, copies DDP bounce data when needed, calls `scsi_done()`, clears the command pointer, and wakes error-handler waiters.

SCSI EH abort posts an ABORT or CLOSE WR depending on lnode readiness, waits for `cmplobj`, and treats `DID_REQUEUE` as a successful abort. LUN reset issues an FCP task-management command, waits by polling `csio_scsi_cmnd(ioreq)`, then gathers active I/O matching the LUN and aborts them.

## State And Persistence

Runtime state is in `struct csio_scsim`: `active_q`, `ioreq_freelist`, `ddp_freelist`, `freelist_lock`, protocol lengths, `max_sge`, and statistics. Each `csio_ioreq` persists through firmware completion and carries state-machine state, queue indices, DMA response buffer, WR status, callback, lnode/rnode, command pointer, optional DDP buffer list, and completion object. No on-disk state exists. Hardware-visible state consists of DMA mappings, firmware exchanges, and FCoE/SCSI sessions.

## Dependencies And Integration Points

This code integrates with Linux SCSI, libfc/fc transport, csiostor hardware/lnode/rnode modules, the Chelsio WR layer, firmware ABI structures from `t4fw_api_stor.h`, DMA pools, PCI device DMA allocation, sysfs host attributes, and FC error-recovery helpers such as `fc_block_scsi_eh()` and `fc_remote_port_chkready()`.

## Risks

Request lifetime is race-prone: abort, close, firmware completion, and driver cleanup all mutate the same `csio_ioreq` and command pointer. DDP bounce buffering depends on page-boundary alignment and finite `csio_ddp_descs`; underprovisioning returns `-EBUSY`. Several cleanup paths sleep while dropping and reacquiring `hw->lock`, so queue membership must remain consistent. `csio_store_dbg_level()` appears to return `-EINVAL` when `sscanf()` succeeds, which makes the sysfs debug-level store path suspect. LUN reset failure paths increment rnode stats only when `rn` is valid; earlier `fail_ret` avoids that, but later paths assume a live rnode.

## Test Signals

Useful signals include successful kernel build with csiostor, SCSI discovery through `csio_scan_finished()`, normal read/write/control I/O, SGE-limit rejection, DMA-map failure injection, unaligned-read DDP bounce coverage, FCP autosense and residual handling, abort/close races, LUN reset with pending I/O, link-down/rdev-lost serialization, sysfs `hw_state`, `device_reset`, `disable_port`, and `dbg_level` behavior, plus leak checks for ioreq/DDP freelists after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_scsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_scsi.h

## Purpose

This header defines the public SCSI-module contract for csiostor: host templates, SCSI queue tunables, max SGE sizing, request/stat/state types, freelist helpers, event wrappers, and exported functions implemented by `csio_scsi.c`.

## Important APIs, Types, And Functions

Key constants include `CSIO_SCSI_MAX_SGE`, `CSIO_SCSI_ABRT_TMO_MS`, `CSIO_SCSI_LUNRST_TMO_MS`, `CSIO_SCSI_IQSIZE`, `CSIO_MAX_SNS_LEN`, and `CSIO_SCSI_RSP_LEN`. `struct csio_scsi_stats` records I/O success, readiness failures, DMA failures, SCSI/FW errors, abort/close outcomes, active counts, freelist counts, DDP unalignment, and invalid CPL/opcode counters. `struct csio_scsim` is the module owner for active and free request lists.

`enum csio_scsi_ev` names the request state-machine events, and `enum csio_scsi_lev` plus `struct csio_scsi_level_data` support cleanup or abort at all, lnode, rnode, or LUN scope. Inline APIs manage request and DDP freelists (`csio_get_scsi_ioreq()`, `csio_put_scsi_ioreq()`, `csio_get_scsi_ddp()`), post events (`csio_scsi_completed()`, `csio_scsi_aborted()`, `csio_scsi_closed()`), and start/abort/close requests.

## Control Flow

Consumers include this header to allocate `struct csio_scsim`, register `csio_fcoe_shost_template`, and call `csio_scsim_init()`/`exit()`. Completion paths call the inline wrappers to convert firmware completion classes into state-machine events. Queuecommand and EH paths use `csio_scsi_start_io()`, `csio_scsi_start_tm()`, `csio_scsi_abort()`, and `csio_scsi_close()`; each posts an event and returns `ioreq->drv_status`.

## State And Persistence

All state described here is volatile kernel state. `csio_scsi_cmnd(req)` aliases `req->scratch1`, so the active SCSI command pointer shares generic request scratch storage. Freelist accounting is maintained through stats counters and list membership, protected by the caller's expected locks. There is no persisted configuration beyond module parameters declared elsewhere.

## Dependencies And Integration Points

The header depends on Linux spinlock/completion/SCSI headers, FC FCP definitions, `csio_defs.h`, and `csio_wr.h`. It exposes the SCSI module to the csiostor hardware, interrupt/completion, lnode/rnode, and init paths. The `cmd_size` private area expected by the host template is `struct csio_cmd_priv`.

## Risks

The inline freelist helpers are lockless and rely on callers using `freelist_lock` or `hw->lock` consistently. `csio_scsi_cmnd(req)` is a macro over generic scratch storage, so any other user of `scratch1` would corrupt command association. `csio_put_scsi_ioreq_list()` increments counters by a caller-provided `n`; wrong values desynchronize stats. Event wrappers add list nodes to callback queues based on state side effects, so misuse outside the expected locked completion path can duplicate list entries.

## Test Signals

Build signals catch struct/API drift with `csio_scsi.c`. Runtime signals include balanced `n_free_ioreq` and `n_free_ddp` after stress, correct active/TM counts, SCSI EH completion behavior, and no list-debug warnings under abort, close, LUN reset, and driver cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_wr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_wr.c

## Purpose

This file implements the csiostor work-request module. It allocates DMA-backed ingress, egress, and freelist queues; creates/destroys firmware queue contexts via mailbox commands; reserves and issues egress WRs; processes ingress responses and freelist buffers; and initializes SGE host/interrupt/coalescing parameters.

## Important APIs, Types, And Functions

Externally used APIs are `csio_wr_alloc_q()`, `csio_wr_iq_create()`, `csio_wr_eq_create()`, `csio_wr_destroy_queues()`, `csio_wr_get()`, `csio_wr_copy_to_wrp()`, `csio_wr_issue()`, `csio_wr_process_iq()`, `csio_wr_process_iq_idx()`, `csio_wr_sge_init()`, `csio_wrm_init()`, and `csio_wrm_exit()`. Internal response handlers include `csio_wr_iq_create_rsp()`, `csio_wr_eq_cfg_rsp()`, `csio_wr_iq_destroy_rsp()`, and `csio_wr_eq_destroy_rsp()`. Fast-path helpers manage FL doorbells, queue credits, IQ generation bits, and queue wraparound.

## Control Flow

Initialization starts with `csio_wrm_init()`, which allocates the WR module queue-pointer array and per-queue metadata. `csio_wr_sge_init()` then reads or programs SGE registers depending on mastership, firmware init state, and soft-parameter use. Queue allocation reserves a queue slot, allocates DMA memory, calculates credits/wrap pointers, optionally recursively allocates a freelist for an ingress queue, allocates FL buffer metadata, fills FL buffers, and records INTx handlers.

Firmware context creation uses mailbox commands. `csio_wr_iq_create()` builds IQ parameters from interrupt mode, WR size, vector, port, async flag, and optional freelist; synchronous callers immediately parse the response and install IQ/FL ids and interrupt map entries. `csio_wr_eq_create()` creates offload egress queues attached to an IQ.

Transmit paths call `csio_wr_get()` to read EQ status-page `cidx`, compute free credits, return one or two memory spans for possible wraparound, advance `pidx`, and record `inc_idx`. `csio_wr_issue()` uses a write barrier and rings the SGE doorbell. Receive paths call `csio_wr_process_iq()`, which loops while the footer generation bit indicates a new entry, dispatches CPL, FLBUF, or forwarded interrupt responses, replenishes FL queues below low water, then writes GTS with consumed count and coalescing timer.

## State And Persistence

`struct csio_wrm` owns the queue array, firmware id bases, interrupt map, free queue cursor, and cached SGE registers. Each `struct csio_q` stores producer/consumer indices, increment count, DMA region, owner, context-specific IDs, and stats. State is volatile but synchronized with hardware through DMA queue memory, status pages, doorbells, GTS writes, SGE registers, and firmware mailbox contexts.

## Dependencies And Integration Points

The file depends on Chelsio register definitions in `t4_values.h`, hardware helpers in `csio_hw.h`, mailbox helpers in `csio_mb.h`, `t4fw_api.h`, and `t4fw_api_stor.h`. It integrates with PCI DMA allocation, SGE hardware registers, firmware IQ/EQ commands, interrupt dispatch, and upper csiostor modules that provide IQ handlers and consume WR queue slots.

## Risks

Queue wrap and credit arithmetic are correctness-critical; an off-by-one can overwrite unconsumed WRs or starve queues. Several error paths in `csio_wr_alloc_q()` return after partially allocated queues or FL buffers, relying on later WRM exit for cleanup. `csio_wr_process_iq()` indexes `intr_map[qid]` without an explicit bound check after subtracting `fw_iq_start`, so corrupt forwarded interrupt qids can be dangerous. FL buffer invalidation does not free DMA memory immediately, which is intentional but makes refill/accounting bugs harder to see. SGE programming differs across T5/T6 and master/non-master paths; wrong flags can misconfigure padding, status page size, or coalescing.

## Test Signals

Test by creating/destroying IQ/EQ/FL queues in all interrupt modes, exhausting queue slots, forcing mailbox failures, issuing WRs that wrap around EQ end, processing empty and stray IQ interrupts, handling CPL/FLBUF/INTR responses, exercising FL refill thresholds, unloading after partial allocation failures, and validating SGE coalescing values against module parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_wr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_wr.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_wr.h

## Purpose

This header defines the csiostor WR queue data model and public WRM APIs. It provides SGE field constants, queue parameter structures, generic DMA/request structures, IQ footer parsing helpers, queue metadata, SGE cache state, WRM state, accessor macros, and function prototypes.

## Important APIs, Types, And Functions

Important types include `struct csio_iq_params`, `struct csio_eq_params`, `struct csio_dma_buf`, `struct csio_ioreq`, `struct csio_qstatus_page`, `struct csio_iqwr_footer`, `struct csio_wr_pair`, `struct csio_fl_dma_buf`, `struct csio_iq`, `struct csio_eq`, `struct csio_fl`, `struct csio_q`, `struct csio_sge`, and `struct csio_wrm`. The `iq_handler_t` callback type is the WR completion interface. `csio_wr_status()` extracts firmware retval/status from a WR header.

The accessor macros abstract queue arrays and firmware ids (`csio_q_iqid()`, `csio_q_eqid()`, `csio_q_physiqid()`, `csio_q_eq_wrap()`, and others). Prototypes expose queue allocation/creation/destruction, WR reservation/copy/issue, IQ processing, SGE init, and WRM init/exit.

## Control Flow

Higher-level modules allocate queue metadata through `csio_wrm_init()`, allocate specific queues with `csio_wr_alloc_q()`, ask firmware to create contexts, then reserve WR space via `csio_wr_get()`. If a WR spans the circular queue end, callers receive `struct csio_wr_pair` with two segments and can use `csio_wr_copy_to_wrp()` or local split-copy code. Interrupt handlers process IQ entries through `csio_wr_process_iq()` or `_idx()`.

## State And Persistence

This header defines volatile in-memory state mirrored to hardware. `struct csio_ioreq` is cacheline-aligned and reused by SCSI and other protocols. Queue state persists only while the driver owns DMA memory and firmware contexts. Hardware queue ids are invalidated with `CSIO_MAX_QID`; queue memory and SGE cached values are rebuilt on driver/device initialization.

## Dependencies And Integration Points

It includes `csio_defs.h`, generic Chelsio firmware API headers, and storage firmware API definitions. It is consumed by SCSI, hardware, mailbox, interrupt, and possibly lnode/rnode modules. The layout of `struct csio_ioreq` and firmware WR status extraction must match `csio_scsi.c` and firmware ABI structures.

## Risks

The macro `csio_q_iq_to_flid(__hw, __iq_idx)` references `__iq_qidx`, which is not its parameter name; use would fail to compile or expand incorrectly. Many accessor macros evaluate arguments directly and assume valid queue indices. `struct csio_ioreq` embeds generic scratch pointers with protocol-specific meanings, creating aliasing risk. Bitfield layout in parameter structs is host-compiler-sensitive but appears to be an internal mailbox helper contract rather than direct DMA ABI.

## Test Signals

Build coverage should include all macros used by WR/SCSI paths. Runtime signals include valid queue id transitions from `CSIO_MAX_QID` to firmware ids and back, correct two-segment WR behavior, stable `struct csio_ioreq` alignment, and no list/DMA corruption under high I/O and interrupt rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_wr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/t4fw_api_stor.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/t4fw_api_stor.h

## Purpose

This header defines Chelsio T4/T5 storage firmware ABI structures and constants for FCoE and SCSI offload. It is a packed protocol contract between driver code and adapter firmware, covering remote-device events, FCoE ELS/CT, SCSI read/write/command/abort-close WRs, FCoE resource/link/VNP/service-parameter/stat/FCF commands, and field extraction helpers.

## Important APIs, Types, And Functions

Key enums are `fw_fcoe_link_sub_op`, `fw_fcoe_link_status`, `fw_ofld_prot`, `rport_type_fcoe`, `event_cause_fcoe`, `fcoe_cmn_type`, `fw_wr_stor_opcodes`, and `fw_cmd_stor_opcodes`. Important structures include `fw_rdev_wr`, `fw_fcoe_els_ct_wr`, `fw_scsi_write_wr`, `fw_scsi_read_wr`, `fw_scsi_cmd_wr`, `fw_scsi_abrt_cls_wr`, `fw_fcoe_res_info_cmd`, `fw_fcoe_link_cmd`, `fw_fcoe_vnp_cmd`, `fw_fcoe_sparams_cmd`, `fw_fcoe_stats_cmd`, and `fw_fcoe_fcf_cmd`.

Macros such as `FW_RDEV_WR_FLOWID_GET()`, `FW_SCSI_*_WR_IMMDLEN()`, `FW_SCSI_ABRT_CLS_WR_SUB_OPCODE()`, and `FW_FCOE_*_GET()` encode or decode packed firmware fields. `SCSI_ABORT` and `SCSI_CLOSE` define abort-close suboperation values.

## Control Flow

This file has no executable control flow. Driver code fills these structures, converts fields to big-endian as needed, appends immediate FCP payloads or DSGLs, posts the resulting WRs to Chelsio queues, and later decodes firmware responses or asynchronous events using the same opcode and field definitions.

## State And Persistence

There is no mutable state in this header. Its structures describe DMA/mailbox payloads that become transient hardware/firmware state when submitted. Firmware-created resources such as rdev flowids, FCFs, VNPs, sessions, and exchanges persist on the adapter until explicitly closed, reset, or invalidated by link/session events.

## Dependencies And Integration Points

The header depends on fixed-width Linux endian types and the generic firmware command header conventions from included Chelsio headers. It is consumed by csiostor SCSI, lnode/rnode, FCoE control, mailbox, and WR paths. Correct integration requires exact field sizes, endian conversion, opcode values, and firmware-version compatibility.

## Risks

Any layout drift breaks hardware communication. Several fields are densely packed and exposed only through partial macros, so callers must know which endian conversion and bit shifts apply. `u64 cookie` fields carry host pointers in csiostor; that assumes pointer-width compatibility and that firmware returns the value opaquely. This ABI mixes FCoE and iSCSI remote-device layouts in unions, increasing risk if protocol selectors are wrong.

## Test Signals

Signals include successful compile against firmware headers, adapter login and rdev events, FCoE link up/down handling, VNP allocation/free, FCF discovery, SCSI read/write/cmd completions, abort/close completions, stats retrieval, and verification that firmware statuses map correctly into SCSI/FC upper-layer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/t4fw_api_stor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/Kconfig

## Purpose

This top-level Kconfig file includes the Chelsio iSCSI offload driver configuration fragments for T3 (`cxgb3i`) and T4+ (`cxgb4i`). It provides no direct option itself; it composes the submenu content from child directories.

## Important APIs, Types, And Functions

The only directives are `source "drivers/scsi/cxgbi/cxgb3i/Kconfig"` and `source "drivers/scsi/cxgbi/cxgb4i/Kconfig"`.

## Control Flow

During kernel configuration, Kconfig reads this file and then evaluates each child config. Selecting either child driver controls object inclusion through the sibling Makefile.

## State And Persistence

Configuration state persists in the kernel `.config` as `CONFIG_SCSI_CXGB3_ISCSI` and/or `CONFIG_SCSI_CXGB4_ISCSI`. This file owns no runtime state.

## Dependencies And Integration Points

It integrates the Chelsio iSCSI offload family into the SCSI driver Kconfig tree and delegates all dependency selection to child Kconfig files.

## Risks

If this file is omitted from the parent SCSI Kconfig, neither child option is visible. If child paths are renamed without updating these `source` lines, configuration fails.

## Test Signals

Run menuconfig/olddefconfig with the parent SCSI Kconfig and confirm both Chelsio T3 and T4 iSCSI options appear and can be selected subject to their dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/Makefile

## Purpose

This Makefile builds the shared Chelsio iSCSI library and the selected T3/T4 driver subdirectories. It also adds the shared Chelsio `libcxgb` include path needed by `libcxgbi` and children.

## Important APIs, Types, And Functions

The file sets `ccflags-y += -I $(srctree)/drivers/net/ethernet/chelsio/libcxgb`. It builds `libcxgbi.o cxgb3i/` when `CONFIG_SCSI_CXGB3_ISCSI` is enabled and `libcxgbi.o cxgb4i/` when `CONFIG_SCSI_CXGB4_ISCSI` is enabled.

## Control Flow

Kbuild evaluates the config-symbol object lists. If both drivers are enabled, `libcxgbi.o` is listed by both conditional lines; Kbuild normally handles object inclusion for the directory, but this duplication is a notable build-shape point.

## State And Persistence

The file has no runtime state. Build outputs are generated according to `.config` and Kbuild state.

## Dependencies And Integration Points

It integrates `drivers/scsi/cxgbi/libcxgbi.c`, `cxgb3i/Kbuild`, and `cxgb4i/Kbuild` with Chelsio Ethernet include headers. It depends on the Kconfig symbols defined in child Kconfig files.

## Risks

The duplicated `libcxgbi.o` conditional can be surprising when both T3 and T4 are enabled, although this is an established kernel build pattern in some shared-library directories. Include path changes in Chelsio net drivers can break compilation.

## Test Signals

Build with only T3, only T4, both, and neither enabled. Confirm `libcxgbi` is built when needed, no duplicate-symbol/link issue occurs, and both child modules resolve Chelsio Ethernet headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/Kbuild

## Purpose

This Kbuild fragment compiles the Chelsio T3 iSCSI offload module and supplies include paths for T3 Ethernet and common Chelsio library headers.

## Important APIs, Types, And Functions

It adds `drivers/net/ethernet/chelsio/cxgb3` and `drivers/net/ethernet/chelsio/libcxgb` to `ccflags-y`, then maps `CONFIG_SCSI_CXGB3_ISCSI` to `cxgb3i.o`.

## Control Flow

When the top-level cxgbi Makefile descends into `cxgb3i/`, Kbuild uses this fragment to compile `cxgb3i.c` if the T3 iSCSI config is enabled.

## State And Persistence

No runtime state exists here. Build state is determined by `.config`.

## Dependencies And Integration Points

This file ties `cxgb3i.c` to the cxgb3 Ethernet driver headers and shared Chelsio library headers that define CPLs, offload device APIs, L2T, and pagepod support.

## Risks

Header path drift in the Ethernet driver tree will break this module. Because this is a Kbuild fragment, placing module-wide flags here only affects this subdirectory, not `libcxgbi.o`.

## Test Signals

Enable `CONFIG_SCSI_CXGB3_ISCSI=m` or `=y` and confirm `cxgb3i.o` builds with no missing `cxgb3` or `libcxgb` includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/Kconfig

## Purpose

This Kconfig file defines the `SCSI_CXGB3_ISCSI` option for Chelsio T3 iSCSI offload support.

## Important APIs, Types, And Functions

The option is `tristate "Chelsio T3 iSCSI support"`. It depends on `PCI && INET` and selects `NETDEVICES`, `ETHERNET`, `NET_VENDOR_CHELSIO`, `CHELSIO_T3`, `CHELSIO_LIB`, and `SCSI_ISCSI_ATTRS`.

## Control Flow

When selected, Kconfig enables the necessary Chelsio Ethernet and iSCSI transport support. Kbuild then compiles `libcxgbi.o` and the `cxgb3i` subdirectory through the parent Makefile.

## State And Persistence

The selected state persists as `CONFIG_SCSI_CXGB3_ISCSI` in `.config`; no runtime state exists in this file.

## Dependencies And Integration Points

The option integrates SCSI iSCSI transport attributes, the Chelsio T3 Ethernet offload driver, common Chelsio library support, PCI, and IPv4/INET networking.

## Risks

The `select` chain can force lower-level networking drivers on, so dependency correctness matters. The help text is minimal and does not mention firmware/offload requirements or hardware generation limits beyond T3.

## Test Signals

Kconfig tests should verify that the symbol is visible only with PCI and INET, that selecting it pulls in Chelsio T3/library and iSCSI attrs, and that module/built-in builds both link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/cxgb3i.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/cxgb3i.c

## Purpose

This file is the Chelsio T3 iSCSI offload driver. It registers as a cxgb3 offload client, exposes a libiscsi transport, creates SCSI hosts through libcxgbi, manages offloaded TCP connection setup/teardown over CPL messages, sends and receives iSCSI PDUs, and programs T3 pagepod/DDP resources.

## Important APIs, Types, And Functions

Module parameters include `dbg_level`, `cxgb3i_rcv_win`, `cxgb3i_snd_win`, `cxgb3i_rx_credit_thres`, `cxgb3i_max_connect`, and `cxgb3i_sport_base`. Important global objects are `t3_client`, `cxgb3i_host_template`, `cxgb3i_iscsi_transport`, `cxgb3i_stt`, and `cxgb3i_cpl_handlers`.

Connection transmit/control helpers include `send_act_open_req()`, `send_close_req()`, `send_abort_req()`, `send_abort_rpl()`, `send_rx_credits()`, `make_tx_data_wr()`, and `push_tx_frames()`. CPL receive handlers include `do_act_establish()`, `do_act_open_rpl()`, `do_peer_close()`, `do_close_con_rpl()`, `do_abort_req()`, `do_abort_rpl()`, `do_iscsi_hdr()`, and `do_wr_ack()`. Device/DDP lifecycle flows through `cxgb3i_ofld_init()`, `cxgb3i_ddp_init()`, `cxgb3i_dev_open()`, `cxgb3i_dev_close()`, and module init/exit.

## Control Flow

Module init registers the iSCSI transport with libcxgbi and registers `t3_client` with cxgb3. When a T3 offload device opens, `cxgb3i_dev_open()` allocates a `cxgbi_device`, fills port/PCI/MTU/transport fields, initializes DDP/pagepod resources, installs offload operation callbacks, creates HBA hosts, and captures per-port private IPv4 addresses.

Endpoint connect uses libcxgbi routing to create a `cxgbi_sock`, then `init_act_open()` updates the adapter-private IPv4 address, obtains an L2T entry, allocates an ATID, prepares an active-open CPL, initializes windows/credits/MSS, and sends `CPL_ACT_OPEN_REQ`. Establish/open-failure CPLs convert hardware status into socket state, retry connection-exists cases briefly, or fail the endpoint. Once established, queued PDUs are pushed by `push_tx_frames()`, which consumes WR credits, prepends TX_DATA WRs, updates sequence numbers, and sends through L2T.

Receive flow enters CPL handlers. `do_iscsi_hdr()` validates connection state, parses coalesced iSCSI header/DDP status trailers, sets skb control flags for digest/padding/DDP status, queues the PDU to `receive_queue`, and notifies libcxgbi. Close and abort CPLs delegate state transitions to shared `cxgbi_sock_*` helpers. DDP setup writes pagepods with ULP memory I/O WRs and configures TCB page index/digest fields.

## State And Persistence

Persistent runtime state is held in `struct cxgbi_device`, `struct cxgbi_hba`, `struct cxgbi_sock`, T3 ATID/TID tables, L2T entries, WR queues, preallocated close/abort CPL skbs, pagepod manager state in `t3dev->ulp_iscsi`, and private IPv4 fields in cxgb3 `port_info`. No disk persistence exists. Hardware state includes TCBs, offload connection ids, DDP pagepod memory, iSCSI parameter limits, and firmware/client registrations.

## Dependencies And Integration Points

The driver depends on cxgb3 Ethernet offload APIs (`t3cdev`, CPL handlers, L2T, ATID/TID management, adapter control calls), `libcxgbi`, `libiscsi_tcp`, SCSI host/transport templates, Chelsio pagepod library, Linux networking skbs/routes, and iSCSI userspace transport operations. It is built only when Kconfig enables Chelsio T3 and iSCSI attrs.

## Risks

The connection state machine is race-sensitive: active open retry timers, abort requests/replies, close replies, and peer close can arrive in different orders. `abort_status_to_errno()` takes `need_rst` but does not use it, suggesting either stale API or incomplete reset-status handling. `do_iscsi_hdr()` assumes coalesced CPL layout and aborts on malformed lengths; firmware or skb format drift can kill connections. DDP/pagepod programming is asynchronous and can partially fail under skb allocation pressure. Private IPv4 address mutation in netdev private data must stay synchronized with HBA/session setup.

## Test Signals

Signals include module load/unload, cxgb3 client add/remove, HBA creation per port, login/logout through open-iscsi, active-open errors for ARP miss/TCAM full/connection exists, high-throughput TX WR credit recovery, RX digest/DDP error reporting, abort/close races, adapter reset events, DDP enabled/disabled paths, pagepod allocation/tagmask correctness, and cleanup of ATID/TID/L2T/CPL skb resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/cxgb3i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/cxgb3i.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/cxgb3i.h

## Purpose

This header provides T3-specific constants, exported CPL handler declaration, netdev-private IPv4 accessors, and no-RSS CPL layout structures used by `cxgb3i.c`.

## Important APIs, Types, And Functions

Constants include `CXGB3I_SCSI_HOST_QDEPTH`, `CXGB3I_MAX_LUN`, `ISCSI_PDU_NONPAYLOAD_MAX`, and `CXGB3I_TX_HEADER_LEN`. The header declares `cxgb3i_cpl_handlers[NUM_CPL_CMDS]`. Inline helpers `cxgb3i_get_private_ipv4addr()` and `cxgb3i_set_private_ipv4addr()` read/write `struct port_info` iSCSI fields. `struct cpl_iscsi_hdr_norss` and `struct cpl_rx_data_ddp_norss` model compact receive-side CPL data without RSS prefix.

## Control Flow

`cxgb3i.c` uses the constants in host-template and skb reservation setup, registers the exported handler array with cxgb3, and calls the IPv4 helpers during HBA address synchronization. Receive parsing copies no-RSS CPL trailers into the local structs to extract PDU length, sequence, digest, and DDP status.

## State And Persistence

The header itself has no state. The IPv4 accessors mutate `port_info.iscsic.flags`, `port_info.iscsi_ipv4addr`, and `iscsic.mac_addr` in the cxgb3 netdev private area. That state persists for the life of the netdev/adapter and is used by offloaded connection setup.

## Dependencies And Integration Points

It depends on cxgb3 `struct port_info`, CPL types, iSCSI header/digest constants, skb header sizes, and `NUM_CPL_CMDS`. It is the T3-specific bridge between cxgb3 network internals and the shared cxgbi iSCSI layer.

## Risks

The inline helpers assume `netdev_priv(ndev)` is a cxgb3 `struct port_info`; using them with another netdev type corrupts memory. `CXGB3I_TX_HEADER_LEN` must match the headroom required by `make_tx_data_wr()`. The no-RSS CPL structs must match firmware layout exactly or RX parsing in `do_iscsi_hdr()` misinterprets status and lengths.

## Test Signals

Build tests should catch missing cxgb3 types. Runtime tests include private IPv4 propagation to physical and VLAN devices, TX skb headroom checks, and RX PDU parsing with DDP and non-DDP payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/cxgb3i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/Kbuild

## Purpose

This Kbuild fragment compiles the Chelsio T4 iSCSI offload module and supplies include paths for the T4 Ethernet driver and common Chelsio library headers.

## Important APIs, Types, And Functions

It adds `drivers/net/ethernet/chelsio/cxgb4` and `drivers/net/ethernet/chelsio/libcxgb` to `ccflags-y`, then maps `CONFIG_SCSI_CXGB4_ISCSI` to `cxgb4i.o`.

## Control Flow

When the parent cxgbi Makefile descends into `cxgb4i/`, Kbuild compiles `cxgb4i.c` if the T4 iSCSI config is enabled.

## State And Persistence

No runtime state exists here. Build state is determined by `.config`.

## Dependencies And Integration Points

This file ties the T4 iSCSI driver to cxgb4 Ethernet headers and the common Chelsio library. It is selected through the parent `cxgbi/Makefile` and child Kconfig symbol.

## Risks

Header path drift in cxgb4 or libcxgb breaks compilation. Flags are local to the subdirectory and do not affect `libcxgbi.o`.

## Test Signals

Enable `CONFIG_SCSI_CXGB4_ISCSI=m` or `=y` and confirm `cxgb4i.o` builds cleanly with cxgb4 and libcxgb include dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/Kconfig

## Purpose

This Kconfig file defines `SCSI_CXGB4_ISCSI`, the Chelsio T4-generation iSCSI offload driver option.

## Important APIs, Types, And Functions

The option is `tristate "Chelsio T4 iSCSI support"`. It depends on `PCI && INET`, `PTP_1588_CLOCK_OPTIONAL`, `THERMAL || !THERMAL`, `ETHERNET`, and `TLS || TLS=n`. It selects `NET_VENDOR_CHELSIO`, `CHELSIO_T4`, `CHELSIO_LIB`, and `SCSI_ISCSI_ATTRS`.

## Control Flow

Kconfig exposes the option only when dependencies are satisfied. When selected, Kbuild compiles shared `libcxgbi.o` and descends into `cxgb4i/` to build `cxgb4i.o`.

## State And Persistence

The selected state persists in `.config` as `CONFIG_SCSI_CXGB4_ISCSI`. This file has no runtime state.

## Dependencies And Integration Points

The option integrates PCI/INET networking, Chelsio T4 Ethernet support, shared Chelsio library support, iSCSI transport attributes, optional PTP, thermal, and TLS compatibility constraints.

## Risks

The `TLS || TLS=n` dependency prevents unsupported TLS combinations but can make the option disappear in configurations where TLS is modular or otherwise incompatible. The thermal dependency is a compatibility pattern that should match cxgb4 requirements. As with T3, `select` pulls lower-level Chelsio components into the configuration.

## Test Signals

Kconfig tests should cover built-in and modular combinations for TLS/PTP/THERMAL, verify option visibility, confirm selected dependencies, and build both module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/Kconfig -->
