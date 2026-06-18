# Research: subset-b-005260

This grouped report covers the FNIC FCoE driver completion-descriptor, FCP firmware ABI, FIP, FDLS discovery, core private-state, and host sysfs attribute files under `sources/distributed-fs/ceph-client/drivers/scsi/fnic/`. Each file section is source-path aligned for reconciliation into its corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_enet_desc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_enet_desc.h

## Purpose

`cq_enet_desc.h` defines the 16-byte Ethernet completion queue descriptor formats used by the Cisco vNIC/FNIC hardware path. It covers completions for Ethernet work queues and receive queues, including generic CQ metadata plus Ethernet, VLAN, checksum, RSS, FCoE SOF/EOF, CRC, and error indicators. The file is a firmware/hardware ABI helper rather than a policy module: callers pass a descriptor and receive decoded scalar fields.

## Important APIs, Types, and Functions

- `struct cq_enet_wq_desc`: Ethernet work-queue completion with `completed_index`, `q_number`, reserved bytes, and `type_color`.
- `cq_enet_wq_desc_dec()`: thin wrapper around `cq_desc_dec()` for type, color, queue number, and completed index.
- `struct cq_enet_rq_desc`: receive completion layout with packed flag fields, RSS hash, byte count, VLAN, checksum/FCoE, protocol flags, and `type_color`.
- `CQ_ENET_RQ_DESC_*` macros: masks and flag bits for SOP/EOP, ingress port, FCoE, RSS type, checksum availability, truncation, VLAN stripping, FCoE SOF/EOF, TCP/UDP/IP checksum status, protocol type, and FCS status.
- `cq_enet_rq_desc_dec()`: decodes all receive-completion fields, performs little-endian conversion for multi-byte descriptor fields, and switches `checksum_fcoe` interpretation based on the decoded FCoE bit.

## Control Flow

The decode flow starts by converting the packed `completed_index_flags`, `q_number_rss_type_flags`, and `bytes_written_flags` fields from little-endian to CPU order. It then delegates generic CQ metadata extraction to `cq_desc_dec()`. The rest of the function masks and shifts individual bitfields into one-byte booleans or scalar outputs. For non-FCoE frames, `checksum_fcoe` is returned as the network checksum. For FCoE frames, the same storage is split into SOF/EOF metadata, FC CRC status, and encapsulation error status, and the checksum output is forced to zero.

## State and Persistence Behavior

This header has no persistent state, allocation, locking, or side effects. Its only state interaction is through caller-owned descriptor memory and caller-provided output pointers. Correctness depends on callers reading a descriptor only after CQ color ownership indicates that hardware has completed writing it.

## Dependencies and Integration Points

The file depends on `cq_desc.h` for generic CQ decoding and queue-number bit constants, plus Linux byte-order helpers such as `le16_to_cpu()` and `le32_to_cpu()`. It integrates with FNIC/vNIC receive completion processing: receive CQ handlers decode these descriptors before recycling RQ buffers and dispatching Ethernet/FIP/FCoE frames into the FNIC frame handling paths.

## Risks and Edge Cases

- The descriptor layout is a hardware ABI. Field reordering, size changes, or incorrect masks will corrupt completion interpretation.
- The FCoE and non-FCoE meanings of `checksum_fcoe` overlap, so callers must trust the decoded `fcoe` flag before using checksum or SOF/EOF data.
- `desc->checksum_fcoe` is shifted directly in the FCoE EOF path rather than shifting the already converted temporary, so the code assumes the expression behaves correctly for the underlying little-endian type.
- The function writes many output pointers without null checks; it is only safe for internal callers that pass a complete output set.
- Packet truncation is reported as `packet_error`, so downstream paths must not confuse it with FC CRC or encapsulation errors.

## Test Signals

Useful signals include receive-path tests for plain Ethernet and FCoE frames, VLAN-stripped and non-stripped packets, truncated frames, RSS hash/type reporting, checksum-not-calculated cases, IPv4/IPv6/TCP/UDP flag combinations, FC CRC failures, FCoE encapsulation errors, and CQ color wrap behavior under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_enet_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_exch_desc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_exch_desc.h

## Purpose

`cq_exch_desc.h` defines completion queue descriptors for Fibre Channel exchange-oriented work in the FNIC/vNIC SCSI datapath. It decodes work-queue exchange completions, FCP receive completions, and SGL completion/error descriptors. These descriptors bridge low-level CQ polling with higher-level FCP I/O, abort, and SGL error handling.

## Important APIs, Types, and Functions

- `struct cq_exch_wq_desc`: exchange work-queue completion containing completed index, queue number, exchange ID, template field, status, and type/color.
- `enum cq_exch_status_types`: completion status values for complete, abort, SGL EOF, and template error.
- `cq_exch_wq_desc_dec()`: decodes generic CQ fields and masks `exch_status`.
- `struct cq_fcp_rq_desc`: FCP receive descriptor carrying completed index, SOP/EOP, ingress port, exchange ID, template, byte count, VLAN, SOF/EOF, FC CRC, FCoE error, and FCS status.
- `cq_fcp_rq_desc_dec()`: extracts FCP receive state and packet/error metadata.
- `struct cq_sgl_desc`: SGL completion/error descriptor with exchange ID, queue number, active burst offset, total data bytes, template, SGL error, and type/color.
- `enum cq_sgl_err_types`: SGL failure codes for overflow, local address errors, response errors, zero/max counts, ordering, host CQ write errors, and no-error.
- `cq_sgl_desc_dec()`: decodes SGL CQ metadata and SGL-specific fields.

## Control Flow

All decode helpers first call `cq_desc_dec()` to obtain common CQ type, color, queue number, and completion index. `cq_exch_wq_desc_dec()` then returns the two-bit exchange status. `cq_fcp_rq_desc_dec()` interprets packed SOP/EOP/port bits from `completed_index_eop_sop_prt`, extracts template and byte-count masks, shifts packet/VLAN/error bits, and returns raw SOF/EOF and VLAN values. `cq_sgl_desc_dec()` treats `exchange_id` as the completed index for generic CQ decode, then returns transfer offsets, total byte count, template, and masked SGL error.

## State and Persistence Behavior

This header maintains no persistent state. It turns a hardware-owned descriptor snapshot into caller-owned scalar values. The operational state represented by the decoded fields belongs to firmware exchanges, FCP receive paths, and SGL engines elsewhere in the driver.

## Dependencies and Integration Points

The file depends on `cq_desc.h`. It is consumed by vNIC CQ completion handlers and FNIC SCSI/FCP code that must map hardware CQ entries into `fcpio` completions, receive-frame processing, abort handling, and SGL error accounting. The descriptor status values should be correlated with `fcpio_status` and FNIC SCSI error handling when diagnosing I/O failures.

## Risks and Edge Cases

- Unlike `cq_enet_desc.h`, these structures use plain integer types and the helpers do not perform explicit endian conversion. That is safe only if this hardware ABI is already CPU-endian for this path or the surrounding CQ copy layer normalizes it.
- `cq_sgl_desc_dec()` deliberately "cheats" by using `exchange_id` as the completed index. Any hardware layout change that breaks that equivalence would misroute SGL completions.
- Byte-count and VLAN-stripped fields share packed storage; mask/shift mistakes can convert packet errors into data length corruption.
- Error handling depends on distinguishing SGL EOF from abort/template errors and on mapping detailed `CQ_SGL_ERR_*` reasons to the right reset or retry policy.

## Test Signals

Validation should cover normal exchange completions, abort completions, template errors, FCP receive SOP/EOP combinations, VLAN-stripped receive frames, packet/FCoE/FCS/FC-CRC error injection, SGL overflow and address errors, SGL order errors, and CQ wrap/color behavior while multiple copy work queues are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_exch_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fcpio.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fcpio.h

## Purpose

`fcpio.h` is the host-to-firmware and firmware-to-host command ABI for FNIC FCP I/O. It defines request/response types, status codes, command tags, initiator SCSI commands, task management commands, target-mode command structures, reset/FLOGI/echo/lunmap requests, fixed-size host and firmware request unions, CQ color-bit handling, and SCSI vNIC LUN map formats.

## Important APIs, Types, and Functions

- `enum fcpio_type`: command and completion type namespace, including initiator commands (`FCPIO_ICMND_16`, `FCPIO_ICMND_32`, completions, and ITMF), target-mode requests, ACK/reset/FLOGI/echo/lunmap, and FIP FLOGI registration.
- `enum fcpio_status`: firmware header and completion status values such as invalid header/parameter, out of resources, abort, timeout, SGL invalid, data count mismatch, firmware error, task-management failure, no path, path failed, and LUN map change pending.
- `struct fcpio_tag` plus `fcpio_tag_id_*()` and `fcpio_tag_exid_*()`: encodes either a host request ID or FC OX/RX exchange IDs.
- `struct fcpio_header` plus `fcpio_header_enc()` and `fcpio_header_dec()`: common type/status/tag header for all requests and responses.
- `struct fcpio_icmnd_16` and `struct fcpio_icmnd_32`: host initiator SCSI commands with LUN map ID, SGL address/count, sense buffer address/length, CDB, flags, FC destination, and timeouts.
- `struct fcpio_itmf` and `enum fcpio_itmf_tm_req_type`: host task management and abort requests.
- Target-mode structures: `fcpio_tdata`, `fcpio_txrdy`, `fcpio_trsp`, `fcpio_ttmf_ack`, `fcpio_tabort`, target command notifications, target TMF, and target abort completions.
- Miscellaneous structures: `fcpio_reset`, `fcpio_flogi_reg`, `fcpio_flogi_fip_reg`, `fcpio_echo`, `fcpio_lunmap_req`, and their completions/notifications.
- `struct fcpio_host_req`: 128-byte host request envelope.
- `struct fcpio_fw_req`: 64-byte firmware request/completion envelope.
- `fcpio_color_enc()` and `fcpio_color_dec()`: manipulate and read the firmware request color bit, with `rmb()` after color read to order descriptor contents.
- `struct fcpio_lunmap_entry` and `struct fcpio_lunmap_tbl`: 256-entry LUN map table for SCSI vNICs.

## Control Flow

Runtime code fills `struct fcpio_host_req` with a common header and one union member, posts it through a vNIC work queue, and later receives a `struct fcpio_fw_req` from firmware. `fcpio_header_dec()` and tag decoding identify the request or exchange being completed. Initiator I/O completions use `fcpio_icmnd_cmpl` status, residual, and sense length; task management completions use ITMF response status; ACK messages carry firmware's last received work entry; reset/FLOGI/echo/lunmap completions advance control paths. Firmware-owned descriptors use the color bit in the last byte as the ownership/validity marker, and `fcpio_color_dec()` enforces a read barrier before callers inspect the rest of the descriptor.

## State and Persistence Behavior

The header itself has no mutable global state, but it defines all firmware-visible state exchanged across the host/adapter boundary. Tags persist for the lifetime of outstanding requests, SGL and sense addresses point into DMA-mapped host memory, LUN maps persist until firmware reports a change, and FLOGI registration state tells firmware the FC identity/MAC selection in use. The fixed 128-byte and 64-byte envelope sizes are an ABI persistence boundary across driver and firmware versions.

## Dependencies and Integration Points

The file depends on Ethernet address definitions from `<linux/if_ether.h>`. It is used heavily by `fnic_scsi.c` for SCSI command submission/completion, abort and reset handling, firmware reset completion, FLOGI registration completion, ACK processing, and status-to-SCSI-result mapping. It also interacts with `fnic_fdls.h` and `fip.c` through FLOGI/FIP registration payloads and with vNIC work-queue/copy-work-queue code that transports these envelopes.

## Risks and Edge Cases

- Structure layout, envelope size, and field offsets must match firmware exactly.
- Many fields are plain integer types rather than annotated `__le` or `__be`; callers must know which fields are firmware-endian, FC big-endian, or host-endian.
- Tag reuse before a delayed completion arrives can complete the wrong SCSI command; the FNIC tag and OXID lifetimes must stay aligned with this ABI.
- Incorrect SGL count/address/sense length can trigger firmware SGL errors or corrupt host memory.
- `fcpio_color_dec()` relies on hardware writing the color bit last. Removing or moving the barrier can expose stale descriptor contents.
- Status values such as `FCPIO_LUNMAP_CHNG_PEND`, `FCPIO_PATH_FAILED`, and task-management failures need careful mapping to SCSI retry, failfast, or transport events.

## Test Signals

Useful tests include normal read/write completions for 16-byte and 32-byte CDB paths, residual under/over handling, sense data transfer, abort-task and LUN-reset completions, reset completion, FLOGI and FIP FLOGI registration completion, ACK index tracking, LUN-map change notification, firmware timeout/abort/SGL-invalid/data-count-mismatch statuses, color-bit wrap, and DMA/SGL stress under queue depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fcpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fdls_disc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fdls_disc.c

## Purpose

`fdls_disc.c` implements FNIC Fabric Discovery and Login Services for FCoE. It drives non-FIP fabric login, name-server registration, state-change registration, target discovery, target login/PRLI/ADISC, FDMI registration, RSCN handling, LOGO/ABTS handling, and link-down cleanup. It is the main FC control-plane state machine that turns link availability into registered SCSI remote ports.

## Important APIs, Types, and Functions

Externally referenced functions include:

- `fdls_alloc_frame()`: allocates a zeroed FCoE frame from `fnic->frame_pool`.
- `fdls_alloc_oxid()`, `fdls_free_oxid()`, `fdls_schedule_oxid_free()`, `fdls_reclaim_oxid_handler()`, and `fdls_schedule_oxid_free_retry_work()`: manage the bitmap-based OXID pool and delayed OXID reclamation.
- `fnic_del_fabric_timer_sync()` and `fnic_del_tport_timer_sync()`: cancel fabric/target timers while temporarily releasing `fnic_lock`.
- `fdls_send_tport_abts()`, `fdls_send_fabric_logo()`, `fdls_tgt_logout()`, and `fdls_delete_tport()`: explicit abort, logout, and target deletion helpers used by discovery and teardown paths.
- `fnic_find_tport_by_fcid()` and `fnic_find_tport_by_wwpn()`: lookup live, non-terminating target ports.
- `fnic_fdls_disc_start()`: starts FDLS after link/FIP login.
- `fnic_fdls_validate_and_get_frame_type()`: classifies received FC/FCoE frames after checking frame control, type, S_ID/D_ID, and OXID frame type.
- `fnic_fdls_recv_frame()`: top-level receive dispatcher for fabric, FDMI, target, ABTS, and unsolicited ELS frames.
- `fnic_fdls_disc_init()` and `fnic_fdls_link_down()`: initialize/reset FDLS state and process link down.

Major internal senders include `fdls_send_fabric_flogi()`, `fdls_send_fabric_plogi()`, `fdls_send_rpn_id()`, `fdls_send_register_fc4_types()`, `fdls_send_register_fc4_features()`, `fdls_send_scr()`, `fdls_send_gpn_ft()`, `fdls_send_tgt_plogi()`, `fdls_send_tgt_prli()`, `fdls_send_tgt_adisc()`, `fdls_send_fdmi_plogi()`, `fdls_fdmi_register_hba()`, and `fdls_fdmi_register_pa()`.

Major response handlers include `fdls_process_flogi_rsp()`, `fdls_process_fabric_plogi_rsp()`, `fdls_process_rpn_id_rsp()`, `fdls_process_rft_id_rsp()`, `fdls_process_rff_id_rsp()`, `fdls_process_scr_rsp()`, `fdls_process_gpn_ft_rsp()`, `fdls_process_tgt_plogi_rsp()`, `fdls_process_tgt_prli_rsp()`, `fdls_process_tgt_adisc_rsp()`, `fdls_process_fabric_abts_rsp()`, `fdls_process_tgt_abts_rsp()`, `fdls_process_fdmi_plogi_rsp()`, `fdls_process_fdmi_reg_ack()`, `fdls_process_fdmi_abts_rsp()`, `fdls_process_rscn()`, `fdls_process_logo_req()`, `fdls_process_adisc_req()`, `fdls_process_rls_req()`, and generic ELS accept/reject helpers.

## Control Flow

Discovery begins with `fnic_fdls_disc_start()`. It posts an FC host LIP reset event and either sends a fabric FLOGI for non-FIP operation or, when FIP already completed login, starts with fabric PLOGI to the directory server. On non-FIP first link-up, it also calls `fnic_fcpio_reset()` before sending FLOGI.

The non-FIP fabric sequence is FLOGI, PLOGI to directory server, RPN_ID, RFT_ID, RFF_ID, SCR, and GPN_FT. Each sender allocates an OXID, fills the FC header/payload, sends through `fnic_send_fcoe_frame()`, and arms a fabric retry timer. The response handlers validate state and OXID, free the OXID, cancel timers, update fabric/iport parameters, and advance to the next step. Busy/unable rejects set `FNIC_FDLS_RETRY_FRAME` so `fdls_fabric_timer_callback()` retries from a controlled timer path.

Target discovery is driven by GPN_FT. `fdls_process_gpn_ft_tgt_list()` parses each returned FCID/WWPN, creates new `fnic_tport_s` entries, reconciles FCID changes for an existing WWPN, and after RSCN marks missing targets for deletion. `fdls_tgt_discovery_start()` sends PLOGI to new targets or ADISC to targets marked by RSCN. Successful target PLOGI learns WWNN/WWPN, max frame size, and concurrent sequence limits, then sends PRLI. Successful PRLI verifies SCSI FCP target capability, records retry support, moves the target to READY, and queues `TGT_EV_RPORT_ADD` on `fnic_event_queue`.

Timers provide abort-and-retry control. `fdls_fabric_timer_callback()` sends ABTS when a fabric request times out, schedules delayed OXID reclaim when ABTS times out, and retries or falls back to PLOGI depending on state. `fdls_tport_timer_callback()` performs the analogous logic for target PLOGI, PRLI, and ADISC, deleting target ports when retries are exhausted. `fdls_fdmi_timer_callback()` aborts pending FDMI PLOGI/RHBA/RPA exchanges and retries FDMI registration up to its limit.

The receive path enters at `fnic_fdls_recv_frame()`. It finds the FC header at the supplied offset, logs/debug-dumps when enabled, classifies the frame with `fnic_fdls_validate_and_get_frame_type()`, suppresses unrelated frames during FLOGO, and dispatches to response or request handlers. Unsolicited RSCN triggers GPN_FT and RSCN accept, LOGO removes a target and may restart GPN_FT, ADISC/RLS/ECHO/RRQ are accepted or rejected based on current iport/tport state, and unsupported ELS requests are rejected.

Link down enters `fnic_fdls_link_down()`. It moves the fabric state to LINKDOWN, clears fabric flags, calls `fnic_fcpio_reset()` outside `fnic_lock`, deletes all tports, cancels FDMI pending state, and clears the FDMI-active flag.

## State and Persistence Behavior

The file mutates the in-memory `fnic_iport_s` and `fnic_tport_s` control-plane state. Key state includes `iport->fabric.state`, fabric retry flags, retry counters, timer-pending flags, active fabric/FDMI OXIDs, FDMI pending bitmask, `iport->state`, `iport->fcid`, `r_a_tov`, `e_d_tov`, `max_payload_size`, host transport fields, the OXID bitmap/reclaim lists, and `iport->tport_list`. Target state includes FCID, WWPN/WWNN, active OXID, PRLI service parameters, retry support, max payload size, timers, SCSI registration flags, and deletion/terminating flags.

No data is persisted to disk. State persists in memory across I/O until link down, device removal, reset, LOGO, RSCN reconciliation, or module unload. Some target operations queue work to `fnic_event_queue`, so target lifetime spans both FDLS lock-protected state and asynchronous SCSI transport registration/deletion handlers.

## Dependencies and Integration Points

The file depends on `fnic.h`, `fdls_fc.h`, `fnic_fdls.h`, Linux FC/FCoE headers, SCSI transport FC, workqueues, timers, mempools, and UTS host identity. It integrates with `fnic_fcs.c` through `fnic_send_fcoe_frame()`, `fnic_fdls_register_portid()`, `fnic_fdls_learn_fcoe_macs()`, `fnic_fcpio_reset()`, and SCSI remote-port add/remove helpers. It also integrates with `fip.c`: FIP completion can skip FDLS FLOGI and start FDLS at fabric PLOGI, while FIP cleanup calls FDLS link-down paths.

## Risks and Edge Cases

- Locking is delicate. Many functions assume `fnic_lock` is held, and timer cancellation helpers intentionally drop and reacquire it.
- OXID lifecycle is central. Stale responses, timed-out ABTS, delayed reclaim, and OXID reuse can misassociate responses if state/OXID checks regress.
- `fnic_fdls_validate_and_get_frame_type()` is the security and correctness gate for unsolicited FC frames; missing validation can let wrong S_ID/D_ID/type combinations mutate discovery state.
- RSCN processing handles malformed payloads, port-change RSCN, zero-FCID wildcard pages, and optional PCRSCN host reset. These branches are easy to regress.
- Target deletion spans local list removal, exchange reset, queued SCSI transport events, and timer state. Double deletion or use-after-free is the primary lifetime risk.
- FDMI is optional and parallel to fabric PLOGI, which makes its timers and active OXIDs independent from the main fabric active OXID.
- Several paths continue after allocation/send failure by arming retry timers, so tests need to observe recovery rather than only immediate return values.

## Test Signals

Useful signals include full fabric login through FLOGI/PLOGI/RPN/RFT/RFF/SCR/GPN_FT, FIP-complete entry into PLOGI, target PLOGI/PRLI registration, RSCN-triggered ADISC and target deletion, LOGO from target, fabric LOGO, ABTS accept/reject paths, timeout and busy-reject retries, OXID delayed reclaim, FDMI PLOGI/RHBA/RPA registration and abort timeout, malformed RSCN payloads, unsupported ELS rejection, RLS/ECHO/RRQ/ADISC request handling, link-down during discovery, and remote-port add/remove event ordering under SCSI I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fdls_disc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fdls_fc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fdls_fc.h

## Purpose

`fdls_fc.h` defines Fibre Channel and FCoE constants, frame classification macros, field accessors, and packed wire-format structures used by FNIC FDLS and FIP code. It is the shared vocabulary for building and decoding FLOGI/PLOGI, ELS accept/reject, ADISC, RLS, ABTS, PRLI, name-server CT requests, FDMI requests, GPN_FT responses, RSCN, LOGO, and Ethernet/FCoE header offsets.

## Important APIs, Types, and Definitions

- Service parameter and FC constants: FNIC FCP service parameters, unassigned OX/RX IDs, ELS/FCP/ABTS F_CTL values, FC-PH version, buffer-to-buffer credit, default receive data field size, frame-size limits, timeout unit conversion, and PRLI target function bit.
- `FNIC_LOGI_*` macros: get/set FLOGI/PLOGI common service parameters, port name, node name, R_A_TOV, E_D_TOV, and receive data field size.
- `FNIC_STD_SET_*` and `FNIC_STD_GET_*` macros: write/read FC frame header fields, FC IDs, OX/RX IDs, WWNs, and CT commands using the proper unaligned big-endian helpers where needed.
- `FNIC_FC_FRAME_*` macros: classify unsolicited frames, solicited data/control replies, F_CTL patterns, FC type, CS_CTL, ELS, BLS, and FC-GS frames.
- Packed structures such as `fc_std_flogi`, `fc_std_els_acc_rsp`, `fc_std_els_rjt_rsp`, `fc_std_els_adisc`, `fc_std_rls_acc`, `fc_std_abts_ba_acc`, `fc_std_abts_ba_rjt`, `fc_std_els_prli`, `fc_std_rpn_id`, `fc_std_fdmi_rhba`, `fc_std_fdmi_rpa`, `fc_std_rft_id`, `fc_std_rff_id`, `fc_std_gpn_ft`, `fc_gpn_ft_rsp_iu`, `fc_std_rls`, `fc_std_scr`, `fc_std_rscn`, and `fc_std_logo`.
- `FNIC_ETH_FCOE_HDRS_OFFSET`: offset from an Ethernet frame start to the FC header/payload after Ethernet and FCoE headers.

## Control Flow and Design Role

This header does not implement a state machine. Instead, senders in `fdls_disc.c` allocate a frame, offset to `FNIC_ETH_FCOE_HDRS_OFFSET`, cast to one of these packed structures, and fill header/payload fields with the provided macros. Receivers in FDLS validate frame type and fields with the classification macros, then cast to the appropriate structure for response-specific parsing.

## State and Persistence Behavior

There is no local state. The structures describe transient FC/FCoE frames. Their exact layout persists as an interoperability contract with fabrics, FCFs, targets, name server, management server, and the Linux FC header definitions.

## Dependencies and Integration Points

The header depends on Linux SCSI FC/FCoE UAPI headers, FC ELS/GS/NS/MS definitions, Ethernet headers, and unaligned/big-endian helpers. It is included by `fdls_disc.c`, `fip.h`, and FNIC initialization paths that need frame pool sizing. Its structures are the direct payloads passed to `fnic_send_fcoe_frame()` and parsed by `fnic_fdls_recv_frame()`.

## Risks and Edge Cases

- Many macros write multi-byte fields in big-endian FC order; using plain assignment in callers would break wire format.
- The F_CTL setters and classifiers operate on byte arrays and sometimes shift constants before writing 24-bit fields, so callers must use the expected constant form.
- Packed wire structures rely on external FC header definitions remaining compatible.
- GPN_FT response parsing depends on `struct fc_gpn_ft_rsp_iu` matching the CT response list element exactly, including the `ctrl` last-entry bit.
- `FNIC_ETH_FCOE_HDRS_OFFSET` must match the actual receive/transmit buffer layout used by frame allocation and hardware.

## Test Signals

Useful validation includes frame captures for FLOGI/PLOGI/PRLI/SCR/RPN/RFT/RFF/GPN_FT/FDMI/RSCN/LOGO/ADISC/RLS/ABTS, checks for correct S_ID/D_ID/OX_ID/RX_ID/F_CTL values, big-endian WWN and FCID encoding, GPN_FT multi-entry parsing, and interoperability with fabrics that send ECHO/RRQ, malformed RSCN, or different class-3 service parameter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fdls_fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fip.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fip.c

## Purpose

`fip.c` implements FNIC's FCoE Initialization Protocol control path. It discovers FCoE VLANs, selects an FCF from advertisements, performs FIP-encapsulated FLOGI, maintains FCF/enode/VN-port keepalives, processes Clear Virtual Link messages, and restarts discovery after timeouts or link/control failures.

## Important APIs, Types, and Functions

- `fnic_fcoe_reset_vlans()`: clears the discovered VLAN list under `vlans_lock`.
- `fnic_fcoe_send_vlan_req()`: sends a VLAN request to all FCFs, resets VLAN state, clears VLAN tag, sets `FDLS_FIP_VLAN_DISCOVERY_STARTED`, and arms `retry_fip_timer`.
- `fnic_fcoe_process_vlan_resp()`: parses VLAN notification descriptors and appends available VLANs to `fnic->vlan_list`.
- `fnic_fcoe_start_fcf_discovery()`: sends a discovery solicitation on the selected VLAN and starts FCF discovery timeout.
- `fnic_fcoe_fip_discovery_resp()`: handles solicited FCF advertisements during discovery and unsolicited advertisements as FCF keepalives after FLOGI starts/completes.
- `fnic_fcoe_start_flogi()`: sends FIP FLOGI to the selected FCF with an allocated FDLS OXID.
- `fnic_fcoe_process_flogi_resp()`: validates and processes FIP FLOGI responses, learns FPMA/FCID/timeouts, registers the port ID, and starts FDLS discovery.
- `fnic_common_fip_cleanup()`: cancels FIP timers, removes FPMA from vNIC filters, clears FCF/FCID/timeout state, and resets VLAN list.
- `fnic_fcoe_process_cvl()`: validates Clear Virtual Link, runs FDLS link down, and restarts VLAN discovery.
- `fdls_fip_recv_frame()`: demultiplexes Ethernet FIP frames by op/subcode.
- Timer/work handlers: `fnic_work_on_fip_timer()`, `fnic_handle_fip_timer()`, `fnic_handle_enode_ka_timer()`, `fnic_handle_vn_ka_timer()`, `fnic_vlan_discovery_timeout()`, `fnic_work_on_fcs_ka_timer()`, and `fnic_handle_fcs_ka_timer()`.

## Control Flow

FIP discovery starts with `fnic_fcoe_send_vlan_req()`. It broadcasts a FIP VLAN request, records the state, and waits for responses until `retry_fip_timer` fires. `fnic_fcoe_process_vlan_resp()` records VLAN IDs. On timeout, `fnic_vlan_discovery_timeout()` selects a VLAN, programs it through `fnic->set_vlan()`, marks it sent, and calls `fnic_fcoe_start_fcf_discovery()`.

FCF discovery sends a solicitation and waits for advertisements. `fnic_fcoe_fip_discovery_resp()` stores the available FCF with the best priority and its keepalive parameters. When discovery times out, `fnic_work_on_fip_timer()` either starts FIP FLOGI against the selected FCF or restarts VLAN discovery.

FIP FLOGI builds a FIP LS request containing an FC FLOGI frame, allocates a fabric OXID through FDLS, and arms the FLOGI timeout. `fnic_fcoe_process_flogi_resp()` validates descriptor lengths/types and FC header fields, frees the OXID, cancels the retry timer, and on LS_ACC learns FPMA, FCID, R_A_TOV, and E_D_TOV. It programs the FPMA into the vNIC, registers the port ID, transitions to `FDLS_FIP_FLOGI_COMPLETE` and `FNIC_IPORT_STATE_FABRIC_DISC`, calls `fnic_fdls_disc_start()`, and starts enode/VN keepalive timers when FKA is enabled.

After login, unsolicited FCF advertisements refresh `fcs_ka_timer` and can enable/disable keepalive timers if the FKA descriptor changes. Enode and VN-port keepalive timers send FIP control requests periodically. If no FCF keepalive is received, `fnic_work_on_fcs_ka_timer()` performs common cleanup, brings FDLS down, moves the iport back to FIP state, and restarts VLAN discovery. A CVL message follows a similar cleanup and rediscovery path after validating that it targets the selected FCF and local FPMA.

## State and Persistence Behavior

The file mutates `fnic->vlan_list`, `fnic->vlan_id` through the `set_vlan` callback, `iport->fip.state`, `iport->fip.flogi_retry`, `iport->selected_fcf`, `iport->fpma`, `iport->fcid`, `iport->r_a_tov`, `iport->e_d_tov`, `iport->fcfmac`, `iport->state`, and several timers. State is in-memory only and is reset on link down, CVL, FCS keepalive timeout, or explicit cleanup. VLAN list operations are protected by `vlans_lock`; some CVL and timeout paths coordinate with `fnic_lock` and reset completion state.

## Dependencies and Integration Points

`fip.c` depends on `fnic.h`, `fip.h`, Linux Ethernet helpers, FIP/FC definitions, mempool frame allocation from FDLS, FDLS OXID allocation/free, `fnic_send_fip_frame()`, `fnic_fdls_validate_and_get_frame_type()`, `fnic_fdls_register_portid()`, `fnic_fdls_disc_start()`, `fnic_fdls_link_down()`, and vNIC MAC filter programming through `vnic_dev_add_addr()`/`vnic_dev_del_addr()`.

## Risks and Edge Cases

- FIP timers share `fip_timer_work`; reinitializing work in multiple timer callbacks can be fragile if timers overlap.
- `FCOE_CTLR_MAX_SOL` is used as a solicitation-count threshold but is defined in milliseconds, so retry count semantics deserve scrutiny.
- VLAN response parsing advances by descriptor `fip_dlen` units and stops after adding one VLAN descriptor; multi-VLAN responses need validation.
- FLOGI response validation is strict on descriptor length and FC header fields; fabric variants can be dropped if assumptions are too narrow.
- CVL handling drops and reacquires `fnic_lock` while waiting for reset completion, so reset/link event ordering is a risk.
- Keepalive disable/enable changes require synchronizing FCF, enode, and VN timers to avoid stale cleanup after a valid advertisement.

## Test Signals

Useful tests include VLAN discovery with no VLANs, one VLAN, and multiple FCFs; FCF priority selection; FIP FLOGI accept and reject; FLOGI timeout/retry exhaustion; unsolicited FCF advertisements with changed FKA period/flags; enode/VN keepalive emission; FCS keepalive timeout; CVL for unrelated and local FPMA; link reset during CVL; MAC filter add/delete; and transition from FIP completion into FDLS target discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fip.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fip.h

## Purpose

`fip.h` defines FNIC-specific FIP constants, FIP discovery state enums, VLAN list entries, packed FIP wire-frame layouts, and prototypes for `fip.c`. It connects FIP protocol structures from the kernel FC stack with FNIC's FDLS/iport state.

## Important APIs, Types, and Definitions

- FIP constants: all-FCF MAC, maximum FCoE size, VLAN/FCF timeout values, maximum solicitation constant, and descriptor-list lengths for discovery, VLAN requests, keepalives, and FLOGI.
- `enum fdls_vlan_state`: per-VLAN availability vs sent state.
- `enum fdls_fip_state`: FIP progression from init, VLAN discovery, FCF discovery, FLOGI started, to FLOGI complete.
- `struct fcoe_vlan`: list entry containing VLAN ID, solicitation count, and state.
- Packed wire structures: `fip_vlan_req`, `fip_vlan_notif`, `fip_vn_port_ka`, `fip_enode_ka`, `fip_cvl`, `fip_flogi_desc`, `fip_flogi_rsp_desc`, `fip_flogi`, `fip_flogi_rsp`, `fip_discovery`, and `fip_disc_adv`.
- FIP function prototypes for VLAN, FCF discovery, FLOGI, CVL, timers, and the global `fnic_fip_queue`.
- `fnic_debug_dump_fip_frame()`: debug-only FIP frame dump wrapper; compiles to a no-op without `FNIC_DEBUG`.

## Control Flow and Design Role

The header models the frames that `fip.c` allocates and sends or receives. VLAN request and discovery structures include Ethernet headers because they are transmitted as complete Ethernet/FIP frames. Response/notification structures start at the FIP header because receive handlers pass a pointer after the Ethernet header. FLOGI structures embed `fc_std_flogi` from `fdls_fc.h`, allowing FIP LS messages to carry FC login payloads.

## State and Persistence Behavior

The header defines in-memory state shapes but does not mutate them. `struct fcoe_vlan` entries persist in `fnic->vlan_list` between VLAN discovery response handling and FCF discovery attempts. `enum fdls_fip_state` values persist in `iport->fip.state` and drive timeout behavior. Packed FIP structures represent transient wire frames.

## Dependencies and Integration Points

`fip.h` includes `fdls_fc.h`, `fnic_fdls.h`, and `<scsi/fc/fc_fip.h>`. It is used by `fip.c` and by FNIC initialization/teardown code that declares FIP work queues and timers. It bridges standard kernel FIP descriptor types with FNIC-specific FCoE discovery and FDLS startup.

## Risks and Edge Cases

- Descriptor-list length constants must match the packed structures and FIP `fip_dlen` units.
- Flexible arrays in VLAN notification and CVL structures require receive handlers to validate FIP descriptor lengths before indexing.
- `struct fip_flogi_rsp` assumes the response descriptor and MAC descriptor order used by FCFs.
- Debug dump code assumes an Ethernet header followed by a FIP header and must only be called with full FIP Ethernet frames.

## Test Signals

Useful validation includes compile-time structure size checks by observation, packet capture comparison for VLAN request, discovery solicitation, FIP FLOGI, enode keepalive, VN keepalive, CVL parsing, debug-frame logging when enabled, and state transitions through all `fdls_fip_state` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic.h

## Purpose

`fnic.h` is the central private header for the Cisco FNIC FCoE HBA driver. It defines driver identity, PCI IDs, SCSI command-private state, I/O and reset flags, logging macros, queue sizing, interrupt indexes, driver state enums, event structures, the main `struct fnic`, cross-file prototypes, SCSI iteration helpers, and debug dump helpers.

## Important APIs, Types, and Definitions

- Driver metadata: `DRV_NAME`, `DRV_DESCRIPTION`, `DRV_VERSION`, and logging prefixes.
- I/O tags and flags: special abort/device-reset tag bits, `FNIC_TAG_MASK`, and many `FNIC_IO_*`/`FNIC_DEV_RST_*` bits used by SCSI command state machines.
- `struct fnic_cmd_priv`, `fnic_priv()`, and `fnic_flags_and_state()`: per-SCSI-command private data and compact state/flag reporting.
- Reset and RSCN enums: reset progress, RSCN type, PCRSCN handling state, and feature flag.
- Logging macros: `FNIC_MAIN_DBG`, `FNIC_FCS_DBG`, `FNIC_FIP_DBG`, `FNIC_SCSI_DBG`, and `FNIC_ISR_DBG`, gated by `fnic_log_level`.
- Interrupt and driver state enums: INTx/MSI-X indexes and `enum fnic_state` for FC/Ethernet transition modes.
- `struct fnic_frame_list`, `struct fnic_event`, and `struct fnic_cpy_wq`: queued frame/event and copy-work-queue software state.
- `struct fnic`: per-adapter state for SCSI host, vNIC resources, interrupt resources, reset state, stats, link/FIP/FDLS state, workqueues, frame queues, target events, mempools, work/copy/receive/completion queues, and locks.
- Cross-file prototypes for interrupt setup, frame/link/event handlers, queue completion handlers, SCSI host callbacks, reset paths, debugfs/stats, FIP/FDLS operations, target handling, queue counting, unload cleanup, and debug info.
- `fnic_scsi_io_iter()`: wrapper around `scsi_host_busy_iter()` for applying a callback to outstanding SCSI commands.

## Control Flow and Design Role

This header defines the driver layering. `fnic_main.c` allocates and initializes `struct fnic`, vNIC queues, interrupts, mempools, timers, and the `iport`. ISR and CQ handlers use queue arrays and interrupt indexes from this header. `fnic_scsi.c` uses the command-private fields, tag flags, state flags, and SCSI prototypes. `fdls_disc.c` and `fip.c` use the embedded `iport`, frame queues, work items, timers, VLAN state, and logging macros. Sysfs/debugfs files expose fields declared here.

## State and Persistence Behavior

`struct fnic` is the primary per-device in-memory state object. It persists from PCI probe through remove and includes hardware resources, queue state, work items, timers, locks, FIP/FDLS state, SCSI host pointer, mempools, stats, and reset/removal flags. Command-private state persists for each outstanding SCSI command. `state_flags` is protected by the SCSI host lock, while many FDLS/FIP fields are protected by `fnic_lock`, `vlans_lock`, target-list locks, or queue-specific locks. No disk persistence is performed.

## Dependencies and Integration Points

`fnic.h` depends on Linux interrupt, netdevice, workqueue, bitops, SCSI command/transport, FC frame, vNIC resource/queue/interrupt/stats headers, FNIC I/O/stats/trace headers, and `fnic_fdls.h`. It is included by nearly every FNIC source file and is the main integration point between PCI/vNIC hardware, Linux SCSI transport, FDLS/FIP discovery, debugfs, sysfs, and reset handling.

## Risks and Edge Cases

- `struct fnic` is broad shared mutable state; wrong lock usage can affect SCSI I/O, discovery, reset, and remove paths.
- Command flags and states are bitmasks shared across abort/reset/completion paths; double completion or stale `io_req` pointers are major risks.
- Queue-count constants define array sizes for MSI-X, CQs, work queues, and receive queues. Mismatched hardware negotiation can overrun or underutilize queues.
- State transitions between FC mode and Ethernet/FIP mode must coordinate link events, FIP timers, firmware reset, and blocked I/O flags.
- Logging macros are compile-time safe but runtime-heavy if enabled at high volume in IRQ or completion paths.

## Test Signals

Useful signals include successful probe/remove, interrupt-mode selection, queue allocation and completion handling, SCSI command private state transitions, abort/device-reset/host-reset handling, firmware reset blocking/unblocking I/O, link up/down mode transitions, FIP/FDLS startup, debugfs/sysfs exposure, multi-queue mapping, outstanding I/O counting, and unload cleanup with active target ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_attrs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_attrs.c

## Purpose

`fnic_attrs.c` exposes a small sysfs attribute group for FNIC SCSI hosts. It provides read-only host attributes for the driver state, driver version, and link state.

## Important APIs, Types, and Functions

- `fnic_show_state()`: retrieves `struct fnic *` from the SCSI host private data and emits `fnic_state_str[fnic->state]`.
- `fnic_show_drv_version()`: emits `DRV_VERSION`.
- `fnic_show_link_state()`: reports `"Link Up"` unless `iport.state` is `FNIC_IPORT_STATE_INIT` or `FNIC_IPORT_STATE_LINK_WAIT`; otherwise reports `"Link Down"`.
- `DEVICE_ATTR(fnic_state)`, `DEVICE_ATTR(drv_version)`, and `DEVICE_ATTR(link_state)`: read-only attributes.
- `fnic_host_attrs`, `fnic_host_attr_group`, and exported `fnic_host_groups[]`: SCSI host attribute group consumed by the host template.

## Control Flow

When user space reads a sysfs file, the device attribute callback converts the device to `Scsi_Host` with `class_to_shost()`, obtains the FNIC pointer from `shost_priv()`, formats the requested value with `sysfs_emit()`, and returns the byte count. `fnic_host_groups[]` is referenced by the SCSI host template so the attributes are registered with each FNIC host.

## State and Persistence Behavior

The file maintains no independent state. It reads live `fnic->state`, `fnic->iport.state`, and the compile-time driver version. Attribute output reflects current in-memory state and is not persisted.

## Dependencies and Integration Points

The file depends on Linux device/sysfs APIs, SCSI host helpers, and `fnic.h`. It integrates with `fnic_main.c`, where the SCSI host template assigns `.shost_groups = fnic_host_groups`, and with the state strings and iport state maintained by the rest of the driver.

## Risks and Edge Cases

- `fnic_show_state()` indexes `fnic_state_str` with `fnic->state`; invalid state values would read outside the expected string table.
- The link-state heuristic treats all states except INIT and LINK_WAIT as up, so FIP discovery, fabric discovery, or transitional failure states may be displayed as up even when SCSI targets are not ready.
- The callbacks do not take locks, so reads can race with state changes. The values are simple scalar snapshots, but output can be transient during reset/remove.

## Test Signals

Useful validation includes checking `/sys/class/scsi_host/host*/fnic_state`, `drv_version`, and `link_state` after probe, link down, FIP discovery, ready state, reset, and remove/reprobe. Confirm `drv_version` matches `DRV_VERSION` and host attribute registration occurs for each FNIC SCSI host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_attrs.c -->
