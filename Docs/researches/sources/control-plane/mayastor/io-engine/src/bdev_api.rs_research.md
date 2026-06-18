## sources/control-plane/mayastor/io-engine/src/bdev_api.rs

### Purpose
`bdev_api.rs` provides the generic URI-facing bdev create/destroy/name/equality API and central error type shared by URI adapters.

### Important APIs, Types, And Functions
`BdevError` enumerates URI parse, unsupported scheme, invalid parameter, duplicate/missing bdev, create/destroy/resize failures, canceled commands, and wipe failure. `ToErrno for BdevError` maps errors to `nix::Errno`. Public functions are `bdev_create()`, `bdev_destroy()`, `bdev_get_name()`, `bdev_uri_eq()`, and `bdev_url_eq()`. `TryFrom<Bdev<T>> for Url` extracts a bdev URI.

### Control Flow
Create/destroy/name parse the URI through `bdev::uri::parse()` and dispatch trait methods on the resulting adapter. URI equality parses the provided URL, compares parsed device name to the bdev name, then compares bdev driver against the URI scheme with NVMe-family schemes normalized to `"nvme"`. Conversion from bdev to URL asks the bdev for its stored URI and reports aliases when none match.

### State, Persistence, And Dependencies
No state is stored here. It depends on adapter registry/parsing in `bdev::uri`, core `Bdev`, `Share` import, `ToErrno`, `snafu`, `url`, and lower-level parse errors.

### Integration Points
CLI tools, control-plane handlers, tests, and nexus child creation use this as the top-level URI bdev API. The error type is used by many adapter files for consistent user-facing diagnostics.

### Risks
`BdevExists` maps to `ENOENT`, which is counterintuitive and may affect API consumers. `bdev_uri_eq()` and `bdev_url_eq()` are duplicate implementations. Scheme normalization must stay aligned with every URI adapter. String-based errors map to `EPERM`, which may be too generic.

### Test Signals
Cover every `ToErrno` mapping, parse dispatch for create/destroy/name, unsupported schemes, equality for nvmf/nvmf+tcp/nvmf+rdma+tcp/pcie mapping to nvme, alias extraction failure, and duplicate behavior of the two equality functions.
