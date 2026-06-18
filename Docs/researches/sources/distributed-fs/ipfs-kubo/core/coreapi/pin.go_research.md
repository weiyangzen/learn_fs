# sources/distributed-fs/ipfs-kubo/core/coreapi/pin.go

Purpose: implements CoreAPI pin add/list/check/remove/update/verify operations.

Important APIs/types/functions: `PinAPI`, methods `Add`, `Ls`, `IsPinned`, `Rm`, `Update`, `Verify`, helper `pinLsAll`, and output implementations `pinStatus`, `badNode`, and `pinInfo`.

Control flow: add resolves a node, parses recursive/name options, locks pin state, pins and flushes. Listing validates pin type then delegates to `pinLsAll`, which streams recursive/direct pins and optionally walks recursive DAGs to emit indirect pins while deduplicating. `IsPinned` resolves path and checks pin mode. Remove/update resolve paths, lock, mutate pinner, and flush. Verify builds an offline DAG service over the blockstore, recursively walks each recursive pin, memoizes visited CIDs, and streams status objects with bad node paths/errors.

State and persistence behavior: add/remove/update mutate pinner state and flush for durability. Listing/checking/verify are read-only, though verify can be expensive over local blockstore.

Dependencies and integration points: integrates CoreAPI resolution, pinner, blockstore pin locks, boxo merkledag walk, offline block exchange, and tracing.

Risks: `pinLsAll` requires callers to drain channels or goroutines can leak, as noted in comment. Recursive/indirect listing can be expensive and context-sensitive. Verify only checks recursive pins. Partial failures during walks return errors or bad nodes but do not repair.

Test signals: covered through CoreAPI interface tests; repo verify is a separate block-integrity command.
