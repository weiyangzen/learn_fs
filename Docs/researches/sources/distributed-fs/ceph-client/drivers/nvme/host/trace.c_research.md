<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/trace.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/trace.c

## Purpose
Provides formatter helpers behind the NVMe tracepoints declared in `trace.h`. It decodes admin, NVM, zoned, reservation, and fabrics command dwords into readable trace strings and exports the `nvme_sq` tracepoint symbol.

## Important APIs, Types, And Functions
Public helpers are `nvme_trace_parse_admin_cmd()`, `nvme_trace_parse_nvm_cmd()`, `nvme_trace_parse_fabrics_cmd()`, and `nvme_trace_disk_name()`. Opcode-specific decoders include queue create/delete, identify, get/set features, format NVM, get LBA status, read/write/write-zeroes/zone-append, DSM, zone management send/receive, reservation operations, and fabrics property/connect/auth commands. All helpers write into `struct trace_seq` and use unaligned little-endian accessors for command bytes.

## Control Flow
Tracepoint print code passes opcode, queue id, fabrics command type, and command dwords into the parse helpers. The helpers switch on the opcode or fabrics type, decode recognized fields, terminate the trace sequence string, and fall back to raw hex dumps for unsupported commands. Disk names are conditionally prefixed only when a request has a backing gendisk.

## State And Persistence
The file is stateless. It uses static string tables for zone and reservation action names and writes transient formatted data into trace sequence buffers supplied by ftrace.

## Dependencies And Integration Points
Depends on Linux trace infrastructure, `linux/unaligned.h`, NVMe opcode definitions, and the `TRACE_EVENT` declarations in `trace.h`. It is part of the host trace ABI and is consumed by ftrace/perf tooling when NVMe trace events are enabled.

## Risks
Formatter bugs can mislead debugging without affecting I/O behavior. Field offsets must match NVMe command layouts, especially packed cdw10-cdw15 interpretations for zone, reservation, and fabrics commands. Unsupported new opcodes fall back to raw bytes, so observability can lag protocol support.

## Test Signals
Enable `nvme_setup_cmd` traces for representative admin, I/O, fabrics, zoned, and reservation commands and verify decoded fields against submitted commands. Build testing should catch missing opcode definitions, while trace output should not contain unterminated strings or incorrect endian conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/trace.c -->
