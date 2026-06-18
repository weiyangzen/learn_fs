# sources/cloud-native/nydus/src/bin/nydusctl/commands.rs

## Purpose
`commands.rs` implements the high-level `nydusctl` operations: daemon info/configuration, backend/cache/filesystem metrics, mount, and umount. It turns CLI context maps into `NydusdClient` API calls and formats responses for humans or raw JSON.

## Important APIs, Types, And Functions
`CommandParams` is a string map for parsed CLI context. `load_param_interval` parses optional metric polling intervals. `CONFIGURE_ITEMS_MAP` maps user-facing configuration keys such as `log-level` to daemon API keys such as `log_level`. Command structs are `CommandCache`, `CommandBackend`, `CommandFsStats`, `CommandDaemon`, `CommandMount`, and `CommandUmount`. Helpers `metric_delta` and `metric_vec_delta` compute saturating counter deltas for interval mode.

## Control Flow
`CommandCache::execute` gets blobcache metrics and prints prefetch/cache data. `CommandBackend::execute` gets backend metrics; with `interval`, it loops forever, sleeps, fetches new metrics, computes deltas, and prints bandwidth/latency distributions; without interval, it prints cumulative stats. `CommandFsStats` prints global FUSE/read operation metrics. `CommandDaemon` either PUTs mapped configuration JSON or GETs daemon info and backend collection details. `CommandMount` reads a config file, builds an `ApiMountCmd` JSON payload, and POSTs it with a mountpoint query. `CommandUmount` DELETEs the mount endpoint with a mountpoint query.

## State And Persistence
The module persists no local state. It changes daemon state through API calls: log-level updates, dynamic mount, and dynamic umount. Interval backend metrics keep only the previous JSON sample in memory.

## Dependencies And Integration Points
It depends on `NydusdClient`, shared `nydus` API types (`FsBackendDescriptor`, `FsBackendType`), JSON response shapes from `nydusd`, and `std::thread::sleep`. It is called by `nydusctl/main.rs` after Clap parsing.

## Risks
The human-format paths use many `unwrap` calls on JSON fields and array lengths, so daemon API schema drift or partial metrics can panic. `--interval 0` is accepted by parser/tests and causes a tight polling loop. `metric_vec_delta` intentionally panics on mismatched vector lengths. `CommandMount` uses `std::fs::read_to_string(...).unwrap()`, so a missing config file panics rather than returning `anyhow`. Query values are not URL encoded by the client.

## Test Signals
Unit tests cover interval parsing, overflow rejection, configuration-key mapping, scalar and vector metric deltas, counter reset saturation, empty vectors, and mismatched vector panic. API integration, real mount/umount, formatting over full daemon payloads, and zero-interval behavior need higher-level tests.
