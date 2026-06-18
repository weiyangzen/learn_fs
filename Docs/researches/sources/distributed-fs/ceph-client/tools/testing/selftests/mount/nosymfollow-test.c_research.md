<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/nosymfollow-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/nosymfollow-test.c

## Purpose
Validates `MS_NOSYMFOLLOW` remount semantics in an unprivileged user/mount namespace. It confirms symlink traversal is blocked after remount while `readlink()` and `realpath()` behavior and `statfs()` flags remain correct.

## Important APIs, Types, and Functions
- Namespace helpers `create_and_enter_ns()`, `write_file()`, and `maybe_write_file()`.
- `setup_symlink()` creates `/tmp/data` and `/tmp/symlink`.
- `test_link_traversal()` expects successful open without nosymfollow and `ELOOP` with nosymfollow.
- `test_readlink()`, `test_realpath()`, and `test_statfs()` validate unaffected symlink inspection and flag reporting.
- `run_tests()` runs the four checks for the current mount state.

## Control Flow
The program enters a new user namespace, maps current uid/gid to root, enters a new mount namespace, mounts ramfs on `/tmp`, creates the symlink setup, runs tests without nosymfollow, remounts `/tmp` with `MS_REMOUNT | MS_NOSYMFOLLOW`, and runs tests again expecting traversal denial and `ST_NOSYMFOLLOW`.

## State and Persistence Behavior
All filesystem changes are in a private mount namespace on `/tmp`. It creates `DATA` and `LINK` paths inside the ramfs. No intended host persistence occurs once the namespace exits.

## Dependencies and Integration Points
Requires user namespaces, mount namespaces, ramfs, mount/remount support, and the kernel `MS_NOSYMFOLLOW`/`ST_NOSYMFOLLOW` ABI. Invoked by `run_nosymfollow.sh`.

## Risks and Edge Cases
The test uses fixed `/tmp` paths inside the new namespace after mounting ramfs, so failure to isolate would be dangerous; namespace setup must succeed first. `realpath()` is expected to resolve the symlink even though later open traversal is denied under nosymfollow.

## Test Signals
Success exits 0. Any unexpected syscall result prints a detailed message and exits failure through `die()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/nosymfollow-test.c -->
