# sources/cloud-native/ostree/tests/test-core.js

Purpose: GJS introspection test for core libostree repository APIs from JavaScript.

Important APIs/types/functions: imports `Gio` and `OSTree`, defines `assertEquals()` and `assertThrows()`, uses `Repo.new`, `repo.create`, `prepare_transaction`, `write_directory_to_mtree`, `write_mtree`, `write_commit`, `read_commit`, `transaction_set_refspec`, and `commit_transaction`.

Control flow: creates a repo, builds a mutable tree from a Gio file/directory, writes a commit with subject/body, reads it back, sets a refspec transactionally, resolves/reads it, and checks expected exceptions for invalid operations.

State/persistence: writes a local OSTree repo, commits, and refs. Dependencies include GJS, GI bindings for OSTree, Gio, and ByteArray.

Integration/risk/test signals: protects public introspection bindings, not just C ABI. Risks include binding signature changes and JS exception text. Process exit status and explicit assertions are the signal.
