# sources/cloud-native/nydus/upgrade/Cargo.toml

Purpose: package manifest for the `nydus-upgrade` crate, which supports Nydus daemon online upgrade state persistence.

Important APIs/types/functions: package metadata names the crate `nydus-upgrade` version `0.2.0`, edition 2021, Apache-2.0 license. Dependencies are `sendfd`, `dbs-snapshot`, `thiserror`, `versionize_derive`, and `versionize`.

Control flow: none; Cargo uses the manifest to resolve and build the crate.

State and persistence: declares persistence-related dependencies but stores no runtime state.

Dependencies and integration points: `sendfd` supports fd transfer over Unix sockets; `dbs-snapshot` and `versionize` support versioned state snapshots; `thiserror` implements typed errors. The crate integrates with the rest of Nydus as an upgrade helper library.

Risks: dependency versions are pinned to broad minor versions. Snapshot compatibility depends on the exact behavior of `dbs-snapshot`/`versionize`, so manifest changes can affect upgrade compatibility.

Test signals: no tests in the manifest. Crate tests live in `src/backend/*` and `src/persist.rs`.
