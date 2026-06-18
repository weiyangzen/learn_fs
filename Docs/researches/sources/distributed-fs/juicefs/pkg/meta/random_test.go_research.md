# sources/distributed-fs/juicefs/pkg/meta/random_test.go

## Purpose

`random_test.go` is a property-based state-machine test for the `Meta` interface. It builds an in-memory model of filesystem metadata (`fsMachine`) and uses `pgregory.net/rapid` to generate long random sequences of namespace, file, xattr, ACL, stat, and lock operations, comparing real metadata engine behavior against the model after each operation.

## Important Types And Model Functions

Model types include `tSlice`, `tQuota`, `tNode`, `tEntry`, and `fsMachine`. `tNode` models inode type, mode, uid/gid, timestamps, flags, length, parents/hardlink state, chunks, children, symlink target, xattrs, quotas, flocks, plocks, and ACLs. Permission helpers `accessMode`, `access`, and `stickyAccess` implement simplified POSIX/ACL checks.

`fsMachine.Init` creates a root model, initializes a real `Meta` client from `-rapid.meta` (default `memkv://jfs-unit-test`), resets/formats it, installs session/metrics state, and records backend type (`db`, `redis`, or `tkv`) to account for backend-specific errno ordering. `Cleanup` closes/reset/shuts down the real backend.

The model implements expected behavior for create/link/symlink/readlink/unlink/rmdir/lookup/getattr/truncate/fallocate/copy-file-range/rmr/rename/readdir/write/read/xattrs/tree checking/ACL/statfs/times/chmod/chown/flock/plock/list-locks/getlk/setlk.

## Control Flow And Test Coverage

Each exported method on `fsMachine` is a rapid action. It draws random inputs, calls the real `Meta` method, calls the model method, and fails if errno or returned data diverges. Enabled actions cover `Mkdir`, `Mknod`, `Link`, `Rmdir`, `Unlink`, `Symlink`, `Readlink`, `Lookup`, `Getattr`, `Rename`, `Readdir`, `Fallocate`, `Write`, `Read`, `SetXAttr`, `RemoveXattr`, `GetXAttr`, `ListXAttr`, `Check`, `Setfacl`, `GetACL`, `RemoveACL`, `StatFS`, `SetAmtime`, `Chmod`, `Chown`, `Flock`, `ListLocks`, `Getlk`, and `Setlk`. Truncate, copy-file-range, and recursive remove actions are present but disabled due to slice compaction/concurrency unpredictability.

`Check` recursively compares the full filesystem tree, attributes, chunks, symlinks, and xattrs. Lock methods also compare `ListLocks` results after successful updates. `TestFSOps` configures rapid defaults (`steps=200`, `checks=5000`, `shrinktime=1h`) and runs the state machine with logging reduced to errors.

## Dependencies And Integration Points

The test depends on `rapid`, ACL APIs, Prometheus metrics setup, package lock helpers (`ownerKey`, `plockRecord`, `updateLocks`), context constructors, test config/format helpers, and all registered metadata engines reachable through `NewClient`. It is same-package and touches internal session fields.

## Risks And Edge Cases

The model includes backend-specific conditional behavior because db/redis/tkv sometimes differ in validation order and returned errno. Some model checks are intentionally simplified or disabled, especially truncate/copy-file-range slice compaction and recursive remove concurrency. Name generation filters `|`, `.#`, and newline due to known metadata constraints. The test is powerful but can be slow and failure shrinking can take time; default check count is high. It mutates global flags and logger level, restoring them with defers.

## Test Signals

This is the broadest behavioral signal for `Meta` compatibility. Failures usually indicate a real metadata semantic regression, a backend-specific errno ordering change, or a model drift that needs explicit reconciliation.
