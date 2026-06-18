# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-subset-pid.c

Purpose: verifies that mounting procfs with `subset=pid` exposes only pid directories plus `/proc/self` and `/proc/thread-self`, hiding global proc entries like `cpuinfo`.

Important APIs and functions: `make_private_proc()` creates a private mount namespace and remounts `/proc`; `string_is_pid()` validates directory names. It uses `opendir`, `readdir`, `readlink`, `open`, and dirent type checks.

Control flow: unshare mount namespace, make mounts private, mount proc with `subset=pid`, iterate `/proc`, allow only `.`, `..`, `self`, `thread-self`, and numeric pid directory entries, then require `/proc/cpuinfo` readlink and open to fail with `ENOENT`.

State and persistence: remounts `/proc` only in a private namespace, so state is transient.

Dependencies and integration: requires mount namespace and procfs subset option support. `ENOSYS` or `EPERM` during unshare returns skip 4.

Risks and test signals: relies on dirent `d_type` being populated by procfs. Failures show subset filtering regressions or unexpected global entries leaking into a pid-only proc mount.
