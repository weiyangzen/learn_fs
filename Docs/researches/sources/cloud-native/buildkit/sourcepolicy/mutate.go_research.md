# sources/cloud-native/buildkit/sourcepolicy/mutate.go

## Purpose
Applies a source policy convert rule to a BuildKit source operation.

## Important APIs, Types, And Functions
- `mutate(ctx, op, rule, selector, ref)` changes `op.Identifier` and/or `op.Attrs`.

## Control Flow
The function requires `rule.Updates`, chooses the update identifier or falls back to the selector identifier, formats it through the selector cache, updates the source identifier if changed, ensures the attrs map exists, writes changed attr values, logs conversions and attr updates, and returns whether anything changed.

## State And Persistence
Mutates the supplied protobuf `SourceOp` in place. No persisted state.

## Dependencies And Integration Points
Called by `Engine.evaluatePolicy` for `CONVERT` rules. Uses BuildKit logging and sourcepolicy protobuf update fields.

## Risks And Edge Cases
Missing `Updates` is an error. Empty destination falls back to selector identifier, so rules that only set attrs still may format a selector-derived identifier. Existing attrs are overwritten without delete support.

## Test Signals
`mutate_test.go` covers identifier rewrites, digest replacement, HTTP checksum attr insertion, and proto equality after mutation.
