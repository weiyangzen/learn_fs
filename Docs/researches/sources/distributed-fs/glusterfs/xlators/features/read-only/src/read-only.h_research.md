# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only.h

## Purpose
`read-only.h` defines the shared private state structures for both the read-only and WORM translators, including WORM retention attributes.

## Important APIs and Types
- `worm_reten_state_t` stores packed WORM/retention flags (`worm`, `retain`, `legal_hold`, `ret_mode`) plus retention and auto-commit periods.
- `read_only_priv_t` stores global read-only/WORM enablement, file-level WORM mode, deletability policy, default retention period, auto-commit period, retention mode, and start time.

## Control Flow
No executable flow. The fields are interpreted by `read-only-common.c`, `read-only.c`, `worm.c`, and `worm-helper.c`.

## State and Persistence
`read_only_priv_t` is process-local translator state populated from volume options. `worm_reten_state_t` is also serialized to the `trusted.reten_state` xattr by helper functions, making its layout semantically tied to persistent xattr encoding even though the struct itself is in memory.

## Dependencies and Integration Points
Includes standard integer/time headers and GlusterFS boolean definitions. Used by both modules from the read-only feature directory.

## Risks
Bit-field layout is not directly written as binary, but semantic changes must stay compatible with `gf_worm_serialize_state()` and `gf_worm_deserialize_state()`. Option handling must keep `read_only_priv_t` fields initialized before wrappers run.

## Test Signals
Tests should verify retention serialization/deserialization preserves every `worm_reten_state_t` field and that option parsing in read-only/WORM populates `read_only_priv_t` as expected.
