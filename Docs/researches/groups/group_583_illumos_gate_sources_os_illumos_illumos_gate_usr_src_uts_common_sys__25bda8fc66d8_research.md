# Group Research: group_583_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__25bda8fc66d8

Scope: `Docs/research_subset_a.md`. All listed source files were read completely. The group covers illumos Fibre Channel transport/ULP headers plus core file descriptor, file ioctl, firmware loading, and record-locking headers.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fcio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fcio.h

Defines the user/kernel FCIO ioctl ABI for Fibre Channel port management. It assigns `FCIO_CMD`, subcommands for device enumeration, symbolic names, login/logout, topology, reset, diagnostics, name service, firmware/FCODE download, node-id operations, and T11 FC-HBA/NPIV library operations.

Key contracts are `fc_port_dev_t`/`fc_ns_map_entry_t`, `fcio_t`, and T11 HBA exchange structures such as `fc_hba_list_t`, `fc_hba_single_t`, `fc_hba_adapter_attributes_t`, `fc_hba_port_attributes_t`, and `fc_hba_adapter_port_stats_t`. The file also provides 32-bit syscall variants where pointer and size layout differs.

Dependencies are `fc_types.h` and `fc_appif.h` for WWNs, port IDs, HBA state-change types, and topology/state definitions. Treat this file as stable ABI: structure sizes, version fields, flexible one-element arrays, and `_SYSCALL32` packing are externally visible.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fcio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_error.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_error.h

Defines common Fibre Channel return codes, packet states, packet reason codes, packet actions, and explanation values shared by FCA, fctl/fp, and ULP layers. General results include `FC_SUCCESS`, `FC_FAILURE`, allocation/packet/offline errors, ELS and transport errors, busy states, login/reset errors, and NPIV-specific errors.

Packet classification is split into `pkt_state` values such as `FC_PKT_SUCCESS`, `FC_PKT_TIMEOUT`, `FC_PKT_*_RJT`, and `FC_PKT_*_BSY`, then state-specific `FC_REASON_*`, `FC_ACTION_*`, and `FC_EXPLN_*` values. These constants are consumed by packet error translation helpers exposed through FCA/ULP interfaces.

This file is a vocabulary header, not an implementation header. Its values are part of cross-module behavior and should be extended carefully because callers may persist or expose them through ioctl error paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_fcaif.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_fcaif.h

Defines the Fibre Channel adapter driver interface consumed by the transport framework. It declares FCA module revision levels, state-change values, port-management flags, reset command codes, port-management command codes, and capability string names.

Core data structures are `fc_fca_bind_info_t`, `fc_fca_port_info_t`, `fc_fca_pm_t`, `fc_fca_p2p_info_t`, and especially `fc_fca_tran_t`. `fc_fca_tran_t` is the adapter operations vector for binding/unbinding ports, packet initialization, ELS send, capability get/set, loop-map retrieval, transport, unsolicited buffer management, abort/reset, port management, FCA device lookup, and notifications.

Exports include `fc_fca_init`, `fc_fca_attach`, `fc_fca_detach`, and error translation helpers. This file is the main fctl-to-HBA-driver contract; changes affect every FCA driver and the fp/fctl framework.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_fcaif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_fla.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_fla.h

Defines Fabric Loop Application payloads and constants. It covers SCR registration function codes, RSCN affected-address formats, `FLA_RR_TOV`, and structures for SCR requests/responses, RSCN payload headers, affected IDs, LINIT requests/responses, and loop-status requests/responses.

The structures use endian-dependent bitfields guarded by `_BIT_FIELDS_LTOH` / `_BIT_FIELDS_HTOL`, so they are wire-format sensitive. Consumers must not treat the bitfield layout as portable outside the illumos build configuration.

The file is used by fp/fctl discovery and state-change handling when registering for fabric notifications, processing RSCNs, and dealing with loop initialization/status ELS payloads.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_fla.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_linkapp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_linkapp.h

Defines Link Application ELS opcode constants and common ELS/BLS payload structures. It includes PLOGI/FLOGI/LOGO/PRLI/PRLO/ADISC/PDISC/FDISC/RSCN/SCR/LINIT/RNID opcodes, BA_ACC/BA_RJT payloads, LOGO and ADISC payloads, ELS RJT payloads, and PRLI/PRLO service parameter layouts.

The file includes process login/logout service parameter flags such as `SP_OPA_VALID`, `SP_RPA_VALID`, and response-code masks. Like other FC wire headers, it uses endian-dependent bitfields.

This is a protocol layout header for ELS handling in fp/fctl and ULPs. It is most relevant when tracing login/logout, address discovery, and unsolicited ELS response paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_linkapp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_portif.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_portif.h

Defines internal fctl/fp port-driver interfaces. It contains orphan-scan and LOGO tolerance constants, name-server request flags, fp soft-state bits, fp option bits, power-management levels, and device-address helper macros.

The central type is `job_request_t`, used by the per-port job-handler thread. Job codes cover ULP attach, port startup/shutdown, map retrieval, PLOGI/LOGO, online/offline, unsolicited requests, name-server commands, link reset, ULP notification, and FCIO login/logout. Job flags control fctl async completion, fp async completion, and ULP notification cancellation.

Also defines `fc_port_clist_t`, `fctl_ns_req_t`, `fc_orphan_t`, DMA/no-DMA copy macros `FC_GET_RSP` and `FC_SET_CMD`, and a broad set of fctl prototypes for remote node/port lifecycle, job queueing, ULP attach/detach, port busy/idle, lookup tables, port-map filling, name-service commands, orphan handling, WWN utilities, timed counters, and NPIV adapter lookup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_portif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_ulpif.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_ulpif.h

Defines the upper-layer protocol interface between fctl/fp and FC ULP modules such as FCP, FCIP, and FCSM. It provides ULP module revision constants, port attach/detach command enums, PLOGI behavior flags, device online/offline values, and port reset command codes.

Key structures are `fc_portmap_t`, `fc_ulp_port_info_t`, and `fc_ulp_modinfo_t`. `fc_ulp_modinfo_t` is the ULP callback vector for port attach/detach/ioctl, ELS callbacks, data callbacks, and state-change callbacks.

Exports include `fc_ulp_add/remove`, packet init/uninit, port map retrieval, login, remote-port lookup, name-service submission, transport, ELS issue, unsolicited buffer alloc/free/release, abort, link reset, port reset, error decoding, WWN/D_ID lookup, FCA device lookup, port notification, relogin disable/enable, port busy/idle, NPIV queries, and device-event logging.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_ulpif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcal.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcal.h

Defines FC-AL loop initialization identifiers and magic values for LISM, LIFA, LIPA, LIHA, LISA, LIRP, and LILP. It also defines PLDA timer values and `LILP_LBIT_SET`, which signals login-required state in the high bits of `lilp_myalpa`.

The main structure is `fc_lilpmap_t`, containing the loop initialization map magic, local AL_PA, map length, and up to 127 AL_PA entries. This is consumed by fp/fctl loop discovery and private loop diagnostics.

This header is small but wire/protocol significant: the AL_PA list and LBIT behavior influence whether fp performs implicit logout and PLOGI after loop initialization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcgs2.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcgs2.h

Defines FC-GS-2 / FC-CT common transport and name-server constants. It includes CT revision, service type/subtype constants, FC-CT accept/reject codes, reject reasons, name-service command codes, name-service reject explanations, management-service command codes, class-of-service bits, and port type values.

The file provides registration/query payload structures for port/node WWNs, class of service, FC-4 types, symbolic names, port type, IP address, initial process associator, deregistration, `GID_PT`, `GA_NXT`, `GID_PN`, `GPN_ID`, and `GPT_ID`. `ns_resp_gan_t` is the large aggregate response used for discovery.

It also duplicates SCR registration constants used elsewhere. This is the primary name-server protocol layout header used by fp/fctl and ULP name-service paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcgs2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcph.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcph.h

Defines low-level FC-PH frame constants and the Fibre Channel frame header layout. It covers `r_ctl` routing/info masks and values, FC type values for link services and device data, `F_CTL` bits, `DF_CTL` bits, and well-known fabric addresses.

`FC_WELL_KNOWN_ADDR(x)` recognizes the well-known range plus domain-controller IDs. `fc_frame_hdr_t` models the 24-byte FC frame header using endian-dependent bitfields for D_ID, S_ID, F_CTL/type, sequence fields, OX_ID/RX_ID, and relative offset.

This header underpins every `fc_packet_t` command/response frame header and is a protocol ABI within the Fibre Channel stack.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcph.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fctl.h

Defines shared fctl/fp transport structures and constants. It encodes local port state and link speed values in `fp_state`, helper masks for state and speed, notification flags, packet transport flags/classes, packet transport types, and trace logging flags.

The key type is `fc_packet_t`, the common exchange object passed between ULPs, fctl/fp, and FCA drivers. It contains command/response/data buffers, DMA handles/cookies, FC frame headers, completion callbacks, remote-port and FCA-private references, packet state/reason/action/explanation, residuals, unsolicited response token, and reserved fields including `pkt_ulp_rscn_infop`.

The file also defines T11 HBA speed/attribute constants, `fca_port_attrs_t`, unsolicited buffer `fc_unsol_buf_t`, trace queue/message structures, remote-port change type constants, trace utility prototypes, and WWN string conversion helpers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fctl_private.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fctl_private.h

Defines private fctl state not intended for other modules. It includes hash table sizes/functions for PWWN, D_ID, and NWWN, FC-4 bitmap helpers, invalid error sentinels, translated ULP state-change values, ULP attach retry count, NPIV limits, and ULP port lifecycle flags.

Major structures include `fc_ulp_ports_t`, `fc_ulp_module_t`, `fc_fca_port_t`, `timed_counter_t`, `fc_remote_node_t`, `fc_remote_port_t`, global NWWN hash entries, packet error mapping structures, and `fc_local_port_t`. The comments document lock ordering, reference counts, login state, relogin suppression, remote-node/remote-port relationships, job queues, state-change nesting, port power management, unsolicited buffers, orphan lists, HBA attributes, and NPIV bookkeeping.

`fc_local_port_t` is the fp per-instance soft state. It ties together FCA handle/vector, local state/topology, job queue, wait queue, remote-port hash tables, taskq, timeouts, power management, FC-4 type registration, fabric data, and NPIV port lists. The file ends with private/static prototypes for fctl child management, ULP port registration, host name-service values, link reset completion, error decoding, DMA attribute initialization, and NPIV create/delete lookup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fctl_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fp.h

Defines private declarations for the fp port driver implementation. It provides trace levels/destinations, `FP_DTRACE`/`FP_TRACE` wrappers, packet-error testing, discovery/timeouts/retry constants, task states, command flags, DMA flags, open flags, and message-control constants.

Main structures are `fp_soft_attach_t`, `fp_cmd_t`, and `fp_unsol_spec_t`. `fp_cmd_t` wraps an `fc_packet_t` for fp internal ELS/name-service operations, with DMA state, retry timing, job association, ULP packet linkage, and transport function pointer.

Most of the file is a prototype map for fp implementation paths: attach/detach/power/open/close/ioctl, packet allocation/freeing, job handling, startup/shutdown, loop/fabric/point-to-point online handling, FLOGI/PLOGI/LOGO/ADISC/RLS/RNID, state-change callbacks, name-service registration/query/GAN handling, FCIO command copyin/copyout, unsolicited ELS handling, RSCN validation, ULP attach/notification, target logout/login, and port capability retrieval.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcip.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcip.h

Defines private and protocol structures for the FCIP ULP that carries IP/ARP over Fibre Channel. It includes STREAMS module constants, MTU/packet sizing, multicast hash configuration, per-stream state `struct fcipstr`, DLPI address length, port attach information `fcip_port_info_t`, unsolicited buffer sizing, timeout/retry constants, routing/destination hash sizes, and taskq sizing.

`struct fcip` is the per-device state: devinfo/instance, sibling port, port state, ULP port info, FARP serialization, unsolicited buffer tokens/counts, destination and routing hash tables, local MAC/WWN/IP addresses, transmit/send-up caches, taskq/thread synchronization, broadcast D_ID, kstats, MIB-II counters, and CPR state.

The file also defines route and destination objects (`fcip_routing_table`, `fcip_dest`), transmit packet wrapper `fcip_pkt_t`, DLPI full address `fcipdladdr`, LLC/SNAP header, kstat layout, copy macros, FARP ELS request/reply codes and payload `la_els_farp_t`, FARP/InARP response lists, optional FC-PH network header, InARP packet structure, esballoc callback argument, send-up queue element, and FC-4 type bitmap helpers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcp.h

Defines FCP wire-format structures for SCSI over Fibre Channel. It includes FCP frame information categories for SCSI data, command, response, and transfer-ready frames.

Core structures are `fcp_cntl_t`, `fcp_ent_addr_t`, `fcp_cmd_t`, `fcp_status_t`, and `fcp_rsp_t`. These model command task attributes, task management bits, read/write direction, hierarchical LUN addressing, command CDB payload, response status, residual flags, sense length, and response-info length. Bitfield order depends on `_BIT_FIELDS_HTOL` or `_BIT_FIELDS_LTOH`.

The file also defines response-info codes, PRLI and PRLI-ACC payload layouts, unsolicited FCP buffer flags for target/out-of-band commands, maximum response IU size, and FC-4 type bitmap helpers. It is protocol layout, not driver state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcp_util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcp_util.h

Defines FCP utility ioctl command values and user/kernel exchange structures. Commands cover target inquiry/create/delete, sending a SCSI command, state count, and target mapping retrieval.

`struct fcp_ioctl` carries an fp minor number plus a variable list pointer. `struct device_data` reports target WWN, status, LUN count, and LUN0 type. `struct fcp_scsi_cmd` describes a passthrough SCSI command including FC port number, target PWWN, FC/SCSI status, packet state/action/reason, LUN, read flag, timeout, CDB buffer, data buffer/residual/status, and request-sense buffer.

The file also defines T11 target mapping structures (`fc_hba_mapping_entry_t`, `fc_hba_target_mappings_t`) and 32-bit syscall variants/conversion macros for ioctl and SCSI command structures. Pointer-width conversion here is ABI-sensitive.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcp_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcpvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcpvar.h

Defines the private state model for the FCP SCSI-over-FC driver. It includes REPORT_LUNS limits, internal SCSI opcodes, FC-4 SCSI type, retry/offline/reset delays, invalid timeout sentinel, legacy hotplug event strings, hash sizing, state-change masks, packet private sizing, and optional stats.

`fcp_port_t` is the per-local-port soft state. It tracks global linkage, internal retry packets, discovery counters/deadlines, topology, port ID, physical state, reset/offline queues, link generation counter, local WWNs, fp/fctl handle, outstanding packet queue, internal packet count, DMA/FCA attributes, SCSA `scsi_hba_tran`, devinfo, reset callbacks, NDI/MDI event handles, target hash table, MPxIO mode, throttling notification, boot WWN, config condition variable, and DMA cookie sizing.

`fcp_pkt_t` bridges `scsi_pkt`, `fcp_pkt`, and `fc_packet_t` for normal I/O. `fcp_ipkt_t` models internal commands such as PLOGI, PRLI, INQUIRY, REPORT_LUNS, and passthrough, with restart timing, link/change counters, retry count, and embedded `fc_packet_t`. `fcp_tgt_t` models remote SCSI targets with WWNs, D_ID, LUN list, discovery counters, target state/capability flags, manual configuration state, and trace bits. `fcp_lun_t` models OS-visible LUNs, including NDI/MDI child handle, state, type, target-init count, GUIDs, inquiry data, MPxIO flag, and packet queue.

The file also defines target/LUN state flags, discovery trace macros, hotplug/reset/offline queue elements, LUN masking entries, SCSI address conversion macros, timeout constants, lock annotations, DMA/no-DMA copy macros, open state flags, and attach/init wait timeouts. Its comments are unusually detailed and document generation-counter behavior used to discard stale discovery work after link or target changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcpvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcsm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcsm.h

Defines the SAN Management ULP private state and ioctl interface. Kernel-only definitions include message destinations, debug levels, open flags, ELS/management-server timeouts, retry constants, job structure `fcsm_job_t`, per-port state `fcsm_t`, and command wrapper `fcsm_cmd_t`.

`fcsm_t` tracks per-port SAN management state: mutex, global list linkage, S_ID, instance, port state/topology, flags, pending command and callback counts, ULP port info, job queue, retry queue, timers, job condition variable, discovered device map, per-port job thread, command cache, management-server login parameters, and CPR state.

The public ioctl portion defines `fc_ct_aiu_t`, `FCSMIO_CMD`, subcommands for CT passthrough and adapter lookup, maximum CT payload size, and many management-server/fabric-configuration command codes. Kernel prototypes cover driver entry points, ULP callbacks, attach/detach/resume, job and command queues, management-server login, CT passthrough, retry handling, and formatting helpers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcsm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/file.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/file.h

Defines the illumos kernel `file_t` open-file object and user/kernel file flag constants. `file_t` holds short-term lock, open flags, extra flags, vnode pointer, file offset, credentials, audit data, reference count, and OFD lock pointer. Comments specify `f_tlock` protects most fields while `f_rwlock` elsewhere protects vnode and credentials.

Defines standard and illumos-specific open flags: `FREAD`, `FWRITE`, `FNDELAY`, `FAPPEND`, `FSYNC`, `FNONBLOCK`, create/truncate/exclusive/noctty, large-file, xattr, nofollow, nolinks, ignorecase, xattr directory open, `FSEARCH`, `FEXEC`, `FCLOEXEC`, `FDIRECTORY`, `FDIRECT`, and `FCLOFORK`. Kernel-only fake ioctl/open flags include data-model bits, `FKIOCTL`, and `FKLYR`.

Also exposes historical `flock(3C)` constants and kernel file-descriptor APIs such as `getf`, `releasef`, `closef`, `ufalloc`, `falloc`, `setf`, fd flag accessors, `close_exec`, poll-info helpers, socket async query, and zone-change checking.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/filep.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/filep.h

Defines private standalone/boot-style file and device identification structures tied to UFS headers. `devid_t` stores a description, device cookie, taken flag, and an embedded UFS superblock-sized union.

`fileid_t` stores a file descriptor id, path, block number, count, offset, memory pointer, taken flag, cache/compression flags, owning device id, block buffer, block-read callback, UFS inode pointer, list links, compressed-file offset, decompression scratch buffer metadata, and zlib stream pointer.

Flags include cached/partial/no-cache bits borrowed from inode flags plus `FI_COMPRESSED` and `DECOMP_BUFSIZE`. It declares `diskread(fileid_t *)`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/filep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/filio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/filio.h

Defines general file ioctl numbers using `sys/ioccom.h`. Standard ioctls include `FIOCLEX`, `FIONCLEX`, `FIONREAD`, `FIONBIO`, `FIOASYNC`, `FIOSETOWN`, and `FIOGETOWN`.

The rest are mostly illumos/UFS/private filesystem ioctls: filesystem lock/status/flush, obsolete allocation info, atime setting, delayed I/O get/set, inode open, DiskSuite/UFS logging protocols, busy/directio/tuning controls, logging enable/disable, UFS snapshot create/delete including multi-backing-file snapshot creation, superblock retrieval, maxphys query, TSufs debug/error/stats controls, SEEK_DATA/SEEK_HOLE implementation ioctls, boot archive compression marking, and filled-region counting.

This file is user-visible ioctl ABI. Numeric values should be considered stable even for obsolete/private operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/filio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/firmload.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/firmload.h

Defines a small kernel-only firmware loading API derived from NetBSD. It introduces opaque `firmware_handle_t` and declares `firmware_open`, `firmware_close`, `firmware_get_size`, and `firmware_read`.

The API is only visible under `_KERNEL` and includes `sys/types.h`. Callers open firmware by name/path components, query size, read at offsets into caller buffers, then close the handle.

This is an abstraction header for drivers that load firmware blobs without directly depending on filesystem details.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/firmload.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/flock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/flock.h

Defines private kernel record-locking declarations and instrumentation. It introduces `F_REMOTELOCK` and `F_PXFSLOCK`, reclock command bits (`INOFLCK`, `SETFLCK`, `SLPFLCK`, remote/PXFS/nonblocking-mandatory bits), `IGN_PID`, unsigned lock offset types, and maximum offset constants.

`pad_info_t` describes private interpretation of `struct flock.l_pad`, especially `F_HASREMOTELOCKS`. `flk_callback_t` supports before/after sleep callbacks for blocking lock requests and CPR-safe suspension. `filock_t` is retained mostly for pointer casts, while `grant_lock_t` batches locks to grant.

The file defines NLM and lock-manager status enums, kernel `locklist_t` for active/sleeping lock queries, query flags, OFD lock helpers, core lock functions (`reclock`, `chklock`, `convoff`, `cleanlocks`), lock-list query/free helpers, lock data conversion/checking, remote-lock checks, lock-manager status update, callback list operations, zone hooks, and clustering hooks for NLM/PXFS lock handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/flock.h -->