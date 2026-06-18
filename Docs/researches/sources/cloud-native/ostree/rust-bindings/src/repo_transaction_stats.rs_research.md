# sources/cloud-native/ostree/rust-bindings/src/repo_transaction_stats.rs

## sources/cloud-native/ostree/rust-bindings/src/repo_transaction_stats.rs

Handwritten/newtype support around generated `RepoTransactionStats`. It provides `uninitialized` construction for passing an output stats struct to `ostree_repo_commit_transaction`, plus field accessors for transaction counters such as metadata/content objects written and bytes written.

Control flow is low-level GLib struct ownership: the value is prepared as an output target, then populated by libostree and returned from `Repo::commit_transaction` or `TransactionGuard::commit`. State is summary data for a completed repo transaction; persistence has already happened in the repository.

Dependencies are GLib pointer conversion traits and `ffi`. Risks are uninitialized-memory correctness and keeping the Rust accessor layout aligned with C. There are no dedicated tests, but transaction paths rely on this type.
