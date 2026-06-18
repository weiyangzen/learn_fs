# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_lio.c

## Purpose
`efct_lio.c` binds EFCT Fibre Channel target IOs to Linux target core (LIO). It implements configfs fabric templates for physical and NPIV EFCT fabrics, creates/destroys target portal groups, handles initiator session setup/removal, translates FCP commands and TMFs into `se_cmd`/TMR submissions, maps target-core scatterlists to EFCT SGLs, drives read/write/status/TMF responses, and handles abort/free callbacks.

## Important APIs, Types, and Functions
Configuration helpers include WWN formatting/parsing, TPG enable attributes, NPIV enable handling, TPG attribute macros, and fabric operations tables `efct_lio_ops` and `efct_lio_npiv_ops`. Nport/TPG lifecycle is implemented by `efct_lio_make_nport`, `efct_lio_drop_nport`, `efct_lio_npiv_make_nport`, `efct_lio_npiv_drop_nport`, `efct_lio_make_tpg`, `efct_lio_drop_tpg`, `efct_lio_npiv_make_tpg`, and `efct_lio_npiv_drop_tpg`.

Session management is `efct_session_cb`, `efct_lio_setup_session`, `efct_scsi_new_initiator`, `efct_lio_remove_session`, and `efct_scsi_del_initiator`. Target device lifecycle is `efct_scsi_tgt_new_device`, `efct_scsi_tgt_del_device`, `efct_scsi_tgt_new_nport`, and `efct_scsi_tgt_del_nport`. IO datapath functions are `efct_scsi_recv_cmd`, `efct_scsi_recv_tmf`, `efct_lio_write_pending`, `efct_lio_queue_data_in`, `efct_lio_queue_status`, `efct_lio_queue_tm_rsp`, `efct_lio_datamove_done`, `efct_lio_send_resp`, and `efct_lio_status_done`.

## Control Flow
Driver init registers two target-core fabric templates: `efct` for the physical port and `efct_npiv` for NPIV. Configfs creates WWNs and TPGs; enabling a physical TPG brings the xport online, while enabling an NPIV TPG creates or requests a vport. When the EFC layer discovers an initiator, `efct_scsi_new_initiator` queues ordered work. The work selects a vport TPG if applicable, otherwise the physical TPG, calls `target_setup_session`, creates an `efct_node`, stores it in `efct->lookup` keyed by port FCID and initiator FCID, completes EFC registration, and adjusts IO watermarks.

Incoming FCP commands arrive from `efct_unsol.c` through `efct_scsi_recv_cmd`. This clears `tgt_io`, records state, increments `ios_in_use`, maps FCP task attributes and data direction to target-core values, initializes `se_cmd`, prepares submission with the CDB, and calls `target_submit`. Target core later calls fabric ops: writes use `write_pending` to DMA-map SGs and call `efct_scsi_recv_wr_data`; reads use `queue_data_in` to map and segment SGs and call `efct_scsi_send_rd_data`; status uses `queue_status`/`efct_lio_send_resp`; TMFs use `queue_tm_rsp` and `efct_scsi_send_tmf_resp`.

Completion flows unmap DMA SGs, continue segmented transfers if more SG entries remain, execute write commands after successful data-in from initiator, send final status for reads, or free the target command. Abort callbacks set `aborting`, call `efct_scsi_tgt_abort_io`, and rely on target-core release to complete IO object lifetime.

## State and Persistence Behavior
Configfs state creates in-kernel nport, vport, and TPG objects. There is no file-backed persistence here. `efct->tgt_efct` tracks max SGE/SGL, initiator count, IO high watermark, vport list, LIO nport, TPG, and counters. Sessions are serialized on a global ordered `lio_wq`. Active initiators are mapped through `efct->lookup` xarray. Each `efct_scsi_tgt_io` tracks target-core command state, DMA direction, TMF, SG map/count/current segment, error status, aborting flag, response-sent flag, and transferred length. The bitmask state in `tgt_io.state` is diagnostic and cumulative.

## Dependencies and Integration Points
The file integrates with Linux target core (`target_register_template`, `core_tpg_register`, `target_setup_session`, `target_init_cmd`, `target_submit`, `target_submit_tmr`, `transport_generic_free_cmd`, `target_execute_cmd`, session stop/wait/remove APIs), SCSI/FC helpers, EFCT xport, EFC node/session callbacks, fc_vport APIs, DMA SG mapping, atomics, workqueues, configfs, and xarray lookup.

## Risks
`lio_wq` is a single static workqueue shared by devices; teardown only flushes it and driver exit does not visibly destroy it here. Several error paths after `target_submit_prep` or `target_init_cmd` can leak `ios_in_use` or IO references if they return without target-core release. Segment handling must keep `seg_map_cnt`, `seg_cnt`, `cur_seg`, and `transferred_len` consistent or reads/writes can underrun, overrun, or double-unmap. NPIV creation and configfs teardown involve multiple ownership systems (`fc_vport`, vport list, TPG) and require strict ordering. `efct_lio_drop_nport` frees `efct->tgt_efct.lio_nport` rather than the container derived from `wwn`, so stale pointer assumptions matter. Watermark adjustments rely on balanced initiator add/remove callbacks.

## Test Signals
Test with configfs physical and NPIV fabric create/drop, TPG enable/disable with and without link/domain, initiator login/logout, session deletion while IOs are active, read/write/no-data commands, residual/sense responses, segmented SG transfers larger than `io->sgl_allocated`, TMF abort task and LUN reset, ABTS-driven aborts, target-core command failure paths, and DMA map/unmap fault injection. Counters to watch include `ios_in_use`, initiator count, watermarks, `rsp_sent`, and active IO list emptiness.
