# sources/distributed-fs/ipfs-kubo/core/coreiface/options/key.go

## Purpose
Builds settings for key generation and key rename operations.

## Important APIs, Types, and Functions
Defines key algorithm constants `RSAKey`, `Ed25519Key`, `DefaultRSALen`, settings structs, option function types, `KeyGenerateOptions`, `KeyRenameOptions`, `Key` namespace, and option methods `Type`, `Size`, and `Force`.

## Control Flow and State
Generate defaults to RSA with implementation-selected size (`-1`). Rename defaults to no overwrite. Option functions simply mutate settings; validation is expected in the implementation.

## Dependencies and Integration Points
No external package dependencies. Consumed by KeyAPI implementations and conformance tests.

## Risks and Test Signals
Risks include accepting unsupported algorithms/sizes too late, self-key overwrite/remove protection, and force semantics. Tests cover size, type, existing-name errors, rename overwrite, and self restrictions.
