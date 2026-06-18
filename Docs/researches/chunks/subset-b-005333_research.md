# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_init.c lines 9694-10284

## Scope And Purpose

This chunk covers late `qla_init.c` helper code for three driver surfaces:

- FCP command priority configuration application for logged-in Fibre Channel targets.
- Dynamic multi-queue `qla_qpair` creation and deletion for MQ/NVMe/vport paths.
- Vendor BSG management callbacks for statistics collection/reset and host-port disable/enable isolation.

The code is not a single init sequence despite living in `qla_init.c`; it provides exported helper functions used by discovery/login paths, sysfs and NPIV queue provisioning, NVMe-FC queue mapping, vport teardown, and vendor-specific BSG commands.

## Important APIs, Types, And Functions

- `qla24xx_get_fcp_prio()` scans `ha->fcp_prio_cfg` for a matching `struct qla_fcp_prio_entry` and returns an FCP priority tag or `-1`.
- `qla24xx_update_fcport_fcp_prio()` applies the priority to one target `fc_port_t`, using `qla24xx_set_fcp_prio()` mailbox command except on P3P hardware where it only updates `fcport->fcp_prio`.
- `qla24xx_update_all_fcp_prio()` iterates `vha->vp_fcports` and applies per-port FCP priority, typically after FCP priority configuration is enabled, disabled, or replaced through BSG.
- `qla2xxx_create_qpair()` allocates and starts a non-base request/response queue pair when firmware reports multi-queue support and MSI-X is enabled.
- `qla2xxx_delete_qpair()` tears down request/response queues, buffer pools, DSD DMA chain allocations, map/list membership, and the per-qpair SRB mempool.
- `qla2x00_count_set_bits()` and `qla2x00_get_num_tgts()` are utility helpers for sizing vendor statistics responses.
- `qla2xxx_reset_stats()`, `qla2xxx_start_stats()`, and `qla2xxx_stop_stats()` reset selected host and per-target counters. Start/stop are aliases for reset in this implementation.
- `qla2xxx_get_ini_stats()` fills a variable-length `struct ql_vnd_host_stats_resp`.
- `qla2xxx_get_tgt_stats()` fills a one-target `struct ql_vnd_tgt_stats_resp`.
- `qla2xxx_disable_port()` isolates the adapter port and cleans up the ISP/session state if online.
- `qla2xxx_enable_port()` clears isolation, marks the VHA online, requests `ISP_ABORT_NEEDED`, and wakes the DPC thread.

Key types and fields:

- `scsi_qla_host_t` / `struct scsi_qla_host`: per-host or per-vport driver state, including `vp_fcports`, `qp_list`, `dpc_flags`, `flags.online`, request queue pointers, and vendor stat counters.
- `struct qla_hw_data`: shared adapter state, including `fcp_prio_cfg`, `flags.fcp_prio_enabled`, `fw_attributes`, `msix_entries`, `queue_pair_map`, `qpair_qid_map`, `num_qpairs`, `mq_lock`, `base_qpair`, and target-session lock state.
- `fc_port_t`: remote port state used for priority matching, loop IDs, rport numbers, and per-target short-link-down counters.
- `struct qla_qpair`: queue-pair runtime object with lock, IDs, request/response queue pointers, MSI-X vector, SRB mempool, DSD list, buffer pool, FW-resource accounting, CPU mapping, and online/delete flags.
- Vendor BSG stats structures are declared in `qla_def.h`: `ql_vnd_mng_host_stats_param`, `ql_vnd_stats_param`, `ql_vnd_tgt_stats_param`, `ql_vnd_host_stats_resp`, `ql_vnd_tgt_stats_resp`, and flexible-array `ql_vnd_stats.entry[]`.

## FCP Priority Control Flow

`qla24xx_get_fcp_prio()` first requires both an in-memory priority config and `ha->flags.fcp_prio_enabled`. It then walks `ha->fcp_prio_cfg->entry[]`, skipping entries without `FCP_PRIO_ENTRY_VALID`. For each valid entry it separately counts PID matches and WWN matches:

- Source PID compares the config source PID with `vha->d_id.b24`; destination PID compares the config destination PID with `fcport->d_id.b24`.
- Source WWN compares `vha->port_name`; destination WWN compares `fcport->port_name`.
- `INVALID_PORT_ID` and all-ones WWN values act as wildcard matches.
- A priority is selected only when both source and destination PID match, or both source and destination WWN match. The returned priority is meaningful only if `FCP_PRIO_ENTRY_TAG_VALID` is set; otherwise the loop breaks and returns `-1`.

`qla24xx_update_fcport_fcp_prio()` rejects non-target ports and ports without a firmware loop ID. It then looks up a configured priority. P3P adapters only cache `priority & 0xf` in `fcport->fcp_prio`; 24xx/25xx adapters call `qla24xx_set_fcp_prio(vha, loop_id, priority, mb)`, which sends an `MBC_PORT_PARAMS` mailbox command and uses `ha->flags.fcp_prio_enabled` to choose enable/disable bits. On success the cached low nibble is updated and a user debug message is emitted when the value changed.

`qla24xx_update_all_fcp_prio()` is intentionally simple: it walks all `vp_fcports`, invokes the single-port updater, and returns the last updater return value. This means earlier failures or successes are overwritten by later ports. The function is called from FCP priority BSG configuration handling when priority state is toggled or replaced, and individual updates also occur in login/discovery paths.

## Queue-Pair Lifecycle Control Flow

`qla2xxx_create_qpair()` gates dynamic qpair creation on firmware multi-queue capability (`ha->fw_attributes & BIT_6`) and MSI-X enablement. It only allocates when `ql2xmqsupport` or `ql2xnvmeenable` is true. The creation sequence is:

1. Allocate and initialize `struct qla_qpair`, including lock, hardware/VHA links, shadow-register capability, list heads, copied base-qpair reset/class/confirmation flags, and `fw_started`.
2. Under `ha->mq_lock`, choose the first free qpair ID, ensure `ha->num_qpairs < ha->max_qpairs`, publish the qpair in `ha->queue_pair_map`, set the qid bitmap, increment `num_qpairs`, and select the first unused MSI-X vector.
3. Mark the MSI-X vector in use, link the qpair into `vha->qp_list`, copy `ha->pdev`, and set the 83xx-style IOCB start helper on 27xx/83xx/28xx hardware.
4. Create the firmware response queue first with `qla25xx_create_rsp_que()`, then the request queue with `qla25xx_create_req_que()`.
5. Wire `qpair->req`, `qpair->rsp`, `rsp->req`, and `rsp->qpair`; CPU-map the qpair if needed; enable DIF/DIX support when hardware and module parameters allow it.
6. Create a per-qpair SRB slab mempool and buffer pool.
7. Mark the qpair online and set `vha->flags.qpairs_available`.

Failure cleanup unwinds in reverse order: buffer pool, mempool, request queue, response queue, MSI-X/list state, map/bitmap/count state, and the qpair allocation. The map/list mutations happen before firmware queue creation, so all error labels must keep the partially published object coherent.

`qla2xxx_delete_qpair()` marks `delete_in_progress`, frees the qpair buffer pool, deletes request and response queues through firmware helpers, frees any DSD DMA chain objects from `qpair->dsd_list`, removes the qpair from `ha->queue_pair_map` and `vha->qp_list` under `ha->mq_lock`, clears bitmap/count state, resets `vha->flags.qpairs_available`, `qpairs_req_created`, and `qpairs_rsp_created` when no qpairs remain, destroys the SRB mempool, and frees the object. If request or response queue deletion fails, the function returns the failure without removing map/list state or destroying the qpair object.

Important integration callers include NVMe queue mapping (`qla_nvme.c`), vport QoS queue creation and vport deletion (`qla_attr.c`), and bulk queue deletion for a VHA (`qla_mid.c`). The qpair object also feeds target-mode qpair hints, IOCB allocation, interrupt routing, per-qpair buffer pooling, and firmware-resource accounting elsewhere in the driver.

## Vendor Statistics Control Flow

The statistics helpers implement the backend for vendor-specific BSG commands in `qla_bsg.c`.

`qla2xxx_reset_stats()` clears selected counters based on `QLA2XX_*` flag bits:

- Host counters: hardware errors, short link down, interface errors, command timeout, and reset command errors.
- Per-target short-link-down counters: protected by `vha->hw->tgt.sess_lock`, iterating `vha->vp_fcports` and resetting `fcport->tgt_short_link_down_cnt` and `fcport->tgt_link_down_time`.
- Host `vha->link_down_time` is always reset to `QLA2XX_MAX_LINK_DOWN_TIME`, even if no specific link-down flag was requested.

`qla2xxx_start_stats()` and `qla2xxx_stop_stats()` simply call reset; there is no persistent collection enable state in this chunk.

`qla2xxx_get_ini_stats()` computes a response entry count from requested flag bits. It treats `QLA2XX_TGT_SHT_LNK_DOWN`/`BIT_17` specially: the bit contributes one entry per target instead of one host entry. It fills host entries first, then target entries for target fcports with a valid `rport`, using `rport->number` as `tgt_num`. The BSG caller precomputes the same response size and allocates the flexible-array response buffer before calling this helper.

`qla2xxx_get_tgt_stats()` dereferences `rport->dd_data` to obtain the driver's `fc_port_t`, then writes one stat entry containing the requested `flags`, the remote-port number, and `fcport->tgt_short_link_down_cnt`.

## Port Disable/Enable Control Flow

`qla2xxx_disable_port()` sets `vha->hw->flags.port_isolated` before validating register accessibility. If `qla2x00_isp_reg_stat()` reports PCI/register disconnect, it marks EEH busy and returns `FAILED`. If the chip is already down, it returns success with isolation set. For an online host it calls `qla2x00_abort_isp_cleanup()` and waits for session deletion, effectively forcing the port offline from the driver and fabric-session perspective.

`qla2xxx_enable_port()` first checks register accessibility. On success it clears `port_isolated`, sets `vha->flags.online = 1` so abort processing can run, sets `ISP_ABORT_NEEDED`, and wakes the driver DPC via `qla2xxx_wake_dpc()`. Actual hardware recovery and relogin are therefore deferred to the normal DPC/ISP abort path.

These functions are reached from `qla2x00_manage_host_port()` in the BSG vendor-management path, where userspace sends a `QLA_ENABLE` or `QLA_DISABLE` action and receives a packed status response.

## State And Persistence Behavior

The persistent state here is in-memory driver and firmware state rather than on-disk data.

- FCP priority state persists in `ha->fcp_prio_cfg`, `ha->flags.fcp_prio_enabled`, and each `fcport->fcp_prio`. Configuration can originate from flash (`qla24xx_read_fcp_prio_cfg()`) or from BSG-provided replacement data. Firmware-visible priority is updated through mailbox commands for supported adapters.
- Qpair creation persists shared object pointers in `ha->queue_pair_map`, bitmaps in `ha->qpair_qid_map`, list membership in `vha->qp_list`, MSI-X vector `in_use` state, firmware request/response queues, mempools, buffer pools, and queue-to-CPU mappings. Deletion must remove all of these to avoid stale queue routing or leaked DMA/memory resources.
- Statistics counters live on `scsi_qla_host_t` and `fc_port_t`. The start/stop/clear BSG operations reset counters rather than enabling a separate sampling state.
- Port isolation persists in `ha->flags.port_isolated` and is coupled to `vha->flags.online`, DPC flags, session teardown, and later ISP recovery.

## Dependencies And Integration Points

- Kernel FC transport and SCSI host APIs: `struct Scsi_Host`, `shost_priv()`, `struct fc_rport`, `fc_bsg` vendor jobs, and remote-port `dd_data`.
- Kernel synchronization and allocation primitives: spin locks with IRQ save, mutexes, linked lists, bitmaps, mempools, DMA pools, work/DPC flags, `raw_smp_processor_id()`, and PCI/MSI-X state.
- qla2xxx mailbox and queue helpers: `qla24xx_set_fcp_prio()`, `qla25xx_create_rsp_que()`, `qla25xx_create_req_que()`, `qla25xx_delete_req_que()`, `qla25xx_delete_rsp_que()`, `qla_create_buf_pool()`, `qla_free_buf_pool()`, and `qla_cpu_update()`.
- Module parameters and capability macros: `ql2xmqsupport`, `ql2xnvmeenable`, `ql2xenabledif`, `IS_P3P_TYPE`, `IS_T10_PI_CAPABLE`, `IS_SHADOW_REG_CAPABLE`, `IS_QLA27XX`, `IS_QLA83XX`, and `IS_QLA28XX`.
- User-facing integration: sysfs/vport queue QoS paths in `qla_attr.c`, NVMe-FC queue allocation in `qla_nvme.c`, BSG vendor management in `qla_bsg.c`, target-mode qpair hinting in `qla_target.c`, and discovery/login flows that apply FCP priority after target login.

## Risks And Edge Cases

- `qla24xx_update_all_fcp_prio()` returns only the last per-port result, so partial failures are not visible to its caller unless debug logs are inspected.
- FCP priority matching ignores LUN begin/end fields even though flags exist in the firmware config format; this chunk only matches PID-pair or WWN-pair selectors.
- `qla24xx_get_fcp_prio()` trusts `ha->fcp_prio_cfg->num_entries`; corruption or insufficient validation before storing config would affect iteration bounds.
- Qpair ID selection calls `find_first_zero_bit()` before checking `num_qpairs >= max_qpairs`. The subsequent capacity check prevents normal over-allocation, but correctness still depends on bitmap/count consistency under `ha->mq_lock`.
- The qpair is published in `queue_pair_map` and `vha->qp_list` before request/response queues and mempools are fully created. Any concurrent path observing those structures must tolerate partially initialized qpairs or be excluded by higher-level sequencing.
- `qla2xxx_delete_qpair()` leaves the qpair object and map/list membership intact when firmware queue deletion fails. That avoids freeing active firmware resources, but callers must handle a qpair that is marked `delete_in_progress` and partly torn down, including an already freed buffer pool.
- `qla2xxx_reset_stats()` resets `vha->link_down_time` regardless of requested flags, which can surprise callers requesting unrelated stat resets.
- `qla2xxx_get_ini_stats()` receives a `size` argument but does not validate it locally; it relies on BSG caller-side response sizing. Other future callers must preserve that contract.
- `qla2xxx_get_tgt_stats()` assumes `rport->dd_data` points to a valid `fc_port_t *`. The BSG lookup path must avoid stale or NULL rports.
- `qla2xxx_disable_port()` sets `port_isolated` before PCI/register validation. If the register check fails, the function returns `FAILED` with software isolation already set.
- BSG target-stat request validation in the nearby caller compares payload length to `sizeof(struct ql_vnd_stat_entry)` rather than `sizeof(struct ql_vnd_tgt_stats_param)`, which is a compatibility or validation risk adjacent to these helpers.

## Test Signals

Useful validation signals for this chunk include:

- FCP priority tests with enabled/disabled config, invalid entries, wildcard PIDs/WWNs, source/destination PID pair matches, WWN pair matches, no tag-valid flag, non-target ports, `FC_NO_LOOP_ID`, P3P hardware, and mailbox failure injection.
- BSG FCP priority config flows that replace config, toggle enable/disable, and verify that all logged-in target ports receive expected cached and firmware priority values.
- Qpair creation tests for missing firmware multi-queue support, MSI-X disabled, full qpair map, no free MSI-X vectors, response queue creation failure, request queue creation failure, SRB mempool failure, buffer-pool failure, and successful DIF/DIX enablement.
- Qpair deletion tests that verify request/response queue deletion ordering, DSD DMA list cleanup, mempool destruction, `queue_pair_map`/bitmap/count/list state, MSI-X reuse behavior after failed creation, and VHA flags when the final qpair is deleted.
- NVMe/vport integration tests that allocate a qpair through `qla_nvme.c` and `qla_attr.c`, then release it through vport deletion or `qla25xx_delete_queues()`.
- Vendor stats BSG tests for response sizing, buffer-too-small behavior, each `QLA2XX_*` flag, combined host and per-target flags, no-rport target skipping, reset/start/stop aliases, and lock-safe target counter reset.
- Port management BSG tests for enable and disable actions, invalid action handling, PCI/register disconnect handling, already-down chip behavior, online-session cleanup, DPC wakeup on enable, and persistence of `port_isolated`.
