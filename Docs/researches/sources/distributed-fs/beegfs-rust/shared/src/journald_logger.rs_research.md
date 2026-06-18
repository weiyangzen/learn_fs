## sources/distributed-fs/beegfs-rust/shared/src/journald_logger.rs

### Purpose
Implements a `log` crate backend that sends structured log records directly to the systemd journal socket.

### Important APIs, Types, and Functions
- `JournaldLogger` stores a connected Unix datagram socket and a `LevelFilter`.
- `init(level_filter)` connects to `/run/systemd/journal/socket`, installs the boxed logger, and sets the max log level.
- `impl Log for JournaldLogger` filters records, formats journald fields, encodes `MESSAGE` as a binary field with little-endian length, and sends via Unix datagram.
- `level_to_priority` maps Rust log levels to syslog priorities: error `3`, warn `4`, info `5`, debug `6`, trace `7`.

### Control Flow and State
After initialization, logging is synchronous per record: build a buffer and send it through the socket. State is only the socket and max level.

### Dependencies and Integration Points
Uses `log`, `std::os::unix::net::UnixDatagram`, and systemd journald's native socket protocol. Exposed by `lib.rs` for BeeGFS Rust daemons.

### Risks and Edge Cases
Hard-coded `SYSLOG_IDENTIFIER=beegfs-mgmtd` makes the logger less reusable for non-management binaries. Send failures are printed to stderr, which may be unavailable or noisy in daemon contexts. `init` fails on non-systemd systems or if journald socket is absent. Message size is not capped locally.

### Test Signals
No tests. Unit tests could cover priority mapping; integration tests would need a fake Unix datagram receiver or journald socket abstraction.
