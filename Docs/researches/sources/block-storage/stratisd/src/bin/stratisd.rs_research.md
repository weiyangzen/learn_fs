# File Research: sources/block-storage/stratisd/src/bin/stratisd.rs

Primary `stratisd` daemon entry point.

Key behavior:
- Defines `--sim` and `--log-level`.
- Acquires `/run/stratisd.pid` with nonblocking flock, writes current PID, and errors if another full daemon is running.
- Checks `/run/stratisd-min.pid`; if locked by `stratisd-min`, reads its PID, sends `SIGINT`, and waits for the lock to release.
- Configures logging for `stratisd` from explicit log level or `RUST_LOG`.
- Calls `stratisd::stratis::run(sim)` and exits with process status `0` or `1`.

Filesystem relevance:
- The lock handoff from `stratisd-min` to full `stratisd` avoids concurrent block-device ownership during boot transition.
- PID-file handling is part of daemon exclusivity for pool/device management.

Testing:
- Includes `parse_args().debug_assert()`.
