# sources/distributed-fs/ipfs-kubo/core/commands/name/ipns.go

## Purpose

`name/ipns.go` implements `ipfs name resolve`, resolving IPNS and DNSLink names to IPFS paths. It supports recursive or one-step resolution, DHT resolver tuning, cache control, and streaming intermediate search results.

## Important APIs, Types, and Functions

`IpnsCmd` emits `ResolvedPath`. Options are `recursive`, `nocache`, `dht-record-count`, `dht-timeout`, and `stream`. It uses `api.Name().Resolve` for final resolution and `api.Name().Search` for streaming. Resolver options are built with `namesys.ResolveWithDepth`, `ResolveWithDhtRecordCount`, and `ResolveWithDhtTimeout`.

## Control Flow

The command gets CoreAPI, chooses the requested name or defaults to `api.Key().Self().ID()`, builds name-resolution options from flags, validates non-negative DHT timeout, and prefixes bare names with `/ipns/`. Non-stream mode calls `Resolve`, tolerating `namesys.ErrResolveRecursion` only when the user requested non-recursive behavior, normalizes the result through `path.NewPath`, and emits once. Stream mode calls `Search`, iterates result events, applies the same recursion-error rule, and emits each resolved path.

## State and Persistence Behavior

The command is read-only. It may use or bypass resolver caches depending on `nocache`; online resolution can use DHT and DNSLink sources via the name system. Streaming mode holds a live resolver channel until completion or cancellation.

## Dependencies and Integration Points

Dependencies include Boxo `namesys` and `path`, Kubo CoreAPI name/key interfaces, command environment helpers, and Go duration parsing. It integrates with `name publish`, `name put/get`, IPNS pubsub, and key management through peer IDs and IPNS names.

## Risks and Test Signals

Risks include long DHT timeouts, recursion behavior confusion, accepting both bare and `/ipns/` inputs, and partial stream results when later resolution fails. Tests should cover default self-name lookup, cache flag inversion, recursive false depth-one behavior, DHT count/timeout validation including zero and negative values, stream and non-stream error handling, DNSLink inputs, and output path normalization.
