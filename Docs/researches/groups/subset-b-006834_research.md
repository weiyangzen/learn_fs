# Research: subset-b-006834 kernel selftest filesystem, firmware, fpu, ftrace, futex, gpio, and hid files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.c

## Purpose
This C utility file provides shared helpers for filesystem selftests that need user namespaces, id maps, capability dropping, mount namespace isolation, robust child waiting, simple proc/sysfs writes, and unique mount IDs. It is support code rather than a standalone test.

## Important APIs, Types, And Functions
Important local types are `enum idmap_type_t`, `struct id_map`, `struct list`, and `struct userns_hierarchy`. Public functions exported through `utils.h` are `get_userns_fd()`, `switch_ids()`, `setup_userns()`, `enter_userns()`, `caps_down()`, `cap_down()`, `wait_for_pid()`, `write_file()`, and `get_unique_mnt_id()`. Internal helpers include `do_clone()`, `write_id_mapping()`, `map_ids_from_idmap()`, `get_userns_fd_from_idmap()`, `create_userns_hierarchy()`, `read_nointr()`, and `write_nointr()`.

## Control Flow
Namespace helpers clone or unshare into new user/mount namespaces, write `/proc/<pid>/{u,g}id_map`, deny `/proc/<pid>/setgroups` when required, synchronize parent/child setup over a socketpair, and then expose `/proc/<pid>/ns/user` as an fd. `setup_userns()` creates a private mount tree after writing the current uid/gid as id 0; `enter_userns()` only creates a user namespace. Capability helpers fetch process caps, clear either all effective caps or one named cap, then install the modified set.

## State And Persistence
The file owns only transient heap, stack, child process, socketpair, and fd state. Persistent effects are process credentials/capabilities, namespace membership, `/proc` id-map writes, and mount propagation changes in the calling test process. `get_unique_mnt_id()` reads `statx()` metadata and does not mutate state.

## Dependencies And Integration Points
The code depends on Linux namespace and capability APIs, `/proc` id-map semantics, libcap, `clone()`, `setns()`, `setresuid()`, `setresgid()`, `mount()`, `statx()`, kselftest logging, and syscall compatibility definitions from `wrappers.h`.

## Risks
The user namespace code is ordering-sensitive: writing gid maps without denying setgroups can fail for unprivileged callers, and the shared `CLONE_VM|CLONE_FILES` hierarchy path requires careful socket/fd cleanup. `map_ids_from_idmap()` has a per-map 4 KiB buffer and returns `-E2BIG` if exceeded. Several functions return negative errno-like values while others return bool-style success, so callers must not mix conventions.

## Test Signals
Good signals are successful id-mapped namespace creation as root and non-root, correct skip/failure messages on blocked user namespaces, successful capability dropping, no leaked child processes, `setup_userns()` leaving mounts private, and nonzero `STATX_MNT_ID_UNIQUE` on kernels that support unique mount IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.h

## Purpose
This header declares the filesystem selftest helper API implemented by `utils.c` and provides the inline `switch_userns()` convenience wrapper.

## Important APIs, Types, And Functions
It exposes namespace helpers `get_userns_fd()`, `setup_userns()`, `enter_userns()`, `switch_userns()`, credential helper `switch_ids()`, capability helpers `caps_down()` and `cap_down()`, process helper `wait_for_pid()`, file helper `write_file()`, and mount identifier helper `get_unique_mnt_id()`. It imports libcap's `cap_value_t` and Linux/user namespace types.

## Control Flow
`switch_userns()` calls `setns(fd, CLONE_NEWUSER)`, switches uid/gid with `switch_ids()`, and optionally drops all effective capabilities through `caps_down()`. Other functions are declarations for callers that include this header in selftest binaries.

## State And Persistence
The header has no mutable state. Its inline wrapper changes caller process namespace, credentials, and effective capabilities when invoked.

## Dependencies And Integration Points
It depends on `_GNU_SOURCE`, `<sys/capability.h>`, Linux namespace headers, and the implementation in `utils.c`. It is intended for tools under `tools/testing/selftests/filesystems`.

## Risks
The bool return from `switch_userns()` hides detailed errno from the failing substep. Callers must understand that namespace and credential changes are process-global and not automatically reversible.

## Test Signals
Compilation with libcap headers, successful linkage with `utils.o`, and tests that can switch to a prepared namespace and then access proc files are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/wrappers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/wrappers.h

## Purpose
This header supplies thin syscall wrappers and fallback constants for newer mount API operations used by filesystem selftests on systems whose libc/kernel headers may be older.

## Important APIs, Types, And Functions
The exported inline wrappers are `sys_fsopen()`, `sys_fsconfig()`, `sys_fsmount()`, `sys_mount()`, `sys_move_mount()`, and `sys_open_tree()`. It also defines compatibility values for `STATX_MNT_ID_UNIQUE`, `MOVE_MOUNT_F_EMPTY_PATH`, `MOVE_MOUNT_T_EMPTY_PATH`, `OPEN_TREE_CLONE`, `OPEN_TREE_CLOEXEC`, `AT_RECURSIVE`, and architecture-specific syscall numbers for `move_mount` and `open_tree`.

## Control Flow
Each wrapper forwards directly to `syscall()` with the appropriate `__NR_*` number. There is no branching beyond compile-time architecture fallback selection.

## State And Persistence
The header has no state. State changes occur only when callers invoke mount syscalls that create fs contexts, configure mounts, clone/open mount trees, or move mounts.

## Dependencies And Integration Points
It integrates tests with Linux's new mount API and raw syscall ABI. It depends on `<linux/mount.h>`, `<sys/syscall.h>`, and architecture preprocessor definitions such as `_MIPS_SIM`.

## Risks
Hard-coded syscall numbers must stay aligned with architecture ABIs. Because wrappers return raw syscall results, callers must handle `-1` and `errno` themselves.

## Test Signals
Build success on architectures with and without libc definitions and runtime mount API tests that either succeed or fail with expected `ENOSYS`/permission errors validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/wrappers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/Makefile

## Purpose
This kselftest Makefile builds the xattr socket test binaries.

## Important APIs, Types, And Functions
It appends `$(KHDR_INCLUDES)` to `CFLAGS`, declares `TEST_GEN_PROGS := xattr_socket_test xattr_sockfs_test xattr_socket_types_test`, and includes `../../lib.mk`.

## Control Flow
The kselftest build system compiles the three C harness tests and installs/runs them as generated test programs.

## State And Persistence
No runtime state is owned by the Makefile. It produces build artifacts under the kselftest output directory.

## Dependencies And Integration Points
It depends on kernel headers and kselftest `lib.mk`. The generated programs exercise VFS xattr behavior on Unix socket path inodes and sockfs inodes.

## Risks
Missing `KHDR_INCLUDES` or older headers can hide constants used by the tests. The Makefile has no per-test skip handling; runtime skip behavior lives in the binaries.

## Test Signals
Successful `make -C tools/testing/selftests/filesystems/xattr` and execution of all three generated binaries are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_test.c

## Purpose
This kselftest verifies path-based extended attribute operations on filesystem-backed Unix domain socket nodes in `/tmp` for `SOCK_STREAM`, `SOCK_DGRAM`, and `SOCK_SEQPACKET`.

## Important APIs, Types, And Functions
The `xattr_socket` fixture creates a bound `AF_UNIX` socket path per socket type. Tests cover `setxattr()`, `getxattr()`, `listxattr()`, `removexattr()`, `lsetxattr()`, `lgetxattr()`, `XATTR_CREATE`, `XATTR_REPLACE`, empty values, size probes, small buffers, nonexistent names, multiple names, and a 4096-byte value. A second `xattr_socket_trusted` fixture checks `trusted.*` behavior with `CAP_SYS_ADMIN` handling.

## Control Flow
Each fixture setup unlinks a unique `/tmp/xattr_socket_test_<type>.<pid>` path, creates the requested Unix socket, binds it, and tears it down by closing and unlinking. Tests then operate on the pathname rather than the socket fd, proving the socket inode's filesystem xattr hooks work.

## State And Persistence
The socket path and xattrs are temporary filesystem state. The persistence test closes the socket fd and confirms the xattr remains available through the path until the node is unlinked. Trusted xattrs may persist only when the caller has the required capability and filesystem support.

## Dependencies And Integration Points
The file depends on Unix domain sockets, the underlying `/tmp` filesystem's socket inode support, VFS xattr syscalls, and `kselftest_harness.h`.

## Risks
`/tmp` may be mounted on a filesystem without the expected socket xattr support, causing environment-specific failures. `trusted.*` results depend on privilege and are skipped/accepted carefully for `EPERM`. Path length and stale socket cleanup are handled but still depend on `/tmp` accessibility.

## Test Signals
Expected pass signals are correct byte counts and values, `ENODATA` after removal/nonexistent lookup, `EEXIST` for create-on-existing, `ERANGE` for too-small buffers, and trusted xattr skip when `CAP_SYS_ADMIN` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_types_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_types_test.c

## Purpose
This test verifies fd-based `user.*` xattrs on sockfs sockets across multiple address families and an abstract Unix socket.

## Important APIs, Types, And Functions
The `xattr_socket_types` fixture variants create `AF_INET`, `AF_INET6`, `AF_NETLINK`, and `AF_PACKET` sockets. The main test uses `fsetxattr()`, `fgetxattr()`, `flistxattr()`, and `fremovexattr()`. The `xattr_abstract` fixture binds an abstract `AF_UNIX` socket and tests fd-based set/get.

## Control Flow
Setup creates the socket for each family and skips unsupported or permission-blocked socket types on `EAFNOSUPPORT`, `EPERM`, or `EACCES`. The test writes a `user.testattr`, verifies retrieval and list membership, removes it, and verifies `ENODATA`.

## State And Persistence
Xattrs are per sockfs inode and exist only while the socket fd and inode live. Abstract Unix sockets have no pathname, so all access is through the fd.

## Dependencies And Integration Points
It integrates with sockfs, networking socket families, Linux netlink headers, AF_PACKET permission behavior, VFS fd xattr syscalls, and kselftest fixture variants.

## Risks
AF_PACKET and netlink availability vary by kernel config and privileges. The test assumes sockfs supports `user.*` xattrs uniformly; regressions may show as set/list/remove failures on only some families.

## Test Signals
Pass signals are successful set/get/list/remove on each available socket family and `futex`-style skip reporting for unavailable families, with `ENODATA` after removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_types_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_sockfs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_sockfs_test.c

## Purpose
This test validates `user.*` extended attributes on anonymous sockfs socket inodes and checks sockfs-specific per-inode limits.

## Important APIs, Types, And Functions
The `xattr_sockfs` fixture creates an unbound `AF_UNIX` stream socket. Tests use `fsetxattr()`, `fgetxattr()`, `flistxattr()`, and `fremovexattr()`. Constants `SIMPLE_XATTR_MAX_NR` and `SIMPLE_XATTR_MAX_SIZE` model sockfs limits, with `XATTR_SIZE_MAX` fallback for older headers.

## Control Flow
Tests cover basic set/get/list/remove/update, create/replace flags, nonexistent names, empty values, size probes, small buffers, maximum xattr count, maximum total value size, freeing limit space after removal, and independence between two socket inodes.

## State And Persistence
All state is in-memory sockfs inode state tied to socket fd lifetimes. The per-inode tests prove values and limits are isolated between two sockets.

## Dependencies And Integration Points
The file depends on sockfs simple xattr support, VFS fd xattr syscalls, kernel xattr limit definitions, and `kselftest_harness.h`.

## Risks
The test encodes expected 128-name and 128 KiB total value limits; kernel changes to `simple_xattrs` accounting require test updates. Large allocations and limit tests can expose off-by-one or cleanup bugs.

## Test Signals
Expected results include `system.sockprotoname` in lists, `ENOSPC` at the 129th xattr and beyond 128 KiB total values, `ERANGE` on undersized reads, and independent values on separate sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_sockfs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/Makefile

## Purpose
This Makefile builds and registers firmware loader selftests.

## Important APIs, Types, And Functions
It sets `CFLAGS = -Wall -O2`, declares `TEST_PROGS := fw_run_tests.sh`, `TEST_FILES := fw_fallback.sh fw_filesystem.sh fw_upload.sh fw_lib.sh`, and `TEST_GEN_FILES := fw_namespace`, then includes `../lib.mk`.

## Control Flow
kselftest builds the `fw_namespace` helper and installs/runs `fw_run_tests.sh`, which invokes the shell test set.

## State And Persistence
Build artifacts are generated in the output tree. Runtime state is owned by the scripts and test firmware kernel module.

## Dependencies And Integration Points
It integrates with kselftest and the kernel `test_firmware` module. The paired `config` file lists required firmware loader Kconfig options.

## Risks
The Makefile assumes all shell scripts are copied as `TEST_FILES`; missing one breaks `fw_run_tests.sh` sourcing or subtest invocation.

## Test Signals
Successful build of `fw_namespace` and installed availability of all firmware shell scripts are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/config

## Purpose
This file documents the kernel configuration requirements for firmware loader selftests.

## Important APIs, Types, And Functions
It requires `CONFIG_TEST_FIRMWARE=y`, `CONFIG_FW_LOADER=y`, `CONFIG_FW_LOADER_USER_HELPER=y`, `CONFIG_IKCONFIG=y`, `CONFIG_IKCONFIG_PROC=y`, and `CONFIG_FW_UPLOAD=y`.

## Control Flow
The shell library prints this file when prerequisites are missing or `/proc/config.gz` cannot confirm support.

## State And Persistence
It has no runtime state; it is a declarative prerequisite list.

## Dependencies And Integration Points
It integrates with `fw_lib.sh` `print_reqs_exit()` and kselftest config reporting.

## Risks
The config list is broad; some subtests can still run without every option, but missing options cause skips or degraded heuristic detection.

## Test Signals
When the running kernel matches these options, `fw_run_tests.sh` should proceed beyond prerequisite checks instead of returning kselftest skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_fallback.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_fallback.sh

## Purpose
This script tests firmware loader sysfs fallback behavior, including manual loading, cancellation, timeout handling, custom fallback triggers, and signal behavior for synchronous requests.

## Important APIs, Types, And Functions
Core helpers are `load_fw()`, `load_fw_cancel()`, `load_fw_custom()`, `load_fw_custom_cancel()`, `load_fw_fallback_with_child()`, `test_syfs_timeout()`, `run_sysfs_main_tests()`, and `run_sysfs_custom_load_tests()`. It manipulates `$DIR/trigger_request`, `$DIR/trigger_custom_fallback`, per-request `loading` and `data` files, `/sys/class/firmware/timeout`, and `/dev/test_firmware`.

## Control Flow
The script sources `fw_lib.sh`, checks modules/config, prepares a temporary firmware file, and installs `test_finish` as cleanup. It blocks kernel requests in the background, waits for the fallback directory to appear, writes `1`, data, and `0` to complete loads, or `-1` to cancel. Main tests run only when fallback support is detected; custom load tests run separately.

## State And Persistence
It mutates firmware class timeout, sysfs fallback request directories, `/dev/test_firmware` contents, and temp files. Cleanup restores timeout/path/proc fallback defaults and removes temporary firmware data.

## Dependencies And Integration Points
It requires root, `test_firmware`, firmware loader user helper fallback support for main fallback tests, and the shared environment exported by `fw_lib.sh`.

## Risks
Distribution udev rules that immediately cancel firmware fallback requests can make the timeout test fail. The script relies on polling loops with short countdowns and assumes request names do not collide with installed firmware.

## Test Signals
Expected signals are timeout failure for nonexistent firmware, mismatched content when intentionally loading the script, successful manual load of the temp firmware, successful cancel paths, SIGCHLD not canceling sync firmware requests, and custom fallback load/cancel success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_fallback.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_filesystem.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_filesystem.sh

## Purpose
This script validates firmware loading from the filesystem, asynchronous requests, platform firmware requests, batched request paths, partial loads, not-found paths, and compressed firmware support.

## Important APIs, Types, And Functions
It uses config helpers such as `config_reset()`, `config_set_name()`, `config_set_into_buf()`, `config_set_partial()`, `config_set_sync_direct()`, `config_set_uevent()`, `config_trigger_sync()`, and `config_trigger_async()`. Readback helpers include `read_firmwares()`, `read_partial_firmwares()`, and `read_firmwares_expect_nofile()`. Test loops are driven by `do_tests()` and `test_request_firmware_compressed()`.

## Control Flow
After shared setup with a custom firmware path, it rejects empty names, verifies direct filesystem loading and async loading, optionally tests platform loading, then exercises batched request variants five times each with present, missing, and compressed firmware. Partial into-buffer requests validate offset/length slicing.

## State And Persistence
It changes `/sys/module/firmware_class/parameters/path`, writes many config knobs under `$DIR`, writes/readbacks `/dev/test_firmware` and `$DIR/read_firmware`, creates compressed firmware companions, and releases firmware between batched cases.

## Dependencies And Integration Points
The script depends on `test_firmware` sysfs control files, optional XZ/ZSTD compression tools and Kconfig support, optional platform trigger support, and `fw_lib.sh`.

## Risks
It assumes the test driver's sysfs ABI names are present; missing batched triggers cause skips. Compression tests depend on external tools. The readback comparison uses `diff -q -Z`, so whitespace behavior is intentionally tolerated.

## Test Signals
Pass signals include empty filename rejection, direct and async filesystem load success, platform load success when supported, nofile cases not hanging and not matching stale firmware, correct partial data, and success for both plain-preferred and compressed-only modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_filesystem.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_lib.sh

## Purpose
This shell library centralizes prerequisite checks, Kconfig detection, firmware temp-file setup, proc/sysfs fallback toggles, and cleanup for firmware loader selftests.

## Important APIs, Types, And Functions
Key functions are `print_reqs_exit()`, `test_modprobe()`, `check_mods()`, `check_setup()`, `verify_reqs()`, `setup_tmp_file()`, `setup_random_file()`, `setup_random_file_fake()`, `proc_set_force_sysfs_fallback()`, `proc_set_ignore_sysfs_fallback()`, `proc_restore_defaults()`, `test_finish()`, and `kconfig_has()`. Important variables include `DIR`, `PROC_CONFIG`, `FW_FORCE_SYSFS_FALLBACK`, `FW_IGNORE_SYSFS_FALLBACK`, `OLD_TIMEOUT`, `OLD_FWPATH`, `HAS_FW_*`, `FW`, `FW_INTO_BUF`, and `NAME`.

## Control Flow
Tests call `check_mods()` to require root and load `test_firmware` and optionally `configs`, `check_setup()` to detect kernel capabilities and save old tunables, `verify_reqs()` to skip unsupported test modes, and `setup_tmp_file()` before manipulating firmware paths. `test_finish()` restores global firmware loader settings and removes temp files.

## State And Persistence
The library mutates global shell variables, `/sys/class/firmware/timeout`, `/sys/module/firmware_class/parameters/path`, `/proc/sys/kernel/firmware_config/*`, and temporary firmware directories. Cleanup is essential because those knobs are global kernel state.

## Dependencies And Integration Points
It integrates with `test_firmware`, `/proc/config.gz`, optional `configs` module, firmware loader proc/sysfs knobs, external compression tools detected by `which`, and kselftest skip code `4`.

## Risks
Unquoted variable tests such as `[ -z $PROC_SYS_DIR ]` can be sensitive to unusual values. Old heuristic Kconfig detection can overestimate fallback support when `/proc/config.gz` is absent. Cleanup must run through traps to avoid leaving global firmware settings modified.

## Test Signals
Good signals are root prerequisite enforcement, accurate skip when `test_firmware` or upload support is missing, restoration of timeout/path/fallback toggles after every script, and correct creation of temp firmware names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_namespace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_namespace.c

## Purpose
This helper tests that firmware requests use the mount namespace of PID 1 rather than the caller's private mount namespace.

## Important APIs, Types, And Functions
Important functions are `die()`, `trigger_fw()`, `setup_fw()`, `test_fw_in_ns()`, and `main()`. It manipulates `/lib/firmware`, a temporary `test-firmware.bin`, mount namespaces through `unshare(CLONE_NEWNS)`, and the sysfs trigger path supplied as argv[1].

## Control Flow
`main()` mounts tmpfs on `/lib/firmware`, writes firmware, then runs a positive case where the child hides firmware only in its own namespace and a negative case where the parent namespace blocks firmware while the child namespace exposes it. `test_fw_in_ns()` forks, adjusts mount propagation to slave in the child, mounts or unmounts tmpfs depending on the scenario, triggers firmware, and reports child exit status.

## State And Persistence
It temporarily mounts tmpfs over `/lib/firmware`, creates and unlinks a firmware file, and unmounts on exit/error. Failed cleanup can leave a test mount behind.

## Dependencies And Integration Points
It requires root, mount namespace support, writable mount operations on `/lib/firmware`, and the `test_firmware` sysfs trigger passed by `fw_run_tests.sh`.

## Risks
The test assumes the initial mount namespace is equivalent to PID 1 for firmware loading. `die()` unmounts `/lib/firmware` globally, so running on non-isolated systems is invasive. The negative case depends on firmware not being found through any other loader path.

## Test Signals
Pass signals are success when firmware exists in the parent/PID1 namespace and failure when firmware exists only in the child namespace, followed by clean unmount and unlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_run_tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_run_tests.sh

## Purpose
This top-level firmware selftest runner orchestrates namespace, filesystem, fallback, and upload tests under several emulated firmware loader configurations.

## Important APIs, Types, And Functions
It sources `fw_lib.sh`, defines `run_tests()`, `run_test_config_0001()`, `run_test_config_0002()`, and `run_test_config_0003()`, and toggles fallback behavior through `proc_set_force_sysfs_fallback()` and `proc_set_ignore_sysfs_fallback()`.

## Control Flow
The script requires modules/setup, runs `fw_namespace $DIR/trigger_request`, then either runs three emulated configurations when `force_sysfs_fallback` exists or runs the three subtests once under the current kernel config. Each config calls `fw_filesystem.sh`, `fw_fallback.sh`, and `fw_upload.sh`.

## State And Persistence
It mutates proc firmware fallback toggles and relies on subtests to restore per-test settings. The exported `HAS_FW_*` variables are recalculated by `fw_lib.sh`.

## Dependencies And Integration Points
It integrates all firmware selftest scripts and the compiled namespace helper. It requires the `test_firmware` module and root privileges through `check_mods()`.

## Risks
Because it uses `set -e`, an unhandled failure in any subtest aborts later configurations. Running all emulations changes global firmware loader proc knobs between subtests, making cleanup ordering important.

## Test Signals
A successful run prints the namespace `OK` and completes filesystem, fallback, and upload tests for each supported/emulated configuration without leaving proc knobs forced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_run_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_upload.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_upload.sh

## Purpose
This script validates the firmware upload sysfs interface using the `test_firmware` driver, covering registration, data transfer, cancellation, error injection, size rejection, and multiple upload devices.

## Important APIs, Types, And Functions
Important helpers are `upload_finish()`, `upload_fw()`, `verify_fw()`, `inject_error()`, `await_status()`, `await_idle()`, `expect_error()`, `random_firmware()`, `test_upload_cancel()`, `test_error_handling()`, and `test_fw_too_big()`. It uses `$DIR/upload_register`, `$DIR/upload_unregister`, `$DIR/<name>/loading`, `$DIR/<name>/data`, `$DIR/<name>/status`, `$DIR/<name>/error`, `$DIR/<name>/cancel`, `$DIR/config_upload_name`, and `$DIR/upload_read`.

## Control Flow
After upload support verification, it registers three firmware upload devices. It injects user-abort at each progress state, injects all defined hardware/error codes at each progress state, tests oversized firmware, uploads random firmware to three devices, verifies readback, then unregisters them.

## State And Persistence
It creates kernel upload device instances, temporary random files under `/tmp`, and sysfs upload state. `upload_finish()` unregisters remaining devices through an EXIT trap.

## Dependencies And Integration Points
It requires `CONFIG_FW_UPLOAD`, the `test_firmware` upload test ABI, root, `dd`, `/dev/urandom`, and `fw_lib.sh`.

## Risks
The polling loop in `await_status()` is short and assumes status changes within about 50 milliseconds. Random firmware temp files for successful uploads are not explicitly removed after verification. Error strings must match the kernel test driver's exact accepted values.

## Test Signals
Pass signals include correct cancellation errors of form `<state>:user-abort`, correct injected errors for every state/error pair, `preparing:invalid-file-size` for too-large upload, and byte-for-byte readback of all three random firmware images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_upload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/Makefile

## Purpose
This Makefile builds and registers the kernel FPU selftest helper.

## Important APIs, Types, And Functions
It links with `-lm`, declares `TEST_GEN_PROGS := test_fpu`, `TEST_PROGS := run_test_fpu.sh`, and includes `../lib.mk`.

## Control Flow
kselftest builds `test_fpu` and runs the shell wrapper, which loads the kernel module and invokes many user-space helper instances.

## State And Persistence
The Makefile only produces build artifacts.

## Dependencies And Integration Points
It depends on libm for fenv functions and kselftest `lib.mk`.

## Risks
Missing math library linkage breaks `fesetround()`/`feenableexcept()` references.

## Test Signals
Successful compilation of `test_fpu` and execution through `run_test_fpu.sh` validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/run_test_fpu.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/run_test_fpu.sh

## Purpose
This shell wrapper loads the `test_fpu` kernel module, ensures debugfs access to its helper file, and runs the user-space FPU test repeatedly across all online CPUs.

## Important APIs, Types, And Functions
It uses `modprobe`, `modinfo`, `getconf _NPROCESSORS_ONLN`, `mount -t debugfs`, `/sys/kernel/debug/selftest_helpers/test_fpu`, `./test_fpu`, and `rmmod`.

## Control Flow
The script requires root and modprobe, skips if `CONFIG_TEST_FPU=m` is unavailable, loads `test_fpu`, mounts debugfs if needed, then starts `NR_CPUS` copies of `test_fpu` for each of 1000 iterations before unloading the module.

## State And Persistence
It mutates kernel module state and may mount debugfs. It does not explicitly wait for every background `test_fpu` before `rmmod`, relying on shell job behavior and module reference constraints.

## Dependencies And Integration Points
It integrates with the `test_fpu` kernel module and `test_fpu.c` binary.

## Risks
Running `1000 * NR_CPUS` processes can stress small systems. The script returns `1` for root/modprobe errors but `4` for missing prerequisites, matching kselftest skip only for some cases.

## Test Signals
Expected signals are successful module load, debugfs helper availability, many `[OK] test_fpu` helper outputs, and clean `rmmod`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/run_test_fpu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/test_fpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/test_fpu.c

## Purpose
This helper verifies that kernel FPU use by the `test_fpu` module does not corrupt user-mode floating point control state.

## Important APIs, Types, And Functions
`main()` opens `/sys/kernel/debug/selftest_helpers/test_fpu`, reads from it under default rounding, after `fesetround(FE_DOWNWARD)`, and after `feenableexcept(FE_ALL_EXCEPT)`. It checks `fegetround()` and `fegetexcept()`.

## Control Flow
Open failure prints `[SKIP]` and returns success. Each read triggers kernel module floating point work. The helper returns distinct failure codes if default access fails, downward rounding access fails, rounding mode is clobbered, unmasked exception access fails, or exception mask is clobbered.

## State And Persistence
It changes only the calling process FPU rounding mode and exception mask and reads a debugfs file. The expected persistent condition is that user FPU state remains unchanged across kernel entry/exit.

## Dependencies And Integration Points
It depends on libm/fenv, debugfs, and the `test_fpu` kernel module.

## Risks
The unmasked exception phase can expose severe kernel FPU bugs and potentially crash a broken kernel, as noted in the source. Open failure returns 0 with `[SKIP]`, so wrapper-level skip accounting may be weak.

## Test Signals
Pass output is `[OK]\ttest_fpu`; failures identify the precise state corruption or access phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/test_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/Makefile

## Purpose
This Makefile registers the ftrace shell test suite and builds the `poll` helper.

## Important APIs, Types, And Functions
It declares `TEST_PROGS_EXTENDED := ftracetest`, `TEST_PROGS := ftracetest-ktap`, `TEST_FILES := test.d settings`, `EXTRA_CLEAN := $(OUTPUT)/logs/*`, `TEST_GEN_FILES := poll`, and includes `../lib.mk`.

## Control Flow
kselftest builds `poll`, installs the test directory and settings, and runs `ftracetest-ktap`, which delegates to `ftracetest -K -v`.

## State And Persistence
Build artifacts and logs are generated in the output tree; runtime tracing state is managed by `ftracetest`.

## Dependencies And Integration Points
It integrates with tracefs/debugfs ftrace test cases and the kselftest runner.

## Risks
All real feature requirements are in `config` and per-`.tc` metadata, so Makefile success alone does not prove runtime coverage.

## Test Signals
Successful `poll` build and KTAP output from `ftracetest-ktap` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/config

## Purpose
This file lists kernel configuration options needed for broad ftrace selftest coverage.

## Important APIs, Types, And Functions
It requires ftrace, kprobe/uprobe, eprobe/fprobe, BTF, histogram triggers, syscall tracing, function graph return values, IRQ/preempt tracers, stack/snapshot/profiler support, modules, samples, and delay-test modules.

## Control Flow
kselftest uses this as prerequisite documentation/config checking data; individual `ftracetest` cases still evaluate runtime files and README strings.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
It maps to ftrace features under tracefs and module-based samples used by `test.d`.

## Risks
Config options may be necessary but not sufficient; tracefs permissions, module availability, and architecture support can still skip or fail tests.

## Test Signals
Kernels satisfying this config should expose the required tracefs files, tracers, and README feature strings for most ftrace `.tc` cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest

## Purpose
This shell harness discovers, filters, runs, logs, and summarizes ftrace and RV selftests from `test.d`.

## Important APIs, Types, And Functions
Important functions include `usage()`, `setup()`, `cleanup()`, `errexit()`, `absdir()`, `abspath()`, `find_testcases()`, `parse_opts()`, `strip_esc()`, `prlog()`, `catlog()`, `testcase()`, `checkreq()`, `test_on_instance()`, `ktaptest()`, `eval_result()`, `exit_pass()`, `exit_fail()`, `exit_unresolved()`, `exit_untested()`, `exit_unsupported()`, `exit_xfail()`, `__run_test()`, and `run_test()`. It sources `test.d/functions`.

## Control Flow
The script requires root, disables RT runtime throttling, locates or mounts tracefs/debugfs, parses options, prepares logs, discovers `.tc` files, then runs each test in tracefs with `set -e` and helper functions loaded. Signal traps map special exit helpers to Dejagnu-style result codes. Tests marked for instance mode are run again in a temporary trace instance. KTAP mode emits TAP version, plan, per-test lines, and totals.

## State And Persistence
It changes `/proc/sys/kernel/sched_rt_runtime_us`, may mount tracefs/debugfs, creates logs and `latest` symlink under `logs/`, exports temporary directories, creates/removes trace instances, and relies on `initialize_system`/`finish_system` from `test.d/functions` to reset tracing state.

## Dependencies And Integration Points
It integrates with tracefs/debugfs, ftrace test metadata (`# description`, `# requires`, `# flags`), kselftest skip code, KTAP output, and RV tests under tracefs `rv`.

## Risks
Global scheduler RT runtime is modified for the duration and must be restored. Test scripts run sourced in a shell with `set -e`, so cleanup in individual cases must be robust. Mount discovery and user-provided log paths can affect host state.

## Test Signals
Signals include correct root/tracefs skip behavior, per-test PASS/FAIL/UNSUPPORTED/UNRESOLVED accounting, cleanup of temporary trace instances, restored RT runtime, and valid KTAP totals in `-K` mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest-ktap -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest-ktap

## Purpose
This wrapper adapts `ftracetest` to kselftest's expected KTAP output.

## Important APIs, Types, And Functions
It runs `./ftracetest -K -v` under `sh -e`.

## Control Flow
kselftest invokes this script as `TEST_PROGS`; the script immediately delegates to the main harness with KTAP and verbose mode enabled.

## State And Persistence
All state changes are from `ftracetest`; the wrapper has none of its own.

## Dependencies And Integration Points
It depends on `ftracetest` being present and executable in the same directory.

## Risks
Any nonzero `ftracetest` exit is propagated because `-e` is active.

## Test Signals
Expected output starts with KTAP/TAP formatting and exits with the aggregate ftrace test status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest-ktap -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/poll.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/poll.c

## Purpose
This small helper polls a file for `POLLIN` or `POLLPRI` events and is used by ftrace tests that need deterministic polling of tracefs files.

## Important APIs, Types, And Functions
`main()` parses `-I`, `-P`, and `-t timeout`, opens the target file, optionally drains it before `POLLIN`, calls `poll()`, and maps timeout to exit code `1`.

## Control Flow
The helper defaults to infinite timeout and `POLLIN`. For `POLLIN`, it reads in 4096-byte chunks until a short read to reset readiness, then polls one fd. `EINTR` is treated as a non-timeout return path, while other poll errors fail.

## State And Persistence
It reads but does not otherwise mutate the target file. Draining tracefs files can consume pending data intentionally.

## Dependencies And Integration Points
It depends on POSIX `poll()`, `open()`, `read()`, and tracefs/debugfs file semantics.

## Risks
Returning `0` for interrupted polls may be interpreted as event success by callers. The usage error path returns `-1`, which maps to shell exit 255.

## Test Signals
Exit `0` means event or interrupt, exit `1` means timeout, and exit 255/error output indicates open/poll/argument failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/test.d/template -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/test.d/template

## Purpose
This file is a skeleton for new ftrace `.tc` shell test cases.

## Important APIs, Types, And Functions
It documents required metadata lines `# description:` and `# requires:` and the result helpers `exit_pass`, `exit_fail`, `exit_unsupported`, `exit_unresolved`, `exit_untested`, and `exit_xfail`.

## Control Flow
The template exits `0` by default. Real tests are sourced by `ftracetest` under `set -e` from the tracefs directory after requirements are checked.

## State And Persistence
The template has no state. Real tests may mutate tracefs and should rely on harness cleanup helpers.

## Dependencies And Integration Points
It integrates with `ftracetest` metadata parsing and `test.d/functions` helper API.

## Risks
Leaving the template unchanged as a `.tc` would create a meaningless passing test. Requirement strings need correct `:tracer` or `:README` suffixes to avoid false skips/failures.

## Test Signals
For a real test derived from it, a correct description appears in harness output and the chosen exit helper maps to the intended result code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/test.d/template -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/Makefile

## Purpose
This top-level futex selftest Makefile delegates build, install, and clean operations to the `functional` subdirectory.

## Important APIs, Types, And Functions
It defines `SUBDIRS := functional`, `TEST_PROGS := run.sh`, custom `all`, `INSTALL_RULE`, and `CLEAN` blocks, and includes `../lib.mk`.

## Control Flow
The `all` target creates per-subdir output directories, invokes `make -C functional`, and copies subdir `run.sh` into the output tree. Install and clean recurse similarly.

## State And Persistence
It creates output directories and installed test files.

## Dependencies And Integration Points
It integrates `functional/Makefile` with kselftest's top-level futex entry point.

## Risks
Recursive output path handling must stay aligned with `lib.mk`; missing `rsync` would break copying the subdir runner.

## Test Signals
Successful recursive build of all functional programs and executable top-level `run.sh` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/Makefile

## Purpose
This Makefile builds the futex functional test binaries and conditionally links libnuma support for NUMA/MPOL tests.

## Important APIs, Types, And Functions
It detects `pkg-config numa --atleast-version 2.0.18`, sets include paths to futex headers and kselftest headers, enables pthread/time64 flags, links `-lpthread -lrt` and optional `-lnuma`, and declares all functional `TEST_GEN_PROGS`.

## Control Flow
kselftest compiles wait, requeue, PI, waitv, NUMA, private hash, and robust list tests and installs `run.sh`.

## State And Persistence
It creates build outputs only.

## Dependencies And Integration Points
It depends on kernel headers, futex local headers, pthread, rt, optional libnuma, and kselftest `lib.mk`.

## Risks
The `LIBNUMA_VER_*` define changes runtime coverage; without sufficient libnuma the MPOL subtest reports skip. Time64 flags intentionally affect syscall wrapper selection.

## Test Signals
All listed binaries compile, and `futex_numa_mpol` reports MPOL pass only when libnuma is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa.c

## Purpose
This stress test exercises futex2 NUMA-aware wait/wake behavior with a custom 64-bit lock word that stores both lock bits and a NUMA node hint.

## Important APIs, Types, And Functions
Important types are `struct futex_numa_32` and `struct thread_args`. Functions include `futex_numa_32_lock()`, `futex_numa_32_unlock()`, `threadfn()`, `contendfn()`, and `main()`. It uses `futex2_wait()` and `futex2_wake()` with `FUTEX2_SIZE_U32`, `FUTEX2_PRIVATE`, optional `FUTEX2_NUMA`, and optional node value.

## Control Flow
Command-line options set worker count, contender count, sleep duration, nanosleep time, and NUMA mode. Worker threads take the custom lock, update paired counters with an invariant check, observe the node field, and unlock. Contender threads intentionally call futex2 wait with a wrong value to create hash-bucket contention.

## State And Persistence
All state is in process memory: global `done`, `lock`, `val1`, and `val2`, plus per-thread counters. The futex node field is kernel-written state in the shared lock word.

## Dependencies And Integration Points
It depends on futex2 wait/wake syscalls, pthreads, atomic builtins, and kernel NUMA futex support.

## Risks
Assertions abort the process on invariant or wake assumptions. The fixed arrays allow at most 512 workers/contenders but input is not bounded against that size. Futex2 syscall availability varies by kernel.

## Test Signals
Expected output includes observed node changes and final total/contender counts without assertion failures or deadlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa_mpol.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa_mpol.c

## Purpose
This kselftest verifies futex2 NUMA node initialization, memory boundary validation, and optional memory-policy-derived node hints.

## Important APIs, Types, And Functions
It defines `thread_lock_fn()`, `create_max_threads()`, `join_max_threads()`, `__test_futex()`, `test_futex()`, and `TEST(futex_numa_mpol)`. It uses `struct futex32_numa`, `futex2_wait()`, `futex2_wake()`, `mmap()`, `mprotect()`, optional `mbind()`, and `numa_set_mempolicy_home_node()`.

## Control Flow
The test maps two pages, protects the second page, launches 64 waiters, and wakes them while checking success or expected errors. It verifies regular NUMA initialization, misaligned address `EINVAL`, out-of-range and read-only/no-access `EFAULT`, restored RW success, and optional MPOL node selection.

## State And Persistence
State is anonymous memory protection and futex/numa fields in the mapped page. Optional memory policy is applied to the mapping only.

## Dependencies And Integration Points
It depends on futex2 NUMA flags, pthread barriers, memory protection faults, kselftest harness, and optional libnuma 2.0.18+.

## Risks
Pointer arithmetic on `void *` relies on GNU C. The MPOL section is skipped without libnuma and may be sensitive to available NUMA nodes and permissions.

## Test Signals
Pass signals include non-`FUTEX_NO_NODE` after regular wake, correct `EINVAL`/`EFAULT` cases, pass for RW retry, and MPOL pass or explicit skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa_mpol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_priv_hash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_priv_hash.c

## Purpose
This test validates the `PR_FUTEX_HASH` prctl interface for private futex hash bucket sizing, automatic initialization/scaling, manual settings, and global-hash fallback.

## Important APIs, Types, And Functions
Important helpers are `futex_hash_slots_set()`, `futex_hash_slots_get()`, `futex_hash_slots_set_verify()`, `futex_hash_slots_set_must_fail()`, `thread_return_fn()`, `thread_lock_fn()`, `create_max_threads()`, `join_max_threads()`, and `futex_dummy_op()`. It uses `pthread_mutex` with `PTHREAD_PRIO_INHERIT` to force futex operations.

## Control Flow
The test observes initial slot count, creates a thread to trigger private hash initialization, optionally checks automatic growth on systems with more than 16 CPUs, verifies accepted manual power-of-two slot counts, rejects invalid values, confirms manual settings disable auto-resize, then requests global hash with slot count 0 and verifies later private settings fail.

## State And Persistence
It changes process-level futex hash configuration via `prctl()`, creates many threads, and uses global counter/lock/barrier state. The prctl state persists for the process.

## Dependencies And Integration Points
It depends on kernel support for `PR_FUTEX_HASH`, pthread PI mutexes, RCU-delayed private hash replacement behavior, and kselftest harness.

## Risks
Auto-scaling is timing-sensitive; the retry loop uses timed mutex operations to wait for RCU grace periods. Systems with <=16 CPUs skip that part. Unsupported prctl will fail early.

## Test Signals
Pass signals include positive slot count after first thread, optional increased slots on large systems, exact get-after-set values, rejection of bad sizes, stable manual size after more threads, and permanent global hash state after setting 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_priv_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue.c

## Purpose
This test verifies non-PI `FUTEX_CMP_REQUEUE` behavior for moving waiters from one futex to another.

## Important APIs, Types, And Functions
It defines `waiterfn()`, `TEST(requeue_single)`, and `TEST(requeue_multiple)`, using `futex_wait()`, `futex_cmp_requeue()`, and `futex_wake()`.

## Control Flow
Waiter threads block on `f1` with a short timeout. The single test requeues one waiter from `f1` to `f2` and wakes it. The multiple test creates ten waiters, wakes three and requeues seven, then wakes exactly seven from `f2`.

## State And Persistence
State is local futex words and pthread waiters. No persistent system state is modified.

## Dependencies And Integration Points
It depends on pthreads, the local `futextest.h` wrappers, and kselftest harness.

## Risks
The test uses `usleep(WAKE_WAIT_US)` rather than a deterministic barrier, so very slow systems can race waiter blocking. Waiter threads are not explicitly joined, relying on test process exit after wake checks.

## Test Signals
Expected syscall return counts are `1` then `1` in the single case and `10` then `7` in the multiple case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi.c

## Purpose
This test exercises priority-inheritance requeue operations used to implement PI-aware condition variables and mutexes.

## Important APIs, Types, And Functions
Important globals are `waiters_blocked`, `waiters_woken`, `f1`, `f2`, and `wake_complete`. Helpers include `create_rt_thread()`, `waiterfn()`, `broadcast_wakerfn()`, `signal_wakerfn()`, and `third_party_blocker()`. The fixture variants cover timeout lengths, broadcast vs signal, waker-held PI lock, and third-party owner.

## Control Flow
For each variant, ten RT waiter threads call `futex_wait_requeue_pi()` on `f1` targeting PI futex `f2`. A waker either signals one at a time or broadcasts through `futex_cmp_requeue_pi()`, optionally while holding `f2`. A third-party blocker variant owns `f2` until wake completion. Waiters unlock `f2` after return or after taking it on timeout.

## State And Persistence
All state is process-local futex words, atomic counters, RT pthread attributes, and optional timeout structs. It temporarily consumes realtime scheduling capability.

## Dependencies And Integration Points
It depends on PI futex operations, realtime scheduling (`SCHED_FIFO`), pthreads, kselftest fixture variants, and the `atomic.h` helpers.

## Risks
Creating RT threads may require privileges and can fail under scheduling restrictions. The code relies on sleeps and iteration bounds to avoid races; a failure can leave waiters hung if kernel PI requeue behavior regresses.

## Test Signals
Good signals are all variant combinations completing, `task_count` reaching expected waiter counts, no unexpected `futex_wait_requeue_pi()` errors except allowed timeouts, and no stuck PI lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_mismatched_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_mismatched_ops.c

## Purpose
This regression test ensures the kernel rejects `FUTEX_CMP_REQUEUE_PI` when the waiter used plain `FUTEX_WAIT` instead of `FUTEX_WAIT_REQUEUE_PI`.

## Important APIs, Types, And Functions
It defines globals `f1`, `f2`, `child_ret`, helper `blocking_child()`, and `TEST(requeue_pi_mismatched_ops)`. It uses `futex_wait()`, `futex_cmp_requeue_pi()`, and `futex_wake()`.

## Control Flow
A child thread blocks in plain `futex_wait()` on `f1`. The parent sleeps briefly, then calls `futex_cmp_requeue_pi()` from `f1` to `f2`. Correct behavior is `-1/EINVAL`, after which the parent wakes the child using non-PI `FUTEX_WAKE` and joins it.

## State And Persistence
State is two process-local futex words and one child thread.

## Dependencies And Integration Points
It depends on PI futex validation, pthreads, and kselftest harness.

## Risks
If the kernel fails to detect the mismatch, it may incorrectly hand a PI lock to a waiter not prepared for it and hang. The final `else` path appears to print pass text for a failure string, which can weaken result reporting.

## Test Signals
The key signal is `FUTEX_CMP_REQUEUE_PI` returning `EINVAL`, followed by `FUTEX_WAKE` waking exactly one child and a clean join.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_mismatched_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_signal_restart.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_signal_restart.c

## Purpose
This test verifies signal handling around `futex_wait_requeue_pi()` before and after requeue.

## Important APIs, Types, And Functions
Important helpers are `create_rt_thread()`, `handle_signal()`, `waiterfn()`, and `TEST(futex_requeue_pi_signal_restart)`. It uses `futex_wait_requeue_pi()`, `futex_cmp_requeue_pi()`, `futex_lock_pi()`, `futex_unlock_pi()`, `pthread_kill()`, and atomic flag `requeued`.

## Control Flow
The parent installs a SIGUSR1 handler, starts an RT waiter on `f1`, locks PI futex `f2`, repeatedly signals the waiter before requeue until `futex_cmp_requeue_pi()` succeeds, marks requeued, then signals after requeue. The waiter should restart before requeue and return with `EWOULDBLOCK` after requeue.

## State And Persistence
State is process-local futexes, signal handler state, one RT thread, and the atomic `requeued` flag.

## Dependencies And Integration Points
It depends on PI futex restart behavior, POSIX signals, realtime scheduling, pthreads, and `atomic.h`.

## Risks
Timing is deliberately racy before requeue; the parent loops until the signal and waiter blocking order allows requeue. RT thread creation may fail without privileges.

## Test Signals
Expected behavior is no failure from pre-requeue signals, successful requeue, waiter observing post-requeue `EWOULDBLOCK`, and successful final `FUTEX_UNLOCK_PI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_signal_restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait.c

## Purpose
This test validates basic `FUTEX_WAIT`/`FUTEX_WAKE` behavior for private, SysV shared-memory, and file-backed shared futexes.

## Important APIs, Types, And Functions
It defines shared global `void *futex`, helper `waiterfn()`, and tests `private_futex`, `anon_page`, and `file_backed`. It uses `futex_wait()`, `futex_wake()`, `shmget()`, `shmat()`, `mmap(MAP_SHARED)`, and a temporary `futex_shm_file`.

## Control Flow
Each test places a zero-valued futex in the target backing type, starts a waiter with a short timeout, sleeps to let it block, then wakes one waiter and expects return count `1`.

## State And Persistence
It creates transient pthreads, SysV shared memory attachment, and a temporary file-backed mapping. The file is removed at the end of the file-backed test.

## Dependencies And Integration Points
It depends on System V shared memory support, filesystem-backed shared mappings, pthreads, and futex wrappers.

## Risks
Waiter synchronization uses `usleep`, so extreme scheduling delay can race. The SysV segment is detached but not explicitly marked for removal with `shmctl(IPC_RMID)`, which is a cleanup concern.

## Test Signals
Each backing type should report a pass when `futex_wake()` returns exactly one woken waiter; `shmget ENOSYS` skips the shared-memory case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_private_mapped_file.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_private_mapped_file.c

## Purpose
This regression test targets private file mapping futex key transitions where a mapping may behave like file-backed before write and anonymous after copy-on-write.

## Important APIs, Types, And Functions
It uses global page-aligned padding around `futex_t val`, `wait_timeout`, helper `thr_futex_wait()`, and `TEST(wait_private_mapped_file)`. The futex operations are `futex_wait(&val, 1, timeout, 0)` and `futex_wake(&val, 1, 0)`.

## Control Flow
A thread waits on `val == 1`. The parent sleeps long enough for the waiter to block, changes `val` to `2`, wakes the futex, and expects exactly one waiter found and no timeout.

## State And Persistence
All state is process memory and one pthread.

## Dependencies And Integration Points
It depends on futex key handling for private mappings, pthreads, and kselftest harness.

## Risks
The test relies on a long fixed `WAKE_WAIT_US` sleep. It does not actually create an external file mapping in this source version; the regression signal is tied to the binary's private executable/data mapping layout.

## Test Signals
Pass requires the waiter not timing out and `FUTEX_WAKE` returning `1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_private_mapped_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_timeout.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_timeout.c

## Purpose
This test validates timeout behavior for multiple futex wait operations, including classic waits, bitset waits, PI lock waits, requeue-PI waits, and futex2 `waitv`.

## Important APIs, Types, And Functions
Important functions are `get_pi_lock()`, `test_timeout()`, `futex_get_abs_timeout()`, and tests `wait_bitset`, `requeue_pi`, `lock_pi`, and `waitv`. It calls `futex_wait()`, `futex_wait_bitset()`, `futex_wait_requeue_pi()`, `futex_lock_pi()`, and `futex_waitv()`.

## Control Flow
The wait-bitset and requeue tests compute relative or absolute timeouts for monotonic and realtime clocks and expect `ETIMEDOUT`. The lock-PI test starts a thread that locks `futex_pi` forever, then verifies the main thread times out trying to lock it and rejects unsupported timeout flags. The waitv test checks monotonic and realtime absolute timeouts.

## State And Persistence
State is local futex words, a global PI futex, one barrier, and a helper thread that blocks indefinitely within the process.

## Dependencies And Integration Points
It depends on futex classic and futex2 syscalls, PI futex support, pthread barriers, and kselftest harness.

## Risks
The helper thread intentionally blocks forever after taking the PI lock; test process teardown must end it. Historical `FUTEX_LOCK_PI` realtime semantics are subtle and encoded in the expected flags.

## Test Signals
Pass signals are nonzero syscall returns with `errno == ETIMEDOUT` for timeout paths and `ENOSYS` for invalid `FUTEX_CLOCK_REALTIME` on `FUTEX_LOCK_PI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_uninitialized_heap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_uninitialized_heap.c

## Purpose
This test checks that waiting on an uninitialized anonymous heap page does not incorrectly block when the expected value does not match zero-filled memory.

## Important APIs, Types, And Functions
It defines globals `child_blocked`, `child_ret`, and `buf`, helper `wait_thread()`, and `TEST(futex_wait_uninitialized_heap)`. It uses `mmap(MAP_PRIVATE|MAP_ANONYMOUS)` and `futex_wait(buf, 1, NULL, 0)`.

## Control Flow
The parent maps a zero-filled page and starts a thread that waits for value `1`. Because the actual value is zero, the futex syscall should immediately return `EWOULDBLOCK`. After a fixed sleep the parent fails if the child is still blocked or reported an unexpected errno.

## State And Persistence
Only anonymous memory and thread flags are used.

## Dependencies And Integration Points
It depends on zero-page handling in futex value comparison, pthreads, mmap, and kselftest harness.

## Risks
There is no `pthread_join()` before test exit. The child status variables are unsynchronized plain globals, which is acceptable for this simple timing test but not a general pattern.

## Test Signals
Pass requires the child to return promptly and accept only `EWOULDBLOCK` for the mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_uninitialized_heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_wouldblock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_wouldblock.c

## Purpose
This test verifies immediate `EWOULDBLOCK` behavior when classic `futex_wait` and futex2 `waitv` expected values do not match the current futex word.

## Important APIs, Types, And Functions
It defines `TEST(futex_wait_wouldblock)` and `TEST(futex_waitv_wouldblock)`, using `futex_wait()` and `futex_waitv()` with an expected value of `f1 + 1`.

## Control Flow
The classic test uses a short relative timeout but expects immediate `EWOULDBLOCK`. The waitv test computes an absolute monotonic timeout, sets one waiter entry with mismatched value, and also expects immediate `EWOULDBLOCK`.

## State And Persistence
State is local futex words and a local `struct futex_waitv`.

## Dependencies And Integration Points
It depends on futex classic and futex2 value-check semantics and the kselftest harness.

## Risks
The waitv failure checks compare `errno` after `res`, so syscall wrapper conventions must be understood. A kernel that incorrectly waits would make the test timeout or fail.

## Test Signals
Both tests pass only when the syscall returns failure with `errno == EWOULDBLOCK`, not a timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_wouldblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_waitv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_waitv.c

## Purpose
This test covers futex2 `futex_waitv()` waiting on multiple futexes, for private and shared futex arrays plus invalid-argument cases.

## Important APIs, Types, And Functions
It uses global `waitv[NR_FUTEXES]`, `futexes[NR_FUTEXES]`, helper `waiterfn()`, and tests `private_waitv`, `shared_waitv`, `invalid_flag`, `unaligned_address`, `null_address`, and `invalid_clockid`. It calls `futex_waitv()` and wakes with classic `futex_wake()` on the final futex.

## Control Flow
The private test points all waitv entries at local futexes with `FUTEX_32|FUTEX_PRIVATE_FLAG`, starts a waiter, then wakes the last futex and expects `futex_waitv()` to return that index. The shared test uses SysV shared memory entries with shared flags. Invalid tests mutate flags, address, pointer, or clockid and expect syscall rejection.

## State And Persistence
It uses process memory, SysV shared memory attachments, one waiter thread per positive case, and global waitv entries reused by tests.

## Dependencies And Integration Points
It depends on the `futex_waitv` syscall, classic futex wake compatibility, SysV shared memory, and kselftest harness.

## Risks
Several invalid tests appear to check `res == EINVAL` rather than `res < 0 && errno == EINVAL`, which may weaken failure detection. SysV segments are detached but not explicitly removed. Positive tests rely on a fixed sleep before wake.

## Test Signals
Positive signals are wake return `1` and waiter return index `NR_FUTEXES - 1`; invalid cases should surface `EINVAL`-class behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_waitv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/robust_list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/robust_list.c

## Purpose
This kselftest validates the robust futex list ABI, including owner-death wakeups, list registration size validation, `get_robust_list()`, pending operations, multiple list elements, and circular list handling.

## Important APIs, Types, And Functions
Important functions are `set_robust_list()`, `get_robust_list()`, `create_child()`, `set_list()`, `mutex_lock()`, `child_fn_lock()`, `child_list()`, `child_fn_lock_with_error()`, `child_lock_holder()`, `child_wait_lock()`, and `child_circular_list()`. Important types are `struct lock_struct` and `struct robust_list_head`.

## Control Flow
Tests clone child tasks sharing VM, register robust lists, have children exit while holding futexes, and verify waiters wake with `FUTEX_OWNER_DIED`. Other tests validate exact `set_robust_list()` size, self and child `get_robust_list()`, `list_op_pending` owner death, multiple held locks waking multiple waiters, and kernel handling of circular robust lists.

## State And Persistence
State is shared process memory, robust list head pointers registered with the kernel per thread, clone stacks, barriers, and futex words. Kernel robust-list registration persists per thread until replaced or thread exit.

## Dependencies And Integration Points
It depends on `SYS_set_robust_list`, `SYS_get_robust_list`, clone with `CLONE_VM`, robust futex ABI structures from Linux headers, pthread barriers, and kselftest harness.

## Risks
The test uses handmade robust mutex logic that is intentionally incomplete; it only validates ABI behavior. Race avoidance relies on barriers plus short sleeps before child death. Some child cleanup paths can leak mmaped stacks.

## Test Signals
Pass signals include `FUTEX_OWNER_DIED` set after owner death, `EINVAL` for invalid robust-list sizes, correct robust-list pointer returned for self/child, pending-op death handled, all multiple waiters waking, and circular list child exiting without kernel hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/robust_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/run.sh

## Purpose
This script is the functional futex test runner installed for the `functional` subdirectory.

## Important APIs, Types, And Functions
The visible file contains only the shell interpreter and SPDX line in this snapshot, with no explicit commands.

## Control Flow
As written, invoking it exits successfully after shell startup because no commands are present.

## State And Persistence
It has no state or side effects.

## Dependencies And Integration Points
It is referenced by both futex Makefiles as `TEST_PROGS`, so kselftest installs/runs it even though individual generated programs may also be run directly by other mechanisms.

## Risks
An empty runner means the built functional binaries are not orchestrated by this script in this snapshot, which can hide runtime failures unless another harness runs them.

## Test Signals
The only direct signal is exit status `0`; meaningful futex coverage requires invoking the generated test binaries separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/atomic.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/atomic.h

## Purpose
This header provides minimal GCC atomic builtin wrappers for futex tests.

## Important APIs, Types, And Functions
It defines `atomic_t` with volatile `int val`, `ATOMIC_INITIALIZER`, and inline functions `atomic_cmpxchg()`, `atomic_inc()`, `atomic_dec()`, and `atomic_set()`.

## Control Flow
Each wrapper directly calls a GCC `__sync_*` builtin or assigns the value for `atomic_set()`.

## State And Persistence
It has no state of its own; callers mutate `atomic_t` objects.

## Dependencies And Integration Points
It is used by PI requeue tests to coordinate waiter counters and flags without pulling in kernel atomic APIs.

## Risks
`atomic_set()` is a plain volatile assignment, not a full barrier. The wrappers are legacy `__sync` builtins rather than C11 atomics.

## Test Signals
Tests using waiter counters should not observe torn or lost increments/decrements under normal pthread concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futex2test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futex2test.h

## Purpose
This header supplies futex2 syscall numbers, flags, structures, and wrappers for futex selftests on systems whose headers may not yet define them.

## Important APIs, Types, And Functions
It defines fallback `__NR_futex_waitv`, `__NR_futex_wake`, `__NR_futex_wait`, `struct futex_waitv`, futex2 flags such as `FUTEX2_SIZE_U32`, `FUTEX2_NUMA`, `FUTEX2_MPOL`, `FUTEX2_PRIVATE`, `FUTEX_32`, `struct futex32_numa`, and wrappers `futex_waitv()`, `futex2_wait()`, and `futex2_wake()`.

## Control Flow
The wrappers call raw syscalls. `futex_waitv()` converts a userspace `timespec` to `struct __kernel_timespec` before passing it with a clock id. `futex2_wait()` and `futex2_wake()` pass full bitsets using `~0U`.

## State And Persistence
The header has no state. Futex state is in caller-provided user memory.

## Dependencies And Integration Points
It integrates futex2 tests with the kernel futex2 ABI and relies on `futextest.h` for `futex_t`.

## Risks
Fallback syscall numbers are architecture-sensitive and may be wrong outside the intended architectures. `futex_waitv()` assumes non-null timeout in its conversion path.

## Test Signals
Futex2 tests compile on old headers and either pass on kernels with futex2 support or fail/skip consistently when syscalls are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futex2test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futextest.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futextest.h

## Purpose
This header is the classic futex test library, providing raw futex syscall wrappers and atomic helpers independent of glibc abstractions.

## Important APIs, Types, And Functions
It defines `futex_t`, `FUTEX_INITIALIZER`, fallback futex op constants, `SYS_futex` time64 compatibility selection, the `futex()` syscall macro, wrappers for wait/wake/bitset/PI/wake-op/requeue/requeue-PI operations, and helpers `futex_cmpxchg()`, `futex_dec()`, `futex_inc()`, and `futex_set()`.

## Control Flow
All futex operation wrappers forward to `syscall(SYS_futex, ...)` with operation flags ORed into the op. Atomic helpers use GCC builtins or direct assignment.

## State And Persistence
The header owns no state; it mutates caller-supplied futex words and interacts with kernel futex wait queues.

## Dependencies And Integration Points
It integrates all classic futex functional tests with the Linux futex syscall ABI and handles 32-bit time64 build modes.

## Risks
The macro signature is intentionally loose because futex arguments are overloaded; type mistakes can compile. Fallback op definitions must stay correct. `futex_set()` is a plain assignment.

## Test Signals
All classic futex binaries should compile regardless of libc futex wrappers and observe expected syscall return counts/errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futextest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/run.sh

## Purpose
This top-level futex runner detects color support and delegates to the functional test runner.

## Important APIs, Types, And Functions
It uses `tput setf/setaf/sgr0`, exports `USE_COLOR`, and runs `(cd functional; ./run.sh)`.

## Control Flow
The script probes terminal color capability, sets `USE_COLOR=1` if color setup succeeds, then executes the functional runner in a subshell.

## State And Persistence
It only exports an environment variable and changes directory in a subshell.

## Dependencies And Integration Points
It integrates the top-level kselftest entry with `functional/run.sh`.

## Risks
Because `functional/run.sh` is empty in this snapshot, this top-level runner also performs no actual binary execution beyond delegation.

## Test Signals
Direct success only proves shell and directory availability; meaningful futex test signals require functional runner content or direct binary invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gen_kselftest_tar.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gen_kselftest_tar.sh

## Purpose
This utility script generates a distributable kselftest installation tarball.

## Important APIs, Types, And Functions
`main()` parses optional format names `tar`, `targz`, `tarbz2`, and `tarxz`, chooses tar flags and extension, creates `kselftest_install/kselftest`, runs `./kselftest_install.sh`, creates the archive, prints a notice, and removes the work directory.

## Control Flow
No argument defaults to gzip. Unknown formats exit `1`. Archive creation runs from the temporary install work parent so the archive root is `kselftest`.

## State And Persistence
It creates and deletes `kselftest_install/` in the current directory and leaves `kselftest.tar*` in the invocation directory.

## Dependencies And Integration Points
It depends on `kselftest_install.sh`, `tar`, and compression support selected by tar flags. It is an older convenience path superseded by `make gen_tar`.

## Risks
The script removes `$install_work` recursively; if path construction or cwd is unexpected, cleanup could be destructive within the working directory. Consumers may parse the final archive-created line, so the warning intentionally appears before it.

## Test Signals
Expected signal is `Kselftest archive kselftest<ext> created!` and a matching non-empty archive in the current directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gen_kselftest_tar.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/Makefile

## Purpose
This Makefile builds and registers GPIO selftests for mockup, simulator, aggregator, and character-device UAF coverage.

## Important APIs, Types, And Functions
It sets `TEST_PROGS := gpio-mockup.sh gpio-sim.sh gpio-aggregator.sh gpio-cdev-uaf.sh`, `TEST_FILES := gpio-mockup-sysfs.sh`, `TEST_GEN_PROGS_EXTENDED := gpio-mockup-cdev gpio-chip-info gpio-line-name gpio-cdev-uaf`, and `CFLAGS += -O2 -g -Wall $(KHDR_INCLUDES)`.

## Control Flow
kselftest builds helper binaries, installs shell scripts, and runs the four main GPIO test scripts.

## State And Persistence
Build artifacts are generated; runtime module/configfs/debugfs state is owned by scripts.

## Dependencies And Integration Points
It integrates with GPIOLIB, GPIO cdev, `gpio-mockup`, `gpio-sim`, and `gpio-aggregator` modules.

## Risks
Missing helper binaries break shell scripts that query chip info or exercise cdev line requests.

## Test Signals
Successful helper builds and PASS messages from mockup, sim, aggregator, and UAF scripts validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/config

## Purpose
This config file records kernel options needed for GPIO selftests.

## Important APIs, Types, And Functions
It requires `CONFIG_GPIOLIB=y`, `CONFIG_GPIO_CDEV=y`, `CONFIG_GPIO_MOCKUP=m`, `CONFIG_GPIO_SIM=m`, and `CONFIG_GPIO_AGGREGATOR=m`.

## Control Flow
It is consumed by kselftest prerequisite reporting; scripts still do runtime `modprobe` and mount checks.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
It maps to modules and APIs used by the GPIO test scripts and helper binaries.

## Risks
Even with these options, debugfs/configfs mount availability and permissions can still cause skips.

## Test Signals
Kernels matching this config should allow the scripts to load required modules and create simulated GPIO devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-aggregator.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-aggregator.sh

## Purpose
This shell test validates the `gpio-aggregator` module using `gpio-sim` chips as backends, covering configfs/sysfs creation, reconfiguration rules, module unload behavior, forwarding functionality, and a race stress test.

## Important APIs, Types, And Functions
It defines simulator helpers `sim_enable_chip()`, `sim_disable_chip()`, `sim_configfs_cleanup()`, `sim_get_chip_label()` and aggregator helpers for chip/line create/remove, key/offset/name setting, live toggles, configfs device/chip name lookup, line count, chip label, and line name. It uses `/sys/kernel/config/gpio-sim`, `/sys/kernel/config/gpio-aggregator`, and `/sys/bus/platform/drivers/gpio-aggregator`.

## Control Flow
The script loads modules, verifies configfs, cleans stale devices, creates two simulated chips with two banks each, then runs numbered scenarios for configfs creation/deletion, sysfs creation/deletion, offline/online/deferred-probe reconfiguration, module unload, forwarding set values/config, and concurrent new/delete plus module load/unload stress.

## State And Persistence
It creates configfs simulator and aggregator devices, toggles `live`, starts temporary `gpio-mockup-cdev` processes, manipulates sysfs `new_device`/`delete_device`, and loads/unloads modules. EXIT cleanup removes devices.

## Dependencies And Integration Points
It depends on root, `gpio-sim`, `gpio-aggregator`, configfs, helper binaries `gpio-chip-info`, `gpio-line-name`, and `gpio-mockup-cdev`.

## Risks
The test is invasive to module state and can unload/reload `gpio-aggregator`. Many checks assume immediate sysfs/configfs consistency except where sleeps are added. The race loop intentionally hammers module load/unload and device creation.

## Test Signals
Expected signal is final `GPIO gpio-aggregator test PASS`, with intermediate assertions confirming invalid configs stay non-live, deferred sysfs devices later become live, online config is immutable, forwarding changes backend values, and module unload is blocked only for configfs-owned devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-aggregator.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.c

## Purpose
This helper exercises GPIO character-device file descriptors after the backing `gpio-sim` chip is destroyed, checking for safe `ENODEV`/poll behavior rather than use-after-free.

## Important APIs, Types, And Functions
Important helpers are `_create_chip()`, `create_chip()`, `remove_chip()`, `_create_bank()`, `create_bank()`, `remove_bank()`, `_enable_chip()`, `enable_chip()`, `disable_chip()`, `open_chip()`, `close_chip()`, `test_poll()`, `test_read()`, `test_ioctl()`, and `main()`. It uses GPIO v1 handle/event ioctls and v2 line request ioctls.

## Control Flow
`main()` validates target object (`chip`, `handle`, `event`, or `req`) and operation (`poll`, `read`, `ioctl`), creates a one-bank simulated chip, obtains the chosen fd, destroys the chip through configfs, then performs the requested operation on the dangling fd. Success is no unexpected readiness for poll or `ENODEV` for read/ioctl.

## State And Persistence
It creates/removes configfs gpio-sim directories, opens `/dev/gpiochip*`, and holds chip/line/event/request fds across device teardown.

## Dependencies And Integration Points
It depends on `gpio-sim`, configfs, GPIO cdev v1/v2 uAPIs, and kernel cleanup paths for removed GPIO devices.

## Risks
Path buffers are fixed-size and assume short chip/bank names. The ioctl test uses command `0`, expecting generic `ENODEV` after removal; behavior changes in fd validation can affect the result.

## Test Signals
Pass is exit `0` for each matrix entry, with reads/ioctls returning `ENODEV` and poll reporting no events except allowed `POLLHUP|POLLERR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.sh

## Purpose
This wrapper runs the GPIO cdev UAF helper across chip, line handle, line event, and v2 line request file descriptor operations.

## Important APIs, Types, And Functions
It defines `fail()` and `skip()`, loads `gpio-sim`, ensures configfs is mounted, and invokes `gpio-cdev-uaf` for chip poll/read/ioctl, handle ioctl, event read/poll/ioctl, and request read/poll/ioctl.

## Control Flow
The script mounts configfs if necessary, then executes numbered subtests and fails immediately on any helper nonzero exit.

## State And Persistence
It may mount configfs and loads `gpio-sim`; per-test configfs state is created by the helper.

## Dependencies And Integration Points
It depends on root, `modprobe`, `gpio-sim`, configfs, and the compiled `gpio-cdev-uaf` helper.

## Risks
No global cleanup beyond helper cleanup is provided if a helper crashes mid-device removal. Mounting configfs modifies host mount state.

## Test Signals
Expected final line is `GPIO gpio-cdev-uaf test PASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-chip-info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-chip-info.c

## Purpose
This helper reads GPIO chip name, label, or line count from a gpiochip character device.

## Important APIs, Types, And Functions
`main()` opens the provided chip path, calls `GPIO_GET_CHIPINFO_IOCTL` into `struct gpiochip_info`, and prints `name`, `label`, or `num-lines`.

## Control Flow
Invalid argument count or unknown field exits failure. Open or ioctl errors print diagnostics and exit failure.

## State And Persistence
It only opens and reads a GPIO cdev; no persistent state is modified.

## Dependencies And Integration Points
It is used by GPIO shell tests to compare configfs expectations with cdev-visible chip metadata.

## Risks
It opens with `O_RDWR`, which may require write permissions even though it only reads metadata.

## Test Signals
Expected output is one line containing the requested chip field and exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-chip-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-line-name.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-line-name.c

## Purpose
This helper reads a GPIO v2 line name for a specified chip path and offset.

## Important APIs, Types, And Functions
`main()` parses the offset with `strtoul()`, fills `struct gpio_v2_line_info`, calls `GPIO_V2_GET_LINEINFO_IOCTL`, and prints `info.name`.

## Control Flow
Invalid arguments, nonnumeric offsets, open failure, or ioctl failure produce usage/error and nonzero exit.

## State And Persistence
It reads GPIO line metadata only.

## Dependencies And Integration Points
It is used by `gpio-sim.sh` and `gpio-aggregator.sh` to verify line names visible through the cdev ABI.

## Risks
It relies on GPIO cdev v2 support; kernels with only v1 cdev cannot satisfy it.

## Test Signals
Expected output is the line name, including an empty line when the name is unset, with exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-line-name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-cdev.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-cdev.c

## Purpose
This helper drives GPIO mockup lines through cdev v1 or v2 APIs for the shell tests.

## Important APIs, Types, And Functions
It provides `request_line_v2()`, `get_value_v2()`, `request_line_v1()`, `get_value_v1()`, `usage()`, `wait_signal()`, and `main()`. Options select active-low, bias (`pull-up`, `pull-down`, `disabled`), output value, and uAPI version.

## Control Flow
The helper opens a gpiochip, requests one line as input or output using v1/v2 ioctl structures, closes the chip fd, then either waits for a termination signal while holding an output request or reads and returns the input value as the process exit code.

## State And Persistence
It holds a line request fd while running and can drive output values or request bias configuration. Output state persists while the fd is held and according to GPIO subsystem semantics after close.

## Dependencies And Integration Points
It is used by GPIO mockup, simulator, and aggregator scripts to set/read lines and biases via cdev.

## Risks
Returning the line value as process exit code is intentional but unusual. Bias option strings that do not match known values silently leave bias unchanged. Output mode blocks until signal, so callers must kill it.

## Test Signals
Exit `0` or `1` from input reads maps to line value, while background output processes should change backend mockup/sysfs values and terminate cleanly on signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-cdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-sysfs.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-sysfs.sh

## Purpose
This script overrides `gpio-mockup.sh` line helpers to test the deprecated GPIO sysfs ABI instead of the cdev ABI.

## Important APIs, Types, And Functions
It defines `find_sysfs_nr()`, `acquire_line()`, `get_line()`, `set_line()`, and `release_line()`. It uses `/sys/class/gpio/export`, `/sys/class/gpio/unexport`, `direction`, `value`, and `active_low`.

## Control Flow
When sourced, it verifies sysfs and GPIO sysfs support, maps a chip/offset to a global sysfs GPIO number through platform device `base`, exports the line on demand, then implements read/write/release operations for the parent script.

## State And Persistence
It exports GPIO lines into sysfs and unexports them during `release_line()`. It maintains `sysfs_nr` and `sysfs_ldir` shell globals.

## Dependencies And Integration Points
It is sourced by `gpio-mockup.sh -t sysfs` and relies on the parent script's `skip`, `fail`, `chip`, and `offset` variables.

## Risks
The sysfs GPIO ABI is deprecated and may be disabled. Global GPIO base numbers can be absent or dynamic, so discovery depends on mockup platform layout.

## Test Signals
Successful sourced operation lets the parent mockup tests pass through sysfs and prints the deprecation warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-sysfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup.sh

## Purpose
This main GPIO mockup test validates module range parsing, line read/write behavior, active-low handling, optional bias behavior, deprecated ABI modes, and overlap/error handling.

## Important APIs, Types, And Functions
Key functions are `usage()`, `skip()`, `prerequisite()`, `remove_module()`, `cleanup()`, `fail()`, `try_insert_module()`, `release_line()`, `get_line()`, `set_line()`, `assert_line()`, `assert_mock()`, `set_mock()`, `test_line()`, `test_no_line()`, and `insmod_test()`. It uses debugfs `/sys/kernel/debug/gpio-mockup`, `modprobe gpio-mockup gpio_mockup_ranges=...`, and helper `gpio-mockup-cdev`.

## Control Flow
After parsing `-f`, `-r`, `-t`, and `-v`, the script requires root/debugfs, selects cdev v2, cdev v1, or sysfs line helpers, removes existing module state, optionally skips full tests when `/dev/gpiochip0` exists, then runs dynamic allocation tests and optional manual/overlap tests. Each `insmod_test()` loads the module, discovers debugfs chips, tests fencepost and optional random lines, checks one-past-end absence, and unloads the module.

## State And Persistence
It loads/unloads `gpio-mockup`, creates line request processes, manipulates line values/biases, reads debugfs mockup state, and uses traps to release lines and kill background jobs.

## Dependencies And Integration Points
It depends on root, debugfs, `gpio-mockup`, GPIO cdev helper, optional sysfs override, and optional existing gpiochip constraints for full tests.

## Risks
The test is invasive to GPIO module state and skips full manual allocations when physical gpiochip0 exists. Background output helper processes must be killed to release lines. Random-line mode adds nondeterministic coverage.

## Test Signals
Expected final signal is `GPIO gpio-mockup test PASS`; line tests verify input reads, output writes, active-low inversion, optional bias pull behavior, fencepost absence, and range overlap handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-sim.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-sim.sh

## Purpose
This shell test validates the `gpio-sim` configfs interface, cdev-visible metadata, sysfs simulator controls, hogged lines, and functional line behavior.

## Important APIs, Types, And Functions
Helpers include `remove_chip()`, `create_chip()`, `create_bank()`, `set_label()`, `set_num_lines()`, `set_line_name()`, `enable_chip()`, `disable_chip()`, `configfs_cleanup()`, `configfs_chip_name()`, `configfs_dev_name()`, `get_chip_num_lines()`, `get_chip_label()`, `get_line_name()`, and `sysfs_set_pull()`.

## Control Flow
The script loads `gpio-sim`, waits for configfs, cleans stale chips, then runs numbered tests for chip/dev name attributes, default/custom line counts, labels, line names, invalid line directory names, multiple chips, immutable live settings, probe error propagation, no-bank rejection, duplicate label rejection, hogged lines, pull set/read/reject through sysfs, read-only value, and functional value/bias behavior through `gpio-mockup-cdev`.

## State And Persistence
It creates configfs chips/banks/lines/hogs, toggles `live`, reads platform sysfs paths, and starts temporary cdev helper processes. EXIT cleanup removes configfs devices.

## Dependencies And Integration Points
It depends on `gpio-sim`, configfs, GPIO cdev helpers `gpio-chip-info`, `gpio-line-name`, and `gpio-mockup-cdev`.

## Risks
The cleanup loop assumes all entries under configfs are chips created by tests; stale external simulator devices could be removed. Several checks depend on immediate sysfs/cdev propagation with small sleeps.

## Test Signals
Expected final `GPIO gpio-sim test PASS` plus intermediate checks for metadata, immutability, rejection paths, hog behavior, pull values, and cdev-driven value changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-sim.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/Makefile

## Purpose
This Makefile builds HID selftest user binaries, HID-BPF programs, libbpf/bpftool support, and registers hid-tools wrapper scripts.

## Important APIs, Types, And Functions
It defines many `TEST_PROGS` wrappers, `TEST_FILES := run-hid-tools-tests.sh tests`, `TEST_GEN_PROGS = hid_bpf hidraw`, `TEST_GEN_PROGS_EXTENDED += $(DEFAULT_BPFTOOL)`, BPF object/skeleton generation rules, libbpf/bpftool/resolve_btfids build rules, `VMLINUX_BTF` discovery, clang/GCC BPF build macros, and C compile/link rules.

## Control Flow
The build locates vmlinux BTF, builds libbpf for target and host as needed, builds bpftool, dumps `vmlinux.h`, compiles BPF programs from `progs/*.c`, generates skeleton headers, then compiles `hid_bpf` and `hidraw`. Shell wrappers run hid-tools Python targets via `run-hid-tools-tests.sh`.

## State And Persistence
It creates scratch build directories under `$(OUTPUT)/tools` and host tools under `$(OUTPUT)/host-tools`, BPF objects, skeleton headers, helper binaries, and bpftool.

## Dependencies And Integration Points
It depends on kernel tools sources, libelf, zlib, pthread, clang or BPF GCC, bpftool, vmlinux BTF, HID, HIDRAW, UHID, HID-BPF, USB HID, and hid-tools test files.

## Risks
Builds fail hard if no vmlinux BTF is found. Cross-compilation requires separate host libbpf/bpftool paths. BPF compiler include paths and endianness handling are architecture-sensitive.

## Test Signals
Successful generation of `vmlinux.h`, BPF skeletons, `hid_bpf`, `hidraw`, and PASS from each hid-tools wrapper indicate healthy integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/config

## Purpose
This file lists kernel options needed for HID, HID-BPF, hidraw, UHID, USB HID, and device-specific HID selftests.

## Important APIs, Types, And Functions
It includes BPF core options (`CONFIG_BPF`, `CONFIG_BPF_SYSCALL`, JIT, BTF, LSM, cgroup), tracing helpers, `CONFIG_HIDRAW`, `CONFIG_HID`, `CONFIG_HID_BPF`, `CONFIG_INPUT_EVDEV`, `CONFIG_UHID`, USB HID, and vendor drivers such as Apple, ITE, Multitouch, PlayStation/Sony, and Wacom.

## Control Flow
The config is prerequisite metadata for kselftest; wrappers and hid-tools still perform runtime device/test availability checks.

## State And Persistence
No runtime state is mutated.

## Dependencies And Integration Points
It aligns with the HID Makefile's BPF build needs and the Python hid-tools target coverage.

## Risks
The list is broad; a missing vendor driver may only affect that vendor wrapper, but config reporting may present it as a suite prerequisite.

## Test Signals
A kernel matching these options should support building HID-BPF tests and running UHID/hidraw/hid-tools scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-apple.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-apple.sh

## Purpose
This wrapper runs the hid-tools Apple keyboard test target.

## Important APIs, Types, And Functions
It exports `TARGET=test_apple_keyboard.py` and invokes `bash ./run-hid-tools-tests.sh`.

## Control Flow
The script delegates all setup, execution, and result handling to the shared hid-tools runner.

## State And Persistence
It only sets an environment variable for the child process.

## Dependencies And Integration Points
It depends on `run-hid-tools-tests.sh`, the `tests` tree, and kernel Apple HID support.

## Risks
Any failure/skip semantics are hidden in the shared runner. Running from the wrong directory breaks the relative runner path.

## Test Signals
The expected signal is the shared runner executing `test_apple_keyboard.py` and propagating its result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-apple.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-core.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-core.sh

## Purpose
This wrapper runs core HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_hid_core.py` and calls `bash ./run-hid-tools-tests.sh`.

## Control Flow
The wrapper has no local branching; the shared runner performs the test.

## State And Persistence
It only sets `TARGET`.

## Dependencies And Integration Points
It depends on core HID, UHID/hidraw support as required by hid-tools, and the shared runner.

## Risks
Relative invocation requires the script to run from the HID selftest directory.

## Test Signals
Pass/fail/skip comes from `test_hid_core.py` through the shared runner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-core.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-gamepad.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-gamepad.sh

## Purpose
This wrapper runs hid-tools gamepad tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_gamepad.py` and calls the shared hid-tools runner.

## Control Flow
Execution is delegated to `run-hid-tools-tests.sh`.

## State And Persistence
Only `TARGET` is set.

## Dependencies And Integration Points
It integrates gamepad HID scenarios with the kselftest HID suite.

## Risks
All environment and dependency checks are external to this wrapper.

## Test Signals
The result is the shared runner's result for `test_gamepad.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-gamepad.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-ite.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-ite.sh

## Purpose
This wrapper runs ITE keyboard HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_ite_keyboard.py` and invokes the shared runner.

## Control Flow
No local logic beyond delegation.

## State And Persistence
It sets one environment variable.

## Dependencies And Integration Points
It depends on ITE HID support and the hid-tools test harness.

## Risks
Missing vendor driver support should be handled by the target/runner rather than this wrapper.

## Test Signals
The expected signal is successful execution or an appropriate skip/fail for `test_ite_keyboard.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-ite.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-keyboard.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-keyboard.sh

## Purpose
This wrapper runs generic keyboard HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_keyboard.py` and invokes `bash ./run-hid-tools-tests.sh`.

## Control Flow
The shared runner owns setup and result handling.

## State And Persistence
Only `TARGET` is set.

## Dependencies And Integration Points
It depends on HID keyboard functionality exposed to hid-tools.

## Risks
Relative path execution assumptions are the only local risk.

## Test Signals
Runner output for `test_keyboard.py` is the meaningful signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-keyboard.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-mouse.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-mouse.sh

## Purpose
This wrapper runs generic HID mouse hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_mouse.py` and calls the shared runner.

## Control Flow
No local branching; all behavior is delegated.

## State And Persistence
It only mutates the child environment.

## Dependencies And Integration Points
It integrates mouse HID scenarios into the kselftest HID suite.

## Risks
The wrapper provides no local dependency checks.

## Test Signals
Expected pass/fail/skip is produced by the shared runner for `test_mouse.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-mouse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-multitouch.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-multitouch.sh

## Purpose
This wrapper runs HID multitouch hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_multitouch.py` and invokes the shared runner.

## Control Flow
The script delegates directly to `run-hid-tools-tests.sh`.

## State And Persistence
It only sets `TARGET`.

## Dependencies And Integration Points
It depends on HID multitouch kernel support and hid-tools.

## Risks
Missing multitouch support should be represented in runner output; the wrapper itself cannot distinguish it.

## Test Signals
The meaningful signal is the shared runner result for `test_multitouch.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-multitouch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-sony.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-sony.sh

## Purpose
This wrapper runs Sony/PlayStation HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_sony.py` and calls the shared runner.

## Control Flow
All test work is in `run-hid-tools-tests.sh` and the Python target.

## State And Persistence
It sets only the target environment variable.

## Dependencies And Integration Points
It depends on Sony/PlayStation HID and force-feedback related config as applicable.

## Risks
Vendor-specific kernel support controls whether the target can pass.

## Test Signals
Runner output for `test_sony.py` is the result signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-sony.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-tablet.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-tablet.sh

## Purpose
This wrapper runs generic HID tablet hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_tablet.py` and invokes `bash ./run-hid-tools-tests.sh`.

## Control Flow
The wrapper delegates fully to the shared runner.

## State And Persistence
It only sets `TARGET`.

## Dependencies And Integration Points
It integrates tablet HID test coverage into kselftest.

## Risks
No local validation exists for tablet support or hid-tools availability.

## Test Signals
The shared runner's result for `test_tablet.py` is the expected signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-tablet.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-usb_crash.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-usb_crash.sh

## Purpose
This wrapper runs HID USB crash regression tests from hid-tools.

## Important APIs, Types, And Functions
It exports `TARGET=test_usb_crash.py` and calls the shared runner.

## Control Flow
No local control flow beyond delegation.

## State And Persistence
It only mutates the environment for the child process.

## Dependencies And Integration Points
It depends on USB HID support and the hid-tools test harness.

## Risks
The wrapper does not isolate crash-regression effects; any safety/skip handling must be in the shared runner and target tests.

## Test Signals
The shared runner should execute `test_usb_crash.py` and return its kselftest result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-usb_crash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-wacom.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-wacom.sh

## Purpose
This wrapper runs Wacom generic HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_wacom_generic.py` and invokes `bash ./run-hid-tools-tests.sh`.

## Control Flow
Execution is delegated to the shared hid-tools runner.

## State And Persistence
It only sets the test target environment variable.

## Dependencies And Integration Points
It depends on Wacom HID support and the shared hid-tools test suite.

## Risks
The wrapper has no local dependency checks and assumes the relative runner exists.

## Test Signals
The expected signal is the shared runner result for `test_wacom_generic.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-wacom.sh -->
