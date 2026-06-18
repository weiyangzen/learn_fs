# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitReplica.java

Purpose: `ShortCircuitReplica` represents cached local file descriptors and optional shared-memory slot for an HDFS block replica used by short-circuit local reads.

Important APIs/types/functions: constructor stores block key, data/meta streams, cache, creation time, slot, and reads `BlockMetadataHeader`, accepting only version 1. `isStale()` checks slot validity when a slot exists or falls back to age threshold. `addNoChecksumAnchor()`/`removeNoChecksumAnchor()` manage slot anchors. `hasMmap()`, `munmap()`, and `loadMmapInternal()` handle mmap state. `close()` munmaps, closes streams, and schedules slot release. Accessors expose streams, metadata, key, slot, and `getOrCreateClientMmap()`.

Control flow: created by cache loader, handed to block readers, referenced/unreferenced through `ShortCircuitCache`. When no longer referenced and purged, `close()` releases all resources. Staleness is checked by cache before reuse and on unref.

State and persistence behavior: fields include immutable identity/resources plus cache-protected mutable `mmapData`, `purged`, `refCount`, and `evictableTimeNs`. The underlying file descriptors and mmap are OS resources; slot state is shared memory.

Dependencies and integration points: integrates with `ExtendedBlockId`, `BlockMetadataHeader`, `ShortCircuitCache`, `ShortCircuitShm.Slot`, `NativeIO.POSIX.munmap`, and `IOUtilsClient`.

Risks and test signals: metadata version mismatch fails construction. `close()` requires `refCount == 0` and `purged == true`. Slot-based staleness is safer than time-based fallback; no-slot replicas depend on configured threshold. Tests should cover metadata header validation, slot and time staleness, anchor add/remove, mmap limits/errors, close preconditions, and scheduled slot release.
