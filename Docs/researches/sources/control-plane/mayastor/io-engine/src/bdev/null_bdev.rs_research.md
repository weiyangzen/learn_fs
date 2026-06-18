## sources/control-plane/mayastor/io-engine/src/bdev/null_bdev.rs

### Purpose
`null_bdev.rs` implements the URI-backed SPDK null bdev adapter. It creates in-memory/discard devices for tests and benchmarks, with all writes discarded and read data undefined.

### Important APIs, Types, And Functions
`Null` stores name, alias URI, block count, block size, and optional UUID. `TryFrom<&Url>` parses `null:///name` URIs with `blk_size`, `size_mb`, `size`, `num_blocks`, and `uuid`. `GetName`, `Probe`, and `CreateDestroy` integrate it with the generic bdev URI API.

### Control Flow
URI parsing rejects empty paths, mutually exclusive size forms, invalid block sizes other than 512 or 4096, bad integers, bad byte-unit values, bad UUIDs, and unknown parameters. `create()` rejects existing bdev names, builds `null_bdev_opts`, calls `bdev_null_create()`, then looks up the bdev, optionally overwrites its UUID, and adds the original URI as an alias. `destroy()` looks up the bdev by name and calls `bdev_null_delete()` through a oneshot completion.

### State, Persistence, And Dependencies
State is not persisted; created devices live in SPDK until destroyed. The alias preserves the original URI for later matching. Dependencies include SPDK null bdev FFI, `UntypedBdev`, URI helpers, `reject_unknown_parameters`, byte-unit parsing, UUID parsing, and async callback helpers.

### Integration Points
This driver is selected by URI parsing and is useful for benchmarking the I/O stack without backing storage. It participates in generic `bdev_create`, `bdev_destroy`, and bdev alias matching.

### Risks
`create()` generates an SPDK UUID and then optionally overrides it with the requested UUID after creation, so failures between those steps leave a valid but differently identified bdev. The `num_blocks` parse error labels the parameter as `blk_size`, which can mislead users. A zero size and zero `num_blocks` is accepted and creates a zero-block null device.

### Test Signals
Cover size versus size_mb versus num_blocks parsing, block-size validation, UUID aliasing, unknown-parameter rejection, duplicate create, destroy missing bdev, callback cancellation, zero-size behavior, and alias-based URI lookup.
