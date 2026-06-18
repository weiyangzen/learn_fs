# Research: subset-b-005246

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_attr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_attr.c

## Purpose
`bfad_attr.c` binds the BFAD initiator driver to the Linux FC transport and SCSI host sysfs attribute surfaces. It translates BFA/FCS adapter, port, target, statistics, vport, and firmware attributes into `fc_host_*`, `fc_starget_*`, FC vport operations, BSG hooks, and read-only host attributes.

## Important APIs, Types, and Functions
The file exports two `struct fc_function_template` instances: `bfad_im_fc_function_template` for the physical port and `bfad_im_vport_fc_function_template` for NPIV vports. Dynamic target callbacks (`bfad_im_get_starget_port_id`, `_node_name`, `_port_name`) locate `bfad_itnim_s` by SCSI target ID under `bfad_lock`. Host callbacks expose port ID, type, state, FC4s, speed, fabric WWN, and stats through BFA/FCS helpers. `bfad_im_get_stats` and `bfad_im_reset_stats` issue asynchronous BFA port-stat commands and wait on `bfad_hal_comp`. Vport callbacks create/delete/disable vports through `bfad_vport_create`, `bfa_fcs_vport_lookup`, `bfa_fcs_vport_stop/start`, and `bfa_fcs_vport_delete`. Sysfs show functions expose serial, model, model description, WWNs, symbolic name, hardware/firmware/option-ROM versions, port count, driver name/version, and discovered-port count.

## Control Flow
Transport callbacks enter from FC transport or sysfs, recover `bfad_im_port_s` from `shost->hostdata[0]`, and then call into BFA/FCS. Read-only lookups are mostly synchronous. Operations that touch firmware state lock `bfad->bfad_lock`, start BFA work, unlock, and wait for completion. Vport creation fills a `bfa_lport_cfg_s`, checks the preboot vport list for preserved preboot state, calls the BFAD vport constructor, looks up the resulting FCS vport, initializes the new vhost FC transport fields, and stores `fc_vport->dd_data`. Deletion marks `BFAD_PORT_DELETE`, starts FCS deletion, waits for callback completion, removes the SCSI host, unlinks the vport, and frees it.

## State and Persistence
The file mutates transport-visible host fields, `fc_vport` state, `fc_vport->dd_data`, `vport->drv_port.flags`, `vport->comp_del`, and per-port sysfs attribute values derived from live adapter state. Adapter names and firmware versions are read from BFA state; there is no direct on-disk persistence here. Vport preboot awareness is inherited from `bfad->pbc_vport_list`.

## Dependencies and Integration Points
It depends on `bfad_drv.h`, `bfad_im.h`, Linux FC transport, SCSI host sysfs, and many BFA/FCS APIs: `bfa_fcport_get_attr`, `bfa_port_get_stats`, `bfa_fcs_lport_get_attr`, `bfa_fcs_vport_*`, and adapter query helpers. It integrates BSG by wiring `bfad_im_bsg_request` and `bfad_im_bsg_timeout` into the physical-port FC template.

## Risks
Most callbacks assume `shost->hostdata[0]`, `rport->dd_data`, and FCS lookup results remain valid while locks are held. `strcpy` is used for vport symbolic names after checking only `strlen(vname) > 0`; safety depends on FC transport buffer sizing. Several operations can wait indefinitely if firmware callbacks do not complete. `bfad_im_num_of_discovered_ports_show` allocates a fixed 2048-entry qualifier buffer and reports BFA-filled counts, so behavior depends on BFA enforcing bounds.

## Test Signals
Useful signals are FC transport sysfs reads, `fc_vport_create/delete/disable` exercises, `issue_lip`, `get_fc_host_stats`/reset behavior, and BSG availability on physical hosts. Negative tests should cover invalid WWNs, max vport failures, firmware command failures, disabled vports, and missing `itnim` target mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_bsg.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_bsg.c

## Purpose
`bfad_bsg.c` implements the driver-private FC BSG interface. It is an ioctl-like command dispatcher for adapter, port, lport/rport, vport, FCP initiator, diagnostics, flash, PHY, boot, QoS, trunking, LUN masking, FRU/VPD, debug, and FC ELS/CT pass-through operations.

## Important APIs, Types, and Functions
The main exported entry points are `bfad_im_bsg_request` and `bfad_im_bsg_timeout`. Vendor commands enter `bfad_im_bsg_vendor_request`, are copied from request scatterlists into a linear buffer, and then dispatched by `bfad_iocmd_handler`. That handler maps `IOCMD_*` values to many `bfad_iocmd_*` helpers. ELS/CT pass-through enters `bfad_im_bsg_els_ct_request`, which consumes a userspace `bfa_bsg_fcpt_s`, resolves lport/rport context, maps request and response buffers through coherent DMA via `bfad_fcxp_map_sg`, sends through `bfa_fcxp_send`, and completes from `bfad_send_fcpt_cb`.

## Control Flow
Vendor request flow is simple: allocate `payload_kbuf`, `sg_copy_to_buffer`, dispatch, copy the updated command/result block to reply scatterlists, fill `fc_bsg_reply`, and call `bsg_job_done` on success. The dispatcher has broad categories: IOC enable/disable/getattr/stats; port enable/disable/config/stats; LPORT/RPORT/VPORT/Fabric queries; rate limiting and FCPIM stats; PCI function and adapter mode management; CEE/SFP/flash/diagnostic/PHY operations; debug trace/core/log controls; boot/ethboot/preboot; trunk/QoS/VF; LUN mask and throttle; TFRU/FRUVPD. Many handlers lock `bfad_lock`, issue a BFA module call, unlock, and wait on a `bfad_hal_comp`. Variable payload handlers verify `payload_len == sizeof(header) + expected_buffer_size` with `bfad_chk_iocmd_sz`.

ELS/CT flow uses `bfa_bsg_data` embedded after `fc_bsg_request` to copy a control block from an arbitrary user pointer. It verifies local port existence and online state, optionally resolves a remote port for RPT commands, allocates DMA request/response buffers, sends an FCXP, waits for completion, populates CT/ELS reply status, copies DMA response into the BSG reply scatterlist, copies the updated control block back to userspace, and completes the job only on `BFA_STATUS_OK`.

## State and Persistence
Handlers mutate live driver and firmware state: IOC enable/disable state, adapter/port names, port topology/speed/ALPA/max frame size, BBCR, rate limiting, QoS, trunking, flash partitions, boot/PXE configuration, LUN masking, queue-scan flags, profiling state, port logs, trace state, firmware core offsets, and FRU/VPD contents. Runtime stats are read or cleared in BFA/FCS structures. Persistent writes occur indirectly through BFA flash/FRU helpers for boot config, ethboot config, flash parts, PHY firmware, and FRUVPD/TFRU data.

## Dependencies and Integration Points
This file depends on the BSG ABI in `bfad_bsg.h`, BFAD core state in `bfad_drv.h`, IM helpers in `bfad_im.h`, Linux BSG scatterlist helpers, usercopy, PCI DMA APIs, and almost every BFA service module. It is wired into the FC transport template from `bfad_attr.c`.

## Risks
The surface is privileged and very broad. Some commands use direct userspace pointers (`bfa_bsg_data.payload`) in addition to BSG scatterlists, so compat, bounds, and TOCTOU issues need attention. Several handlers perform unbounded waits on firmware completions. Many commands trust structure fields for buffer sizes after only aggregate payload-length checks; integer overflow and large allocation behavior should be scrutinized. `bfad_iocmd_lunmask` calls SCSI host operations while holding `bfad_lock`, and `bfad_reset_sdev_bflags` takes `host_lock`, so lock ordering matters. Flash/PHY/FRU write commands can persistently alter adapter state.

## Test Signals
Test with representative BSG vendor commands for each category, malformed payload lengths, zero counts, unknown WWNs/VF IDs, offline ports, firmware failure completions, and large buffer sizes. ELS/CT tests should validate HST versus RPT paths, unknown remote ports, timeout behavior (`-EAGAIN`), DMA cleanup on all error exits, and reply length/status consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_bsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_bsg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_bsg.h

## Purpose
`bfad_bsg.h` defines the private userspace/kernel ABI for BFAD vendor-specific FC BSG commands. It enumerates all `IOCMD_*` operation codes and declares the command/result payload structures consumed by `bfad_bsg.c`.

## Important APIs, Types, and Functions
The leading enum assigns stable numeric command IDs for IOC, IOCFC, port, lport/rport/vport, fabric, rate-limit, FCPIM, ITNIM, PCI function, adapter mode, BBCR, FAA, CEE, SFP, flash, diagnostics, PHY, debug, boot, trunk, QoS, VF, LUN masking, D-port, throttle, TFRU, FRUVPD, and FC pass-through commands. Nearly every structure begins with `bfa_status_t status` and `u16 bfad_num`, then command-specific identifiers and payloads. Important structures include `bfa_bsg_ioc_info_s`, `bfa_bsg_ioc_attr_s`, `bfa_bsg_port_stats_s`, `bfa_bsg_lport_get_rports_s`, `bfa_bsg_rport_*`, `bfa_bsg_flash_s`, `bfa_bsg_debug_s`, `bfa_bsg_fcpim_lunmask_s`, `bfa_bsg_tfru_s`, `bfa_bsg_fruvpd_s`, and `bfa_bsg_fcpt_s`. `struct bfa_bsg_data` is packed and carries a byte length plus a userspace pointer for FC pass-through control data. `bfad_chk_iocmd_sz` validates composite command sizes.

## Control Flow
The header itself has no execution flow, but it defines the layout expected by `bfad_im_bsg_vendor_request` and `bfad_im_bsg_els_ct_request`. Vendor command buffers are passed inline through BSG scatterlists and may include trailing payload bytes immediately after the command structure. FC pass-through uses `bfa_bsg_data` in the request header to point to a separate userspace `bfa_bsg_fcpt_s` block.

## State and Persistence
The structs describe both transient read/write state and persistent operations. Name, port, flash, boot, ethboot, PHY update, FRU/VPD, QoS, trunking, LUN mask, and debug control commands can change device or driver state. Query structs return snapshots of BFA/FCS state and hardware statistics. The ABI embeds fixed maximum buffer sizes for TFRU and FRUVPD transfers.

## Dependencies and Integration Points
It includes `bfa_defs.h` and `bfa_defs_fcs.h`, so the ABI exposes BFA-defined WWN, MAC, stats, adapter, port, diagnostic, QoS, boot, and LUN-mask types. `bfad_bsg.c` relies on the structure sizes exactly when checking payload lengths and copying data.

## Risks
This is an ABI header: changing enum ordering, field order, packing, or fixed sizes breaks userspace tools. Many structs contain native C types and `u64` pointers, making 32-bit userspace compatibility and endian assumptions important. Inline buffers such as `BFA_MAX_FRUVPD_TRANSFER_SIZE` require careful payload-size validation in callers.

## Test Signals
ABI tests should assert structure sizes, enum values, packed `bfa_bsg_data` layout, and command size checks across architectures. Userspace tools should be tested against mismatched payload lengths and unsupported command IDs to confirm stable failure status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_bsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_debugfs.c

## Purpose
`bfad_debugfs.c` exposes optional debugfs files under `bfa/pci_dev:<pci_name>` for driver trace, firmware trace, saved firmware trace, register reads, and register writes.

## Important APIs, Types, and Functions
`struct bfad_debug_info` carries an output buffer, inode private pointer, and buffer length. Open handlers prepare trace buffers (`bfad_debugfs_open_drvtrc`, `_fwtrc`, `_fwsave`) or register context (`bfad_debugfs_open_reg`). `bfad_debugfs_read` and `bfad_debugfs_lseek` serve trace data. `bfad_debugfs_write_regrd` parses `addr:len`, validates register range through `bfad_reg_offset_check`, reads BAR0 registers into `bfad->regdata`, and `bfad_debugfs_read_regrd` returns/free that buffer. `bfad_debugfs_write_regwr` parses `addr:val` and writes one BAR0 word. `bfad_debugfs_init` and `bfad_debugfs_exit` create/remove the root, per-port directory, and five files.

## Control Flow
When enabled by `bfa_debugfs_enable`, port initialization creates the root and per-PCI directory. Reads of `drvtrc` directly expose the in-memory `bfad->trcmod`; reads of `fwtrc`/`fwsave` allocate a vmalloc buffer and ask the IOC debug helpers to fill it under `bfad_lock`. Register read is two-step: write request string to `regrd`, then read the binary register data. Register write is immediate after parsing and range checking. Exit removes each file, the per-port directory, and the root when the atomic port count reaches zero.

## State and Persistence
State is transient except register writes, which mutate device registers directly. `bfad->regdata` and `bfad->reglen` store one pending register-read result per adapter. Trace buffers are snapshots or direct views of runtime trace state. The debugfs root lifetime is shared by all ports through `bfa_debugfs_port_count`.

## Dependencies and Integration Points
The file depends on Linux debugfs, BAR accessors from the BFA IOC layer, BFAD core state, trace modules, and `bfa_ioc_debug_fwtrc/fwsave`. It is called from the BFAD port lifecycle via prototypes in `bfad_drv.h`.

## Risks
This is a powerful diagnostic interface. `regwr` writes raw device registers and can destabilize hardware. `regrd` stores state in `bfad->regdata`, so concurrent readers/writers can race because only register accesses are locked, not all buffer lifetime transitions. `bfad_debugfs_lseek` uses `debug->buffer_len`, which is not initialized for register files opened through `bfad_debugfs_open_reg`. Permissions restrict writes to owner, but debugfs is not a stable or hardened ABI.

## Test Signals
Mount debugfs and verify file creation/removal across multiple ports and disabled mode. Exercise trace reads, invalid register parse strings, boundary offsets for CT/CB register windows, concurrent `regrd` writes/reads, and module unload with open files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_drv.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_drv.h

## Purpose
`bfad_drv.h` is the central BFAD driver definition header. It declares compile-time constants, driver flags, core objects for PCI functions/ports/vports/VFs, DMA buffers, FCXP pass-through context, completion wrappers, logging, module parameters, and cross-file driver prototypes.

## Important APIs, Types, and Functions
Key macros include `BFAD_DRIVER_NAME`, `BFAD_DRIVER_VERSION`, `BFAD_IRQ_FLAGS`, state flags such as `BFAD_HAL_INIT_DONE`, `BFAD_DRV_INIT_DONE`, `BFAD_PORT_ONLINE`, `BFAD_FC4_PROBE_DONE`, `BFAD_EEH_BUSY`, and defaults such as `BFAD_LUN_QUEUE_DEPTH`, `BFAD_IO_MAX_SGE`, `BFAD_MIN_SECTORS`, and `BFAD_MAX_SECTORS`. `struct bfad_s` is the root PCI-function object and owns the BFA HAL, FCS fabric, PCI resources, completions, locks, primary port, configuration, MSI-X table, timer, IM module, trace/log buffers, debugfs state, AEN queues, and vport list. `struct bfad_port_s`, `bfad_vport_s`, and `bfad_vf_s` represent physical/virtual FC constructs. `struct bfad_fcxp` carries FC pass-through request/response DMA state. `struct bfad_hal_comp` wraps asynchronous BFA completions. The header prototypes PCI lifecycle, interrupt setup, HAL memory management, port/vport creation, debugfs, timer, and worker functions.

## Control Flow
There is no executable flow in the header, but its types encode the driver lifecycle: PCI probe allocates/configures `bfad_s`, initializes BFA/FCS, configures the physical port, creates IM/SCSI state, starts interrupts/timers/workers, and later tears them down through the declared stop/remove/uninit helpers. Shared fields and flags coordinate transitions across implementation files.

## State and Persistence
Most persistent in-memory state for a BFAD instance lives in `struct bfad_s`: hardware mappings, adapter names, firmware config, link stats, debug buffers, AEN queues, and vport lists. `bfad_cfg_param_s` stores runtime queue and binding configuration. Persistent hardware/flash state is not stored here directly but is reached through BFA modules referenced by `bfad_s`.

## Dependencies and Integration Points
The header integrates Linux PCI, DMA, interrupts, cdev/fs, timers, workqueues, SCSI, FC transport, BSG, and BFA/FCS headers. It is included by the sysfs, IM, debugfs, and BSG files in this work item and likely by PCI/core implementation files outside it.

## Risks
Many flags share one `u32` field, and `BFAD_PORT_DELETE` reuses bit value `0x1` in port-level flags while `BFAD_MSIX_ON` uses the same bit in `bfad_flags`; this is safe only because the fields differ. The root structure is large and shared across interrupt, workqueue, sysfs, BSG, and SCSI contexts, so lock discipline around `bfad_lock`, `bfad_mutex`, and AEN spinlock is critical. External module parameters can alter queue sizes and transfer limits, so bounds must be validated in code using them.

## Test Signals
Build tests should catch include-order and type drift. Runtime tests should cover PCI probe/remove, MSI-X and INTx paths, EEH flags, debugfs enable/disable, vport lists, AEN queue reuse, and BSG FCXP allocation paths that depend on `struct bfad_fcxp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_im.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_im.c

## Purpose
`bfad_im.c` implements the SCSI initiator-mode shim. It registers SCSI host templates, creates SCSI hosts for physical/vport ports, maps FCS initiator-target nexus callbacks into FC remote ports, queues SCSI commands to BFA IO objects, handles SCSI error recovery, manages queue depth, and posts vendor AEN events.

## Important APIs, Types, and Functions
Exported callbacks include `bfa_cb_ioim_done`, `bfa_cb_ioim_good_comp`, `bfa_cb_ioim_abort`, and `bfa_cb_tskim_done` for firmware/BFA completions. SCSI EH functions include `bfad_im_abort_handler`, `bfad_im_reset_lun_handler`, and `bfad_im_reset_target_handler`. FCS callbacks `bfa_fcb_itnim_alloc/free/online/offline` manage `bfad_itnim_s` lifecycle. Port/host lifecycle functions include `bfad_im_probe`, `bfad_im_probe_undo`, `bfad_im_port_new/delete/clean`, `bfad_im_scsi_host_alloc/free`, `bfad_scsi_host_alloc/free`, `bfad_thread_workq`, and `bfad_destroy_workq`. The file defines `bfad_im_scsi_host_template` and `bfad_im_vport_template`.

## Control Flow
Module init attaches physical and vport FC transport templates. Probe allocates `bfad_im_s`, creates an ordered reclaim workqueue, and initializes AEN work. Port creation allocates `bfad_im_port_s`; SCSI host allocation reserves an IDR ID, allocates a `Scsi_Host`, sets target/LUN/queue limits and transport template, and calls `scsi_add_host_with_dma`.

When FCS reports an ITNIM online/offline/free transition, the callback sets state and queues `bfad_im_itnim_work_handler`. The work handler adds FC remote ports on online, stores `fc_rport->dd_data`, appends to `itnim_mapped_list`, deletes remote ports on offline/free, unlinks mappings, and frees the ITNIM on final free. `bfad_im_queuecommand_lck` checks rport readiness and EEH state, maps SCSI DMA, verifies HAL started, allocates a BFA IO with the target nexus, stores it in `host_scribble`, and starts it. Completion callbacks set SCSI result, copy sense/residue, unmap DMA, adjust queue depth, and call `scsi_done`.

## State and Persistence
State is in-memory: `bfad_im_port_s` host and target lists, `bfad_itnim_s` state/channel/target ID/queue-depth timestamps, `Scsi_Host` transport attributes, command private status/waitqueue bits, AEN queues, and BFA IO/task objects. Queue-depth ramping persists only during runtime through `last_ramp_up_time` and `last_queue_full_time`.

## Dependencies and Integration Points
The file depends on Linux SCSI mid-layer, FC transport, IDR, workqueues, BFA IO/task/FCS APIs, LUN masking helpers, module parameters from `bfad_drv.h`, and sysfs/transport templates from `bfad_attr.c`. It feeds BSG by providing `bfad_get_im_port` data and host templates.

## Risks
Several paths assume `rport->dd_data`, `itnim_data->itnim`, and `itnim->bfa_itnim` are valid; disconnect races are partly handled but remain high risk. Abort waits poll `host_scribble` with exponential sleeps and then calls `scsi_done`, so double-completion and timeout interactions need scrutiny. Workqueue transitions drop and reacquire `bfad_lock` around FC transport calls, making state changes during the unlocked interval important. LUN masking special-cases LUN 0 and alters scan flags.

## Test Signals
Exercise probe/remove, physical and vport host creation, target discovery/loss/relogin, queuecommand under link-down and EEH states, IO completion status mapping, queue-full ramp down/up, LUN and target reset success/failure, LUN masking visibility, and AEN vendor event posting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_im.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_im.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_im.h

## Purpose
`bfad_im.h` declares the initiator-mode interface shared between BFAD core, SCSI/FC transport, BSG, and IM implementation files. It defines per-command, per-port, per-target-nexus, binding, and module state for the initiator path.

## Important APIs, Types, and Functions
The header declares IM lifecycle APIs (`bfad_im_module_init/exit`, `bfad_im_probe/undo`, `bfad_im_port_new/delete/clean`, `bfad_im_scsi_host_alloc/free`), transport helpers (`bfad_fc_host_init`, `bfad_scsi_host_alloc/free`, `bfad_get_itnim`), queue-depth functions, and BSG entry points. `struct bfad_cmd_priv` stores task-management completion status and waitqueue pointer in SCSI command private space. `struct bfad_im_port_s` links a BFAD port to its SCSI host, vport, binding list, and mapped ITNIM list. `enum bfad_itnim_state` models target nexus lifecycle. `struct bfad_itnim_s` stores FCS/BFA nexus pointers, FC rport pointer, SCSI target/channel IDs, work item, and queue-depth timing. `bfad_im_post_vendor_event` fills AEN entries and queues vendor event work.

## Control Flow
The header supports flow implemented in `bfad_im.c`: command private status is set by task completion callbacks; IM ports are allocated during port creation; ITNIM states drive workqueue processing; `bfad_get_aen_entry` moves entries from free to active queue; `bfad_im_post_vendor_event` timestamps and schedules notification only after FC4 probe completion.

## State and Persistence
All structures are runtime state. `bfad_im_port_s` stores host-visible mappings. `bfad_itnim_s` stores target nexus state and queue-depth timing. AEN entries carry wall-clock timestamps, instance numbers, sequence numbers, category, and event type until posted.

## Dependencies and Integration Points
It includes `bfa_fcs.h` and references SCSI, FC transport, workqueue, and BFA types through included driver headers. It exports templates and transport pointers consumed by `bfad_attr.c` and `bfad_im.c`.

## Risks
The command private `status` bit packing combines `IO_DONE_BIT` with shifted `bfi_tskim_status`; changes to task status width or bit usage could break waits. `bfad_get_im_port` assumes `shost_priv(host)` contains a valid pointer wrapper. AEN macros manipulate queues under a dedicated spinlock but queue work into IM workqueue, so teardown ordering matters.

## Test Signals
Compile tests should validate structure visibility and SCSI `cmd_size` assumptions. Runtime tests should cover task-management wait completion, AEN queue posting during probe and teardown, target online/offline/free transitions, and BSG access through declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_im.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi.h

## Purpose
`bfi.h` defines the low-level Brocade/QLogic firmware interface ABI shared by BFA modules: common message headers, DMA address/SG formats, message classes, IOC control and attributes, preboot configuration, message queues, generic port messages, ASIC block control, CEE/SFP/flash/diagnostic/PHY/FRU message layouts.

## Important APIs, Types, and Functions
The file is packed with `#pragma pack(1)`. Core definitions include `struct bfi_mhdr_s`, `bfi_h2i_set`, `bfi_i2h_set`, `BFA_I2HM`, `union bfi_addr_u`, `struct bfi_sge_s`, `struct bfi_alen_s`, `struct bfi_sgpg_s`, `struct bfi_msg_s`, and `struct bfi_mbmsg_s`. `enum bfi_mclass` assigns firmware message classes for IOC, diagnostics, flash, CEE, FCPORT, IOCFC, ABLK, UF, FCXP, LPS, RPORT, ITN, IOIM, TSKIM, port, SFP, PHY, and FRU. IOC types define adapter attributes, firmware image headers, boot controls, heartbeat, state machine values, and mailbox unions. Later sections define preboot config, message queue rings and doorbells, port stats commands, adapter-block PF/optrom commands, CEE/SFP/flash operations, diagnostic tests including D-port notifications, external PHY operations, and FRU read/write messages.

## Control Flow
This header has no runtime control flow, but BFA modules populate H2I structures, post them to mailbox/message queues, and decode I2H responses using these layouts. Macros set headers and compute DMA segment counts/offsets. Queue macros update producer/consumer indices and calculate free entries.

## State and Persistence
It describes firmware-visible state rather than driver-owned state. Persistent domains include flash image and partitions, boot/preboot configuration, adapter properties, SFP/PHY/FRU data, and firmware image metadata. Runtime domains include IOC heartbeat/state, message queue indices, stats DMA buffers, trace offsets, and diagnostic results.

## Dependencies and Integration Points
The file includes `bfa_defs.h` and `bfa_defs_svc.h` for shared types. Higher-level BFA code and BFAD BSG/debugfs commands rely on these constants and packed structures when communicating with firmware and reading BAR/flash/debug regions.

## Risks
This is a hardware/firmware ABI. Packing, endian fields, bitfields, opcode values, sizes, and queue arithmetic must remain exact. Several macros assume power-of-two queue depths or particular segment sizes. Bitfield layout in `struct bfi_sge_s` varies by endian and must match firmware. Any structure drift can cause firmware misinterpretation.

## Test Signals
Validation should include build-time structure-size/offset assertions where available, endian tests, firmware handshake tests for IOC enable/getattr/heartbeat, message queue wraparound/free-count tests, flash/diag/PHY/FRU command round trips, and compatibility checks across ASIC generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi_ms.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi_ms.h

## Purpose
`bfi_ms.h` defines message-service firmware ABI structures for IOCFC configuration, FC port, FCXP pass-through, unsolicited frame buffers, login services, remote ports, initiator target nexus, SCSI IO, task management, and MSI-X vector mapping.

## Important APIs, Types, and Functions
The file is packed and includes `bfi.h`, `bfa_fc.h`, and service definitions. `struct bfi_iocfc_cfg_s` describes queue counts, endian signature, request/response circular queues, shadow index addresses, stats/config response DMA addresses, sense buffer segments, and interrupt attributes. `struct bfi_iocfc_cfgrsp_s` returns firmware config, interrupt attributes, boot WWNs, preboot config, and queue register offsets. FC port messages cover enable/disable/service params/events/trunk SCNs. `struct bfi_fcxp_send_req_s` and `_rsp_s` define ELS/CT pass-through request/response payloads. LPS messages define login/logout and CVL events. RPORT and ITN sections define create/delete/speed/QoS/LIP and initiator-nexus lifecycles. `struct bfi_ioim_req_s`, `enum bfi_ioim_status`, `struct bfi_ioim_rsp_s`, and task management structs define SCSI IO and reset/abort firmware contracts. MSI-X enums map CB and CT ASIC vectors.

## Control Flow
The driver configures IOCFC queues, then BFA modules use these message structures for FC link, login, rport, ITN, IO, and task-management flows. IO requests carry an FCP command plus inline SGEs and optional DIF metadata. Firmware returns `bfi_ioim_rsp_s`, which BFA/BFAD maps to SCSI completion status. Task-management requests carry LUN and timeout and complete with `bfi_tskim_status`.

## State and Persistence
Most definitions represent runtime firmware state: queue DMA locations, boot WWN snapshots, FC link events, FCXP tags, login tags, rport firmware handles, ITN handles, IO tags, status/reuse semantics, and MSI-X vector layout. IOCFC config also includes boot/preboot configuration read from firmware response state.

## Dependencies and Integration Points
`bfad_im.c` consumes `bfi_ioim_status` and `bfi_tskim_status` to complete SCSI commands and task-management waits. `bfad_bsg.c` uses FCXP behavior for ELS/CT pass-through. Core BFA modules use IOCFC, FC port, RPORT, ITN, IOIM, TSKIM, and MSI-X layouts when programming firmware queues.

## Risks
Like `bfi.h`, this is a packed firmware ABI where field sizes, endian annotations, bitfields, tags, and opcodes are fixed. IO status comments describe reuse restrictions; mishandling `reuse_io_tag` or abort statuses can corrupt IO tag lifecycle. `bfi_ioim_req_s` supports max 64-byte CDBs while BFAD host setup uses 16-byte SCSI CDBs, so any feature expansion must coordinate both layers.

## Test Signals
Test IOCFC queue setup, interrupt attribute programming, link event decode, FCXP pass-through success/failure, login/logout, rport create/delete, ITN lifecycle, IO completion status mapping, abort/task-management paths, and MSI-X vector selection for CB versus CT ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi_ms.h -->
