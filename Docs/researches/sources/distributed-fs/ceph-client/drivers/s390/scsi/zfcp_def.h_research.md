# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_def.h`

## Purpose

`zfcp_def.h` is the central data-model header for the zfcp driver. It defines shared status bits, ERP action types and steps, adapter/port/LUN state containers, latency accounting structures, and the base `struct zfcp_fsf_req` request object used to send commands to the FCP adapter. Most zfcp modules include it directly or indirectly, making it the primary contract between CCW/QDIO transport, FSF command handling, FC discovery, SCSI integration, diagnostics, sysfs, and ERP.

## Important APIs, Types, And Data

- Common status bits (`ZFCP_STATUS_COMMON_RUNNING`, `ERP_FAILED`, `UNBLOCKED`, `OPEN`, `ERP_INUSE`, `ACCESS_DENIED`, `ACCESS_BOXED`, `NOESC`) occupy the high 12 bits and are shared by adapter, port, and LUN-like objects.
- Adapter-only status bits track QDIO state, SIOSL logging, exchange-config success, host-connection initialization, pending ERP, link unplugged, and data-div support.
- Port-only status bits track physical-open state and active ADISC link tests.
- FSF-request status bits track request errors, cleanup ownership, abort outcome, task-management failure, dismissed requests, and incomplete exchange data.
- `enum zfcp_erp_act_type` defines LUN, port, forced-port, and adapter reopen actions. Values must fit into `u8` for debug record storage.
- `enum zfcp_erp_steps` records active ERP substeps: physical port closing, port closing/opening, and LUN closing/opening.
- `struct zfcp_erp_action` stores the queued/running recovery action, target object pointers, action status, current step, FSF request id, and timeout timer.
- `struct zfcp_adapter_mempool` groups mempools for ERP, GID_PN, SCSI, abort, status-read, status-read data pages, QTCBs, and FC requests.
- `struct zfcp_adapter` is the driver root object. It contains CCW/QDIO pointers, hardware feature data, SCSI host, port list and lock, request ids and request list, abort lock, status-read state, ERP queues/thread/wait queues, FC generic service ports, debug feature state, mempools, statistics buffers, work items, service level, event queue, scan throttling, diagnostics, and version-change work.
- `struct zfcp_port` represents a remote FC port and stores the device object, FC transport rport, adapter pointer, unit list, status, WWNN/WWPN/D_ID/handle, ERP action, capability/security fields, GID_PN/ADISC/rport work, and target id.
- `struct zfcp_unit` is the sysfs-configured LUN object; runtime I/O state lives in `struct zfcp_scsi_dev`.
- `struct zfcp_scsi_dev` is SCSI transport-private LUN state: status, FSF LUN handle, ERP action/counter, latency counters, and owning port.
- `sdev_to_zfcp()` returns the SCSI transport private zfcp LUN state.
- `zfcp_scsi_dev_lun()` converts a Linux SCSI LUN into the 64-bit FCP LUN encoding used in FSF commands.
- `struct zfcp_fsf_req` stores one FSF command/status-read request, including list node, request id, adapter, QDIO queue metadata, completion, status bits, QTCB pointer, private data, timer, ERP action, allocation pool, issue timestamp, and completion handler.
- `zfcp_adapter_multi_buffer_active()` and `zfcp_fsf_req_is_status_read_buffer()` are small state classifiers.

## Control Flow And Integration

This header does not implement flows directly, but it defines the state that all flows operate on. FSF request creation fills `struct zfcp_fsf_req` and embeds a `struct zfcp_qdio_req`; QDIO completion uses the request id to locate the request and calls the request handler. ERP queues and mutates `struct zfcp_erp_action` embedded in adapter, port, or SCSI-device state. FC discovery and link testing mutate `struct zfcp_port` D_ID, WWNN, capability, and security fields. The SCSI mid-layer reaches zfcp LUN state through `sdev_to_zfcp()`.

Status propagation is a key design point. ERP setter/clearer functions in `zfcp_erp.c` apply common status bits from adapter to ports and LUNs, and from ports to LUNs. This header's bit layout makes that possible with `ZFCP_COMMON_FLAGS`.

## State And Persistence

All structures are in-kernel runtime state tied to adapter probe/lifetime, port objects, SCSI devices, and outstanding FSF requests. Important persistent-in-memory state includes:

- Monotonic FSF request ids (`adapter->req_no`) and FSF sequence numbers.
- Adapter hardware/configuration data from exchange-config and exchange-port-data.
- Port discovery/cache data (`wwpn`, `wwnn`, `d_id`, `handle`, capability/security fields).
- LUN handles and latency counters.
- ERP counters and total/low-memory ERP counters.
- Debug, workqueue, and diagnostic pointers.

There is no on-disk persistence here; sysfs configuration and SCSI transport objects are managed by other modules.

## Dependencies

The header pulls in Linux block, delay, timer, slab, mempool, scatterlist, ioctl, SCSI core, SCSI transport FC/BSG, s390 CCW/debug/EBCDIC/sysinfo, and zfcp FSF/FC/QDIO headers. This makes it a high-fanout include; changes can trigger broad rebuilds and cross-module coupling.

## Risks And Edge Cases

- Status bit reuse is deliberate. New common bits must stay within `ZFCP_COMMON_FLAGS`, while object-specific bits must not collide semantically with shared high bits.
- `enum zfcp_erp_act_type` and `enum zfcp_erp_steps` have storage-size constraints because debug records store them as `u8`/`u16`.
- `sdev_to_zfcp()` assumes SCSI transport-private data was initialized; using it during early or torn-down states can dereference invalid memory.
- `zfcp_scsi_dev_lun()` casts a local `u64` as `struct scsi_lun`; any endianness or layout assumptions must match SCSI/FCP expectations.
- Request lifetime is subtle: asynchronous FSF requests with cleanup status may be freed on completion, so callers must obey the "do not touch after send" convention implemented in `zfcp_fsf.c`.

## Test Signals

Good tests and runtime signals include:

- Adapter, port, and LUN common status propagation matches parent changes.
- ERP action types and steps still decode correctly in debug traces.
- SCSI devices can round-trip through `sdev_to_zfcp()` and FCP LUN conversion.
- FSF request ids remain unique and request-list lookup/removal works under completion races.
- Multi-buffer status toggles correctly when QDIO open detects hardware capability.
