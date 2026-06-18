# sources/distributed-fs/ipfs-kubo/core/coreiface/options/name.go

## Purpose
Builds IPNS publish and resolve option settings.

## Important APIs, Types, and Functions
Defines `DefaultNameValidTime`, `NamePublishSettings`, `NameResolveSettings`, option types, `NamePublishOptions`, `NameResolveOptions`, `Name` namespace, and methods for valid time, key, offline/delegated publishing, TTL, sequence, v1 compatibility, cache, and raw namesys resolve options.

## Control Flow and State
Publish defaults to 24h validity, key `self`, and no offline/delegated publishing. Resolve defaults to cache enabled. Options append or override fields; implementations consume TTL/sequence pointers to distinguish unset from zero.

## Dependencies and Integration Points
Depends on time and Boxo namesys options. It connects NameAPI to KeyAPI and routing/namesys implementations.

## Risks and Test Signals
Risks include zero TTL/sequence pointer semantics, cache use after expiry, and differences between offline and delegated publishing. Tests cover custom keys, cache disabled, suffix resolution, and expiry.
