# sources/cloud-native/containerd/core/metadata/db_test.go

## Purpose

This test file validates metadata DB initialization, migrations, garbage-collection graph behavior, benchmarks GC, and verifies DB close behavior.

## Important APIs, Types, and Functions

`testDB`, `newStores`, and `testEnv` create temporary DB/content/snapshot environments. `TestInit` verifies DB version. `TestMigrations` drives each migration through an init/check pair. `TestMetadataCollector` builds a mixed graph of content, snapshots, containers, images, leases, flat leases, and custom collectible resources. `BenchmarkGarbageCollect` measures GC over generated object sets. `TestClose` verifies underlying bbolt closure.

## Control Flow

Migration tests create old-layout data, run the selected migration, and inspect the resulting buckets. Collector tests register a custom resource collector, create objects in a single transaction, run `GarbageCollect`, scan all remaining nodes, and compare them to the expected reachable set. Benchmarks generate many repeated content/image/snapshot/container sets and repeatedly invoke GC under pprof labels.

## State and Persistence Behavior

The tests create real bbolt DBs, local content stores, and native snapshotters in temp directories. They exercise schema buckets, content metadata, snapshot metadata, leases, GC labels, custom collector state, backend cleanup, and DB close behavior.

## Dependencies and Integration Points

The file integrates most metadata subsystems: containers, images, content, leases, snapshots, bbolt, local content, native snapshots, GC package, protobuf Any, namespace context, migrations, and test collectors/helpers defined in the same package.

## Risks and Edge Cases

Migration test count is tied to `len(migrations)`, forcing new migrations to add coverage. The GC benchmark does not assert post-GC state during benchmarking. Some helper-created objects bypass public APIs for setup convenience, so public API coverage comes from other tests.

## Test Signals

Passing tests indicate DB version initialization, each migration's structural transformation, GC reachability across labels/leases/flat leases/custom resources, and safe DB close semantics. Benchmarks provide performance signals for mark/sweep scaling.
