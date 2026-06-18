<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_statistics.h -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_statistics.h

## Purpose
Defines a serializable statistics snapshot for filesystem/global resource counters. The source was read completely for this report.

## Important APIs, Types, And Functions
`LizardFsStatistics` fields include version, memory/space counters, trash/reserved node counts, node counts, chunks, chunk copies, and regular copies.

## Control Flow
No handwritten control flow; generated serialization handles data movement.

## State And Persistence Behavior
Instances are transient snapshots but serialized over management protocols or stored where callers choose.

## Dependencies And Integration Points
Depends on `serialization_macros.h`; integrates with status/reporting APIs.

## Risks And Edge Cases
Field order and widths are schema-sensitive. Counters must be updated atomically/consistently by producers outside this header.

## Test Signals
Round-trip serialization and compatibility tests with management clients are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_statistics.h -->
