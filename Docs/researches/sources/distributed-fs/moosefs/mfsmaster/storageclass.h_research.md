# sources/distributed-fs/moosefs/mfsmaster/storageclass.h

## Purpose
`storageclass.h` defines the public storage-class policy surface for MooseFS master code, including the `storagemode` layout shared with chunk placement and client/admin serializers.

## Important APIs, Types, And Functions
`storagemode` contains unique-server mask, EC data/checksum byte, internal label/matching/counter fields, labels mode, label count, and label expression bytecode array. The header declares compatibility conversion helpers, EC version APIs, info/list serializers, class mutation and replay APIs, lookup/accessors, reference counters, mode getters, storage-size/goal helpers, policy attributes, persistence, cleanup, defaults, and initialization.

## Control Flow
Normal callers create or change classes through the non-`mr` functions so changes are changelogged. Restore calls the `sclass_mr_*` variants. Placement code obtains `storagemode *` pointers from the getter functions and should treat them as borrowed, possibly pointing to a shared temporary.

## State, Persistence, And Dependencies
The header includes `MFSCommunication.h` for class and label constants and `bio.h` for persistence. Internal state is held by `storageclass.c`.

## Integration Points
Filesystem, chunk placement, sessions/export checks, admin packet generation, restore, metadata load/store, and patterns all depend on this API.

## Risks
`storagemode` exposes internal fields such as matching-server and EC counters. External code can accidentally rely on or corrupt fields that are meant to be maintained by chunk labelset refresh code.

The declaration `sclass_is_predefined()` has no implementation in `storageclass.c`, indicating stale API drift unless another translation unit supplies it.

Changing `SCLASS_EXPR_MAX_SIZE`, `MAXLABELSCNT`, or struct layout affects metadata parsing, packet sizes, and compatibility code.

## Test Signals
Build/link checks should catch stale declarations. ABI-like tests should verify packet sizes and metadata round-trip behavior whenever `storagemode` or label constants change.
