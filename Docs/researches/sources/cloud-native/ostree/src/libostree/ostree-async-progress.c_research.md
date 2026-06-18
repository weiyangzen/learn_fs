# sources/cloud-native/ostree/src/libostree/ostree-async-progress.c

Purpose: This C file implements `OstreeAsyncProgress`, a thread-safe GObject used by asynchronous libostree operations to publish progress key/value state and emit coalesced change notifications in the caller's thread-default `GMainContext`.

Important APIs, types, and functions: The object stores `GMutex lock`, `GMainContext *maincontext`, `GSource *idle_source`, `GHashTable *values`, and `gboolean dead`. Public APIs include `ostree_async_progress_new`, `new_and_connect`, `get_variant`, `get_uint`, `get_uint64`, varargs `get`, `set_status`, `get_status`, varargs `set`, `set_variant`, `set_uint`, `set_uint64`, `copy_state`, and `finish`. Class setup registers the `changed` signal. `ensure_callback_locked` creates and attaches an idle source; `idle_invoke_async_progress` clears the source and emits `changed`.

Control flow: Setters lock the object, ignore updates after `dead`, compare new `GVariant` values to existing values, replace only changed entries, and schedule one idle callback for one or more changes. The idle callback runs in the captured main context and emits `changed`. Getters lock and either ref/copy variants or atomically unpack multiple varargs values. `finish` marks the object dead, destroys pending idle source, and emits one final `changed` if a callback was pending.

State and persistence behavior: State is in-memory only and scoped to the progress object. Keys are interned to `GQuark` pointers in the hash table and values are owned `GVariant` refs. No disk persistence occurs, but progress state influences UI/CLI feedback and async operation observers.

Dependencies and integration points: Depends on GLib/GObject, `config.h`, `ostree-async-progress.h`, and `libglnx` hash iteration macros. It is exposed through the public C API and raw Rust FFI declarations in `sys/src/lib.rs`. Repo pull and other asynchronous operations accept `OstreeAsyncProgress *`.

Risks: Varargs APIs require exact key/format/value sequences and NULL termination; misuse can assert or corrupt reads. `ostree_async_progress_get` asserts keys exist and formats match, so callers must know state shape. Thread safety depends on holding the mutex around hash table access and careful idle source lifetime management. Calling `copy_state` does not notify destination watchers by design, which can surprise consumers.

Test signals: No direct test in this subset, but Rust FFI ABI layout checks include `OstreeAsyncProgressClass`, and higher-level pull/progress tests elsewhere should validate signal behavior and status values.
