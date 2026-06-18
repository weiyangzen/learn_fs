# Research: sources/distributed-fs/ipfs-kubo/config/internal.go

Purpose: Defines unstable/internal configuration knobs for MFS, shutdown, diagnostics, and Bitswap internals.

Important APIs/types/functions: Defaults include MFS no-flush limit, shutdown timeout, CGNAT check, and dead-listener check. `Internal` holds optional fields for Bitswap, UnixFS sharding migration, reachability, backup bootstrap, MFS no-flush, shutdown timeout, and diagnostic flags. `InternalBitswap` and `BitswapBroadcastControl` hold detailed Bitswap worker/search/broadcast tuning. Broadcast defaults are declared later in the file.

Control flow, state, and persistence: No functions except constants/types. These values are persisted only when set and interpreted by lower-level node subsystems. Many are experimental and may change.

Dependencies and integration points: Uses `time` and custom optional/flag types. `core/builder.go` consumes shutdown timeout through build config derived from internal config.

Risks and test signals: Internal options can destabilize networking or resource behavior. Removed/moved options are partly handled in `types.go`. `internal_test.go` covers default-enabled diagnostic flags and JSON omission/false decoding.
