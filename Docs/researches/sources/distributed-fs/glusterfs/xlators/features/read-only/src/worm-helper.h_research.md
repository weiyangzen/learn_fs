# sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm-helper.h

## Purpose
`worm-helper.h` declares the WORM retention helper API used by the WORM translator.

## Important APIs and Types
- Declares write-bit check, state initialization, state get/set, state lookup/transition, serialization/deserialization, xattr setter, and `is_wormfile()`.
- Uses `worm_reten_state_t`, `xlator_t`, `fd_t`, `loc_t`, `struct iatt`, and `glusterfs_fop_t` types from included translation units.

## Control Flow
No executable flow. It exposes the helper contract consumed by `worm.c`.

## State and Persistence
The APIs operate on trusted xattrs (`trusted.start_time`, `trusted.reten_state`, `trusted.worm_file`) and retention timestamps, but the header itself stores no state.

## Dependencies and Integration Points
Included by both `worm.c` and `worm-helper.c`. Prototype changes must remain aligned with syncop-based helper implementation and WORM FOP wrappers.

## Risks
The header lacks include guards and explicit includes in the inspected file, relying on include order from callers. That can cause duplicate declarations or missing type failures if included in a different context.

## Test Signals
Build coverage from `worm.c` and `worm-helper.c`; adding an include guard would be a low-risk robustness improvement if the project permits functional-neutral changes.
