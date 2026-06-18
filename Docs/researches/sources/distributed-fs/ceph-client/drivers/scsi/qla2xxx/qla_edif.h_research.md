<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.h

## Purpose

`qla_edif.h` contains the in-kernel EDIF definitions shared by the qla2xxx EDIF implementation and the rest of the driver. It defines the application identity, SA control object, doorbell and PUREX queue state, SA update IOCB wire layout, pending ELS event structures, and convenience macros for EDIF session state checks.

## Important APIs, Types, And Data

- `EDIF_APP_ID` and `EDIF_MAX_INDEX` define the expected userspace application identifier and maximum SA index space.
- `struct edif_sa_ctl` tracks a single SA update/delete request, including list linkage, index fields, state bits, owning `fc_port`, optional BSG job, and copied `qla_sa_update_frame`.
- `struct pur_core` holds the pending unsolicited receive event queue (`head`), lock, and active flag.
- `struct edif_dbell` holds the doorbell event queue, lock, active flag, pending long-poll BSG job, and expiration.
- `struct sa_update_28xx` describes firmware IOCB type `0x71`, including nport handle/completion status, VP index, port ID, flags, key material, salt, SPI, SA control, SA index, and old/new SA info fields.
- `struct enode`, `struct purexevent`, and `struct pur_ninfo` describe copied PUREX authentication ELS payloads awaiting userspace retrieval.
- `EDIF_SESSION_DOWN()`, `EDIF_NEGOTIATION_PENDING()`, `EDIF_SESS_DELETE()`, and `EDIF_CAP()` centralize common EDIF capability and session-state predicates.

## Control Flow

This header has no executable control flow, but its structures define the state machines used by `qla_edif.c`. Userspace SA commands are copied into `edif_sa_ctl`, formatted into `sa_update_28xx`, submitted to firmware, then completed back into the same per-port SA tracking. PUREX ELS frames become `enode` entries on `pur_core.head`; doorbell notifications become `edb_node` entries on `edif_dbell.head`; long-poll BSG jobs wait in `edif_dbell.dbell_bsg_job`.

## State And Persistence Behavior

The structures declared here are embedded in long-lived host and port objects or allocated per event/request. `edif_sa_ctl` entries persist from BSG SA request acceptance until firmware completion and cleanup. `pur_core` and `edif_dbell` queues persist for the host lifetime but are active only while the EDIF app is started. The firmware SA indexes represented in `sa_update_28xx` persist in adapter firmware until an invalidate IOCB, session teardown, or reset.

## Dependencies And Integration Points

The header depends on qla core types supplied before inclusion: `fc_port`, `scsi_qla_host`, `qla_sa_update_frame`, `port_id_t`, `bsg_job`, and list/spinlock primitives. It is included by `qla_edif.c` and indirectly tied to `qla_fw.h` command/status definitions, `qla_edif_bsg.h` userspace ABI structures, and `qla_gbl.h` prototypes.

## Risks And Edge Cases

- `struct sa_update_28xx` is a firmware ABI. Field sizes, endian annotations, packing expectations, and bit definitions must match firmware exactly.
- `struct edif_sa_ctl` carries both list state and BSG/firmware request state; double completion or double removal would corrupt per-port lists.
- `EDIF_CAP()` gates support on both module parameter `ql2xsecenable` and `IS_QLA28XX()`. Any new EDIF-capable hardware requires this macro and call sites to be reviewed.
- Macros such as `EDIF_SESSION_DOWN()` dereference nested session fields and assume valid `vha` and initialized EDIF state.

## Test Signals

Compile tests should catch layout users and missing type dependencies across EDIF-enabled and disabled builds. Runtime validation should indirectly exercise every state bit in `edif_sa_ctl`, active/inactive transitions for `pur_core` and `edif_dbell`, firmware SA update IOCB formatting, and capability gating through `EDIF_CAP()` on 28xx and non-28xx adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.h -->
