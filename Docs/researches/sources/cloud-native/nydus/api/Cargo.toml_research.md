# sources/cloud-native/nydus/api/Cargo.toml

## Purpose
This manifest defines the `nydus-api` crate, which contains API data types, HTTP request/response abstractions, endpoint handlers, configuration parsing types, and error helpers for Nydus.

## Important APIs, Types, and Functions
Package metadata sets name `nydus-api`, version `0.4.1`, Apache-2.0/BSD-3-Clause licensing, and homepage. Dependencies include `backtrace`, `dbs-uhttp`, `libc`, `log`, `serde`, `serde_json`, `thiserror`, and `toml`. Features are `error-backtrace` and `handler`.

## Control Flow
Cargo builds this crate as a workspace member and consumers enable optional features. `error-backtrace` activates richer logging in error macros; `handler` likely gates HTTP handler modules elsewhere in the crate.

## State and Persistence
No runtime state is stored in the manifest. It controls dependency resolution and feature compilation.

## Dependencies and Integration Points
The root `nydus-rs` crate depends on this crate with `error-backtrace` and `handler` features. HTTP modules integrate with `dbs-uhttp`; config modules integrate with serde/toml/json.

## Risks and Edge Cases
Feature-gated behavior means tests should cover both default and root-enabled feature sets if API consumers use different combinations. Version must remain synchronized with root manifest dependency expectations.

## Test Signals
Workspace builds and `nydus-api` unit tests validate the manifest. Root CI exercises it through `make build`, unit tests, smoke tests, and Miri.
