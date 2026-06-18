# Group Research: group_378_freebsd_src_sources_os_bsd_freebsd_src_sbin_md5_tests_md5_test_sh_so_8f63ab9f3bee

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/md5/tests/md5_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/md5/tests/md5_test.sh

## Summary
ATF shell test generator for FreeBSD digest utilities. It validates BSD-style digest tools, GNU `*sum` compatibility modes, Perl-compatible `shasum` modes where supported, self-tests, and checksum verification behavior across many algorithms.

## Main Elements
- Defines 8 canonical input vectors and expected outputs for `md5`, SHA variants, RIPEMD-160, and Skein variants.
- Generates ATF test cases with shell `eval` loops for each algorithm and vector.
- Tests BSD output modes: stdin, file, `-`, reverse `-r`, quiet `-q`, passthrough `-p`, and string `-s`.
- Tests GNU output modes: text, binary `-b`, `--tag`, NUL-terminated `-z`, and check mode `-c`.
- Tests Perl `shasum` compatibility for SHA algorithms, including binary and universal input modes.
- Adds targeted tests for GNU binary output, missing-file handling in check mode, `--ignore-missing`, and input-mode parsing.

## Dependencies And Integration
Uses FreeBSD ATF shell APIs: `atf_test_case`, `atf_set`, `atf_check`, and `atf_add_test_case`. Requires the relevant digest utility names (`md5`, `sha256`, `sha256sum`, `shasum`, etc.) per test case.

## Research Notes
The test file is mostly declarative vectors plus dynamic ATF test construction. Its coverage is broad because each vector is checked through multiple command-line compatibility surfaces, not just raw digest calculation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/md5/tests/md5_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdconfig/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mdconfig/Makefile

## Summary
Builds the `mdconfig` runtime utility and its manual page.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mdconfig`.
- Links against `libutil` and `libgeom`.
- Enables tests via `HAS_TESTS` and conditionally descends into `tests` when `MK_TESTS` is enabled.

## Dependencies And Integration
Uses FreeBSD `bsd.prog.mk`; the utility depends on GEOM and md(4) control interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdconfig/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdconfig/mdconfig.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mdconfig/mdconfig.c

## Summary
Implements the `mdconfig` command-line utility for creating, destroying, resizing, querying, and listing FreeBSD memory disks backed by malloc memory, vnode files, swap, or null storage.

## Main Responsibilities
- Parses `-a`, `-d`, `-r`, and `-l` actions and validates incompatible option combinations.
- Builds `struct md_ioctl` requests for `MDIOCATTACH`, `MDIOCDETACH`, `MDIOCRESIZE`, and `MDIOCQUERY`.
- Infers vnode or swap type when `-t` is omitted.
- Parses human-readable sizes with block, byte, KB, MB, GB, TB, and PB suffixes.
- Validates vnode backing files with `realpath`, `open`, `fstat`, and regular-file checks.
- Loads `geom_md` when needed and opens `/dev/mdctl`.
- Lists devices using GEOM tree/stat snapshots, with optional verbose output and file filtering.

## Key Functions
- `main()`: option parsing, action validation, ioctl dispatch.
- `md_set_file()`: canonicalizes and validates vnode backing file and default size.
- `md_list()` / `md_query()`: traverse GEOM providers in class `MD`.
- `print_options()`: queries a unit and prints enabled md options.
- `md_find()`: matches comma-separated md unit/device names.
- `md_prthumanval()`: humanizes provider byte lengths.

## Dependencies And Integration
Includes `<sys/mdioctl.h>`, `<libgeom.h>`, `<libutil.h>`, and devstat/GEOM APIs. It is the userland control path for the `geom_md` kernel module and md(4) providers.

## Research Notes
The code has careful command-line compatibility behavior: `mdconfig file` implies attach-vnode mode, `-n` suppresses the `md` prefix in some output, and read-only vnode mode is auto-enabled when the backing file cannot be opened writable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdconfig/mdconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdconfig/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mdconfig/tests/Makefile

## Summary
Registers the `mdconfig_test` ATF shell test.

## Main Elements
- Sets `ATF_TESTS_SH=mdconfig_test`.
- Marks the test as requiring root through `TEST_METADATA.mdconfig_test+= required_user="root"`.
- Includes `bsd.test.mk`.

## Research Notes
Root is required because the tests create and destroy md(4) devices.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdconfig/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdconfig/tests/mdconfig_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/mdconfig/tests/mdconfig_test.sh

## Summary
ATF shell tests for `mdconfig` attach, resize, listing, and verbose query behavior.

## Main Elements
- `check_diskinfo()` validates sector size, media size, sector count, stripe size, and offset using `diskinfo`.
- `cleanup_common()` detaches the md device recorded in `mdconfig.out`.
- Tests implicit and explicit vnode attach modes.
- Tests vnode sizes smaller and larger than backing file size.
- Tests non-default sector size.
- Tests `malloc` and `swap` md types.
- Tests attaching a specific unit number.
- Tests provider size round-down to sector-size multiples on attach and resize.
- Tests verbose listing with options such as `force,reserve`.

## Dependencies And Integration
Requires `mdconfig`, `diskinfo`, `truncate`, shell, and root privileges. Exercises the live md(4)/GEOM stack.

## Research Notes
The tests intentionally inspect both kernel-visible device geometry and `mdconfig -lv` user-facing output, catching regressions in ioctl behavior and formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdconfig/tests/mdconfig_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdmfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mdmfs/Makefile

## Summary
Builds the `mdmfs` runtime utility and installs compatibility links/manual aliases for `mount_mfs`.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mdmfs`.
- Adds link `${BINDIR}/mount_mfs`.
- Adds manual cross-link `mdmfs.8 mount_mfs.8`.
- Includes `bsd.prog.mk`.

## Research Notes
The link reflects `mdmfs` acting as the replacement wrapper for the historical `mount_mfs` interface.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdmfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdmfs/mdmfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mdmfs/mdmfs.c

## Summary
Implements `mdmfs`, a wrapper around `mdconfig`, `newfs`, `mount`, optional `tmpfs`, mountpoint ownership/mode setup, and skeleton-directory copying. It emulates deprecated `mount_mfs` command-line behavior.

## Main Responsibilities
- Parses mount_mfs-compatible options and translates many of them into `mdconfig`, `newfs`, or `mount` arguments.
- Selects tmpfs automatically for `auto` when available and when multilabel MAC is not requested.
- Creates md devices with fixed or automatic units, formats them unless `-P` is used, then mounts them.
- Supports vnode, malloc, and swap-backed md devices.
- Converts size arguments using mdconfig semantics, including unsuffixed 512-byte block counts.
- Applies mountpoint mode, uid, and gid after mount when requested.
- Optionally copies a skeleton tree into the mounted filesystem with `pax`.

## Key Functions
- `argappend()`: appends formatted helper arguments.
- `run()`: forks and execs helper programs from a whitespace-split command string.
- `do_mdconfig_attach()` / `do_mdconfig_attach_au()` / `do_mdconfig_detach()`.
- `do_newfs()`, `do_mount_md()`, `do_mount_tmpfs()`.
- `do_mtptsetup()`: chmod/chown after mount, skipping read-only mounts.
- `extract_ugid()`: parses `user:group`.

## Dependencies And Integration
Uses `/sbin/mdconfig`, `/sbin/newfs`, `/sbin/mount`, `/bin/pax`, md(4) type constants, `statfs`, user/group databases, and kld module lookup/loading for tmpfs.

## Research Notes
`run()` does not implement shell quoting; it splits generated command strings on spaces before `execv`. Paths or option values containing spaces are therefore fragile. This is consistent with older wrapper-style code but important for behavior analysis.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mdmfs/mdmfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mknod/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mknod/Makefile

## Summary
Builds the `mknod` runtime utility and its manual page.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mknod`.
- Installs `mknod.8`.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mknod/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mknod/mknod.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mknod/mknod.c

## Summary
Implements the `mknod` utility for creating character or block device nodes and optionally setting owner/group.

## Main Responsibilities
- Supports `mknod name` for a default character node with device number 0.
- Supports `mknod name [b|c] major minor [owner:group]`.
- Parses major/minor numbers and validates that `makedev()` preserves them.
- Resolves owner and group names or numeric IDs.
- Calls `mknod()` and optional `chown()`.

## Key Functions
- `id()`: parses numeric uid/gid fallback.
- `a_uid()` / `a_gid()`: resolve user/group names or numeric IDs.
- `main()`: validates arguments, constructs mode/dev, creates node, changes ownership.

## Research Notes
The owner/group parser requires both owner and group when the optional sixth argument is present; partial forms are rejected.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mknod/mknod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mksnap_ffs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mksnap_ffs/Makefile

## Summary
Builds the `mksnap_ffs` UFS snapshot utility.

## Main Elements
- Sets `.PATH` to reuse mount support context.
- Sets `PACKAGE=ufs`.
- Builds `PROG=mksnap_ffs`.
- Links `libutil`.
- Installs `mksnap_ffs.8`.
- Uses setuid-root/operator-group install mode unless `NOSUID` is defined.
- Includes `bsd.prog.mk`.

## Research Notes
The install mode and operator group are part of the utility’s permission model for creating filesystem snapshots.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mksnap_ffs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mksnap_ffs/mksnap_ffs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mksnap_ffs/mksnap_ffs.c

## Summary
Creates an FFS/UFS snapshot file by issuing an `nmount()` update request with the `snapshot` option, then adjusts ownership and permissions.

## Main Responsibilities
- Accepts current `snapshot_name` usage and old three-argument compatibility form.
- Validates snapshot path length, parent directory existence, directory type, write permission, and sticky-bit constraints.
- Handles chroot edge cases where `f_mntonname` may point outside the visible root by finding a same-filesystem path suffix.
- Builds `nmount` iovecs for `fstype=ffs`, `from=snapshot`, `fspath=mountpoint`, `update`, and `snapshot`.
- Verifies created file has `SF_SNAPSHOT`.
- Sets group to `operator` and mode to user/group read.

## Key Functions
- `isdir()`: stat and directory check.
- `issamefs()`: compares filesystem IDs for mountpoint suffix detection.
- `main()`: permission checks, snapshot mount update, post-create validation and chmod/chown.

## Dependencies And Integration
Uses UFS/FFS mount semantics via `nmount()`, `build_iovec`, `statfs`, file flags, and the `operator` group.

## Research Notes
Most safety logic occurs before `nmount`: the program checks that the invoking user can create and later remove the snapshot file in the target directory.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mksnap_ffs/mksnap_ffs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount/Makefile

## Summary
Builds the generic `mount` runtime utility.

## Main Elements
- Builds `mount.c`, `mount_fs.c`, and `vfslist.c`.
- Links `libutil` and `libxo`.
- Installs `mount.8`.
- Includes `bsd.prog.mk`.

## Research Notes
`libxo` is used for structured and human-readable mount output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/extern.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount/extern.h

## Summary
Shared declarations for the generic `mount` utility.

## Main Contents
- Declares `checkvfsname()` and `makevfslist()` from `vfslist.c`.
- Declares `mount_fs()` from `mount_fs.c`.

## Dependencies And Integration
Included by `mount.c`, `mount_fs.c`, and `vfslist.c` to connect VFS list filtering and direct `nmount` mounting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/mount.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount/mount.c

## Summary
Main implementation of FreeBSD’s generic `mount` utility. It lists mounted filesystems, mounts all eligible fstab entries, mounts by fstab lookup, remounts mounted filesystems, delegates legacy filesystem types to `mount_*` helpers, or performs direct `nmount()` through `mount_fs()`.

## Main Responsibilities
- Parses global options: all mounts, debug, alternate fstab, force, late mounts, options, fstab-style output, read-only/read-write, update, verbose, and type filters.
- Handles `mount -a`, `mount -p`, plain listing, one-argument fstab/current lookup, and two-argument direct mount forms.
- Infers NFS for `host:path` or `path@host`-style specs when no type is specified.
- Maintains compatibility with external helpers for `cd9660`, `mfs`, `msdosfs`, `nfs`, `nullfs`, `smbfs`, `udf`, and `unionfs`.
- Converts fstab/current meta-options, removes contradictory options, and strips boot-only options before mounting.
- Emits mount listing through `libxo`.
- Signals mountd via `/var/run/mountd.pid` after successful root-initiated mounts.

## Key Functions
- `use_mountprog()` / `exec_mountprog()`: decide and execute helper programs.
- `specified_ro()`: detects explicit read-only options.
- `ismounted()` / `isremountable()`: avoid duplicate `mount -a` mounts.
- `allow_file_mount()`: permits file mountpoints for nullfs.
- `hasopt()`: option presence with `no` inversion semantics.
- `mountfs()`: resolves paths, prepares helper argv, chooses helper vs direct mount.
- `mangle()`: converts comma options into helper-style arguments and handles `mountprog`.
- `update_options()`, `remopt()`, `flags2opts()`: option normalization.
- `prmount()` and `putfsent()`: output current mounts.

## Dependencies And Integration
Uses fstab APIs, `getmntinfo`, `getmntpoint`, `checkpath`, `checkpath_allow_file`, `rmslashes`, `libxo`, `libutil`, and helper programs searched through `_PATH_SYSPATH`.

## Research Notes
The code has important policy boundaries: `noauto`, `late`, `failok`, and quota options are consumed by `mount` and not passed to filesystems; `mountprog=` can force a helper. Direct mount support remains delegated to `mount_fs()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/mount_fs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount/mount_fs.c

## Summary
Implements direct `nmount()` mounting for filesystems that do not require an external `mount_*` helper.

## Main Responsibilities
- Parses per-mount `-o` options.
- Converts standard mount options to `mntflags` with `getmntopts`.
- Adds each option as an iovec key/value pair.
- Validates and canonicalizes the mount path with `checkpath`.
- Normalizes the source path with `rmslashes`.
- Builds required iovecs: `fstype`, `fspath`, `from`, and `errmsg`.
- Calls `nmount()` and reports kernel-provided error text.

## Dependencies And Integration
Called by `mountfs()` in `mount.c`. Uses `build_iovec`, `getmntopts`, and FreeBSD `nmount()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/mount_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/pathnames.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount/pathnames.h

## Summary
Defines path constants used by the generic `mount` utility.

## Main Contents
- Defines `_PATH_MOUNTDPID` as `/var/run/mountd.pid`.

## Dependencies And Integration
Used by `mount.c` to signal mountd after successful root-initiated mounts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/vfslist.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount/vfslist.c

## Summary
Implements filesystem-type include/exclude filtering for `mount -t`.

## Main Elements
- `makevfslist()`: parses comma-separated filesystem names into a NULL-terminated array, with leading `no` meaning exclusion mode.
- `checkvfsname()`: returns whether a filesystem should be skipped based on the parsed list and global `skipvfs`.

## Research Notes
The parser mutates the input string in place by replacing commas with NUL terminators.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount/vfslist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_cd9660/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_cd9660/Makefile

## Summary
Builds the `mount_cd9660` runtime helper.

## Main Elements
- Builds `PROG=mount_cd9660`.
- Links `libkiconv` and `libutil`.
- Leaves dynamic linking enabled for optional userland libiconv access.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_cd9660/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_cd9660/mount_cd9660.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_cd9660/mount_cd9660.c

## Summary
Mount helper for ISO 9660/CD9660 filesystems with Rock Ridge, Joliet, generation-number, permission mapping, session selection, and charset conversion options.

## Main Responsibilities
- Parses cd9660-specific options and standard/update mount options.
- Resolves uid/gid and masks from names or octal strings.
- Optionally reads CD-ROM TOC to choose the last data track starting sector.
- Forces read-only mount.
- Builds `nmount()` iovecs for `fstype=cd9660`, mount path, source device, start sector, and options.
- Loads `cd9660_iconv` and registers Unicode-to-local charset conversion for `-C`.

## Key Functions
- `get_ssector()`: reads CD TOC and returns last data track LBA.
- `set_charset()`: loads iconv module and builds charset iovecs.
- `a_uid()`, `a_gid()`, `a_mask()`: parse ownership/mode options.

## Research Notes
If no session is specified and TOC probing fails, the helper falls back to sector 0, preserving historical behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_cd9660/mount_cd9660.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_fusefs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_fusefs/Makefile

## Summary
Builds the `mount_fusefs` helper with optional debug compile flags.

## Main Elements
- Supports `DEBUG`, `DEBUG2G`, `DEBUG3G`, `DEBUG_MSG`, and `F4BVERS` make-time flags.
- Builds `PROG=mount_fusefs`.
- Links `libutil`.
- Installs `mount_fusefs.8`.

## Research Notes
The Makefile preserves legacy fuse4bsd version/debug controls.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_fusefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_fusefs/mount_fusefs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_fusefs/mount_fusefs.c

## Summary
Mount helper for FUSE filesystems. It parses FUSE-specific options, opens or validates a fuse device/file descriptor, optionally launches a FUSE daemon, and passes the device fd to the kernel via `nmount()`.

## Main Responsibilities
- Parses positional arguments flexibly, plus long options such as `--daemon`, `--daemon_opts`, `--special`, and `--mountpath`.
- Translates FUSE options into mount flags and iovecs, including `allow_other`, `default_permissions`, `max_read`, `subtype`, `fsname`, `automounted`, `intr`, and `auto_unmount`.
- Ignores selected Linux-specific options for compatibility.
- Supports safe mode that forbids spawning daemons.
- Opens `/dev/fuse` or accepts a numeric fd.
- Validates that the device is a fuse character device.
- Sets `FUSE_DEV_FD` and `FUSE_NO_MOUNT` before launching daemon code.
- Calls `nmount()` with `fstype=fusefs`, `fspath`, `from`, and `fd`.

## Dependencies And Integration
Uses `getopt_long`, `getmntopts`, `devname_r`, environment variables expected by FUSE daemons, and FreeBSD `nmount()`.

## Research Notes
`--daemon` execution uses `system()` with a constructed background command string, while the positional daemon path uses `fork()` plus `execvp()`. Safe mode blocks both daemon-spawning surfaces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_fusefs/mount_fusefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_msdosfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_msdosfs/Makefile

## Summary
Builds the `mount_msdosfs` runtime helper.

## Main Elements
- Builds `PROG=mount_msdosfs`.
- Links `libkiconv` and `libutil`.
- Leaves dynamic linking enabled for optional userland libiconv access.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_msdosfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_msdosfs/mount_msdosfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_msdosfs/mount_msdosfs.c

## Summary
Mount helper for FAT/MS-DOS filesystems. It maps command-line options into msdosfs `nmount()` iovecs, including name handling, uid/gid/mode defaults, and charset conversion.

## Main Responsibilities
- Supports short names, long names, no Win95 mode, uid, gid, file mask, directory mask, generic options, locale, DOS codepage, and predefined conversion tables.
- Defaults uid, gid, and masks from the mountpoint when not explicitly set.
- Loads `msdosfs_iconv` and registers charset mappings when local or DOS charset options are provided.
- Builds iovecs for `fstype=msdosfs`, `fspath`, `from`, `errmsg`, `uid`, `gid`, `mask`, and `dirmask`.
- Calls `nmount()` and reports kernel error text.

## Key Functions
- `a_uid()`, `a_gid()`, `a_mask()`.
- `set_charset()`: registers Unicode/local and DOS/local conversion pairs.

## Research Notes
When only a DOS charset is specified, local charset defaults to `ISO8859-1`. File and directory masks default together unless one was explicitly supplied.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_msdosfs/mount_msdosfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_nfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_nfs/Makefile

## Summary
Builds the `mount_nfs` helper.

## Main Elements
- Sets `PACKAGE=nfs`.
- Builds `mount_nfs.c` and shared `mounttab.c`.
- Links `libutil`.
- Includes rpc.umntall source path for `mounttab` support.
- Defines `NFS`.

## Research Notes
The helper updates the traditional mounttab for non-NFSv4 mounts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_nfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_nfs/mount_nfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_nfs/mount_nfs.c

## Summary
Mount helper for NFS. It parses NFS mount options, resolves servers, negotiates NFS and mount protocol details through RPC, obtains filehandles for NFSv2/v3, handles NFSv4 direct mounts, supports background retry behavior, and calls `nmount()`.

## Main Responsibilities
- Parses legacy flags and modern `-o` options for protocol, version, security, retry, sizes, timeout, locking, reserved ports, and background behavior.
- Loads `nfscl` if needed.
- Handles `server:path`, `[IPv6]:path`, and deprecated `path@server` syntax.
- Resolves hosts with IPv4/IPv6 filtering and TCP/UDP selection.
- For NFSv2/v3, contacts rpcbind and mountd, validates NFS null RPC, sends `MOUNTPROC_MNT`, and extracts root filehandle plus supported auth flavor.
- For NFSv4, skips mountd and passes server address, security flavor, `nfsv4`, and `dirpath`.
- Supports background retries and waits on routing-interface changes.
- Adds successful non-v4 mounts to `PATH_MOUNTTAB`.

## Key Functions
- `getnfsargs()`: parses remote spec, resolves address, retries protocol attempts.
- `nfs_tryproto()`: probes NFS service, mountd, filehandle/security negotiation, and iovec construction.
- `rtm_ifinfo_sleep()`: sleeps until network link state changes or timeout.
- `xdr_dir()` / `xdr_fh()`: mount protocol XDR handling.
- `sec_name_to_num()` / `sec_num_to_name()`.
- `netidbytype()` / `getnetconf_cached()`.

## Dependencies And Integration
Uses ONC RPC, rpcbind, mount protocol, NFS protocol headers, `nfsv4_geterrstr`, `build_iovec`, routing sockets, `nmount()`, and `mounttab` helpers.

## Research Notes
Security flavor negotiation is explicit for NFSv3 mountd responses: if a requested flavor is not advertised, the helper sets `EAUTH`. NFSv4 warns about `soft`/`intr` because they are unsafe for v4 semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_nfs/mount_nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_nullfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_nullfs/Makefile

## Summary
Builds the `mount_nullfs` runtime helper.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mount_nullfs`.
- Links `libutil`.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_nullfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_nullfs/mount_nullfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_nullfs/mount_nullfs.c

## Summary
Mount helper for nullfs loopback mounts, supporting file or directory targets.

## Main Responsibilities
- Parses `-o` key/value mount options into iovecs.
- Resolves both target and mountpoint with `realpath()`.
- Requires target to be either regular file or directory.
- Requires mountpoint and target to have the same file type.
- Builds `nmount()` iovecs for `fstype=nullfs`, `fspath`, `target`, and `errmsg`.
- Reports kernel-provided error text.

## Research Notes
This helper is stricter than generic path resolution: it validates file-vs-directory type compatibility before calling the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_nullfs/mount_nullfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_udf/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_udf/Makefile

## Summary
Builds the `mount_udf` runtime helper.

## Main Elements
- Builds `PROG=mount_udf`.
- Links `libkiconv` and `libutil`.
- Leaves dynamic linking enabled for optional userland libiconv access.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_udf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_udf/mount_udf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_udf/mount_udf.c

## Summary
Mount helper for UDF filesystems with optional charset conversion.

## Main Responsibilities
- Parses standard mount options, verbose flag, and `-C charset`.
- Loads `udf_iconv` and registers Unicode-to-local charset conversion when requested.
- Resolves mountpoint, normalizes source device path, and forces read-only mounting.
- Builds `nmount()` iovecs for `fstype=udf`, `fspath`, `from`, UDF flags, and optional charset names.

## Research Notes
The helper states UDF filesystems are not writable and always sets `MNT_RDONLY`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_udf/mount_udf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_unionfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_unionfs/Makefile

## Summary
Builds the `mount_unionfs` runtime helper.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mount_unionfs`.
- Links `libutil`.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_unionfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_unionfs/mount_unionfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/mount_unionfs/mount_unionfs.c

## Summary
Mount helper for unionfs layered mounts.

## Main Responsibilities
- Parses `-b` deprecated below option and generic `-o` key/value options.
- Resolves uid/gid option values from names to numeric strings.
- Canonicalizes both source and union mount directory paths.
- Rejects overlapping paths where one is a subdirectory of the other.
- Builds `nmount()` iovecs for `fstype=unionfs`, `fspath`, `from`, and `errmsg`.

## Key Functions
- `subdir()`: checks path containment.
- `parse_uid()` / `parse_gid()`: resolve names or validate numeric IDs.

## Research Notes
The helper prevents recursive or self-covering union configurations by checking both path containment directions before mounting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/mount_unionfs/mount_unionfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/natd/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/natd/Makefile

## Summary
Builds the `natd` daemon.

## Main Elements
- Sets `PACKAGE=natd`.
- Builds `natd.c` and `icmp.c`.
- Links `libalias`.
- Installs `natd.8`.
- Sets `WARNS?=3`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/natd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/natd/icmp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/natd/icmp.c

## Summary
Provides ICMP “fragmentation needed” generation for `natd` when aliasing increases packet size beyond MTU.

## Main Responsibilities
- Avoids responding to non-initial fragments.
- Avoids generating ICMP errors in response to ICMP packets.
- Builds an ICMP unreachable/need-fragment message containing the original IP header plus up to 64 bits of payload.
- Computes ICMP checksum through libalias.
- Builds an IP header from the failed datagram with source/destination swapped.
- Runs the packet through inbound aliasing before sending.
- Sends the ICMP message on a raw ICMP socket.

## Key Function
- `SendNeedFragIcmp()`.

## Research Notes
The function sends only the ICMP payload via `sendto()` after preparing an IP header and aliasing it, matching the divert/raw-socket expectations used by natd.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/natd/icmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/natd/natd.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/natd/natd.c

## Summary
Implements FreeBSD `natd`, a divert-socket network address translation daemon built on `libalias`. It supports multiple aliasing instances, dynamic interface address tracking, port/protocol/address redirects, transparent proxy rules, firewall punching, verbose/syslog packet reporting, and graceful shutdown delay.

## Main Responsibilities
- Initializes one or more `struct instance` objects, each with its own `libalias` handle and divert socket configuration.
- Parses command-line and config-file options through a table-driven option system.
- Opens PF_DIVERT sockets for shared or separate inbound/outbound processing, plus optional global divert socket.
- Optionally derives alias address and MTU from an interface, including dynamic refresh through routing socket messages.
- Processes packets from divert sockets, determines direction, applies `LibAliasOut`, `LibAliasIn`, or `LibAliasOutTry`, and reinjects packets.
- Drops ignored incoming packets when configured and logs denied packets.
- Sends ICMP fragmentation-needed messages when aliased packets exceed MTU.
- Supports daemonization, pidfile writing, syslog facilities, SIGHUP module/address refresh, and delayed SIGTERM shutdown.
- Configures libalias modes and redirects: port, protocol, address, LSNAT server pools, proxy rules, Skinny port, and ipfw punch rules.

## Key Functions
- `main()`: lifecycle, socket setup, select loop.
- `DoAliasing()` and `DoGlobal()`: packet receive, aliasing, logging, reinjection.
- `SetAliasAddressFromIfName()`: sysctl route table scan for interface address/MTU.
- `HandleRoutingInfo()`: marks instances for address refresh.
- `ParseArgs()`, `ParseOption()`, `ReadConfigFile()`: option handling.
- `SetupPortRedirect()`, `SetupProtoRedirect()`, `SetupAddressRedirect()`.
- `StrToAddr()`, `StrToPort()`, `StrToPortRange()`, `StrToAddrAndPortRange()`.
- `NewInstance()`: creates or switches named libalias instance.
- `CheckIpfwRulenum()`: validates ipfw punch rule ranges.

## Dependencies And Integration
Uses PF_DIVERT sockets, PF_ROUTE sockets, raw ICMP socket, route-table sysctl, `libalias`, syslog, service/protocol databases, and ipfw default-rule sysctl.

## Research Notes
Multi-instance support is implemented with a global current instance pointer (`mip`) and current libalias handle (`mla`), so parsing and packet dispatch are stateful. Config-file parsing strips comments and trailing whitespace but requires the final line to end with a newline.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/natd/natd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/natd/natd.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/natd/natd.h

## Summary
Shared declarations and constants for `natd`.

## Main Contents
- Defines `PIDFILE` as `/var/run/natd.pid`.
- Defines packet direction constants `INPUT`, `OUTPUT`, and `DONT_KNOW`.
- Defines shutdown delay bounds.
- Declares `Quit()`, `Warn()`, and `SendNeedFragIcmp()`.
- Declares global `struct libalias *mla`.

## Research Notes
The header exposes the global libalias handle so `icmp.c` can checksum and alias generated ICMP packets consistently with the active instance.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/natd/natd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs/Makefile

## Summary
Builds the UFS `newfs` utility and defines legacy test targets.

## Main Elements
- Adds `.PATH: ${SRCTOP}/sys/geom` to build `geom_bsd_enc.c`.
- Sets `PACKAGE=ufs`.
- Builds `PROG=newfs`.
- Sources: `newfs.c`, `mkfs.c`, and `geom_bsd_enc.c`.
- Links `libufs` and `libutil`.
- Installs `newfs.8`.
- Defines a manual `test` target that runs `runtest01.sh`, `runtest00.sh`, compares against `ref.test`, and prints success.

## Research Notes
This Makefile is the build glue for the UFS filesystem creation tool; the implementation files are outside this grouped batch.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/Makefile -->