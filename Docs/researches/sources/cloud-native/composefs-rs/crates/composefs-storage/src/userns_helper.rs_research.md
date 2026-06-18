# sources/cloud-native/composefs-rs/crates/composefs-storage/src/userns_helper.rs

Purpose: Implements a JSON-RPC plus fd-passing helper for rootless storage access. Parent processes spawn themselves through `podman unshare`; the child enters helper mode, opens otherwise unreadable files or storage layers, and returns file descriptors over a Unix socket.

Important APIs and types: Public request/result structs cover `openFile`, `listImages`, `getImage`, and `streamLayer`. `HelperError` wraps spawn, IPC, I/O, and RPC failures. `init_if_helper` is the required early-main entry point. `StorageProxy` manages child process lifecycle and RPC calls. `ProxiedLayerStream` yields `ProxiedTarSplitItem::{Segment, FileContent}` from streaming notifications.

Control flow: `StorageProxy::spawn` skips helper creation when `userns::can_bypass_file_permissions` returns true. Otherwise `spawn_helper_with_binary` creates a socketpair, runs `podman unshare env __CSTORAGE_USERNS_HELPER=1 <exe>`, and wires the child stdin to the socket. In helper mode, `init_if_helper` duplicates stdin, installs a parent-death signal, creates a current-thread Tokio runtime, and enters `run_helper_loop_async`. Requests are decoded with `jsonrpc_fdpass`; normal methods send one response, while `streamLayer` sends multiple `stream.segment` or `stream.file` notifications and a final response.

State and persistence: Runtime state is the child process, socket transport halves, monotonically increasing JSON-RPC ids, and stream completion flag. It reads containers-storage state through `Storage`, `Image`, `Layer`, and `TarSplitFdStream`; it does not persist mutations. `Drop` kills the child if still running.

Dependencies and integration: Integrates `podman`, `/proc/self/exe`, Unix socket fd passing via `jsonrpc_fdpass`, Tokio Unix streams, `rustix` fd/process helpers, and composefs-storage image/layer/tar-split modules. It is the privileged access path for APIs that need rootless overlay contents with restrictive permissions.

Risks: `podman` must be installed and `init_if_helper` must be called early by binaries using the library. `Drop` is forceful and may kill a helper with in-flight work. `openFile` opens arbitrary absolute paths passed by the parent, so caller trust boundaries matter. Streaming assumes ordered notifications on a single receiver; concurrent RPCs while streaming would need careful sequencing. Several `serde_json::to_value(...).unwrap()` calls can panic only if serialization of internal structs fails, but fuzzing does not cover this module.

Test signals: No local unit tests are visible in this file. Practical coverage should include helper spawn failure, graceful shutdown, fd-passing round trips, malformed RPC messages, stream ordering, and rootless integration with actual containers-storage.
