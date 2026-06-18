# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/execveat.c

## Purpose
Comprehensive `execveat(2)` selftest covering path-relative execution, absolute paths, `AT_EMPTY_PATH`, `O_PATH`, `O_CLOEXEC`, symlinks, deleted/renamed files, scripts, long paths, errno cases, and `/proc/self/comm` naming.

## Important APIs, Types, And Functions
Uses raw `execveat`, `fork`, `waitpid`, `sendfile`, `realpath`, `mkfifo`, `rename`, `unlink`, and kselftest result helpers. Key helpers are `execveat_()`, `_check_execveat_fail()`, `check_execveat_invoked_rc()`, `check_execveat()`, `concat()`, `open_or_die()`, `exe_cp()`, `check_execveat_pathmax()`, `check_execveat_comm()`, `prerequisites()`, and `run_tests()`.

## Control Flow
`main()` either acts as the executed payload when invoked with args/env or runs the test plan. Setup creates ephemeral executables/scripts, subdirectories, and FIFO. `run_tests()` opens many fd variants, checks successful execution through directory fds, absolute paths, file fds, O_PATH fds, and scripts, then checks expected failures for invalid flags, symlink no-follow, non-regular files, non-executable files, bad fds, and non-directory dirfds. It also validates near-`PATH_MAX` execution and task comm behavior.

## State And Persistence
Creates, renames, unlinks, and leaves generated output-tree files managed by the Makefile clean rules. Uses environment variables `IN_TEST`, `VERBOSE`, and `CHECK_COMM` to distinguish payload mode.

## Dependencies And Integration Points
Requires generated helpers `script`, `execveat.symlink`, `execveat.denatured`, `subdir`, and the binary itself. Integrates with kselftest TAP output.

## Risks
Expected script long-path exit can be 126 or 127 depending on shell/system. The test mutates files while fds are open to validate fd lifetime, so order matters. `TESTS_EXPECTED` must stay in sync with all result-producing checks.

## Test Signals
Signals are 54 planned kselftest results, exact errno matches (`ENOENT`, `EFAULT`, `ELOOP`, `EACCES`, `EINVAL`, `EBADF`, `ENOTDIR`), expected payload exit 99, and comm checks.
