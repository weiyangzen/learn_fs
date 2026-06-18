# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_os.c lines 1-8898

## Chunk Scope

This chunk covers the main operating-system glue for the QLogic `qla4xxx` iSCSI HBA driver from the file header through `qla4xxx_probe_adapter()`. It includes module parameters, SCSI host and iSCSI transport templates, CHAP and flash DDB sysfs handlers, endpoint/session/connection/task plumbing, queue submission, timer and DPC recovery control flow, boot target export, firmware DDB discovery/build logic, model-specific operation tables, I/O space mapping, memory allocation, and PCI probe initialization. Later adapter removal, SCSI error-handler bodies after probe, PCI AER/EEH handlers, module init/exit, and the PCI id table are outside this chunk.

## Purpose

`ql4_os.c` bridges Linux SCSI/libiscsi/sysfs APIs to QLogic firmware and hardware operations. The code exposes an offloaded iSCSI transport (`qla4xxx_iscsi_transport`) and SCSI host template (`qla4xxx_driver_template`), translates user-visible iSCSI interface and flashnode parameters into firmware address control blocks and DDB records, manages adapter lifecycle state, and coordinates firmware recovery through timers and deferred work.

The file is also the persistence boundary for driver-owned iSCSI target configuration. It reads and writes CHAP tables and device database entries in adapter flash, exports boot and flash DDB entries through sysfs, builds runtime libiscsi sessions/connections from firmware DDBs, and preserves enough state to relogin persistent targets after link changes or adapter reset.

## Important APIs, Types, and Entry Points

- Module parameters: `ql4xdisablesysfsboot`, `ql4xdontresethba`, `ql4xextended_error_logging`, `ql4xenablemsix`, `ql4xmaxqdepth`, `ql4xqfulltracking`, `ql4xsess_recovery_tmo`, `ql4xmdcapmask`, and `ql4xenablemd` tune boot sysfs export, recovery reset behavior, logging, interrupt mode, queue depth, session recovery timeout, and minidump behavior.
- SCSI host template: `qla4xxx_driver_template` binds `queuecommand`, SCSI EH callbacks, timeout handling, `sdev_init`, queue depth change, sysfs host groups, and host reset support into the SCSI midlayer.
- iSCSI transport template: `qla4xxx_iscsi_transport` registers offload capabilities and callbacks for session/connection creation, endpoint management, parameter get/set, PDU task handling, CHAP management, flashnode sysfs operations, BSG, ping, and host stats.
- Model dispatch: `struct isp_operations` tables select implementation families for legacy 4xxx, 82xx, and 83xx/84xx adapters. The probe path assigns one of `qla4xxx_isp_ops`, `qla4_82xx_isp_ops`, or `qla4_83xx_isp_ops` so common lifecycle code can call `ha->isp_ops`.
- Core state types used in this chunk include `struct scsi_qla_host` (`ha`), `struct ddb_entry`, `struct dev_db_entry`, `struct qla_endpoint`, `struct qla_conn`, `struct ql4_task_data`, `struct srb`, `struct qla4_work_evt`, `struct qla_ddb_index`, `struct addr_ctrl_blk`, and libiscsi objects such as `iscsi_cls_session`, `iscsi_session`, `iscsi_cls_conn`, `iscsi_conn`, `iscsi_endpoint`, `iscsi_iface`, and flashnode session/connection objects.

## Control Flow

Probe starts in `qla4xxx_probe_adapter()`: enable PCI, allocate an iSCSI SCSI host, initialize `ha`, pick model-specific ops, configure MMIO/PIO space, configure DMA addressing, initialize locks/completions/work lists, allocate DMA queues and pools, set SCSI host limits, add the SCSI host, collect flash/reset-template information for newer adapters, initialize firmware, retry initialization if appropriate, create DPC/task workqueues, request interrupts for 4xxx, enable interrupts, start the one-second timer, set `AF_INIT_DONE`, publish version and boot/flash DDB information, build runtime DDB sessions, login flash DDBs, cache CHAP data, and create IPv4/IPv6 iSCSI ifaces.

Normal I/O enters through `qla4xxx_queuecommand()`. It rejects or completes commands during EEH failure, missing session state, libiscsi not-ready state, DPC reset/quiesce/recovery flags, link down, loopback, ACB restore, and firmware-context reset. If the host is usable, it allocates an SRB from a mempool, attaches it to `qla4xxx_cmd_priv(cmd)`, and sends it to firmware with `qla4xxx_send_command_to_isp()`. Completion later releases DMA and the SRB through `qla4xxx_srb_compl()`, then calls `scsi_done()`.

Userspace/libiscsi connection setup uses `qla4xxx_ep_connect()` to record a sockaddr in a driver endpoint, `qla4xxx_session_create()` to allocate a firmware DDB index and libiscsi session/private `ddb_entry`, `qla4xxx_conn_create()` and `qla4xxx_conn_bind()` to attach a libiscsi connection to the endpoint, and `qla4xxx_conn_start()` to reject duplicate firmware sessions, set firmware DDB parameters, and issue `qla4xxx_conn_open()`. `qla4xxx_conn_destroy()` logs out by DDB. Non-SCSI iSCSI PDUs are allocated with DMA request/response buffers in `qla4xxx_alloc_pdu()`, transmitted via passthrough in `qla4xxx_task_xmit()`, completed in `qla4xxx_task_work()`, and freed in `qla4xxx_task_cleanup()`.

The timer/DPC path drives recovery and asynchronous work. `qla4xxx_timer()` runs every second, scans persistent flash sessions for relogin timers, skips while EEH is busy, probes PCI config to trigger EEH during mailbox waits, runs the 8xxx watchdog or 4xxx heartbeat check, and wakes DPC when work-list entries or DPC flags are present. `qla4xxx_do_dpc()` posts queued AEN/ping events to libiscsi, handles 8xxx unrecoverable/quiescent/IDC/ACB conditions, performs adapter recovery for reset flags, processes AENs, DHCP IP fetches, relogin requests, link changes, and sysfs flash DDB export.

Recovery is centralized in `qla4xxx_recover_adapter()`. It blocks SCSI requests, marks adapter/link offline, sets `DPC_RESET_ACTIVE`, fails sessions, optionally stops firmware for 8xxx firmware-context reset, waits for or performs chip reset, flushes DDB AENs, aborts active commands, reinitializes the adapter, retries or declares the adapter dead, reenables interrupts if online, unblocks SCSI requests, and clears reset-active state. `qla4xxx_dead_adapter_cleanup()` is the terminal cleanup path for unrecoverable adapters.

Flash DDB discovery and login flow starts from `qla4xxx_build_ddb_list()`. If link is down it defers via `AF_BUILD_DDB_LIST`; otherwise it builds a send-target list (`qla4xxx_build_st_list()`), waits for IP configuration, opens send-target DDBs, waits for discovery, removes failed send-targets, then builds normal-target sessions (`qla4xxx_build_nt_list()`). Duplicate detection compares target name, IP, port, and sometimes ISID using tuple helpers; ISID can be adjusted to avoid duplicate multi-session collisions. On reset, existing sessions are updated rather than duplicated, and new sessions are blocked/relogin-marked.

## State and Persistence Behavior

Persistent adapter state is stored primarily in flash CHAP tables, flash DDB records, boot configuration, and firmware DDB state. The driver caches CHAP flash in `ha->chap_list`, protected by `ha->chap_sem`, and updates that cache after writes/deletes. DDB persistence is mediated by flash cookies: valid cookies make target records persistent, and deletion invalidates the cookie or clears the entry depending on adapter generation.

Runtime adapter state is bit-heavy. `ha->flags` tracks online/init/link/EEH/build-list/ST-discovery/firmware-recovery states; `ha->dpc_flags` tracks reset, relogin, link-change, AEN, DHCP, quiesce, restore ACB, sysfs export, and unrecoverable work. `ddb_entry->flags` tracks per-session relogin, boot-target, close-failure, and relogin-disable behavior. Atomic timers on `ddb_entry` implement delayed relogin and relogin timeout/retry for flash DDBs.

Memory state includes one coherent block split into request ring, response ring, and shadow registers; SRBs allocated from a mempool backed by `srb_cachep`; DMA pools for CHAP and firmware DDB operations; firmware dumps; reset templates; and per-task coherent buffers for passthrough PDU request/response data. `qla4xxx_mem_free()` unwinds queues, pools, ioremaps, reset templates, CHAP cache, and PCI regions.

Boot information is discovered through NVRAM on 4xxx and flash boot parameter regions on 8xxx. If boot sysfs export is enabled, boot target, initiator, and ethernet kobjects are created with `iscsi_boot_*` APIs. If disabled, boot targets are flagged as driver-login targets and are not exposed as firmware boot sysfs records.

## Dependencies and Integration Points

This chunk depends on Linux SCSI midlayer, libiscsi transport class, iSCSI boot sysfs, flashnode sysfs, PCI APIs, DMA APIs, workqueues, timers, completions, spinlocks/mutexes, net address parsing/formatting, and kernel netlink attribute parsing. Hardware/firmware operations are imported through local headers and sibling files: mailbox commands, IOCB queueing/completion, interrupt handlers, flash reads/writes, firmware DDB access, reset and 8xxx IDC helpers, CHAP helpers, BSG, sysfs host groups, and debug/logging helpers.

Important integration points are `iscsi_register_transport()` consumers through `qla4xxx_iscsi_transport`, `scsi_add_host()`/`scsi_remove_host()` lifecycle, firmware mailbox APIs such as `qla4xxx_get_ifcb()`, `qla4xxx_set_acb()`, `qla4xxx_set_flash()`, `qla4xxx_get_fwddb_entry()`, and `qla4xxx_conn_open()`, adapter model helpers for 82xx/83xx/84xx, and sysfs/flashnode entry creation through `iscsi_create_flashnode_sess()` and `iscsi_create_flashnode_conn()`.

## Risks and Edge Cases

- This chunk has many firmware-facing DMA buffers and endian conversions. Bugs in size checks, cookie offsets, or le/be conversions can corrupt flash DDB/CHAP contents or misconfigure hardware.
- Session duplication avoidance is complex. Tuple matching sometimes ignores ISID and sometimes compares it; reset and discovery paths must not create duplicate libiscsi sessions for the same firmware target.
- Relogin and logout share mutable per-DDB flags and atomic timers. Incorrect clearing of `DF_RELOGIN` or `DF_DISABLE_RELOGIN` can cause unwanted relogin, logout races, or permanently blocked persistent sessions.
- Adapter recovery is sensitive to generation-specific behavior. `ql4xdontresethba`, IDC "dont reset", firmware-context reset, link state, and `AF_FW_RECOVERY` alter whether the code stops firmware, resets the chip, retries, or declares failure.
- The code contains long sysfs parameter switch statements with direct copies from netlink/flashnode values. Input length validation is present at the attribute header level, but many value reads assume the expected payload size and backing buffers already exist.
- Several operations sleep or wait on firmware states (`schedule_timeout_uninterruptible`, mailbox completions, boot login waits). Calling context and DPC/timer interactions must remain valid to avoid sleeping in atomic context or stalling recovery.
- Boot and flash DDB deletion/logout protect boot targets, but behavior differs when `ql4xdisablesysfsboot` changes whether boot targets are exported versus driver-managed.
- `qla4xxx_get_ep_fwdb()` explicitly notes endpoint cleanup still needs care; session teardown/logout paths destroy endpoints for flash sessions, so leaks or double-destroys are plausible risk areas when setup partially fails.

## Test and Validation Signals

Useful validation signals include successful module load/probe logs showing ISP model, firmware version, IRQ setup, timer/workqueue startup, boot information handling, CHAP cache creation, iface creation, and no failed adapter initialization. Runtime tests should cover SCSI I/O queueing under link-up and reset states, host busy behavior during DPC flags, SRB DMA cleanup, and completions.

Persistence tests should exercise CHAP list/get/set/delete, flashnode add/set/apply/delete, flashnode login/logout, boot target protection, IPv4 and IPv6 DDBs, send-target discovery, duplicate DDB avoidance, and reset-time DDB rebuild without duplicate sessions. Interface tests should validate `get_iface_param()` and `iface_set_param()` round-trips for IPv4, IPv6, VLAN, TCP, and iSCSI options, including flash persistence and ACB reload.

Recovery tests should force link changes, firmware heartbeat failure, 8xxx NEED_RESET/NEED_QUIESCENT states, adapter initialization retry failure, `ql4xdontresethba` behavior, AER/EEH busy state, and relogin timer expiry. Expected signals are blocked sessions on failure, active commands completed with reset/no-connect statuses, DPC flags cleared after work, requests unblocked after successful recovery, and persistent flash sessions relogged or left blocked according to firmware state.

## Chunk Boundary Notes

This report intentionally stops at line 8898, inside the source file just after the main probe path and before adapter removal, SCSI error-handler implementations, PCI error recovery, PCI driver table, and module init/exit definitions. Cross-chunk reconciliation should connect this chunk's template declarations and probe setup to the later removal/EH/AER/module lifecycle code.
