# File Research: sources/block-storage/thin-provisioning-tools/src/commands/engine.rs

Shared I/O engine option parsing and `IoEngine` construction for commands.

Core types:
- `EngineType`: `Sync`, `Spindle`, and optionally `Async` under `io_uring`.
- `ToolType`: `Thin`, `Cache`, `Era`, `Other`.
- `EngineOptions`: tool type, engine type, and metadata snapshot flag.
- `EngineBuilder`: path, options, write flag, and exclusive-open flag.

Behavior:
- Adds hidden `--io-engine` CLI option.
- Parses `sync`, `spindle`, and conditionally `async`.
- Enables `use_metadata_snap` only for thin/era tools when the command has metadata snapshot option present on command line.
- For thin spindle mode, computes valid metadata blocks from the thin metadata space map, falling back to all blocks if reading fails.
- Cache and era spindle valid-block helpers are `todo!()`, so selecting spindle engine for those tool types will panic if reached.
- Builds `SyncIoEngine`, `AsyncIoEngine`, or `SpindleIoEngine`.

Notable detail: `thin_valid_blocks` uses a sync engine independently to inspect metadata allocation even when the final engine type is spindle.
