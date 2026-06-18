<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_common.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_common.h

## Purpose
This header provides SCSI helpers shared by initiator and target code: persistent-reservation type conversion, command-size parsing, CDB control-byte access, device type naming, LUN conversion, and normalized sense handling.

## Important APIs, Types, And Functions
It defines `enum scsi_pr_type`, converters `block_pr_type_to_scsi()` and `scsi_pr_type_to_block()`, `scsi_varlen_cdb_length()`, external `scsi_command_size_tbl`, `COMMAND_SIZE()`, `scsi_command_size()`, `scsi_command_control()`, `scsi_device_type()`, `int_to_scsilun()`, `scsilun_to_int()`, `struct scsi_sense_hdr`, `scsi_sense_valid()`, `scsi_normalize_sense()`, `scsi_build_sense_buffer()`, `scsi_set_sense_information()`, `scsi_set_sense_field_pointer()`, and `scsi_sense_desc_find()`.

## Control Flow
Inline command parsing branches on `VARIABLE_LENGTH_CMD`: variable CDBs derive length from the header, while fixed CDBs index the command-size table. Sense helpers normalize fixed or descriptor sense into `scsi_sense_hdr` and allow descriptor lookup and extra information/field-pointer population.

## State And Persistence
No persistent state is owned. The sense header is a compact transient representation of a larger sense buffer, and callers must retain the original buffer when detailed descriptors are needed.

## Dependencies And Integration Points
The header depends on Linux types, block persistent-reservation UAPI, and SCSI protocol constants. It is consumed by initiator, target, EH, SG, and drivers that need CDB/sense utility logic.

## Risks
Variable-length CDB parsing trusts the header enough to compute length; callers need buffer-length validation. Sense normalization can lose details if callers discard the original buffer. PR type conversion must stay in sync with block-layer reservation semantics.

## Test Signals
Validate CDB lengths for fixed and variable commands, control-byte extraction, LUN integer round trips, fixed/descriptor sense normalization, sense descriptor lookup, field-pointer insertion, and PR type conversion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_common.h -->
