# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_diag.h

Purpose: defines the binary diagnostic-trigger ABI used by the MPT3SAS driver for configured trigger lists and fired-trigger event payloads. It is shared by sysfs/control code, trigger matching, and persistent trigger-page translation.

Important APIs/types/functions: constants include `NUM_VALID_ENTRIES`, trigger type IDs `MPT3SAS_TRIGGER_MASTER`, `MPT3SAS_TRIGGER_EVENT`, `MPT3SAS_TRIGGER_SCSI`, `MPT3SAS_TRIGGER_MPI`, sysfs file names, master trigger bitmasks, and the synthetic `MPI3_EVENT_DIAGNOSTIC_TRIGGER_FIRED`. Structures are `SL_WH_MASTER_TRIGGER_T`, `SL_WH_EVENT_TRIGGER_T`, `SL_WH_EVENT_TRIGGERS_T`, `SL_WH_SCSI_TRIGGER_T`, `SL_WH_SCSI_TRIGGERS_T`, `SL_WH_MPI_TRIGGER_T`, `SL_WH_MPI_TRIGGERS_T`, and `SL_WH_TRIGGERS_EVENT_DATA_T`.

Control flow: the header has no direct execution, but its layouts drive trigger configuration and matching. The list wrappers carry `ValidEntries` plus up to 20 entries. Trigger event data stores a type discriminator and union so the event log can report the exact condition that released the diagnostic buffer.

State and persistence: structures are copied into adapter runtime fields and may be serialized through sysfs or firmware persistent trigger pages. The header fixes size and field ordering, so it effectively defines an ABI between userspace tooling, driver memory, and event payload decoding.

Dependencies and integration points: included by `mpt3sas_base.h` users and `mpt3sas_trigger_diag.c`. It uses Linux-style integer aliases including `U8` from the MPT headers/base include environment.

Risks and test signals: because these are binary structures, padding, endian assumptions, and `ValidEntries` bounds are important. Tests should verify sysfs read/write sizes, rejection or clamping above 20 entries, correct wildcard values (`0xFF` and `0xFFFFFFFF`), and compatibility of fired-event payloads consumed by diagnostic utilities.
