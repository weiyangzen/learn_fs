# sources/cloud-native/containerd/core/snapshots/snapshotter.go

## Purpose
Defines containerd's snapshotter contract, snapshot metadata structures, label constants, kind handling, cleanup interface, and creation options.

## APIs, Flow, State, Dependencies, Risks, And Tests
Constants define unpack key formats and snapshot labels, including UID/GID mappings and max-size hints. `Kind` models unknown/view/active/committed with parsing, string, and JSON marshal/unmarshal helpers. `Info` stores snapshot kind, name, parent, labels, and timestamps. `Usage` stores inode/size counts and `Add` combines usage values. `Snapshotter` defines stat, update, usage, mounts, prepare, view, commit, remove, walk, and close. `Cleaner` adds async cleanup. `WithLabels`, `FilterInheritedLabels`, and `WithParent` are option/helper functions.

The file is an interface/contract layer, not an implementation. Persistence semantics are documented: active/view/committed snapshots share one keyspace, active snapshots commit into immutable committed snapshots, and parent-child relationships constrain removal.

Dependencies are context, JSON, maps, strings, time, and containerd mount types. Integrations include all snapshotter plugins, metadata stores, proxy clients, unpack code, image layer import, and runtime rootfs preparation.

Risks include implementers violating lifecycle rules, callers relying on ignored max-size labels, unknown kinds mapping to unknown in JSON parsing, and inherited label filtering mistakes. Test signals are snapshotter conformance suites, kind JSON tests, label filtering tests, usage aggregation tests, and plugin integration tests.
