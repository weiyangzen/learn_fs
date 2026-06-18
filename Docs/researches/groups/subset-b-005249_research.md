# subset-b-005249 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_iscsi.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_iscsi.c

Purpose: this file is the libiscsi/SCSI transport glue for the QLogic/Broadcom NetXtreme II offload iSCSI initiator. It exposes `bnx2i_iscsi_transport`, allocates `Scsi_Host`/HBA instances, creates sessions and connections, maps SCSI commands into firmware work queue entries, and drives CNIC option-2 endpoint connect/disconnect flows.

Important APIs, types, and functions: the exported integration points are `bnx2i_alloc_hba()`, `bnx2i_free_hba()`, `bnx2i_drop_session()`, `bnx2i_get_conn_from_id()`, `bnx2i_find_ep_in_ofld_list()`, `bnx2i_find_ep_in_destroy_list()`, `bnx2i_hw_ep_disconnect()`, and the global `bnx2i_iscsi_transport`. The local `bnx2i_host_template` binds the SCSI midlayer to libiscsi handlers and uses `bnx2i_dev_groups` for host sysfs attributes. Endpoint state is held in `struct bnx2i_endpoint`; connection state in `struct bnx2i_conn`; command DMA state in `struct bnx2i_cmd` and its `io_tbl`.

Control flow: HBA creation starts in `bnx2i_alloc_hba()`, which calls `iscsi_host_alloc()`, identifies the CNIC-backed device, maps register windows, allocates the middle-path dummy BD table, initializes endpoint lists and CID queues, sizes SQ/RQ/CQ resources, and registers the host with `iscsi_host_add()`. TCP connect begins in `bnx2i_ep_connect()`: route/HBA selection, CID allocation, QP resource allocation, firmware connection offload, CNIC socket creation, `cm_connect()`, active-list insertion, and doorbell mapping. Sessions and connections are then created by `bnx2i_session_create()` and `bnx2i_conn_create()`, bound by `bnx2i_conn_bind()`, and moved to full feature phase by `bnx2i_conn_start()`. SCSI I/O enters through `bnx2i_task_xmit()`, which maps scatterlists, builds BD chains, copies CDB/LUN data, marks read/write attributes, and sends a firmware SCSI command. Login, NOP-Out, logout, TMF, and text PDUs use `bnx2i_mtask_xmit()` and `bnx2i_iscsi_send_generic_request()`. Disconnect flows run through `bnx2i_ep_disconnect()` and `bnx2i_hw_ep_disconnect()`, then clean CNIC and firmware context with `bnx2i_tear_down_conn()`.

State and persistence behavior: the file maintains per-HBA CID free queues and `conn_cid_tbl`, endpoint lists for offload-pending, active, and destroy states, HBA age checks for stale endpoints, and per-command DMA mapping state. Persistent state is kernel-resident only; firmware/CNIC state is recreated during connection setup and torn down during endpoint disconnect. Synchronization uses `bnx2i_resc_lock`, per-HBA `ep_rdwr_lock`, `net_dev_lock`, wait queues, completion objects, timers, and libiscsi session locks.

Dependencies and integration points: it depends on libiscsi, the SCSI host template, CNIC callbacks (`cm_create`, `cm_connect`, `cm_close`, `cm_abort`, `cm_destroy`, `cm_select_dev`, netlink path updates), PCI DMA APIs, and driver-private firmware send helpers in other bnx2i files. It publishes iSCSI transport callbacks for session/connection lifecycle, parameter reads, endpoint operations, task transmit, stats, path update, and cleanup.

Risks: the highest-risk paths are asynchronous endpoint state transitions, timeouts, and cleanup races. CID queue operations rely on external locking discipline. `bnx2i_map_scsi_sg()` uses `BUG_ON()` for overlarge SG counts and byte-count mismatches, so malformed assumptions become fatal. Connection teardown has device-generation checks and special 57710 timeout behavior, but stale CNIC sockets, delayed callbacks, or adapter removal during recovery remain fragile. The code flushes signals after interruptible waits, which can mask user-visible interruption semantics.

Test signals: useful validation includes successful HBA probe/remove, sysfs host visibility, iSCSI login/logout over IPv4 and IPv6 routes, command I/O with read/write SG lists near `ISCSI_MAX_BDS_PER_CMD`, session recovery timeout, TMF cleanup, CNIC unregister/removal during active sessions, endpoint poll timeout, 5708/5709/57710 queue-size boundaries, and leak checks for DMA BD tables and login resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_iscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_sysfs.c

Purpose: this file exposes bnx2i per-host sysfs tuning attributes for send queue size and command-cell/history queue size. It is tied into `bnx2i_host_template.shost_groups` through `bnx2i_dev_groups`.

Important APIs, types, and functions: `bnx2i_dev_to_hba()` maps a sysfs `struct device` to the driver HBA via `class_to_shost()` and `iscsi_host_priv()`. `bnx2i_show_sq_info()` and `bnx2i_set_sq_info()` implement the `sq_size` attribute. `bnx2i_show_ccell_info()` and `bnx2i_set_ccell_info()` implement `num_ccell`. The exported symbol is the `const struct attribute_group *bnx2i_dev_groups[]` array referenced by the host template.

Control flow: reads format the current HBA values as hex. Writes parse a hex integer with `sscanf()`, reject changes while `hba->ofld_conns_active` is nonzero, and update the in-memory HBA configuration only when values are in range. SQ writes also require power-of-two sizing and choose maximums based on whether the device is a 57710-class adapter or a 570x-class adapter. CCELL writes enforce `BNX2I_CCELLS_MIN` to `BNX2I_CCELLS_MAX`.

State and persistence behavior: settings are runtime HBA fields, not persistent across driver reloads or device reprobe. They influence later connection/session queue resource sizing, but writes are blocked once offloaded connections are active. No lock is taken around the field updates; correctness relies on the active-connection guard and sysfs serialization.

Dependencies and integration points: this file depends on `bnx2i.h`, SCSI host class mapping, libiscsi host private storage, and constants from the bnx2i driver. It integrates with the main iSCSI file through `bnx2i_dev_groups`.

Risks: invalid input silently leaves the old value while still returning `count`, which can surprise management tools. Busy rejection returns `0` rather than `-EBUSY`, which is a weak sysfs signal. Lack of explicit locking is acceptable only if no connection setup can race between the busy check and assignment.

Test signals: verify attribute presence under the bnx2i host, hex read formatting, accepted and rejected SQ sizes, non-power-of-two rejection, 570x versus 57710 max enforcement, CCELL bounds, and busy write behavior with an active offloaded session.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bvme6000_scsi.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/bvme6000_scsi.c

Purpose: this is a platform wrapper for BVME6000 NCR53C710 SCSI hardware. It wires board-specific physical addresses, IRQs, and NCR53C700 core parameters into the generic `53c700` SCSI driver.

Important APIs, types, and functions: `bvme6000_scsi_driver_template` supplies the SCSI host template name/proc name and target ID. `bvme6000_probe()` allocates `struct NCR_700_Host_Parameters`, populates BVME6000-specific fields, calls `NCR_700_detect()`, requests `BVME_IRQ_SCSI`, sets platform driver data, and scans the host. `bvme6000_device_remove()` reverses that setup. Module init/exit register and unregister both the platform driver and a simple platform device.

Control flow: module init registers `bvme6000_scsi_driver`, then creates a `"bvme6000-scsi"` platform device. Probe exits with `-ENODEV` unless `MACH_IS_BVME6000` is true. On the target machine it allocates host parameters, sets `base`, `clock`, `chip710`, `dmode_extra`, `dcntl_extra`, and `ctest7_extra`, detects the NCR core, sets host base/ID/IRQ, installs `NCR_700_intr`, and runs `scsi_scan_host()`. Remove calls `scsi_remove_host()`, `NCR_700_release()`, frees hostdata, and frees the IRQ.

State and persistence behavior: state is limited to the platform device pointer, the SCSI host, and host-private NCR parameters. There is no persistent storage. Resource ownership is linear: platform device owns the SCSI host and IRQ after successful probe.

Dependencies and integration points: it depends on m68k BVME6000 platform definitions, `53c700.h`, SCSI host/device/transport headers, and Linux platform driver APIs. It is integrated with the generic NCR53C700 core rather than implementing SCSI protocol logic itself.

Risks: the hard-coded `hostdata->clock = 40` comment notes CPU-clock dependence, so timing may be wrong on variants. Error paths must keep hostdata, host refs, and IRQ ownership balanced. Probe returns `-ENODEV` both for wrong machine and several setup failures, which limits diagnostics.

Test signals: validate on BVME6000 hardware or emulation that probe reaches `scsi_scan_host()`, IRQ delivery invokes `NCR_700_intr`, remove unloads cleanly, and wrong-machine builds fail probe without leaking the registered platform device or driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bvme6000_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ch.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/ch.c

Purpose: this file implements the SCSI media changer character driver. It creates `/dev` nodes on major `SCSI_CHANGER_MAJOR`, probes `TYPE_MEDIUM_CHANGER` SCSI devices, discovers changer element layout, and translates changer ioctls from `<linux/chio.h>` into SCSI CDBs such as `READ_ELEMENT_STATUS`, `MOVE_MEDIUM`, `EXCHANGE_MEDIUM`, `POSITION_TO_ELEMENT`, `SEND_VOLUME_TAG`, and `INITIALIZE_ELEMENT_STATUS`.

Important APIs, types, and functions: `scsi_changer` is the main object, holding the `scsi_device`, element base/count tables, data-transfer element device references, volume-tag support, minor number, mutex, kref, and list node. `ch_do_scsi()` is the common command executor using `scsi_execute_cmd()` and sense translation through `ch_find_errno()`. `ch_readconfig()` reads mode page `0x1d`, configures element ranges, vendor ranges, and transfer-device lookups. `ch_ioctl()` implements `CHIOGPARAMS`, `CHIOGVPARAMS`, `CHIOPOSITION`, `CHIOMOVE`, `CHIOEXCHANGE`, `CHIOGSTATUS`, compat `CHIOGSTATUS32`, `CHIOGELEM`, `CHIOINITELEM`, `CHIOSVOLTAG`, and falls back to `scsi_ioctl()`. `ch_probe()`/`ch_remove()` bridge to the SCSI driver model, while `changer_fops` exposes open/release/ioctl.

Control flow: module init registers the `scsi_changer` class, the fixed char major, and the SCSI driver. Probe allocates a changer, reserves an IDR minor, gets a SCSI device reference, creates the class device, reads configuration under `ch->lock`, optionally initializes elements, and stores driver data. Open finds the object by minor under `ch_index_lock`, increments the kref, gets a SCSI device ref, and publishes it as `file->private_data`. Ioctl blocks during SCSI error processing, validates user ranges, serializes medium operations with `ch->lock`, builds CDBs, and copies results to or from user memory. Remove deletes the IDR entry, destroys the device node, drops the SCSI reference, and releases the kref.

State and persistence behavior: configuration is cached in memory after probe: `firsts[]`, `counts[]`, optional vendor ranges, detected data-transfer devices, and `voltags`. If reads with volume tags fail, `voltags` is downgraded for future reads. Runtime state is protected by `ch->lock`; object lifetime is split between SCSI device references and `kref`.

Dependencies and integration points: it depends on SCSI core probing, `scsi_execute_cmd()`, SCSI sense helpers, char device registration, class devices, IDR allocation, compat ioctl helpers, and user ABI structures from `<linux/chio.h>`.

Risks: the ioctl ABI exposes many user-controlled element indexes and buffers; range checks are present but all status parsing assumes 512-byte temporary buffers and fixed offsets. `ch_gstatus()` appears to call `ch_read_element_status()` twice per element, which is inefficient and can produce inconsistent results if media moves between reads. Transfer-device lookup stores SCSI device references and needs balanced release behavior through changer teardown. Some sense-to-errno mappings are explicitly approximate.

Test signals: test attach/remove, open during remove, all ioctl range errors, compat `CHIOGSTATUS32`, initialization timeout, element-status parsing with and without volume-tag support, media move/exchange/position success and sense failures, fallback `scsi_ioctl()`, reference leak checks, and concurrent ioctls across multiple open file descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/constants.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/constants.c

Purpose: this file provides shared SCSI debug/stringification helpers: opcode names, service-action names, sense-key text, additional sense code text, host-byte result names, and SCSI midlayer return-code names.

Important APIs, types, and functions: the key exported functions are `scsi_sense_key_string()`, `scsi_extd_sense_format()`, `scsi_hostbyte_string()`, and `scsi_mlreturn_string()`. `scsi_opcode_sa_name()` is a non-exported helper that maps an opcode and service action to CDB and service-action strings. Tables include `cdb_byte0_names`, service-action `value_name_pair` arrays, `sa_names_arr`, `additional[]`, generated `additional_text` from `sense_codes.h`, fallback ranged `additional2[]`, `snstext`, `hostbyte_table`, and `scsi_mlreturn_arr`.

Control flow: opcode/service-action lookup first rejects vendor-specific opcodes, optionally names opcode byte 0, finds a matching service-action table, then scans it for the action value. Sense-key lookup is a direct bounds-checked table read. Additional sense lookup builds a 16-bit ASC/ASCQ key, scans compact `additional[]` entries while accumulating offsets into the concatenated `additional_text` string table, then checks ranged fallback cases such as diagnostic failures and tagged overlapped commands. Host-byte lookup uses `host_byte(result)` to index `hostbyte_table`. Midlayer return lookup scans the named result array.

State and persistence behavior: all state is static read-only table data built into the kernel object. There is no mutation, allocation, locking, or persistence beyond the module/kernel image.

Dependencies and integration points: it includes SCSI core headers and is used by diagnostics across SCSI drivers and error handling. It relies on `sense_codes.h` to generate compact ASC/ASCQ metadata and text. Exported symbols are available to other kernel modules.

Risks: table drift versus current SPC/SBC/MMC standards is the main correctness risk. `scsi_extd_sense_format()` is O(number of sense codes), which is fine for diagnostics but not ideal for hot paths. Some opcode names are combined or overloaded, so users should treat them as diagnostic labels, not as authoritative parsers.

Test signals: unit-style tests can verify known sense key, ASC/ASCQ, host byte, and midlayer return mappings; unknown values should return `NULL`; ranged `additional2[]` entries should set `fmt`; generated `sense_codes.h` offsets should remain aligned after updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/constants.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Kconfig

Purpose: this Kconfig entry declares the Chelsio FCoE offload SCSI driver option `SCSI_CHELSIO_FCOE`.

Important APIs, types, and functions: the configuration symbol is a `tristate` labeled "Chelsio Communications FCoE support". It depends on `PCI`, `SCSI`, and `SCSI_FC_ATTRS`, and selects `FW_LOADER`. The help text identifies T4-based 10Gb converged network adapters and says the module name is `csiostor`.

Control flow: no runtime control flow exists here. Build-time selection controls whether the csiostor object list in the Makefile is compiled into the kernel or built as a loadable module.

State and persistence behavior: state is kernel build configuration only. The selected module dependency on firmware loading is important because runtime code in `csio_hw.c` calls `request_firmware()` for firmware images and configuration files.

Dependencies and integration points: the symbol integrates with the SCSI driver Kconfig tree, FC transport attribute support, PCI device support, firmware loader support, and `drivers/scsi/csiostor/Makefile`.

Risks: the help text mentions T4-era adapters while the code also contains T5/T6 handling, so documentation may underspecify hardware coverage. Missing `SCSI_FC_ATTRS` or `FW_LOADER` support would break required FC transport and firmware/config loading behavior.

Test signals: validate `=m`, `=y`, and disabled builds, dependency gating when `SCSI_FC_ATTRS` is off, automatic firmware loader selection, and that the resulting module is named `csiostor`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Makefile -->
## sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Makefile

Purpose: this Makefile builds the Chelsio FCoE driver and sets the include path required for Chelsio cxgb4 hardware definitions.

Important APIs, types, and functions: `ccflags-y` adds `-I$(srctree)/drivers/net/ethernet/chelsio/cxgb4`. `obj-$(CONFIG_SCSI_CHELSIO_FCOE) += csiostor.o` ties the object to the Kconfig symbol. `csiostor-objs` composes the module from `csio_attr.o`, `csio_init.o`, `csio_lnode.o`, `csio_scsi.o`, `csio_hw.o`, `csio_hw_t5.o`, `csio_isr.o`, `csio_mb.o`, `csio_rnode.o`, and `csio_wr.o`.

Control flow: this is build orchestration only. When the Kconfig symbol is enabled, kbuild links the listed objects into `csiostor.o`; when built as a module, the same aggregate becomes `csiostor.ko`.

State and persistence behavior: no runtime state exists. Build state is determined by the selected kernel configuration and source tree include layout.

Dependencies and integration points: it integrates the csiostor driver with Chelsio cxgb4 register/header definitions and with the Linux kbuild object aggregation model. The source list shows the driver split between attributes, initialization, lnode/rnode state, SCSI I/O, hardware, T5 hardware specifics, ISR, mailbox, and work-request handling.

Risks: include-path coupling to cxgb4 means changes in networking driver headers can affect this SCSI driver. The object list must remain synchronized with exported symbols across the csiostor subsystem; missing one object can produce link failures or incomplete runtime behavior.

Test signals: build with `CONFIG_SCSI_CHELSIO_FCOE=m` and `=y`, run `modpost`, verify all object dependencies resolve, and check that cxgb4 header changes do not break csiostor compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_attr.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_attr.c

Purpose: this file is the FC transport integration layer for the Chelsio FCoE driver. It registers/unregisters remote ports, populates FC host/rport sysfs attributes, exposes FC transport function templates, manages NPIV virtual port lifecycle, reads FC statistics, and translates dev-loss timeouts into serialized driver events.

Important APIs, types, and functions: exported driver-facing routines include `csio_reg_rnode()`, `csio_unreg_rnode()`, `csio_lnode_async_event()`, and `csio_fchost_attr_init()`. The public transport templates are `csio_fc_transport_funcs` for physical ports and `csio_fc_transport_vport_funcs` for vports. Key local helpers include `csio_get_host_port_id()`, `csio_get_host_port_type()`, `csio_get_host_port_state()`, `csio_get_host_speed()`, `csio_get_host_fabric_name()`, `csio_get_stats()`, `csio_set_rport_loss_tmo()`, `csio_vport_set_state()`, `csio_fcoe_alloc_vnp()`, `csio_fcoe_free_vnp()`, `csio_vport_create()`, `csio_vport_delete()`, `csio_vport_disable()`, and `csio_dev_loss_tmo_callbk()`.

Control flow: remote-port registration builds `fc_rport_identifiers`, creates an rport with `fc_remote_port_add()`, stores the driver rnode pointer in `rport->dd_data`, copies max frame size/classes, updates roles via `fc_remote_port_rolechg()`, and records `scsi_target_id`. Local-node async events refresh vport state or host attributes. Vport create allocates a new lnode/shost, validates requested WWNN/WWPN, ensures WWPN uniqueness, allocates a firmware VNP with mailbox retry on `-EBUSY`, initializes FC attributes, and stores the lnode in vport private data. Vport delete/disable block SCSI requests, clean I/O, stop or close lnode state, free firmware VNPs, and exit shosts. Dev-loss callback queues `CSIO_EVT_DEV_LOSS` and schedules the event worker unless removal or rnode recovery makes it unnecessary.

State and persistence behavior: the file updates in-memory `csio_lnode`, `csio_rnode`, `fc_rport`, and `fc_vport` state. Firmware VNP allocation persists in adapter firmware until explicitly freed. Host statistics accumulate in `ln->fch_stats` by adding hardware counters and lnode request counters; reset age is derived from `hw->stats.n_reset_start`.

Dependencies and integration points: it depends on FC transport class APIs, SCSI host request blocking, Chelsio mailbox helpers, lnode/rnode lookup/state helpers, FCoE firmware commands, and the hardware event queue in `csio_hw.c`.

Risks: mailbox commands run while holding `hw->lock` except for retry sleeps, so latency and lock ordering matter. Vport create error paths must unwind shost allocation and firmware VNP allocation correctly. Role updates assume existing `rn->rport` when roles are already set. Dev-loss enqueues a pointer payload, so rnode lifetime must outlive event processing.

Test signals: validate rport add/delete and role changes, sysfs FC attribute correctness, link speed mapping, fabric-name lookup, stats reads, NPIV create/delete/disable/enable including duplicate WWPN and invalid WWN failures, mailbox busy retry, dev-loss timeout event scheduling, and removal races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_defs.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_defs.h

Purpose: this header provides common Chelsio FCoE definitions, generic state-machine helpers, list helpers, stats macros, WWN validation, 64-bit MMIO fallbacks, and assertion macros used across csiostor.

Important APIs, types, and functions: macros include `CSIO_INVALID_IDX`, `CSIO_INC_STATS`, `CSIO_DEC_STATS`, `CSIO_VALID_WWN`, `CSIO_DID_MASK`, `CSIO_WORD_TO_BYTE`, `csio_list_next`, `csio_list_prev`, `CSIO_ASSERT`, and `CSIO_DB_ASSERT`. Fallback inline `readq()` and `writeq()` are defined when absent. State-machine definitions include `enum csio_ln_ev`, `csio_sm_state_t`, `struct csio_sm`, and helpers `csio_set_state()`, `csio_init_state()`, `csio_post_event()`, `csio_get_state()`, and `csio_match_state()`.

Control flow: `csio_post_event()` invokes the current state function directly, making these state machines synchronous unless callers arrange deferred context elsewhere. `csio_set_state()` and `csio_init_state()` update the function pointer in `struct csio_sm`. `csio_match_state()` compares the current function pointer to a known state implementation. `csio_list_deleted()` checks whether a list head points to itself in both directions.

State and persistence behavior: this header does not own storage. It defines how other objects store state as function pointers in `struct csio_sm` and how stats fields are incremented/decremented. There is no persistence beyond the in-memory driver objects using these helpers.

Dependencies and integration points: it depends on Linux kernel, list, timer, PCI, jiffies, and bug headers. It is foundational for csiostor lnode and hardware state machines and for shared stats accounting.

Risks: function-pointer state machines are compact but provide little type safety; the helpers accept `void *`, so misuse can compile and fail at runtime. `CSIO_VALID_WWN()` only checks the high nibble of the first byte, which is a narrow validation. `CSIO_ASSERT()` maps to `BUG_ON()`, making assertion failures fatal.

Test signals: compile coverage across architectures with and without native `readq/writeq`, state-machine transition tests for expected function-pointer matches, debug builds with `__CSIO_DEBUG__`, and static analysis for `void *` helper misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw.c

Purpose: this is the core hardware-management file for the Chelsio FCoE driver. It handles adapter identification, firmware/VPD/flash access, firmware upgrade and configuration-file loading, mailbox-driven bring-up, port enablement, interrupt enable/disable and slow interrupt handling, hardware state-machine transitions, firmware event queues, management request timeouts, and module-level hardware initialization/exit.

Important APIs, types, and functions: externally visible functions include `csio_is_hw_ready()`, `csio_is_hw_removing()`, `csio_hw_wait_op_done_val()`, `csio_hw_tp_wr_bits_indirect()`, `csio_set_reg_field()`, `fwcap_to_fwspeed()`, `fwcaps16_to_caps32()`, `fwcaps32_to_caps16()`, `lstatus_to_fwcap()`, `csio_hw_intr_disable()`, `csio_hw_fatal_err()`, `csio_handle_intr_status()`, `csio_hw_slow_intr_handler()`, `csio_enqueue_evt()`, `csio_evtq_flush()`, `csio_evtq_worker()`, `csio_fwevtq_handler()`, `csio_mgmt_req_lookup()`, `csio_hw_start()`, `csio_hw_stop()`, `csio_hw_reset()`, `csio_hw_init()`, and `csio_hw_exit()`. Major local subsystems include flash/VPD helpers, HELLO/BYE/RESET mailbox helpers, firmware compatibility and upgrade checks, configuration-file processing, port capability conversions, state handlers `csio_hws_*`, interrupt leaf handlers, mailbox timeout/completion workers, event queue allocation/processing, and management timer cleanup.

Control flow: `csio_hw_init()` initializes the hardware object, chip ops, mailbox/work-request/SCSI/management modules, and preallocates firmware event entries. `csio_hw_start()` posts `CSIO_HWE_CFG` into the synchronous hardware state machine. Configuration reads device readiness, flash parameters, PCIe timeout, firmware revision, performs HELLO, reads VPD, optionally flashes firmware from the filesystem, checks firmware config support, loads host or flash config, validates FCoE capabilities, reads device parameters, initializes SGE, and posts `CSIO_HWE_INIT`. Initialization then issues `FW_INITIALIZE_CMD` when master and not already initialized, reads FCoE resource info, configures queues, enables ports, and posts ready. Ready-state reset, suspend, remove, firmware download, and PCI error events quiesce I/O, disable interrupts, stop event queues, clean mailboxes/management, notify lnodes, destroy queues, reset or BYE the adapter, and reconfigure or remove as appropriate.

State and persistence behavior: persistent-on-card state includes serial flash firmware, flash configuration files, VPD data, firmware-selected PF master state, firmware resources, and port/link configuration. Runtime state includes `hw->flags`, `hw->fw_state`, `hw->pfn`, `hw->port_vec`, `hw->pport[]`, queue counts, firmware/event queues, mailbox queues, stats, reset counters, and current/previous hardware events. The event queue uses preallocated `csio_evt_msg` entries and `CSIO_HWF_FWEVT_PENDING/STOP` flags; management requests are tracked in `mgmtm->active_q` with periodic timeout decrement.

Dependencies and integration points: it depends heavily on Chelsio register definitions and chip ops, PCI config space, firmware loader, mailbox builders/processors, work-request queue setup, SCSI I/O cleanup, lnode notifications, FCoE firmware event handling, T5/T6 firmware naming, and kernel timers/workqueues. It is the control-plane center that `csio_attr.c`, `csio_init.c`, ISR code, mailbox code, and SCSI code rely on.

Risks: firmware flash/upgrade is inherently high impact; failures can leave the adapter unusable. Several flows drop and reacquire `hw->lock` around sleeps or firmware loads, so state changes during those windows must be safe. Event queue payload copying from SG fragments must respect `CSIO_EVT_MSG_SIZE`. Many interrupt handlers escalate to fatal hardware disable, so false positives have large blast radius. `csio_sge_intr_handler()` calls `csio_handle_intr_status()` twice on the same register, which may clear on the first call and alter fatal accounting. State-machine calls are synchronous and function-pointer based, so unexpected recursive events or missing locks are hard to reason about.

Test signals: cover cold start as master and slave PF, initialized and uninitialized firmware states, missing/incompatible firmware files, firmware upgrade refusal and success, config file fallback from host to flash to firmware default, VPD checksum failure, flash read/write verification, link capability conversion for 16-bit and 32-bit firmware APIs, queue configuration failure, port enable failure, reset retries, suspend/resume, PCI error recovery, remove/BYE path, event queue stop/drop behavior, dev-loss event handling, mailbox timeout callbacks, and each slow interrupt fatal/nonfatal path with register-level fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw.c -->
