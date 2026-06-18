## sources/cloud-native/moby/daemon/libnetwork/osl/neigh_unsupported.go

Purpose: non-Linux stub for the internal neighbor option storage type.

Important APIs/types/functions: build-tagged empty `neigh` type.

Control flow: no behavior. It enables shared option type declarations to compile without Linux neighbor implementation.

State and persistence behavior: none.

Dependencies and integration points: pairs with `sandbox.go` `NeighOption` and Linux-only option functions.

Risks: neighbor operations are unavailable on unsupported platforms; build tags must prevent Linux-only methods from being referenced.

Test signals: build coverage only.
