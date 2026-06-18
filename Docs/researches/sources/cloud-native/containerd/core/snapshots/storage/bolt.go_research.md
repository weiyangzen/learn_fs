# sources/cloud-native/containerd/core/snapshots/storage/bolt.go

## Purpose
Implements BoltDB-backed snapshot metadata operations used by snapshotter implementations: info lookup/update/walk, active/view creation, active commit, removal, parent-chain lookup, usage storage, and ID mapping.

## APIs, Flow, State, Dependencies, Risks, And Tests
The storage schema uses version bucket `v1`, child bucket `snapshots`, parent backlink bucket `parents`, and per-snapshot keys for id, parent, kind, usage inodes/size, timestamps, and labels. `GetInfo`, `UpdateInfo`, `WalkInfo`, `GetSnapshot`, `CreateSnapshot`, `Remove`, `CommitActive`, and `IDMap` are the public operations. Helpers encode parent composite keys, require a transaction in context, create buckets, follow parent chains, read/write snapshot info, read/write usage, and adapt info to filter fields.

Control flow is transaction-bound. Creation only accepts active/view and requires committed parents. Commit creates the committed bucket, reads active metadata, ensures active kind, replaces labels, optionally rebases only parentless actives, writes usage, deletes the active bucket, and updates parent backlinks. Removal refuses snapshots with children and removes parent backlinks. Walk parses filters and scans all snapshot buckets.

Persistence is strongly tied to Bolt bucket layout and transaction context. Dependencies include bbolt, boltutil timestamps/labels, filters, snapshots types, errdefs, binary varints, and time.

Risks include no operation without transaction, parent backlink corruption blocking removals or parent-chain reads, unknown filters, defaulting missing kind to unknown, inability to remove parents with active/view children, and commit creating destination before validating source. Test signals are the metastore suite for create/get/walk/commit/remove/parents/rebase plus benchmarks and crash-consistency tests.
