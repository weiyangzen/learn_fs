# sources/control-plane/mayastor/io-engine/src/grpc/v1/lvs/mod.rs

Purpose: this compatibility shim converts legacy `Lvol` values into the v1 `Replica` protobuf through the generic replica backend abstraction.

Important APIs/types/functions: `impl From<Lvol> for Replica` casts `&Lvol` to `&dyn ReplicaOps` and delegates to the `From<&dyn ReplicaOps> for Replica` implementation defined in `grpc/v1/replica.rs`.

Control flow: conversion is synchronous and intentionally tiny. It avoids duplicating field mapping for LVS replicas by reusing the trait-object conversion path shared by all replica backends.

State and persistence: none. It reads `Lvol` metadata through `ReplicaOps` only.

Dependencies and integration points: depends on `crate::lvs::Lvol`, `crate::replica_backend::ReplicaOps`, and `io_engine_api::v1::replica::Replica`. It links older LVS-specific code with the backend-neutral v1 replica API.

Risks: correctness depends entirely on the `ReplicaOps` implementation for `Lvol` and on the central mapping in `replica.rs`; any backend-specific data not exposed through `ReplicaOps` is lost. Test signals should verify an `Lvol` converts identically through direct trait-object mapping and through this shim, including snapshots/clones/encryption fields.
