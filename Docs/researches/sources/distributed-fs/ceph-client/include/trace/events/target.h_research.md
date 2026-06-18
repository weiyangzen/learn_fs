
# sources/distributed-fs/ceph-client/include/trace/events/target.h

## Purpose
Defines Linux SCSI target-core tracepoints for command sequencer start and command completion, with opcode, task attribute, status, CDB, sense data, LUN, tag, data length, and initiator identity.

## Important APIs, Types, and Functions
Helper macros mirror SCSI opcode/status decoding: `show_opcode_name`, `show_task_attribute_name`, and `show_scsi_status_name`. Events are `target_sequencer_start` and `target_cmd_complete`. Fields are read from `struct se_cmd`, including `orig_fe_lun`, `tag`, `t_task_cdb`, `data_length`, `sam_task_attr`, `scsi_status`, `sense_buffer`, and session initiator name.

## Control Flow
Target core emits `target_sequencer_start` when a SCSI command enters target command sequencing and `target_cmd_complete` when it completes. Completion traces conditionally copy sense data when status is CHECK CONDITION.

## State and Persistence
The header owns no target-core state. Trace records persist copied CDB bytes, initiator string, sense bytes, status, attributes, and identifiers after the `se_cmd` continues or is freed.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, `linux/trace_seq.h`, SCSI protocol/task constants, and `target/target_core_base.h`. Integrates with LIO target fabrics such as iSCSI, Fibre Channel, vhost-scsi, and loopback target diagnostics.

## Risks
Tracing can expose initiator names, CDBs, LUNs, tags, and sense data. The event assumes populated session/node ACL pointers. Opcode tables must track SCSI command additions. Sense length calculation must stay consistent with SPC sense layout.

## Test Signals
Signals include target command tracing through common fabrics, CHECK CONDITION sense paths, task attribute variants, READ/WRITE/INQUIRY commands, initiator login/logout around tracing, and comparison with initiator-side SCSI traces.
