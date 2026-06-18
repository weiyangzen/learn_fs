# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_ext.h`

## Purpose

`zfcp_ext.h` is the external declaration hub for the zfcp driver. It declares cross-file functions, global driver objects, cache pointers, templates, and sysfs attribute groups. It does not implement behavior, but it documents module boundaries and the major integration surface between adapter/CCW setup, debug tracing, ERP, FC services, FSF commands, QDIO transport, SCSI integration, sysfs, and unit management.

## Important APIs And Integration Points

- `zfcp_aux.c`: adapter/port allocation and lookup, adapter release/unregister.
- `zfcp_ccw.c`: CCW driver object and adapter lookup/reference helpers.
- `zfcp_dbf.c`: debug feature registration/unregistration and trace emitters for recovery, HBA, SAN, and SCSI events.
- `zfcp_erp.c`: all public recovery entry points, ERP thread lifecycle, wait/notify, timeout handler, status propagation, and synchronous adapter reset.
- `zfcp_fc.c`: FC event queueing/posting, port scan, incoming ELS handling, D_ID lookup, PLOGI evaluation, ADISC link tests, WKA GS setup/destruction, BSG CT/ELS execution, symbolic name update, and scan throttling helpers.
- `zfcp_fsf.c`: QTCB cache, FSF open/close/exchange/status-read/SCSI/abort/task-management commands, request cleanup, FC host link-down update, request-id completion, and FC security formatting.
- `zfcp_qdio.c`: QDIO setup/open/close/destroy, SBAL acquisition/send, scatterlist-to-SBAL mapping, SCSI host queue-limit update, and SIOSL logging.
- `zfcp_scsi.c`: transport template, adapter registration, rport work, rport block/register scheduling, DIF/DIX helpers, and SCSI host update callbacks.
- `zfcp_sysfs.c`: sysfs attribute groups and port-removal predicate.
- `zfcp_unit.c`: unit add/remove/find, SCSI-device lookup, SCSI scan queueing, and unit status.

## Control Flow Implications

The declarations reveal the main driver flow:

1. CCW/aux code creates an adapter and sets up debug, QDIO, diagnostics, FC GS, SCSI transport, and ERP.
2. ERP drives QDIO open and FSF exchange-config/port-data.
3. FSF/QDIO handle hardware request submission and completion.
4. FC code manages discovery, WKA name-server ports, CT/ELS traffic, and BSG passthrough.
5. SCSI code registers hosts, rports, and devices, then sends commands through FSF.
6. Debug, sysfs, and diagnostics observe and expose internal state.

## State And Persistence

The header exposes global runtime objects (`zfcp_ccw_driver`, `zfcp_fc_req_cache`, `zfcp_fsf_qtcb_cache`, `zfcp_scsi_transport_template`, `zfcp_transport_functions`, `zfcp_experimental_dix`, sysfs groups, and `zfcp_sysfs_port_units_mutex`). Persistent state itself lives in the modules and structures declared elsewhere. Because this header is included widely, it is a stable in-driver ABI for symbol names and signatures.

## Dependencies

It includes Linux types/sysfs, FC ELS definitions, and `zfcp_def.h`/`zfcp_fc.h`. That creates circular-seeming but guarded include relationships with the central zfcp headers. The header depends on many forward-declared kernel types from included headers: `ccw_device`, `ccw_driver`, `bsg_job`, `scsi_device`, `scsi_cmnd`, `fc_function_template`, and FSF QTCB structures.

## Risks And Edge Cases

- This file has high fanout. Signature changes must be applied consistently across many modules.
- It exposes internal globals and implementation functions, so adding declarations can increase coupling rather than preserving module boundaries.
- The include of `zfcp_def.h` means many declarations rely on full structure definitions rather than forward declarations, increasing compile coupling.
- Some APIs have strict context expectations not visible from the signature, such as QDIO request-lock requirements, FSF async lifetime rules, and ERP lock requirements.

## Test Signals

Build-time validation is the primary signal: all declarations must match definitions across modules. Runtime integration tests should exercise adapter probe/remove, ERP recovery, FC scans, BSG CT/ELS jobs, SCSI command/abort/TMF paths, sysfs add/remove, and diagnostics to catch cross-module signature or lifetime drift.
