# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule_hash.go

## Purpose
This file computes stable compact identifiers for lifecycle rules. The hash is used in `ActionKey` state so compiled actions can retain continuity across rule ID renames and status flips while changing when filters or action semantics change.

## Important APIs and functions
`RuleHash` returns the first eight bytes of SHA-256 over a canonical length-prefixed encoding. It includes prefix, sorted tag filters, size filters, expiration days/date/delete-marker flag, noncurrent days, noncurrent keep count, and MPU abort days. It intentionally ignores `Rule.ID` and `Rule.Status`. Helpers `writeBytes`, `writeUvarint`, `writeInt64`, `writeBool`, and `canonicalTime` encode values with field tags and varint length/value framing.

## Control flow and state behavior
The function is nil-safe, returning a zero hash for nil rules. Tag keys are sorted before encoding so map iteration order cannot perturb hashes. `ExpirationDate` is canonicalized to UTC RFC3339Nano; zero time encodes as an empty string. The file has no persistence but influences persisted or long-lived scheduler prior states keyed by rule hash.

## Dependencies and integration points
Dependencies are `crypto/sha256`, `encoding/binary`, `sort`, and `time`. The hash is consumed by engine compile output, scheduler prior-state seeding, router match keys, and any code reconciling rule state across refreshes.

## Risks and edge cases
Only eight bytes of SHA-256 are retained, so theoretical collision risk exists but is small for operational rule counts. Any new semantically relevant `Rule` field must be added to this encoding or stale action state may be reused after a rule change. Conversely, adding non-semantic fields would unnecessarily reset state if included.

## Test signals
`rule_hash_test.go` covers determinism, tag-order invariance, prefix sensitivity, ignored ID/status, different action/filter fields, nil safety, and delimiter/field-boundary collision resistance.
