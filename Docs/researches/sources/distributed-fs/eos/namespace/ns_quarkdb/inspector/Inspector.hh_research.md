# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Inspector.hh

## Purpose
This header declares the administrative `Inspector` facade for direct QuarkDB namespace inspection and repair. It collects many operational commands behind one object that owns no QDB connection itself, but references a `qclient::QClient` and an `OutputSink`.

## Important APIs, Types, and Functions
`CacheNotifications` groups fids and cids whose metadata caches should be invalidated after direct writes. `Inspector` exposes connectivity, traversal, dump, scan, consistency-check, layout-check, print, repair, mutation, configuration, and metadata-filter methods. Public mutators include `overwriteContainerMD`, `fixDetachedParentContainer`, `fixDetachedParentFile`, `fixShadowFile`, `dropFromDeathrow`, `dropEmptyCid`, `changeFid`, `renameCid`, and `renameFid`.

Private state includes `mgmConfiguration`, `validFsIds`, `mQcl`, `mOutputSink`, and optional `mMetadataFilter`. Private helpers `isDestinationPathSane()` and `executeRequestBatch()` enforce minimal repair destination checks and centralize direct QDB write execution.

## Control Flow
Callers construct `Inspector(qclient::QClient&, OutputSink&)`, optionally call `checkConnection()` and `loadConfiguration()`, then invoke one command method. Methods return errno-like integers: `0` on success and nonzero for command-level failure. Output goes through the injected sink for most scanner commands, while some repair/check methods receive explicit `out` and `err` streams.

## State and Persistence Behavior
The header makes it clear that the inspector can write persistent namespace metadata directly. It stores configuration-derived fs ids for filtering and an optional file metadata filter for raw file scans. It does not own cache, service, or transaction state; persistent effects are delegated to implementation methods that issue Redis requests.

## Dependencies and Integration Points
The declaration depends on EOS namespace macros, `RequestBuilder` request types, container protobufs, qclient forward declarations, scanners, output sink, and file metadata filters. It integrates with command-line/admin layers that need a single API for namespace inspection.

## Risks and Test Signals
The broad API mixes safe reads with dangerous repairs, so callers need explicit dry-run defaults and clear privilege boundaries. Tests should verify each public method returns stable nonzero errors on bad input, that `setMetadataFilter()` ownership is unique and honored by file scans, and that dry-run mutation calls never execute QDB writes.
