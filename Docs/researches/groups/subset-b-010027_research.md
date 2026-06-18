# subset-b-010027 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/test_sshfs.py -->
# sources/user-network-fs/sshfs/test/test_sshfs.py

## Purpose

`test_sshfs.py` is the main integration and regression test suite for the SSHFS userspace filesystem. It mounts the locally built `sshfs` binary against a passwordless `localhost` SSH/SFTP server, then verifies that ordinary POSIX filesystem operations through the FUSE mount behave like operations on the backing source directory. The file also contains targeted option tests for hardlink disabling, symlink following and containment, direct I/O, and malformed SFTP reply handling.

The suite is intended to run under pytest and can be invoked directly because the `__main__` block calls `pytest.main([__file__] + sys.argv[1:])`. It is not a unit-test-only file: most tests require FUSE support, a working `fusermount`/`fusermount3`, the built `sshfs` executable, and passwordless SSH to `localhost`.

## Important APIs, Types, And Functions

- `pytestmark = fuse_test_marker()` applies an environment-sensitive pytest marker from `util.py`, skipping the module when FUSE prerequisites are unavailable.
- `TEST_DATA` reads the current test file as binary data and is reused by read/write/truncate tests as stable nontrivial file content.
- `name_generator()` uses a mutable default counter to generate process-local unique names such as `testfile_1`; this keeps operations from colliding inside a shared temporary mount.
- `test_sshfs(tmpdir, debug, cache_timeout, sync_rd, multiconn, capfd)` is the broad matrix test. It runs across `debug`, directory cache timeout, `sync_readdir`, and `max_conns=3` permutations, mounts SSHFS in foreground mode, then calls the `tst_*` operation helpers.
- `_check_ssh_localhost()` duplicates the passwordless localhost SSH probe used by the main matrix and fails the test on timeout or nonzero exit.
- `_mount_sshfs(tmpdir, extra_opts=None)` and `_sshfs_mount(src_dir, mnt_dir, extra_opts=None)` are reusable mount helpers for option-specific tests; the latter is a context manager.
- `tst_*` helpers exercise individual filesystem semantics: unlink, mkdir/rmdir, rename/rename-over/rename-sibling/rename-open-release, chmod/chown, fsync, symlink, create, open/read/write/append/seek, statvfs, access, hardlink, readdir, path/fd truncate, utimens, passthrough visibility, open-unlink, write-only reads, and repeated readdir consistency.
- Option regression tests include `test_disable_hardlink`, `test_follow_symlinks`, `test_direct_io`, `test_bad_sftp_reply_len`, `test_contain_symlinks`, `test_no_contain_symlinks`, `test_transform_with_contain`, and `test_contain_symlinks_option_precedence`.

## Control Flow

The module first ensures it can SSH into `localhost` without prompting by running `ssh -o StrictHostKeyChecking=no -o KbdInteractiveAuthentication=no -o ChallengeResponseAuthentication=no -o PasswordAuthentication=no localhost -- true` with a 10 second timeout. The main matrix then creates isolated `mnt` and `src` directories under pytest's `tmpdir`, builds a command beginning with `base_cmdline`, the built `sshfs` path, `-f`, `localhost:<src_dir>`, and the mountpoint, and appends options according to the parameter set.

The main command always disables FUSE entry and attribute caching with `entry_timeout=0` and `attr_timeout=0`, disables symlink containment with `no_contain_symlinks` for the legacy symlink helper, and sets `G_DEBUG=fatal-warnings` so GLib warnings abort the mounted process. After `subprocess.Popen`, `wait_for_mount()` polls until the mount appears or the process dies. The test then executes the operation helpers in a fixed sequence and unmounts with `umount()` on success. On any exception, `cleanup()` attempts lazy unmount and terminates or kills the mount process before reraising.

The helper tests follow the same lifecycle in smaller scopes. `_mount_sshfs()` creates a fresh source and mount directory, appends arbitrary `-o` options, waits for the mount, and returns process plus paths. `_sshfs_mount()` wraps that pattern as a context manager for symlink containment scenarios. `test_bad_sftp_reply_len` is different: it generates an executable Python SFTP stub that emits a normal version packet followed by a zero-length reply, starts `sshfs` with `ssh_command=<helper>`, and asserts that SSHFS fails with `bad reply len: 0`.

## State And Persistence Behavior

All filesystem state is intentionally temporary. Pytest's `tmpdir` owns the source and mount directories, and `name_generator()` provides per-process unique leaf names. The tests create files, directories, hardlinks, symlinks, open file descriptors, metadata changes, and timestamps both through the mounted view and directly in the backing source directory. Cache-sensitive tests call `safe_sleep(cache_timeout + 1)` when directory-cache visibility can lag.

The only persistent host-side state risk is SSH known-host and key setup: `StrictHostKeyChecking=no` can add a localhost key warning, which the custom `capfd.register_output()` filter treats as expected output. Mount processes are external stateful processes; the suite relies on `umount()`/`cleanup()` to avoid leaving mounted tmpdirs behind. No durable repository files are written by this test, except the generated helper inside `tmpdir` for `test_bad_sftp_reply_len`.

## Dependencies And Integration Points

- Imports from `util.py`: `wait_for_mount`, `umount`, `cleanup`, `base_cmdline`, `basename`, `fuse_test_marker`, `safe_sleep`, `os_create`, and `os_open`.
- Pytest supplies `tmpdir`, `capfd`, parametrization, skip/fail helpers, and exception assertions. `capfd.register_output()` is a project-specific extension installed by `test/conftest.py`.
- The built SSHFS executable is addressed as `pjoin(basename, "sshfs")`, where `basename` points one directory above `test/`.
- System integration requires OpenSSH client/server, passwordless localhost authentication, FUSE kernel support, `fusermount` for capability detection/cleanup, and `fusermount3` for normal unmounts.
- Standard library dependencies include `subprocess`, `os`, `sys`, `stat`, `shutil`, `filecmp`, `errno`, `NamedTemporaryFile`, and `contextmanager`.
- Meson includes this file through `test/meson.build`, and the CI scripts run it via `python3 -m pytest --maxfail=99 test/`.

## Risks And Edge Cases

- The test suite is highly environment-sensitive. Missing `/dev/fuse`, missing setuid `fusermount` for non-root users, absent `fusermount3`, or no passwordless localhost SSH causes skips or failures unrelated to SSHFS logic.
- `_check_ssh_localhost()` is duplicated instead of reused from the main test body, which can drift if SSH options need updating.
- `name_generator()` uses a mutable default counter, which is acceptable for one process but is not designed for cross-process coordination if tests are parallelized in the same mount directory.
- Cache-sensitive assertions depend on sleep-based expiry; slow filesystems or changed cache semantics can introduce flakiness.
- The main matrix can be expensive: it runs a large operation sequence across 16 combinations and, with `TEST_WITH_VALGRIND=true`, every SSHFS mount runs under Valgrind through `base_cmdline`.
- Some assertions are platform-specific. `tst_chown` only runs as root; symlink opt-out reads `/etc/passwd`; hardlink behavior depends on server extension support; timestamp tolerance is one second for SSHFS set-time semantics.
- `test_bad_sftp_reply_len` assumes the expected diagnostic string is stable, so error-message wording changes can break it even if the behavior remains safe.

## Test Signals

- Passing `test_sshfs` across all parameter combinations signals that core create/read/write/metadata/directory operations work with and without SSHFS directory caching, sync readdir, debug logging, and multiconnection mode.
- `test_disable_hardlink` verifies both the control path where hardlinks work and the `disable_hardlink` option path where `os.link` fails with `ENOSYS` or `EPERM`.
- `test_follow_symlinks`, `test_contain_symlinks`, `test_no_contain_symlinks`, `test_transform_with_contain`, and `test_contain_symlinks_option_precedence` collectively cover symlink resolution policy, escape blocking, transform interactions, and last-option-wins parsing.
- `test_direct_io` covers the `direct_io` option by writing through the mount and verifying both mounted and backing-store reads.
- `test_bad_sftp_reply_len` is a negative protocol test that protects against zero-length SFTP reply underflow.
- Expected-output filters for SSH known-host warnings and transform warnings make unexpected stdout/stderr noise a useful failure signal through the project's pytest capture extension.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/test_sshfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/travis-build.sh -->
# sources/user-network-fs/sshfs/test/travis-build.sh

## Purpose

`travis-build.sh` is a legacy CI build-and-test driver for SSHFS. It performs multiple Meson/Ninja builds, runs the pytest test suite, runs the standard compiler builds under Valgrind, and runs sanitizer builds for undefined behavior and address sanitization. It is designed for Travis-style Linux CI with `sudo` available.

## Important APIs, Types, And Functions

- `set -e` makes the script fail fast on an unhandled command failure.
- `ASAN_OPTIONS="detect_leaks=0"` disables leak detection for now, acknowledging unresolved leaks or false positives.
- `LSAN_OPTIONS="suppressions=${PWD}/test/lsan_suppress.txt"` points LeakSanitizer at the repository's suppression file.
- `TEST_CMD="python3 -m pytest --maxfail=99 test/"` is the common test invocation.
- The first loop builds with `gcc` and `clang`, runs `meson -D werror=true`, compiles with `ninja`, then runs the tests with `TEST_WITH_VALGRIND=true`.
- The sanitizer loop sets `CC=clang`, builds once with `-D b_sanitize=undefined` and once with `-D b_sanitize=address`, runs the test command, and installs each build.

## Control Flow

The script exports sanitizer environment variables, then iterates over `gcc` and `clang`. Each compiler build happens in a subshell so `cd build-${CC}` does not affect the parent shell. There is a dormant branch for `gcc-6` that would add `-D b_lundef=false`, but the active compiler list only contains `gcc` and `clang`. After each standard build, pytest runs with `TEST_WITH_VALGRIND=true`, which `test/util.py` converts into a `valgrind -q --` prefix for the SSHFS process.

After the compiler loop, the script runs `(cd "build-${CC}"; sudo ninja install)`. At that point `CC` is still the last loop value, `clang`, so this installs the `build-clang` tree. It then sets `CC=clang` explicitly and loops over `undefined` and `address` sanitizers. Each sanitizer build gets its own `build-${san}` directory, configures Meson with `b_lundef=false` to work around a documented clang/Meson linker issue, builds, runs pytest normally, and installs with `sudo ninja install`.

## State And Persistence Behavior

The script creates or reuses `build-gcc`, `build-clang`, `build-undefined`, and `build-address` directories in the current working tree. It mutates the host by running `sudo ninja install` for the clang build and for each sanitizer build. Environment variables exported at the top apply to all child Meson, Ninja, and pytest commands. The script does not clean build directories, so reruns can fail if directories already exist or can reuse stale configuration if manually altered.

## Dependencies And Integration Points

- Requires Bash because it uses `#!/bin/bash` and `==` inside `[ ... ]`.
- Requires Meson, Ninja, Python 3, pytest, GCC, Clang, Valgrind, sanitizer-capable Clang runtimes, and sudo privileges.
- Integrates with `test/util.py` through `TEST_WITH_VALGRIND=true`; that environment variable changes `base_cmdline` for the mounted SSHFS process.
- Depends on the SSHFS test prerequisites installed by `travis-install.sh`, especially FUSE/libfuse and passwordless localhost SSH.
- The release packaging script references this file, so it is part of the repository's distributed test tooling even if Travis itself is no longer the active CI provider.

## Risks And Edge Cases

- `mkdir "build-${CC}"` and `mkdir "build-${san}"` fail on rerun if the directories already exist.
- The special `gcc-6` branch is unreachable with the current compiler list, suggesting stale CI compatibility code.
- The post-loop install relies on `CC` retaining `clang`; adding another compiler to the loop changes which standard build is installed.
- `sudo ninja install` mutates `/usr/local` or the configured prefix in CI, which can hide missing runtime path setup or affect later test phases.
- Leak detection is disabled globally, so memory leaks are not caught by the ASan lane.
- Valgrind execution across the full matrix is slow and can expose timing-sensitive test failures.

## Test Signals

- Standard `gcc` and `clang` builds passing with `-D werror=true` signal warning-clean compilation across both compilers.
- `TEST_WITH_VALGRIND=true` passing means the integration tests can run SSHFS under Valgrind without detected severe memory errors or Valgrind-induced behavior changes.
- UndefinedBehaviorSanitizer and AddressSanitizer lanes passing signal no sanitizer-detected UB or memory safety failures under the pytest workload.
- Successful `sudo ninja install` checks install rules after the build and test steps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/travis-build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/travis-install.sh -->
# sources/user-network-fs/sshfs/test/travis-install.sh

## Purpose

`travis-install.sh` is a legacy CI provisioning script for SSHFS. It builds and installs libfuse from the upstream master branch, adjusts pkg-config and dynamic-loader paths for the installed library, and configures localhost SSH key-based authentication so the integration tests can mount `localhost:<tmpdir>` without a password prompt.

## Important APIs, Types, And Functions

- `set -e` fails the provisioning run on any unhandled command error.
- `wget https://github.com/libfuse/libfuse/archive/master.zip` downloads libfuse source as a zip archive.
- `meson ..`, `ninja`, and `sudo ninja install` configure, build, and install libfuse.
- `sudo mv /usr/local/lib/*/pkgconfig/* /usr/local/lib/pkgconfig/` normalizes pkg-config file placement for later Meson discovery.
- `printf '%s\n' /usr/local/lib/*-linux-gnu | sudo tee /etc/ld.so.conf.d/usrlocal.conf` and `sudo ldconfig` add the installed library directory to the runtime linker cache.
- `ssh-keygen`, appending to `~/.ssh/authorized_keys`, chmod, and an SSH smoke test prepare passwordless localhost access.

## Control Flow

The script downloads `master.zip`, unzips it, enters `libfuse-master`, creates and enters `build`, configures with Meson, builds with Ninja, and installs with sudo. After installation it ensures `/usr/local/lib/pkgconfig` exists, moves architecture-specific pkg-config files into that directory, writes the `/usr/local/lib/*-linux-gnu` path to a loader config file, and runs `ldconfig`.

The second phase generates a 1024-bit RSA key at `~/.ssh/id_rsa` with an empty passphrase, appends the public key to `~/.ssh/authorized_keys`, tightens authorized-key permissions to `600`, and runs `ssh -o "StrictHostKeyChecking=no" localhost echo "SSH connection succeeded"` as an end-to-end authentication check.

## State And Persistence Behavior

This script makes durable changes to the CI host. It creates `master.zip`, a `libfuse-master` source tree, and a `libfuse-master/build` directory in the current working directory. It installs libfuse under `/usr/local`, moves pkg-config metadata, writes `/etc/ld.so.conf.d/usrlocal.conf`, and updates the loader cache. It also creates or overwrites `~/.ssh/id_rsa`, appends to `~/.ssh/authorized_keys`, and may add a `localhost` host key to the user's known-hosts file.

The script is not idempotent in a clean sense: rerunning can fail if `~/.ssh/id_rsa` already exists and `ssh-keygen` prompts, can append duplicate authorized keys, and can fail if `master.zip` or `libfuse-master` already exist in conflicting states.

## Dependencies And Integration Points

- Requires POSIX shell, wget, unzip, Meson, Ninja, sudo, a compiler toolchain for libfuse, OpenSSH client/server, and permission to write `/usr/local` and `/etc/ld.so.conf.d`.
- Provides libfuse headers/libraries needed by the SSHFS Meson build.
- Provides the passwordless localhost SSH precondition required by `test_sshfs.py`.
- The script pairs with `travis-build.sh` in release packaging and legacy CI setup.

## Risks And Edge Cases

- Building from libfuse `master` is non-reproducible; upstream changes can break SSHFS CI without a local repository change.
- The 1024-bit RSA key is weak by modern standards and is appropriate only for disposable CI, not developer machines.
- Overwriting or appending to real user SSH configuration is risky outside isolated CI.
- The pkg-config move assumes a specific `/usr/local/lib/*/pkgconfig` layout and may fail or move multiple architecture directories unexpectedly.
- `StrictHostKeyChecking=no` eases CI setup but suppresses host-key verification.
- No cleanup is performed, so repeated runs can accumulate source/build artifacts and SSH authorized-key duplicates.

## Test Signals

- Successful Meson/Ninja libfuse build and `sudo ninja install` indicate the FUSE dependency is available for the SSHFS build.
- `ldconfig` completing after writing the loader path indicates runtime linking should find the installed libfuse.
- The final `ssh localhost echo "SSH connection succeeded"` verifies the exact authentication path later used by `test_sshfs.py`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/travis-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/util.py -->
# sources/user-network-fs/sshfs/test/util.py

## Purpose

`util.py` contains shared pytest helpers for the SSHFS integration tests. It centralizes path discovery for the built `sshfs` binary, small file-descriptor helpers, mount readiness polling, cleanup and unmount behavior, FUSE availability marking, safe sleep across signals, and optional Valgrind command-line prefixing.

## Important APIs, Types, And Functions

- `basename = pjoin(os.path.dirname(__file__), "..")` points from `test/` to the SSHFS build/source root used to locate the `sshfs` executable.
- `os_create(name)` creates an empty read/write file with `os.open(..., O_CREAT | O_RDWR)` and immediately closes it.
- `os_open(name, flags)` is a context manager that yields a raw file descriptor and guarantees `os.close(fd)` in `finally`.
- `wait_for_mount(mount_process, mnt_dir, test_fn=os.path.ismount)` polls for up to 30 seconds until the mountpoint is recognized, failing if the process exits early or the mount never appears.
- `cleanup(mount_process, mnt_dir)` attempts lazy unmount with `fusermount -z -u`, suppresses output, terminates the process, waits one second, and kills it if needed.
- `umount(mount_process, mnt_dir)` performs the normal unmount path with `fusermount3 -z -u`, asserts the path is no longer a mount, and waits up to 30 seconds for a zero process exit code.
- `safe_sleep(secs)` loops around `time.sleep()` until wall-clock time reaches the requested end time, preventing signal-shortened sleeps.
- `fuse_test_marker()` returns either `pytest.mark.uses_fuse()` or a pytest skip marker with a concrete reason after checking `fusermount`, `/dev/fuse`, setuid/root status, and `/dev/fuse` openability.
- `base_cmdline` is `["valgrind", "-q", "--"]` when `TEST_WITH_VALGRIND` is truthy, otherwise an empty list.

## Control Flow

Test modules import these helpers during collection. `fuse_test_marker()` executes at import time in `test_sshfs.py`: it runs `which fusermount`, verifies `/dev/fuse`, allows root directly, checks the setuid bit on `fusermount` for non-root users, and tries to open `/dev/fuse` read/write. The first failed prerequisite becomes a skip reason; otherwise the module receives the `uses_fuse` marker.

At runtime, tests launch SSHFS with `subprocess.Popen`, then call `wait_for_mount()`. That function polls every 0.1 seconds and also checks `mount_process.poll()` to fail early if SSHFS exits before mounting. Successful tests call `umount()`, which uses `fusermount3`, checks the mount disappeared, and polls for process termination. Failing tests call `cleanup()`, which uses the older `fusermount` command for a best-effort lazy unmount and forcefully ends the process if graceful termination fails.

The `base_cmdline` computation is a module-level environment hook. CI can set `TEST_WITH_VALGRIND=true`, causing all test commands that prepend `base_cmdline` to execute SSHFS under Valgrind without changing each test.

## State And Persistence Behavior

This module does not keep durable state. It interacts with system state by probing executables, `/dev/fuse`, file permissions, mount state, and child process status. `cleanup()` and `umount()` mutate mount state by unmounting the FUSE mountpoint and terminating the SSHFS child process. `os_create()` and `os_open()` mutate files only at paths supplied by tests.

The only module-level mutable behavior is `base_cmdline`, derived once from `TEST_WITH_VALGRIND` at import time. Changing that environment variable after import will not affect already imported helpers.

## Dependencies And Integration Points

- Depends on Python standard modules `subprocess`, `os`, `stat`, `time`, `contextmanager`, and `os.path.join`.
- Depends on pytest for `pytest.fail`, skip markers, and `uses_fuse` markers.
- Depends on system `which`, `fusermount`, `fusermount3`, `/dev/fuse`, and optionally `valgrind`.
- Used directly by `test_sshfs.py`; Meson includes `util.py` in the installed/copied test script list via `test/meson.build`.
- `travis-build.sh` controls the Valgrind path through `TEST_WITH_VALGRIND=true`.

## Risks And Edge Cases

- `fuse_test_marker()` checks for `fusermount`, but `umount()` later requires `fusermount3`; an environment with only `fusermount` can collect tests but fail during teardown.
- `cleanup()` and `umount()` use different unmount binaries, which may reflect compatibility needs but can produce inconsistent behavior on systems where only one is installed.
- The mount wait and unmount wait are fixed 30 second loops with 0.1 second sleeps; very slow CI can fail even if the operation would eventually complete.
- `cleanup()` suppresses unmount output, which keeps logs quiet but can hide useful diagnostics.
- `wait_for_mount()` only reports premature termination, not stderr; diagnosing mount failures depends on surrounding pytest capture.
- Valgrind presence is not validated when `TEST_WITH_VALGRIND` is set; missing Valgrind will fail later at process launch.

## Test Signals

- Environment skip reasons from `fuse_test_marker()` distinguish missing `fusermount`, unloaded FUSE kernel support, missing setuid permission, and inability to open `/dev/fuse`.
- `wait_for_mount()` failing with "file system process terminated prematurely" signals SSHFS crashed or exited before mounting.
- `umount()` failing with a nonzero mount process code signals runtime errors detected after unmount.
- Valgrind mode uses the same functional tests while adding memory-error detection around the SSHFS process.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/wrong_command.c -->
# sources/user-network-fs/sshfs/test/wrong_command.c

## Purpose

`wrong_command.c` builds a small executable that intentionally fails with a clear diagnostic telling the user not to run it directly. In the SSHFS Meson test setup, `test/meson.build` builds this program as `wrong_command` from `wrong_command.c`; it acts as a guard or placeholder command that redirects humans toward the real pytest invocation.

## Important APIs, Types, And Functions

- Includes only `<stdio.h>`.
- `int main(void)` writes a colored/bold message to `stderr` with `fprintf`.
- The diagnostic says: "This is not the command you are looking for." and "You probably want to run 'python3 -m pytest test/' instead".
- Returns `1` unconditionally.

## Control Flow

Execution enters `main`, emits ANSI escape sequences for red and bold text, prints the two-line warning, resets terminal styling, and exits with failure status. There are no branches, inputs, allocation, or file operations beyond writing to standard error.

## State And Persistence Behavior

The program has no persistent state. It does not read or write files, environment variables, or process-global state beyond terminal output. Its only externally visible effects are stderr text and exit code `1`.

## Dependencies And Integration Points

- Requires a C compiler and standard C library.
- Integrated by `sources/user-network-fs/sshfs/test/meson.build`, which builds the executable from this source.
- The message points users to `python3 -m pytest test/`, matching the test command used by `travis-build.sh`.

## Risks And Edge Cases

- The source uses both `\x1B` and `\e` escape forms. `\e` is a common compiler extension but is not part of strict ISO C, so strict portability depends on compiler mode.
- ANSI coloring can render literally on terminals or logs that do not interpret escape codes.
- The utility is intentionally always failing; accidentally wiring it into an automated test as the command under test would produce a guaranteed failure.

## Test Signals

- Building this file verifies the test build can compile small C helpers.
- Running the executable should produce the guidance message on stderr and exit with status `1`.
- The absence of dependencies or side effects makes it a stable smoke-test artifact for command-dispatch mistakes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/wrong_command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/utils/install_helper.sh -->
# sources/user-network-fs/sshfs/utils/install_helper.sh

## Purpose

`install_helper.sh` is a Meson install helper for SSHFS. It creates compatibility mount helper names in the system sbin directory by symlinking `mount.sshfs` and `mount.fuse.sshfs` back to the installed `sshfs` executable. The header explicitly warns users not to call it directly because Meson supplies its arguments and installation prefix.

## Important APIs, Types, And Functions

- `set -e` stops the install script on command failure.
- `sbindir="$1"` and `bindir="$2"` consume the directories passed by Meson from `meson.add_install_script('utils/install_helper.sh', get_option('sbindir'), get_option('bindir'))`.
- `prefix="${MESON_INSTALL_DESTDIR_PREFIX}"` uses Meson's install-time destination prefix, including DESTDIR handling.
- `mkdir -p "${prefix}/${sbindir}"` ensures the target sbin directory exists.
- Two `ln -svf --relative` commands create or replace relative symlinks from `${prefix}/${sbindir}/mount.sshfs` and `${prefix}/${sbindir}/mount.fuse.sshfs` to `${prefix}/${bindir}/sshfs`.

## Control Flow

Meson invokes the script during `ninja install` after receiving the configured sbin and bin directory names. The script resolves those arguments, reads Meson's install prefix from the environment, creates the sbin directory under that prefix, then creates the two mount-helper symlinks. `-s` creates symlinks, `-v` logs the operation, `-f` replaces existing paths, and `--relative` makes the links relocatable relative to their target location.

## State And Persistence Behavior

The script mutates the install destination. It creates a directory if needed and overwrites existing `mount.sshfs` and `mount.fuse.sshfs` symlinks or files at the destination. It does not modify repository files. Its behavior depends on `MESON_INSTALL_DESTDIR_PREFIX`, so staged installs and direct installs write to different roots while preserving the same relative link relationship.

## Dependencies And Integration Points

- Requires POSIX shell plus a `ln` implementation supporting GNU `--relative`; this is not universally portable to all POSIX systems.
- Integrated by the repository's top-level `meson.build` through `meson.add_install_script`.
- Supports system mount integration conventions: tools such as `mount -t sshfs` or FUSE helper lookup can find `mount.sshfs` or `mount.fuse.sshfs` in sbin and reach the actual `sshfs` binary in bindir.
- Runs as part of `sudo ninja install` in `travis-build.sh` and normal package/install workflows.

## Risks And Edge Cases

- Argument order matters. If Meson passes bindir and sbindir in the wrong order, the script will create links in the wrong tree; the current Meson call passes sbindir first and bindir second.
- Existing non-symlink files at the mount-helper paths are force-replaced by `ln -f`.
- `MESON_INSTALL_DESTDIR_PREFIX` must be set correctly by Meson; direct manual invocation may produce empty or unintended prefixes.
- GNU `ln --relative` can limit portability on non-GNU userlands.
- The script assumes `sshfs` has already been installed at `${prefix}/${bindir}/sshfs`; if not, it still creates dangling symlinks.

## Test Signals

- `ninja install` completing verifies this script can create the sbin directory and both compatibility symlinks.
- Inspecting the install root should show `mount.sshfs` and `mount.fuse.sshfs` as relative symlinks pointing to the installed `sshfs` binary.
- Packaging or staged-install tests should confirm the links stay inside the staged `MESON_INSTALL_DESTDIR_PREFIX`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/utils/install_helper.sh -->
