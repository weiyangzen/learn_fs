# Research: sources/distributed-fs/ipfs-kubo/config/provider.go

Purpose: Deprecated legacy provider configuration kept for compatibility.

Important APIs/types/functions: `Provider` has deprecated `Enabled`, `Strategy`, and `WorkerCount` fields, with comments pointing to `Provide`.

Control flow, state, and persistence: No functions. Fields may still decode from old config but should be migrated or ignored in favor of `Provide`.

Dependencies and integration points: Top-level `Config` includes both legacy `Provider` and new `Provide`. Migration/compatibility code outside this file handles mapping.

Risks and test signals: Dual legacy/new config can confuse operators. No direct tests in this subset.
