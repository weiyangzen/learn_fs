# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bprm_opts.c

Purpose: `test_bprm_opts.c` verifies that a BPF `bprm_creds_for_exec` program can set `bprm->secureexec` based on task local storage and that userspace observes secure execution through environment-variable scrubbing by the dynamic loader.

Important APIs/types/functions: `bash_envp` provides `TMPDIR=shouldnotbeset`. `update_storage()` opens a pidfd for the current process, inserts `secureexec` into `secure_exec_task_map` with `BPF_NOEXIST`, and closes the pidfd. `run_set_secureexec()` forks a child, redirects output to `/dev/null`, updates task storage, then `execle()`s `/bin/bash` to return 10 if `TMPDIR` remains set and 20 if it is unset. `test_test_bprm_opts()` loads and attaches `bprm_opts.skel.h`, then runs the child path once with secureexec 0 and once with secureexec 1.

Control flow: after skeleton attach, the first child writes secureexec 0 into task local storage and should execute bash normally, preserving `TMPDIR` and exiting 10. The second writes secureexec 1 and should trigger secure execution, causing loader/shell environment scrubbing and exit 20. The parent waits for each child and translates the expected exit code to success.

State and persistence: state includes a BPF task-local-storage map entry keyed by child pidfd, a BPF LSM/bprm attachment from the skeleton, child process environment, and `/dev/null` fd redirection. No files are created except opening `/dev/null`.

Dependencies: depends on generated `bprm_opts.skel.h`, BPF support for bprm hooks and task local storage, `pidfd_open`, `/bin/bash`, dynamic loader secure-exec behavior, and `network_helpers.h` for `sys_pidfd_open`.

Integration points: this bridges BPF process-exec hooks to a concrete userspace security semantic: secureexec causes environment variables such as `TMPDIR` to be ignored/removed. It validates both kernel hook behavior and the selftest BPF program's map lookup path.

Risks: assumes `/bin/bash` exists and that `TMPDIR` is affected as expected under secure execution on the platform. `update_storage()` returns positive errno values rather than negative errors, matching child exit use but different from many kernel-style helpers. The test uses `WEXITSTATUS` without checking abnormal child termination. If a previous map entry exists for the same pidfd, `BPF_NOEXIST` would fail, though pidfds are per child.

Test signals: success requires skeleton load/attach, child with secureexec 0 exiting as normal environment-preserving execution, child with secureexec 1 exiting as secure environment-scrubbed execution, and no errors from pidfd/map update or exec setup.
