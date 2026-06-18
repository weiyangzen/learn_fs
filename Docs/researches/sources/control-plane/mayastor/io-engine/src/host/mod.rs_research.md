# sources/control-plane/mayastor/io-engine/src/host/mod.rs

Purpose: this module is the host subsystem namespace for io-engine. It publicly exposes `blk_device` discovery and `resource` usage modules to gRPC and other callers.

Important APIs/types/functions: it contains only `pub mod blk_device;` and `pub mod resource;`. The important behavior is module visibility, not local logic.

Control flow: none locally. Rust module resolution makes `crate::host::blk_device` and `crate::host::resource` available to v0/v1 gRPC services.

State and persistence: none.

Dependencies and integration points: used by `grpc/v0/mayastor_grpc.rs` and `grpc/v1/host.rs` for block-device listing and process resource usage. Any change here is a public module tree change for the crate.

Risks: removing or privatizing either module breaks host-related gRPC APIs. Test signals are compile-time: host gRPC modules should build and resolve both submodules.
