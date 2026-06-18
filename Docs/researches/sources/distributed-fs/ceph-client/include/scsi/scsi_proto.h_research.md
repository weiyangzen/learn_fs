<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_proto.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_proto.h

## Purpose
This header defines SCSI protocol constants shared by initiator and target code: CDB opcodes, service actions, command sizes, SAM status, sense keys, device types, protocol identifiers, LUN layout, IO advice/stream descriptors, ALUA access states, ZBC zone reporting, version descriptors, and supported-opcode states.

## Important APIs, Types, And Functions
Important definitions include command opcodes from six-byte through variable-length and service-action commands, `SCSI_MAX_VARLEN_CDB_SIZE`, `struct scsi_varlen_cdb_hdr`, `enum sam_status`, sense-key constants, `TYPE_*` peripheral device constants, `enum scsi_protocol`, `struct scsi_lun`, `struct scsi_io_group_descriptor`, `struct scsi_stream_status`, `struct scsi_stream_status_header`, ALUA access-state masks, ZBC reporting/type/condition enums, `enum scsi_version_descriptor`, `enum scsi_support_opcode`, and static assertions for descriptor sizes.

## Control Flow
There is no runtime control flow. The header is consumed by CDB construction, command parsing, sense/status classification, inquiry parsing, ALUA, zoned block command handling, persistent reservations, and target/initiator protocol reporting.

## State And Persistence
No kernel state is owned here. The structs represent on-wire or standards-defined payloads and must stay size/layout stable.

## Dependencies And Integration Points
It depends on build assertions and Linux fixed-width/endian types. It is the protocol vocabulary for virtually all SCSI headers in this shard plus users of SCSI CDBs and responses.

## Risks
Opcode aliases require context-aware interpretation. Endian bitfields in IO advice and stream descriptors must match the protocol. Typographical constants, even if historically present, can become ABI expectations. Static size checks protect only selected structures.

## Test Signals
Compile-time size assertions, CDB opcode table coverage, service-action dispatch tests, SAM status classification, inquiry device-type/modality tests, ALUA state parsing, ZBC report parsing, and cross-build endian validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_proto.h -->
