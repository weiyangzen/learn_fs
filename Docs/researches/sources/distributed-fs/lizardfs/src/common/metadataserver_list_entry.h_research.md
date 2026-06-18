<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadataserver_list_entry.h -->
# sources/distributed-fs/lizardfs/src/common/metadataserver_list_entry.h

## Purpose
Defines a serializable metadataserver address/version entry. The source was read completely for this report.

## Important APIs, Types, And Functions
`MetadataserverListEntry` contains `uint32_t ip`, `uint16_t port`, and `uint32_t version` via serialization macros.

## Control Flow
No handwritten control flow.

## State And Persistence Behavior
Instances are serialized in master/shadow master listing protocols.

## Dependencies And Integration Points
Depends on `serialization_macros.h`.

## Risks And Edge Cases
Field order and IP byte-order expectations are ABI-sensitive.

## Test Signals
Round-trip serialization and list protocol tests are recommended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadataserver_list_entry.h -->
