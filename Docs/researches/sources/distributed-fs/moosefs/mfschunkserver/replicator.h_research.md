# sources/distributed-fs/moosefs/mfschunkserver/replicator.h

## Purpose
`replicator.h` declares the chunkserver replication interface used by background jobs.

## APIs and integration
`repmodeenum` defines `SIMPLE`, `SPLIT`, `RECOVER`, and `JOIN`. `replicator_stats()` returns and resets byte counters plus replication count. `replicate()` accepts destination chunk id/version, split part metadata, and source IP/port/chunk-id arrays sized to `MAX_EC_PARTS`.

## State and risks
Implementation state is private and protected by a mutex for stats. Callers must provide valid source arrays and sane part counts; split mode additionally requires `partno < parts`. Tests should verify status-code propagation and stats reset semantics.
