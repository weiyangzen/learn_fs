<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/bdev.rs -->
## sources/control-plane/mayastor/io-engine/src/core/bdev.rs

### Purpose
`core/bdev.rs` wraps `spdk_rs::Bdev` in io-engine core types. It provides lookup/open/stat/share/unshare behavior, bdev iteration, display/debug formatting, and a `BdevStater` abstraction for I/O statistics.

### Important APIs, Types, And Functions
`Bdev<T>` is a newtype over `spdk_rs::Bdev<T>`, with `UntypedBdev` as `Bdev<()>`. Key methods include `checked_from_ptr`, `open_by_name`, `open`, `lookup_by_name`, `get_by_name`, `lookup_by_uuid_str`, `driver`, `bdev_first`, `get_tick_rate`, `stats_async`, `stats_errors_async`, and stats reset functions. The file implements the `Share` trait for `Bdev<T>`, defines `is_shared`, `BdevIter`, `BdevStater`, `BdevErrorStats`, and `BdevStats`.

### Control Flow
Lookup methods wrap SPDK global bdev lookup and iteration. Opening creates a `BdevDesc` with `bdev_event_callback` and wraps it in `DescriptorGuard`. Stats methods await SPDK async stats and convert them to core structs, using `spdk_get_ticks_hz` for tick rate. Sharing builds an `NvmfSubsystem` from the bdev, applies PTPL path, controller ID range, ANA reporting, host access policy, and allowed hosts, then starts the subsystem. Updating share properties adjusts allowed-host state for existing NVMf subsystems. Unshare stops the NVMf subsystem if present. URI helpers recover original bdev URIs from aliases and append UUID when missing.

### State, Persistence, And Dependencies
The wrapper holds SPDK bdev handles but does not own bdev lifetime. It changes NVMf subsystem state during share/unshare and reads bdev aliases, stats, claims, and module names. Dependencies include `spdk_rs`, `nix::errno`, `async_trait`, `snafu`, `NvmfSubsystem`, NVMf target URI helpers, share property types, and bdev URI comparison.

### Risks And Test Signals
`checked_from_ptr` relies on unsafe pointer wrapping. `stats_errors_async` expects error stats to be present after requesting them. `shared` returns `Some(Off)` instead of `None` for unshared bdevs, so callers must handle both. NVMf sharing depends on global subsystem lookup by bdev name. Tests should cover lookup/open failures, descriptor guard drop behavior through callers, share/unshare allowed-host updates, URI alias matching, stats conversion, error-count filtering, and iteration over global bdevs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/bdev.rs -->
