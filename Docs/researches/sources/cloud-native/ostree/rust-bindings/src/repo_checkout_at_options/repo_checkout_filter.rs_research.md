# sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/repo_checkout_filter.rs

## sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/repo_checkout_filter.rs

Handwritten callback wrapper for checkout filtering. `RepoCheckoutFilter` stores a boxed closure `Fn(&Repo, &Path, &libc::stat) -> RepoCheckoutFilterResult`; `new` returns it pre-wrapped in `Some` for convenient option assignment.

Control flow converts the wrapper to a raw `gpointer` for libostree and defines a trampoline that borrows the repo, converts the path to `PathBuf`, borrows `libc::stat`, calls the closure, and converts the result enum. `filter_trampoline_unwindsafe` catches panics, prints a short diagnostic directly to stderr, and aborts to avoid unwinding through C. State is the closure pointer owned by checkout options for the FFI call.

Dependencies are `Repo`, `RepoCheckoutFilterResult`, GLib translation, `libc::stat`, `Path`, and panic handling. Risks include raw pointer validity and process abort on callback panic, which is deliberate for FFI safety. Tests cover null-pointer panics and successful closure invocation/result conversion.
