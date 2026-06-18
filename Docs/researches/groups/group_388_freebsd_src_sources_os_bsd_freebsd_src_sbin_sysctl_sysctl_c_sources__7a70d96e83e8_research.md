# Group Research: FreeBSD sysctl, tunefs, umount, veriexec, zfsbootcfg, autofs, and cd9660 subset

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/sysctl.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/sysctl.c

## Purpose
Main implementation of the FreeBSD `sysctl` userland utility. It parses command-line and file-based sysctl requests, resolves sysctl names to MIB OIDs, prints values and metadata, and sets writable leaf nodes.

## Main Elements
- `main()` handles display, assignment, all-node traversal, jail attachment, configuration file input, and filters for writable, tunable, prison, and vnet sysctls.
- `parse()` splits `name=value` or `name:value`, trims whitespace/quotes, validates leaf/writable status, parses numeric vectors or strings, performs `sysctl(3)`, and prints old/new values.
- `parsefile()` reads sysctl configuration files, strips comments outside quotes, trims whitespace, and feeds non-empty lines to `parse()`.
- `sysctl_all()` walks the sysctl tree using `CTL_SYSCTL_NEXT` or `CTL_SYSCTL_NEXTNOSKIP`.
- `show_var()` fetches name, format, type, and value, applies filters, and formats scalar, string, known opaque, raw, and hex output.
- Opaque structure printers cover `clockinfo`, `loadavg`, `timeval`, `vmtotal`, evdev `input_id`, page sizes, EFI maps, and BIOS SMAP xattrs.
- `strIKtoi()` parses temperature sysctl assignments with Celsius, Fahrenheit, Kelvin, or raw integer units for `IK` formats.
- Optional jail support attaches to a named jail before reads/writes.

## Dependencies And Integration
Uses FreeBSD sysctl metadata interfaces (`CTL_SYSCTL_NAME2OID`, `OIDFMT`, `NAME`, `OIDDESCR`, `NEXT/NEXTNOSKIP`), optional jail APIs, architecture-specific EFI/BIOS structures, evdev input IDs, and libc formatting/parsing.

## Risk Notes
Assignment paths must match kernel-reported type and size precisely. Tree walking intentionally skips `CTLFLAG_SKIP` descendants for ordinary `-a`, but metadata modes override that. File parsing is quote-aware but still line-oriented, so malformed quoted values can affect comment stripping.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/sysctl.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/sysctl.conf

## Purpose
Default example sysctl configuration file read during transition to multi-user mode.

## Main Elements
- Documents that contents are piped through `sysctl`.
- Points users to `sysctl.conf(5)`.
- Provides a commented example for `security.bsd.see_other_uids=0`.

## Dependencies And Integration
Consumed by system startup scripts rather than compiled code.

## Risk Notes
Uncommented entries here mutate kernel tunables during boot; examples are intentionally disabled by default.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/sysctl.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/tests/Makefile

## Purpose
Builds and installs the shell ATF tests for `sysctl`.

## Main Elements
- Defines `ATF_TESTS_SH=sysctl_test`.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Participates in FreeBSD’s ATF/Kyua test infrastructure.

## Risk Notes
No conditional logic; all behavior is in `sysctl_test.sh`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/tests/sysctl_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/tests/sysctl_test.sh

## Purpose
ATF regression tests for basic `sysctl` output modes and all-node traversal.

## Main Elements
- Uses stable `kern.ostype` expectations: name `kern.ostype`, value `FreeBSD`, type `string`, description `Operating system type`.
- `sysctl_aflag` runs `sysctl -ao` and fails on nonzero exit or stderr.
- `sysctl_aflag_jail` repeats `sysctl -ao` in non-vnet and vnet jails; requires root.
- Tests normal name output, `-n`, `-e`, `-t`, `-d`, `-t -d`, `-d -t`, and `-n -t -d`.
- Registers all cases in `atf_init_test_cases()`.

## Dependencies And Integration
Requires `/usr/sbin/sysctl`, ATF helpers, and root/jail support for the jail case.

## Risk Notes
The all-node tests intentionally avoid `atf_check` output capture because `sysctl -ao` can generate large output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/tests/sysctl_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/tests/Makefile

## Purpose
Top-level test makefile for `sbin` tests.

## Main Elements
- Sets `.PATH` to `${SRCTOP}/tests`.
- Enables `KYUAFILE=yes`.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Creates the Kyua test directory integration point for `sbin`.

## Risk Notes
Build orchestration only.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tunefs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/tunefs/Makefile

## Purpose
Builds the UFS tuning utility `tunefs`.

## Main Elements
- Sets `PACKAGE=ufs`, `PROG=tunefs`, and `MAN=tunefs.8`.
- Links `libufs` and `libutil`.
- Enables tests under `tests` when `MK_TESTS` is enabled.
- Includes `src.opts.mk` and `bsd.prog.mk`.

## Dependencies And Integration
Depends on FreeBSD’s UFS library and test option framework.

## Risk Notes
The build file is simple; filesystem mutation behavior lives in `tunefs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tunefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tunefs/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/tunefs/tests/Makefile

## Purpose
Builds and installs the shell ATF tests for `tunefs`.

## Main Elements
- Sets `PACKAGE=tests`.
- Defines `ATF_TESTS_SH=tunefs_test`.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Participates in FreeBSD ATF/Kyua testing.

## Risk Notes
No special logic beyond registering the shell test.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tunefs/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tunefs/tests/tunefs_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/tunefs/tests/tunefs_test.sh

## Purpose
ATF tests for toggling selected `tunefs` UFS feature flags on a temporary memory-disk filesystem.

## Main Elements
- `tunefs_setup()` creates a 16 MB malloc-backed `md(4)` device and runs `newfs`.
- `tunefs_test()` verifies an option is absent, enables it, verifies it is present via `file -s`, enables it again, disables it, and verifies repeated disable behavior.
- Test cases cover POSIX.1e ACLs, NFSv4 ACLs, soft updates without journaling, soft updates journaling, GEOM journaling, and soft-update/GEOM-journal conflict handling.
- Cleanup detaches the md device if created.
- All tests require root.

## Dependencies And Integration
Uses `mdconfig`, `newfs`, `tunefs`, `file`, ATF helpers, and UFS metadata recognition in `file(1)`.

## Risk Notes
Tests mutate a disposable memory disk only. Failure cleanup must detach the md unit to avoid resource leaks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tunefs/tests/tunefs_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tunefs/tunefs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/tunefs/tunefs.c

## Purpose
Implements `tunefs`, which changes selected layout, policy, label, and feature flags on an existing UFS filesystem.

## Main Elements
- `main()` parses options for alternate superblocks, ACLs, max blocks per cylinder group, average file size, soft updates, soft updates journaling, GEOM journaling, metadata reserve, volume label, multilabel MAC, minfree, NFSv4 ACLs, optimization preference, print-only mode, average files per directory, journal size, and TRIM.
- Opens the target through `ufs_disk_fillout()` and refuses unsafe mutations when the filesystem is unclean unless only printing is requested.
- Updates `sblock` fields such as `fs_flags`, `fs_volname`, `fs_maxbpg`, `fs_avgfilesize`, `fs_metaspace`, `fs_minfree`, `fs_optim`, and `fs_avgfpdir`.
- Enforces mutual exclusion between POSIX.1e and NFSv4 ACLs, and between soft updates and GEOM journaling.
- `journal_alloc()` creates `.sujournal`: finds an inode, allocates direct/indirect blocks, initializes inode metadata, inserts it into the root directory, and updates cylinder groups.
- `journal_clear()` clears immutable/nounlink/nodump flags from an existing journal inode so it can be removed.
- Directory helpers locate and insert `.sujournal`, including extending root directory fragments into full blocks.
- `sbdirty()` marks the filesystem unclean and needing fsck after certain partial failures.
- `printfs()` reports current tunable state and optimization/minfree warnings.

## Dependencies And Integration
Uses `libufs`, UFS/FFS on-disk structures, cylinder group allocation helpers, directory entry formats, `chkdoreload()`, and mountpoint lookup.

## Risk Notes
This utility directly mutates filesystem metadata. The clean-filesystem gate, `sbdirty()` failure handling, and journal allocation paths are the central safety controls.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/tunefs/tunefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/umbctl/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/umbctl/Makefile

## Purpose
Builds the `umbctl` utility for controlling USB MBIM network interfaces.

## Main Elements
- Adds include path `${SRCTOP}/sys/dev/usb/net`.
- Sets `PROG=umbctl`, `MAN=umbctl.8`, and `BINDIR=/sbin`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Depends on MBIM and UMB driver headers under the kernel USB network tree.

## Risk Notes
Build depends on in-tree kernel header layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/umbctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/umbctl/umbctl.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/umbctl/umbctl.c

## Purpose
Userland control utility for MBIM/UMB cellular interfaces.

## Main Elements
- Opens an IPv4 datagram socket and issues `SIOCGUMBPARAM`, `SIOCSUMBPARAM`, and `SIOCGUMBINFO` ioctls through `struct ifreq`.
- Supports direct CLI parameters and `-f config-file` parsing with `key=value` lines.
- Settable parameters include APN, username, password, PIN, PUK, and roaming allow/deny.
- Converts ASCII CLI strings to little-endian UTF-16 fields for MBIM parameter buffers.
- Converts UTF-16 status strings back to printable ASCII with replacement for non-ASCII.
- Prints state, registration mode/state, provider, dataclass, signal quality, phone number, roaming state/text, APN, speeds, firmware, and hardware info.
- `main()` accepts `-f`, `-v`, and a parsed but otherwise unused `-g`.

## Dependencies And Integration
Uses MBIM value description tables and UMB ioctl structures from `mbim.h` and `if_umbreg.h`.

## Risk Notes
Configuration file parsing is simple and line-oriented. Sensitive values such as passwords and PIN/PUK are copied into ioctl structures without extra secrecy handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/umbctl/umbctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/umount/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/umount/Makefile

## Purpose
Builds the `umount` utility.

## Main Elements
- Sets `PACKAGE=runtime`, `PROG=umount`, and `MAN=umount.8`.
- Builds `umount.c`, `vfslist.c`, and `mounttab.c`.
- Adds include paths for sibling `mount` sources and `usr.sbin/rpc.umntall`.
- Uses `.PATH` to locate shared source files.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Shares VFS list and mounttab support with related mount/rpc unmount tooling.

## Risk Notes
Build composition depends on shared source paths remaining stable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/umount/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/umount/umount.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/umount/umount.c

## Purpose
Implements the `umount` command, including individual unmounts, fstab-driven unmount-all, mount-table unmount-all, NFS cleanup RPCs, and optional md-device detach.

## Main Elements
- `main()` parses `-a`, `-A`, `-d`, `-F`, `-f`, `-h`, `-N`, `-n`, `-t`, and `-v`.
- Enforces incompatible combinations such as `-f` with `-n`, and validates `-N` forced NFS dismount use.
- `umountall()` recursively processes fstab entries so unmounts happen in reverse order while skipping root and non-mount fstab types.
- `checkname()` resolves input as fsid, mountpoint, source device, path with trailing slashes removed, deprecated NFS `host@path`, or `statfs()` fallback.
- `umountfs()` prefers unmount by fsid, falls back to path for old kernels, marks internal mount-cache entries removed, and prints verbose output.
- NFS handling detects host/path, filters by `-h`, suppresses MOUNTPROC_UMNT for NFSv4, selects tcp/udp from mount options, updates `/var/db/mounttab`, and supports `nfssvc(NFSSVC_FORCEDISM)`.
- `md_detach()` detaches backing `md(4)` devices after unmount when `-d` is set.

## Dependencies And Integration
Uses `getfsstat`, `unmount(2)`, fstab APIs, VFS type filtering helpers, NFS RPC/mount protocols, `nfssvc`, mounttab helpers, and md ioctl interfaces.

## Risk Notes
Unmount ordering and mount identity resolution are correctness-critical. NFS RPC cleanup only occurs when this is the last matching mount and the operation is not forced.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/umount/umount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/Makefile

## Purpose
Builds the `veriexec` manifest-loading and control utility.

## Main Elements
- Sets `PROG=veriexec`, `MAN=veriexec.8`.
- Builds `veriexec.c`, `manifest_parser.y`, and `manifest_lexer.l`.
- Links `veriexec`, `secureboot`, and `bearssl`.
- Leaves `NO_SHARED` empty.
- Adds current directory include path and parser/lexer warning suppressions.

## Dependencies And Integration
Requires libveriexec, libsecureboot, BearSSL, yacc, and lex integration through FreeBSD make rules.

## Risk Notes
Parser and lexer warning suppressions are target-specific; generated code behavior depends on yacc/lex output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/manifest_lexer.l -->
# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/manifest_lexer.l

## Purpose
Lex scanner for signed Veriexec manifest contents.

## Main Elements
- Tracks `lineno` and beginning-of-line state.
- Returns `PATH` for the first token on a line and `STRING` for subsequent tokens.
- Recognizes `=`, newline as `EOL`, whitespace, comments, and invalid characters.
- Supports version-gated `#>NUMBER` directives by treating the remainder of the line as a comment when parser version is too old.
- `manifest_open()` opens manifest content from an in-memory signed buffer via `fropen()`, resets lexer/parser state, and records the file name for diagnostics.
- `read_string_buf()` feeds bytes from the signed buffer to stdio.
- `yyerror()` reports `file: line: message at token`.

## Dependencies And Integration
Used by `manifest_parser.y`; receives verified manifest text from `veriexec.c`.

## Risk Notes
The lexer scans trusted-after-verification content from memory. Tokenization is simple and does not support quoted whitespace in fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/manifest_lexer.l -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/manifest_parser.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/manifest_parser.y

## Purpose
Yacc parser for Veriexec manifest lines, converting path/fingerprint/flag records into kernel Veriexec load ioctls.

## Main Elements
- Grammar parses `path attributes eol`, recovering by skipping to the next fingerprint on parse errors.
- Attributes include hash fields (`sha1`, `sha256`, `sha384`, `sha512`), `label`, and octal `mode`.
- Flags include `indirect`, `no_ptrace`, `trusted`, and optionally `no_fips`.
- Relative manifest paths are converted to absolute paths, optionally prefixed by `Cdir`.
- `convert()` transforms fixed-length hex fingerprints into binary digests.
- `do_ioctl()` classifies non-executable paths as `VERIEXEC_FILE`, applies forced flags, and sends `VERIEXEC_SIGNED_LOAD` or label load ioctls.
- `manifest_parser_init()` invalidates the current fingerprint state between manifests.

## Dependencies And Integration
Uses Veriexec ioctl ABI, libsecureboot digest size definitions, BearSSL digest constants fallback, optional label support, and globals from `veriexec.c`.

## Risk Notes
Fingerprint conversion assumes the input string is long enough for the declared digest size. Missing fingerprint type causes a manifest entry to be skipped.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/manifest_parser.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/veriexec.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/veriexec.c

## Purpose
Main `veriexec` utility for querying/modifying Veriexec state, checking path status, and loading signed manifests.

## Main Elements
- Opens `_PATH_DEV_VERIEXEC` for ioctls.
- `veriexec_load()` verifies a signed manifest via `verify_signed()`, opens verified content for the lexer, and runs `yyparse()`.
- `veriexec_state_query()` maps partial state names to query bits: active, enforce, loaded, locked.
- `veriexec_state_modify()` maps state commands to Veriexec ioctls: active, enforce, getstate, lock.
- Optional `veriexec_check_labels()` prints labels for paths when label support is compiled in.
- `veriexec_check_paths()` exits nonzero when any path fails Veriexec checking.
- `main()` handles `-C`, `-h`, `-i`, optional `-l`, `-S`, `-v`, `-x`, and `-z`.
- `-z debug` supports `off` or numeric mac_veriexec debug level.
- Initializes the trust store with `ve_trust_init()` before manifest loading.

## Dependencies And Integration
Uses `/dev/veriexec`, libveriexec, libsecureboot, syslog, optional Veriexec version ioctl, and the generated manifest parser.

## Risk Notes
Manifests must verify before parsing. State-command matching uses prefix comparisons, so ambiguous prefixes are rejected only when multiple bits are set in query mode.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/veriexec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/veriexec.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/veriexec.h

## Purpose
Shared declarations for Veriexec source, lexer, and parser.

## Main Elements
- Includes Veriexec ioctl definitions.
- Declares shared globals: `dev_fd`, `parser_version`, `ForceFlags`, `Verbose`, `VeriexecVersion`, and `Cdir`.
- Defines `VERBOSE(n, x)` debug-print macro.
- Declares `manifest_open()`, `manifest_parser_init()`, `yyparse()`, and `yyin`.

## Dependencies And Integration
Included by the lexer, parser, and main program.

## Risk Notes
Parser/lexer behavior depends on shared mutable globals initialized by `veriexec.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/veriexec/veriexec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/zfsbootcfg/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/zfsbootcfg/Makefile

## Purpose
Builds the `zfsbootcfg` utility.

## Main Elements
- Sets `PACKAGE=zfs`, `PROG=zfsbootcfg`, and `MAN=zfsbootcfg.8`.
- Links `libzfsbootenv`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Part of FreeBSD’s ZFS package utilities.

## Risk Notes
Build depends on libzfsbootenv availability.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/zfsbootcfg/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/zfsbootcfg/zfsbootcfg.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/zfsbootcfg/zfsbootcfg.c

## Purpose
Manipulates ZFS boot environment boot configuration data through libzfsbootenv.

## Main Elements
- `add_pair()` fetches a bootenv nvlist, converts a string value to the requested nvpair type, adds the pair, writes the nvlist back, and frees it.
- Supports string, signed/unsigned 8/16/32/64-bit integers, byte, and boolean-value types.
- `delete_pair()` removes a key from a bootenv nvlist and writes it back.
- `main()` parses `-d`, `-k`, `-n`, `-p`, `-t`, `-v`, and `-z`.
- Defaults pool name from `kenv("vfs.root.mountfrom")` when `-z` is omitted and root is ZFS.
- If key is missing or key is `command`, uses `lzbe_set_boot_device()`; otherwise updates a named nvlist pair.
- Without mutations or `-p`, prints the current boot device in `zfs:<dataset>:` form.
- `-p` prints the bootenv or selected nvlist.

## Dependencies And Integration
Uses kernel environment, libzfsbootenv nvlist helpers, and ZFS bootenv conventions.

## Risk Notes
Value parsing checks full-string numeric conversion. Boolean parsing has sequential case-insensitive checks for YES/NO/true/false.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/zfsbootcfg/zfsbootcfg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs.c

## Purpose
Core kernel implementation for FreeBSD autofs device state, request queue, trigger coordination, caching, tunables, and daemon ioctls.

## Main Elements
- Defines `M_AUTOFS`, UMA zones for requests and nodes, `/dev/autofs` cdev operations, and global `autofs_softc`.
- Sysctls/tunables control debug output, mount-on-stat behavior, daemon timeout, cache lifetime, retry attempts/delay, and signal interruptibility.
- `autofs_init()` allocates softc, initializes queues/locks/cv/zones, and creates `/dev/autofs`.
- `autofs_uninit()` refuses unload while the device is open and destroys device/zones/softc.
- `autofs_ignore_thread()` prevents automountd and descendants from recursively triggering autofs, using the session ID of the daemon that opened the device.
- `autofs_trigger_one()` creates or joins a request, starts timeout task, waits for daemon completion, handles signals, applies positive caching, and cleans up refcounted request state.
- `autofs_trigger()` retries failed triggers according to tunables except for signal interruption.
- `autofs_ioctl_request()` gives automountd the next pending request and records daemon session ID.
- `autofs_ioctl_done_101()` and `autofs_ioctl_done()` complete requests and wake blocked threads.
- Timeout task completes stuck requests with `ETIMEDOUT`.

## Dependencies And Integration
Integrates with FreeBSD VFS, cdev, taskqueue, callout, UMA, sysctl, signal mask, and automountd ioctl protocol.

## Risk Notes
Correctness depends on `sc_lock`, request refcounts, timeout cancellation/draining, and avoiding daemon self-trigger recursion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs.h

## Purpose
Internal kernel header for autofs structures, macros, globals, and function prototypes.

## Main Elements
- Defines `VFSTOAUTOFS()` and debug/warning macros.
- Defines lock helper macros for `autofs_mount`.
- `struct autofs_node` stores tree linkage, name, synthetic file number, parent/children, vnode, vnode lock, cache state, wildcard state, callout, retries, and ctime.
- `struct autofs_mount` stores root node, mount pointer, lock, map/from, mountpoint, options, prefix, and last file number.
- `struct autofs_request` stores daemon request identity, copied map/path/key/options fields, timeout task, completion state, wildcard state, and refcount.
- `struct autofs_softc` stores device, cv, global lock, request queue, daemon-open state/session, and request ID counter.
- Declares node, trigger, cache, init/uninit, and vnode helper APIs.
- Declares RB tree prototype for child nodes.

## Dependencies And Integration
Used by autofs core, VFS ops, and vnode ops.

## Risk Notes
This is the contract for autofs lock ordering and lifetime management.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_ioctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_ioctl.h

## Purpose
Public ioctl ABI between the kernel autofs filesystem and `automountd`.

## Main Elements
- Defines `AUTOFS_PATH` as `/dev/autofs`.
- `struct autofs_daemon_request` carries request ID, map/from, full path, prefix, key, and mount options.
- `struct autofs_daemon_done_101` preserves compatibility with FreeBSD 10.1-era automountd completion format.
- `struct autofs_daemon_done` adds wildcard information and reserved spare fields.
- Defines `AUTOFSREQUEST`, `AUTOFSDONE101`, and `AUTOFSDONE` ioctl numbers.

## Dependencies And Integration
Included by kernel autofs and userland automount daemon code.

## Risk Notes
Field sizes are fixed at `MAXPATHLEN`; ABI compatibility is explicit for older daemon completion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_vfsops.c

## Purpose
VFS operation implementation for mounting, unmounting, rooting, and statfs on autofs mounts.

## Main Elements
- Accepts mount options `from`, `master_options`, `master_prefix`, and required `fspath`.
- Update mounts flush autofs cache.
- New mounts allocate `struct autofs_mount`, copy map/prefix/options/mountpoint data, initialize lock and root node, set lookup-shared flag, and set mounted-from text.
- `autofs_unmount()` flushes vnodes, completes outstanding requests for the mount with `ENXIO`, waits for them to drain, then deletes the node tree.
- `autofs_root()` returns the root autofs vnode.
- `autofs_statfs()` reports synthetic zero-capacity filesystem statistics.
- Registers `VFS_SET(..., autofs, VFCF_SYNTHETIC | VFCF_NETWORK)`.

## Dependencies And Integration
Uses autofs node helpers, VFS mount option APIs, vnode flushing, and module registration.

## Risk Notes
Unmount must prevent new triggers, wake existing trigger waiters, and delete nodes only after vnodes are gone.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_vnops.c

## Purpose
Vnode operations and synthetic node management for autofs directories.

## Main Elements
- `autofs_getattr()` returns synthetic directory attributes and can trigger mounts on `stat(2)` when configured.
- `autofs_trigger_vn()` drops the vnode lock, holds a reference, triggers automountd, relocks, and returns the mounted filesystem root if a mount appeared.
- `autofs_lookup()` handles `.`, `..`, cache checks, automount triggers, wildcard/dynamic entries, and synthetic child lookup/creation behavior.
- `autofs_mkdir()` permits only automountd descendants to create synthetic directories.
- `autofs_readdir()` triggers as needed, emits `.`, `..`, and child directory entries, and validates directory offsets.
- `autofs_reclaim()` clears vnode linkage but leaves node freeing to unmount/node deletion.
- VOP vector disables unsupported mutation operations except daemon-controlled mkdir.
- `autofs_node_new()`, `autofs_node_find()`, `autofs_node_delete()`, and `autofs_node_vn()` manage RB-tree nodes, callouts, locks, and vnode creation/reuse.

## Dependencies And Integration
Uses VFS lookup, vnode locking, `vn_vget_ino_gen`, mounted-here transitions, dirent formatting, RB trees, and autofs trigger APIs.

## Risk Notes
The lock dance around triggering is critical because the daemon may mount over the vnode while lookup/stat/readdir waits.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_bmap.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_bmap.c

## Purpose
Maps cd9660 logical file blocks to device blocks for VFS/buffer-cache consumers.

## Main Elements
- Returns the underlying device buffer object when requested.
- Computes physical block number from `iso_start + logical block` shifted by filesystem block size.
- Calculates forward readahead run length capped by `MAXBSIZE`.
- Reports no backward run.

## Dependencies And Integration
Used by cd9660 vnode operations and buffer cache for ISO file extents.

## Risk Notes
Assumes cd9660 files are contiguous extents, matching ISO 9660 layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_iconv.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_iconv.c

## Purpose
Declares cd9660 iconv integration.

## Main Elements
- Includes kernel iconv and mount/module headers.
- Uses `VFS_DECLARE_ICONV(cd9660)`.

## Dependencies And Integration
Provides filesystem-level charset conversion hooks used by Joliet filename handling.

## Risk Notes
No runtime logic in this file; behavior depends on iconv support and callers in cd9660 utilities.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_lookup.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_lookup.c

## Purpose
Implements directory component lookup and directory-block reading for cd9660.

## Main Elements
- `cd9660_lookup()` searches ISO directory records for the requested component, including `.` and `..`.
- Supports associated files via leading `=` for non-RRIP filesystems.
- Uses cached `i_diroff` for repeated lookups and may perform a two-pass search.
- Handles default ISO/Joliet name comparison through `isofncmp()`.
- Handles Rock Ridge names and relocated directory links through `cd9660_rrip_getname()`.
- Returns `EROFS` for create/rename attempts on missing entries.
- Copies directory records before vnode lookup when needed to avoid vnode/buffer lock-order reversal.
- Uses `vn_vget_ino_gen()` for `..` deadlock avoidance.
- Inserts positive and negative namecache entries when requested.
- `cd9660_blkatoff()` reads the directory block for an offset and ensures `b_blkno` is mapped for inode-number calculations.

## Dependencies And Integration
Uses ISO directory format helpers, Rock Ridge helpers, vnode cache, buffer cache, and cd9660 vnode retrieval.

## Risk Notes
Lookup relies on strict directory record validation to avoid malformed media crossing block boundaries or using illegal record lengths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_mount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_mount.h

## Purpose
Defines user-visible mount arguments and mount flags for ISO 9660/cd9660 filesystems.

## Main Elements
- `struct iso_args` includes device path, export args, uid/gid, file and directory masks, flags, starting sector, and optional disk/local charset names.
- Flags include disabling Rock Ridge, generation numbers, extended attributes, disabling/allowing broken Joliet, kernel iconv conversion, and uid/gid overrides.

## Dependencies And Integration
Used by mount code and userland mount_cd9660 ABI.

## Risk Notes
This header is part of the mount ABI; field or flag changes affect userland compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_node.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_node.c

## Purpose
Implements cd9660 inode lifecycle helpers and default ISO attribute/timestamp conversion.

## Main Elements
- `cd9660_inactive()` recycles vnodes whose ISO mode is cleared.
- `cd9660_reclaim()` removes the vnode from the VFS hash and frees the `iso_node`.
- `cd9660_defattr()` derives file type, mode, link count, uid, and gid from ISO directory records or extended attributes.
- `cd9660_deftstamp()` derives atime/mtime/ctime from extended attributes or directory-record timestamps.
- `cd9660_tstamp_conv7()` converts 7-byte ISO timestamps with timezone adjustment and pre-1970 clamping.
- `cd9660_tstamp_conv17()` converts 17-byte timestamps by feeding normalized fields into the 7-byte converter.
- `isodirino()` computes an inode number from extent plus extended attribute length.

## Dependencies And Integration
Used by VFS vnode construction, lookup, and Rock Ridge fallback/default logic.

## Risk Notes
Timestamp conversion tolerates unreliable timezone fields by accepting only a bounded offset range.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_node.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_node.h

## Purpose
Defines cd9660 in-memory node structures and vnode-operation prototypes.

## Main Elements
- Defines `doff_t` for directory offsets.
- `ISO_RRIP_INODE` stores POSIX-like attributes: times, mode, uid, gid, link count, and device number.
- `struct iso_node` stores vnode, inode number, mount pointer, lockf head, lookup offsets, extent, size, data start, and attributes.
- Defines `VTOI()` and `ITOV()` conversion macros.
- Declares malloc types and cd9660 lookup, inactive, reclaim, bmap, block-at-offset, default attribute, and timestamp functions.

## Dependencies And Integration
Included by cd9660 vnode, lookup, node, and bmap code.

## Risk Notes
`iso_node` encodes the relationship between ISO directory records, file extents, and VFS vnode identity.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_rrip.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_rrip.c

## Purpose
Implements Rock Ridge Interchange Protocol parsing for cd9660 POSIX metadata, alternate names, symlinks, relocated directories, devices, timestamps, continuation areas, and extension detection.

## Main Elements
- Uses table-driven SUSP/RRIP record scanning via `cd9660_rrip_loop()`.
- Handles `PX` attributes, `TF` timestamps, `PN` device numbers, `RR` field masks, `CE` continuations, `ST` stop records, and `ER` extension references.
- `cd9660_rrip_slink()` builds symlink targets from component records including current, parent, root, volume root, host, and continuation components.
- `cd9660_rrip_altname()` builds Rock Ridge alternate names and supports continuation.
- Default handlers fall back to ISO attributes, timestamps, and transformed ISO names when required RRIP fields are missing.
- `cd9660_rrip_pclink()` handles child/parent relocated directory links.
- `cd9660_rrip_reldir()` hides relocated directory entries from normal lookup by clearing output length/fields.
- `cd9660_rrip_cont()` records continuation block, offset, and length; the loop validates continuation bounds before reading.
- Public entry points: `cd9660_rrip_analyze()`, `cd9660_rrip_getname()`, `cd9660_rrip_getsymname()`, and `cd9660_rrip_offset()`.

## Dependencies And Integration
Works with ISO directory records, cd9660 node defaults, iconv-aware filename conversion, jail-aware hostname retrieval, and buffer-cache reads from the device vnode.

## Risk Notes
Malformed media handling depends on SUSP length/version validation and continuation bounds checks against volume size and logical block size.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_rrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_rrip.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_rrip.h

## Purpose
Defines on-disc Rock Ridge and SUSP record layouts consumed by `cd9660_rrip.c`.

## Main Elements
- Defines `ISO_SUSP_HEADER`.
- Defines RRIP structures for POSIX attributes, device numbers, symlink components, symlinks, alternate names, child/parent links, relocated directories, timestamps, flags, extension references, SP offset, and continuation pointers.
- Defines symlink component flags such as continue, current, parent, root, volume root, and host.
- Defines timestamp format and field flags.
- Defines `ISO_RRIP_SLSIZ`.

## Dependencies And Integration
Layout definitions map directly onto bytes inside ISO system-use areas.

## Risk Notes
Packed on-media layout assumptions are central; callers validate record lengths before using these structures.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_rrip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_util.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_util.c

## Purpose
Filename character, comparison, and translation utilities for ISO 9660, Joliet, and optional iconv conversion.

## Main Elements
- `isochar()` reads one ISO/Joliet character, using iconv when enabled or simple UCS-2 fallback for Joliet.
- `isofncmp()` compares a user pathname component with an ISO filename, case-folding plain ISO uppercase and allowing omitted `;version` suffixes.
- `isofntrans()` translates ISO directory names into visible names, optionally preserving original case/version and adding the associated-file prefix.
- `sgetrune()` obtains one local filename rune, using iconv when enabled or one-byte fallback otherwise.

## Dependencies And Integration
Used by lookup, readdir, and Rock Ridge default-name logic; depends on cd9660 mount flags and iconv handles.

## Risk Notes
Name comparison and translation differ by Joliet/iconv flags, so mount options affect path lookup semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_util.c -->