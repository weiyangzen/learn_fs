# sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/test_execve.c

## Purpose

This kselftest validates Linux capability transformations across `execve`, especially ambient capabilities, inheritable/permitted/effective sets, user namespaces, and setuid/setgid executable transitions. It runs separate root and non-root scenarios and delegates post-exec capability validation to `validate_cap`.

## Important APIs, Types, and Functions

Important globals are `nerrs` and `mpid`. Key functions are `vmaybe_write_file`, `maybe_write_file`, `write_file`, `create_and_enter_ns`, `chdir_to_tmpfs`, `copy_fromat_to`, `fork_wait`, `exec_other_validate_cap`, `exec_validate_cap`, `do_tests`, and `main`. It uses libcap-ng, `unshare`, uid/gid maps, `PR_SET_KEEPCAPS`, `PR_CAP_AMBIENT_*`, `setresuid`, `setresgid`, `mount` of private tmpfs, `chown`, `chmod`, fork/exec/wait, and kselftest.

## Control Flow

`main` locates the test directory, then forks one root-style scenario and one uid-1 scenario. `do_tests` creates either a privileged mount namespace or a user+mount namespace, remounts private, mounts tmpfs over the working directory, copies `validate_cap`, optionally creates setuid/setgid variants, clears/sets capability sets, tests ambient raise failure cases, raises/clears ambient caps, execs the helper for expected E/P/I/A states, and runs privileged SUID/SGID transition cases only when the outer namespace has real privilege.

## State and Persistence Behavior

The test mutates process credentials/capabilities, namespaces, mount namespace state, a private tmpfs, copied helper files, file ownership/mode bits, and ambient capability state. These changes are isolated in forked children/namespaces where possible.

## Dependencies and Integration Points

It depends on libcap-ng, user namespace support or root, mount namespace support, tmpfs, capability xforms in the kernel, and the `validate_cap` helper built beside the test.

## Risks and Test Signals

Risks include user namespace denial, filesystem or LSM restrictions on setuid/setgid, capability behavior differences under secureexec, skipped privileged cases when not root, and global count confusion across forks. Signals are planned kselftest results, expected failure of invalid ambient raises, expected helper observations for E/P/I/A sets, and skipped SUID/SGID tests without outer privilege.
