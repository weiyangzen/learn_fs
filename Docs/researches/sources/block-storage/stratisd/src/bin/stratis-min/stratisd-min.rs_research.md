# File Research: sources/block-storage/stratisd/src/bin/stratis-min/stratisd-min.rs

Minimal daemon entry point for `stratisd-min`. It exposes `--log-level` and `--sim`, configures logging, locks PID files, and calls `stratisd::stratis::run()`.

Key behavior:
- Uses `/run/stratisd-min.pid` as its own nonblocking flock-guarded PID file.
- Also attempts to lock `/run/stratisd.pid` so full `stratisd` and `stratisd-min` do not run together.
- Writes its current PID into the min PID file after acquiring the lock.
- Uses explicit log-level filtering for the `stratisd` target, otherwise honors `RUST_LOG`.
- `--sim` selects the simulator engine via `run(args.get_flag("sim"))`.

Filesystem relevance:
- This is the minimal daemon used by initrd/rootfs setup paths.
- Locking prevents two Stratis engine instances from concurrently managing the same device state.

Testing:
- Includes `parse_args().debug_assert()` unit coverage.
