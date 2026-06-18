<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_dbg.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_dbg.h

## Purpose
This header declares SCSI debug formatting and printing helpers for commands, sense data, result codes, opcodes, sense keys, and host-byte/mid-layer return strings.

## Important APIs, Types, And Functions
Public declarations include `scsi_print_command()`, `__scsi_format_command()`, `scsi_print_sense_hdr()`, `scsi_print_sense()`, `__scsi_print_sense()`, `scsi_print_result()`, `scsi_opcode_sa_name()`, `scsi_sense_key_string()`, `scsi_extd_sense_format()`, `scsi_mlreturn_string()`, and `scsi_hostbyte_string()`. When `CONFIG_SCSI_CONSTANTS` is disabled, inline stubs return NULL or limited service-action recognition.

## Control Flow
The configured path formats and prints human-readable diagnostic data. The unconfigured path avoids constant tables: service-action names are only considered for commands where service actions are meaningful, and string lookups return NULL.

## State And Persistence
No state is owned. Output is transient logging/formatting data derived from command and sense buffers.

## Dependencies And Integration Points
The header forward declares SCSI command/device/sense types and relies on SCSI protocol constants for opcode checks. It integrates with driver diagnostics, EH logging, and mid-layer debug paths.

## Risks
Callers must tolerate NULL names when constants are disabled. Formatting command buffers must respect destination sizes. Debug output should not expose stale or uninitialized CDB/sense bytes.

## Test Signals
Build with and without `CONFIG_SCSI_CONSTANTS`, format common CDBs and variable/service-action CDBs, print fixed and descriptor sense, verify result string fallbacks, and check buffer truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_dbg.h -->
