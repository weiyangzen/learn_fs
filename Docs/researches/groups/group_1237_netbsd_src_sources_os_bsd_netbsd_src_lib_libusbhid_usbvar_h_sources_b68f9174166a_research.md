# Group Research: group_1237_netbsd_src_sources_os_bsd_netbsd_src_lib_libusbhid_usbvar_h_sources_b68f9174166a

Scope checked: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/usbvar.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/usbvar.h

## Purpose
Defines the private `struct report_desc` container used by `libusbhid` for USB HID report descriptors.

## Key Details
- Holds descriptor byte count in `size`.
- Uses historical trailing `data[1]` variable-sized allocation idiom.

## Dependencies and Role
- No includes or functions.
- Acts as a tiny internal ABI/data carrier for HID descriptor parsing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/usbvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/Makefile

## Purpose
Build definition for NetBSD `libutil`.

## Key Details
- Builds `LIB=util` with `USE_SHLIBDIR=yes`.
- Includes common libutil sources from `common/lib/libutil/Makefile.inc`.
- Local source list covers disk helpers, mount option parsing, login accounting, login capabilities, passwd editing, pid files, ptys, tty messaging, sockaddr formatting, stat flags, and percent formatting.
- Includes `compat/Makefile.inc` for legacy ABI wrappers.
- Sets `YPREFIX=__pd` for `parsedate.y`.
- Defines extensive manpage `MLINKS`.

## Filesystem/Storage Relevance
- Central build map for disklabel, raw/cooked disk naming, fstab/wedge lookup, mount option, and password database utilities in this batch.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/Makefile.inc

## Purpose
Adds compatibility sources and include paths for old `libutil` ABI entry points.

## Key Details
- Adds `.PATH` for the `compat` directory.
- Adds include paths for libc and sys compatibility headers.
- Compiles wrappers for passwd, login, loginx, parsedate, and login capability APIs.

## Dependencies and Role
- Supports old struct/time ABI compatibility by delegating to current implementations after conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_gepwconf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_gepwconf.c

## Purpose
Compatibility wrapper for old `pw_getpwconf` using `struct passwd50`.

## Key Details
- Defines `__LIBC12_SOURCE__`.
- Emits `__warn_references` for callers binding the old symbol.
- Converts `passwd50` to current `struct passwd`.
- Calls `__pw_getpwconf50`.

## Dependencies and Role
- Depends on compatibility passwd and util headers.
- Contains no password config parsing itself; it is a narrow ABI shim.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_gepwconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_login.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_login.c

## Purpose
Legacy `login()` implementation for old `struct utmp50`.

## Key Details
- Converts `utmp50` to current `struct utmp`.
- Writes current tty slot in `_PATH_UTMP`.
- Appends login record to `_PATH_WTMP`.
- Warns callers to include `<util.h>` for the correct symbol reference.

## Dependencies and Role
- Mirrors current `login.c` behavior after compatibility conversion.
- Operates directly on legacy utmp/wtmp accounting files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_login.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_login_cap.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_login_cap.c

## Purpose
Compatibility wrappers for login class APIs that used `struct passwd50`.

## Key Details
- Wraps `login_getpwclass`.
- Wraps `setusercontext`.
- Converts `passwd50` into current `struct passwd`.
- Delegates to `__login_getpwclass50` and `__setusercontext50`.

## Dependencies and Role
- Preserves old ABI while keeping all policy enforcement in current login capability code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_login_cap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_loginx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_loginx.c

## Purpose
Legacy `loginx()` wrapper for old `struct utmpx50`.

## Key Details
- Converts `utmpx50` to current `struct utmpx`.
- Calls `__pututxline50`.
- Appends to `_PATH_WTMPX` via `__updwtmpx50`.
- Emits compatibility warning reference.

## Dependencies and Role
- Bridges old utmpx ABI to current utmpx accounting behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_loginx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_logoutx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_logoutx.c

## Purpose
Compatibility `logoutx()` implementation for utmpx logout updates.

## Key Details
- Looks up an entry by `ut_line`.
- Updates `ut_type`, exit code, signal termination, and timestamp.
- Writes the modified record with `pututxline`.
- Returns `1` on update and `0` when no matching line exists.

## Dependencies and Role
- Same functional shape as current `logoutx.c`; retained for compatibility builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_logoutx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_parsedate.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_parsedate.c

## Purpose
Old `parsedate()` ABI wrapper using 32-bit time input/output.

## Key Details
- Accepts `const int32_t *` base time.
- Converts to `time_t` before calling `__parsedate50`.
- Casts result back to `int32_t`.
- Emits compatibility warning reference.

## Dependencies and Role
- Preserves pre-time_t ABI for date parsing callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_parsedate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_passwd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_passwd.c

## Purpose
Compatibility wrappers for old passwd editing/scanning APIs using `struct passwd50`.

## Key Details
- Wraps `pw_scan`, `pw_copy`, `pw_copyx`, and `pw_getpwconf`.
- Converts between `struct passwd50` and current `struct passwd`.
- Delegates actual parsing/copying/config lookup to `__pw_*50` entry points.
- Emits warning references for old symbols.

## Dependencies and Role
- ABI adapter around password database management functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_passwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/login_cap.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/login_cap.h

## Purpose
Compatibility declarations for login capability functions involving `struct passwd50`.

## Key Details
- Forward declares current and compatibility passwd structs.
- Declares old public signatures and internal `__*50` implementations.

## Dependencies and Role
- Header bridge used by `compat_login_cap.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/login_cap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/util.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/util.h

## Purpose
Compatibility declarations for old `libutil` utmp, utmpx, parsedate, and passwd APIs.

## Key Details
- Declares old public functions taking `utmp50`, `utmpx50`, `passwd50`, and `int32_t` time.
- Declares internal current-ABI delegation symbols such as `__login50`, `__parsedate50`, and `__pw_copy50`.

## Dependencies and Role
- Shared compatibility header for libutil wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/compat/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/disklabel_dkcksum.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/disklabel_dkcksum.c

## Purpose
Computes the NetBSD disklabel checksum.

## Key Details
- XORs 16-bit words from the start of `struct disklabel` through the active partition array.
- Uses `lp->d_npartitions` to choose the endpoint.
- Returns the accumulated 16-bit checksum.

## Filesystem/Storage Relevance
- Used to validate and generate disklabel metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/disklabel_dkcksum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/disklabel_scan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/disklabel_scan.c

## Purpose
Scans a memory buffer for a valid NetBSD disklabel.

## Key Details
- Advances through the buffer in 4-byte increments.
- Copies candidate bytes into a `struct disklabel`.
- Requires both disklabel magic fields to equal `DISKMAGIC`.
- Rejects labels with too many partitions or nonzero checksum.

## Filesystem/Storage Relevance
- Supports disklabel discovery in raw sectors or larger disk buffers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/disklabel_scan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/efun.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/efun.c

## Purpose
Provides error-checking convenience wrappers for common allocation, string, file, formatting, and numeric conversion routines.

## Key Details
- Default error handler is `err`; `esetfunc` can replace it, with `NULL` selecting an exit-only handler.
- Wraps `strlcpy`, `strlcat`, `strdup`, `strndup`, `malloc`, `calloc`, `realloc`, `reallocarr`, `fopen`, `asprintf`, `vasprintf`.
- `estrtoi` and `estrtou` use bounded conversion helpers and report range/parse failures.

## Dependencies and Role
- General utility error-handling layer for callers that prefer fail-fast behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/efun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getbootfile.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/getbootfile.c

## Purpose
Returns the booted kernel path.

## Key Details
- Defaults to `_PATH_UNIX`.
- If `CPU_BOOTED_KERNEL` exists, queries `machdep.booted_kernel`.
- Restores leading `/` for relative kernel path sysctl output.
- Uses `secure_path` and falls back to `_PATH_UNIX` when the path is unsafe.

## Filesystem/Storage Relevance
- Maps kernel boot metadata to a filesystem path with security validation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getbootfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getbyteorder.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/getbyteorder.c

## Purpose
Returns hardware byte order from sysctl.

## Key Details
- Queries `CTL_HW/HW_BYTEORDER`.
- Returns byte order value or `-1` on sysctl failure.

## Dependencies and Role
- Small machine metadata helper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getbyteorder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getdiskrawname.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/getdiskrawname.c

## Purpose
Converts between block “cooked” disk device names and raw character disk device names.

## Key Details
- Resolves symlinks, preserving relative symlink directories.
- `getdiskrawname` requires the resolved path to be a block device, then adds raw `r` naming.
- `getdiskcookedname` requires a character device, then removes raw `r` naming.
- Handles ZFS zvol paths under `/dev/zvol/dsk` and `/dev/zvol/rdsk` specially.
- Sets `EFTYPE`, `EINVAL`, or `ENOSPC` for mismatches and malformed paths.

## Filesystem/Storage Relevance
- Important utility for tools that must switch between block and raw disk device paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getdiskrawname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getfsspecname.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/getfsspecname.c

## Purpose
Resolves filesystem specifier names into device paths.

## Key Details
- `ROOT.` expands to `/dev/<kern.root_device>` with suffix appended.
- Non-`NAME=` inputs are copied through, with a compatibility path that treats busy disk devices as wedge labels.
- `NAME=<label>` is unvis-decoded and matched against dk wedge names from `hw.disknames`.
- Opens dk devices with `opendisk` and reads `DIOCGWEDGEINFO`.
- Converts raw `/rdk` matches to cooked `/dk` names before returning.

## Filesystem/Storage Relevance
- Bridges fstab-style names, root device aliases, and dk wedge labels to usable device paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getfsspecname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getlabelsector.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/getlabelsector.c

## Purpose
Exposes kernel disklabel placement settings.

## Key Details
- `getlabelsector` queries `KERN_LABELSECTOR`.
- `getlabeloffset` queries `KERN_LABELOFFSET`.
- `getlabelusesmbr` queries `kern.labelusesmbr` by name.
- Each returns `-1` on sysctl failure.

## Filesystem/Storage Relevance
- Used by disklabel-aware tools to locate on-disk label metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getlabelsector.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getmaxpartitions.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/getmaxpartitions.c

## Purpose
Returns the kernel maximum partition count.

## Key Details
- Queries `CTL_KERN/KERN_MAXPARTITIONS`.
- Returns value or `-1` on sysctl failure.

## Filesystem/Storage Relevance
- Helps userland disk tools size partition tables consistently with the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getmaxpartitions.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getmntopts.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/getmntopts.c

## Purpose
Parses comma-separated mount option strings into flag words and saved option arguments.

## Key Details
- `getmntopts` duplicates the option string, tokenizes by comma, supports `no` prefixes, and handles `key=value`.
- Option table entries choose normal or alternate flag storage.
- `getmntoptstr` returns saved argument strings.
- `getmntoptnum` converts saved option arguments to numbers.
- `freemntopts` releases parser allocations.
- Global `getmnt_silent` selects fatal `errx` behavior versus returning errors.

## Filesystem/Storage Relevance
- Core helper for mount command option parsing and filesystem-specific flag handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getmntopts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getrawpartition.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/getrawpartition.c

## Purpose
Returns the kernel raw partition index.

## Key Details
- Queries `CTL_KERN/KERN_RAWPARTITION`.
- Returns index or `-1` on sysctl failure.

## Filesystem/Storage Relevance
- Used by disk-opening helpers to append the platform raw partition letter.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/getrawpartition.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/if_media.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/if_media.c

## Purpose
Maps network interface media words to strings and parses media option strings.

## Key Details
- Exposes description arrays from `<net/if_media.h>`.
- Provides type, subtype, mode, and option string lookup.
- Parses comma-separated media options into IFM option bits.
- Returns invalid option text in caller-owned allocated buffer when requested.

## Dependencies and Role
- Network interface utility code; not filesystem-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/if_media.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/kinfo_getvmmap.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/kinfo_getvmmap.c

## Purpose
Retrieves process virtual memory map entries.

## Key Details
- Uses `CTL_VM/VM_PROC/VM_PROC_MAP`.
- First sysctl obtains size, then allocates a 4/3 enlarged buffer.
- Second sysctl fills `struct kinfo_vmentry` array.
- Returns count through `cntp`; caller frees result.

## Dependencies and Role
- Process introspection helper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/kinfo_getvmmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/login.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/login.c

## Purpose
Records a login in legacy utmp/wtmp accounting files.

## Key Details
- Uses `ttyslot()` to locate current tty slot.
- Writes the supplied `struct utmp` into `_PATH_UTMP`.
- Appends the same record to `_PATH_WTMP`.
- Ignores write/open failures.

## Dependencies and Role
- Traditional session accounting utility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/login.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/login_cap.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/login_cap.c

## Purpose
Implements login class capability lookup and applies login class policy to user sessions.

## Key Details
- `login_getclass` loads `_PATH_LOGIN_CONF` only if `secure_path` accepts it.
- `login_getcapstr`, `login_getcaptime`, `login_getcapnum`, `login_getcapsize`, and `login_getcapbool` expose typed capability lookups.
- Time capabilities support seconds, minutes, hours, days, weeks, and years.
- Size capabilities support byte/block/k/m/g/t suffixes and multiplicative expressions, with overflow detection.
- Resource limits covered include CPU, file size, data, stack, RSS, locked memory, process/thread counts, open files, core size, socket buffer size, and address space.
- `setusercontext` can set rlimits, priority, umask, gid, groups, login name, uid, environment, and path.
- Handles per-user `/tmp` creation when `/tmp` is a magic symlink ending in `/@ruid`.
- `setuserenv` parses `setenv` login capabilities with escaped separators.
- `setuserpath` expands `~` path components using the user home directory.

## Security/Filesystem Relevance
- Uses secure file checks for `login.conf`.
- Creates and fixes permissions/ownership for per-user temporary directories.
- Controls session resource and environment policy.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/login_cap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/login_tty.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/login_tty.c

## Purpose
Makes a tty file descriptor the controlling terminal and standard I/O for a session.

## Key Details
- Calls `setsid`.
- Uses `TIOCSCTTY`.
- Duplicates fd to stdin, stdout, and stderr.
- Closes original fd when no longer needed.

## Dependencies and Role
- Used by pty/forkpty session setup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/login_tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/loginx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/loginx.c

## Purpose
Records a login in utmpx/wtmpx accounting.

## Key Details
- Calls `pututxline`.
- Appends to `_PATH_WTMPX` with `updwtmpx`.

## Dependencies and Role
- Modern utmpx counterpart to `login.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/loginx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/logout.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/logout.c

## Purpose
Marks a legacy utmp session as logged out.

## Key Details
- Opens `_PATH_UTMP` read/write.
- Scans records for matching `ut_line` with nonempty `ut_name`.
- Clears username and host fields.
- Updates logout time and rewrites the record in place.
- Returns whether a record was updated.

## Dependencies and Role
- Legacy session accounting cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/logout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/logoutx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/logoutx.c

## Purpose
Marks a utmpx session as logged out.

## Key Details
- Looks up the utmpx entry by line.
- Updates type, exit status, termination signal, and timestamp.
- Writes with `pututxline` and closes utmpx state with `endutxent`.
- Returns `1` on success, `0` if not found.

## Dependencies and Role
- Modern utmpx session accounting cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/logoutx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/logwtmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/logwtmp.c

## Purpose
Appends a legacy wtmp accounting record.

## Key Details
- Opens `_PATH_WTMP` append-only.
- Fills line, name, host, and current time.
- If the write is short, truncates back to original file size.

## Dependencies and Role
- Low-level wtmp writer used by login/session tools.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/logwtmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/logwtmpx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/logwtmpx.c

## Purpose
Appends a utmpx wtmpx accounting record.

## Key Details
- Zeroes and fills a `struct utmpx`.
- Sets line, name, host, type, exit code/signal, and timestamp.
- Writes through `updwtmpx(_PATH_WTMPX, ...)`.

## Dependencies and Role
- Modern wtmpx writer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/logwtmpx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/opendisk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/opendisk.c

## Purpose
Opens disk device names using NetBSD raw/cooked device naming conventions.

## Key Details
- Rejects `NULL` output buffer and `O_CREAT`.
- Gets raw partition via `getrawpartition`.
- For plain names, tries `/dev/[r]name`, then `/dev/[r]name<rawpart>`.
- For paths, tries exact path, then path plus raw partition letter.
- `opendisk` uses `open`; `opendisk1` accepts a caller-provided open-like function.

## Filesystem/Storage Relevance
- Common disk device opener for filesystem and disklabel tools.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/opendisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/parsedate.y -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/parsedate.y

## Purpose
Yacc grammar and lexer for converting human-readable date/time strings to `time_t`.

## Key Details
- Supports times, dates, day names, time zones, relative expressions, CVS timestamps, epoch `@number`, and ISO-like timestamps.
- Tracks parse state in `struct dateinfo`.
- Supports AM/PM, noon, midnight, numeric zones, named zones, military zones, and relative units.
- Handles relative seconds/minutes/days/weeks and month/year arithmetic.
- Includes overflow checks for relative values, month arithmetic, day arithmetic, and year conversion.
- `Convert` validates that `mktime` or `mktime_z` did not normalize invalid fields.
- `parsedate` defaults missing base time to current time and missing zone to local time.

## Dependencies and Role
- Provides flexible date parsing for userland utilities.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/parsedate.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/passwd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/passwd.c

## Purpose
Implements password database editing, locking, copying, and password configuration lookup helpers.

## Key Details
- Maintains optional path prefix for chroot/install-root style operations.
- `pw_lock` creates `_PATH_MASTERPASSWD_LOCK` with `O_EXCL`, retrying on existing lock.
- `pw_mkdb` runs `pwd_mkdb` to rebuild password databases from the lock file.
- `pw_abort` removes the lock file.
- `pw_init` adjusts resource limits and signal handlers for interactive editing.
- `pw_edit` invokes `$EDITOR` or vi through the shell and handles stopped editor processes.
- `pw_copyx` copies master.passwd to the lock file, replacing or appending one entry with consistency checks.
- `pw_getconf` parses `/etc/passwd.conf`; `pw_getpwconf` tries user, group, then default keys.
- Hardcoded defaults include `localcipher=old` and `ypcipher=old`.

## Filesystem/Security Relevance
- Manipulates password database files safely through lock files and rebuild tooling.
- Prefix support matters for alternate root filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/passwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/pidfile.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/pidfile.c

## Purpose
Manages daemon pidfiles with file locking and cleanup.

## Key Details
- Global state tracks pidfile path, fd, and removeability.
- Default path is `/var/run/<program>.pid` when no slash is supplied.
- `pidfile_lock` opens/creates and locks pidfile, writes current PID, and registers an `atexit` cleanup.
- Uses `O_CLOEXEC` and `O_EXLOCK` when available, otherwise fd flags and `flock`.
- If locked by another process, returns that PID when readable and sets `EEXIST`; otherwise `EAGAIN`.
- `pidfile_clean` only truncates/unlinks when the file contains the current PID.
- `pidfile_unremoveable` disables unlinking for environments where truncation is the fallback.

## Filesystem Relevance
- Coordinates daemon ownership through persistent lock files under `/var/run`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/pidfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/pidlock.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/pidlock.c

## Purpose
Implements pid-based lock files and tty lock helpers.

## Key Details
- Creates a temporary lock file named with PID and sanitized hostname.
- Writes PID, optional hostname, and optional info.
- Atomically links the temp file to the target lock path.
- If lock exists, reads owner PID and optionally hostname, removes stale locks when process no longer exists.
- Supports nonblocking mode returning owner PID.
- Verifies link count after linking for NFS correctness.
- `ttylock` and `ttyunlock` use `/var/spool/lock/LCK..<tty>` after validating `/dev/<tty>` is a character device.

## Filesystem Relevance
- Uses link-based filesystem atomicity for lock acquisition.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/pidlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/pty.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/pty.c

## Purpose
Opens pseudo-terminals and forks child sessions attached to them.

## Key Details
- First tries `/dev/ptm` with `TIOCPTMGET`.
- Falls back to scanning legacy pty/tty device name ranges.
- Sets slave owner/group/mode, revokes old access, and opens slave.
- Applies optional termios and window size.
- `forkpty` opens a pty, forks, and calls `login_tty` in the child.

## Filesystem/Device Relevance
- Manages `/dev/ptm` and legacy `/dev/[pt]tyXX` device nodes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/pty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/raise_default_signal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/raise_default_signal.c

## Purpose
Provides `raise_default_signal` when the platform lacks it.

## Key Details
- Blocks all signals.
- Installs default handler for the requested signal.
- Raises and unblocks that signal to deliver it.
- Restores original handler and signal mask.
- Preserves `errno` during restoration paths.

## Dependencies and Role
- Signal utility for programs that need default signal semantics after custom handlers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/raise_default_signal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/secure_path.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/secure_path.c

## Purpose
Checks whether a path is safe for privileged use.

## Key Details
- Uses `lstat`.
- Requires a regular file.
- Requires root ownership.
- Rejects group- or world-writable files.
- Logs failures to syslog except the commented-out stat failure log.
- Returns `0` when secure, `-1` otherwise.

## Filesystem/Security Relevance
- Used by `getbootfile` and `login_cap` to avoid trusting unsafe files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/secure_path.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/sockaddr_snprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/sockaddr_snprintf.c

## Purpose
Formats `struct sockaddr` values according to a custom percent format language.

## Key Details
- Supports AF_LOCAL, AF_INET, AF_INET6, optional AppleTalk, and optional link-layer addresses.
- Numeric and name forms include `%a`, `%p`, `%A`, `%P`, `%n`, `%N`, `%m`, `%D`, family, length, IPv6 flow/scope, and AppleTalk range.
- Uses `getnameinfo` for numeric and named host/service formatting.
- Includes debug formatters for supported sockaddr families.
- Unknown address families return `EAFNOSUPPORT`.

## Dependencies and Role
- Network address formatting helper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/sockaddr_snprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/stat_flags.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/stat_flags.c

## Purpose
Converts filesystem `st_flags` bits to and from strings.

## Key Details
- `flags_to_string` emits comma-separated names or a default string.
- Handles user flags such as append, immutable, nodump, opaque.
- Handles system flags such as append, archived, immutable, and optional snapshot.
- `string_to_flags` parses tokens and `no` prefixes into set/clear masks.
- Supports aliases like `uappnd/uappend`, `uchg/uimmutable`, `sappnd/sappend`, `schg/simmutable`.

## Filesystem Relevance
- Userland interface for BSD file flags used by tools like `ls`, `chflags`, and archivers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/stat_flags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/strpct.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/strpct.c

## Purpose
Formats integer ratios as decimal percentage-like strings without floating point.

## Key Details
- Supports unsigned `strpct` and signed `strspct`.
- Global rounding mode controlled by `strpct_round`.
- Reentrant variants accept explicit rounding mode.
- Uses a small two-word `bignum` helper to avoid overflow while generating digits.
- Honors locale decimal point.
- Handles denominator zero by treating it as one.

## Dependencies and Role
- General numeric formatting helper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/strpct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/ttyaction.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/ttyaction.c

## Purpose
Runs configured commands for matching tty/action/user events.

## Key Details
- Reads `/etc/ttyaction`.
- Strips `/dev/` prefix from tty input.
- Each non-comment line contains tty pattern, action pattern, and shell command.
- Uses `fnmatch` for tty and action matching.
- Executes matched commands through `/bin/sh -c`.
- Provides environment variables `PATH`, `TTY`, `ACT`, and `USER`.

## Filesystem/Security Relevance
- Reads system configuration and executes configured commands for tty lifecycle events.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/ttyaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/ttymsg.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libutil/ttymsg.c

## Purpose
Writes an iovec message to a terminal device.

## Key Details
- Rejects negative or excessive iovec counts.
- Rejects line names containing slash or dot after optional `pts/` handling.
- Opens `/dev/<line>` nonblocking and verifies it is a tty.
- Handles partial `writev` by advancing local iovec state.
- On `EWOULDBLOCK`, forks a child that switches to blocking mode and times out with alarm.
- Ignores normal terminal disappearance/exclusive-use errors.

## Filesystem/Device Relevance
- Safe terminal-device writer used by wall/syslog/talk-style tools.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libutil/ttymsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/Makefile

## Purpose
Build definition for TCP wrappers `libwrap`.

## Key Details
- Builds `LIB=wrap`.
- Enables fortification by default for network server context.
- Compiles access-control, options, shell command, RFC931, socket, update, diagnostics, and message expansion sources.
- Links against `libblocklist`.
- Installs `tcpd.h`.

## Dependencies and Role
- Central build map for TCP wrappers access-control library.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/clean_exit.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/clean_exit.c

## Purpose
Cleans up and exits when a wrapped daemon will not run.

## Key Details
- Calls request sink function for datagram services to drain unread client data.
- Sleeps five seconds to avoid inetd tight loops and extra log noise.
- Exits with status `0`.

## Dependencies and Role
- TCP wrappers helper for refused datagram-oriented services.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/clean_exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/diag.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/diag.c

## Purpose
Central diagnostics for TCP wrappers.

## Key Details
- Maintains global `tcpd_context` and `tcpd_buf`.
- `tcpd_warn` logs a warning and continues.
- `tcpd_jump` logs an error and `longjmp`s with `AC_ERROR`.
- `tcpd_diag` expands `%m` with `expandm`, formats the message, and includes context file/line when available.

## Dependencies and Role
- Error reporting and nonlocal error handling for access table parsing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/diag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/eval.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/eval.c

## Purpose
Lazy evaluation and caching of TCP wrappers request identity fields.

## Key Details
- Defines global `unknown` and `paranoid` strings.
- `eval_user` optionally performs RFC931 lookup when client/server socket addresses are available.
- `eval_hostaddr` and `eval_hostname` call request-provided lookup callbacks.
- `eval_hostinfo` prefers hostname when known, otherwise address.
- `eval_client` and `eval_server` build printable combined identity strings.

## Dependencies and Role
- Defers DNS/user lookup costs until policy evaluation needs them.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/eval.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/expandm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/expandm.c

## Purpose
Expands active `%m` sequences in format strings to `strerror(errno)` while preserving printf format semantics.

## Key Details
- Saves and restores original `errno`.
- Replaces odd runs ending in `%m`; even escaped sequences remain literal.
- Handles very long non-expanded chunks without exceeding `int` width used by `asprintf`.
- Optionally appends suffix string.
- Returns allocated buffer through `rbuf`, or original format on failure.

## Dependencies and Role
- Used by diagnostics before formatting syslog messages.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/expandm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/expandm.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/expandm.h

## Purpose
Declares `expandm`.

## Key Details
- Uses `__BEGIN_DECLS`/`__END_DECLS`.
- Marks the first argument as a format argument with `__format_arg__(1)`.

## Dependencies and Role
- Header for diagnostic message expansion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/expandm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/fix_options.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/fix_options.c

## Purpose
Inspects and disables IPv4 IP-level socket options for wrapped requests.

## Key Details
- Only operates when `IP_OPTIONS` exists and socket is AF_INET.
- Reads IP options with `getsockopt`.
- Refuses source routing options `IPOPT_LSRR` and `IPOPT_SSRR` by logging and shutting down the fd.
- Refuses malformed option lists.
- Logs ignored non-routing options and attempts to clear IP options.

## Security Role
- Protects wrapped services from source-routing and malformed IP option attacks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/fix_options.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/hosts_access.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/hosts_access.c

## Purpose
Implements TCP wrappers host access control using `hosts.allow` and `hosts.deny`.

## Key Details
- Access policy: allow if matched in allow table, deny if matched in deny table, otherwise allow.
- Uses `setjmp`/`longjmp` for fatal parser/option errors.
- Integrates with `blocklist` on authentication/access failures.
- `table_match` reads logical lines, skips comments/blank lines, splits daemon/client/optional command fields, and runs optional commands or options after match.
- `list_match` supports token lists and `EXCEPT` recursion.
- Server patterns match daemon or `daemon@host`; client patterns match host or `user@host`.
- Host matching supports netgroups, host files, `KNOWN`, `LOCAL`, RBL lookups, net/mask, exact strings, suffixes, and prefixes.
- IPv4 masked matching uses dotted-quad parsing and warns if host bits are set.
- IPv6-capable builds support address/prefix masks, IPv4-mapped addresses, and scope-id comparison.

## Security/Network Role
- Core access-control engine for wrapped daemons.
- Policy errors tend toward denial through `AC_ERROR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/hosts_access.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/hosts_ctl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/hosts_ctl.c

## Purpose
Convenience wrapper around `hosts_access`.

## Key Details
- Initializes a `request_info` with daemon, client name, client address, and user.
- Calls `hosts_access`.
- Provides a limited interface that cannot support selective username lookups or hostname double checks.

## Dependencies and Role
- Simple public API for applications using TCP wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/hosts_ctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/libwrap2netbsd -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/libwrap2netbsd

## Purpose
Shell script to import a tcp_wrappers source tree into NetBSD’s `libwrap` layout.

## Key Details
- Requires source and destination arguments.
- Removes and recreates destination `libwrap` directory.
- Copies selected C sources, manpages, headers, and disclaimer via `pax`.
- Source list includes upstream files such as `hosts_access.c`, `options.c`, `rfc931.c`, `socket.c`, and `diag.c`.

## Dependencies and Role
- Maintainer/import helper, not compiled library code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/libwrap2netbsd -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/misc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/misc.c

## Purpose
Miscellaneous TCP wrappers helper functions.

## Key Details
- `xgets` reads logical lines, increments context line count, and strips backslash-newline continuations.
- `split_at` splits on a delimiter while ignoring delimiters inside square brackets.
- `dot_quad_addr` converts dotted IPv4 text with `inet_aton`.

## Dependencies and Role
- Parser and address helpers used by access-control code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/mystdarg.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/mystdarg.h

## Purpose
Compatibility macros abstracting `stdarg.h` and old `varargs.h`.

## Key Details
- Uses `stdarg.h` under `__STDC__`.
- Falls back to `varargs.h` macros otherwise.
- Defines `VARARGS`, `VASTART`, and `VAEND`.

## Dependencies and Role
- Historical portability header for older tcp_wrappers code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/mystdarg.h -->