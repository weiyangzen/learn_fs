# subset-b-006833 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/epoll/epoll_wakeup_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/epoll/epoll_wakeup_test.c

## Purpose

`epoll_wakeup_test.c` is a kselftest coverage matrix for epoll readiness propagation and waiter wakeup semantics. It covers plain sockets, eventfds, nested epoll instances, poll on epoll fds, level-triggered and edge-triggered registrations, multiple waiters, `epoll_pwait`, and direct syscall coverage for `epoll_pwait2`.

## Important APIs, Types, and Functions

The shared `struct epoll_mtcontext` stores up to three epoll fds, four socket fds, a volatile wake counter, and waiter thread IDs. Helpers wrap `__NR_epoll_pwait2`, install a no-op `SIGUSR1` handler, send timeout-breaking signals, and provide waiter/emitter thread functions. Tests use `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, `poll`, `socketpair`, `eventfd`, pthreads, atomic builtins, and kselftest harness assertions.

## Control Flow, State, and Persistence

Tests `epoll1` through `epoll58` form a hand-written topology matrix: a thread waits directly or with `poll`, watches sockets or nested epoll fds, and asserts whether repeated waits produce events under LT or ET rules. The multithreaded cases synchronize with delayed writers and signal-based timeout escape. `epoll59` repeatedly modifies an eventfd interest set while another thread waits, targeting a historical lost wake race. `epoll60` starts ten waiters against ten eventfds and verifies all ET waiters wake in 300 iterations. `epoll61` races a near-timeout epoll waiter with a blocking waiter and eventfd writes. `epoll62` and `epoll63` exercise `epoll_pwait2` readiness and timeout duration. `epoll64` checks two level-triggered waiters both wake for one ready socket. Persistent state is limited to kernel wait queues, eventfd counters, socket buffers, and epoll ready lists during each test.

## Dependencies, Integration Points, Risks, and Test Signals

The test depends on pthreads, Unix sockets, eventfd, signal delivery, high-resolution enough scheduling, and kernel support for `epoll_pwait2` where exercised. It integrates with `tools/testing/selftests/filesystems/epoll` and validates core fs/eventpoll behavior used by user space runtimes. Main risks are timing sensitivity, busy waits on volatile fields, signal interruption masking real races, and platform load causing long joins. Passing signals include exact wake counts, ET second wait returning zero, LT repeated readiness, `EINTR` only during stop, no lost waiters in stress loops, and `epoll_pwait2` timeout at least the configured delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/epoll/epoll_wakeup_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/eventfd/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/eventfd/Makefile

## Purpose

This Makefile builds the eventfd filesystem selftest binary `eventfd_test`.

## Important APIs, Types, and Functions

It adds `$(KHDR_INCLUDES)` to `CFLAGS`, links with `-lpthread`, declares `TEST_GEN_PROGS := eventfd_test`, and includes `../../lib.mk`.

## Control Flow, State, and Persistence

There is no runtime control flow. kselftest make infrastructure consumes `TEST_GEN_PROGS` and emits the compiled test into the output directory. The only persistent state is build metadata.

## Dependencies, Integration Points, Risks, and Test Signals

The file depends on the common kselftest `lib.mk`, kernel headers, and pthread linkage. It integrates the eventfd test into the selftests build and install flow. Risks are missing kernel headers or pthread flags causing compile/link failures. Test signals are successful compilation and the presence of `eventfd_test` in the generated programs list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/eventfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/eventfd/eventfd_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/eventfd/eventfd_test.c

## Purpose

`eventfd_test.c` validates eventfd creation flags, fdinfo reporting, and read/write counter semantics for regular and semaphore eventfds.

## Important APIs, Types, and Functions

The file wraps `__NR_eventfd2` in `sys_eventfd2`. `struct error`, `error_set`, `trim_newline`, and `verify_fdinfo` provide detailed diagnostics for `/proc/self/fdinfo/<fd>`. Tests cover `EFD_CLOEXEC`, `EFD_NONBLOCK`, `EFD_SEMAPHORE`, `fcntl(F_GETFL/F_GETFD)`, `read`, `write`, and errno checks.

## Control Flow, State, and Persistence

Flag tests create one eventfd, query descriptor flags, assert expected `O_RDWR`, `FD_CLOEXEC`, or nonblocking bits, and close it. The semaphore flag test verifies fdinfo contains `eventfd-semaphore: 1`. Write tests ensure undersized writes and `UINT64_MAX` writes fail with `EINVAL`; valid writes increase the kernel counter. Read tests ensure undersized reads fail, non-semaphore reads return and reset the accumulated counter, semaphore reads return one and decrement, and empty nonblocking reads fail with `EAGAIN`. Persistent state is only the eventfd counter and descriptor flags for each test.

## Dependencies, Integration Points, Risks, and Test Signals

The test depends on eventfd2 syscall support, procfs fdinfo, kselftest harness, and standard file descriptor semantics. It integrates with the eventfd selftest target and validates behavior relied on by epoll, async notification, and userspace synchronization. Risks include fdinfo format drift and very large iteration counts making failures slower. Strong pass signals are exact flag values, fdinfo semaphore visibility, correct `EINVAL` and `EAGAIN`, one aggregate non-semaphore read of 100000, and 100000 semaphore reads of value one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/eventfd/eventfd_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/Makefile

## Purpose

This Makefile registers the FAT/vfat filesystem selftest script and builds its helper program.

## Important APIs, Types, and Functions

`TEST_PROGS := run_fat_tests.sh` marks the shell test as the executable test entry. `TEST_GEN_PROGS_EXTENDED := rename_exchange` builds the helper used by the script. `CFLAGS` enables optimization, debug info, warnings, and kernel header includes before including `../../lib.mk`.

## Control Flow, State, and Persistence

There is no runtime flow in the Makefile. The kselftest framework builds `rename_exchange` as an extended generated program and runs `run_fat_tests.sh`.

## Dependencies, Integration Points, Risks, and Test Signals

The Makefile depends on common kselftest make rules and kernel headers for `renameat2` constants. It integrates the FAT rename-exchange regression into the filesystems selftests suite. Build risks are missing headers or unsupported `renameat2` declarations. Passing build signals are the generated helper and script being present in the test output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/config

## Purpose

This config fragment declares kernel configuration prerequisites for the FAT selftests.

## Important APIs, Types, and Functions

It requires `CONFIG_BLK_DEV_LOOP=y` for loopback mounting disk images and `CONFIG_VFAT_FS=y` for the vfat filesystem implementation.

## Control Flow, State, and Persistence

There is no control flow. The fragment is consumed by kselftest or kernel test configuration tooling as static requirement metadata.

## Dependencies, Integration Points, Risks, and Test Signals

The fragment integrates with `run_fat_tests.sh`, which formats a vfat image and mounts it with `-o loop`. Without either option, the test cannot mount its target filesystem. Passing signals are a loop-backed vfat mount succeeding and the test not skipping or failing due to absent kernel support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/rename_exchange.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/rename_exchange.c

## Purpose

`rename_exchange.c` is a small helper that atomically swaps two paths with `renameat2(..., RENAME_EXCHANGE)`. It exists so the FAT shell test can exercise vfat rename-exchange behavior through a compiled helper.

## Important APIs, Types, and Functions

`print_usage` emits the required two-argument form. `main` validates `argc == 3`, calls `renameat2(AT_FDCWD, argv[1], AT_FDCWD, argv[2], RENAME_EXCHANGE)`, reports errors with `perror`, and exits success or failure.

## Control Flow, State, and Persistence

The program has one direct path: parse arguments, call the syscall wrapper exposed by libc with directory-relative current working directory fds, and exit. It persists only the filesystem namespace change produced by the atomic exchange.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on `_GNU_SOURCE`, `fcntl.h` exposing `renameat2` and `RENAME_EXCHANGE`, and kernel filesystem support for exchange rename. It integrates with `run_fat_tests.sh` against a mounted vfat image. Risks are missing libc declaration, unsupported syscall, or filesystem-specific exchange bugs. Passing signal is the two files trading names without content loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/rename_exchange.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/run_fat_tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/run_fat_tests.sh

## Purpose

`run_fat_tests.sh` creates a tiny vfat filesystem image, mounts it through a loop device, and verifies `RENAME_EXCHANGE` for files in the same directory and across a subdirectory.

## Important APIs, Types, and Functions

Shell helpers are `cleanup`, `create_loopback`, `mount_image`, `rename_exchange_test`, `rename_exchange_subdir_test`, and `unmount_image`. The script uses `mktemp`, `truncate`, `mkfs.vfat`, `sudo mount -o loop`, `tee`, the compiled `rename_exchange` helper, `sync -f`, `grep`, and `sudo umount`.

## Control Flow, State, and Persistence

With `set -euo pipefail`, any failed command aborts. A temporary directory holds `fat.img` and mountpoint `mnt`. Cleanup is trapped for signals and exit, unmounting if still mounted and removing the temp tree. After formatting and mounting, the script writes `old` and `new` file contents, performs an exchange, syncs the mount, and checks that path contents swapped. The subdir variant repeats with the new file inside `subdir`. Persistent state is limited to the temporary image and mounted filesystem, removed at exit.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on `mkfs.vfat`, loop device support, sudo privileges, vfat kernel support, and the helper binary path relative to the script. Risks include sudo prompts in automation, unavailable loop devices, `chattr +C` being best-effort, and cleanup depending on mountpoint detection. Passing signals are successful mount, both exchange operations, synced data, and grep confirming swapped contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/run_fat_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fclog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fclog.c

## Purpose

`fclog.c` tests the read side of new mount API filesystem context logs, especially empty-log, error-log, post-creation retention, and too-small-buffer behavior.

## Important APIs, Types, and Functions

The `ns` fixture saves the original mount namespace, unshares a private mount namespace, and restores it during teardown. Assertion macros compare syscall return values to negative errno. Tests call `fsopen`, `fsconfig`, `fsmount`, `move_mount`, `read`, `close`, `unshare`, `mount`, and `setns`.

## Control Flow, State, and Persistence

Each test opens a tmpfs filesystem context. `fscontext_log_enodata` repeatedly reads a fresh context and expects `ENODATA`. `fscontext_log_errorfc` submits an invalid option and expects one exact tmpfs error line, then `ENODATA` after consumption. `fscontext_log_errorfc_after_fsmount` verifies the same log remains readable after `FSCONFIG_CMD_CREATE`, `fsmount`, and attaching the mount to `/tmp`. `fscontext_log_emsgsize` verifies zero-, one-, and sixteen-byte reads fail with `EMSGSIZE` without consuming the message. State is the fscontext log queue and temporary mount namespace.

## Dependencies, Integration Points, Risks, and Test Signals

The file depends on new mount API syscalls, tmpfs option parsing, mount namespace capability, and kselftest harness support. It integrates with VFS fs_context diagnostics. Risks are exact error string drift, namespace restore failures, and attaching to `/tmp` in an isolated namespace. Passing signals are stable `ENODATA`, `EINVAL`, `EMSGSIZE`, exact error text, and non-consumption on short reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fclog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/file_stressor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/file_stressor.c

## Purpose

`file_stressor.c` is a long-running stress test for file reference lifetime behavior under `SLAB_TYPESAFE_BY_RCU`. It tries to provoke races between rapid file allocation/freeing and `/proc/<pid>/fd` directory iteration.

## Important APIs, Types, and Functions

It wraps `fsopen`, `fsconfig`, `fsmount`, and `move_mount`, defines `MOVE_MOUNT_F_EMPTY_PATH` if needed, and uses a `file_stressor` fixture containing tmpfs mount fd, process counts, child pid arrays, proc fd directory fds, and `max_fds`. The test uses `fork`, `open`, `close_range`, `getdents64`, `lseek`, `clock_nanosleep`, `kill`, and wait logic.

## Control Flow, State, and Persistence

Setup unshares a mount namespace, mounts a detached tmpfs at `/slab_typesafe_by_rcu`, allocates arrays sized by online CPU count, and sets a 500-fd churn limit. The test forks one opener process per CPU; each repeatedly creates many files and closes all descriptors. The parent opens each opener's `/proc/<pid>/fd/`, then forks one getdents process per CPU; each continuously reads and rewinds that proc fd directory. After fifteen minutes the parent kills all children. Teardown waits for killed children, frees arrays, closes the tmpfs fd, unmounts, and removes the directory.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on procfs, new mount API, tmpfs, `close_range`, `getdents64`, namespaces, and enough process/file limits. It integrates with VFS file lifetime and proc fd iteration regression testing. Risks include long runtime, high CPU/file churn, a likely typo using `self->pids_openers[i]` inside the child loop path format, resource exhaustion, and tests passing only by absence of kernel warnings. Signals are no assertion failures, no hangs before timeout, child cleanup success, and external kernel logs remaining free of file refcount warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/file_stressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fsmount_ns/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fsmount_ns/Makefile

## Purpose

This Makefile builds the `fsmount_ns_test` kselftest for the `FSMOUNT_NAMESPACE` mount API flag.

## Important APIs, Types, and Functions

It sets `CFLAGS += -Wall -O2 -g $(KHDR_INCLUDES)`, declares `TEST_GEN_PROGS := fsmount_ns_test`, adds `LOCAL_HDRS += ../wrappers.h ../statmount/statmount.h ../utils.h`, and links `fsmount_ns_test` with `../utils.c`.

## Control Flow, State, and Persistence

There is no runtime flow. The common kselftest makefile compiles the test with local wrapper and utility dependencies.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on kernel headers, kselftest `lib.mk`, and utility source availability. Integration points are the new mount API wrappers and statmount helper. Risks are header/API drift around newly added flags. Passing signals are successful compile and the generated `fsmount_ns_test` binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fsmount_ns/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fsmount_ns/fsmount_ns_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fsmount_ns/fsmount_ns_test.c

## Purpose

`fsmount_ns_test.c` verifies that `fsmount(..., FSMOUNT_NAMESPACE, ...)` can create a mount namespace containing a configured tmpfs mount, expose a namespace id, allow `setns`, preserve mount attributes, and enforce capability/containment rules.

## Important APIs, Types, and Functions

Helpers include `get_mnt_ns_id`, `get_mnt_ns_id_from_path`, `log_mount`, `dump_mounts`, and `create_tmpfs_fd`. The tests use `sys_fsopen`, `sys_fsconfig`, `sys_fsmount`, `setns`, `ioctl(NS_GET_MNTNS_ID)`, `listmount`, `statmount`, `statmount_alloc`, `setup_userns`, `enter_userns`, `caps_down`, `umount2`, and kselftest fixtures/variants.

## Control Flow, State, and Persistence

The main fixture checks syscall availability and records the current mount namespace id. Variants exercise `FSMOUNT_NAMESPACE|FSMOUNT_CLOEXEC`, `FSMOUNT_CLOEXEC` alone, and namespace without cloexec. Core tests create a tmpfs fscontext, call `fsmount`, compare namespace ids, list mounts in the new namespace, and fork a child to enter it. Property tests inspect root mount metadata and fs type. Capability tests pre-create an fs fd, drop privileges in a child, and expect `EPERM`. Userns tests create namespaces with mapped privileges, create fsmount namespaces, setns into them, and verify locked mounts fail unmount with `EINVAL` while unshared private mount trees can be unmounted. Attribute tests assert `MOUNT_ATTR_RDONLY`, `NOEXEC`, `NOSUID`, `NOATIME`, and combined bits via statmount. State is held in fds, tmpfs fscontexts, and mount namespace objects.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are new mount API syscalls, nsfs mount namespace ids, statmount/listmount, user namespace helpers, and CAP_SYS_ADMIN behavior. It integrates with VFS mount namespace creation semantics and statmount namespace-aware queries. Risks include skipping on older kernels, user namespace restrictions, exact errno expectations, and cleanup relying on fd closure rather than mounted paths. Passing signals include different ns ids when expected, successful `setns`, tmpfs fs type visibility, correct mount count floor, `EPERM` after capability drop, expected `EINVAL` for locked unmounts, and visible mount attribute bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fsmount_ns/fsmount_ns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/Makefile

## Purpose

This Makefile builds the FUSE control selftest and its helper FUSE daemon.

## Important APIs, Types, and Functions

It builds `fusectl_test` as `TEST_GEN_PROGS` and `fuse_mnt` as `TEST_GEN_FILES`. It discovers FUSE CFLAGS and LDLIBS through `pkg-config fuse`, falling back to `-D_FILE_OFFSET_BITS=64 -I/usr/include/fuse` and `-lfuse -pthread`.

## Control Flow, State, and Persistence

Build flow is conditional on pkg-config output. The output-specific rules add the discovered FUSE flags only to `fuse_mnt`; `fusectl_test` uses the base flags.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on libfuse development headers/libraries, kselftest `lib.mk`, and kernel headers. It integrates `fuse_mnt` as a local daemon executed by `fusectl_test`. Risks are distribution-specific FUSE package names and fallback include paths being wrong. Passing signals are successful build of both files and link of `fuse_mnt` against libfuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/fuse_mnt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/fuse_mnt.c

## Purpose

`fuse_mnt.c` is a minimal libfuse filesystem daemon used by the fusectl abort test. It exposes a writable single-file filesystem at `/test`.

## Important APIs, Types, and Functions

Global state is `content`, `content_size`, and `test_path`. FUSE operations are `test_getattr`, `test_readdir`, `test_open`, `test_read`, `test_write`, and `test_truncate`, collected in `memfd_ops` and passed to `fuse_main`.

## Control Flow, State, and Persistence

`main` delegates lifecycle to libfuse. `getattr` reports `/` as a directory and `/test` as a regular file sized from `content_size`. `readdir` lists `.`, `..`, and `test`. `open` rejects non-test paths. `read` clamps by offset and returns current memory content. `write` rejects holes, reallocates when needed, updates `content_size`, and copies bytes. `truncate` frees or resizes content and zero-fills growth. Persistence is in process memory only, lost when the daemon exits or is aborted.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on libfuse API version 26 and a usable `/dev/fuse`. It integrates with `fusectl_test`, which starts this daemon and then aborts the connection through fusectl. Risks include memory allocation failure, no cleanup of `content` at normal exit, non-thread-safe globals if libfuse dispatches concurrently, and no sparse write support. Passing signals are successful mount, `/test` open/read/write/truncate behavior, and subsequent `ENOTCONN` after fusectl abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/fuse_mnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/fusectl_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/fusectl_test.c

## Purpose

`fusectl_test.c` verifies that writing to a FUSE connection's `abort` control file disconnects an active FUSE mount and causes future file operations to fail with `ENOTCONN`.

## Important APIs, Types, and Functions

`write_file` writes uid/gid maps. The `fusectl` fixture stores a temporary mountpoint and connection number. Setup uses `unshare(CLONE_NEWNS|CLONE_NEWUSER)`, uid/gid maps, private mounts, `mkdtemp`, `fork`, `execlp("./fuse_mnt")`, `stat`, and fusectl paths under `/sys/fs/fuse/connections`.

## Control Flow, State, and Persistence

Setup creates a user and mount namespace, maps the caller id, makes mounts private, creates a FUSE mountpoint, requires fusectl to be mounted, forks the helper daemon, waits for it to exit from foreground setup, and reads `st_dev` from the mountpoint as the connection id. The `abort` test opens `/sys/fs/fuse/connections/<id>/abort`, opens `/test`, verifies empty read, writes data, seeks back, writes `1` to abort, closes the abort fd, and expects a subsequent read to fail with `ENOTCONN`. Teardown detaches the mount and removes the temporary directory.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include libfuse helper availability, `/dev/fuse`, mounted fusectl, user namespace mapping support, and permissions to create FUSE mounts. It integrates fuse userspace daemon behavior with kernel fusectl connection management. Risks are connection id assumptions from `st_dev`, helper startup timing, environments without fusectl, and namespace restrictions. Passing signals are abort path presence, positive abort write, and `ENOTCONN` from the still-open file after abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fuse/fusectl_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/kernfs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/kernfs_test.c

## Purpose

`kernfs_test.c` validates xattr behavior on kernfs-backed sysfs files.

## Important APIs, Types, and Functions

It contains two kselftest tests using `listxattr` and `getxattr` against `/sys/kernel`. It includes `_GNU_SOURCE`, sane userspace types, `sys/xattr.h`, and the kselftest harness.

## Control Flow, State, and Persistence

`kernfs_listxattr` calls `listxattr("/sys/kernel", NULL, 0)` and expects `ENOTSUP`. `kernfs_getxattr` calls `getxattr("/sys/kernel", "user.test", NULL, 0)` and expects `ENOTSUP`. No state is modified.

## Dependencies, Integration Points, Risks, and Test Signals

The test depends on sysfs mounted at `/sys` and kernfs returning unsupported xattr errors for this path. It integrates with kernfs/sysfs VFS xattr semantics. Risks are environments without sysfs or changed errno behavior for unsupported xattrs. Passing signals are both calls failing with `-1` and `errno == ENOTSUP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/kernfs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/Makefile

## Purpose

This Makefile builds fanotify mount notification selftests.

## Important APIs, Types, and Functions

It sets warning, optimization, debug, and kernel header CFLAGS. `TEST_GEN_PROGS := mount-notify_test mount-notify_test_ns` declares the normal and user-namespace variants. It includes `../../lib.mk`.

## Control Flow, State, and Persistence

There is no runtime flow. The Makefile registers two generated kselftest binaries.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on kernel headers with fanotify mount notification definitions and kselftest build rules. It integrates both namespace variants into the filesystems selftests. Risks are header drift for newer `FAN_REPORT_MNT` and `FAN_MNT_*` constants. Passing signals are successful compilation of both test binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/mount-notify_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/mount-notify_test.c

## Purpose

`mount-notify_test.c` verifies fanotify mount namespace notifications for mount attach and detach operations in a private chrooted mount namespace.

## Important APIs, Types, and Functions

The `fanotify` fixture tracks three fanotify fds, event parsing buffer state, temporary root path, original root fd, namespace fd, and root mount id. Helpers include `expect_notify`, `expect_notify_n`, `expect_notify_mask`, `verify_mount_ids`, `check_mounted`, and `setup_mount_tree`. APIs include `fanotify_init(FAN_REPORT_MNT)`, `fanotify_mark(... FAN_MARK_MNTNS ...)`, `listmount`, `get_unique_mnt_id`, `mount`, `umount`, `move_mount`, `fsopen`, `fsmount`, and `pivot_root`.

## Control Flow, State, and Persistence

Setup unshares a mount namespace, makes it private, mounts tmpfs as a temporary root, chroots into it, creates `/a` and `/b`, records the root mount id, and creates three fanotify groups. Only the first group keeps a mark; the second removes it and the third flushes it, so reads assert events only on group zero. Tests exercise bind attach/detach, moving a mount, propagation across a shared tree, attaching a new mount from `fsmount`, reparenting across shared/slave propagation, detach caused by rmdir in another namespace, and pivot_root. Each event's `fanotify_event_info_mnt` mount id and mask are compared with `listmount` snapshots.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are fanotify mount reporting, statmount/listmount helpers, namespace and chroot privilege, and new mount API calls. Integration points are VFS mount lifecycle notifications and fanotify mark management. Risks include event ordering assumptions, fixed 256-byte event buffer, chroot cleanup complexity, and mount propagation sensitivity. Passing signals are exact `FAN_MNT_ATTACH`, `FAN_MNT_DETACH`, or combined masks, no duplicate mount ids, and `listmount` membership matching expected mounted sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/mount-notify_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/mount-notify_test_ns.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/mount-notify_test_ns.c

## Purpose

`mount-notify_test_ns.c` is the user-namespace variant of the fanotify mount notification test. It verifies both notification delivery inside the created mount namespace and permission boundaries for watching namespaces and filesystems outside that user namespace.

## Important APIs, Types, and Functions

It uses the same event parsing and mount verification helpers as `mount-notify_test.c`, with added setup of `orig_ns_fd`, `setup_userns`, and `mark_types` covering filesystem, mount, and inode marks. Setup probes `FAN_REPORT_FID` permission against the tmpfs root and original root, then installs `FAN_REPORT_MNT` namespace marks.

## Control Flow, State, and Persistence

Setup opens the original mount namespace, enters a new user namespace, opens the new mount namespace fd, mounts tmpfs as a chroot root, creates test directories, and records the root mount id. It confirms watching tmpfs mounted inside the user namespace is allowed, watching the original root filesystem is rejected, watching the current mount namespace is allowed, and watching the original namespace is rejected. It then runs the same bind, move, propagation, fsmount, reparent, rmdir, and pivot_root notification scenarios as the non-`_ns` file. State consists of namespace fds, fanotify event queues, and the temporary mount tree.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are user namespace support, fanotify permission checks, mount notifications, statmount/listmount, and mount/chroot operations. It integrates fanotify mount notification security rules with namespace ownership semantics. Risks include disabled unprivileged user namespaces, permission errno differences, event ordering, and cleanup after chroot. Passing signals are rejected marks on original objects, accepted marks inside the user namespace, exact mount notification masks, and mounted-set verification after each operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/mount-notify_test_ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/move_mount/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/move_mount/Makefile

## Purpose

This Makefile builds `move_mount_test`, focused on `MOVE_MOUNT_BENEATH` semantics.

## Important APIs, Types, and Functions

It sets warning, optimization, debug, and kernel header flags, declares `TEST_GEN_PROGS := move_mount_test`, lists local headers `../wrappers.h ../utils.h ../statmount/statmount.h`, includes `../../lib.mk`, and links `move_mount_test` with `../utils.c`.

## Control Flow, State, and Persistence

There is no runtime logic. The Makefile wires wrapper and utility dependencies into the generated test.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on local wrappers/utilities, statmount helpers, kselftest rules, and current kernel headers. It integrates the move_mount regression into the selftest suite. Risks are missing newer constants in older headers. Passing signals are successful compile and test binary generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/move_mount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/move_mount/move_mount_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/move_mount/move_mount_test.c

## Purpose

`move_mount_test.c` verifies `MOVE_MOUNT_BENEATH`, especially root replacement, chroot edge cases, and `MNT_LOCKED` transfer/containment behavior in user namespaces.

## Important APIs, Types, and Functions

Helpers include `get_unique_mnt_id_fd`, `setup_locked_overmount`, and `create_detached_tmpfs`. The fixture isolates a mount namespace and records the original root mount id. Tests use `sys_open_tree`, `sys_move_mount`, `sys_fsopen`, `sys_fsconfig`, `sys_fsmount`, `statmount`, `chroot`, `fchdir`, `umount2`, `setup_userns`, `mount`, and `statx(STATX_MNT_ID_UNIQUE)`.

## Control Flow, State, and Persistence

Rootfs tests clone `/`, move the clone beneath `/`, chroot to the clone, and detach the old root. They verify the visible root id changes and the old root's parent becomes the clone. A chroot into a subdirectory of the same mount must reject mount-beneath with `EINVAL`; a chroot into a separate tmpfs mount must succeed. Locked tests enter a user namespace where existing mounts become locked, move a cloned tree beneath the locked mount, and verify the displaced mount becomes unmountable or unmountable as expected while the replacement inherits locking. Non-rootfs tests build a locked overmount stack at `/mnt_dir`, insert a detached tmpfs beneath it, detach the top mount, and verify the newly visible mount cannot be detached when containment requires it. State is the mount stack and unique ids.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include `MOVE_MOUNT_BENEATH`, open_tree clone support, statmount, userns helpers, and CAP_SYS_ADMIN. It integrates with VFS mount stacking and namespace containment logic. Risks are highly privileged operations, path cleanup in `/mnt_dir`, exact `EINVAL` expectations for locked mounts, and chroot state changes. Passing signals are correct unique mount ids, expected root visibility, statmount parent ids, successful/failed umounts matching lock transfer, and no containment escape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/move_mount/move_mount_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/Makefile

## Purpose

This Makefile builds nsfs ioctl selftests.

## Important APIs, Types, and Functions

`TEST_GEN_PROGS := owner pidns iterate_mntns` declares the three generated programs. `CFLAGS := -Wall -Werror` turns warnings into build failures, and `../../lib.mk` supplies the kselftest rules.

## Control Flow, State, and Persistence

There is no runtime flow in the Makefile. It persists build intent for the nsfs test directory.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on common kselftest rules and headers available to each C file. It integrates owner, pid namespace parent, and mount namespace iteration tests. Risks are warning drift breaking `-Werror`. Passing signal is successful generation of all three binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/config

## Purpose

This config fragment declares namespace features required by the nsfs tests.

## Important APIs, Types, and Functions

It requires `CONFIG_USER_NS=y`, `CONFIG_UTS_NS=y`, and `CONFIG_PID_NS=y`.

## Control Flow, State, and Persistence

There is no control flow. The fragment is static test configuration metadata.

## Dependencies, Integration Points, Risks, and Test Signals

The owner test needs user and UTS namespaces; the pidns test needs user and PID namespaces. Without these options, the binaries cannot exercise target nsfs ioctls. Passing signals are successful namespace creation and no skip/failure due to unavailable namespace types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/iterate_mntns.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/iterate_mntns.c

## Purpose

`iterate_mntns.c` tests nsfs ioctls that expose information about mount namespaces and iterate to neighboring mount namespaces.

## Important APIs, Types, and Functions

It defines `struct mnt_ns_info`, `NS_MNT_GET_INFO`, `NS_MNT_GET_NEXT`, and `NS_MNT_GET_PREV`. The fixture stores eleven mount namespace fds and ids. `mntns_in_list` checks whether a returned namespace id belongs to the fixture-created set. Tests use `unshare(CLONE_NEWNS)`, `/proc/self/ns/mnt`, `ioctl`, `fcntl(F_DUPFD_CLOEXEC)`, `setns`, and negative autofs ioctl probes.

## Control Flow, State, and Persistence

Setup repeatedly unshares a mount namespace, opens its nsfs fd, calls `NS_MNT_GET_INFO`, and records the returned ids. Forward and backward whole-list tests duplicate the first or last fd and repeatedly call NEXT or PREV until `ENOENT`, counting fixture ids encountered. Direct iteration tests `setns` into an endpoint and walk exactly ten steps, closing previous fds as they go. `nfs_valid_ioctl` ensures unrelated autofs ioctls on a mount namespace fd fail with `ENOTTY`. Persistent state is a chain of open mount namespace fds held by the fixture.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include nsfs mount namespace iteration ioctls, mount namespace creation, and kselftest harness. It integrates with namespace lifetime and ioctl ABI validation. Risks are global mount namespace ordering assumptions, count checks relying on fixture-created namespaces being visible in traversal, and a test name typo (`nfs_valid_ioctl`). Passing signals are successful INFO ids, NEXT/PREV traversal, `ENOENT` termination, and `ENOTTY` for invalid autofs ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/iterate_mntns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/owner.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/owner.c

## Purpose

`owner.c` tests `NS_GET_USERNS`, which returns the owning user namespace for another namespace fd, and verifies permission behavior after entering a different user namespace.

## Important APIs, Types, and Functions

The program defines `NS_GET_USERNS` and a `pr_err` diagnostic macro. It uses `pipe`, `fork`, `unshare(CLONE_NEWUTS|CLONE_NEWUSER)`, `/proc/<pid>/ns/uts`, `/proc/self/ns/user`, `ioctl`, `fstat`, `stat`, `prctl(PR_SET_PDEATHSIG)`, `kill`, and `wait`.

## Control Flow, State, and Persistence

The parent forks a child that creates a new UTS and user namespace, closes pipe ends, and sleeps. The parent treats pipe EOF as readiness, opens the child's UTS namespace fd, calls `NS_GET_USERNS`, and compares the returned namespace inode to `/proc/self/ns/user` or the expected owner. It opens the initial user namespace and then unshares into a new user namespace, where `NS_GET_USERNS` on both the child's namespace and initial user namespace should fail with `EPERM`. State is held in namespace fds and the child process lifetime.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are user and UTS namespace support and nsfs owner ioctls. It integrates with namespace ownership and permission checks. Risks include EOF-as-ready synchronization being ambiguous if the child exits early, infinite child sleep requiring cleanup, and exact permission expectations. Passing signals are matching namespace inode numbers before privilege transition and `EPERM` after entering the new user namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/owner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/pidns.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/pidns.c

## Purpose

`pidns.c` tests `NS_GET_PARENT` for PID and user namespace fds created by a child in new user and PID namespaces.

## Important APIs, Types, and Functions

It defines `NS_GET_USERNS`, `NS_GET_PARENT`, a small aligned clone stack in `struct cr_clone_arg`, and a sleeping `child` function. APIs include `clone(CLONE_NEWUSER|CLONE_NEWPID|SIGCHLD)`, `/proc/<pid>/ns/{pid,user}`, `/proc/self/ns/{pid,user}`, `ioctl`, `fstat`, `stat`, `prctl(PR_SET_PDEATHSIG)`, `kill`, and `wait`.

## Control Flow, State, and Persistence

The parent clones a child that sleeps forever. For both `pid` and `user` namespace paths, it opens the child's namespace fd, calls `NS_GET_PARENT`, stats the returned parent fd, and compares its inode with the caller's corresponding namespace. It then verifies asking for the parent of that parent fails with `EPERM`. State persists only as the child process and namespace fds until killed.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are PID/user namespace support and nsfs parent ioctl behavior. It integrates with namespace hierarchy permission checks. Risks include fixed small clone stack, lack of explicit child readiness, and exact `EPERM` expectation for parent-of-parent. Passing signals are parent namespace inode matches for both namespace types and `EPERM` on further parent lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/pidns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/open_tree_ns/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/open_tree_ns/Makefile

## Purpose

This Makefile builds the `open_tree_ns_test` binary for `OPEN_TREE_NAMESPACE` behavior.

## Important APIs, Types, and Functions

It declares warning, optimization, debug, and kernel header CFLAGS, `TEST_GEN_PROGS := open_tree_ns_test`, local headers `../wrappers.h ../statmount/statmount.h ../utils.h`, and links `open_tree_ns_test` with `../utils.c`.

## Control Flow, State, and Persistence

There is no runtime flow. The Makefile wires local support code into the kselftest binary.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on current kernel headers, wrappers, statmount helpers, utils, and kselftest rules. It integrates open_tree namespace tests into the filesystems suite. Risks are missing newer constants in older headers. Passing signal is successful generation of `open_tree_ns_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/open_tree_ns/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/open_tree_ns/open_tree_ns_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/open_tree_ns/open_tree_ns_test.c

## Purpose

`open_tree_ns_test.c` verifies that `open_tree(..., OPEN_TREE_NAMESPACE, ...)` creates a mount namespace containing a selected mount tree, handles recursive and unbindable cases, and enforces namespace/capability containment rules.

## Important APIs, Types, and Functions

Helpers mirror the fsmount namespace test: `get_mnt_ns_id`, `get_mnt_ns_id_from_path`, `log_mount`, and `dump_mounts`. Fixtures cover basic variants, capability checks, user namespace behavior, and unbindable mounts. APIs include `sys_open_tree`, `ioctl(NS_GET_MNTNS_ID)`, `listmount`, `statmount_alloc`, `setns`, `enter_userns`, `caps_down`, `umount2`, `mount`, and `mkdtemp`.

## Control Flow, State, and Persistence

Basic variants call `open_tree` on `/`, `/tmp`, `/proc`, or `/run` with `OPEN_TREE_NAMESPACE`, optional `AT_RECURSIVE`, and cloexec, expecting a new namespace id and at least one visible mount. A negative variant with `AT_RECURSIVE` but no namespace flag expects `EINVAL`. Setns and property tests verify entering the returned namespace and root mount metadata. Capability tests drop privileges and expect `EPERM`. User namespace tests create namespaces, open trees inside them, setns from an inner child, verify recursive copies, and compare locked mount unmount failure (`EINVAL`) with private unshared tree unmount success. Unbindable tests require direct namespace open on an unbindable mount to fail and recursive root copy to omit the unbindable mount. State is the returned namespace fd and copied mount trees.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include `OPEN_TREE_NAMESPACE`, statmount/listmount, user namespaces, mount propagation, and CAP_SYS_ADMIN. It integrates with VFS open_tree clone/copy semantics and namespace containment. Risks are path assumptions for `/run` and `/proc`, older kernels skipping, userns restrictions, and exact unbindable filtering. Passing signals are different ns ids, successful `setns`, expected `EINVAL` or `EPERM`, visible mount count floors, locked unmount behavior, and absence of the unbindable mount from recursive results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/open_tree_ns/open_tree_ns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/Makefile

## Purpose

This Makefile builds overlayfs selftests for mapping device/inode reporting and fd-based layer configuration.

## Important APIs, Types, and Functions

It adds warning and kernel header CFLAGS, links with `-lcap`, lists local headers `../wrappers.h log.h`, and declares `TEST_GEN_PROGS := dev_in_maps set_layers_via_fds`. The `set_layers_via_fds` target also compiles with `../utils.c`.

## Control Flow, State, and Persistence

There is no runtime flow. Build metadata ensures the tests have wrapper, logging, utility, and libcap support.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are overlayfs-capable kernel headers, libcap, wrappers, utils, and kselftest rules. It integrates overlayfs new mount API tests into the suite. Risks include missing libcap development files. Passing signals are successful compile and link of both generated programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/dev_in_maps.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/dev_in_maps.c

## Purpose

`dev_in_maps.c` verifies that a memory-mapped overlayfs file appears in `/proc/self/maps` with the same device and inode values reported by `statx` on the file.

## Important APIs, Types, and Functions

`get_file_dev_and_inode` parses `/proc/self/maps` for the mapping start address and extracts major, minor, and inode. `ovl_mount` constructs tmpfs and overlayfs mounts through `fsopen`, `fsconfig`, `fsmount`, and `move_mount`. `test` creates and mmaps a file on the detached overlay mount and compares maps data to `statx`.

## Control Flow, State, and Persistence

`main` first probes that overlay fsopen works, enters a new mount namespace, makes `/` slave, sets a one-test plan, and runs `test`. The test creates a tmpfs mounted at `/tmp`, creates work/upper/lower directories, configures overlay source/lower/upper/work, obtains a detached overlay fd, opens `test` on it, mmaps one page shared writable, parses `/proc/self/maps`, stats the fd, and compares device/inode triples. Mount state is isolated to the namespace and not explicitly cleaned.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are overlayfs, tmpfs, new mount API wrappers, procfs maps format, mmap, statx, and namespace privilege. It integrates overlayfs with procfs VMA reporting. Risks are strict maps parsing, assuming mapping start equals `addr`, no cleanup beyond namespace lifetime, and older kernels lacking overlay fsopen. Passing signal is `ksft_test_result_pass("devices are matched")` with identical dev major/minor and inode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/dev_in_maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/log.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/log.h

## Purpose

`log.h` provides small kselftest-oriented logging macros for overlayfs selftests.

## Important APIs, Types, and Functions

Macros are `pr_msg`, `pr_p`, `pr_err`, `pr_fail`, and `pr_perror`. They wrap `ksft_print_msg`, `ksft_test_result_error`, and `ksft_test_result_fail`, returning `-1` for error/fail expressions.

## Control Flow, State, and Persistence

The header has no standalone control flow or state. It formats source file and line number into diagnostic messages and lets C expressions return failure values inline.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on included tests having kselftest APIs visible. It integrates with `dev_in_maps.c` and potentially other overlayfs tests. Risks are macro side effects and the header guard name referencing timens rather than overlayfs, which is cosmetic but confusing. Passing signal is consistent kselftest diagnostics and propagated `-1` return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/set_layers_via_fds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/set_layers_via_fds.c

## Purpose

`set_layers_via_fds.c` validates overlayfs new mount API support for configuring workdir, upperdir, lowerdir, datadir, and credential override behavior using file descriptors instead of path strings.

## Important APIs, Types, and Functions

The fixture tracks a pidfd for child cleanup and creates mount directories. Tests use `sys_fsopen`, `sys_fsconfig` with `FSCONFIG_SET_FD`, `FSCONFIG_SET_STRING`, and `FSCONFIG_SET_FLAG`, `fsmount`, `move_mount`, `open_tree`, `openat`, user namespace helpers, pidfd helpers, libcap helpers, and `/proc/self/mountinfo` parsing.

## Control Flow, State, and Persistence

The basic test creates tmpfs directories for work, upper, four lowers, and three data dirs, opens fds for each, moves tmpfs to `/tmp`, configures overlay with `lowerdir+` and `datadir+`, enables metacopy, mounts it, and scans mountinfo for path rendering. The 500-layer tests add 500 lower fds and verify a 501st fails, both with normal and `O_PATH` fds. Credential tests toggle `override_creds` and `nooverride_creds` from child processes, validate an invalid user namespace cannot set override on a shared context, and verify dropping `CAP_MKNOD` before `override_creds` causes `mknodat` in the overlay to fail with `EPERM`. The detached mount fd test configures layers from cloned open_tree fds and checks mountinfo output.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are overlayfs fd-based fsconfig support, tmpfs, new mount API wrappers, user namespace and capability helpers, pidfds, and mountinfo formatting. It integrates with overlayfs layer parser, metacopy/datadir support, and credential stashing semantics. Risks include mountinfo string matching, hard-coded `/tmp`, high fd counts, child synchronization, and cleanup after namespace changes. Passing signals are expected failure for plain `lowerdir`, success for `lowerdir+`/`datadir+`, 500-layer limit enforcement, correct mountinfo entries, valid credential toggles, invalid namespace rejection, and `EPERM` for mknod under dropped creds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/set_layers_via_fds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/Makefile

## Purpose

This Makefile builds the statmount and listmount syscall selftests.

## Important APIs, Types, and Functions

It sets warning, optimization, debug, and kernel header CFLAGS; declares `TEST_GEN_PROGS := statmount_test statmount_test_ns listmount_test`; and includes `../../lib.mk`.

## Control Flow, State, and Persistence

There is no runtime flow. The kselftest make framework compiles three binaries.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on kernel headers exposing statmount/listmount structs and flags plus common kselftest rules. It integrates syscall ABI tests into the filesystems suite. Risks are older headers missing constants. Passing signal is successful compilation of all three binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/listmount_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/listmount_test.c

## Purpose

`listmount_test.c` checks ordering and pagination semantics of the `listmount` syscall.

## Important APIs, Types, and Functions

It includes `statmount.h`, defines `LISTMOUNT_REVERSE` if absent, uses a ten-entry buffer, and contains `listmount_forward` and `listmount_backward` kselftest tests.

## Control Flow, State, and Persistence

Both tests repeatedly call `listmount(LSMT_ROOT, 0, last_mnt_id, list, 10, flags)` until zero entries are returned. The forward test asserts each batch is strictly increasing and advances `last_mnt_id` to the last returned id. The reverse test uses `LISTMOUNT_REVERSE`, asserts strictly decreasing ids, and likewise advances the cursor. No mount state is created or destroyed.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are listmount syscall support and `LSMT_ROOT` constants from kernel headers. It integrates with statmount helper wrappers. Risks are assumptions about strict id order across concurrent mount changes in the system namespace. Passing signals are nonnegative syscall results, eventual zero-length termination, and monotonic order within every batch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/listmount_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount.h

## Purpose

`statmount.h` provides local syscall wrappers and allocation helpers for `statmount` and `listmount` tests.

## Important APIs, Types, and Functions

It defines fallback syscall numbers for `statmount` and `listmount` on alpha, MIPS ABIs, and generic architectures. `statmount` builds `struct mnt_id_req` using mount id, mount namespace id, or fd when `STATMOUNT_BY_FD` is set. `listmount` builds a similar request with `last_mnt_id` in `param`. `statmount_alloc` and `statmount_alloc_by_fd` retry with doubling buffers on `EOVERFLOW`.

## Control Flow, State, and Persistence

Wrappers are synchronous syscall shims. Allocation helpers start at `STATMOUNT_BUFSIZE` (32 KiB), call the syscall, return the filled buffer on success, free and fail on non-overflow errors, or double the buffer on overflow. No state persists outside caller-owned allocated buffers.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on `<linux/mount.h>`, syscall ABI compatibility, and `struct mnt_id_req` version sizes. It integrates all statmount/listmount selftests and other namespace tests in this subset. Risks are stale fallback syscall numbers, ABI version mismatch, unbounded doubling on repeated overflow, and callers needing to free returned buffers. Passing signals are successful wrapper calls, correct fd-vs-id request selection, and overflow handling for string-heavy masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount_test.c

## Purpose

`statmount_test.c` is the main statmount/listmount ABI validation program. It checks mount ids, parent ids, propagation, superblock fields, string fields, mount options, pagination, and `STATMOUNT_BY_FD` behavior.

## Important APIs, Types, and Functions

Helpers include `write_file`, `get_mnt_id`, `cleanup_namespace`, `setup_namespace`, `setup_mount_tree`, many `test_statmount_*` functions, and `test_listmount_tree`. It uses `statmount`, `listmount`, `statmount_alloc`, `statmount_alloc_by_fd`, `statx`, `statfs`, mount namespace and user namespace setup, bind mounts, chroot, and kselftest result APIs.

## Control Flow, State, and Persistence

`main` probes syscall support, sets up a private user/mount/pid namespace, maps uid/gid, opens mountinfo, creates a temporary bind-mounted root, chroots into it, and records old and unique mount ids for root and parent. It plans 17 tests: list an empty root, zero-mask statmount, mount basic fields, superblock fields, mount root and point strings, filesystem type from a known list, mount options compared with `/proc/self/mountinfo`, string exact-size and `EOVERFLOW` checks, all-mask string checks, listmount tree pagination over propagated bind mounts, statmount by fd on an unmounted mount, and statmount by fd across chroot visibility. Cleanup restores the original root and detaches the temporary mount.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are statmount/listmount syscalls, statx unique mount ids, user namespace mapping, mountinfo format, statfs, bind mounts, and chroot. It integrates directly with the new mount introspection ABI. Risks include exact option-string comparison, known filesystem list aging, global mount changes, chroot cleanup hazards, and statmount masks being optional on older kernels. Passing signals are matching ids/parents, correct masks and sizes, string offsets in bounds, `EOVERFLOW` on short buffers, matching mount options, correct pagination, and expected hidden mountpoint behavior for inaccessible or detached mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount_test_ns.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount_test_ns.c

## Purpose

`statmount_test_ns.c` validates mount namespace id reporting through statmount and listmount, including by-fd behavior and querying another process's mount namespace.

## Important APIs, Types, and Functions

It defines `NSID_PASS`, `NSID_FAIL`, `NSID_SKIP`, and `NSID_ERROR`, with `handle_result` translating child return codes to kselftest results. Helpers include `get_mnt_ns_id`, `setup_namespace`, `_test_statmount_mnt_ns_id`, `_test_statmount_mnt_ns_id_by_fd`, `test_statmount_mnt_ns_id`, `validate_external_listmount`, and `test_listmount_ns`. APIs include `ioctl(NS_GET_MNTNS_ID)`, `statmount`, `listmount`, `STATMOUNT_BY_FD`, `get_unique_mnt_id`, `setup_userns`, `fork`, and `wait_for_pid`.

## Control Flow, State, and Persistence

The statmount namespace-id test forks a child, sets up a user namespace, obtains the current mount namespace id from nsfs, stats `/` with `STATMOUNT_MNT_NS_ID`, and checks equality. The by-fd subtest bind-mounts a temporary directory, stats namespace id by fd while mounted, detaches it, and verifies `STATMOUNT_MNT_NS_ID` is no longer reported for the detached mount. The listmount namespace test creates a child namespace with a known mount count, then the parent gets the child's mount namespace id through `/proc/<pid>/ns/mnt` and calls `listmount` against that external id to validate visibility/count behavior. State is mostly child namespaces, temp bind mounts, and namespace ids.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are nsfs mount namespace ids, statmount/listmount namespace-id support, user namespace helpers, procfs, and mount privilege. It integrates namespace-aware mount introspection across process boundaries. Risks include child synchronization, namespace lifetime tied to process/fd references, optional mask support producing skips, and a diagnostic `sleep(60)` on open failure. Passing signals are matching statmount namespace ids, missing namespace id for detached by-fd mounts, and successful external listmount count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount_test_ns.c -->
