# sources/distributed-fs/juicefs/pkg/object/filesystem_test.go


Purpose: defines a reusable contract test for filesystem-like object backends.

Important APIs and flow: `testFileSystem` creates a small directory tree, verifies directory `Head`, lists with prefixes, exercises chmod effects on listings, tests symlink creation/readlink/head/list behavior for stores implementing `SupportSymlink`, and writes a 255-character filename. It is invoked by `TestDisk2`, `TestSftp2`, `TestCifs2`, `TestHDFS2`, `TestNFS2`, and Gluster tests. `testKeysEqual` provides strict ordered key comparisons.

State and persistence: tests mutate temporary disk storage or configured external filesystems, then delete created keys in reverse order to handle directory emptiness.

Dependencies and integration: validates the `ObjectStorage`, `FileSystem`, and `SupportSymlink` contracts for local and network filesystem adapters. It expects delimiter listing and recursive `listAll` behavior from package helpers.

Risks and gaps: many backends are environment-gated and skipped without credentials or services. Permission behavior has backend-specific exceptions for NFS, CIFS, and Gluster. Cleanup failures can fail tests after earlier assertions.

Test signal: high-value shared behavioral coverage for path ordering, directory markers, permissions, symlink following, and long names across filesystem-style implementations.
