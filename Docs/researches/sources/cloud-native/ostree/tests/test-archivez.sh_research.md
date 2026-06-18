# sources/cloud-native/ostree/tests/test-archivez.sh

Purpose: checks archive-z2 compatibility, including archive-z2 alias initialization and pulling from a file URI.

Important APIs/functions: `setup_test_repository "archive"`, `ostree init --mode=archive-z2`, `remote add`, `pull`, `rev-parse`, and `fsck`.

Control flow: creates a standard archive repository fixture, initializes a second repo using the archive-z2 alias, then creates another repo with a file remote pointed at the fixture, pulls the test branch, resolves the remote ref, and fscks.

State/persistence: writes `repo-archive-z2`, `repo2`, remote config, and imported objects. Dependencies include local file URI support and archive mode compatibility.

Integration/risk/test signals: protects mode alias compatibility and local pull behavior. Risks are narrow coverage of archive-z2 beyond initialization. Two TAP cases report init and file pull.
