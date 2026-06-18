# Group Research: group_362_freebsd_src_sources_os_bsd_freebsd_src_sbin_Makefile_sources_os_bsd__546c6b77b6ea

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/Makefile

## Purpose
Top-level FreeBSD `sbin` build directory makefile. It enumerates base system administrative utilities built under `/sbin`.

## Main Elements
- Includes `src.opts.mk` and `bsd.arch.inc.mk` for build option and architecture conditionals.
- Defines core `SUBDIR` entries such as `adjkerntz`, `camcontrol`, `fsck`, `ifconfig`, `mount`, `newfs`, `route`, `sysctl`, and `umount`.
- Adds optional subdirectories based on `MK_*` knobs: networking, CCD, HAST, IPFilter, IPFW, OpenSSL, PF, quotas, routed, Veriexec, ZFS, and tests.
- Sets `SUBDIR_PARALLEL=` to enable subdir parallelism under FreeBSD bmake semantics.
- Includes `bsd.prog.mk` and `bsd.subdir.mk`.

## Dependencies And Integration
This is build orchestration only. It ties `sbin` utilities into the FreeBSD source tree option framework and controls whether ZFS-dependent `bectl` and `zfsbootcfg` are included.

## Risk Notes
Build membership depends on `MK_*` options. Missing a conditional here silently excludes utilities from system builds.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/Makefile.inc -->
# File Research: sources/os/bsd/freebsd-src/sbin/Makefile.inc

## Purpose
Shared makefile fragment for programs under `sbin`.

## Main Elements
- Includes `src.opts.mk`.
- Defaults `BINDIR` to `/sbin`.
- Sets `NO_SHARED=YES` when `MK_DYNAMICROOT == "no"`.

## Dependencies And Integration
Consumed by descendant program makefiles through FreeBSD make include conventions. It enforces static linking behavior for non-dynamic-root builds.

## Risk Notes
Affects linkage mode broadly across `sbin`; dynamic-root option changes can alter binary dependency expectations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/adjkerntz/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/adjkerntz/Makefile

## Purpose
Builds the `adjkerntz` runtime utility.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=adjkerntz`.
- Installs `adjkerntz.8`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Relies on the default single-source FreeBSD program build rule for `adjkerntz.c`.

## Risk Notes
No special libraries or flags are specified; behavior is almost entirely in the C source.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/adjkerntz/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/adjkerntz/adjkerntz.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/adjkerntz/adjkerntz.c

## Purpose
Adjusts kernel time and timezone state when the machine uses a local-time CMOS clock, indicated by `/etc/wall_cmos_clock`. It handles boot-time initialization and later adjustment calls across timezone/DST changes.

## Main Elements
- `main()`: parses `-i`, `-a`, and `-s`; checks wall-clock marker; daemonizes for initial mode; loops on signal-triggered adjustment.
- Uses `sysctlbyname()` for `machdep.adjkerntz`, `machdep.disable_rtc_set`, and `machdep.wall_cmos_clock`.
- Computes local-to-GMT offset using `localtime()`, `mktime()`, `tm_gmtoff`, current kernel offset, and `gettimeofday()` timezone fields.
- Handles DST edge cases by recalculating final offset and retrying nonexistent local times in sleep mode.
- Uses `settimeofday()` to clear obsolete timezone state and adjust wall-clock-derived kernel time.
- Temporarily disables RTC writes while changing kernel time/offset in paths where RTC should not be rewritten.
- `fake()` is a no-op signal handler used with `sigsuspend()`.
- `usage()` prints init/adjustment invocation forms and exits.

## Dependencies And Integration
Run from rc/periodic system paths. Depends on kernel machine-dependent time sysctls, `/etc/wall_cmos_clock`, libc timezone rules, syslog, and process signals.

## Behavioral Notes
The program has a timing-sensitive critical section around reading time, computing offset, setting system time, updating kernel offset, and restoring RTC-write behavior. In initial mode it can daemonize and wait for `SIGTERM`-driven adjustment cycles.

## Risk Notes
This utility changes system time and kernel RTC behavior. Failures after disabling RTC writes but before restoration are explicitly called out as risky in comments.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/adjkerntz/adjkerntz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/adjkerntz/pathnames.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/adjkerntz/pathnames.h

## Purpose
Defines path constants for `adjkerntz`.

## Main Elements
- Includes `<paths.h>`.
- Defines `_PATH_CLOCK` as `/etc/wall_cmos_clock`.

## Dependencies And Integration
`adjkerntz.c` uses `_PATH_CLOCK` as the marker file that enables wall CMOS clock behavior.

## Risk Notes
Changing this path changes system policy detection for local-time RTC handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/adjkerntz/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/bectl/Makefile

## Purpose
Builds the ZFS boot environment control utility `bectl`.

## Main Elements
- Includes `src.opts.mk`.
- Sets `PACKAGE=zfs`, `PROG=bectl`, and `MAN=bectl.8`.
- Builds `bectl.c`, `bectl_jail.c`, and `bectl_list.c`.
- Links against `be`, `jail`, `nvpair`, `spl`, `util`, `zfsbootenv`, and `pthread`.
- Adds ZFS/OpenZFS include paths and compatibility defines.
- Enables tests via `HAS_TESTS=yes` and `SUBDIR.${MK_TESTS}+= tests`.

## Dependencies And Integration
Tightly coupled to FreeBSD libbe and in-tree OpenZFS headers/configuration.

## Risk Notes
Build correctness depends on ZFS source tree include paths and generated `zfs_config.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/bectl.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/bectl/bectl.c

## Purpose
Main command dispatcher for `bectl`, implementing boot environment lifecycle commands backed by libbe.

## Main Elements
- `usage()`: prints all subcommands and options.
- `command_map`: maps command names to handlers, libbe error-printing behavior, and history logging policy.
- Command handlers:
  - `activate`: permanent, temporary next-boot, or temporary-activation reset.
  - `create`: creates BEs from active BE, named BE, snapshot, recursive clone, snapshot-only form, or empty BE.
  - `destroy`: supports force/origin flags and warns when non-auto origin snapshots are left intact.
  - `export` / `import`: stream BE data over stdout/stdin, rejecting terminal use.
  - `mount` / `unmount`: mount deeply, optionally at a caller-provided path, with force unmount.
  - `rename`: renames a BE.
  - `check`: silent initialization probe.
- `save_cmdline()`: builds a bounded history string for ZFS history logging.
- `main()`: parses global `-h` and `-r`, initializes libbe, dispatches command, logs successful mutating commands, and closes libbe.

## Dependencies And Integration
Uses `libbe`, `libutil`, nvlist properties, ZFS history logging, and helpers exported by `bectl_jail.c` and `bectl_list.c`.

## Risk Notes
Most commands mutate ZFS datasets or boot configuration. Import/export intentionally use raw file descriptors, so terminal checks are important safety gates.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/bectl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/bectl.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/bectl/bectl.h

## Purpose
Shared declarations for `bectl` source files.

## Main Elements
- Declares `usage()`.
- Declares jail, unjail, and list command handlers.
- Exposes global `libbe_handle_t *be`.

## Dependencies And Integration
Included by `bectl.c`, `bectl_jail.c`, and `bectl_list.c`.

## Risk Notes
The global libbe handle keeps command modules simple but makes handlers depend on `main()` initialization order.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/bectl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/bectl_jail.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/bectl/bectl_jail.c

## Purpose
Implements `bectl jail` and `bectl unjail` support: mounting a boot environment, creating a jail rooted there, optionally running a command, and cleaning up.

## Main Elements
- Jail parameter management:
  - `jailparam_add()`, `jailparam_del()`, `jailparam_addarg()`, `jailparam_delarg()`.
  - Blocks dangerous caller-supplied jail params including `command`, `exec.start`, `persist`, and `nopersist`.
- `build_jailcmd()`: constructs `/usr/sbin/jail -c` argv from nvlist params and optional command, defaulting interactive mode to `/bin/sh`.
- `bectl_cmd_jail()`: parses `-b`, `-o`, `-U`, `-u`; mounts the BE; sets default hostname/path; forks and execs `jail`; optionally removes jail and unmounts BE.
- `bectl_jail_cleanup()`: removes jail and unmounts non-ZFS filesystems beneath the BE path.
- `bectl_search_jail_paths()` / `bectl_locate_jail()`: find jails by jid/name or by matching mounted BE path.
- `bectl_cmd_unjail()`: locates jail, verifies its path belongs to a mounted BE, removes jail, and unmounts.

## Dependencies And Integration
Uses libjail, `jail_getv()`, `jail_getid()`, `jail_remove()`, filesystem mount table inspection, and libbe mount state.

## Risk Notes
Cleanup walks mountpoints beneath the BE path and unmounts non-ZFS filesystems. Jail parameter filtering prevents callers from overriding command/persist semantics that would break lifecycle control.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/bectl_jail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/bectl_list.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/bectl/bectl_list.c

## Purpose
Implements `bectl list`, formatting boot environment, dataset, snapshot, active, mount, space, and creation-time information.

## Main Elements
- `struct printc`: carries column widths and display mode flags.
- `get_origin_props()`: fetches properties for a BE origin snapshot/dataset.
- `dataset_space()`: fetches `used` space for an origin dataset, truncating snapshot names as needed.
- `print_info()`: prints one BE/dataset/snapshot row, including active flags `N`, `R`, `T`, mountpoint, computed space, and creation time.
- `print_snapshots()`: prints snapshots for a dataset.
- `print_headers()`: computes column widths and prints headers unless script mode is selected.
- `prop_list_sort()`: sorts nvlist boot environments by string or numeric properties, supporting reverse order.
- `bectl_cmd_list()`: parses `-a`, `-D`, `-H`, `-s`, `-c`, `-C`; fetches BE props; sorts; prints rows.

## Dependencies And Integration
Uses libbe property-list APIs and nvlist iteration. Output feeds humans by default and scripts with `-H`.

## Risk Notes
Formatting depends on string properties returned by libbe. `-D` space composition is disabled when `-a` or `-s` expands rows, avoiding misleading combined totals.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/bectl_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/bectl/tests/Makefile

## Purpose
Registers shell ATF tests for `bectl`.

## Main Elements
- Sets `PACKAGE=tests`.
- Adds `bectl_test` to `ATF_TESTS_SH`.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Installs/runs `bectl_test.sh` through the FreeBSD ATF test framework.

## Risk Notes
No logic beyond test registration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/tests/bectl_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/bectl/tests/bectl_test.sh

## Purpose
ATF shell test suite for `bectl`, exercising real ZFS pools backed by sparse disk images.

## Main Elements
- Setup helpers:
  - Generates a temporary zpool name.
  - Creates sparse disk image, zpool, `ROOT`, and default BE datasets.
  - Creates deep BE layouts with child `/usr` dataset.
  - Destroys the zpool during cleanup.
- Test cases:
  - `bectl_create`: standard, snapshot, snapshot-derived, recursive, empty BE, and invalid option combinations.
  - `bectl_destroy`: destroy behavior, origin handling, clone chains, snapshot destruction with clones.
  - `bectl_export_import`: BE stream export/import and post-destroy checks.
  - `bectl_list`: verifies created/destroyed BEs appear and disappear.
  - `bectl_mount`: both `unmount` and `umount` aliases.
  - `bectl_rename`: dataset rename visibility.
  - `bectl_jail`: batch and command jails, numeric BE names, explicit jid/name/path, `ujail`/`unjail`, and cleanup behavior.
  - `bectl_promotion`: activation promotes clone chains out of clone status.
  - `bectl_destroy_bootonce`: destroying a bootonce BE clears `zfsbootcfg`.
  - `bectl_rename_bootonce`: renaming a bootonce BE updates `zfsbootcfg`.
- Skips known CI/problem architectures `i386` and `armv7` for referenced PRs.
- Requires root, ZFS module, sparse-file support, and for jail tests `/rescue/rescue`.

## Dependencies And Integration
Uses ATF, `zpool`, `zfs`, `bectl`, `zfsbootcfg`, `jail`, `jls`, sparse files, and root privileges.

## Risk Notes
Tests create and destroy zpools with generated names. Cleanup is defensive, especially for jails left behind after failures.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bectl/tests/bectl_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bsdlabel/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/bsdlabel/Makefile

## Purpose
Builds deprecated BSD disklabel utility `bsdlabel`.

## Main Elements
- Adds `.PATH` to `${SRCTOP}/sys/geom`.
- Installs `disktab` config.
- Builds `bsdlabel` from `bsdlabel.c` and `geom_bsd_enc.c`.
- Installs `bsdlabel.8`.
- On i386/amd64, creates `disklabel` hardlink and manpage alias.
- Links against `libgeom`.

## Dependencies And Integration
Bridges userland utility code with GEOM disklabel encoding helpers.

## Risk Notes
Only i386/amd64 get historical `disklabel` aliases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bsdlabel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bsdlabel/bsdlabel.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/bsdlabel/bsdlabel.c

## Purpose
Reads, displays, edits, restores, writes, and boot-code-installs BSD disk labels. It prints a deprecation warning and directs users toward `gpart`.

## Main Elements
- `main()`: parses `-A`, `-B`, `-b`, `-e`, `-f`, `-m`, `-n`, `-R`, `-r`, `-w`; resolves GEOM device paths; selects operation.
- Operations:
  - `READ`: read and display label.
  - `EDIT`: write label to temp file, invoke editor, parse result, write back.
  - `RESTORE`: parse ASCII protofile and write.
  - `WRITE`: generate label from `auto` or disktab type.
  - `WRITEBOOT`: install boot code while preserving/updating label.
- Label handling:
  - `readlabel()` reads boot area, decodes little-endian disklabel, handles absolute partition offsets.
  - `writelabel()` computes magic/checksum, optionally reads boot code, encodes label into boot area, and writes `bbsize` bytes.
  - `getvirginlabel()` creates an auto label from media size, sector size, and firmware geometry ioctls.
  - `fixlabel()` creates a default `a` partition if no non-raw partitions exist.
- ASCII handling:
  - `display()` emits editable text form.
  - `getasciilabel()` parses label fields and partition lines.
  - `getasciipartspec()` parses partition size, offset, fstype, and FFS/LFS fields.
  - `checklabel()` fills defaults, expands `*`, `%`, and K/M/G/T size suffixes, assigns offsets, checks bounds and overlaps.
- Editor support:
  - `edit()` loops until a valid edit is written or user declines.
  - `editit()` drops effective uid/gid to real ids before invoking `$EDITOR` or `vi`.

## Dependencies And Integration
Uses `libgeom` for provider paths, media geometry, and GEOM class detection; `geom_bsd_enc.c` for label encode/decode; `<sys/disklabel.h>` for structures and constants; `/boot/boot` as default boot code; `/tmp/EdDk.XXXXXXXXXX` for edits.

## Behavioral Notes
Requires `-m i386` or `-m amd64` to set label sector/offset and boot block size. Supports file mode with `-f`, where regular files are treated as disk images.

## Risk Notes
Writes raw boot block areas and partition metadata. `-n` suppresses writes and prints the would-be label. It refuses disks larger than `2^32-1` sectors and caps partitions at 8 due to the local `MAXPARTITIONS` setting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bsdlabel/bsdlabel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bsdlabel/pathnames.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/bsdlabel/pathnames.h

## Purpose
Path constants for `bsdlabel`.

## Main Elements
- Includes `<paths.h>`.
- Defines `_PATH_BOOTDIR` as `/boot`.
- Defines `PATH_TMPFILE` as `/tmp/EdDk.XXXXXXXXXX`.

## Dependencies And Integration
`bsdlabel.c` uses `PATH_TMPFILE` for editor-backed label edits. `_PATH_BOOTDIR` documents boot path convention, though the source directly defaults boot code to `/boot/boot`.

## Risk Notes
Tempfile path affects where editable disklabel prototypes are created.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/bsdlabel/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/Makefile

## Purpose
Builds `camcontrol`, the CAM storage control utility.

## Main Elements
- Builds many command modules: `camcontrol.c`, `attrib.c`, `depop.c`, `epc.c`, `fwdownload.c`, `modeedit.c`, `persist.c`, `progress.c`, `timestamp.c`, `util.c`, and `zone.c`.
- Pulls NVMe helper sources from `sbin/nvmecontrol` and `sys/dev/nvme`.
- Adds include paths for NVMe control and `libnvmf`.
- Lowers warnings to 3 on ARM due to a noted build issue.
- Links `cam`, `nvmf`, `sbuf`, and `util`.
- Installs `camcontrol.8`.

## Dependencies And Integration
Combines SCSI, ATA, NVMe, and NVMf support under one utility.

## Risk Notes
This makefile includes sources from outside the local directory, so API drift in `nvmecontrol` helpers can affect `camcontrol`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/attrib.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/attrib.c

## Purpose
Implements SCSI READ ATTRIBUTE support for `camcontrol`.

## Main Elements
- Maps element types, read service actions, and output format flags from strings to SCSI constants.
- `scsiattrib()` parses options for attribute number, cache flag, element address/type, logical volume, partition, service action, and output format.
- Sends `scsi_read_attribute()` through CAM.
- Decodes returned data for:
  - Attribute values via `scsi_attrib_sbuf()`.
  - Supported/available attribute lists.
  - Partition and logical-volume lists.
- Write attribute path is present in option parsing but explicitly not implemented.

## Dependencies And Integration
Uses CAM CCBs, SCSI changer element constants, SCSI attribute decode helpers, and `sbuf`.

## Risk Notes
Read-only in current implementation. It allocates the maximum 16-bit-ish transfer buffer and trusts returned lengths after bounding to valid transfer length.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/attrib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/camcontrol.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/camcontrol.h

## Purpose
Shared declarations and enums for `camcontrol` command modules.

## Main Elements
- Defines option lookup result enum `camcontrol_optret`.
- Defines device type enum `camcontrol_devtype` covering SCSI, SATL, ATA, NVMe, MMCSD, unknown, and none.
- Declares `struct get_hook` for argument callback helpers.
- Declares global `verbose`.
- Declares ATA, SCSI, firmware, zone, EPC, timestamp, depop, mode, inquiry, persistent reservation, attribute, argument, confirmation, and usage helper APIs.

## Dependencies And Integration
Included across `camcontrol` modules. It is the local interface contract between command parser/core and subcommand implementations.

## Risk Notes
Prototype changes here affect many storage command modules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/camcontrol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/depop.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/depop.c

## Purpose
Implements SCSI disk head depopulation commands: list physical elements, remove/truncate an element, and restore/rebuild elements.

## Main Elements
- `depop_list()`: sends GET PHYSICAL ELEMENT STATUS and prints element ID, restore eligibility, health, type, and capacity.
- `depop_remove()`: sends REMOVE ELEMENT AND TRUNCATE for an element and/or capacity.
- `depop_restore()`: sends RESTORE ELEMENTS AND REBUILD.
- `depop()`: parses `-c`, `-e`, `-d`, `-l`, `-r`; enforces a single action; chooses timeouts.

## Dependencies And Integration
Uses CAM, SCSI wrapper helpers, physical element status structures, and SCSI depopulation commands.

## Behavioral Notes
Default timeout is 5 seconds for listing. For remove/restore it uses block device characteristics VPD `depopulation_time` when present, otherwise one day.

## Risk Notes
Remove/restore operations are disruptive storage maintenance commands. The file comments note depop can make drives format-corrupt until the operation completes or is repeated.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/depop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/epc.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/epc.c

## Purpose
Implements ATA Extended Power Conditions control and reporting for ATA/SATL devices.

## Main Elements
- Maps EPC commands, power conditions, restore value sources, power sources, and flags.
- `epc_print_pcl_desc()`: formats one ATA power condition log descriptor.
- `epc_list()`: reads ATA power condition log pages and prints Idle A/B/C and Standby Y/Z state.
- `epc_getmode()`: reads identify data and supported capabilities log, reports APM/EPC support, low-power standby support, current power state, wait mode, and hold state.
- `epc_set_features()`: builds ATA SET FEATURES EPC subcommands for timer/state/goto/restore/enable/disable/source.
- `epc()`: parses options, validates action-specific required arguments, checks device type, and dispatches.

## Dependencies And Integration
Uses CAM ATA command construction, ATA identify/log structures, SATL handling, and shared `get_device_type()` / `get_ata_status()` helpers.

## Risk Notes
Some actions change drive power state or persistent EPC timers. The command is restricted to ATA and SATL devices to avoid invalid SCSI/NVMe use.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/epc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/fwdownload.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/fwdownload.c

## Purpose
Implements firmware download for SCSI and ATA devices, using SCSI WRITE BUFFER or ATA DOWNLOAD MICROCODE as appropriate.

## Main Elements
- Vendor table encodes vendor/device matching, packet sizes, WRITE BUFFER mode bytes, offset/buffer ID behavior, readiness requirements, and timeout strategy.
- `fw_get_vendor()`: matches SCSI inquiry vendor or ATA identify model to vendor table.
- `fw_get_timeout()`: honors user timeout or probes REPORT SUPPORTED OPERATION CODES timeout descriptors for WRITE BUFFER.
- `fw_validate_ibm()`: validates IBM tape firmware file header against device VPD page 0x03.
- `fw_read_img()`: opens and reads firmware image, skipping known vendor-specific headers and validating special IBM tape images.
- `fw_check_device_ready()`: tests SCSI readiness or ATA identify response according to vendor policy.
- `fw_rescan_target()`: sends `XPT_SCAN_TGT` via `/dev/xpt` after successful download.
- `fw_download_img()`: chunks firmware, draws progress, and sends SCSI WRITE BUFFER or ATA DOWNLOAD MICROCODE commands; supports simulation mode.
- `fwdownload()`: parses `-f`, `-q`, `-s`, `-y`; identifies device; prompts unless confirmed; runs download.

## Dependencies And Integration
Uses CAM, SCSI inquiry/opcode helpers, ATA identify helpers, `progress.c`, and shared confirmation/transfer-rate functions.

## Risk Notes
Explicitly warns that firmware download may damage drives. The command has confirmation, simulation mode, vendor checks, readiness checks, and timeout probing, but the core path still writes firmware to hardware.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/fwdownload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/modeedit.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/modeedit.c

## Purpose
Displays and edits SCSI mode pages and block descriptors using a mode-page format database.

## Main Elements
- Maintains editable fields in `editlist` and page names in `namelist`.
- `load_format()`: parses `/usr/share/misc/scsi_modes` or `$SCSI_MODES`, collecting page names and selected page format.
- `editlist_populate()` / `editlist_populate_desc()`: MODE SENSE current/changeable data and decode into edit entries.
- `editentry_set()` validates integer/string changes, clips out-of-range integers, and tracks changed state.
- `modepage_write()` / `modepage_read()`: serialize editable fields and parse edited values.
- `modepage_edit()`: reads changes from stdin when noninteractive, otherwise invokes `$EDITOR` or `vi` on a temp file.
- `editlist_save()` / `editlist_save_desc()`: MODE SENSE current data, encode edited values, clear reserved fields, then MODE SELECT.
- `modepage_dump()` / `modepage_dump_desc()`: raw hex fallback.
- `mode_edit()`: top-level display/edit path.
- `mode_list()`: queries all pages and prints page/subpage IDs with names from the database.

## Dependencies And Integration
Uses CAM MODE SENSE/SELECT wrappers from other `camcontrol` code and SCSI buffer encode/decode visitor helpers.

## Risk Notes
Edit mode can change device configuration, including saved values. The code restricts editing to current or saved page controls and falls back to binary display when database formatting is unavailable in non-edit mode.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/modeedit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/persist.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/persist.c

## Purpose
Implements SCSI Persistent Reserve In/Out support for `camcontrol`.

## Main Elements
- Maps persistent-reserve in actions: read keys, read reservation, report capabilities, read full status.
- Maps persistent-reserve out actions: register, reserve, release, clear, preempt, preempt-abort, register-ignore, register-move, replace-lost.
- Maps reservation scopes and types.
- Print helpers:
  - `persist_print_scopetype()`
  - `persist_print_transportid()`
  - `persist_print_res()`
  - `persist_print_keys()`
  - `persist_print_cap()`
  - `persist_print_full()`
- `scsipersist()` parses action, keys, transport IDs, scope, reservation type, APTPL/all-target/spec-I-T flags, unregister, and relative target port.
- Builds appropriate parameter buffers for PERSISTENT RESERVE IN/OUT, including transport ID lists for register/register-move.
- Retries reads with larger allocation lengths when target reports more data than initially allocated.

## Dependencies And Integration
Uses CAM CCBs, SCSI persistent reservation structures/helpers, transport ID parser/formatter, nv lookup helpers, and `sbuf`.

## Risk Notes
Persistent reservation OUT commands alter multi-initiator access control and can block or preempt other hosts. The code intentionally does not over-validate whether keys are required because zero can be valid for some workflows.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/persist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/progress.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/progress.c

## Purpose
Provides a terminal progress meter used by `camcontrol` firmware downloads.

## Main Elements
- `progress_init()`: initializes total size, prefix, start time, and terminal width.
- `progress_update()`: updates bytes done, percentage, elapsed time, and ETA.
- `progress_reset_size()`: changes total size.
- `progress_complete()`: updates, draws final state, and prints newline.
- `progress_draw()`: renders carriage-return progress line with percent, bar, abbreviated bytes, throughput, and ETA.

## Dependencies And Integration
Uses `progress.h`, terminal window-size ioctl, time, and direct `write()` to stdout. `fwdownload.c` calls it during firmware chunk transfers.

## Risk Notes
`progress_update()` divides by `prog->size`; callers must initialize with a nonzero total. `progress_init()` duplicates prefix but this module does not free it.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/progress.c -->