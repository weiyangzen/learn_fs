# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_bsg.c

## Purpose
`qla_bsg.c` implements the qla2xxx Fibre Channel BSG request path. It handles standard ELS and CT passthrough plus a broad vendor-specific ABI for loopback diagnostics, flash access, 84xx management, FCP priority, IIDMA, FRU/I2C/SFP operations, bidirectional diagnostic I/O, FX00 management IOCBs, SERDES access, flash update capabilities, BBCR data, private statistics, D_Port diagnostics, EDIF management, host/tgt stats, host-port management, mailbox passthrough, timeout handling, and QLA28xx image validation.

## Important APIs and Functions
- Common completion/freeing:
  - `qla2x00_bsg_job_done()` writes the BSG result, completes the `bsg_job`, releases the SRB kref, and completes optional waiters.
  - `qla2x00_bsg_sp_free()` unmaps request/reply DMA or frees remap pool buffers, schedules dummy `fcport` freeing for CT/ELS/FX IOCBs, and releases the SRB.
- ELS/CT passthrough:
  - `qla2x00_process_els()` handles `FC_BSG_RPT_ELS` and `FC_BSG_HST_ELS_NOLOGIN`, including EDIF auth ELS dispatch, dummy fcport allocation for host ELS, DMA mapping, SRB setup, and `qla2x00_start_sp()`.
  - `qla2x00_process_ct()` handles host CT requests to SNS or management server loop IDs, allocates a dummy fcport, calculates IOCB count with `qla24xx_calc_ct_iocbs()`, and starts an SRB.
- Vendor command handlers include `qla2x00_process_loopback()`, `qla84xx_reset()`, `qla84xx_updatefw()`, `qla84xx_mgmt_cmd()`, `qla24xx_iidma()`, `qla24xx_proc_fcp_prio_cfg_cmd()`, `qla2x00_read_optrom()`, `qla2x00_update_optrom()`, FRU/I2C helpers, `qla24xx_process_bidir_cmd()`, `qlafx00_mgmt_cmd()`, SERDES handlers, flash capability handlers, BBCR/stats/D_Port handlers, host/tgt stats handlers, host-port management, and mailbox passthrough.
- Dispatch:
  - `qla2x00_process_vendor_specific()` switches on `vendor_cmd[0]`.
  - `qla24xx_bsg_request()` is the FC transport entry point and switches on BSG message code.
  - `qla24xx_bsg_timeout()` searches outstanding BSG SRBs and aborts timed-out jobs.

## Control Flow
- `qla24xx_bsg_request()` initializes reply length, resolves `vha` from rport or host, rejects isolated/down/removing adapters except selected host management/stat commands, then dispatches ELS, CT, or vendor requests.
- Asynchronous ELS/CT/FX/bidirectional requests allocate an SRB, set `sp->u.bsg_job`, `sp->free`, and `sp->done`, then rely on firmware interrupt completion to call `qla2x00_bsg_job_done()`.
- Synchronous vendor commands generally copy request SG payloads into kernel or DMA buffers, issue mailbox/IOCB/helper operations, copy response data back to reply SG payloads, set vendor status in `vendor_rsp[0]`, and call `bsg_job_done()`.
- Loopback processing maps request/reply SGs, allocates coherent request/reply buffers, chooses echo versus loopback based on topology/options/payload, manipulates 81xx/8031/8044 loopback port configuration when needed, runs mailbox diagnostics, restores port config, and returns mailbox response plus command-sent type in the BSG reply area.
- Flash read/update uses `qla2x00_optrom_setup()` under `ha->optrom_mutex` to validate region and state, allocate `ha->optrom_buffer`, perform read/write through `ha->isp_ops`, copy SG data, free the buffer, and reset state.
- Bidirectional diagnostic I/O validates adapter capability, reset state, online state, cable/topology/P2P mode, performs self-login under `selflogin_lock` when needed, maps SGs, validates equal request/reply lengths, allocates an SRB, and starts a bidirectional IOCB.
- Timeout handling logs the timed-out job, detects PCI/register disconnect, searches base and additional qpairs for matching BSG SRBs, attempts firmware abort, waits up to a R_A_TOV-derived timeout, and if needed detaches the outstanding command and completes the BSG with `-ENXIO`.
- QLA28xx image validation checks adapter and physical function, locks `optrom_mutex`, verifies MPI firmware state bits, takes the FAC semaphore, calls `qla_mpipt_validate_fw()`, releases the semaphore, and reports image/config validation vendor status.

## State and Persistence
- Persistent operations include flash/option ROM update, FRU version/status writes, I2C/SFP writes, 84xx firmware update, flash image validation, and mailbox passthrough that may alter firmware state.
- Runtime state includes SRBs in outstanding queues, DMA mappings, dummy `fcport` structures, `ha->optrom_state` and buffer fields, FCP priority config (`ha->fcp_prio_cfg`, `fcp_prio_enabled`), self-login loop ID, D_Port diagnostic status/data, stats counters, and host-port enable/disable state.
- Vendor command results are often encoded in `bsg_reply->reply_data.vendor_reply.vendor_rsp[0]` using `EXT_STATUS_*`, while transport result is frequently `DID_OK << 16` even for vendor-level failures.

## Dependencies and Integration Points
- Integrates with Linux BSG (`struct bsg_job`, `bsg_job_done()`), FC BSG request/reply formats, SCSI host/rport lookup, scatter-gather DMA mapping, DMA pools/coherent buffers, mempools, workqueues, completions, mutexes, and qpair locking.
- Calls qla mailbox/firmware helpers from the wider driver: ELS/CT IOCB start, loopback/echo tests, 84xx access chip/verify chip IOCBs, NVRAM/flash ops, SFP/I2C ops, D_Port diagnostics, stats helpers, port enable/disable, EDIF app management, mailbox passthrough, and MPI flash validation.
- Tied to FC transport through `qla2xxx_transport_functions` and `qla2xxx_transport_vport_functions` in `qla_attr.c`.
- ABI definitions are shared with `qla_bsg.h` and `qla_edif_bsg.h`.

## Risks and Edge Cases
- BSG is a privileged low-level ABI; malformed payload sizes, SG counts, or vendor structs can lead to incorrect hardware operations if not validated.
- Many handlers assume exact payload struct sizes but some copy fixed `DMA_POOL_SIZE` or struct sizes from SG without checking the job payload length first. This is a review hotspot for short-buffer behavior.
- DMA mapping paths must unmap only what was mapped. The ELS/CT and FX paths have several failure labels where request and reply mapping state matters.
- Some handlers return `0` while reporting vendor-level failure in `vendor_rsp[0]`; user-space must inspect both transport and vendor status.
- Timeout handling races with firmware completion; it rechecks the outstanding slot under lock before detaching, but SRB lifetime depends on krefs and completion ordering.
- Flash and mailbox passthrough commands can alter persistent adapter state, require adapter-family checks, and may conflict with concurrent sysfs flash paths through shared `optrom_state`.
- `qla2xxx_find_rport()` dereferences `fcport->rport` while iterating; missing rport guards would be risky if list entries without rports are possible.
- QLA28xx validation returns `QLA_SUCCESS` even after setting vendor error status, so callers must rely on vendor status.

## Test Signals
- BSG ABI tests for each supported message code and vendor command, including unsupported adapter families and isolated/down/removing adapter states.
- SG mapping tests with zero SGs, multiple SGs where forbidden, short request/reply payloads, oversized flash regions, and DMA mapping failures.
- ELS and CT passthrough tests for rport and host no-login modes, including EDIF auth ELS dispatch.
- Loopback/echo diagnostics on supported topologies with forced DCBX timeout, loopback already active, mailbox reset errors, and port config restore failure.
- Flash read/update tests sharing state with sysfs optrom, including invalid region, PCI offline, allocation failure, and write failure.
- Timeout tests where firmware completes before abort, abort succeeds after delay, abort fails, and PCI EEH is active.
- Stats and host/tgt management tests checking both transport result and `EXT_STATUS_*` vendor response values.
