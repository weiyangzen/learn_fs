# Group Research: group_1801_util_linux_sources_block_storage_util_linux_sys_utils_flock_c_sourc_e97fcd4c4c01

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/block-storage/util-linux`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/flock.c -->
# File Research: sources/block-storage/util-linux/sys-utils/flock.c

Purpose: Implements the `flock(1)` command-line utility for shell-level file locking. It supports locking a named file/directory while running a command, or operating directly on an already-open file descriptor.

Core behavior:
- Parses shared/exclusive/unlock modes, nonblocking and timed waits, command execution (`-c` via the default shell or argv passthrough), `--close`, `--no-fork`, verbose timing, and custom conflict exit status.
- Uses `flock(2)` by default and can switch to Linux open-file-description locks via `fcntl(F_OFD_SETLK/F_OFD_SETLKW)` for byte ranges selected by `--start` and `--length`.
- Opens path locks with `O_CREAT|O_NOCTTY`, falls back for directories when Linux rejects `O_CREAT` on directories, and opens OFD exclusive locks writable because fcntl write locks require that.
- Implements timeouts through util-linux timer helpers and treats `-w 0` as equivalent to nonblocking mode.
- On NFS-style `flock()` failures (`EIO`/`EBADF`) it attempts a reopen in read-write mode when an exclusive lock on an accessible named file might need fcntl-compatible semantics.

Important implementation details:
- `do_lock()` dispatches between the `flock()` and OFD `fcntl()` APIs, while `flock_to_fcntl_type()` maps lock modes to `F_RDLCK`, `F_WRLCK`, and `F_UNLCK`.
- The parent process keeps the lock while waiting for a forked child; `--close` closes the lock fd only in the child before `execvp()`. `--no-fork` directly replaces the `flock` process and is incompatible with `--close`.
- Exit status mirrors command status where a command is executed, maps signal termination to `128 + signal`, and uses sysexits values for setup errors.

Dependencies and integration:
- Relies on util-linux helpers from `strutils.h`, `timer.h`, `monotonic.h`, `default_shell.h`, `closestream.h`, and NLS wrappers.
- Exposes user-facing behavior documented as `flock(1)`.

Risks and edge cases:
- OFD lock constants are locally defined when libc/kernel headers lack them, so build/runtime kernel support can diverge.
- The lock loop only treats `EACCES`/`EWOULDBLOCK` as normal conflict errors; other errors become data or OS errors.
- Verbose elapsed timing is monotonic and only measures lock acquisition, not child execution.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/flock.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fsfreeze.c -->
# File Research: sources/block-storage/util-linux/sys-utils/fsfreeze.c

Purpose: Implements `fsfreeze(8)`, a small Linux utility that freezes or thaws a mounted filesystem through VFS ioctls.

Core behavior:
- Accepts exactly one action, `--freeze` or `--unfreeze`, enforced as mutually exclusive.
- Requires a single mountpoint argument, opens it read-only, verifies it is a directory, and then issues `ioctl(fd, FIFREEZE, 0)` or `ioctl(fd, FITHAW, 0)`.
- Reports open/stat/ioctl failures with util-linux translated diagnostics and exits success only after the selected ioctl succeeds.

Dependencies and integration:
- Uses Linux `FIFREEZE`/`FITHAW` definitions from `<linux/fs.h>`.
- Uses util-linux common CLI helpers (`optutils.h`, `closestream.h`, `nls.h`) and is documented as `fsfreeze(8)`.

Risks and edge cases:
- It validates that the path is a directory, not that it is the root of a mount; the kernel ioctl decides whether the target is a valid freeze point.
- The file includes `blkdev.h` but does not use block-device helpers directly.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fsfreeze.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fstrim.c -->
# File Research: sources/block-storage/util-linux/sys-utils/fstrim.c

Purpose: Implements `fstrim(8)`, which discards unused blocks from mounted filesystems through the Linux `FITRIM` ioctl.

Core behavior:
- Supports trimming one mountpoint or multiple filesystems selected by `--all`, `--fstab`, or `--listed-in`.
- Maintains an `fstrim_control` with the `fstrim_range` (`start`, `len`, `minlen`) plus type filtering, verbose output, dry-run mode, and quiet unsupported behavior.
- For a single path, verifies it is a directory, resolves it with `realpath()`, opens it read-only, and sends `FITRIM`; unsupported errors (`EBADF`, `ENOTTY`, `EOPNOTSUPP`, `ENOSYS`) are distinguished from hard failures.
- For batch trimming, parses mount/fstab files with libmount, removes duplicate mount targets, filters pseudo/network/swap/autofs/read-only/notrim filesystems, canonicalizes sources, checks mounted accessibility, optionally resolves bind mounts with statmount support, verifies discard support in sysfs, deduplicates by source, then trims.
- Return codes for batch mode follow mount-style codes: success, all failed, or partial success.

Important implementation details:
- `has_discard()` resolves block devices to whole-disk sysfs contexts and checks `queue/discard_granularity` plus read-only state, reusing a whole-disk `path_cxt` for partitions.
- `is_unwanted_fs()` combines libmount classification, fstype filters, mount options, `statfs()` autofs detection, and write-access checks.
- `/etc/fstab` mode can synthesize a `/` entry from `mnt_guess_system_root()` if root is absent, so root filesystems can still be trimmed.
- `--quiet-unsupported` suppresses unsupported trim warnings, and for single-filesystem mode converts unsupported into success only when requested.

Dependencies and integration:
- Uses Linux `FITRIM`, libmount tables/iterators/cache, util-linux sysfs/path/mount helpers, size parsing/formatting, and `statfs_magic.h`.
- The systemd service in this group invokes `fstrim --listed-in /etc/fstab:/proc/self/mountinfo --verbose --quiet-unsupported`.

Risks and edge cases:
- `has_discard()` returns true on sysfs lookup failure, so the utility may still attempt FITRIM when it cannot prove discard support.
- Batch delta between mount table parsing and actual trimming can race with mounts/unmounts.
- Source deduplication intentionally avoids pseudo/net filesystems but can still skip repeated block-device sources after canonicalization.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fstrim.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fstrim.service.in -->
# File Research: sources/block-storage/util-linux/sys-utils/fstrim.service.in

Purpose: systemd unit template for running periodic discard through `fstrim`.

Core behavior:
- Defines a oneshot service with `ExecStart=@sbindir@/fstrim --listed-in /etc/fstab:/proc/self/mountinfo --verbose --quiet-unsupported`.
- Runs only outside containers via `ConditionVirtualization=!container`.
- Applies service hardening while permitting device access needed for filesystem discard: `PrivateDevices=no`, `PrivateNetwork=yes`, `PrivateUsers=no`, kernel/control-group protections, `MemoryDenyWriteExecute=yes`, and a constrained `SystemCallFilter`.

Dependencies and integration:
- `@sbindir@` is substituted by the build/install system.
- Paired with `fstrim.timer` for weekly scheduling.

Risks and edge cases:
- The service intentionally leaves `PrivateDevices` disabled because FITRIM/mount-device probing needs real device visibility.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fstrim.service.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fstrim.timer -->
# File Research: sources/block-storage/util-linux/sys-utils/fstrim.timer

Purpose: systemd timer that schedules the `fstrim` service.

Core behavior:
- Runs weekly with `AccuracySec=1h`, `Persistent=true`, and `RandomizedDelaySec=100min`.
- Avoids containers and initrd environments with `ConditionVirtualization=!container` and `ConditionPathExists=!/etc/initrd-release`.
- Installs under `timers.target`.

Dependencies and integration:
- Activates the service unit of the same base name, expected to be `fstrim.service`.

Risks and edge cases:
- Randomization and one-hour accuracy intentionally make execution time approximate rather than exact.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fstrim.timer -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock-cmos.c -->
# File Research: sources/block-storage/util-linux/sys-utils/hwclock-cmos.c

Purpose: Provides the direct ISA/CMOS hardware-clock backend for `hwclock`, used when direct port access is selected and `USE_HWCLOCK_CMOS` is enabled.

Core behavior:
- Reads and writes classic RTC CMOS registers through `outb()`/`inb()` at ports `0x70` and `0x71`.
- Converts RTC fields between BCD/binary and 12/24-hour formats according to status register B.
- Reads time only when the update-in-progress bit in status register A is clear, then rechecks seconds to reduce the chance of reading a mixed update.
- Sets the clock by setting the SET bit, stopping/resetting the prescaler, writing time fields, then restoring control and frequency registers in the required order.
- Synchronizes to a clock tick by polling the update-in-progress bit for a rise and fall with bounded spin loops.

Important implementation details:
- Years are interpreted without using a century byte: values 69-99 map to 1969-1999 and 00-68 map to 2000-2068.
- `get_permissions_cmos()` requests I/O privilege through `iopl(3)` when available, otherwise uses `ioperm()` over the two CMOS ports.
- The backend exports a `clock_ops` instance with no device path and the label "Using direct ISA access to the clock".

Dependencies and integration:
- Implements `probe_for_cmos_clock()` declared in `hwclock.h`.
- Used by `hwclock.c` only when direct ISA support is compiled and `--directisa` is requested.

Risks and edge cases:
- The `atomic()` wrapper is only a direct call and does not provide real interrupt exclusion; comments acknowledge only the kernel can make CMOS access truly atomic.
- Direct port access requires privileges and platform support; failure is reported as an access-method failure.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock-cmos.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock-parse-date.y -->
# File Research: sources/block-storage/util-linux/sys-utils/hwclock-parse-date.y

Purpose: Provides the GPLv3 gnulib-derived date parser used by `hwclock --date` and `--predict` when `USE_HWCLOCK_GPLv3_DATETIME` is enabled.

Core behavior:
- Defines a reentrant Bison grammar for absolute times, ISO-8601 dates/times, numeric epochs using `@seconds`, month/day names, weekdays, timezone names and offsets, local time zone abbreviations, relative units, "ago"/"hence", and hybrid numeric date plus relative-offset input.
- Accumulates parse state in `parser_control`, including absolute date/time fields, relative year/month/day/hour/minute/second/nanosecond offsets, timezone selection, meridian style, and counters used to reject conflicting date/time constructs.
- Lexes signed/unsigned integers and decimal seconds with overflow checks and nanosecond truncation toward negative infinity for negative fractional values.
- Builds local timezone abbreviation tables from `tm_zone` or `tzname`, probing future quarters to detect alternate DST names where possible.
- Temporarily honors leading `TZ="..."` strings by mutating the process `TZ` environment for parsing and restoring the prior setting before returning.
- Converts parsed values through `mktime()`, applies weekday and relative date shifts, adjusts explicit time zones, then applies relative smaller units with overflow checks.

Important implementation details:
- The grammar explicitly expects 31 shift/reduce conflicts inherited from gnulib.
- `time_zone_hhmm()` accepts `HHMM`, `HH:MM`, and short hour forms with range checks against POSIX/ISO-style offset bounds.
- `to_year()` maps two-digit years 00-68 to 2000-2068 and 69-99 to 1969-1999.
- `mktime_ok()` guards against normalized invalid calendar fields and avoids false failure for valid timestamps equal to `(time_t)-1`.

Dependencies and integration:
- Includes util-linux `timeutils.h`, `cctype.h`, `nls.h`, and `hwclock.h`.
- `hwclock.c` calls `parse_date()` for `--date`/`--predict` under the GPLv3 parser build option.

Risks and edge cases:
- File comments note incomplete arithmetic overflow coverage and assumptions inherited from old gnulib code.
- `parse_date()` manipulates global timezone state, so the parser is reentrant at the Bison state level but not fully thread-isolated around TZ/localtime behavior.
- Timezone abbreviations remain inherently ambiguous; numeric offsets are more deterministic.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock-parse-date.y -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock-rtc.c -->
# File Research: sources/block-storage/util-linux/sys-utils/hwclock-rtc.c

Purpose: Provides the `/dev/rtc` hardware-clock backend for `hwclock`, including Linux RTC ioctls, GNU/Hurd RTC support, Linux RTC parameters, and voltage-low status operations.

Core behavior:
- Opens an explicitly requested `--rtc` path or probes common RTC paths (`/dev/rtc`, `/dev/rtc0`, `/dev/misc/rtc`, plus ia64 EFI variants).
- Reads and sets RTC time using `RTC_RD_TIME` and `RTC_SET_TIME`, copying between kernel `struct rtc_time` and userspace `struct tm`.
- Synchronizes to the next RTC tick by enabling `RTC_UIE_ON` and waiting with `select()`; falls back to busy-waiting on repeated reads when update interrupts are unsupported.
- Exposes `probe_for_rtc_clock()` as a `clock_ops` backend when an RTC device can be opened.
- On Alpha builds, supports reading and setting the RTC epoch using `RTC_EPOCH_READ` and `RTC_EPOCH_SET`.
- On Linux non-GNU builds, supports `RTC_PARAM_GET/SET` for named or numeric RTC parameters and voltage-low read/clear via `RTC_VL_READ` and `RTC_VL_CLR`.

Important implementation details:
- Device fd is cached globally and closed with `atexit()`.
- Linux opens RTC devices read-only except on GNU/Hurd, where read-write is used.
- `set_param_rtc()` reads the current parameter and skips the set ioctl if the value is unchanged.
- Voltage-low reporting decodes known bits and prints any remaining unknown bitmask.

Dependencies and integration:
- Implements declarations from `hwclock.h`: RTC probe, optional epoch helpers, parameter helpers, and voltage-low helpers.
- Used by `hwclock.c` as the preferred access method on Linux/GNU when direct ISA is not selected.

Risks and edge cases:
- Some diagnostic strings mention `RTC_RD_NAME`/`RTC_VL_CLEAR` while calling `RTC_RD_TIME`/`RTC_VL_CLR`; this is cosmetic but can confuse troubleshooting.
- Busy-wait tick synchronization has a 1.5 second timeout and depends on RTC reads changing seconds promptly.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock-rtc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock.c -->
# File Research: sources/block-storage/util-linux/sys-utils/hwclock.c

Purpose: Implements the main `hwclock(8)` utility: reading, setting, adjusting, predicting, and synchronizing hardware and system clocks.

Core behavior:
- Defaults to `--show`, and supports `--get`, `--set --date`, `--hctosys`, `--systohc`, `--systz`, `--adjust`, `--predict --date`, Linux RTC parameters, voltage-low operations, Alpha epoch operations, testing mode, alternate adjtime/RTC files, UTC/localtime selection, and verbose/debug output.
- Selects a hardware access backend through `clock_ops`: direct CMOS when compiled and requested, otherwise `/dev/rtc` on Linux/GNU.
- Reads `/etc/adjtime`-style data into drift factor, last adjustment, last calibration, unadjusted remainder, and UTC/local marker; writes it back when dirty unless `--noadjfile`.
- Determines whether the hardware clock is UTC from command-line options or adjtime state, defaulting to UTC when not explicitly local.
- Performs tick-synchronized reads, converts RTC `struct tm` with `mktime()`/`timegm()`, calculates drift, and displays either raw show time or drift-corrected get time.
- Sets the hardware clock with sub-second alignment logic that waits for the chosen reference offset and accounts for the typical RTC set delay.
- Handles system clock/timezone operations through `settimeofday` wrappers that avoid libc portability issues around the deprecated timezone argument.

Important implementation details:
- `set_hardware_clock_exact()` is the timing-critical core: it computes a target system time, loops until close enough within an expanding tolerance, retargets after missed windows or backward jumps, then sets the RTC to an adjusted integer second.
- `adjust_drift_factor()` updates drift only with `--update-drift`, enough calibration history, and at least four hours since prior calibration; excessive drift is reset to zero.
- `manipulate_clock()` centralizes operation selection and intentionally avoids reading the RTC for simple set/systohc operations unless drift update is requested, reducing shutdown latency and allowing recovery from corrupt RTC reads.
- Audit logging is optional through libaudit and records time-changing operations unless testing.

Dependencies and integration:
- Uses `hwclock.h` backend contracts, `hwclock-rtc.c`, optionally `hwclock-cmos.c`, and optionally `hwclock-parse-date.y`.
- Relies on util-linux time, path, string, debug, NLS, and close-stream helpers.

Risks and edge cases:
- Time-setting logic is sensitive to scheduler delays and system time jumps; the code explicitly retargets and widens tolerance but cannot guarantee exactness under severe scheduling latency.
- `--noadjfile` requires explicit `--utc` or `--localtime`, preventing silent defaulting when state storage is disabled.
- Kernel timezone/PCIL behavior is Linux-specific and handled with detailed compatibility paths.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock.h -->
# File Research: sources/block-storage/util-linux/sys-utils/hwclock.h

Purpose: Shared interface for the `hwclock` implementation and its hardware backends.

Core contents:
- Defines debug mask bits and `DBG`/`ON_DBG` macros for hwclock-specific util-linux debugging.
- Defines `struct hwclock_control`, the central option/state bundle shared by `hwclock.c`, RTC, and CMOS backends.
- Defines `struct clock_ops`, the backend vtable for permissions, read, set, tick synchronization, and device path lookup.
- Declares CMOS and RTC probe functions, optional Alpha epoch helpers, Linux RTC parameter helpers, voltage-low helpers, `hwclock_exit()`, and `parse_date()`.

Dependencies and integration:
- Included by all hwclock source files in this group.
- Encodes platform-conditional fields so callers and backends share a single control ABI across Linux, GNU, Alpha, and direct ISA builds.

Risks and edge cases:
- Many fields in `hwclock_control` are conditional, so source files must preserve matching preprocessor guards when accessing them.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/hwclock.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcmk.c -->
# File Research: sources/block-storage/util-linux/sys-utils/ipcmk.c

Purpose: Implements `ipcmk(1)`, a utility for creating ad-hoc System V and POSIX IPC resources.

Core behavior:
- Creates System V shared memory (`shmget`), message queues (`msgget`), and semaphore arrays (`semget`) using random keys from util-linux random helpers.
- Creates POSIX shared memory (`shm_open` plus `ftruncate`), POSIX message queues (`mq_open`), and POSIX semaphores (`sem_open`) when the relevant headers/features are available.
- Parses resource size/count, octal permissions, and POSIX resource names; POSIX IPC creation requires `--name`.
- Prints the created System V id or POSIX name on success.

Dependencies and integration:
- Uses `randutils.h` for random keys, `strutils.h` for size/integer parsing, and feature guards for `mqueue.h`, `semaphore.h`, and `sys/mman.h`.

Risks and edge cases:
- Multiple creation options can be combined; a single `size`, `nsems`, `permission`, and `name` state is reused according to parsed options.
- POSIX fallbacks emit "not supported" warnings and fail cleanly when headers/features are unavailable.
- System V resources use random keys with `IPC_CREAT` but not `IPC_EXCL`, so an unlikely key collision could attach to an existing resource type rather than force uniqueness.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcmk.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcrm.c -->
# File Research: sources/block-storage/util-linux/sys-utils/ipcrm.c

Purpose: Implements `ipcrm(1)`, removing System V and POSIX IPC resources by id, key, name, or whole category.

Core behavior:
- Supports modern options for shared memory, message queues, semaphores by id/key, and POSIX shared memory/message queues/semaphores by name.
- Retains deprecated syntax `ipcrm shm|msg|sem <id>...`.
- Converts System V keys to ids with `shmget`, `msgget`, or `semget`, rejecting `IPC_PRIVATE`.
- Removes System V resources with `shmctl(IPC_RMID)`, `msgctl(IPC_RMID)`, or `semctl(IPC_RMID)`.
- Removes POSIX resources with `shm_unlink`, `mq_unlink`, and `sem_unlink` under feature guards.
- `--all[=shm|pshm|msg|pmsg|sem|psem]` enumerates each resource class and removes discovered resources.

Important implementation details:
- System V "remove all" uses kernel enumeration via `SHM_INFO/SHM_STAT`, `SEM_INFO/SEM_STAT`, and `MSG_INFO/MSG_STAT`.
- POSIX "remove all" relies on `ipcutils` enumeration functions over `/dev/shm` and `/dev/mqueue`.
- Removal errors are accumulated; the command exits failure if any requested removal fails.

Dependencies and integration:
- Depends on `ipcutils.h` for POSIX enumeration structures and fallback compatibility definitions.
- Shares POSIX IPC support additions with `ipcmk.c` and `ipcutils.c`.

Risks and edge cases:
- `--all` is broad and destructive by design; filtering by category is supported but not by owner.
- Error strings distinguish invalid/permission/already-removed ids and keys for System V resources.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcrm.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcs.c -->
# File Research: sources/block-storage/util-linux/sys-utils/ipcs.c

Purpose: Implements `ipcs(1)`, displaying System V IPC status, limits, ownership, timestamps, PIDs, and detailed resource data.

Core behavior:
- Selects resource classes with `--queues`, `--shmems`, `--semaphores`, or defaults to all.
- Selects output forms: default listings, `--time`, `--pid`, `--creator`, `--limits`, `--summary`, and specific `--id` detail mode.
- Supports byte and human-readable size output using `ipc_print_size()`.
- For shared memory, prints limits/status, standard listings including status flags (`dest`, `locked`), creator/owner, attach/detach/change times, PIDs, and detailed id records.
- For semaphores, prints limits/status, array listings, creator/owner, operation/change times, and per-semaphore values/wait counts/PIDs in id detail mode.
- For message queues, prints limits/status, queue listings, creator/owner, send/receive/change times, PIDs, and detailed id records including queue byte limits.

Dependencies and integration:
- Uses data collection and formatting helpers from `ipcutils.c`/`ipcutils.h`.
- Uses `timeutils.h` for ctime buffer sizing and util-linux parsing/NLS helpers.

Risks and edge cases:
- `--id` requires exactly one resource class; without `--id`, no class means all classes.
- `ctime64()` casts int64-backed procfs timestamps to `time_t *`, matching the file comment's assumption but depending on local `time_t` representation compatibility.
- POSIX IPC structures exist in `ipcutils.h`, but this `ipcs.c` implementation displays System V IPC only.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcutils.c -->
# File Research: sources/block-storage/util-linux/sys-utils/ipcutils.c

Purpose: Shared IPC data collection and formatting library for `ipcs` and `ipcrm`, covering System V IPC and newer POSIX IPC enumeration support.

Core behavior:
- Reads System V IPC limits from procfs paths when available, falling back to `msgctl(IPC_INFO)`, `semctl(IPC_INFO)`, or `shmctl(IPC_INFO)`.
- Collects shared memory, semaphore, and message queue records from `/proc/sysvipc/*` when available, falling back to kernel enumeration through `*_INFO` and `*_STAT`.
- For a specific semaphore id, retrieves each semaphore element's value, wait-for-increase count, wait-for-zero count, and last-operation PID.
- Enumerates POSIX shared memory and POSIX semaphores from `/dev/shm`, distinguishing semaphore entries by the `sem.` prefix.
- Enumerates POSIX message queues from `/dev/mqueue`, reading queue byte usage from the queue filesystem entry and current message count through `mq_getattr()`.
- Provides free functions for linked-list result structures and common printers for permissions and sizes.

Important implementation details:
- The System V list representation uses a sentinel-like extra allocated node; callers iterate until `next == NULL`.
- `ipc_print_size()` supports default bytes, kilobytes, and human output with configurable width and label style.
- POSIX message queue names are normalized with a leading `/` before `mq_open()`/comparison.

Dependencies and integration:
- Uses `pathnames.h` procfs and devfs constants, `path.h` read helpers, `xalloc.h`, `strutils.h`, and POSIX/System V IPC headers exposed through `ipcutils.h`.
- Serves `ipcs.c` for display and `ipcrm.c` for `--all` POSIX removal.

Risks and edge cases:
- Several POSIX result free functions free list nodes but not allocated name strings, so enumeration can leak per-entry names in long-running callers; current CLI tools are short-lived.
- The POSIX message queue allocator uses `sizeof(struct msg_data)` for a `struct posix_msg_data` pointer in the initial allocation, which overallocates but is type-inconsistent.
- Fallback paths assign `cgid` from `cuid` in shared memory and semaphore fallback records, which appears inconsistent with the procfs path and likely loses creator group information.
- Delta/list consumers assume stable procfs parsing formats, with partial parsing lines skipped.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcutils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcutils.h -->
# File Research: sources/block-storage/util-linux/sys-utils/ipcutils.h

Purpose: Header for shared IPC compatibility definitions, data structures, and helper APIs used by `ipcs`, `ipcrm`, and related IPC utilities.

Core contents:
- Includes System V IPC, POSIX mqueue/semaphore, passwd/group, and standard type headers under feature guards.
- Supplies fallback definitions for `SHM_DEST`, `SHM_LOCKED`, `MSG_STAT/INFO`, `SHM_STAT/INFO`, `SEM_STAT/INFO`, `IPC_INFO`, `struct shm_info`, and `union semun` where libc/kernel headers do not expose them.
- Defines the `KEY` macro abstraction for glibc `ipc_perm.__key` versus older `key`.
- Defines output units, `struct ipc_limits`, common `struct ipc_stat`, and typed linked-list records for System V shared memory/semaphore/message queues plus POSIX shared memory/semaphore/message queues.
- Declares limit, enumeration, free, permission-printing, and size-printing functions.

Dependencies and integration:
- Central contract for `ipcutils.c`, `ipcs.c`, and `ipcrm.c`.
- Encodes portability glue for older libc/kernel header combinations.

Risks and edge cases:
- Structures mirror kernel/procfs concepts and comments cite kernel internal structures; field availability and width assumptions must stay aligned with parser code in `ipcutils.c`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ipcutils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/irq-common.c -->
# File Research: sources/block-storage/util-linux/sys-utils/irq-common.c

Purpose: Shared parser, sorter, and libsmartcols table builder for interrupt and softirq display tools.

Core behavior:
- Defines output columns (`IRQ`, `TOTAL`, `DELTA`, `NAME`) with smartcols width hints, alignment/truncation flags, help text, and JSON types.
- Parses `/proc/interrupts` or `/proc/softirqs`, counts active CPU columns from the header, sums per-IRQ and per-CPU totals over an optional CPU filter, and stores descriptive names.
- For softirqs, maps well-known softirq names such as `NET_RX`, `BLOCK`, and `RCU` to friendly descriptions.
- Builds smartcols tables for IRQ rows and for per-CPU percentage summaries.
- Computes deltas from a previous snapshot, sorts by total by default, and supports sorting by IRQ, total, delta, or name.

Important implementation details:
- CPU filtering is applied while accumulating totals; absent a cpuset all CPUs are included.
- `/proc/interrupts` parsing advances the input cursor by fixed-width counter fields after `sscanf("%10lu")`, matching the kernel file's column layout.
- `get_scols_table()` copies `irq_info` into a sortable result array so the original snapshot can be retained as the next `prev_stat`.
- Threshold filtering uses total counts, not deltas.

Dependencies and integration:
- Implements APIs declared in `irq-common.h`.
- Used by `irqtop.c` and likely other util-linux IRQ reporting tools.
- Uses libsmartcols, util-linux cpuset, string, pathnames, xalloc, and NLS helpers.

Risks and edge cases:
- Delta calculation assumes current and previous IRQ arrays have the same ordering and count. If `/proc/interrupts` changes between samples, deltas can be associated with the wrong row.
- Per-CPU total percentage divides by `curr->total_irq`; unusual empty input could risk invalid percentages.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/irq-common.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/irq-common.h -->
# File Research: sources/block-storage/util-linux/sys-utils/irq-common.h

Purpose: Shared declarations and data structures for IRQ reporting utilities.

Core contents:
- Defines column ids for `IRQ`, `TOTAL`, `DELTA`, and `NAME`.
- Defines `struct irq_info` for per-interrupt totals/deltas/name, `struct irq_cpu` for per-CPU totals/deltas, and `struct irq_stat` for a whole snapshot.
- Defines `struct irq_output` for selected columns, sorting callback, and output modes (`json`, key-value pairs, no headings).
- Declares column lookup/printing, sort selection, snapshot freeing, and smartcols table construction functions.

Dependencies and integration:
- Includes util-linux `cpuset.h` and libsmartcols types through function declarations.
- Consumed by `irq-common.c` and `irqtop.c`.

Risks and edge cases:
- `irq_output.columns` is fixed-size at twice the column count; callers must use provided parsing helpers or maintain bounds.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/irq-common.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/irqtop.c -->
# File Research: sources/block-storage/util-linux/sys-utils/irqtop.c

Purpose: Implements `irqtop(1)`, an interactive or batch top-like display for kernel interrupt or softirq activity.

Core behavior:
- Supports curses screen mode by default and batch stdout mode with `--batch`; JSON implies batch mode.
- Periodically refreshes using `timerfd` and `epoll`, handles signals through `signalfd`, and accepts interactive sort keys from stdin.
- Displays a header with total interrupts, delta interrupts, hostname, and current timestamp.
- Shows optional per-CPU percentage tables (`auto`, `never`, `always`) and the main IRQ/softirq table from `irq-common.c`.
- Supports CPU filtering, refresh delay, iteration limit, selected columns, sort column, softirq mode, and total-count threshold.
- Interactive keys sort by IRQ (`i`), total (`t`), delta (`d`), name (`n`), or quit (`q`).

Important implementation details:
- `update_screen()` selects `/proc/softirqs` or `/proc/interrupts`, builds smartcols output, renders through curses or stdout, and retains the current snapshot as `prev_stat` for the next delta.
- `event_loop()` multiplexes timer, signals, and stdin. Window resize triggers terminal dimension refresh and `resizeterm()` when available.
- Terminal state is saved/restored around curses mode when stdin is a TTY.
- Default columns are `IRQ,TOTAL,DELTA,NAME`; `--output` is parsed through `irq_column_name_to_id()`.

Dependencies and integration:
- Uses `irq-common.c`, libsmartcols, curses/slang/ncurses variants, util-linux cpuset, time, monotonic, tty, hostname, and parsing helpers.

Risks and edge cases:
- The event loop returns an accumulated status but `main()` currently returns `EXIT_SUCCESS`, so update failures do not affect process exit status.
- Batch mode still uses the same event loop and timer semantics; an explicit iteration count is needed for bounded repeated batch output.
- Snapshot delta caveats from `irq-common.c` apply if IRQ rows appear/disappear between refreshes.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/irqtop.c -->