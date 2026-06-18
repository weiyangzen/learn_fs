# sources/cloud-native/containerd/core/leases/id.go

## Purpose

This file provides lease option helpers for setting lease IDs. It includes explicit IDs and a simple random ID generator.

## Important APIs, Types, and Functions

`WithRandomID()` returns an option that sets `Lease.ID` to `<nanosecond>-<base64url random 3 bytes>`. `WithID(id)` returns an option that sets `Lease.ID` to the provided string.

## Control Flow

Each function returns a closure over a `*Lease`. The random form reads three random bytes, combines them with the current nanosecond value, and assigns the resulting string. The explicit form assigns the given ID directly.

## State and Persistence Behavior

The functions mutate only an in-memory `Lease` during option application. Persistence is handled by lease manager implementations.

## Dependencies and Integration Points

These options are passed to `leases.Manager.Create`, including metadata and proxy lease managers. They depend on `crypto/rand`, `base64`, `fmt`, and `time`.

## Risks and Edge Cases

`rand.Read` errors are ignored, so random bytes could remain zero if the system RNG fails. Three random bytes plus nanoseconds is not a strong global uniqueness guarantee under high concurrency or across processes. `WithID` performs no validation; managers must reject invalid or duplicate IDs.

## Test Signals

Tests should check explicit ID application, random ID non-empty format, low collision behavior in repeated calls, and manager-level duplicate/invalid ID handling.
