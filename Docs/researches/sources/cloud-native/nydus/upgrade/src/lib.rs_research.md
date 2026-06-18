# sources/cloud-native/nydus/upgrade/src/lib.rs

Purpose: crate root for `nydus-upgrade`.

Important APIs/types/functions: exposes `pub mod backend` and `pub mod persist`.

Control flow: none.

State and persistence: none directly. It makes backend fd transfer and snapshot persistence modules available to downstream crates.

Dependencies and integration points: Cargo builds this as the library root. Public module exposure defines the crate API.

Risks: minimal. All public API is delegated to submodules, so compatibility is controlled there.

Test signals: no direct tests; submodules contain unit tests.
