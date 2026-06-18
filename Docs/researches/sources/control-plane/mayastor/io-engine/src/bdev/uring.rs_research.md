## sources/control-plane/mayastor/io-engine/src/bdev/uring.rs

### Purpose
`uring.rs` adapts files or block devices to SPDK io_uring bdevs via the generic URI API.

### Important APIs, Types, And Functions
`Uring` stores path/name, original URI alias, block size, and optional UUID. `TryFrom<&Url>` parses paths and query parameters. `GetName`, `CreateDestroy`, and `Probe` integrate with generic bdev management.

### Control Flow
Parsing rejects empty paths, detects whether the path is a block device, defaults block size to `0` for block devices and `512` for regular files unless `blk_size` is supplied, parses optional UUID, and rejects unknown parameters. `create()` rejects an existing bdev, fills `bdev_uring_opts` with filename/name, calls `create_uring_bdev()`, optionally sets UUID, adds the alias, and returns the bdev name. `destroy()` calls `delete_uring_bdev()` through a oneshot completion. `probe()` delegates to `probe_file()`.

### State, Persistence, And Dependencies
The SPDK uring bdev is runtime state only; data persistence depends on the backing file/block device. Dependencies include Unix file type inspection, SPDK uring FFI, `UntypedBdev`, URI helpers, UUID parsing, and callback helpers.

### Integration Points
This adapter is selected for uring URIs and is used wherever generic bdev creation can attach local files or block devices. Alias metadata allows later URI-to-bdev matching.

### Risks
For block devices, block size `0` delegates sizing to SPDK; for regular files the default is fixed 512, so caller expectations must match file layout. `CString::new(self.get_name()).unwrap()` will panic if a path contains NUL. Create failure returns `BdevNotFound`, which may hide the real SPDK failure reason.

### Test Signals
Cover regular file and block device defaults, explicit `blk_size`, UUID parsing, unknown parameters, probe_file outcomes, duplicate create, alias failure logging, create null pointer, destroy cancellation, and missing destroy target.
