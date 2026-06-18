# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_debug.c

## Purpose

`gnilnd_debug.c` centralizes verbose debug formatting for GNI LNet driver messages, connections, transmit descriptors, and unexpected GNI API return codes. It exists so macros in the rest of gnilnd can emit consistent, high-context diagnostic records without duplicating formatting logic.

## Important APIs, Types, And Functions

- `_kgnilnd_debug_msg(kgn_msg_t *msg, struct libcfs_debug_msg_data *msgdata, const char *fmt, ...)` logs a caller-supplied prefix plus message pointer, magic, version, type, checksums, payload length, sequence number, and type string.
- `_kgnilnd_debug_conn(kgn_conn_t *conn, struct libcfs_debug_msg_data *msgdata, const char *fmt, ...)` logs a connection pointer, peer NID, connection state, CQID, timeout, RX/TX sequence/timing data, NOOP timing data, scheduler timing data, and device scheduler liveness.
- `_kgnilnd_debug_tx(kgn_tx_t *tx, struct libcfs_debug_msg_data *msgdata, const char *fmt, ...)` logs a TX pointer, peer NID, event/cookie IDs, message type, buffer type, message sequence, list state, queue age, flags, and retransmit count.
- `_kgnilnd_api_rc_lbug(const char *rcstr, int rc, struct libcfs_debug_msg_data *msgdata, const char *fmt, ...)` logs an unexpected GNI API return code and then calls `LBUG()`.

All functions use kernel `va_list` plus `struct va_format` and pass formatting through `libcfs_debug_msg()`.

## Control Flow

Callers pass an already populated `libcfs_debug_msg_data` and an optional formatted prefix. Each helper starts a variadic argument list, wraps it in `va_format`, emits one `libcfs_debug_msg()` record with driver-specific fields, and then ends the argument list. `_kgnilnd_api_rc_lbug()` additionally crashes through `LBUG()` after logging.

## State And Persistence Behavior

The file does not mutate protocol state except for reading live fields from `kgn_msg_t`, `kgn_conn_t`, and `kgn_tx_t`. It does not persist data; output goes to Lustre/libcfs debug logging. Values such as `jiffies` deltas and atomics are snapshots and may race benignly with live driver activity.

## Dependencies And Integration Points

This file depends on `gnilnd.h` for driver structures and stringification helpers such as `kgnilnd_msgtype2str()`, `kgnilnd_conn_state2str()`, and `kgnilnd_tx_state2str()`. It depends on libcfs debug infrastructure, Linux variadic formatting, atomics, `jiffies`, and `cfs_duration_sec()`.

The functions are normally reached through local debug macros (`GNIDBG_MSG`, `GNIDBG_CONN`, `GNIDBG_TX`, and API return-check wrappers) used throughout `gnilnd_cb.c`, `gnilnd_conn.c`, and related files.

## Risks And Edge Cases

- Debug helpers assume non-NULL `msg`/`tx`/`conn` for most field accesses. `_kgnilnd_debug_conn()` tolerates a NULL peer pointer, and `_kgnilnd_debug_tx()` tolerates missing connection/peer for the NID string, but not a NULL TX itself.
- Because the code reads live connection/TX fields without taking their locks, output can be internally inconsistent during heavy races. It is diagnostic, not an invariant snapshot.
- `_kgnilnd_api_rc_lbug()` is intentionally fatal. It should only wrap API return codes that the driver genuinely cannot recover from.
- The message debug helper has a TODO for union-specific payload detail; current output identifies type and common header only.

## Test Signals

- Build tests should verify format strings match argument types across supported kernels, especially `%pV`, `%px`/`%p`, `%llu`, and atomic/jiffies-derived fields.
- Runtime debug tests can force representative TX, RX, connection timeout, and API error paths and confirm logs include NID, state, sequence, age, and cookie fields needed to trace a failed transaction.
- Fatal-path testing should only use controlled fail injection to ensure `_kgnilnd_api_rc_lbug()` is not reachable from recoverable GNI return codes.
