# Group Research: group_1803_util_linux_sources_block_storage_util_linux_sys_utils_lsns_c_source_a5c05e4a988b

Scope: `Docs/research_subset_a.md`, specifically the `sources/block-storage/util-linux` source tree. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lsns.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lsns.c

This file implements `lsns(8)`, the namespace inventory command. It builds an in-memory model of processes and namespaces by scanning `/proc`, reading `/proc/<pid>/stat`, `/proc/<pid>/ns/*`, open namespace file descriptors, nsfs bind mounts from `/proc/self/mountinfo`, and, when supported, namespace metadata from `NS_GET_*` ioctls.

The central types are `struct lsns`, `struct lsns_process`, and `struct lsns_namespace`. Processes carry per-namespace inode IDs, parent/owner namespace IDs, UID, command metadata, and namespace sibling links. Namespaces carry type, inode ID, process count, representative lowest PID, optional UID fallback, network namespace ID, and parent/owner relationship pointers.

Network namespaces receive extra handling through rtnetlink `RTM_GETNSID`, a small inode-to-netnsid cache, and optional socket namespace discovery with `pidfd_open()`, `pidfd_getfd()`, and `SIOCGSKNS`. When `USE_NS_GET_API` is available, the command can discover persistent or otherwise processless namespaces from nsfs fds and can connect parent/owner namespace trees.

Output is driven by libsmartcols. Column definitions cover namespace ID/type/path/process counts, representative PID/PPID/command/user, netnsid, nsfs mountpoints, parent namespace, and owner namespace. The command supports raw, JSON, no-heading, no-wrap, custom columns, hidden columns needed for `--filter`, namespace/process trees, parent/owner trees, `--persistent`, `--task`, namespace ID selection, and namespace type filtering.

Important behavior: default output becomes a process tree unless list mode is forced; selecting a namespace ID changes the default columns to process-oriented columns. Owner/parent tree modes require nsfs ioctl support. The code treats disappearing `/proc` tasks as normal races and suppresses many transient `EACCES`, `ENOENT`, and `ESRCH` failures so listing remains best-effort.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lsns.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/meson.build -->
# File Research: sources/block-storage/util-linux/sys-utils/meson.build

This Meson fragment declares source lists and manpage inputs for many `sys-utils` programs in util-linux. The files in this research group are represented by target variables such as `rfkill_sources`, `renice_sources`, `setpgid_sources`, `setsid_sources`, `readprofile_sources`, `rtcwake_sources`, `setarch_sources`, `prlimit_sources`, `lsns_sources`, `mount_sources`, `mountpoint_sources`, `pivot_root_sources`, `nsenter_sources`, `setpriv_sources`, and `swapoff_sources`.

Most entries are simple `files('name.c')` declarations paired with `*_manadocs`. Some targets append shared helper source sets, for example `nsenter_sources` includes `caputils_c` and `exec_shell_c`, `setpriv_sources` includes `caputils_c`, and `swapoff_sources` includes `swapon-common.c`, `swapon-common.h`, and `swapprober_c`. `setpriv-landlock.c` is conditionally added only on Linux builds with `HAVE_LINUX_LANDLOCK_H`.

The file also shows sys-utils build conventions: generated parser sources for `hwclock`, conditional systemd unit installation for `fstrim`, and target-local source variables that later build rules consume.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/mount.c -->
# File Research: sources/block-storage/util-linux/sys-utils/mount.c

This file implements the `mount(8)` frontend around libmount. It creates a `libmnt_context`, parses command-line options, configures sources, targets, fstab tables, option modes, namespace targets, bind/move/propagation operations, ID-mapped mount options, helper policy, fake mode, fork mode, canonicalization, and mtab behavior, then delegates the actual operation to libmount.

Major execution paths are listing current mounts, `mount -a`, `mount -a -o remount`, single-source/target mounting, bind/rbind/move operations, and propagation-only changes. `print_all()` reads the current mtab through libmount and prints classic `source on target type fstype (opts)` lines. `mount_all()` and `remount_all()` iterate libmount’s fstab-driven operation APIs and produce aggregate exit codes for all-success, all-failed, and mixed results.

The code contains compatibility and safety logic for setuid execution. Restricted users may only use a narrow option subset until `suid_drop()` permanently drops elevated privileges and restores sanitized environment variables. `sanitize_paths()` uses restricted canonicalization so non-root users cannot exploit unreadable path resolution. Parser callbacks convert fstab parse errors into warnings.

Option parsing translates traditional CLI flags into libmount option strings or context flags, including `-L`/`-U`, `--source`, `--target`, `--target-prefix`, `--options-mode`, `--options-source`, `--onlyonce`, `--exclusive`, `--beneath`, `--namespace`, and `--map-users`/`--map-groups`. Final status comes from `mk_exit_code()`, which asks libmount for backward-compatible mount exit codes and prints libmount warnings/info plus SELinux and systemd hints when applicable.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/mountpoint.c -->
# File Research: sources/block-storage/util-linux/sys-utils/mountpoint.c

This file implements `mountpoint(1)`, checking whether a path is a mountpoint or printing device numbers. It supports quiet mode, no-follow symlink behavior, filesystem device number output, block-device major:minor output, and `--show` to print the mountpoint for a path.

The primary check is `dir_to_device()`. On systems with statmount support it first uses `mnt_id_from_path()` and `mnt_fs_fetch_statmount()` to compare the kernel-reported mountpoint with the requested path and to obtain the filesystem device number. Otherwise it falls back to parsing `/proc/self/mountinfo` with libmount and finding a target match. If mountinfo is unavailable, it uses the traditional parent-directory stat heuristic, which cannot detect bind mounts.

`--devno` validates that the path is a block device and prints `st_rdev`. `--show` requires statmount support in this implementation. Exit status uses `32` for “not a mountpoint,” matching the utility’s historical behavior.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/mountpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/nsenter.c -->
# File Research: sources/block-storage/util-linux/sys-utils/nsenter.c

This file implements `nsenter(1)`, a command-line wrapper for `setns(2)` and related process setup. It can enter mount, UTS, IPC, network, PID, cgroup, user, and time namespaces from a target PID, explicit namespace path, namespace ID, socket fd, or parent user namespace, then execute a requested program or shell.

Namespace state is represented by `namespace_files[]`, whose order is significant because user namespaces may need to be entered before or after other namespaces depending on whether privileges are being gained or reduced. The implementation supports pidfd-based multi-namespace `setns()` on newer kernels, fd-by-fd fallback, namespace ID lookup via nsfs file handles and `open_by_handle_at()`, and network namespace discovery from a target process socket with `pidfd_getfd()` and `SIOCGSKNS`.

After entering namespaces, the command can chroot to the target root, set cwd either from the target or inside the entered namespace, import the target environment, set UID/GID or follow the target process’s credentials, preserve credentials, retain ambient capabilities for user namespaces, set SELinux exec context, and join the target cgroup v2 by writing to `cgroup.procs`.

Important behavior: entering PID namespaces defaults to forking so the command runs as a child in the new PID namespace. `--all` skips unusable namespaces, including reentering the current user namespace. Namespace entry happens in two passes: non-user namespaces first with ignored errors, then remaining namespaces with fatal errors.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/nsenter.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/pivot_root.c -->
# File Research: sources/block-storage/util-linux/sys-utils/pivot_root.c

This small file implements `pivot_root(8)` as a direct wrapper around the `SYS_pivot_root` syscall. It accepts only `new_root` and `put_old` positional arguments plus help/version options.

The command performs locale/stdout setup, validates exactly two arguments, calls `pivot_root(argv[1], argv[2])`, and reports a fatal error if the syscall fails. It intentionally leaves all mount namespace setup and path preparation to the caller.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/pivot_root.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/prlimit.c -->
# File Research: sources/block-storage/util-linux/sys-utils/prlimit.c

This file implements `prlimit(1)`, showing or changing resource limits for the current process, another process, or a command to be executed. It wraps `prlimit64` directly when libc lacks `prlimit()`.

Resource metadata is held in `prlimit_desc[]`, covering address space, core size, CPU, data, file size, locks, memlock, message queues, nice, open files, processes, RSS, realtime priority/time, pending signals, and stack. Requested operations are represented as `struct prlimit` entries in a list; entries either request current values for display or contain new soft/hard limits to apply.

Limit parsing accepts `value`, `soft:hard`, `soft:`, `:hard`, and `unlimited`. If only one side of a limit is supplied, `get_unknown_hardsoft()` fetches the existing limit to preserve the unspecified half. The code rejects soft limits above hard limits and checks `RLIMIT_NOFILE` against `/proc/sys/fs/nr_open`.

Output uses libsmartcols with configurable columns, raw mode, and no headings. If a command is supplied, limits are applied before `execvp()`. `--pid` accepts util-linux PID syntax with optional pidfd inode validation when supported.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/prlimit.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/readprofile.c -->
# File Research: sources/block-storage/util-linux/sys-utils/readprofile.c

This file implements `readprofile(8)`, a legacy reader for Linux kernel profiling data from `/proc/profile` correlated with `System.map`. It can display sampling step info, reset counters, set the profiling multiplier, print all symbols, print individual histogram bins, print per-function counters, and handle compressed `.gz` map files through a forked `zcat`.

The program reads the whole profile buffer as unsigned integers, optionally detects reversed byte order using a heuristic over high/low half-word usage, and treats `buf[0]` as the sampling step. It opens the requested map file or falls back from `/boot/System.map` to `/boot/System.map-$(uname -r)`.

Main processing finds `_stext`/`__stext`, then walks text symbols until `_etext`/`__etext`, accumulating profile bins whose addresses fall inside each function. It prints either per-bin counts or per-symbol totals and normalized counts per byte, then emits the final unknown bucket and total. Reset and multiplier writes use `/proc/profile` with root attempt via `setuid(0)`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/readprofile.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/renice.c -->
# File Research: sources/block-storage/util-linux/sys-utils/renice.c

This file implements `renice(1)`, changing nice values for processes, process groups, or users. It supports `-p`, `-g`, and `-u` selectors, numeric or named users, and three priority modes: historical absolute `-n`, POSIX-relative `-n` when `POSIXLY_CORRECT` is set, explicit `--priority`, and explicit `--relative`.

For each target, `donice()` reads the old priority with `getpriority()`, computes the new priority, calls `setpriority()`, reads the result back, and prints old/new values. Errors are accumulated so multiple targets can be attempted before returning failure.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/renice.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/rfkill.c -->
# File Research: sources/block-storage/util-linux/sys-utils/rfkill.c

This file implements the `/dev/rfkill` control utility. It supports listing devices, streaming events, blocking, unblocking, and toggling rfkill state by numeric index, type name, or `all`. Type aliases include `wifi` for WLAN and `ultrawideband` for UWB, with compatibility definitions for older kernel headers.

Device state is read by opening `/dev/rfkill` and consuming `struct rfkill_event` records, while sysfs under `/sys/class/rfkill/rfkill<N>/` supplies names and type strings for output. Modern list output uses libsmartcols with optional JSON/raw/no-heading/custom columns. Explicit `list` without custom output preserves the deprecated historical multi-line format.

Block and unblock write `RFKILL_OP_CHANGE` or `RFKILL_OP_CHANGE_ALL` events to `/dev/rfkill` and log the change through syslog. Toggle reads current add events, matches the selected device or type, and writes the opposite soft-block value. Event mode polls indefinitely and prints timestamped raw event fields until polling or stdout fails.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/rfkill.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/rtcwake.c -->
# File Research: sources/block-storage/util-linux/sys-utils/rtcwake.c

This file implements `rtcwake(8)`, setting an RTC wake alarm and optionally suspending, powering off, waiting on the RTC, disabling the alarm, or showing the current alarm. It uses `/dev/rtc0` by default, RTC ioctls for time/alarm operations, `/sys/class/rtc/<rtc>/device/power/wakeup` to verify wakeup capability, and `/sys/power/state` for suspend modes.

Clock handling supports UTC, local time, or auto mode from the third line of the adjtime file. `get_basetimes()` reads RTC and system time close together, sets `TZ=UTC` when needed, and computes the delta used to translate POSIX alarm times into RTC time. Alarm setup writes `RTC_WKALM_SET`; cleanup disables the alarm unless dry-run or show/no mode prevents it.

Mode handling includes sysfs suspend states, `off` via shutdown/poweroff executable lookup, `on` by blocking on RTC alarm interrupts, `no` for alarm setup without suspend, `disable`, and `show`. The command also supports relative seconds, absolute time_t, parsed timestamp dates, dry-run, mode listing, and verbose diagnostics.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/rtcwake.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setarch.c -->
# File Research: sources/block-storage/util-linux/sys-utils/setarch.c

This file implements `setarch(8)` and its architecture-name wrapper aliases. It changes the process personality architecture and optional personality flags before executing a command or shell. It also lists supported architecture names and shows current or target process personality values.

Architecture support is encoded in `init_arch_domains()`, which builds a static transition table conditioned on compile-time architecture macros and adds the running machine as a trivial transition when appropriate. It maps names such as `linux32`, `linux64`, `i386`, `x86_64`, `arm`, `aarch64`, `ppc`, `s390`, `sparc`, `mips`, `riscv`, and others to `PER_*` values and expected `uname` results. `verify_arch_domain()` checks that the kernel accepted the requested architecture.

Personality flags include address limit flags, no-randomize, read-implies-exec, mmap-page-zero, sticky-timeouts, uname-2.6, FDPIC function pointers, and compatibility options. `--show` decodes the personality and option bits into symbolic names, optionally using `/proc/<pid>/personality`. After calling `personality()`, the command execs the provided program or a login-style `/bin/sh`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setarch.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setpgid.c -->
# File Research: sources/block-storage/util-linux/sys-utils/setpgid.c

This file implements `setpgid(1)`, running a command in a new process group. It calls `setpgid(0, 0)` for the current process before `execvp()`.

With `--foreground`, it opens `/dev/tty`, temporarily blocks `SIGTTOU`, and calls `tcsetpgrp()` to make the new process group foreground for the controlling terminal. The utility otherwise only handles argument validation, help/version output, and exec error reporting.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setpgid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setpriv-landlock.c -->
# File Research: sources/block-storage/util-linux/sys-utils/setpriv-landlock.c

This file implements the Landlock-specific support used by `setpriv(1)`. It provides syscall fallbacks for `landlock_create_ruleset`, `landlock_add_rule`, and `landlock_restrict_self` when libc does not expose wrappers.

The parser supports `--landlock-access fs` or `fs:<rights>` and path-beneath rules of the form `path-beneath:<rights>:<path>`. Rights map to `LANDLOCK_ACCESS_FS_*` constants, including conditionally compiled newer rights such as `refer`, `truncate`, and `ioctl-dev`. Empty right lists mean all known filesystem rights.

`do_landlock()` creates a ruleset with the requested handled filesystem accesses, adds all parsed path-beneath rules using `O_PATH` parent fds, sets `PR_SET_NO_NEW_PRIVS`, then restricts the current process. Landlock failures use setpriv’s privilege-error exit code `127`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setpriv-landlock.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setpriv-landlock.h -->
# File Research: sources/block-storage/util-linux/sys-utils/setpriv-landlock.h

This header declares the Landlock option structure and helper functions used by `setpriv.c`. When `HAVE_LINUX_LANDLOCK_H` is available, `struct setpriv_landlock_opts` stores the handled filesystem access mask and a list of parsed rules.

When Landlock headers are unavailable, the header provides empty stubs. Runtime attempts to parse Landlock access or rules fail with “no support for landlock,” while initialization, application, and usage extension become no-ops. This keeps `setpriv.c` buildable without conditional call sites.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setpriv-landlock.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setpriv.c -->
# File Research: sources/block-storage/util-linux/sys-utils/setpriv.c

This file implements `setpriv(1)`, executing a program after changing Linux privilege state. It supports dumping current state, listing capabilities, no-new-privs, inheritable/ambient/bounding capabilities, real/effective UID/GID, supplementary group policies, securebits, parent-death signal, Yama ptracer allowance, SELinux exec label, AppArmor exec profile, Landlock, seccomp filter loading, and environment reset.

`struct privctx` accumulates all requested changes. Capability handling uses libcap-ng for effective/permitted/inheritable/bounding sets and direct `prctl(PR_CAP_AMBIENT, ...)` for ambient capabilities. Capability strings require `+` or `-` actions and accept `all`, libcap-ng names, or numeric `cap_N`. Securebits parsing allows selected securebit toggles but refuses `+all` and direct `keep_caps` adjustment.

Dump mode reports real/effective/saved IDs, supplementary groups, no-new-privs, effective/permitted/inheritable/ambient/bounding capabilities, securebits, parent-death signal, and active SELinux/AppArmor labels when their filesystems exist. Reset-env preserves terminal color variables, clears the environment, then sets `SHELL`, `HOME`, `USER`, `LOGNAME`, and `PATH` from passwd/logindefs data.

Main validation enforces that GID changes must explicitly choose a supplementary-group policy, `--init-groups` requires a resolvable `--ruid`/`--reuid`, `--dump` is standalone, and `--list-caps` is standalone. The application order is significant: reset environment; set no-new-privs/LSM labels/seccomp; enable keepcaps; raise helper caps; set UIDs and reapply caps; set GIDs/groups; set securebits; apply bounding, inheritable, and ambient caps; set parent-death signal and ptracer; apply Landlock; then `execvp()`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setpriv.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setsid.c -->
# File Research: sources/block-storage/util-linux/sys-utils/setsid.c

This file implements `setsid(1)`, running a command in a new session. It optionally forks first, always forks when the current process is already a process-group leader, then calls `setsid()` in the child path before executing the requested command.

Options include `--ctty` to set the controlling terminal with `TIOCSCTTY`, `--fork` to force forking, and `--wait` to have the parent wait and return the child’s exit status. Without `--wait`, the parent exits successfully after forking.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/setsid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/swapoff.c -->
# File Research: sources/block-storage/util-linux/sys-utils/swapoff.c

This file implements `swapoff(8)`, disabling swap devices or files by path, `LABEL=`, `UUID=`, `-L`, `-U`, or `--all`. It uses the `swapoff(2)` syscall or a syscall fallback, libmount tables for `/proc/swaps` and fstab, blkid probing helpers, and the shared `swapon-common` infrastructure.

`do_swapoff()` resolves non-canonical specs through the global libmount cache and, for swap files, can resolve labels/UUIDs by scanning active swap files from `/proc/swaps` and probing them directly. It maps failures into bitwise exit codes distinguishing success, ENOMEM, generic swapoff failure, system errors, usage errors, all-failed, and mixed `--all` results.

`swapoff_all()` first disables active swaps from `/proc/swaps` in reverse order, counting success/failure, then scans fstab swap entries and quietly attempts inactive entries not already present. Main lowers its OOM killer score via `/proc/oom_adj`, initializes the libmount cache, processes labels, UUIDs, positional specs, and `--all`, then frees shared tables and returns the combined status.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/swapoff.c -->