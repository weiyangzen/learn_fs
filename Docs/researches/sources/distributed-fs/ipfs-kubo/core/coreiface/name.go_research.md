# sources/distributed-fs/ipfs-kubo/core/coreiface/name.go

## Purpose
Defines CoreAPI IPNS publishing and resolution contracts.

## Important APIs, Types, and Functions
Defines `ErrResolveFailed`, `IpnsResult`, and `NameAPI` methods `Publish` and `Resolve`.

## Control Flow and State
No implementation appears here. The interface requires publishing signed paths under self or selected keys and resolving mutable names back to paths with options controlling cache/depth/validity behavior.

## Dependencies and Integration Points
Depends on context, Boxo IPNS/path, and name options. It integrates with KeyAPI identities, routing value stores, and namesys.

## Risks and Test Signals
Risks include expired records resolving from cache, path suffix preservation, offline/delegated publish semantics, and key selection. Tests cover publish/resolve with self and generated keys, suffix resolution, cache off, and record expiry.
