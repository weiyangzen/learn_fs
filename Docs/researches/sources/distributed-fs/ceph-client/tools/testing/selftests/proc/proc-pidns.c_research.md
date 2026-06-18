# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-pidns.c

Purpose: kselftest harness for procfs `pidns=` mount option support through both legacy mount strings and new mount API fsconfig inputs. It also verifies PID namespace association cannot be reconfigured after procfs creation.

Important APIs and functions: uses namespace operations `unshare`, `setns`, `mount`, bind mount of `/proc/self/ns/pid`, `fsopen`, `fsconfig`, `fsmount`, `faccessat`, and kselftest `ASSERT_*` macros. `ASSERT_ERRNO_EQ` normalizes syscall negative errno handling.

Control flow: fixture stashes host mount and PID namespace fds, creates private tmpfs-backed `/tmp`, creates a dummy PID namespace in a child, bind-mounts its pidns fd, then returns to the host pidns. Tests mount proc using host and dummy pidns paths or fd and verify expected visibility. Reconfiguration tests require `EBUSY` and verify original view remains intact.

State and persistence: transient mount namespace with tmpfs under `/tmp`; bind-mounted namespace file and proc mount are discarded when returning to original mount namespace.

Dependencies and integration: requires new mount API, PID namespaces, mount namespaces, bind mounts, and privileges. Integrated with `kselftest_harness.h`.

Risks and test signals: environment privilege restrictions will fail setup. Semantic failures indicate procfs pid namespace selection or immutability regressions.
