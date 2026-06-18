# Research: sources/distributed-fs/ipfs-kubo/config/reprovider.go

Purpose: Deprecated legacy reprovider configuration kept for compatibility.

Important APIs/types/functions: `Reprovider` has deprecated `Interval` and `Strategy` fields pointing to `Provide.DHT.Interval` and `Provide.Strategy`.

Control flow, state, and persistence: No functions. Fields may decode old configs but should not be the primary source of truth in new configs.

Dependencies and integration points: Top-level `Config` keeps `Reprovider` alongside unified `Provide`.

Risks and test signals: Legacy/new duplication can produce migration ambiguity. No direct tests in this subset.
