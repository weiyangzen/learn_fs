# sources/cloud-native/ostree/rust-bindings/src/auto/async_progress.rs

Purpose: Generated Rust wrapper for `OstreeAsyncProgress`, exposing progress state used by asynchronous libostree operations.

Important APIs: `AsyncProgress::new`, `copy_state` behind `v2019_6`, `finish`, getters for `status`, `uint`, `uint64`, and `variant`, setters for status/integers/variant values, and `connect_changed` for the `changed` signal. Varargs C APIs `get` and `set`, and `new_and_connect`, are left commented as unimplemented.

Control flow and state: The object stores mutable progress key/value state in the underlying GObject. Rust methods translate strings, variants, and numeric values across FFI. `connect_changed` boxes a Rust closure and registers a C trampoline through `connect_raw`.

Dependencies and integration points: Depends on `glib`, `gio` conventions, `ffi::ostree_async_progress_*`, feature gates, and signal handling. It is used by pull, checkout, and other async APIs to observe or propagate progress.

Risks: Signal connection uses unsafe trampoline plumbing and boxed closure ownership; leaks or invalid callbacks would be serious. Key names are stringly typed and not validated here. Varargs APIs are unavailable, so callers only get typed helper coverage.

Test signals: Compile under base and version features, connect a changed handler, set/get typed values, call `finish`, and validate `copy_state` under `v2019_6`.
