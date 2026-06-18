# sources/cloud-native/ostree/rust-bindings/src/auto/content_writer.rs

Purpose: Generated wrapper for `OstreeContentWriter`, a `gio::OutputStream` subclass used to write OSTree content and finish with a checksum.

Important APIs: The wrapper extends `gio::OutputStream` and exposes `finish(cancellable) -> Result<glib::GString, glib::Error>`, which calls `ostree_content_writer_finish`.

Control flow and state: Callers write bytes through the output stream interface, then call `finish` to finalize content and receive the checksum. Persistent effects are managed by the underlying writer, typically repository object storage.

Dependencies and integration points: Depends on Gio output streams, cancellables, GLib error translation, and libostree content writer internals. It likely integrates with repo write APIs that return a content writer.

Risks: Finalization order matters; dropping without `finish` may leave incomplete content depending on underlying implementation. The wrapper does not expose constructor APIs here, so lifecycle is controlled by other repo APIs.

Test signals: Integration tests should write content, call `finish`, validate checksum format, and verify cancellation/error handling.
