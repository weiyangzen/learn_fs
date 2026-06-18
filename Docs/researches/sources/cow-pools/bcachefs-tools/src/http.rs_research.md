# File Research: sources/cow-pools/bcachefs-tools/src/http.rs

Starts a per-process tiny HTTP server over a Unix socket to expose bcachefs userspace sysfs/debugfs content.

Core behavior:
- `bch2_start_http_lazy` is `#[no_mangle]` and called from C-side debugfs/kobject shims.
- Chooses `/run/bcachefs/<pid>.sock` for root or `$XDG_RUNTIME_DIR/bcachefs/<pid>.sock` / `/run/user/<uid>/bcachefs/<pid>.sock` for non-root.
- Spawns a server thread using `tiny_http::Server::http_unix`.
- GET requests call C `sysfs_read_or_html_dirlist` into a `Printbuf`; failures return HTTP 403.
- Non-GET requests return HTTP 405.

Fork/exit handling:
- Tracks the PID that started the server so forked children can start a new socket.
- Registers `pthread_atfork` child handler to call startup after fork.
- Registers `atexit` cleanup to remove the current PID socket.
- Uses a mutex and atomics to keep initialization idempotent per process.

Potential concerns:
- URL handling uses `split_once('/').unwrap()`, so a malformed URL without `/` would panic, although HTTP request URLs normally include a leading slash.
- Socket bind failure is printed but not returned to callers.
- Stale sockets after crashes are intentionally not removed automatically.
