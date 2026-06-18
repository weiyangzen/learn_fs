# File Research: sources/block-storage/stratisd/src/stratis/errors.rs

## Purpose

Defines the central `StratisError` type and `StratisResult<T>` alias.

## Main Types and Behavior

- `StratisError` covers plain messages, chained errors, best-effort rollback groups, rollback errors with action availability, no-action rollback errors, disabled actions, out-of-space, and wrapped external errors.
- `error_to_all_available_actions` walks nested error structures to collect pool action availability restrictions.
- `error_to_available_actions` returns the most restrictive availability state.
- Implements `Display`, `Error`, and `From` conversions for IO, nix, UUID, UTF-8, serde JSON, data encoding, devicemapper, cryptsetup, tokio join, blkid, udev, mpsc receive, NUL, and feature-gated D-Bus errors.

## Integration Points

This error type is used across engine, runtime, JSON-RPC, D-Bus, devicemapper, cryptsetup, udev, and systemd integration.

## Notable Semantics

Rollback-related variants carry enough structure to both report the causal and rollback failures and derive the pool action restrictions that should result.
