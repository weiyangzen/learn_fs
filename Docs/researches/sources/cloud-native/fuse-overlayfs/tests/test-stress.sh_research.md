<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-stress.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-stress.sh

## Purpose
Runs a broad stress suite against `fuse-overlayfs` by repeatedly creating a temporary lower/upper/work/merged overlay, mounting it, exercising high-volume and concurrent filesystem operations, and verifying postconditions. It is intended to expose races in copy-up, whiteout creation, readdir, hardlink accounting, symlink handling, xattrs, permission changes, sparse files, fsync, and multi-layer merge behavior.

## Important APIs, Types, And Functions
- `NPROC` defaults to `nproc` and controls parallel worker fan-out; `SCALE` multiplies test sizes.
- `cleanup`, registered with `trap EXIT`, unmounts `$MERGED` and removes `$TESTDIR`.
- `mount_overlay`, `remount_overlay`, and `reset_overlay` centralize mount lifecycle.
- `elapsed` returns elapsed milliseconds from a captured epoch-millis timestamp.
- `chunk_end COUNT NPROC WORKER_INDEX` gives each worker a range and makes the last worker absorb remainders.
- External test tools include `fuse-overlayfs`, `umount`, `stat`, `ln`, `chown`, `setfattr`, `getfattr`, `fallocate`, `dd`, `mknod`, and `find`.

## Control Flow
The script is linear and fail-fast under `set -xeuo pipefail`. Each numbered block resets state, prepares lower and/or merged content, mounts the overlay, runs a specific workload, validates invariants, then resets. The 40 workloads cover sequential and parallel file creation, deep and wide directories, stat storms, concurrent reads/writes, rename storms, hardlinks, copy-up storms, mixed create/stat/write/rename/unlink workloads, unlink storms, mount cycles, container-storage-like hardlink rewrites, large file throughput, concurrent mkdir/rmdir, same-file copy-up races, readdir during mutations, symlink and xattr storms, whiteout persistence, fallocate writes, cross-directory renames, copy-up/stat races, mmap-style reads, chmod/chown copy-up, truncation, multi-lower overlays, rapid open/close, tmpfile patterns, nested lower directories, concurrent appends, read-during-unlink, sparse files, lower-layer whiteout ordering, concurrent fsync, and interleaved copy-up/stat checks.

## State And Persistence
State is scoped to a `mktemp` directory under `/tmp`. The suite deliberately preserves or discards `upper` and `workdir` depending on the test: most tests remove all layers, while whiteout persistence remounts with the same upper/work layers. Multi-layer tests use separate lower directories and remove them manually. No repository files are modified.

## Dependencies And Integration Points
This is an integration test for the installed `fuse-overlayfs` binary and kernel/FUSE support. It assumes GNU-style userland flags such as `stat -c`, `dd conv=fsync`, `touch -h -d`, `getfattr --only-values`, and overlay lowerdir colon ordering. It complements narrower symlink, xattr, unlink, and unprivileged tests in the same directory.

## Risks And Edge Cases
`CHUNK=$((COUNT / NPROC))` can be zero if `NPROC` exceeds small scaled counts, causing duplicated ranges or empty worker ranges in some tests. The suite is intentionally expensive when `SCALE` or `NPROC` is high. Some xattr operations ignore failures, which keeps the stress portable but weakens assertions on filesystems without user xattr support. Tests using `mknod` whiteouts, `chown`, `fallocate`, and mount/unmount require sufficient privileges/capabilities.

## Test Signals
Success requires all shell assertions to pass and ends with `All stress tests passed!`. Failure points identify functional regressions in visibility, content preservation, link counts, whiteout semantics, final permissions, file sizes, and surviving original entries after concurrent mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-stress.sh -->
