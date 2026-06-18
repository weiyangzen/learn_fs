# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_gs.c

## Purpose

`qla_gs.c` implements Fibre Channel Generic Services support for the QLogic `qla2xxx` driver. It builds and submits Common Transport (CT), Simple Name Server (SNS), Fabric Device Management Interface (FDMI), and Fabric Management (FM) requests used during adapter registration, fabric discovery, port capability lookup, and asynchronous session reconciliation.

The file has three major roles:

- Name-server discovery: query the fabric for port IDs, port WWNs, node WWNs, fabric port names, FC-4 feature bits, and GA_NXT fallback enumeration.
- Fabric registration: register the local adapter/virtual port with SNS and FDMI using RFT_ID, RFF_ID, RNN_ID, RSNN_NN, RHBA, RPRT, RPA, and related commands.
- Asynchronous fabric scan and per-port lookups: drive GPN_FT/GNN_FT scan sequencing for FCP and NVMe, reconcile results into `fc_port_t` sessions, and schedule follow-on GFPN_ID/GPSC/IIDMA work.

## Important APIs, Types, and Functions

The exported API surface is declared in `qla_gbl.h` and is consumed by loop initialization, workqueue dispatch, EDIF, target, and OS setup code:

- IOCB/CT preparation: `qla2x00_prep_ms_iocb()`, `qla24xx_prep_ms_iocb()`, `qla2x00_chk_ms_status()`.
- Synchronous discovery helpers: `qla2x00_ga_nxt()`, `qla2x00_gid_pt()`, `qla2x00_gpn_id()`, `qla2x00_gnn_id()`, `qla2x00_gfpn_id()`, `qla2x00_gff_id()`.
- SNS registration: `qla2x00_rft_id()`, `qla2x00_rff_id()`, `qla2x00_rnn_id()`, `qla2x00_rsnn_nn()`.
- FDMI registration: `qla2x00_fdmi_register()`.
- Async per-port fabric queries: `qla24xx_post_gpsc_work()`, `qla24xx_async_gpsc()`, `qla24xx_async_gffid()`, `qla24xx_post_gfpnid_work()`, `qla24xx_async_gfpnid()`.
- Async scan engine: `qla_fab_scan_start()`, `qla_fab_async_scan()`, `qla_fab_scan_finish()`, `qla_scan_work_fn()`.

Key local helpers include `qla2x00_prep_ct_req()` for SNS CT headers, `qla2x00_prep_sns_cmd()` for legacy mailbox SNS commands, `qla2x00_prep_ct_fdmi_req()` for FDMI CT headers, `qla24xx_prep_ct_fm_req()` for Fabric Management CT headers, FDMI attribute builders `qla2x00_hba_attributes()` and `qla2x00_port_attributes()`, and async completion handlers such as `qla2x00_async_sns_sp_done()`, `qla24xx_async_gpsc_sp_done()`, `qla24xx_async_gffid_sp_done()`, `qla_async_scan_sp_done()`, and `qla2x00_async_gfpnid_sp_done()`.

Important data structures are defined mainly in `qla_def.h`:

- `struct ct_arg` carries IOCB buffer, request/response DMA addresses, sizes, nport handle, and optional allocated CT buffers for `SRB_CT_PTHRU_CMD`.
- `struct ct_sns_pkt`, `struct ct_sns_req`, and `struct ct_sns_rsp` model CT request/response payloads for SNS, FDMI, FM, and feature/speed responses.
- `fc_port_t` stores remote-port identity and discovery state: WWNs, `d_id`, `loop_id`, fabric port name, fabric-port speed, `fc4_type`, `fc4_features`, `scan_state`, login/RSCN generations, flags, and discovery/login state.
- `struct fab_scan` and `struct fab_scan_rp` hold the asynchronous fabric scan list, scan step, RSCN generation bounds, retry count, scan flags, and delayed rescan work.
- `srb_t` plus `struct srb_iocb.ctarg` is the async command carrier; completions release its kref or post follow-on work.
- `struct qla_work_evt` carries queued events such as `QLA_EVT_GPSC`, `QLA_EVT_GFPNID`, `QLA_EVT_SCAN_CMD`, `QLA_EVT_SCAN_FINISH`, `QLA_EVT_SP_RETRY`, and `QLA_EVT_UNMAP`.

## Control Flow

For newer adapters, most SNS commands use the same pattern: fill `struct ct_arg`, call `ha->isp_ops->prep_ms_iocb()`, initialize a CT request with `qla2x00_prep_ct_req()`, fill the command-specific payload, issue `qla2x00_issue_iocb()`, and validate both firmware completion and CT accept status with `qla2x00_chk_ms_status()`. `qla2x00_ga_nxt()`, `qla2x00_gid_pt()`, `qla2x00_gpn_id()`, `qla2x00_gnn_id()`, `qla2x00_gfpn_id()`, and `qla2x00_gff_id()` then copy response fields into `fc_port_t` or `sw_info_t` state.

For ISP2100/ISP2200 hardware, the public discovery and registration entry points fall back to legacy mailbox SNS helpers (`qla2x00_sns_ga_nxt()`, `qla2x00_sns_gid_pt()`, `qla2x00_sns_gpn_id()`, `qla2x00_sns_gnn_id()`, `qla2x00_sns_rft_id()`, `qla2x00_sns_rnn_id()`). These use `ha->sns_cmd`, `ha->sns_cmd_dma`, and `qla2x00_send_sns()` rather than CT IOCBs and parse fixed response offsets.

SNS registration for modern adapters is asynchronous. `qla_async_rftid()`, `qla_async_rffid()`, `qla_async_rnnid()`, and `qla_async_rsnn_nn()` allocate request and response CT packets with `dma_alloc_coherent()`, initialize an `SRB_CT_PTHRU_CMD`, submit it with `qla2x00_start_sp()`, and rely on `qla2x00_async_sns_sp_done()` to retry up to three failures, queue unmap work, or free DMA buffers directly if work allocation fails.

FDMI registration starts in `qla2x00_fdmi_register()`. It skips unsupported 2100/2200/FX adapters, logs in to the management server via `qla2x00_mgmt_svr_login()`, and then chooses the registration sequence. NPIV vports send only RPRT, trying Smart SAN/FDMI2/FDMI1 variants. Physical ports try RHBA with FDMI2, delete/retry on already-registered HBA, then register port attributes with RPA, falling back to FDMI1 if needed. RHBA, RPRT, and RPA use dynamic request sizing: prepare an FDMI IOCB with request size zero, append attributes, then update the IOCB byte count with `qla2x00_update_ms_fdmi_iocb()`.

The asynchronous fabric scan is a staged state machine. `qla_fab_scan_start()` starts `qla_fab_async_scan(vha, NULL)`. The first call allocates one CT request buffer and a response buffer sized for `max_fibre_devices`, clears `vha->scan.l`, and starts `FAB_SCAN_GPNFT_FCP`. Completion runs `qla_async_scan_sp_done()`, which parses the response into the scan list with `qla2x00_find_free_fcp_nvme_slot()`, clears `SF_SCANNING`, and posts `QLA_EVT_SCAN_CMD` or `QLA_EVT_SCAN_FINISH`. The sequence is GPN_FT FCP, GNN_FT FCP, optionally GPN_FT NVMe, and GNN_FT NVMe. `qla_fab_scan_finish()` then reconciles the accumulated list against `vha->vp_fcports`, suppresses self and same-host virtual ports, detects duplicate NPORT IDs, creates new sessions with `qla24xx_post_newsess_work()`, relogs changed/found ports, schedules lost sessions for deletion, and requeues loop resync if scan-needed ports remain.

GFPN_ID and GPSC form a follow-on chain for per-port fabric-port-name and speed discovery. `qla24xx_post_gfpnid_work()` queues `QLA_EVT_GFPNID`; `qla24xx_async_gfpnid()` sends GFPN_ID using the port CT descriptor; its completion stores `fabric_port_name` and calls `qla24xx_handle_gfpnid_event()`, which validates login/RSCN generations and posts GPSC. `qla24xx_async_gpsc()` queries fabric-management speed by fabric port name; its completion maps the returned speed bits to driver `PORT_SPEED_*` values and schedules IIDMA work when generations still match.

## State and Persistence Behavior

This file does not persist data to disk. Its persistence is in kernel driver state, firmware-visible fabric registrations, and switch name-server/FDMI database records.

Local adapter state updated by this file includes `vha->qla_stats.control_requests`, `vha->flags.management_server_logged_in`, `ha->flags.gpsc_supported`, `fc_port_t.fabric_port_name`, `fc_port_t.fp_speed`, `fc_port_t.fc4_type`, `fc_port_t.fc4_features`, `fc_port_t.scan_state`, `fc_port_t.scan_needed`, `fc_port_t.last_rscn_gen`, `fc_port_t.d_id`, `fc_port_t.flags`, `fc_port_t.logout_on_delete`, and the fabric scan fields under `vha->scan`. Loop recovery bits such as `LOOP_RESYNC_NEEDED` and `LOCAL_LOOP_UPDATE` are set when SNS login drops, scan retries are required, or delayed scan recovery is needed.

Remote switch state is changed by registration commands. RFT_ID/RFF_ID/RNN_ID/RSNN_NN advertise local FC-4 types/features, node name, and symbolic node name to the name server. FDMI RHBA/RPRT/RPA/DHBA commands register or remove HBA and port attributes in the management server database. These remote registrations can survive locally until fabric events or explicit de-registration paths elsewhere cause refresh or deletion; this file mostly handles registration and retry/fallback behavior.

Memory lifecycle is mixed. Synchronous paths reuse shared `ha->ms_iocb`, `ha->ct_sns`, and `ha->sns_cmd` buffers owned by the adapter context. Async registration and some GFF_ID paths allocate DMA-coherent CT buffers per `srb_t` and free them in completion/unmap/error paths. GPSC and GFPN_ID reuse per-`fc_port_t` `ct_desc.ct_sns` buffers and therefore do not free those buffers in their local completion paths.

Concurrency state is guarded by `vha->work_lock` for scan flags and by `ha->vport_slock` for vport list traversal. Async callbacks use generation checks (`login_gen`, `rscn_gen`, chip reset generation) to avoid applying stale fabric query results after target-side changes, RSCNs, or chip reset.

## Dependencies and Integration Points

The file depends on adapter operation hooks in `ha->isp_ops`, especially `prep_ms_iocb`, `prep_ms_fdmi_iocb`, `fabric_login`, and `fw_version_str`. It also depends on lower-level submission helpers such as `qla2x00_issue_iocb()`, `qla2x00_start_sp()`, `qla2x00_send_sns()`, `qla2x00_get_sp()`, `qla2x00_init_async_sp()`, `qla2x00_post_work()`, `qla2x00_alloc_work()`, and `qla24xx_sp_unmap()`.

Discovery integration is primarily in `qla_init.c`: adapter initialization calls FDMI/SNS registrations, starts fabric scans for newer paths, and uses the synchronous GID_PT/GPN_ID/GNN_ID/GFPN_ID/GFF_ID or GA_NXT flow for other discovery paths. `qla_os.c` initializes `vha->scan.scan_work` and dispatches queued events to `qla24xx_async_gpsc()`, `qla_fab_async_scan()`, `qla_fab_scan_finish()`, and `qla24xx_async_gfpnid()`. `qla_target.c` can post GPSC work for target-side session handling, and `qla_edif.c` uses `qla24xx_async_gffid()` to refresh FC-4 feature information for encrypted fabric flows.

Protocol constants, request/response layouts, FDMI attribute definitions, fabric scan structures, and port/session state are supplied by `qla_def.h`. Logging and debug paths use the qla debug/logging infrastructure (`ql_dbg`, `ql_log`, `ql_dump_buffer`). Kernel services include DMA-coherent allocation/freeing, completions, spin locks, delayed work, bit operations, `utsname()`, PCI IDs, and libfc host attributes.

## Risks and Edge Cases

- Shared synchronous buffers (`ha->ms_iocb`, `ha->ct_sns`, `ha->sns_cmd`) assume serialized use by the discovery/control path. New concurrent callers would need explicit exclusion or separate buffers.
- Many request sizes are hand-computed from protocol struct sizes and appended FDMI attribute lengths. Mistakes in alignment or `alen` reuse can produce malformed FDMI requests or expose stale bytes in CT payloads.
- Async DMA ownership differs by path. Registration and synchronous-wait GFF_ID allocate/free private buffers, while GPSC/GFPN_ID use per-port buffers. Mixing those ownership models can cause leaks, double frees, or use-after-free bugs.
- `qla2x00_async_sns_sp_done()` retries failed async SNS registrations by reposting the same `srb_t`; if work allocation fails it must free DMA memory directly to avoid leaks. This makes its error path sensitive to future changes in `ctarg` allocation.
- Fabric scan results are bounded by `ha->max_fibre_devices`. If the switch reports more devices than fit, synchronous GID_PT returns failure so GA_NXT can be used, while the async GPN_FT scan allocates a response sized to the same maximum and may not represent excess devices.
- Stale event protection relies on generation fields. A missing generation update elsewhere could let old GFPN_ID/GPSC or scan results alter a port after RSCN, login, or reset changes.
- `qla_fab_scan_finish()` mutates session state, schedules deletes, and posts new sessions based on switch data. Errors in duplicate handling, self/vport filtering, or RSCN clearing could cause unnecessary logout/login churn.
- GPSC unsupported responses disable future GPSC queries through `ha->flags.gpsc_supported`; this is appropriate for fabrics that reject the command but may hide recovery if fabric behavior changes without a full driver refresh.
- FDMI fallback logic treats `QLA_ALREADY_REGISTERED` specially by issuing DHBA and retrying. Switches with partial or inconsistent FDMI databases are likely to stress this path.

## Test Signals

Useful validation signals for this file are mostly integration and hardware/fabric oriented:

- Fabric login/initialization should show successful RFT_ID, RFF_ID for FCP and optional NVMe, RNN_ID, RSNN_NN, and FDMI registration without loop-resync storms.
- Discovery against a fabric with FCP-only, NVMe-only, and dual FC-4 targets should populate `fc4_type`, `fc4_features`, WWPN, node WWN, `d_id`, fabric port name, and speed correctly.
- A switch with more devices than `max_fibre_devices` should drive the intended GID_PT failure/GA_NXT fallback path rather than overflowing response parsing.
- RSCN and rapid login/reset tests should confirm stale async completions are ignored when `login_gen`, `rscn_gen`, or chip reset generation no longer match.
- NPIV tests should verify same-host virtual ports are filtered from scan results and that vports use RPRT-only FDMI registration.
- FDMI interoperability tests should cover FDMI2, Smart SAN, already-registered responses, DHBA retry, and FDMI1 fallback.
- Fault injection for DMA allocation failure, work allocation failure, IOCB timeout, CT reject, `CS_PORT_LOGGED_OUT`, and unsupported GPSC/GFF_ID should verify cleanup, retry, and resync behavior.
- Kernel leak and lifetime tooling should show balanced `dma_alloc_coherent()`/`dma_free_coherent()` and `srb_t` kref release on success, retry exhaustion, timeout, and synchronous wait paths.
