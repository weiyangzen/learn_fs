# sources/distributed-fs/lizardfs/src/master/matomlserv.h

## Purpose

`matomlserv.h` declares the public interface for the master-to-metalogger/shadow service. It exposes status, shadow listing, changelog broadcast, metadata-save result broadcast, initialization, and graceful-exit queries. The source was read as a complete 50-line header.

## Important APIs, Types, and Functions

Functions include `matomlserv_mloglist_size`, `matomlserv_mloglist_data`, `matomlserv_shadows`, `matomlserv_broadcast_logstring`, `matomlserv_broadcast_logrotate`, `matomlserv_broadcast_metadata_saved`, `matomlserv_init`, `matomlserv_canexit`, and `matomlserv_shadows_count`.

## Control Flow

There is no executable flow in the header. It defines entry points used by filesystem/changelog code to push changes and by event-loop startup/shutdown paths to run the service.

## State and Persistence Behavior

No state is owned here. The implementation owns runtime connections, shadow queues, and cached changelog blocks; persistent metadata/changelog files are accessed indirectly.

## Dependencies and Integration Points

The only project-specific type exposed is `MetadataserverListEntry`, making this header part of status/reporting surfaces as well as the metadata replication pipeline.

## Risks and Edge Cases

Callers of `matomlserv_broadcast_logstring` pass raw buffers and sizes; ownership remains with the caller, but the implementation copies into its cache and output queues. `matomlserv_canexit` reflects connection-drain state and must be polled during shutdown.

## Test Signals

Compile coverage from master filesystem/changelog/status code, integration tests that observe changelog packets at metaloggers/shadows, and shutdown tests that wait on `matomlserv_canexit`.
