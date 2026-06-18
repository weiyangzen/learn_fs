# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpffs.c

Purpose: `test_bpffs.c` validates bpffs behavior across two independent mounts, including debug iterator files, directory creation, BPF object pinning, and `renameat2()` semantics for `RENAME_EXCHANGE` and `RENAME_NOREPLACE`.

Important APIs/types/functions: `read_iter()` opens a bpffs debug file and scans for the string `iter`, proving iterator-backed debug entries produce content. `fn()` runs the actual isolated filesystem test in a child process: it unshares the mount namespace, makes mounts private, creates `/tmp/test_bpffs_testdir`, mounts tmpfs, mounts two bpffs instances, creates directories, creates an array map with `bpf_map_create()`, pins it with `bpf_obj_pin()`, exchanges directories and a pinned map path with `renameat2(RENAME_EXCHANGE)`, tests `RENAME_NOREPLACE`, then unmounts/removes paths and exits with the status. `test_test_bpffs()` forks `fn()` and checks the child exit status.

Control flow: the child isolates mount state, mounts tmpfs and bpffs under `fs1` and `fs2`, verifies `maps.debug` and `progs.debug`, creates `fs1/a/1` and `fs1/b`, pins a map at `fs1/c`, swaps `a` and `b` and verifies inode/path effects, swaps pinned map `c` with directory `b` and verifies mixed-type exchange behavior, then verifies `RENAME_NOREPLACE` fails when destination exists and the original remains. Cleanup unmounts bpffs and tmpfs and removes directories before exit. Parent waits and fails if child exits nonzero.

State and persistence: state is intentionally confined to the child mount namespace and temporary directory tree under `/tmp/test_bpffs_testdir`. It creates kernel BPF map state while pinned, two bpffs mounts, a tmpfs mount, directories, and a pinned map path. Cleanup unmounts and removes all paths; an abrupt child termination could leave temporary paths in the parent filesystem but mounts are namespace-local.

Dependencies: depends on mount namespace support, tmpfs, bpffs, `renameat2()` flags, BPF map creation/pinning, and permission to mount filesystems and create BPF maps.

Integration points: this is a filesystem-level BPF selftest that exercises bpffs VFS behavior rather than BPF program execution. It validates how bpffs participates in Linux rename semantics and debug iterators.

Risks: requires mount privileges and bpffs support. The fixed temporary directory may already exist from a prior failed run; the code tolerates initial `EEXIST` but cleanup assumptions may fail if unrelated content exists there. `read_iter()` searches for a short substring, which is a smoke signal rather than exact debug output validation. `WEXITSTATUS(status)` is used without an explicit `WIFEXITED` check.

Test signals: pass signals include successful mount namespace isolation, tmpfs and bpffs mounts, readable iterator debug files containing `iter`, successful map creation and pinning, inode movement after directory exchange, path validity after mixed map/directory exchange, expected failure of `RENAME_NOREPLACE`, and zero child exit status.
