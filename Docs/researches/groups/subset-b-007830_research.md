# subset-b-007830 Research

Grouped research for the listed OrangeFS kernel-client, user utility, visualization, cp-library, and Hadoop 1 adapter files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/kernel/linux/pvfs2-client.c -->
# sources/distributed-fs/orangefs/src/apps/kernel/linux/pvfs2-client.c

## Purpose
Implements the supervising `pvfs2-client` daemon wrapper for Linux kernel-client deployments. It validates root execution, optionally backgrounds itself, watches a child `pvfs2-client-core`, forwards signals, and translates wrapper options into the core process command line.

## Important APIs, Types, And Functions
`options_t` carries cache, logging, descriptor, performance, readahead, event, key, and BMI settings. `main` parses options, installs signal handlers, daemonizes, and enters `monitor_pvfs2_client`. `client_sig_handler` kills the process group and waits for the core child on normal termination signals. `verify_pvfs2_client_path` checks executable paths. `monitor_pvfs2_client` forks, builds `arg_list`, execs `pvfs2-client-core`, and interprets exit statuses. `parse_args` maps short and long command-line switches to `options_t`.

## Control Flow
The parent loops forever spawning the core, redirecting stdio to `/dev/null`, waiting for exit, and logging restart decisions. Device-initialization failures sleep and retry up to `MAX_DEV_INIT_FAILURES`; `PVFS_ENODEV` exits; `PVFS_EAGAIN` restarts immediately; signal deaths are rate-limited by `CLIENT_RESTART_INTERVAL_SECS` and `CLIENT_MAX_RESTARTS`.

## State And Persistence
State is in memory: `core_pid`, `s_client_core_path`, parsed option pointers, restart counters, and the process group. Persistent effects are the log target, syslog records, and the running child process. No config file is written.

## Dependencies And Integration Points
Depends on POSIX process/signal APIs, `gossip` logging, OrangeFS error codes, and cache defaults from `acache.h`/`ncache.h`. It is the service-level launcher for the kernel request-device client core.

## Risks And Test Signals
Risks include fixed `arg_list[128]` capacity, duplicated `--perf-time-interval-secs` forwarding, signal fanout with `kill(0, signum)`, assert-based fork/wait handling, leaked logfile open descriptor from writability probing, and options accepted by `parse_args` only when build flags expose them. Test signals are root/non-root startup, foreground/background behavior, invalid core path rejection, restart throttling, logtype variants, signal shutdown, and forwarding of every option to the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/kernel/linux/pvfs2-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/kernel/linux/umount_pvfs2.sh -->
# sources/distributed-fs/orangefs/src/apps/kernel/linux/umount_pvfs2.sh

## Purpose
Provides a small manual teardown script for a test OrangeFS kernel mount at `/tmp/mnt`.

## Important APIs, Types, And Functions
The script directly invokes `umount`, `killall -TERM pvfs2-client`, `sleep`, `fuser /dev/pvfs2-req`, and `rmmod pvfs2`. There are no shell functions or arguments.

## Control Flow
It unmounts `/tmp/mnt`, terminates all `pvfs2-client` processes, waits two seconds, then removes the `pvfs2` kernel module only if `fuser` reports no remaining users of `/dev/pvfs2-req`. If the device is still open it prints a warning and the active users.

## State And Persistence
State changes are host-level and destructive for the test mount: unmount state, daemon processes, and kernel module load state. It does not persist files.

## Dependencies And Integration Points
Integrates with Linux module tooling and the OrangeFS kernel request device. It assumes the mountpoint, module name, and daemon name are fixed.

## Risks And Test Signals
Risks are hard-coded paths, killing all matching clients on the host, no error checks for failed unmount or kill, and no privilege validation. Test signals are clean unmount with no device users, warning behavior with an intentionally held descriptor, and successful module removal on an isolated test host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/kernel/linux/umount_pvfs2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/module.mk.in -->
# sources/distributed-fs/orangefs/src/apps/ucache/module.mk.in

## Purpose
Registers the user-cache daemon sources in the OrangeFS build when `BUILD_UCACHE` is enabled.

## Important APIs, Types, And Functions
The make fragment sets `DIR := src/apps/ucache` and appends `ucached.c` and `ucached_cmd.c` to `UCACHEDSRC`. There are no functions; the API is the build variable contract consumed by higher-level make logic.

## Control Flow
The whole fragment is gated by `ifdef BUILD_UCACHE`; when unset it contributes no sources. When set, both daemon and command helper are compiled as the user-cache application set.

## State And Persistence
No runtime state. Build state is the make variable expansion used during configure-generated builds.

## Dependencies And Integration Points
Depends on the top-level make system defining `BUILD_UCACHE` and consuming `UCACHEDSRC`. It ties the application layer to user-cache shared-memory support under `src/client/usrint`.

## Risks And Test Signals
Risks are stale source lists if ucache files move or new daemon support files are added without updating this fragment. Test signals are configure/build runs with `BUILD_UCACHE` enabled and disabled, verifying that both `ucached` and `ucached_cmd` targets are present only when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached.c -->
# sources/distributed-fs/orangefs/src/apps/ucache/ucached.c

## Purpose
Implements the `ucached` daemon that creates, destroys, and inspects System V shared-memory regions used by the OrangeFS user cache. It also exposes a FIFO command protocol for `ucached_cmd`.

## Important APIs, Types, And Functions
Important functions are `main`, `run_as_child`, `execute_cmd`, `create_ucache_shmem`, `destroy_ucache_shmem`, `ucached_lockchk`, `clean_up`, and `check_rc`. Global state includes FIFO descriptors, the command buffer, `ucache_avail`, parent/child `pid`, and `locked_time` for every cache block. It uses `ucache`, `ucache_aux`, `ucache_lock`, `ucache_stats`, and lock/file-table helpers from the user-cache library.

## Control Flow
`main` enables gossip logging, daemonizes, optionally creates shared memory through a child, creates two FIFOs, and polls `FIFO1` for commands. Valid commands create (`c`), destroy (`d`), produce info (`i`), or exit (`x`). Creation first obtains/initializes the auxiliary lock segment, locks the global lock, initializes statistics, then attaches or creates the cache segment and file table. Destruction marks selected segments with `IPC_RMID`.

## State And Persistence
The daemon persists `/tmp/ucached.log`, `/tmp/ucached.info`, `/tmp/ucached.started`, two FIFOs, and SYSV shared-memory segments keyed by `/etc/fstab` plus IDs `l` and `m`. Cleanup removes FIFOs and, if enabled, marks shared memory for deletion at parent exit.

## Dependencies And Integration Points
Depends on SYSV IPC, POSIX daemon/FIFO/poll APIs, `gossip`, and `src/client/usrint/ucache.h`. `ucached_cmd.c` is the intended client. The daemon must coordinate with user processes attaching to the same shared-memory cache.

## Risks And Test Signals
Risks include world-writable FIFO permissions, hard-coded `/tmp` and `/etc/fstab` keys, blocking FIFO writes, incomplete cleanup if `mkfifo` fails after daemonization, `shmat` checked against `NULL` instead of `(void *)-1`, unused `ucache_avail`, and TODO-only hung-lock recovery. Test signals are start/create/destroy/info/exit command cycles, restart after stale shared memory, concurrent attach behavior, FIFO timeout behavior, and verifying no orphaned segments or FIFOs remain after shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached.h -->
# sources/distributed-fs/orangefs/src/apps/ucache/ucached.h

## Purpose
Defines constants, includes, and shared settings for the ucache daemon and command helper.

## Important APIs, Types, And Functions
The header exports no functions. It defines daemon file paths (`UCACHED_LOG_FILE`, `UCACHED_INFO_FILE`, `UCACHED_STARTED`), gossip masks, FIFO names and buffer sizes, shared-memory key inputs (`KEY_FILE`, `SHM_ID1`, `SHM_ID2`), permissions (`FILE_MODE`, `SVSHM_MODE`), and control defaults (`CREATE_AT_START`, `DEST_AT_EXIT`, `FIFO_TIMEOUT`, `BLOCK_LOCK_TIMEOUT`).

## Control Flow
Compile-time `#ifndef` guards allow build or compiler flags to override most defaults. Both `ucached.c` and `ucached_cmd.c` consume the same constants so daemon and client agree on IPC paths.

## State And Persistence
The header defines the persistent namespace for the daemon: `/tmp` files/FIFOs and SYSV keys derived from `/etc/fstab`. It does not own runtime state itself.

## Dependencies And Integration Points
Pulls in POSIX, SYSV IPC, poll, and `ucache.h` declarations needed by daemon code. It bridges application commands to user-cache shared-memory structures.

## Risks And Test Signals
Risks are hard-coded globally shared IPC paths, permissive `0666` FIFO/shared-memory permissions, and build-time overrides that can desynchronize daemon and command binaries. Test signals include compiling both binaries with default and overridden paths, permission checks, and successful command exchange against the same FIFO names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached_cmd.c -->
# sources/distributed-fs/orangefs/src/apps/ucache/ucached_cmd.c

## Purpose
Implements the `ucached_cmd` command-line client for starting `ucached` and sending daemon commands through FIFOs.

## Important APIs, Types, And Functions
`main` is the only function. It recognizes command characters `s`, `c`, `d`, `x`, and `i`. It uses `UCACHED_STARTED`, `FIFO1`, `FIFO2`, `BUFF_SIZE`, and `UCACHED_INFO_FILE` from `ucached.h`.

## Control Flow
For `s`, it checks `/tmp/ucached.started`, removes stale FIFOs, launches `ucached` with `system`, writes the started marker, and returns. Other commands open `FIFO1` for writing, send the command plus optional argument, open `FIFO2` for reading, print the response, and for `i` additionally opens and prints `UCACHED_INFO_FILE`.

## State And Persistence
It mutates the daemon marker and can remove FIFOs before daemon start. It reads daemon-created info and response data but does not manage shared memory directly.

## Dependencies And Integration Points
Depends on the daemon FIFO protocol, `usrint.h`, POSIX file APIs, and matching constants in `ucached.h`. It is the operator-facing control plane for `ucached.c`.

## Risks And Test Signals
Risks include race-prone started-file detection, no verification that `system("ucached")` succeeded, unsafe `strcat` into a fixed command buffer for optional arguments, blocking opens when daemon/FIFOs are absent, and `i` mode reading a possibly missing info file after printing a success response. Test signals are start idempotency, create/destroy/info/exit round trips, daemon-not-running failures, long optional argument handling, and stale marker/FIFO recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/getmattr.c -->
# sources/distributed-fs/orangefs/src/apps/user/getmattr.c

## Purpose
Retrieves OrangeFS mirroring extended attributes from a file through the kernel-mode client path. It is intended for numeric mirror settings that are not convenient to inspect with generic `getfattr`.

## Important APIs, Types, And Functions
`options_t` stores filename plus booleans for copies and mode. `main` calls `getxattr` for `user.pvfs2.mirror.mode` and `user.pvfs2.mirror.copies`, then prints decoded values. `parse_args` handles `-c`, `-m`, `-f`, and help. `usage` exits after printing command syntax.

## Control Flow
If neither `-c` nor `-m` is supplied, both attributes are queried. Mode values are decoded against `NO_MIRRORING` and `MIRROR_ON_IMMUTABLE` from `pvfs2-mirror.h`; unknown values are reported as unsupported.

## State And Persistence
Read-only except for stdout/stderr. It observes xattrs stored on the target OrangeFS file.

## Dependencies And Integration Points
Depends on Linux or Darwin-style xattr prototypes via `HAVE_GETXATTR_EXTRA_ARGS`, `pvfs2.h`, and `pvfs2-mirror.h`. It integrates with mirror-policy code that stores `user.pvfs2.mirror.*` xattrs.

## Risks And Test Signals
Risks include treating a zero-length successful xattr read as failure because it checks `if (!ret)`, limited validation of file path existence, and direct binary integer representation in xattrs. Test signals are files with both mirror attributes set, missing attributes, supported and unsupported mode values, and builds on platforms with both xattr signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/getmattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/graphite_connect_test.c -->
# sources/distributed-fs/orangefs/src/apps/user/graphite_connect_test.c

## Purpose
Standalone connectivity probe that repeatedly sends a fixed metric to a hard-coded Graphite endpoint on TCP port 2003.

## Important APIs, Types, And Functions
`main` loops forever building `system.graphite_test 1000 <timestamp>` and writing it to a socket. `graphite_connect` opens an IPv4 TCP socket, resolves the address with `gethostbyname`, fills `sockaddr_in`, and connects.

## Control Flow
Every 20 seconds it opens a fresh connection, writes the NUL-terminated metric buffer, closes the socket, and repeats. There is no command-line parsing.

## State And Persistence
No local persistence. External state is one metric stream delivered to Graphite if the endpoint is reachable.

## Dependencies And Integration Points
Uses POSIX sockets, DNS/host lookup APIs, and Graphite plaintext protocol conventions. It is a developer/test utility related to `ofs_graphite_driver.c`.

## Risks And Test Signals
Risks include hard-coded IP address, implicit prototype for `graphite_connect` in old C modes, unused variables, printing `server->h_addr` as a string, no handling for failed connect before `write`, and sending `strlen()+1` including a NUL byte. Test signals are connection success to a test Graphite listener, failure handling for invalid host, and validating the emitted plaintext metric format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/graphite_connect_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/module.mk.in -->
# sources/distributed-fs/orangefs/src/apps/user/module.mk.in

## Purpose
Build-system fragment listing OrangeFS user utilities compiled when the user-interface layer is enabled.

## Important APIs, Types, And Functions
The fragment sets `DIR := src/apps/user` and, when `build_usrint` is `yes`, appends `getmattr.c`, `ofs_rm.c`, `ofs_cp.c`, `ofs_graphite_driver.c`, `ofs_setdirhint.c`, `pvfs2-rm.c`, and `setmattr.c` to `USERSRC`.

## Control Flow
The conditional `ifeq ($(build_usrint),yes)` gates all utility sources. No generated target appears when user-interface support is disabled.

## State And Persistence
No runtime state. The only state is make variable composition during build generation.

## Dependencies And Integration Points
Consumed by the top-level OrangeFS automake/make machinery. It ties user-space utilities to the `usrint` build option and shared headers such as `orange.h`.

## Risks And Test Signals
Risks are stale lists, missing `graphite_connect_test.c` if expected as a built utility, and inconsistent gating if a utility no longer requires `usrint`. Test signals are builds with `build_usrint=yes/no` and checking expected binaries in the install tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_cp.c -->
# sources/distributed-fs/orangefs/src/apps/user/ofs_cp.c

## Purpose
Implements `ofs_cp`, a copy utility that works across local and OrangeFS paths while preserving selected metadata and applying OrangeFS layout, distribution, and datafile hints at destination creation.

## Important APIs, Types, And Functions
`cp_options` stores copy flags, buffer size, striping/datafile/layout hints, source/destination paths, and timing totals. `main` parses arguments, allocates a transfer buffer, chooses one-to-one or directory-copy mode, traverses sources with FTS, and delegates file copies. `copy_file` opens source/destination, builds `PVFS_hint` values (`PVFS_HINT_DFILE_COUNT_NAME`, distribution, layout, server list), streams read/write data, and preserves mode/owner/timestamps. `edit_dest_path`, `Wtime`, `print_timings`, `parse_args`, and `usage` support traversal, reporting, and command-line handling.

## Control Flow
Destination classification comes from `stat`/`pvfs_stat_mask`. Recursive directory copies use `fts_open` with symlink following on command-line roots but physical traversal. Directories are created preorder and metadata adjusted postorder. Files are copied in `buf_size` chunks; symlinks are recreated with `readlink`/`symlink`.

## State And Persistence
It creates files/directories/symlinks, truncates destination files, updates permissions, ownership, and times, and can set OrangeFS creation hints. Runtime state is the global destination buffer, a per-copy transfer buffer, and aggregate byte count.

## Dependencies And Integration Points
Depends on POSIX file APIs, FTS, `orange.h`, `pint-sysint-utils.h`, PVFS stat helpers, and OrangeFS hint-aware open support (`O_HINTS`). It integrates with OrangeFS layout and distribution xattr/creation paths indirectly through hints.

## Risks And Test Signals
Risks include hand-maintained `index` instead of `optind`, long-path truncation in `dest_path_buffer`, no cleanup of allocated `server_list`/one-to-one path strings, partial write handling without retry, symlink `readlink` result not NUL-terminated before `symlink`, and option definitions marking long options with `has_arg=0` even when arguments are required. Test signals are local-to-OFS, OFS-to-local, OFS-to-OFS, recursive, symlink, metadata-preserving, layout/list-layout, large-buffer, overwrite, and missing-destination scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_graphite_driver.c -->
# sources/distributed-fs/orangefs/src/apps/user/ofs_graphite_driver.c

## Purpose
Continuously polls OrangeFS server performance counters or timers and emits metrics to stdout and/or a Graphite plaintext endpoint.

## Important APIs, Types, And Functions
`options` captures mount point, Graphite host, name prefix, single-server selection, counter/timer type, key/history/frequency settings, raw/print/debug flags. `GRAPHITE_CNT` computes raw or delta counter samples and writes/prints them. `GRAPHITE_TIMER` emits sum/average/count/min/max timer values. `main` initializes OrangeFS, resolves the mount, discovers I/O servers, allocates performance matrices, calls `PVFS_mgmt_perf_mon_list` in an infinite loop, formats metric names, and tracks last samples. `parse_args`, `usage`, `graphite_connect`, and `print_sample` support setup.

## Control Flow
After defaults are filled, the tool optionally connects to Graphite, initializes PVFS, resolves the mount point, gets I/O server addresses, and enters a polling loop. Each loop refreshes credentials, fetches up to `history` samples, skips the very first sample to avoid counter discontinuity, emits selected counter/timer names, saves the last sample per server, and sleeps.

## State And Persistence
Runtime state includes dynamically allocated matrices, per-server last samples, next sample IDs, server names, and the Graphite socket. It writes no local files but publishes external metrics.

## Dependencies And Integration Points
Depends on `pvfs2.h`, `pvfs2-mgmt.h`, `pvfs2-internal.h`, POSIX sockets, DNS, and Graphite port 2003. It is an operational monitoring integration for OrangeFS performance monitor APIs.

## Risks And Test Signals
Risks include DEBUG always enabled, infinite loop with limited cleanup, sending NUL bytes with metrics, possible server-index mismatch when single-server mode narrows arrays, unchecked `strcat` into metric name buffers, and dependence on internal counter enum ordering. Test signals are counter and timer polling against a test cluster, single-server selection, Graphite listener output validation, raw versus delta output, credential refresh, and handling of unreachable Graphite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_graphite_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_rm.c -->
# sources/distributed-fs/orangefs/src/apps/user/ofs_rm.c

## Purpose
Implements a POSIX-like `rm` utility for OrangeFS-capable paths using FTS traversal and regular `unlink`/`rmdir` calls.

## Important APIs, Types, And Functions
`rm_options` stores force, interactive, recursive, verbose, debug, and filename list options. `main` opens an FTS traversal, optionally skips directory contents, prompts interactively, unlinks files/symlinks, removes directories postorder, and accumulates error state. `parse_args` handles short and long options. `usage` describes flags.

## Control Flow
Without `-r`, child directories are skipped and directory inputs report an error. With `-r`, directories are removed postorder. File and symlink cases are removed immediately. `-f` disables interactive prompting. The final exit code reflects whether any removal error was seen.

## State And Persistence
Destructively removes files, links, and directories. Runtime state is the FTS cursor and options-owned filename array; no persistent metadata is written.

## Dependencies And Integration Points
Depends on POSIX FTS, `orange.h`, `unlink`, and `rmdir`. It relies on mounted OrangeFS paths behaving through the VFS/client layer rather than direct PVFS sysint calls.

## Risks And Test Signals
Risks include manual `index` tracking instead of `optind`, `-V` printing version but continuing parse, force handling that appears inverted for `ENOENT` checks (`if ENOENT && !force break`), prompting loops that ignore EOF, and `fts_close(fs)` even if `fts_open` failed. Test signals are file, symlink, empty directory, non-empty directory with/without `-r`, missing file with/without `-f`, interactive yes/no, and mixed-success argument lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_rm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_setdirhint.c -->
# sources/distributed-fs/orangefs/src/apps/user/ofs_setdirhint.c

## Purpose
Sets OrangeFS directory hints as extended attributes on one or more directories, optionally recursively. Hints include distribution name/parameters, layout algorithm, server list, and datafile count.

## Important APIs, Types, And Functions
`user_options` stores selected hints and traversal flags. `layout_table_s` maps textual layouts (`none`, `round_robin`, `random`, `list`, `local`) and numeric strings to `PVFS_SYS_LAYOUT_*` values. `main` traverses with FTS, opens directories, and calls `fsetxattr` for `user.pvfs2.dist_name`, `dist_params`, `layout`, `server_list`, and `num_dfiles`. `translate_layout`, `parse_args`, and `usage` provide parsing.

## Control Flow
Without `-r`, child directories are skipped. For each preorder directory, optional interactive confirmation precedes setting requested xattrs. List layout converts a colon/list input into a `PVFS_sys_layout` using `pvfs_layout_fd`, serializes it with `pvfs_layout_string`, writes `user.pvfs2.server_list`, and derives `num_dfiles` from the layout count.

## State And Persistence
Persists user xattrs on directories, affecting later file placement/layout choices. Runtime state is the FTS traversal and allocated option strings.

## Dependencies And Integration Points
Depends on FTS, Linux xattr APIs, `orange.h`, OrangeFS layout helpers, and kernel-client xattr support. It complements `ofs_cp` creation hints by setting defaults on directories.

## Risks And Test Signals
Risks include flag string mismatch (`p` parsed as dist params but switch also has unreachable `s`), long-option names with underscores only, fixed 10-byte numeric buffers, possible descriptor leaks on early returns, typo/unreachable message in `translate_layout`, and limited validation of conflicting hints. Test signals are setting each xattr, recursive traversal, list layout conversion, invalid layout rejection, interactive skip, non-directory inputs, and verifying newly created files inherit expected hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_setdirhint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/pvfs2-rm.c -->
# sources/distributed-fs/orangefs/src/apps/user/pvfs2-rm.c

## Purpose
Older OrangeFS-specific remove utility that uses PVFS-aware stat and recursive delete helpers rather than FTS.

## Important APIs, Types, And Functions
`options` stores force, recursive, count, and filenames. `main` loops over input paths, calls `pvfs_lstat_mask(..., PVFS_ATTR_SYS_TYPE)`, dispatches directories to `recursive_delete_dir` when `-r` is set, and unlinks non-directories. `parse_args` handles `-r`, `-f`, and help; `usage` prints syntax.

## Control Flow
Missing files are ignored under force and reported otherwise. Directories require recursive mode; non-directories are removed with `unlink`. The final exit code is failure if any path produced an error.

## State And Persistence
Destructively removes OrangeFS files and possibly directory trees. No local persistence.

## Dependencies And Integration Points
Depends on `orange.h`, `recursive-remove.h`, PVFS stat wrappers, and the VFS unlink path. It is a simpler predecessor/alternative to `ofs_rm.c`.

## Risks And Test Signals
Risks include no interactive/verbose support, reliance on PVFS-only `pvfs_lstat_mask` so non-PVFS paths may fail, recursive helper behavior hidden in another module, and no NULL terminator in `filenames` array because the code tracks count separately. Test signals are PVFS files, missing paths with/without force, directory removal with/without recursive mode, symlink behavior, and mixed argument exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/pvfs2-rm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/setmattr.c -->
# sources/distributed-fs/orangefs/src/apps/user/setmattr.c

## Purpose
Sets OrangeFS mirror-mode and mirror-copy-count extended attributes on a file through the kernel client.

## Important APIs, Types, And Functions
`options_t` stores filename, copy count, and mode. `main` calls `setxattr` for `user.pvfs2.mirror.mode` and `user.pvfs2.mirror.copies`. `parse_args` validates numeric `-c` and `-m` values, requires `-f`, and accepts only `NO_MIRRORING` or `MIRROR_ON_IMMUTABLE` for positive modes. `usage` documents the numeric constants.

## Control Flow
The program exits on parse errors. It sets mode only when `mode > 0` and copies when `copies >= 0`, printing each attempted value and using platform-specific xattr signatures under `HAVE_SETXATTR_EXTRA_ARGS`.

## State And Persistence
Persists binary integer xattrs on the target file. It has no other local state.

## Dependencies And Integration Points
Depends on `pvfs2-config.h`, POSIX xattr APIs, `pvfs2.h`, and `pvfs2-mirror.h`. The mirror-management code must interpret the same xattr names and integer constants.

## Risks And Test Signals
Risks include mode value `0` being impossible to set because the code checks `> 0`, copy count documentation says positive but zero is accepted, direct binary integer encoding portability, and no final nonzero exit on failed `setxattr`. Test signals are setting mode, copies, both together, invalid numeric input, unsupported mode, missing file, and reading values back with `getmattr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/setmattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ucache.conf -->
# sources/distributed-fs/orangefs/src/apps/user/ucache.conf

## Purpose
Configuration template for OrangeFS user-cache sizing and statistics constants.

## Important APIs, Types, And Functions
Defines shell-style key/value assignments: `UcacheSizeMB`, `BlocksInCache`, `LockSize`, `UCACHE_STATS_64`, and `UCACHE_STATS_16`. There are no executable functions.

## Control Flow
Any consumer must parse these variables and translate them into generated constants or runtime settings. This file itself has no includes or conditionals.

## State And Persistence
It is persistent configuration data. Values describe cache memory size, block count, lock structure size, and stats field counts that should align with `ucache.h` structures.

## Dependencies And Integration Points
Intended to integrate with the ucache build or configuration generation path and the daemon/shared-memory layout used by `ucached.c`.

## Risks And Test Signals
Risks are stale values if structure sizes change, shell quoting assumptions, and no comments documenting units beyond names. Test signals are regenerating ucache headers/config from this file and validating that daemon shared-memory sizes match expected block and lock counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ucache.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/module.mk.in -->
# sources/distributed-fs/orangefs/src/apps/vis/module.mk.in

## Purpose
Build-system fragment for optional OrangeFS visualization tools.

## Important APIs, Types, And Functions
When `BUILD_VIS` is set, it adds `simple.c` and `pvfs2-vis-bw-2d.c` to `VISSRC`, adds `pvfs2-vis.c` to `VISMISCSRC`, and injects configured SDL compiler/linker flags plus `-lSDL_ttf`.

## Control Flow
The entire block is conditional on `BUILD_VIS`. This separates SDL-dependent tools from default builds.

## State And Persistence
No runtime state. Build-time state is CFLAGS/LDFLAGS and source-list membership.

## Dependencies And Integration Points
Depends on configure substitutions `@VISCFLAGS@` and `@VISLIBS@` and top-level make rules that build visualization binaries from `VISSRC` and shared misc sources.

## Risks And Test Signals
Risks include SDL/SDL_ttf detection drift, missing `pvfs2-vis.h` as a dependency if headers are tracked separately, and link-order issues because common source is in `VISMISCSRC`. Test signals are configure/build with visualization enabled/disabled and running linked tools against an OrangeFS mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis-bw-2d.c -->
# sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis-bw-2d.c

## Purpose
SDL/SDL_ttf graphical visualization that displays per-I/O-server OrangeFS read/write bandwidth bars and recent peaks.

## Important APIs, Types, And Functions
`options` stores mount point, window width, and update interval. `main` parses options, starts the shared visualization poller with `pvfs2_vis_start`, and calls `draw`. `draw` initializes SDL/TTF, opens `VeraBd.ttf`, allocates bar state and bandwidth matrices, waits on `pint_vis_cond`, computes MB/s from `pint_vis_shared` samples, and renders axes, labels, read/write bars, and peaks. `check_for_exit`, `parse_args`, and `usage` handle events and options.

## Control Flow
The UI blocks on a condition variable signaled by the background poller in `pvfs2-vis.c`. On each update it calculates bandwidth between adjacent samples or sample end time, adjusts global `max_bw`, redraws labels/borders/bars, and flips the SDL surface. Quit events, Escape, or `q` exit.

## State And Persistence
Runtime UI state includes SDL surfaces, font, allocated matrices, bar rectangles, and shared performance buffers protected by `pint_vis_mutex`. It writes no persistent data.

## Dependencies And Integration Points
Depends on SDL, SDL_ttf, pthreads, `pvfs2-vis.h`, and OrangeFS management performance samples. It is a frontend over `pvfs2_vis_start`.

## Risks And Test Signals
Risks include hard-coded font path, division by zero if timestamps do not advance, unbounded `max_bw` growth that never decays, memory leaks on repeated errors, and condition waits without a predicate loop. Test signals are successful window creation, updates for multiple server counts, quit handling, missing font behavior, and visual sanity with read/write traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis-bw-2d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.c -->
# sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.c

## Purpose
Provides the shared polling backend for visualization programs. It initializes OrangeFS management access, gathers I/O server performance samples, stores them in a global buffer, and signals consumers when new samples arrive.

## Important APIs, Types, And Functions
Exports `pvfs2_vis_start`, `pvfs2_vis_stop`, `pint_vis_shared`, `pint_vis_error`, `pint_vis_mutex`, and `pint_vis_cond`. Internal `poll_thread_args` carries filesystem ID, credentials, server addresses, temp matrices, next IDs, end times, server count, history count, and sleep interval. `poll_for_updates` is the background thread.

## Control Flow
Start initializes PVFS defaults, resolves a mount path, generates credentials, counts I/O servers, allocates temp sample matrices and shared matrices, repeatedly polls until the initial `HISTORY` samples are valid, copies initial data, then launches a thread. The thread polls `PVFS_mgmt_perf_mon_list`, shifts new valid samples into the shared ring, updates end times, signals the condition, unlocks, and sleeps.

## State And Persistence
All state is process memory: global shared buffer, synchronization objects, thread ID, allocated matrices, and PVFS system state. `pvfs2_vis_stop` cancels the thread and finalizes PVFS.

## Dependencies And Integration Points
Depends on pthreads, `pvfs2.h`, `pvfs2-mgmt.h`, and management perf monitor APIs. Used by `pvfs2-vis-bw-2d.c` and `simple.c`.

## Risks And Test Signals
Risks include memory leaks on partial allocation failures, no cleanup of `args`, cancellation without joining, condition signaling with questionable mutex handling on error, credential refresh absence in the polling loop, and API signature sensitivity across OrangeFS versions. Test signals are startup on valid/invalid mount, polling multiple servers, consumer wakeups, stop/finalize behavior, and induced management-call failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.h -->
# sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.h

## Purpose
Declares the visualization polling API and shared state used by OrangeFS visualization clients.

## Important APIs, Types, And Functions
Defines `struct pvfs2_vis_buffer` with I/O server count, history depth, performance matrix, and end-time array. Declares `pvfs2_vis_start(char *path, int update_interval)` and `pvfs2_vis_stop(void)`. Extern declarations expose `pint_vis_shared`, `pint_vis_error`, `pint_vis_mutex`, and `pint_vis_cond`.

## Control Flow
Consumers call `pvfs2_vis_start`, wait on `pint_vis_cond` while holding `pint_vis_mutex`, read `pint_vis_shared`, check `pint_vis_error`, and eventually call `pvfs2_vis_stop`.

## State And Persistence
The header itself stores no state but defines the process-global state contract exported by `pvfs2-vis.c`.

## Dependencies And Integration Points
Requires pthreads and `struct PVFS_mgmt_perf_stat`/`uint64_t` declarations from included OrangeFS headers in consumers. It is the common interface for SDL and simple text visualizers.

## Risks And Test Signals
Risks are exposing mutable globals directly, ABI drift in `PVFS_mgmt_perf_stat`, and consumers misusing the condition variable without a predicate. Test signals are compile coverage for all visualization clients and runtime wait/read cycles under concurrent updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/simple.c -->
# sources/distributed-fs/orangefs/src/apps/vis/simple.c

## Purpose
Minimal text-mode visualization smoke test. It starts the shared visualization poller and prints the latest read counter from server 0 for five updates.

## Important APIs, Types, And Functions
`options` stores only the mount point. `main` parses `-m`, calls `pvfs2_vis_start`, waits on `pint_vis_cond`, prints `pint_vis_shared.io_perf_matrix[0][depth-1].read`, checks `pint_vis_error`, then stops the poller. `parse_args` and `usage` handle the mount argument and version flag.

## Control Flow
After startup the program performs exactly five blocking waits. Each wake prints one sample and unlocks the mutex. It then calls `pvfs2_vis_stop` and exits.

## State And Persistence
No persistent state. Runtime state is the shared visualization globals managed by `pvfs2-vis.c` and the parsed mount string.

## Dependencies And Integration Points
Depends on pthreads, OrangeFS management headers, and the visualization backend. Useful as a non-SDL smoke consumer of `pvfs2_vis_start`.

## Risks And Test Signals
Risks include assuming at least one I/O server, waiting without a predicate loop, memory leak for parsed mount path, and returning without unlocking if `pint_vis_error` is seen. Test signals are five printed samples on an active mount, invalid mount failure, and error propagation from the polling thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.c -->
# sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.c

## Purpose
Implements a Windows-oriented exported C client library wrapping OrangeFS/PVFS system-interface operations for initialization, lookup, creation, removal, rename, attributes, directory listing, I/O, statfs, and credential management.

## Important APIs, Types, And Functions
Exports the functions declared in `orangefs-client.h`: `orangefs_initialize`, `orangefs_lookup`, `orangefs_lookup_follow_links`, `orangefs_get_symlink_attr`, `orangefs_create`, `orangefs_create_h`, `orangefs_remove`, `orangefs_remove_h`, `orangefs_rename`, `orangefs_getattr`, `orangefs_setattr`, `orangefs_mkdir`, `orangefs_io`, `orangefs_flush`, `orangefs_find_files`, `orangefs_get_diskfreespace`, `orangefs_finalize`, credential helpers, and debug helpers. `split_path` is a local path utility. Globals include `mntents`, `tab`, and `MVS_DEBUGGING`.

## Control Flow
Initialization derives a tabfile path relative to the executable, repeatedly initializes PVFS, parses the tab file, and adds the first filesystem until success. Most path operations split parent/name, resolve parents with link-following lookup, then call the matching `PVFS_sys_*` operation. I/O builds contiguous memory requests and calls `PVFS_sys_io`. Directory listing uses `PVFS_sys_readdirplus`, copies names and attributes, follows symlink targets, and releases allocated attr fields.

## State And Persistence
Runtime state includes PVFS system-interface initialization, parsed tabfile data, copied mount entry, debug output sinks, allocated credential group/signature/issuer fields, and output attribute buffers. It writes no local persistent files.

## Dependencies And Integration Points
Depends on Windows APIs for initialization/debug behavior, OrangeFS/PVFS sysint and utility APIs, `gossip`, `pint-util`, `cred.h`, and exported DLL decoration. It bridges external Windows callers to OrangeFS internal C APIs.

## Risks And Test Signals
Risks include unimplemented `orangefs_load_tabfile`, uninitialized `tabfile`/`malloc_flag` paths, incorrect pointer casts such as `(PVFS_fs_id) fs_id` instead of `*fs_id` in handle variants, `orangefs_rename` using uninitialized parent lookup responses, possible attr lifetime bugs after copying and releasing fields, `vsprintf` into fixed buffer, and retry loop without cancellation. Test signals are DLL build, initialization from a tabfile, create/remove/rename/mkdir/io/list/statfs, symlink following, credential group management, debug modes, and negative path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.h -->
# sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.h

## Purpose
Public ABI header for the OrangeFS client DLL/library. It defines fixed-width types, permission/debug constants, object/credential/mount/attribute structures, and exported function prototypes.

## Important APIs, Types, And Functions
Key types include `OrangeFS_fsid`, `OrangeFS_handle`, `OrangeFS_credential`, `OrangeFS_object_ref`, `OrangeFS_mntent`, `OrangeFS_attr`, `OrangeFS_sysresp_lookup`, and enums for I/O type, object type, flow protocol, and encoding. It defines gossip debug masks, debug output type masks, permission bits, pointer-alignment macros for 32-bit/64-bit ABI matching, and all `DLL_CODE` client functions.

## Control Flow
No executable control flow. Consumers include this header, initialize credentials and a filesystem, perform file operations, and finalize. `CREATING_DLL` controls whether declarations are exported or imported on Windows.

## State And Persistence
The header declares data shapes that carry persistent filesystem metadata such as owner, group, permissions, timestamps, link target, distribution parameters, directory entry count, and flags. It stores no runtime state.

## Dependencies And Integration Points
Depends on C99 fixed-width types and Windows `__declspec` semantics. The structures must remain layout-compatible with PVFS internal equivalents and external callers compiled against the DLL.

## Risks And Test Signals
Risks include ABI fragility from pointer fields and manual padding, Windows-only `DLL_CODE` definitions when compiled on non-Windows platforms, constants drifting from PVFS enums/masks, and callers misunderstanding ownership of pointer fields in `OrangeFS_attr`. Test signals are 32-bit and 64-bit ABI size checks, C/C++ compile coverage, DLL import/export tests, and round-trip operations through every prototype.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/build-and-install.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/build-and-install.sh

## Purpose
Builds the Hadoop 1 OrangeFS filesystem adapter with Maven and installs the resulting jar into the OrangeFS prefix.

## Important APIs, Types, And Functions
The script uses `mvn` with Java source/target 1.6, skips tests, runs `clean package`, and copies `target/orangefs-hadoop1-?.?.?.jar` to `${ORANGEFS_PREFIX}/lib/` with `sudo`.

## Control Flow
It enables shell tracing, changes to its own directory, then chains build and copy with `&&` so install runs only after a successful Maven package.

## State And Persistence
Creates Maven build artifacts under `target/` and installs a jar into the OrangeFS library directory.

## Dependencies And Integration Points
Depends on Maven, JDK compatible with source/target 1.6, sudo privileges, `ORANGEFS_PREFIX`, and `pom.xml` generated from `pom.xml.in`.

## Risks And Test Signals
Risks include unquoted `cd $(dirname $0)`, glob mismatch if version has more digits or multiple jars exist, skipped tests, and sudo prompting in automation. Test signals are successful Maven package, exactly one jar copied, and Hadoop classpath loading the installed adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/build-and-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/pom.xml.in -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/pom.xml.in

## Purpose
Maven POM template for the Hadoop 1 OrangeFS filesystem plugin jar.

## Important APIs, Types, And Functions
Defines group `org.apache.hadoop.fs.ofs`, artifact `orangefs-hadoop1`, jar packaging, version substituted from OrangeFS version macros, and dependencies on `hadoop-core` 1.2.1, `orangefs-jni` with matching OrangeFS version, and test-scope JUnit 4.12.

## Control Flow
No runtime control flow. Configure substitutes version placeholders before Maven builds the project.

## State And Persistence
Build metadata persists in the generated POM and Maven artifacts. It declares the dependency graph required to compile/package the adapter.

## Dependencies And Integration Points
Integrates OrangeFS JNI bindings with the Hadoop 1 `FileSystem` API. Depends on Maven repositories containing Hadoop core, OrangeFS JNI, log4j through Hadoop, and JUnit.

## Risks And Test Signals
Risks include old Hadoop 1 dependency, source compatibility constraints, version substitution drift between adapter and JNI jar, and no explicit compiler plugin beyond command-line flags in the build script. Test signals are `mvn package`, dependency resolution, unit test execution if enabled, and loading `org.apache.hadoop.fs.ofs.OrangeFileSystem` in Hadoop 1.2.1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/pom.xml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/relaunch.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/relaunch.sh

## Purpose
Convenience orchestration script to stop OrangeFS and Hadoop, clean Hadoop local state, reset OrangeFS storage/config, and restart Hadoop for examples.

## Important APIs, Types, And Functions
Runs `stop_orangefs.sh`, `stop_hadoop.sh`, `cleanup_hadoop.sh`, `reset_orangefs.sh`, and `start_hadoop.sh` from the example script directories.

## Control Flow
With tracing enabled, it changes to the adapter directory and executes each child script sequentially. A TODO notes that failures are not currently enforced.

## State And Persistence
Mutates service state, Hadoop local directories, and OrangeFS storage through child scripts.

## Dependencies And Integration Points
Depends on the example Hadoop/OrangeFS scripts and their `setenv` files/environment variables. It coordinates the demo stack, not production service management.

## Risks And Test Signals
Risks include continuing after failed stop/cleanup/reset, unquoted script directory handling, and destructive cleanup of configured storage. Test signals are a full relaunch on an isolated test cluster, verifying each stage succeeded and Hadoop can run an OrangeFS-backed job afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/relaunch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_clean.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_clean.sh

## Purpose
Runs Hadoop 1 `TestDFSIO -clean` to remove benchmark data/results from the configured Hadoop filesystem, expected to be OrangeFS-backed in these examples.

## Important APIs, Types, And Functions
Invokes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} jar ${HADOOP_PREFIX}/hadoop-test-1.?.?.jar TestDFSIO -clean`.

## Control Flow
The script traces commands, changes to its own directory, and executes one Hadoop command. It relies on Hadoop returning an exit status.

## State And Persistence
Deletes TestDFSIO benchmark artifacts in the Hadoop filesystem namespace.

## Dependencies And Integration Points
Depends on `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, the Hadoop test jar glob, and the Hadoop filesystem configuration selecting OrangeFS where desired.

## Risks And Test Signals
Risks include unquoted variables, jar glob ambiguity, no explicit `set -e`, and comments mentioning file size even though clean does not use it. Test signals are successful cleanup after read/write runs and absence of TestDFSIO output paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_clean.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_read.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_read.sh

## Purpose
Runs Hadoop 1 `TestDFSIO -read` with two 64 MB files against the configured filesystem to benchmark read throughput.

## Important APIs, Types, And Functions
Invokes the Hadoop command with `TestDFSIO -read -nrFiles 2 -fileSize 64`. Comments document optional `-Dfs.ofs.file.buffer.size` override for the OrangeFS adapter.

## Control Flow
Traces commands, changes to its directory, and launches one Hadoop job.

## State And Persistence
Reads benchmark files and writes Hadoop/TestDFSIO result output in the configured filesystem/job output locations.

## Dependencies And Integration Points
Depends on `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, the Hadoop test jar, existing TestDFSIO write data, and `OrangeFileSystem` honoring `fs.ofs.file.buffer.size`.

## Risks And Test Signals
Risks include fixed small workload, unquoted variables, ambiguous jar glob, and no cleanup/error enforcement. Test signals are successful job completion, expected read throughput counters, and buffer-size override changing adapter logs/behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_read.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_write.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_write.sh

## Purpose
Runs Hadoop 1 `TestDFSIO -write` with two 64 MB files to benchmark OrangeFS-backed write throughput.

## Important APIs, Types, And Functions
Invokes `TestDFSIO -write -nrFiles 2 -fileSize 64`. Comments document adapter properties `fs.ofs.file.layout=PVFS_SYS_LAYOUT_RANDOM` and `fs.ofs.file.buffer.size`.

## Control Flow
Traces commands, changes to the script directory, and runs a single Hadoop job.

## State And Persistence
Creates TestDFSIO benchmark files and result output in the configured Hadoop filesystem.

## Dependencies And Integration Points
Depends on Hadoop 1 test jar, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and the OrangeFS Hadoop adapter mapping create calls to layout/buffer settings.

## Risks And Test Signals
Risks include unquoted env vars, jar glob ambiguity, fixed benchmark scale, no `set -e`, and stale data if clean is not run. Test signals are successful file creation in OrangeFS, adapter layout setting observed in logs, and clean/read scripts working afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/cleanup_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/cleanup_hadoop.sh

## Purpose
Removes Hadoop temporary/local directories from each configured slave node for the example Hadoop cluster.

## Important APIs, Types, And Functions
Sources `setenv`, iterates over `$(cat $HADOOP_CONF_DIR/slaves)`, and runs `ssh $slave "rm -rf /tmp/hadoop-$USER $HADOOP_LOCAL_DIR"`.

## Control Flow
After tracing and directory change, it loads environment settings, then performs remote cleanup sequentially for each slave host.

## State And Persistence
Destructively removes `/tmp/hadoop-$USER` and `$HADOOP_LOCAL_DIR` on every listed slave.

## Dependencies And Integration Points
Depends on passwordless SSH, `HADOOP_CONF_DIR/slaves`, `HADOOP_LOCAL_DIR`, and a local `setenv` file. Used by reset/relaunch scripts.

## Risks And Test Signals
Risks include unquoted variables in a destructive `rm -rf`, missing/incorrect `setenv`, no handling for SSH failures, and legacy Hadoop slave file naming. Test signals are cleanup on all hosts, proper failure when a slave is unreachable, and Hadoop starting with fresh local dirs afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/cleanup_hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/hadoop_prog.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/hadoop_prog.sh

## Purpose
Small wrapper that runs arbitrary Hadoop commands using the example `setenv` configuration.

## Important APIs, Types, And Functions
Sources `setenv` and executes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} $@`.

## Control Flow
Traces commands, changes to its own directory, loads environment, then forwards all script arguments to Hadoop.

## State And Persistence
State effects depend entirely on the forwarded Hadoop command.

## Dependencies And Integration Points
Depends on `setenv`, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and Hadoop 1 command-line semantics. It is an operator convenience wrapper for the example stack.

## Risks And Test Signals
Risks include unquoted `$@` causing argument splitting changes, no `set -e`, and unquoted paths. Test signals are forwarding commands with multiple arguments/properties and verifying the intended Hadoop config directory is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/hadoop_prog.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/reset_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/reset_hadoop.sh

## Purpose
Restarts the example Hadoop job/tasktracker environment from a clean local state.

## Important APIs, Types, And Functions
Runs `stop_hadoop.sh`, sleeps three seconds, runs `cleanup_hadoop.sh`, then `start_hadoop.sh`.

## Control Flow
Sequential shell orchestration with tracing and a fixed delay between stop and cleanup.

## State And Persistence
Stops Hadoop services, deletes local Hadoop state via the cleanup script, and starts services again.

## Dependencies And Integration Points
Depends on sibling scripts, their environment variables, and Hadoop 1 mapred start/stop commands.

## Risks And Test Signals
Risks include continuing after failed stop or cleanup, fixed sleep instead of service-state polling, and destructive cleanup. Test signals are services stopped before deletion, local dirs recreated, and job submission success after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/reset_hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/start_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/start_hadoop.sh

## Purpose
Starts the Hadoop 1 MapReduce daemons for the example environment.

## Important APIs, Types, And Functions
Runs `$HADOOP_PREFIX/bin/start-mapred.sh` and prints the jobtracker URL `http://localhost:50030`.

## Control Flow
Traces commands, changes to the script directory, and invokes the Hadoop start script.

## State And Persistence
Starts Hadoop daemon processes and causes Hadoop runtime/log directories to be created by Hadoop itself.

## Dependencies And Integration Points
Depends on `HADOOP_PREFIX`, `HADOOP_CONF_DIR` being meaningful to the Hadoop scripts, and Hadoop 1 mapred tooling.

## Risks And Test Signals
Risks include comments saying environment variables are required but not sourcing `setenv`, unquoted variables, and assuming the UI is local. Test signals are running daemons, reachable jobtracker UI, and successful example job submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/start_hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/stop_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/stop_hadoop.sh

## Purpose
Stops Hadoop 1 MapReduce daemons for the example environment.

## Important APIs, Types, And Functions
Runs `$HADOOP_PREFIX/bin/stop-mapred.sh` after changing to the script directory.

## Control Flow
Single traced command invocation; no explicit environment sourcing.

## State And Persistence
Stops Hadoop daemon processes. It does not remove runtime directories.

## Dependencies And Integration Points
Depends on `HADOOP_PREFIX`, Hadoop 1 scripts, and the configured cluster environment.

## Risks And Test Signals
Risks include missing `HADOOP_PREFIX`, unquoted path, no verification daemons stopped, and no `set -e`. Test signals are jobtracker/tasktracker processes gone and reset scripts able to clean local state after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/stop_hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teragen.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teragen.sh

## Purpose
Runs Hadoop example `teragen` to create 10,000,000 TeraSort records in `teragen_data`.

## Important APIs, Types, And Functions
Invokes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} jar ${HADOOP_PREFIX}/hadoop-examples-1.?.?.jar teragen 10000000 teragen_data`. Comments describe optional map task tuning.

## Control Flow
Traced script with one Hadoop job command.

## State And Persistence
Creates `teragen_data` in the configured Hadoop filesystem, which may map to OrangeFS through the adapter.

## Dependencies And Integration Points
Depends on Hadoop examples jar, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and functional OrangeFS filesystem configuration.

## Risks And Test Signals
Risks include fixed output path, jar glob ambiguity, unquoted vars, and stale output causing job failure. Test signals are successful data generation, expected file count/size, and subsequent `terasort.sh` consuming the output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teragen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/terasort.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/terasort.sh

## Purpose
Runs Hadoop example `terasort` from `teragen_data` to `terasort_data`.

## Important APIs, Types, And Functions
Executes the Hadoop examples jar with `terasort teragen_data terasort_data`. Comments mention optional `-D mapred.reduce.tasks`.

## Control Flow
One traced Hadoop command after changing to the script directory.

## State And Persistence
Reads `teragen_data` and creates sorted output at `terasort_data`.

## Dependencies And Integration Points
Depends on prior `teragen.sh`, Hadoop examples jar, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and OrangeFS adapter read/write behavior.

## Risks And Test Signals
Risks include fixed paths, stale output, unquoted variables, no tuning defaults, and no cleanup. Test signals are successful sort completion and `teravalidate.sh` passing against `terasort_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/terasort.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teravalidate.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teravalidate.sh

## Purpose
Runs Hadoop example `teravalidate` to verify the sorted output generated by `terasort.sh`.

## Important APIs, Types, And Functions
Invokes the Hadoop examples jar with `teravalidate terasort_data teravalidate_data`.

## Control Flow
Single traced Hadoop command after changing directories.

## State And Persistence
Reads `terasort_data` and creates validation output at `teravalidate_data`.

## Dependencies And Integration Points
Depends on Hadoop examples jar, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and existing sorted data. It validates OrangeFS-backed Hadoop output correctness indirectly.

## Risks And Test Signals
Risks include stale/missing input or output paths, unquoted variables, and no explicit failure handling. Test signals are successful validation job, empty/no-error validation output, and failure when sorted input is intentionally corrupted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teravalidate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/wordcount.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/wordcount.sh

## Purpose
Runs the Hadoop 1 example `wordcount` with caller-supplied input/output arguments using the example configuration.

## Important APIs, Types, And Functions
Sources `setenv` and executes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} jar ${HADOOP_PREFIX}/hadoop-examples-1.?.?.jar wordcount $@`.

## Control Flow
Traces commands, changes directory, loads environment, and forwards arguments to the Hadoop example.

## State And Persistence
Reads and writes paths determined by caller arguments in the configured Hadoop filesystem.

## Dependencies And Integration Points
Depends on Hadoop examples jar, `setenv`, and the OrangeFS Hadoop adapter for filesystem operations.

## Risks And Test Signals
Risks include unquoted `$@`, jar glob ambiguity, no check for required input/output args, and no cleanup of output path. Test signals are a successful wordcount over an OrangeFS input file and expected output counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/wordcount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/cleanup_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/cleanup_orangefs.sh

## Purpose
Deletes all files under the example OrangeFS storage directory.

## Important APIs, Types, And Functions
Changes to the script directory, sources `setenv`, and runs `rm -rf ${ORANGEFS_STORAGE_DIR}/*`.

## Control Flow
Straight-line cleanup with no tracing or error checks.

## State And Persistence
Destructively removes OrangeFS server storage contents for the example deployment.

## Dependencies And Integration Points
Depends on sibling `setenv` defining `ORANGEFS_STORAGE_DIR`. Used by reset/relaunch scripts before reinitializing storage.

## Risks And Test Signals
Risks include unquoted destructive path expansion, empty or wrong `ORANGEFS_STORAGE_DIR`, glob behavior with hidden files, and no service-state check before deletion. Test signals are running only after server stop, verifying storage is empty, and ensuring reset can reinitialize successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/cleanup_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/init_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/init_orangefs.sh

## Purpose
Formats/initializes the example OrangeFS server storage using a configured server config file.

## Important APIs, Types, And Functions
Sources `setenv` and runs `${ORANGEFS_PREFIX}/sbin/pvfs2-server -a localhost ${ORANGEFS_CONF_FILE} -f`.

## Control Flow
Changes directory, loads environment, and invokes `pvfs2-server` with force/create format mode.

## State And Persistence
Creates or reinitializes OrangeFS storage metadata/data according to the config file.

## Dependencies And Integration Points
Depends on `ORANGEFS_PREFIX`, `ORANGEFS_CONF_FILE`, and the example config/storage layout. Called by reset scripts before server startup.

## Risks And Test Signals
Risks include destructive `-f` use, unquoted variables, no validation of config path, and assuming localhost-only server address. Test signals are successful format, created storage files, and `start_orangefs.sh`/`pvfs2-ping` succeeding afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/init_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/reset_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/reset_orangefs.sh

## Purpose
Performs a full reset of the example OrangeFS service and storage.

## Important APIs, Types, And Functions
Runs `stop_orangefs.sh`, sleeps, runs `cleanup_orangefs.sh`, sleeps, runs `init_orangefs.sh`, sleeps, then runs `start_orangefs.sh`.

## Control Flow
Sequential orchestration with fixed one-second sleeps and no explicit failure checks.

## State And Persistence
Stops the server, deletes storage contents, reformats storage, and restarts the server.

## Dependencies And Integration Points
Depends on sibling OrangeFS example scripts and their `setenv` variables. Used by Hadoop relaunch testing.

## Risks And Test Signals
Risks include continuing after failed stop/init, destructive cleanup, fixed sleeps instead of readiness checks, and unquoted script directory handling. Test signals are clean reset on isolated storage and successful `pvfs2-ping` after start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/reset_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/start_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/start_orangefs.sh

## Purpose
Starts the example OrangeFS server and verifies it with `pvfs2-ping`.

## Important APIs, Types, And Functions
Sources `setenv`, copies `$PVFS2TAB_FILE` to `/tmp/orangefs_hadoop_storage/pvfs2tab`, runs `${ORANGEFS_PREFIX}/sbin/pvfs2-server -a localhost ${ORANGEFS_CONF_FILE}`, sleeps three seconds, then runs `${ORANGEFS_PREFIX}/bin/pvfs2-ping -m /mnt/orangefs`.

## Control Flow
Performs tabfile copy, daemon start, fixed wait, and ping verification in order.

## State And Persistence
Starts a server process and writes a tabfile into the example storage directory.

## Dependencies And Integration Points
Depends on `ORANGEFS_PREFIX`, `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, hard-coded storage and mount paths, and initialized storage. It prepares the filesystem for Hadoop examples.

## Risks And Test Signals
Risks include hard-coded `/tmp/orangefs_hadoop_storage` and `/mnt/orangefs`, unquoted variables, fixed sleep, no failure stop on bad ping, and stale server process conflicts. Test signals are successful server process startup, ping success, and Hadoop adapter access through the configured mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/start_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/stop_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/stop_orangefs.sh

## Purpose
Stops all `pvfs2-server` processes for the example environment.

## Important APIs, Types, And Functions
Runs `killall pvfs2-server`.

## Control Flow
Single command with no directory setup, environment sourcing, or status checks.

## State And Persistence
Terminates matching server processes on the host. Storage files remain untouched.

## Dependencies And Integration Points
Depends on `killall` and process names matching `pvfs2-server`. Used by reset/relaunch scripts.

## Risks And Test Signals
Risks include killing unrelated OrangeFS servers on the same host, no graceful per-config targeting, no wait for shutdown, and no error handling when no process exists. Test signals are server process disappearance, subsequent storage cleanup safety, and no impact on unrelated services in isolated tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/stop_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java

## Purpose
Implements a Hadoop 1 `FileSystem` adapter for OrangeFS. It maps `ofs://authority/path` Hadoop operations to OrangeFS JNI POSIX/stdio operations under a configured local OrangeFS mount.

## Important APIs, Types, And Functions
The class extends `FileSystem` and overrides `initialize`, `getUri`, `getWorkingDirectory`, `setWorkingDirectory`, `makeAbsolute`, `open`, `create`, `append`, `delete`, `exists`, `getFileStatus`, `listStatus`, `mkdirs`, `rename`, `setPermission`, local-copy helpers, and local-output helpers. State includes singleton `Orange`, POSIX/stdio flags, configured buffer/block size, file layout, URI, selected mount path, working directory, local filesystem, Hadoop statistics, and initialization guard.

## Control Flow
`initialize` validates URI/config, reads `fs.ofs.systems` and `fs.ofs.mntLocations`, matches URI authority to a mount, configures buffer/block/layout defaults, initializes local FS and working directory, then calls `super.initialize`. Path operations call `getOFSPathName`, which prepends `ofsMount` to the absolute Hadoop path. `create` handles overwrite and parent creation before constructing `OrangeFileSystemOutputStream` and setting permissions. `delete` chooses recursive stdio directory deletion or POSIX unlink. `listStatus` stats the path, returns a singleton for files, or enumerates directory entries and stats each child.

## State And Persistence
Persists filesystem changes through JNI: file creation, appends, deletes, mkdirs, chmod, rename, and directory listings. Hadoop operation statistics are incremented for read/write calls. Working directory is in-memory per instance.

## Dependencies And Integration Points
Depends on Hadoop 1 APIs, `org.orangefs.usrint` JNI classes (`Orange`, `Stat`, stream wrappers, layout enum), and configuration keys `fs.ofs.systems`, `fs.ofs.mntLocations`, `fs.ofs.file.buffer.size`, `fs.ofs.block.size`, and `fs.ofs.file.layout`.

## Risks And Test Signals
Risks include Hadoop 1 deprecated API behavior, returning `null` from `listStatus` on errors, `delete(Path)` deprecated overload always returning false, block replication hard-coded to zero, sticky bit stripped in permissions, parent path handling based on string split, no atomic rename fallback, and reliance on local mount paths matching URI authorities. Test signals are Hadoop contract tests for create/open/append/delete/list/mkdir/rename/permissions, multiple authority mappings, relative working-directory paths, local copy helpers, buffer/layout property overrides, and JNI error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java -->
