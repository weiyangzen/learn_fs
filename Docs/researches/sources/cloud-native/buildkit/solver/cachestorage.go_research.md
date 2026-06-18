## sources/cloud-native/buildkit/solver/cachestorage.go

Purpose: declares the interfaces and small data records separating solver cache metadata from actual result storage.

Important APIs/types/functions: `ErrNotFound` is the storage not-found sentinel. `CacheKeyStorage` defines key existence, walking, result metadata, release, forward links, and backlinks. `CacheResult` stores result id and creation time. `CacheInfoLink` describes a dependency link by input index, output index, operation digest, and selector. `CacheResultStorage` saves/loads concrete `Result`s, loads remote descriptors, and checks existence.

Control flow: none; pure contracts.

State and persistence: implementations persist metadata and result payloads separately. `CacheInfoLink` JSON tags define on-disk encoding in bbolt storage.

Dependencies and integration points: implemented by bbolt/in-memory stores and consumed by `cacheManager`. `LoadRemotes` integrates session groups and compression config for remote cache/export operations.

Risks and test signals: interface changes have broad impact. The `CacheInfoLink` JSON representation is part of persistent bbolt key encoding. Shared storage tests validate implementations.
