# sources/distributed-fs/eos/namespace/interface/Misc.hh

Purpose: provides a small shared metadata interface struct for namespace cache statistics.

Important APIs/types/functions: `CacheStatistics` has fields `enabled`, `maxNum`, `occupancy`, `inFlight`, `numRequests`, and `numHits`, all default-initialized.

Control flow: none; this is a data-only header.

State and persistence: no internal state or persistence. Instances represent a snapshot of cache configuration, capacity, occupancy, inflight fetches, and hit/request counters.

Dependencies and integration: included by namespace service interfaces and implementations that report metadata cache status, such as QuarkDB file/container metadata services.

Risks: counters are plain values in the snapshot; producers must collect them under their own synchronization if they need consistency. The struct does not encode units beyond field names.

Test signals: indirectly covered where file/container service cache statistics are asserted or exposed through namespace monitoring paths.
