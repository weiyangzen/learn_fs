# sources/distributed-fs/ceph-client/fs/xfs/scrub/orphanage.h

## Purpose
`orphanage.h` declares the repair-facing orphanage and adoption interface and provides stubs when online repair is disabled.

## Important APIs, Types, And Functions
With `CONFIG_XFS_ONLINE_REPAIR`, it declares orphanage creation, lock helpers, reference release, adoption transaction allocation, name computation, move, and transaction roll functions. `xrep_orphanage_try_create` wraps creation and suppresses nonfatal orphanage unavailability errors. `struct xrep_adoption` carries the scrub context, chosen name, parent-pointer args, block reservations, and whether the child link count should be bumped.

## Control Flow
The inline `xrep_orphanage_try_create` asserts repair mode, calls `xrep_orphanage_create`, and treats `-ENOENT`, `-ENOTDIR`, and `-ENOSPC` as nonfatal because callers can still perform repairs that do not require adoption.

## State And Persistence Behavior
The header itself has no persistence. The adoption object is per-operation mutable state consumed by `orphanage.c`.

## Dependencies And Integration Points
It depends on scrub context, XFS parent args, and repair configuration. Nlink and parent repairs use this API to reconnect disconnected files.

## Risks And Edge Cases
The stub `struct xrep_adoption` is empty when online repair is disabled, so callers must be behind repair configuration guards. Nonfatal orphanage creation failures intentionally degrade repair capability rather than failing all setup.

## Test Signals
Compile coverage should include online repair enabled and disabled. Runtime tests should confirm callers handle `xrep_orphanage_can_adopt` false after suppressed setup errors.
