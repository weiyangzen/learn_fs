# subset-b-005999 Research

Grouped research for UAPI SCSI/Fibre Channel and ALSA sound headers under `sources/distributed-fs/ceph-client/include/uapi`. These files are exported kernel ABI contracts rather than executable modules, so control flow below describes the externally visible request, event, ioctl, netlink, BSG, and protocol-message flows that kernel and userspace must follow.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_els.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_els.h

## Purpose
`fc_els.h` defines Fibre Channel Extended Link Services payload formats and command identifiers for login, logout, discovery, state-change, diagnostic, and fabric-performance notification exchanges. It is a userspace-visible protocol layout header shared by libfc, FC transport drivers, diagnostic tooling, and BSG users that need to build or decode ELS frame payloads. It complements `fc_fs.h` frame header/type definitions and uses big-endian network-order scalar fields for wire compatibility.

## Important APIs, Types, and Constants
The central command namespace is `enum fc_els_cmd`, with `FC_ELS_CMDS_INIT` for decoder name tables. It covers core link service commands such as `ELS_LS_RJT`, `ELS_LS_ACC`, `ELS_PLOGI`, `ELS_FLOGI`, `ELS_LOGO`, `ELS_PRLI`, `ELS_PRLO`, `ELS_SCR`, `ELS_RSCN`, `ELS_RNID`, and newer diagnostic commands including `ELS_FPIN`, `ELS_EDC`, and `ELS_RDF`.

Reject handling is represented by `struct fc_els_ls_rjt`, `enum fc_els_rjt_reason`, and `enum fc_els_rjt_explan`. The accept case uses `struct fc_els_ls_acc`. Login negotiation uses `struct fc_els_csp`, `struct fc_els_cssp`, and `struct fc_els_flogi`, with feature bits such as `FC_SP_FT_NPIV`, `FC_SP_FT_FPORT`, `FC_SP_FT_EDTR`, and payload-size bounds inherited from `FC_MIN_MAX_PAYLOAD`/`FC_MAX_PAYLOAD`.

Process login and recovery payloads are represented by `struct fc_els_spp`, `struct fc_els_prli`, `struct fc_els_prlo`, `struct fc_els_rrq`, `struct fc_els_rec`, and `struct fc_els_rec_acc`. Discovery and topology/status payloads include `struct fc_els_adisc`, `struct fc_els_scr`, `struct fc_els_rscn`, `struct fc_els_rscn_page`, `struct fc_els_rnid*`, `struct fc_els_rpl*`, `struct fc_els_rps*`, `struct fc_els_lesb`, `struct fc_els_rls*`, `struct fc_els_rlir`, `struct fc_els_clir`, and `struct fc_els_clid`.

Diagnostic and FPIN support is built around `struct fc_tlv_desc`, tag enum `fc_ls_tlv_dtag`, `fc_tlv_next_desc()`, descriptor size helpers, `struct fc_els_fpin`, `struct fc_fn_li_desc`, `struct fc_fn_deli_desc`, `struct fc_fn_peer_congn_desc`, `struct fc_fn_congn_desc`, `struct fc_df_desc_fpin_reg`, `struct fc_els_rdf`, `struct fc_els_rdf_resp`, `struct fc_diag_lnkflt_desc`, `struct fc_diag_cg_sig_desc`, `struct fc_els_edc`, and `struct fc_els_edc_resp`. Flexible arrays and `_Static_assert()` checks preserve ABI offsets for variable descriptor lists.

## Control Flow and State
This header has no executable kernel flow except the inline `fc_tlv_next_desc()` helper, which advances through a received TLV list by converting the descriptor length from big endian and adding the TLV header size. The operational flow is protocol-driven: userspace or a driver selects an ELS command byte, fills the command-specific request structure, transmits the payload inside an FC frame, and then interprets the response as either `LS_ACC`, `LS_RJT`, or a command-specific accept payload.

Login flows use FLOGI/PLOGI payloads to exchange common and class-specific service parameters, then may use PRLI/PRLO to activate or tear down FC-4 process images. Change notification flow uses SCR registration followed by RSCN payloads containing one or more affected-port pages. Diagnostic flow uses EDC/RDF exchanges to advertise supported descriptor tags and FPIN events to report link integrity, delivery, peer congestion, or congestion conditions.

## State and Persistence Behavior
The header does not persist data itself. It encodes state exchanged across the fabric: login negotiated parameters, timeout values, registered state-change interests, link-error counters, diagnostic-capability registration, FPIN event metadata, and topology identity information. Consumers must treat variable-length arrays (`desc[]`, `pname_list[]`, `rpl_pnb[1]`) as serialized message tails whose lifetime and bounds are owned by the containing receive buffer.

## Dependencies and Integration Points
It includes `<linux/types.h>`, `<asm/byteorder.h>`, and `stddef`/`linux/stddef.h` for `offsetof`. It depends on Fibre Channel scalar types and payload bounds defined in `fc_fs.h`. Integration points are FC transport drivers, libfc, fcoe tooling, BSG ELS passthrough (`scsi_bsg_fc.h`), and diagnostic tools that parse FPIN/RDF/EDC TLV lists.

## Risks and Test Signals
Primary risks are ABI layout drift, endian mistakes, and unbounded TLV walking. Variable payloads must be length-checked before accessing flexible arrays or using `fc_tlv_next_desc()`. Packed login/discovery structs should be guarded by compile-time size/offset checks where code depends on exact wire positions. Test signals include building exported UAPI headers for userspace, sparse/endian checking for `__be*` conversions, unit tests for TLV descriptor traversal with malformed lengths, and BSG or fabric-loop tests that verify LS_ACC/LS_RJT and FPIN/RDF/EDC decoding against known payload captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_els.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_fs.h

## Purpose
`fc_fs.h` defines Fibre Channel Framing and Signalling wire constants: the FC frame header layout, routing-control values, well-known fabric IDs, frame type values, exchange ID bounds, frame-control bits, basic-link-service accept/reject payloads, port/fabric reject codes, and default timeout values. It is the foundational UAPI header used by FC protocol parsing and frame construction.

## Important APIs, Types, and Constants
`struct fc_frame_header` is the core 24-byte FC frame header, with `FC_FRAME_HEADER_LEN`, `FC_MAX_PAYLOAD`, `FC_MAX_FRAME`, and minimum payload/frame constants documenting expected sizes. `enum fc_rctl` and `FC_RCTL_NAMES_INIT` identify data, ELS, FC-4 ELS, optional headers, basic link service, and link-control routing categories.

`enum fc_well_known_fid` defines fabric service addresses such as broadcast, FLOGI, fabric controller, directory server, management server, multicast server, and domain manager base. `enum fc_fh_type` and `FC_TYPE_NAMES_INIT` identify payload protocols including BLS, ELS, IP over FC, SCSI FCP, FC-CT, ILS, and FC-NVME.

Exchange and sequence semantics are represented by `FC_XID_UNKNOWN`, `FC_XID_MIN/MAX`, and `FC_FC_*` frame-control bit masks. BLS response structures include `struct fc_ba_acc`, `struct fc_ba_rjt`, `enum fc_ba_rjt_reason`, and `enum fc_ba_rjt_explan`. Port/fabric rejects use `struct fc_pf_rjt` and `enum fc_pf_rjt_reason`. Default timing uses `FC_DEF_E_D_TOV` and `FC_DEF_R_A_TOV`.

## Control Flow and State
There is no executable code. Runtime control flow is frame parsing: consumers inspect `fh_r_ctl` and `fh_type` to dispatch payloads to BLS, ELS, FC-CT, FCP, NVMe-FC, or other handlers; use `fh_f_ctl` bits to decide sequence/exchange state and acknowledgements; and process BLS or reject payload structures for abort and error paths.

## State and Persistence Behavior
The header describes transient wire state: source/destination IDs, sequence IDs/counts, exchange IDs, relative offsets, acknowledgement expectations, abort ranges, and reject reasons. Persistence, if any, is in transport driver exchange tables and fabric login state, not in this header.

## Dependencies and Integration Points
It includes `<linux/types.h>` and supplies constants used by `fc_els.h`, `fc_gs.h`, `fc_ns.h`, FC transport drivers, libfc, FCoE code, BSG FC requests, packet decoders, and userspace diagnostic tools.

## Risks and Test Signals
Risks are exact ABI/wire layout changes, incorrect 24-bit FC_ID byte ordering, and mishandling the three-byte `fh_f_ctl` field as a native integer without explicit conversion. Tests should check `sizeof(struct fc_frame_header) == FC_FRAME_HEADER_LEN`, decode/encode known frame captures, verify reject-code mappings, and exercise abort/reject paths in FC transport integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_gs.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_gs.h

## Purpose
`fc_gs.h` defines Fibre Channel Generic Services Common Transport (FC-CT) header and generic accept/reject values. It is the shared wrapper for directory/name service and other fabric service transactions.

## Important APIs, Types, and Constants
`struct fc_ct_hdr` is the 16-byte FC-CT header with revision, originator ID, service type/subtype, command/response code, maximum/residual size, reject reason, explanation, and vendor byte fields. `FC_CT_HDR_LEN` documents expected size. `enum fc_ct_rev` currently defines revision `FC_CT_REV`.

`enum fc_ct_fs_type` names fabric service types including alias, management, time, and directory service. `enum fc_ct_cmd` defines generic reject and accept response codes (`FC_FS_RJT`, `FC_FS_ACC`). `enum fc_ct_reason` and `enum fc_ct_explan` describe reject reason and explanation values shared by service subprotocols.

## Control Flow and State
There is no executable code. FC-CT control flow is request/response dispatch: a consumer sends a frame with `FC_TYPE_CT`, parses `ct_fs_type` and `ct_fs_subtype` to select a service, interprets `ct_cmd` either as a service command or as `FC_FS_ACC`/`FC_FS_RJT`, and uses reason/explanation fields when rejected.

## State and Persistence Behavior
The header carries per-transaction state only: requested service, command, sizing, and reject metadata. Persistent fabric database state is managed by the switch/name server and by FC transport registration logic.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Name-service definitions in `fc_ns.h` rely on this CT framework, and FC BSG CT passthrough uses the first CT preamble words described here.

## Risks and Test Signals
Risks are endian conversion errors for `ct_cmd`/`ct_mr_size`, service-type/subtype mismatch, and accepting malformed short CT payloads. Test signals include known-good CT accept/reject payload decode tests, compile-time size checks, and BSG CT passthrough tests against a name server or mocked fabric service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_gs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_ns.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_ns.h

## Purpose
`fc_ns.h` defines Fibre Channel directory/name service request codes and payload structures used inside FC-CT transactions. It supports querying and registering N_Port IDs, WWPN/WWNN values, symbolic names, FC-4 type bitmaps, port type, and FC-4 feature data.

## Important APIs, Types, and Constants
`FC_NS_SUBTYPE` selects the name server common-transport subtype. `enum fc_ns_req` defines name-service commands such as `FC_NS_GA_NXT`, `FC_NS_GPN_ID`, `FC_NS_GNN_ID`, `FC_NS_GID_PN`, `FC_NS_GID_FT`, `FC_NS_GPN_FT`, `FC_NS_RPN_ID`, `FC_NS_RNN_ID`, `FC_NS_RFT_ID`, `FC_NS_RSPN_ID`, `FC_NS_RFF_ID`, and `FC_NS_RSNN_NN`.

`enum fc_ns_pt` describes port types. Object structures include `struct fc_ns_pt_obj`, `struct fc_ns_fid`, `struct fc_ns_fts`, and `struct fc_ns_ff`. Request/response payloads include `struct fc_ns_gid_pt`, `struct fc_ns_gid_ft`, `struct fc_gpn_ft_resp`, `struct fc_ns_gid_pn`, `struct fc_gid_pn_resp`, `struct fc_gspn_resp`, `struct fc_ns_rft_id`, `struct fc_ns_rn_id`, `struct fc_ns_rsnn`, `struct fc_ns_rspn`, and `struct fc_ns_rff_id`.

## Control Flow and State
There is no executable flow in the header. Name-service flow is CT-based: a driver builds `fc_ct_hdr` with directory service type and `FC_NS_SUBTYPE`, places one of these request payloads after it, and parses a response containing IDs, names, bitmaps, or a generic CT accept/reject. Registration commands update the fabric name server; query commands discover remote ports and capabilities.

## State and Persistence Behavior
The header models fabric directory state: port IDs, WWPN/WWNN registration, symbolic names, FC-4 type support, and FC-4 feature bits. Persistence is external in the fabric name server and in driver discovery caches. Variable-length symbolic-name responses are serialized tails and must be length-bound by the CT payload.

## Dependencies and Integration Points
It includes `<linux/types.h>` and integrates with `fc_gs.h` common transport, `fc_fs.h` FC frame types, SCSI FC transport discovery, FCoE/libfc, and management tools that inspect or register fabric identity.

## Risks and Test Signals
Risks are bitmap size/bit-order mistakes (`FC_NS_TYPES`, `FC_NS_BPW`), 24-bit FC_ID byte ordering, missing packed layout on variable-name structures, and treating `FC_NS_FID_LAST` incorrectly when iterating multi-object responses. Tests should include name-service payload round trips, GID_FT/GPN_FT multi-entry parsing with final-entry flags, and registration payload size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_ns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_fc.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_fc.h

## Purpose
`scsi_bsg_fc.h` defines the Fibre Channel transport Block SCSI Generic (BSG) SG_IO v4 request and reply ABI. It lets privileged userspace issue FC host or remote-port management operations such as add/delete rport, ELS, CT, and vendor-specific commands through the SCSI transport BSG path.

## Important APIs, Types, and Constants
`FC_BSG_HST_*` and `FC_BSG_RPT_*` msgcodes identify host-class and rport-class operations, with `FC_BSG_CLS_MASK`, `FC_BSG_HST_MASK`, and `FC_BSG_RPT_MASK` for classification. Host request payloads are `struct fc_bsg_host_add_rport`, `fc_bsg_host_del_rport`, `fc_bsg_host_els`, `fc_bsg_host_ct`, and `fc_bsg_host_vendor`. Rport request payloads are `struct fc_bsg_rport_els` and `fc_bsg_rport_ct`.

`struct fc_bsg_request` is the packed SG_IO v4 command descriptor with a msgcode and unioned request data. `struct fc_bsg_reply` is the request-sense reply, with `result`, `reply_payload_rcv_len`, and unioned `vendor_reply` or `ctels_reply`. `struct fc_bsg_ctels_reply` records CT/ELS completion status and reject details with `FC_CTELS_STATUS_*` values.

## Control Flow and State
The userspace flow is: open the BSG device for an FC host or rport, populate an SG_IO v4 request whose request CDB is `struct fc_bsg_request`, attach request/reply payload buffers for the ELS/CT/vendor data, and inspect `struct fc_bsg_reply` after completion. Host operations may cause the driver to log in to or enumerate a remote port; CT/ELS operations may use existing rport context or transient host-level routing.

## State and Persistence Behavior
The header itself has no state, but commands can mutate FC transport state: add-rport can create/enumerate a remote port, del-rport can request logout/removal, and ELS/CT exchanges can change fabric or endpoint state depending on payload. `result < 0` means an errno-style failure with no per-msg reply data; nonnegative results use SCSI status semantics plus message-specific reply union data.

## Dependencies and Integration Points
It includes `<linux/types.h>` and depends conceptually on SG_IO v4 BSG, SCSI FC transport classes, `fc_els.h`, `fc_gs.h`, `fc_ns.h`, and vendor ID formatting from `scsi_netlink.h`. The `vendor_cmd[]` and `vendor_rsp[]` flexible arrays are integration points for vendor-specific tools.

## Risks and Test Signals
Risks include msgcode/class mismatch, failure to keep ELS command byte in sync with the first request payload byte, confusion between transport status and LS_RJT/CT reject payload status, and unsafe vendor flexible-array sizing. Tests should issue mocked or hardware-backed BSG ELS and CT requests, verify reject reporting in both payload and `rjt_data` modes, and validate add/delete rport behavior under login failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_mpi3mr.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_mpi3mr.h

## Purpose
`scsi_bsg_mpi3mr.h` defines the Broadcom MPI3MR storage-controller BSG userspace ABI. It covers driver-specific management requests, MPI passthrough requests, adapter information/reset, target inventory, persistent event log and cached log data controls, host diagnostic buffers, NVMe encapsulated requests, SCSI task management, and PEL constants.

## Important APIs, Types, and Constants
Top-level command type `enum command` distinguishes `MPI3MR_DRV_CMD` from `MPI3MR_MPT_CMD`. Driver opcodes include `MPI3MR_DRVBSG_OPCODE_ADPINFO`, `ADPRESET`, `ALLTGTDEVINFO`, `GETCHGCNT`, `LOGDATAENABLE`, `PELENABLE`, `GETLOGDATA`, `QUERY_HDB`, `REPOST_HDB`, `UPLOAD_HDB`, and `REFRESH_HDB_TRIGGERS`. Buffer type constants identify RAID management request/response, data in/out, MPI reply/error/request, and HDB trace/firmware buffer types.

Driver-management payloads include `struct mpi3_driver_info_layout`, `mpi3mr_bsg_in_adpinfo`, `mpi3mr_bsg_adp_reset`, `mpi3mr_change_count`, `mpi3mr_device_map_info`, `mpi3mr_all_tgt_info`, `mpi3mr_logdata_enable`, `mpi3mr_bsg_out_pel_enable`, `mpi3mr_logdata_entry`, `mpi3mr_bsg_in_log_data`, `mpi3mr_hdb_entry`, `mpi3mr_bsg_in_hdb_status`, `mpi3mr_bsg_out_repost_hdb`, `mpi3mr_bsg_out_upload_hdb`, and `mpi3mr_bsg_out_refresh_hdb_triggers`.

Passthrough layout is `struct mpi3mr_bsg_drv_cmd`, `mpi3mr_bsg_mptcmd`, `mpi3mr_buf_entry`, `mpi3mr_buf_entry_list`, `mpi3mr_bsg_in_reply_buf`, and top-level `struct mpi3mr_bsg_packet`. Protocol passthrough subformats include `struct mpi3_nvme_encapsulated_request`, `mpi3_nvme_encapsulated_error_reply`, `mpi3_scsi_task_mgmt_request`, and `mpi3_scsi_task_mgmt_reply`, with constants for NVMe PRP/SGL offsets, SCSI task-management task types, response codes, PEL locales/classes, and MPI3 function codes.

## Control Flow and State
Userspace submits a BSG packet identifying either a driver command or MPI passthrough. Driver commands route by opcode and return typed payloads such as adapter info, target maps, log entries, HDB status, or reset completion. MPT commands use a variable buffer-entry list to describe request, response, data-in/data-out, error, and reply buffers, then the controller firmware executes the MPI request.

NVMe encapsulated flow sends an MPI3 NVMe encapsulated request whose command tail contains an NVMe command and whose data format is selected by PRP/SGL constants. SCSI task management flow sends a task-management request with task tag/type/LUN and receives IOC status plus response data.

## State and Persistence Behavior
The ABI can observe and mutate persistent controller state: resets can disrupt adapter state, PEL enable affects event reporting, diagnostic buffers can be posted/released/uploaded, log-data enable controls cached driver log entries, and target inventory reflects persistent firmware device handles and driver target IDs. The header relies on reserved fields for forward compatibility and variable-length arrays for inventories/logs/replies.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points are the `mpi3mr` SCSI driver, Broadcom MPI3 firmware protocol, BSG/SG_IO v4 userspace tools, RAID management applications, NVMe/SCSI passthrough clients, and persistent-event-log diagnostics.

## Risks and Test Signals
Risks are very high ABI-surface complexity, little-endian firmware field handling, C bitfield layout in PCI address fields, variable-length one-element arrays that require caller-sized buffers, and commands that can reset controllers or expose raw firmware buffers. Test signals include UAPI compile tests, ioctl/BSG ABI size tests on 32-bit and 64-bit builds, mocked driver dispatch for every driver opcode, negative tests for invalid buffer types/counts/lengths, and hardware integration tests for reset, PEL, HDB upload, NVMe encapsulation, and SCSI task management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_mpi3mr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_ufs.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_ufs.h

## Purpose
`scsi_bsg_ufs.h` defines the UFS transport BSG SG_IO v4 ABI for UPIU transaction requests and advanced RPMB/ARPMB commands. It exposes UFS query, command, UIC, and RPMB metadata structures to userspace tools that interact with UFS host controllers through BSG.

## Important APIs, Types, and Constants
`UFS_CDB_SIZE` and `UIC_CMD_SIZE` define CDB and UIC command sizing. `enum ufs_bsg_msg_code` selects `UPIU_TRANSACTION_UIC_CMD` or `UPIU_TRANSACTION_ARPMB_CMD`. `enum ufs_rpmb_op_type` identifies RPMB operations such as write key, read counter, write, read, read response, secure configuration read/write, purge enable, and purge status read.

`struct utp_upiu_header` overlays raw dwords with field accessors for transaction code, flags, LUN, task tag, command set, query/task management function, response, status, EHS length, device information, and data segment length. It uses endian-conditional bitfield order for `iid` and `command_set_type`. Request bodies are `struct utp_upiu_query`, `utp_upiu_query_v4_0`, `utp_upiu_cmd`, and `utp_upiu_req`.

RPMB/EHS support uses `struct ufs_arpmb_meta` and `struct ufs_ehs`. BSG wrappers are `struct ufs_bsg_request`, `ufs_bsg_reply`, `ufs_rpmb_request`, and `ufs_rpmb_reply`.

## Control Flow and State
Userspace constructs a `ufs_bsg_request` with a msgcode and UPIU request, submits it through BSG, and receives `ufs_bsg_reply` with a result, payload receive length, and response UPIU. ARPMB operations add EHS request/reply metadata and MAC key material around the BSG wrapper. Query request format differs for UFS 4.0 and later, where `utp_upiu_query_v4_0` exposes OSF fields.

## State and Persistence Behavior
This ABI can touch persistent UFS state: query write operations can update descriptors/attributes/flags, RPMB write-key permanently programs authentication material, secure configuration and purge operations can change device security state. The header itself does not store state; it defines one transaction's serialized UPIU and metadata.

## Dependencies and Integration Points
It includes `<asm/byteorder.h>` and `<linux/types.h>`. Integration points are the UFS host controller driver, SCSI BSG transport, UFSHCI/UPIU protocol handlers, RPMB security tooling, and SCSI command payloads embedded in `utp_upiu_cmd`.

## Risks and Test Signals
Risks include endian/bitfield portability, mixing raw dword and structured header views, wrong EHS length interpretation, and destructive RPMB operations. Tests should compile on big- and little-endian targets, validate UPIU dword field packing, round-trip query and SCSI command requests through a mock UFS BSG handler, and gate RPMB write-key/purge tests to explicit hardware-safe environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_ufs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_netlink.h

## Purpose
`scsi_netlink.h` defines the generic SCSI transport netlink event ABI. It provides the common message type, broadcast group, message header, vendor-host message layout, vendor ID encoding, alignment helper, and initializer macro used by SCSI transport event producers and consumers.

## Important APIs, Types, and Constants
`SCSI_TRANSPORT_MSG` is the netlink message type. `SCSI_NL_GRP_FC_EVENTS` identifies the FC transport event broadcast group. `struct scsi_nl_hdr` is the aligned common header with version, transport, magic, message type, and message length. Version/magic/transport constants include `SCSI_NL_VERSION`, `SCSI_NL_MAGIC`, `SCSI_NL_TRANSPORT`, `SCSI_NL_TRANSPORT_FC`, and `SCSI_NL_MAX_TRANSPORTS`.

Generic vendor host messages use `SCSI_NL_SHOST_VENDOR` and `struct scsi_nl_host_vendor_msg`. `SCSI_NL_VID_TYPE_SHIFT`, `SCSI_NL_VID_TYPE_MASK`, `SCSI_NL_VID_TYPE_PCI`, and `SCSI_NL_VID_ID_MASK` define the 64-bit vendor ID namespace. `SCSI_NL_MSGALIGN()` rounds payloads to 8-byte boundaries, and `INIT_SCSI_NL_HDR()` populates the common header.

## Control Flow and State
Kernel producers allocate a netlink message of type `SCSI_TRANSPORT_MSG`, fill `scsi_nl_hdr`, append a transport or vendor-specific payload, align to 8 bytes, and multicast to interested listeners. Userspace validates version, magic, transport, msgtype, and `msglen` before parsing the trailing payload. Vendor messages can travel in both kernel-to-user and user-to-kernel directions.

## State and Persistence Behavior
The header defines transient event packets only. Persistent state is in transport drivers and userspace subscribers. `host_no`, vendor IDs, and payload length fields are snapshots carried in individual messages.

## Dependencies and Integration Points
It includes `<linux/netlink.h>` and `<linux/types.h>`. FC transport-specific netlink messages in `scsi_netlink_fc.h` embed `scsi_nl_hdr`. BSG FC vendor IDs reference the same formatting rules.

## Risks and Test Signals
Risks include misaligned payload parsing, trusting `msglen` without comparing netlink length, vendor ID type/ID bit mistakes, and accepting messages with wrong magic/version. Tests should validate header initialization, alignment, short-message rejection, and FC event subscription through a netlink listener.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_netlink_fc.h -->
# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_netlink_fc.h

## Purpose
`scsi_netlink_fc.h` defines Fibre Channel transport-specific netlink event messages layered on the generic SCSI netlink ABI. It currently exposes asynchronous FC events from kernel to userspace.

## Important APIs, Types, and Constants
`FC_NL_ASYNC_EVENT` is the FC transport message type. `FC_NL_MSGALIGN()` mirrors generic 8-byte alignment. `struct fc_nl_event` embeds `struct scsi_nl_hdr` as the first member, then carries seconds, vendor ID, host number, data length, event number, event code, and either a single `event_data` word or flexible byte payload.

## Control Flow and State
Kernel FC transport code fills the embedded SCSI netlink header with transport `SCSI_NL_TRANSPORT_FC` and msgtype `FC_NL_ASYNC_EVENT`, appends `fc_nl_event`, and multicasts on the FC event group. Userspace first validates the generic header, then interprets FC event fields and optional vendor payload using `event_datalen`.

## State and Persistence Behavior
Events are transient notifications. `seconds`, `event_num`, and `event_code` snapshot a transport event; vendor payload interpretation is external. No persistent state is stored by the header.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<scsi/scsi_netlink.h>`. Integration points are FC transport class event emitters, netlink listeners, vendor diagnostics, and userspace daemons that react to FC topology or link events.

## Risks and Test Signals
Risks are flexible-array length validation, header-not-first regressions, vendor ID formatting mismatches, and interpreting `event_data` when `event_datalen` indicates a byte payload. Tests should verify struct alignment, first-member embedding, valid/invalid event length parsing, and multicast receive behavior for FC async events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_netlink_fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/asequencer.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/asequencer.h

## Purpose
`asequencer.h` defines the ALSA sequencer userspace ABI for MIDI-style event routing, client/port management, subscriptions, queues, timing, UMP notifications, pools, and sequencer ioctls. It is the contract for `/dev/snd/seq` event read/write and control operations.

## Important APIs, Types, and Constants
`SNDRV_SEQ_VERSION` declares the protocol version. Event type constants span system/result, note, controller, timing, queue control, client/port lifecycle, subscription lifecycle, UMP endpoint/block changes, fixed user events, variable-length SysEx/user events, kernel-private events, hardware-specific events, and `SNDRV_SEQ_EVENT_NONE`.

Addressing and event payload types include `struct snd_seq_addr`, `snd_seq_connect`, `snd_seq_ev_note`, `snd_seq_ev_ctrl`, `snd_seq_ev_ext`, `snd_seq_result`, `snd_seq_real_time`, `union snd_seq_timestamp`, `snd_seq_ev_queue_control`, `snd_seq_ev_quote`, `snd_seq_ev_ump_notify`, `union snd_seq_event_data`, `struct snd_seq_event`, and `struct snd_seq_ump_event`. Event flags cover timestamp type, absolute/relative time, fixed/variable/user-memory length, priority, and UMP packets.

Management structures include `snd_seq_system_info`, `snd_seq_running_info`, `snd_seq_client_info`, `snd_seq_client_pool`, `snd_seq_remove_events`, `snd_seq_port_info`, `snd_seq_queue_info`, `snd_seq_queue_status`, `snd_seq_queue_tempo`, `snd_seq_queue_timer`, `snd_seq_queue_client`, `snd_seq_port_subscribe`, `snd_seq_query_subs`, and `snd_seq_client_ump_info`. Ioctls provide protocol query, client ID/info, UMP info, port create/delete/query/set, subscriptions, queue create/delete/status/tempo/timer/client, pool control, event removal, and client/port iteration.

## Control Flow and State
Sequencer flow is event-oriented. A client opens `/dev/snd/seq`, queries its client ID, optionally sets client metadata and pool sizes, creates ports with capabilities/type flags, subscribes port pairs, then writes `snd_seq_event` records or reads delivered events. Timestamped events are queued using tick or real-time queues; direct events use `SNDRV_SEQ_QUEUE_DIRECT`. Queue ioctls create, configure, start/stop, and monitor timing queues.

## State and Persistence Behavior
Kernel sequencer state persists while clients, ports, queues, subscriptions, and pools exist. Event queues, client filters, port attributes, UMP endpoint/block metadata, and queue tempo/timer settings live in kernel memory and are exposed through ioctl structures. `snd_seq_ev_ext` carries a userspace pointer and length for variable data, so data lifetime is tied to the write operation and must be copied safely by the kernel.

## Dependencies and Integration Points
It includes `<sound/asound.h>` for timer IDs, protocol macros, ioctl definitions, and base ALSA types. Integration points include ALSA raw MIDI/UMP clients, MIDI applications, synth drivers, queue/timer infrastructure, and alsa-lib sequencer wrappers.

## Risks and Test Signals
Risks include 32/64-bit pointer ABI in `snd_seq_ev_ext` and quoted events, variable event length validation, queue timestamp mode mistakes, event filter bitmap bounds, and UMP-to-legacy conversion behavior. Tests should cover UAPI compilation, client/port lifecycle ioctls, subscription routing, queue tempo/timer behavior, SysEx variable events, UMP-capable clients, and compat-mode reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/asequencer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/asoc.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/asoc.h

## Purpose
`asoc.h` defines the ALSA System-on-Chip topology firmware file ABI. It describes serialized topology blocks for mixers, bytes controls, enums, DAPM graphs/widgets, PCM/front-end/back-end links, physical DAIs, stream capabilities, hardware link configurations, manifests, vendor tuples, and private data.

## Important APIs, Types, and Constants
The file starts with topology limits (`SND_SOC_TPLG_MAX_CHAN`, stream config count, hardware config count), kcontrol/widget control type IDs, DAPM widget IDs, magic `SND_SOC_TPLG_MAGIC`, ABI version constants, block data types, vendor block IDs, stream direction IDs, tuple types, DAI/link flags, DAI format IDs, clock-gating and provider/consumer constants.

`struct snd_soc_tplg_hdr` is the block header for every serialized object block. Vendor and private-data support uses `snd_soc_tplg_vendor_uuid_elem`, `snd_soc_tplg_vendor_value_elem`, `snd_soc_tplg_vendor_string_elem`, `snd_soc_tplg_vendor_array`, and `snd_soc_tplg_private`. Control metadata uses `snd_soc_tplg_tlv_dbscale`, `snd_soc_tplg_ctl_tlv`, `snd_soc_tplg_channel`, `snd_soc_tplg_io_ops`, and `snd_soc_tplg_ctl_hdr`.

Audio object structures include `snd_soc_tplg_stream_caps`, `snd_soc_tplg_stream`, `snd_soc_tplg_hw_config`, `snd_soc_tplg_manifest`, `snd_soc_tplg_mixer_control`, `snd_soc_tplg_enum_control`, `snd_soc_tplg_bytes_control`, `snd_soc_tplg_dapm_graph_elem`, `snd_soc_tplg_dapm_widget`, `snd_soc_tplg_pcm`, `snd_soc_tplg_link_config`, and `snd_soc_tplg_dai`.

## Control Flow and State
Topology load flow is serialized-file parsing: the kernel topology loader reads a `snd_soc_tplg_hdr`, verifies magic/ABI/type/size/count/payload size, then dispatches each block to the generic ASoC topology core or to component drivers for vendor/private blocks. Graph, widget, control, PCM, link, and DAI objects are registered into the card/component topology in file order, with manifests available before object allocation.

## State and Persistence Behavior
The header describes persistent runtime topology created from a firmware file: controls, DAPM widgets/routes, stream capabilities, DAI links, physical DAI parameters, and vendor private data remain in the ALSA card/component until removed or card teardown. Reserved fields and packed little-endian structures are ABI compatibility mechanisms.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<sound/asound.h>` for control name sizes, TLV types, and PCM format/rate bit namespaces. Integration points are topology compiler tools, firmware/topology blobs, the ASoC topology loader, codec/platform/component drivers, DAPM, ALSA control, PCM, and compressed stream setup.

## Risks and Test Signals
Risks are malformed topology block sizes, count/payload overflow, packed little-endian parsing errors, appending variable private/vendor data incorrectly, and changing enum values that serialized files rely on. Tests should fuzz topology block headers, load known topology blobs, verify ABI version rejection/acceptance, check object count vs payload bounds, and confirm DAPM/control/PCM objects appear as expected after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/asoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/asound.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/asound.h

## Purpose
`asound.h` is the central ALSA userspace ABI header. It defines protocol-version helpers, digital audio metadata, hardware-dependent DSP loading, PCM stream formats and ioctls, raw MIDI and UMP interfaces, timer interfaces, control/mixer interfaces, events, power states, and common structures shared by other ALSA UAPI headers.

## Important APIs, Types, and Constants
Version helpers include `SNDRV_PROTOCOL_VERSION`, major/minor/micro extraction, and compatibility testing. Digital audio metadata includes `struct snd_aes_iec958` and `snd_cea_861_aud_if`. Hardware-dependent APIs use `SNDRV_HWDEP_VERSION`, `SNDRV_HWDEP_IFACE_*`, `snd_hwdep_info`, `snd_hwdep_dsp_status`, `snd_hwdep_dsp_image`, and `SNDRV_HWDEP_IOCTL_*`.

PCM definitions include `SNDRV_PCM_VERSION`, stream/access/format/subformat enums and bitwise typedefs, PCM info flags, state values, mmap offset constants, hardware/software parameter structures (`snd_pcm_hw_params`, `snd_pcm_sw_params`), channel info, timestamp types, status/mmap/sync pointer layouts including 64-bit time variants, transfer structs, channel maps, and `SNDRV_PCM_IOCTL_*` commands for refine/params/status/sync/prepare/start/drop/drain/pause/rewind/forward/read/write/link/unlink.

Raw MIDI/UMP definitions include `SNDRV_RAWMIDI_VERSION`, stream flags, `snd_rawmidi_info`, framing mode constants and `snd_rawmidi_framing_tstamp`, `snd_rawmidi_params`, `snd_rawmidi_status`, UMP endpoint/block info structs, and `SNDRV_RAWMIDI_IOCTL_*` plus UMP ioctls. Timer definitions include timer IDs, global timer constants, `snd_timer_*` info/params/status/read/tread structures, event constants, userspace-driven timer info, and `SNDRV_TIMER_IOCTL_*`. Control definitions include `SNDRV_CTL_VERSION`, card info, element ID/list/info/value/TLV, control ioctls, control event masks, and standard control-name macros.

## Control Flow and State
PCM flow is open a PCM device, query info/protocol, refine and set hardware parameters, set software parameters, mmap or transfer samples, prepare/start/pause/drop/drain, and monitor status/delay/sync pointers. Raw MIDI flow configures stream parameters, reads/writes MIDI bytes or timestamped frames, and can query UMP endpoint/block metadata. Timer flow selects/configures a timer, starts/stops/continues/pauses, and reads events. Control flow enumerates cards/elements, reads/writes/locks controls, manages user controls/TLVs, subscribes to events, and receives `snd_ctl_event` records.

## State and Persistence Behavior
ALSA runtime state is represented extensively: PCM hardware/software params, mmap application/hardware pointers, timestamps, stream state, raw MIDI buffers and xruns, timer selection/queue/status, control element ownership/value/TLV, user-created controls, and card power state. Many structures include reserved padding for ABI extension. Some ABI behavior differs on 32-bit vs 64-bit and time64 builds, especially PCM status/sync pointer and timer read layouts.

## Dependencies and Integration Points
It conditionally includes kernel or userspace type/ioctl/endian headers and is included by sequencer, ASoC, compress, and many device-specific ALSA UAPI headers. Integration points are alsa-lib, user applications, ALSA core, PCM engine, rawmidi/UMP core, timer core, control core, hardware-dependent drivers, and compat ioctl layers.

## Risks and Test Signals
Risks are ABI breakage across architectures, y2038/time64 layout differences, `size_t` and pointer fields in UAPI structs, endian-selected PCM aliases, mmap status/control offset compatibility, and reserved-field assumptions. Tests should include UAPI header compilation under kernel and userspace modes, ioctl number stability, 32-bit compat tests, PCM mmap/read-write lifecycle tests, raw MIDI framing tests, timer event tests, and control enumeration/read/write/event subscription tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/asound.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/asound_fm.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/asound_fm.h

## Purpose
`asound_fm.h` defines the ALSA direct FM synthesizer UAPI for OPL2/OPL3 hardware. It exposes mode selection, voice/operator programming, note control, global FM parameters, SBI patch records, and hwdep ioctl commands.

## Important APIs, Types, and Constants
Mode constants are `SNDRV_DM_FM_MODE_OPL2` and `SNDRV_DM_FM_MODE_OPL3`. Core structures are `snd_dm_fm_info`, `snd_dm_fm_voice`, `snd_dm_fm_note`, and `snd_dm_fm_params`, representing synthesizer mode, operator/voice envelope and modulation settings, note frequency/key state, and global depth/rhythm/percussion settings.

Ioctls include `SNDRV_DM_FM_IOCTL_INFO`, `RESET`, `PLAY_NOTE`, `SET_VOICE`, `SET_PARAMS`, `SET_MODE`, `SET_CONNECTION`, and `CLEAR_PATCHES`. OSS-compatible command numbers are also defined. Patch records use `FM_KEY_SBI`, `FM_KEY_2OP`, `FM_KEY_4OP`, and `struct sbi_patch`.

## Control Flow and State
Userspace opens the relevant hwdep device, queries info, optionally resets the chip, sets OPL mode/connection, programs operator voices and global parameters, then plays notes by sending octave/frequency/key-on state. Patch writes use fixed-size SBI records.

## State and Persistence Behavior
The hardware/driver retains FM register state for mode, operator parameters, rhythm flags, patches, and active notes until changed, reset, or device close/driver reset. The header itself stores no state.

## Dependencies and Integration Points
It relies on ioctl macros from surrounding ALSA/UAPI include context and integrates with ALSA hwdep FM drivers, OSS compatibility paths, and userspace FM patch players/editors.

## Risks and Test Signals
Risks include invalid bit-range values for OPL register fields, OPL2/OPL3 voice count mismatch, and ambiguous OSS compatibility command use. Tests should verify ioctl number stability, mode switching, register writes for voice/note/global parameters, and patch parsing with fixed SBI/2OP/4OP keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/asound_fm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/compress_offload.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/compress_offload.h

## Purpose
`compress_offload.h` defines the ALSA compressed-audio offload userspace ABI. It supports querying DSP/codec capabilities, setting compressed stream parameters, timestamps/availability, metadata, stream control, and non-realtime task-based acceleration using DMA-BUF file descriptors.

## Important APIs, Types, and Constants
`SNDRV_COMPRESS_VERSION` declares protocol version. Stream setup uses `snd_compressed_buffer` and `snd_compr_params`, embedding `struct snd_codec` from `compress_params.h`. Runtime reporting uses `snd_compr_tstamp`, `snd_compr_tstamp64`, `snd_compr_avail`, and `snd_compr_avail64`. Capability queries use `snd_compr_caps`, `snd_compr_codec_caps`, and direction enum `snd_compr_direction`.

Metadata uses `enum sndrv_compress_encoder` and `snd_compr_metadata`. Task mode uses `SND_COMPRESS_TFLG_NEW_STREAM`, `snd_compr_task`, `enum snd_compr_state`, and `snd_compr_task_status`. Ioctls include version/caps/codec-caps/set-get-params/set-get-metadata/tstamp/avail/pause/resume/start/stop/drain/next-track/partial-drain plus task create/free/start/stop/status.

## Control Flow and State
Compressed stream flow is capability query, parameter setup, optional metadata setup, start, write/read compressed fragments, monitor availability and timestamps, then pause/resume/drain/stop as needed. Task mode creates a task using input/output DMA-BUF FDs, starts processing, polls status until finished, and frees task resources.

## State and Persistence Behavior
The kernel/DSP retains stream configuration, ring-buffer fragment geometry, codec configuration, metadata, timestamp counters, and task queue state. `no_wake_mode` changes wakeup behavior. Task sequence numbers and origin sequence numbers let userspace track asynchronous operations and possible buffer reuse.

## Dependencies and Integration Points
It includes `<linux/types.h>`, `<sound/asound.h>`, and `<sound/compress_params.h>`. Integration points are ALSA compress core, DSP firmware drivers, media frameworks using compressed offload, DMA-BUF exporters/importers, and codec capability descriptions.

## Risks and Test Signals
Risks include packed/aligned ABI layout changes, 32-bit timestamp wrap in legacy structures, fragment-size mismatch, stale DMA-BUF FDs, task lifecycle races, and confusion between decoded `pcm_frames` and output `pcm_io_frames` for A/V sync. Tests should cover capability negotiation, codec parameter round trips, timestamp/avail 32-bit and 64-bit ioctls, stream state transitions, metadata, drain behavior, and task-mode create/start/status/free error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/compress_offload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/compress_params.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/compress_params.h

## Purpose
`compress_params.h` defines codec identifiers, profiles, modes, stream formats, rate-control flags, codec-specific encoder/decoder options, capability descriptors, and `struct snd_codec` used by the ALSA compress offload ABI.

## Important APIs, Types, and Constants
Global limits include `MAX_NUM_CODECS`, `MAX_NUM_CODEC_DESCRIPTORS`, `MAX_NUM_BITRATES`, and `MAX_NUM_SAMPLE_RATES`. Codec IDs cover PCM, MP3, AMR, AMR-WB, AMR-WB+, AAC, WMA, RealAudio, Vorbis, FLAC, IEC61937, G.723.1, G.729, bespoke codecs, ALAC, APE, and raw Opus.

Profile/mode/format bitmasks cover PCM, MP3 channel modes, AMR/AMR-WB DTX/VAD and stream formats, AAC profiles and stream formats, WMA profiles/levels/formats, RealAudio modes, Vorbis, FLAC quality modes/formats, IEC61937 modes, G.723.1/G.729 annexes, and VBR/CBR rate-control. Codec-specific structures include `snd_enc_wma`, `snd_enc_vorbis`, `snd_enc_real`, `snd_enc_flac`, `snd_enc_generic`, `snd_dec_flac`, `snd_dec_wma`, `snd_dec_alac`, `snd_dec_ape`, and `snd_dec_opus`, with `union snd_codec_options` selecting the option layout.

Capabilities and configuration are represented by `struct snd_codec_desc`, `snd_codec_desc_src`, and `struct snd_codec`, including channel counts, sample rate, bit rate, profile, level, channel mode, bitstream format, alignment, PCM format, and reserved extension fields.

## Control Flow and State
This header is data-only. It is consumed by compress offload capability flow: drivers fill codec descriptor arrays describing valid profiles/modes/formats/rates; userspace selects one combination and submits `snd_codec` as part of `SNDRV_COMPRESS_SET_PARAMS`.

## State and Persistence Behavior
No state is stored by the header. Chosen codec parameters become part of the compress stream state in the kernel/DSP after setup. Descriptor arrays are snapshots of driver/DSP capabilities.

## Dependencies and Integration Points
It includes `<linux/types.h>` and is included by `compress_offload.h`. It derives many definitions from OpenMAX AL/IL concepts and integrates with ALSA compress core, DSP firmware, media frameworks, and codec-specific userspace configuration.

## Risks and Test Signals
Risks are invalid profile/mode/format combinations, treating bitmask fields as linear enums, codec-specific option union mismatch, packed alignment changes, and insufficient channel mapping for unsupported multichannel encoder cases. Tests should validate descriptor matching, reject unsupported codec combinations, round-trip every supported `snd_codec` option layout, and compare ioctl ABI sizes across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/compress_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/emu10k1.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/emu10k1.h

## Purpose
`emu10k1.h` defines the ALSA hwdep UAPI for Creative EMU10K1/Audigy FX8010 DSP programming. It exposes DSP instruction opcodes, register number spaces, bus/input/output channel maps, debug bits, TRAM memory controls, GPR control descriptors, code/TRAM/PCM records, and ioctl commands for code loading, memory access, PCM setup, and debugging.

## Important APIs, Types, and Constants
Instruction constants `iMAC0` through `iSKIP` and operand masks describe FX8010/Audigy instruction encoding. Register macros define FX buses, external inputs/outputs, Audigy-specific buses, constants, GPRs, accumulator/condition/noise/IRQ registers, TRAM data/address registers, tank-memory control bits, and channel map aliases. Debug bits include EMU10K1 and Audigy single-step, saturation, condition, and TRAM counter flags.

ABI structures include `snd_emu10k1_fx8010_info`, `emu10k1_ctl_elem_id`, `snd_emu10k1_fx8010_control_gpr`, legacy `snd_emu10k1_fx8010_control_old_gpr`, `snd_emu10k1_fx8010_code`, `snd_emu10k1_fx8010_tram`, and `snd_emu10k1_fx8010_pcm_rec`. Ioctls include info, code poke/peek, TRAM setup/poke/peek, PCM poke/peek, protocol version, stop/continue, zero TRAM counter, single-step, and debug read.

## Control Flow and State
Userspace queries DSP capabilities, prepares bitmaps and maps of GPR/TRAM/code initializers, optionally adds/removes/list GPR controls, uploads or peeks DSP code, configures TRAM and FX8010 PCM ring buffers, then starts/stops or single-steps the DSP for debugging. TRAM operations can clear or read/write internal/external delay memory.

## State and Persistence Behavior
The driver/hardware retains DSP code, GPR initial values, control definitions, TRAM contents, PCM routing/ring-buffer state, and debug/single-step state until overwritten or reset. Pointer fields in UAPI structures point to userspace arrays that are copied during ioctl handling and are sensitive to compat translation.

## Dependencies and Integration Points
It conditionally includes `<linux/types.h>` and defines a local bitmap macro for userspace visibility. Integration points are ALSA hwdep, mixer controls, PCM routing, EMU10K1/Audigy DSP firmware tools, and legacy userspace DSP loaders.

## Risks and Test Signals
Risks include pointer-heavy UAPI structures, 32/64-bit compat handling, user-provided bitmap/map length mismatches, programming invalid register/instruction indexes, legacy control ABI differences, and hardware state corruption from malformed code. Tests should cover ioctl number stability, compat ioctl translation, code/TRAM/PCM poke-peek round trips with bounds checks, GPR control add/delete/list behavior, and debug single-step on supported hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/emu10k1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/fcp.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/fcp.h

## Purpose
`fcp.h` defines the ALSA hwdep userspace ABI for the Focusrite Control Protocol driver. It exposes privileged control of proprietary Focusrite USB audio interface features for Scarlett, Clarett, Clarett+, and Vocaster devices.

## Important APIs, Types, and Constants
Version macros define FCP hwdep version 2.0.0 and extraction helpers. Ioctls are `FCP_IOCTL_PVERSION`, `FCP_IOCTL_INIT`, `FCP_IOCTL_CMD`, `FCP_IOCTL_SET_METER_MAP`, and `FCP_IOCTL_SET_METER_LABELS`.

`struct fcp_init` contains step 0/2 response sizes, two initialization opcodes, and a flexible response tail. `struct fcp_cmd` contains an opcode, request size, response size, and in-place flexible data buffer. `struct fcp_meter_map` configures control-channel-to-meter mappings with signed slots, and `struct fcp_meter_labels` provides null-terminated label data.

## Control Flow and State
Userspace opens the hwdep device with `CAP_SYS_RAWIO`, queries protocol version, calls `FCP_IOCTL_INIT` to synchronize sequence numbers and protocol state, then uses `FCP_IOCTL_CMD` for device commands. Meter support is configured by setting a meter map, then labels. The map size and slot count become fixed after first configuration, though mappings may be updated.

## State and Persistence Behavior
Initialization synchronizes driver/device sequence state. Meter map and labels configure ALSA level-meter controls and remain functional after the hwdep device closes. Command buffers are variable-length and response data overwrites request data.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/ioctl.h>`. Integration points are ALSA hwdep, the Focusrite USB mixer/scarlett2 driver, privileged user daemons such as fcp-server, and level-meter ALSA controls.

## Risks and Test Signals
Risks include privileged near-direct device access, flexible-array size validation, sequence synchronization mistakes, response-overwrites-request buffer sizing, and immutable meter map dimensions after configuration. Tests should cover version/init flow, invalid command before init, command req/resp size bounds, meter map reconfiguration rules, label parsing, and permission enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/fcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/firewire.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/firewire.h

## Purpose
`firewire.h` defines ALSA FireWire hwdep userspace ABI events and ioctls for DICE, Fireworks, BeBoB, OXFW, Digi00x, TASCAM, MOTU, and RME Fireface devices. It supports reading async event records, querying device info, stream locking, TASCAM state, MOTU DSP meters/parameters, and Fireface 400 messages.

## Important APIs, Types, and Constants
Event type constants identify lock status, DICE notification, Echo Fireworks response, Digi00x message, MOTU notification, TASCAM control, MOTU register DSP change, and FF400 message. Event structures include common/lock/DICE/EFW transaction/response/Digi00x/MOTU/TASCAM/MOTU register DSP/FF400 forms and `union snd_firewire_event`.

Ioctls include `SNDRV_FIREWIRE_IOCTL_GET_INFO`, `LOCK`, `UNLOCK`, `TASCAM_STATE`, `MOTU_REGISTER_DSP_METER`, `MOTU_COMMAND_DSP_METER`, and `MOTU_REGISTER_DSP_PARAMETER`. Device type constants identify supported FireWire driver families. MOTU structures provide fixed-size register-DSP meter and parameter snapshots and command-DSP meter data. `snd_firewire_get_info` returns type, card, GUID, and device name.

## Control Flow and State
Userspace reads event records from the hwdep device and dispatches by the leading `type` word. It can query static device identity, lock streaming before exclusive operations, unlock after configuration, and use family-specific ioctls to fetch state or DSP meter/parameter data. Fireworks transaction fields are big endian; variable-length events use trailing arrays whose size is determined by read length and count fields.

## State and Persistence Behavior
Lock/unlock affects streaming availability. Device-specific state includes TASCAM control state, MOTU register/command DSP meter snapshots and parameters, and Fireface hardware knob messages. Event queues are transient and filled by driver notifications from asynchronous or isochronous FireWire traffic.

## Dependencies and Integration Points
It includes `<linux/ioctl.h>` and `<linux/types.h>`. Integration points are ALSA hwdep FireWire drivers, IEC 61883/FireWire device stacks, userspace mixers/control panels, and model-specific DSP control utilities.

## Risks and Test Signals
Risks include variable-length event parsing, endian handling for Fireworks/TASCAM fields, float vs `__u32` representation of MOTU command-DSP meters between kernel and userspace, lock-state races with streaming, and model-dependent channel mapping. Tests should cover event read dispatch with every type, ioctl lock/unlock behavior under active streams, TASCAM/MOTU/FF400 payload sizing, and endian conversion for big-endian device transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/firewire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/hdsp.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/hdsp.h

## Purpose
`hdsp.h` defines the ALSA hwdep UAPI for RME Hammerfall DSP cards. It exposes ioctl structures for peak/RMS meters, configuration status, firmware upload, hardware version, mixer matrix, and HDSP 9632 expansion board detection.

## Important APIs, Types, and Constants
`HDSP_MATRIX_MIXER_SIZE` fixes the mixer matrix array length. `enum HDSP_IO_Type` identifies Digiface, Multiface, H9652, H9632, RPM, and Undefined variants. `struct hdsp_peak_rms` returns input/playback/output peaks and RMS values. `struct hdsp_config_info` reports sync status, SPDIF settings, sample rates, clocking, gain, passthrough, and expansion-board configuration.

`struct hdsp_firmware` carries a userspace firmware pointer. `struct hdsp_version` reports IO type and firmware revision. `struct hdsp_mixer` returns a 2048-entry matrix. `struct hdsp_9632_aeb` reports analog expansion input/output boards. Ioctls are `GET_PEAK_RMS`, `GET_CONFIG_INFO`, `UPLOAD_FIRMWARE`, `GET_VERSION`, `GET_MIXER`, and `GET_9632_AEB`.

## Control Flow and State
Userspace opens the HDSP hwdep device, queries version/config/meters/mixer, optionally uploads firmware via a firmware-data pointer, and checks AEB expansion status on 9632 devices. Meter and config ioctls are snapshot queries; firmware upload mutates device state.

## State and Persistence Behavior
The card/driver maintains firmware load state, clock/sync configuration, mixer matrix, meter counters, and expansion-board detection. The header itself is a binary ABI with fixed arrays plus a pointer for firmware upload.

## Dependencies and Integration Points
It conditionally includes `<linux/types.h>` and integrates with ALSA hwdep, RME HDSP drivers, mixer applications, firmware loaders, and metering tools.

## Risks and Test Signals
Risks include pointer-size compat handling in `hdsp_firmware`, hard-coded firmware size expectations, fixed meter/mixer array sizing, and hardware-specific meaning of config bytes. Tests should check ioctl number stability, compat firmware upload, meter/config/mixer snapshot sizes, firmware upload error handling, and variant-specific version/AEB behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/hdsp.h -->
