# sources/cloud-native/ostree/rust-bindings/src/auto/mod.rs

Purpose: Generated module aggregator for the Rust `ostree` crate's auto-generated bindings. It declares generated modules and re-exports their public types, enums, flags, constants, and selected extension traits.

Important APIs: Re-exports core object wrappers such as `AsyncProgress`, `BootconfigParser`, `Deployment`, `Repo`, `Sysroot`, `SysrootUpgrader`, finder/sign/sepolicy types, boxed/shared structs, enums, flags, and constants. It keeps `functions` as `pub(crate)` and exposes extension traits under `pub(crate) mod traits`.

Control flow and state: There is no runtime control flow. Compile-time feature gates determine which modules and symbols are included, such as `CollectionRef`, `CommitSizesEntry`, `Remote`, `RepoFinderResult`, `ChecksumFlags`, `RepoCommitState`, and `RepoVerifyFlags`.

Dependencies and integration points: This file is the central integration point between generated files and the rest of the crate. Manual modules import from these re-exports, and public crate users see this curated surface.

Risks: Export drift here can make generated APIs inaccessible or expose APIs under the wrong feature. Because `functions` is crate-private, manual wrapper code must intentionally re-export any free functions meant for public use. Regeneration can reorder or alter exports broadly.

Test signals: `cargo doc` and compile tests across features should verify exports. Public API diff tooling is useful when regenerating bindings.
