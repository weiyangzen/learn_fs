# sources/cloud-native/nydus/upgrade/src/persist.rs

Purpose: provides a `Snapshotter` trait for saving and restoring versioned Rust structs using `dbs-snapshot` and `versionize`.

Important APIs/types/functions: `Versions = Vec<HashMap<TypeId, u16>>` maps each snapshot version to per-type version numbers. `Snapshotter` extends `Versionize + Sized + Debug` and requires `get_versions`. Default methods build a `VersionMap`, create a latest-version `Snapshot`, serialize `self` into `Vec<u8>` with `save`, and deserialize from a mutable `Vec<u8>` with `restore`.

Control flow: `new_version_map` iterates over version maps; the first map applies to version 1, later maps call `version_map.new_version()` before setting type versions. `save` constructs a snapshot and serializes into a fresh buffer. `restore` calls `Snapshot::load` over the full input buffer and maps snapshot errors to `std::io::Error::other`.

State and persistence: persists versionized object graphs into byte buffers. No files or sockets are used directly; callers decide where bytes are stored, possibly via `StorageBackend`.

Dependencies and integration points: integrates with `dbs_snapshot::Snapshot` and `versionize::{VersionMap, Versionize}`. Designed for daemon online upgrade structures that need backward/forward version handling.

Risks: correctness depends on each implementor providing a complete `get_versions` map and proper `#[version]` annotations/defaults. `restore` consumes from a slice over the provided vector but does not shrink or clear it. Error messages include debug formatting but no structured error type. TypeId-based version maps are process/build specific and must align with versionize expectations.

Test signals: tests define simple versionized structs and cover single/multiple versions, snapshot creation, save/restore round trips with normal/empty/large values, and invalid/empty restore buffers.
