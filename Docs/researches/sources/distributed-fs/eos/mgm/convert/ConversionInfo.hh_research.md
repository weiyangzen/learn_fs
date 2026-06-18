# sources/distributed-fs/eos/mgm/convert/ConversionInfo.hh

## Purpose
Declares the conversion descriptor type and its public immutable fields. It is the shared contract for converter scheduling, job execution, CLI/tag helpers, and proc path construction.

## Important APIs and Types
- `constexpr int CONVERTION_SHARD_MOD = 256` defines conversion proc sharding.
- `struct ConversionInfo` exposes `UPDATE_CTIME`, constructor, `ToString`, `ConversionPath`, and static `parseConversionString`.
- Public const fields hold fid, target layout, target `GroupLocator`, placement policy, update-ctime flag, and app tag.

## Control Flow and State
The only inline logic is `ToString`, returning the private canonical conversion string. All semantic parsing/formatting is implemented in the `.cc`. Instances are effectively immutable after construction.

## Dependencies and Integration Points
Includes MGM namespace, `FileId`, `LayoutId`, and `FileSystem` for `GroupLocator`. `ConversionJob` takes a `ConversionInfo` by value and trusts its parsed fields.

## Risks
- Public const data fields make the type simple but lock in representation and force construction of whole new objects for any change.
- The documented format includes `[!]`, while implementation uses `+`; this can mislead callers.
- There is no escaping scheme for app tags or placement policies.

## Test Signals
Header-facing tests should verify construction from typed values, `ToString` consistency, public field values, and compile compatibility with converter and tag helper callers.
