# sources/cloud-native/nydus/upgrade/src/backend/unix_domain_socket.rs

Purpose: implements `StorageBackend` by transferring state bytes and file descriptors over a Unix domain socket.

Important APIs/types/functions: `UdsStorageBackend` stores `socket_path: PathBuf`. `new` constructs it. `MAX_STATE_DATA_LENGTH` is 32 KiB. `save` connects to the socket and calls `send_with_fd(data, fds)`. `restore` connects, allocates a fixed 32 KiB byte buffer and 16-fd array, then calls `recv_with_fd`.

Control flow: `save` rejects an empty fd slice before connecting, then returns the number of bytes sent. `restore` reads one message with fds, truncates the fd vector to the returned fd count, and returns fds with the data buffer.

State and persistence: no local durable state; persistence is delegated to the peer listening on `socket_path`. Fds are passed through SCM_RIGHTS via the `sendfd` crate. State data is transient bytes.

Dependencies and integration points: depends on `sendfd::{SendWithFd, RecvWithFd}` and `std::os::unix::net::UnixStream`. Implements the backend trait from `upgrade/src/backend/mod.rs`.

Risks: `restore` checks `if fds.is_empty()` before truncating, but the preallocated fd vector has length 16, so a zero-fd receive will not be rejected; it should likely check `fds_cnt`. It also returns the full 32 KiB data buffer rather than truncating to the actual byte count returned by `recv_with_fd`, so callers may see trailing zeroes as state. `save` requires at least one fd, which may preclude data-only upgrade state. Fixed fd capacity of 16 and data capacity of 32 KiB are hard limits.

Test signals: tests cover constructor path storage, empty-fd save error, invalid socket save connect error, and invalid socket restore connect error. There is no loopback socket test validating successful fd/data transfer or received-length truncation.
