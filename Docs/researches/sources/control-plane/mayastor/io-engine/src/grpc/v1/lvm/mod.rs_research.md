# sources/control-plane/mayastor/io-engine/src/grpc/v1/lvm/mod.rs

Purpose: this module centralizes conversion from the internal LVM backend error type into tonic statuses for v1 gRPC callers.

Important APIs/types/functions: the sole public behavior is `impl From<LvmError> for tonic::Status`. It maps invalid pool type, VG UUID mismatch, and disk mismatch to `invalid_argument`; missing VG/LV to `not_found`; no space to `resource_exhausted`; unsupported snapshots to `failed_precondition`; and all remaining errors to `internal`.

Control flow: conversion is a direct match on `LvmError`, preserving the error’s string representation as the status message. There is no asynchronous behavior and no service implementation in this file.

State and persistence: none. It only translates errors raised by the LVM backend elsewhere.

Dependencies and integration points: depends on `crate::lvm::Error` and `tonic::Status`. It is pulled into the v1 gRPC module tree and is also indirectly gated by `grpc::lvm_enabled` and pool backend selection.

Risks: broad fallback to `internal` may obscure actionable client errors; adding new `LvmError` variants without updating this match changes client-visible semantics; messages may include backend details. Test signals should pin mappings for each explicit variant and include a representative fallback variant.
