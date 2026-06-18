# Research: sources/cloud-native/moby/daemon/libnetwork/internal/kvstore/boltdb/boltdb.go

Purpose: implements libnetwork's internal KV store interface using bbolt. Important type/API are `BoltDB`, `New`, `Put`, `Exists`, `List`, `AtomicPut`, `AtomicDelete`, `Delete`, and `Close`; stored values have an eight-byte little-endian index prefix.

Control flow: `New` creates parent directories and opens bbolt with a nanosecond timeout to fail fast when the DB is already locked. `Put` creates the bucket, increments an atomic index, prefixes it, and writes. `Exists` and `List` view the bucket and return `ErrKeyNotFound` for absent keys/prefixes. Atomic operations compare the stored index against `previous.LastIndex`, handling create-if-absent for nil previous in `AtomicPut`. `Delete` removes without CAS.

State/dependencies: state is the bbolt file, bucket, mutex, and monotonic in-process `dbIndex`. Dependencies include bbolt, internal `kvstore`, atomic counters, and binary encoding. Risks include index reset on process restart, value-prefix assumptions requiring at least eight bytes, serialized access through a coarse mutex, and fast failure on lock contention. Tests are outside this subset.
