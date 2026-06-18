# sources/cloud-native/ostree/rust-bindings/src/repo.rs

## sources/cloud-native/ostree/rust-bindings/src/repo.rs

Handwritten extensions for `Repo`, filling gaps that GIR could not convert ergonomically. It adds path/dirfd constructors, RAII transactions, hash-table conversions for refs/objects/traversals, required revision resolution, file metadata/content helpers, trusted and untrusted content/metadata writes returning `Checksum`, async write wrappers and futures, dirmeta parsing, and commit-object prefix listing.

Important types/functions include `TransactionGuard`, `auto_transaction`, `dfd_as_file`, `dfd_borrow`, `traverse_commit`, `list_refs`, `list_objects`, `list_refs_ext`, `require_rev`, `load_file`, `query_file`, `write_content`, `write_metadata`, `write_content_async_future`, `write_metadata_async_future`, `read_dirmeta`, and `list_commit_objects_starting_with`. Control flow frequently calls C APIs that return `GHashTable`s, then iterates or converts them into Rust `HashSet`/`HashMap` and unrefs where appropriate. `TransactionGuard::drop` aborts uncommitted transactions, while `commit` consumes the guard and disables the abort.

State and persistence are central: these helpers read and write repository object storage, refs, metadata, and transactions. Dependencies include `Checksum`, `ObjectName`, `ObjectDetails`, `RepoTransactionStats`, `gio`, `glib`, raw fd traits, futures, and libostree FFI. Risks include unsafe hash-table conversion, assuming output initialization on success, abort errors being ignored in `Drop`, async callback ownership, and persistent side effects of write/list operations. Test signals are indirect plus dedicated repo mode tests in `tests/repo.rs`.
