# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-hvpipe.h

## Purpose
Defines internal HVPIPE constants, event/source state structures, migration actions, and the pSeries migration hook declaration.

## Important APIs, Types, And Functions
Defines `HVPIPE_HMC_ID_MASK`, `HVPIPE_MAX_WRITE_BUFFER_SIZE`, `RTAS_HVPIPE_CLOSED`, `HVPIPE_HDR_LEN`, `enum hvpipe_migrate_action`, `struct hvpipe_source_info`, `struct hvpipe_event_buf`, and `hvpipe_migration_handler`.

## Control Flow
No runtime control flow is present. The declarations guide `papr-hvpipe.c` and `mobility.c` interactions.

## State And Persistence
`struct hvpipe_source_info` describes per-source runtime list membership, status, source id, and poll waitqueue. `struct hvpipe_event_buf` mirrors the firmware event payload. The header itself stores no state.

## Dependencies And Integration Points
Depends on list and waitqueue types through including translation units. It links the HVPIPE driver with partition migration code and the uapi HVPIPE header's message flags/header structure.

## Risks And Edge Cases
The source-id mask supports only HMC-style ids in the current driver. The comment documents the source id format; mismatched firmware encoding would break filtering in ioctl/event paths.

## Test Signals
Compile coverage for HVPIPE and mobility builds, plus runtime source-id validation and event decoding, are the main signals.
