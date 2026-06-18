# Group Research: group_363_freebsd_src_sources_os_bsd_freebsd_src_sbin_camcontrol_progress_h_so_66a9a14e0f49

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/progress.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/progress.h

## Purpose
Declares the progress meter interface used by `camcontrol` operations that need terminal progress reporting.

## Main Elements
- `progress_t`: tracks prefix text, total size, completed units, cached percentage, start/current/ETA times, elapsed time, and terminal width.
- API declarations: `progress_init()`, `progress_update()`, `progress_draw()`, `progress_reset_size()`, and `progress_complete()`.

## Dependencies And Integration
Includes `<sys/types.h>` and `<inttypes.h>`. This is a header-only contract; implementation is elsewhere in `camcontrol`.

## Risk Notes
The state model assumes monotonically advancing work and terminal-width-aware drawing. Callers must keep `size`/`done` coherent to avoid misleading percentages or ETA output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/progress.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/timestamp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/timestamp.c

## Purpose
Implements `camcontrol timestamp` support for SCSI tape-drive timestamps, including reporting the device timestamp and setting it from local/UTC time or a formatted string.

## Main Elements
- `set_restore_flags()`: reads the SCSI control extension mode subpage, temporarily sets `SCEP_SCSIP` to allow SCSI timestamp changes, and restores original flags afterward.
- `report_timestamp()`: issues `REPORT TIMESTAMP`, converts the 6-byte device timestamp into a host `uint64_t` millisecond value.
- `set_timestamp()`: parses requested time, converts seconds to milliseconds, builds SCSI timestamp parameters, and issues `SET TIMESTAMP`.
- `timestamp()`: command parser for `-r`, `-s`, `-f`, `-m`, `-U`, and `-T`.

## Dependencies And Integration
Uses CAM CCB allocation/submission, SCSI helper builders from `<cam/scsi/scsi_all.h>`, and `camcontrol.h` shared command plumbing. It respects task attribute, retry count, and timeout passed from the main `camcontrol` dispatcher.

## Risk Notes
Setting timestamps temporarily changes a device control mode page and attempts restoration on exit. Time parsing uses `strptime()`/`mktime()` for formatted input, so timezone and locale behavior matter unless `-U` is used.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/timestamp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/util.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/util.c

## Purpose
Provides small utility callbacks and prompting helpers shared by `camcontrol`.

## Main Elements
- Global `verbose`.
- `iget()`: fetches and parses the next integer argument from `struct get_hook`.
- `cget()`: fetches the next string argument from `struct get_hook`.
- `arg_put()`: prints decoded integer, byte/string, or space-trimmed string values for format-driven SCSI argument output.
- `get_confirmation()`: repeatedly prompts for explicit `yes`/`no`.

## Dependencies And Integration
Uses `camcontrol.h` for parser hook structures and `usage()`. These helpers support older SCSI command argument formatting and dangerous-operation confirmation.

## Risk Notes
`iget()` uses `strtol()` without full validation of trailing characters. `arg_put()` allocates temporary buffers for string output and exits on allocation failure.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/zone.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/zone.c

## Purpose
Implements SCSI ZBC and ATA ZAC shingled-media zone commands for `camcontrol`, including zone reporting and zone-management operations.

## Main Elements
- Command maps: translate user names such as `reportzones`, `close`, `finish`, `open`, and `rwp` to ZBC/ZAC service actions.
- Report filters and print modes: support all/empty/open/closed/full/etc. filters and normal/summary/script output.
- `zone_rz_print()`: decodes report-zone headers/descriptors in SCSI big-endian or ATA little-endian form, prints zone metadata, and signals whether more data is needed.
- `zone()`: parses command options, detects device type, builds SCSI ZBC or ATA ZAC/NCQ commands, sends the CCB, loops for multi-buffer reports, and frees resources.

## Dependencies And Integration
Uses CAM, SCSI, ATA command builders, `get_device_type()`, and `build_ata_cmd()` from `camcontrol` shared code. Handles both direct SCSI devices and ATA/SATL devices.

## Risk Notes
Report pagination depends on `next_start_lba` from the last decoded descriptor. ATA NCQ and non-NCQ paths encode parameters differently, so command construction must stay aligned with ZAC command definitions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/camcontrol/zone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ccdconfig/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ccdconfig/Makefile

## Purpose
Builds the `ccdconfig` utility.

## Main Elements
- `PACKAGE=ccdconfig`
- `PROG=ccdconfig`
- `MAN=ccdconfig.8`
- `LIBADD=geom`
- Includes `<bsd.prog.mk>`.

## Dependencies And Integration
Links against `libgeom` because the utility controls CCD GEOM instances through GEOM control requests.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ccdconfig/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ccdconfig/ccdconfig.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ccdconfig/ccdconfig.c

## Purpose
Configures, unconfigures, and dumps FreeBSD concatenated disk (`ccd`) GEOM devices.

## Main Elements
- CLI actions: configure one, configure all from a file, unconfigure one, unconfigure all, and dump configuration.
- `do_single()`: validates ccd name, interleave, flags, and providers; sends GEOM `create geom` or `destroy geom` requests.
- `do_all()`: reads `/etc/ccd.conf` or `-f` file, tokenizes non-comment lines, and applies configure/unconfigure action.
- `dumpout()` / `dump_ccd()`: request CCD class `list` output through GEOM control.
- `flags_to_val()`: parses numeric or comma-separated string flags.

## Dependencies And Integration
Uses kernel module loading (`modfind`, `kldload`) to try `geom_ccd`, and `libgeom` control APIs for runtime operations. `pathnames.h` supplies default config path.

## Risk Notes
This utility performs direct storage-topology mutation. Numeric flag parsing only allows a subset of flags in numeric form, while string parsing allows all declared flags.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ccdconfig/ccdconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ccdconfig/pathnames.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ccdconfig/pathnames.h

## Purpose
Defines filesystem path constants for `ccdconfig`.

## Main Elements
- `_PATH_CCDCONF`: `/etc/ccd.conf`
- `_PATH_CCDCTL`: `ccd.ctl`

## Dependencies And Integration
Included by `ccdconfig.c` for the default configuration file. `_PATH_CCDCTL` is retained as a named path constant though the modern implementation uses GEOM control APIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ccdconfig/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/clri/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/clri/Makefile

## Purpose
Builds the `clri` UFS inode-clearing utility.

## Main Elements
- `PACKAGE=ufs`
- `PROG=clri`
- `MAN=clri.8`
- `LIBADD=ufs`
- `WARNS?=2`
- Includes `<bsd.prog.mk>`.

## Dependencies And Integration
Links `libufs` for superblock and inode access.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/clri/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/clri/clri.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/clri/clri.c

## Purpose
Clears selected UFS inode records on a special device, preserving only an incremented generation number.

## Main Elements
- `usage()`: requires device plus one or more inode numbers.
- `main()`: opens UFS disk metadata with `ufs_disk_fillout()`, iterates inode arguments, validates inode number, reads inode with `getinode()`, zeros UFS1 or UFS2 dinode body, increments `di_gen`, writes with `putinode()`, and calls `fsync()`.

## Dependencies And Integration
Uses `<libufs.h>` and UFS/FFS dinode definitions. Intended as a low-level administrative repair tool.

## Risk Notes
This is destructive by design. Inode parsing uses `atoi()`, so malformed numeric strings can collapse to invalid low numbers but are not fully diagnosed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/clri/clri.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/comcontrol/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/comcontrol/Makefile

## Purpose
Builds the `comcontrol` serial/tty control utility.

## Main Elements
- `PACKAGE=runtime`
- `PROG=comcontrol`
- `MAN=comcontrol.8`
- Includes `<bsd.prog.mk>`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/comcontrol/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/comcontrol/comcontrol.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/comcontrol/comcontrol.c

## Purpose
Gets or sets tty drain-wait behavior on a file descriptor or device.

## Main Elements
- `usage()`: documents `comcontrol <filename> [drainwait <n>]`.
- `main()`: opens the target or uses stdin for `-`, reads `TIOCGDRAINWAIT` when no setting is supplied, and writes `TIOCSDRAINWAIT` for `drainwait`.

## Dependencies And Integration
Uses tty ioctls from system headers. It is a small wrapper around kernel tty control.

## Risk Notes
The setter validates only the first character of the numeric argument with `isdigit()` and then uses `atoi()`, so partial numeric strings are accepted.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/comcontrol/comcontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/conscontrol/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/conscontrol/Makefile

## Purpose
Builds the `conscontrol` console-control utility.

## Main Elements
- `PACKAGE=runtime`
- `PROG=conscontrol`
- `MAN=conscontrol.8`
- `WARNS?=2`
- Includes `<bsd.prog.mk>`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/conscontrol/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/conscontrol/conscontrol.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/conscontrol/conscontrol.c

## Purpose
Lists and changes kernel console configuration, muting, and virtual-console assignment.

## Main Elements
- `consstatus()`: reads `kern.consmute` and `kern.console`, splits configured/available consoles, and prints state.
- `consmute()`: toggles `kern.consmute`.
- `stripdev()`: normalizes `/dev/...` names and rejects other pathnames.
- `consadd()` / `consdel()`: add or remove console devices through `kern.console` sysctl writes.
- `consset()`: uses `TIOCCONS` ioctl to set/unset a virtual console.
- `main()`: dispatches `list`, `mute`, `add`, `delete`, `set`, and `unset`.

## Dependencies And Integration
Uses sysctls and tty ioctls. Device names are expected to refer to entries under `/dev`.

## Risk Notes
Changing console routing affects system logging and console input/output. `consdel()` builds a `-name` command string for the sysctl interface.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/conscontrol/conscontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ddb/Makefile

## Purpose
Builds the `ddb` userland control utility and installs default DDB configuration.

## Main Elements
- `CONFS=ddb.conf`
- `PACKAGE=runtime`
- `PROG=ddb`
- `SRCS=ddb.c ddb_capture.c ddb_script.c`
- `MAN=ddb.8`
- `LIBADD=kvm`

## Dependencies And Integration
Links `libkvm` for crash-dump capture-buffer access.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb.c

## Purpose
Top-level command dispatcher for managing DDB capture buffers and scripts.

## Main Elements
- `usage()`: documents `capture`, `script`, `scripts`, `unscript`, and pathname modes.
- `ddb_readfile()`: reads a config file, skips blanks/comments, splits each line into command plus optional argument string, and dispatches it.
- `ddb_main()`: dispatches subcommands.
- `main()`: treats a single readable absolute path as a batch file; otherwise dispatches command-line arguments.

## Dependencies And Integration
Calls functions declared in `ddb.h` and implemented by `ddb_capture.c` and `ddb_script.c`.

## Risk Notes
Batch parsing supports only two logical arguments per line: command and the rest of the line.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb.conf

## Purpose
Default DDB script definitions loaded during multi-user startup.

## Main Elements
- Defines `lockinfo` script for lock and vnode diagnostics.
- Defines `kdb.enter.panic` script to enable textdump capture, collect CPU/backtrace/process/thread diagnostics, dump textdump, and reset.
- Defines `kdb.enter.witness` script to run lock diagnostics on witness locking errors.

## Dependencies And Integration
Intended to be piped through `ddb` by rc startup. Consumed by `ddb_readfile()` command parsing.

## Risk Notes
The panic script performs `reset` after textdump capture, so changing this file changes crash-time system behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb.h

## Purpose
Shared declarations for the `ddb` utility.

## Main Elements
- Declares capture, script, scripts, unscript, and usage entry points.
- Has a conventional include guard.

## Dependencies And Integration
Included by all `ddb` source files to connect the dispatcher to subcommand implementations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb_capture.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb_capture.c

## Purpose
Prints and reports status for the DDB capture buffer from either a live kernel or a crash dump.

## Main Elements
- Sysctl names for live capture data, buffer offsets, size, max size, and in-progress state.
- `namelist[]`: kernel symbols for libkvm crash-dump reads.
- `kread()` / `kread_symbol()`: wrappers for exact-size `kvm_read()`.
- `ddb_capture_print_kvm()` / `ddb_capture_status_kvm()`: read capture data and metadata from crash dumps.
- `ddb_capture_print_sysctl()` / `ddb_capture_status_sysctl()`: read live kernel state through sysctl, retrying data reads on `ENOMEM`.
- `ddb_capture()`: parses `-M` and `-N`, opens kvm if needed, then dispatches `print` or `status`.

## Dependencies And Integration
Uses `libkvm` for crash dumps and `debug.ddb.capture.*` sysctls for live kernels.

## Risk Notes
Crash-dump access depends on exact kernel symbol names. Live buffer reads handle concurrent size changes by retrying when sysctl reports `ENOMEM`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb_capture.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb_script.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb_script.c

## Purpose
Lists, sets, and removes DDB scripts from userland.

## Main Elements
- Sysctl names for setting one script, listing scripts, and removing a script.
- `ddb_list_scripts()`: obtains full script list, prints all or finds a named script by parsing `name=value` lines.
- `ddb_script()`: sets a script when the argument contains `=`, otherwise prints a named script.
- `ddb_scripts()`: prints all scripts.
- `ddb_unscript()`: removes a named script and maps kernel `EINVAL` to user-facing `ENOENT`.

## Dependencies And Integration
Uses `debug.ddb.scripting.*` sysctls. Called from `ddb.c` dispatcher.

## Risk Notes
Script strings are passed directly to kernel DDB scripting sysctls. Listing parses kernel output format line by line.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ddb/ddb_script.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/decryptcore/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/decryptcore/Makefile

## Purpose
Builds the `decryptcore` encrypted kernel core dump decryptor.

## Main Elements
- `PROG=decryptcore`
- Sets `OPENSSL_API_COMPAT=0x10100000L`
- `LIBADD=crypto pjdlog`
- `MAN=decryptcore.8`
- Adds include path for `libpjdlog`.

## Dependencies And Integration
Links OpenSSL crypto and FreeBSD `pjdlog`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/decryptcore/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/decryptcore/decryptcore.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/decryptcore/decryptcore.c

## Purpose
Decrypts encrypted FreeBSD kernel core dumps using a private RSA key and kernel dump key file.

## Main Elements
- `usage()`: supports explicit key/core paths or crashdir plus dump number.
- `read_key()`: reads `struct kerneldumpkey`, converts encrypted-key size from dump endian, and reads appended encrypted key bytes.
- `decrypt()`: forks a child, opens inputs, enters Capsicum capability mode, reads RSA private key, decrypts dump key with OAEP or legacy PKCS#1 padding, initializes AES-256-CBC or ChaCha20 EVP decryption, streams plaintext to output, and exits with status.
- `main()`: parses options, derives `/var/crash/key.N`, `vmcore.N`, and `vmcore_encrypted.N` names when `-n` is used, handles `-f`, creates output with `O_EXCL`, deletes partial output on failure, and manages logging mode.

## Dependencies And Integration
Uses kernel dump metadata from `<sys/kerneldump.h>`, OpenSSL EVP/RSA/PEM APIs, Capsicum helpers, and `pjdlog`.

## Risk Notes
The parent unlinks partially decrypted output on child failure. Private-key and encrypted-core processing happens after entering capability mode, limiting filesystem reach after descriptors are open.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/decryptcore/decryptcore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/Makefile

## Purpose
Builds and installs `devd`, its grammar sources, tests, and platform/package-specific configuration files.

## Main Elements
- Installs `devd.conf` and many `/etc/devd/*.conf` files conditionally by build options and architecture.
- `PROG_CXX=devd`
- `SRCS=devd.cc token.l parse.y y.tab.h`
- `LIBADD=util`
- Enables yacc verbose output and tests subdirectory.

## Dependencies And Integration
Conditionally ties configs to packages such as ACPI, autofs, dhclient, console-tools, bluetooth, Hyper-V, nvme-tools, sound, USB, and ZFS.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/apple.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/apple.conf

## Purpose
Defines PowerPC Apple-specific `devd` reactions.

## Main Elements
- PMU power button and lid close trigger `shutdown -p now`.
- Brightness keys adjust `dev.backlight.0.level`.
- Volume and mute keys call `mixer`.
- Eject key calls `camcontrol eject cd0`.
- PMU AC-line events invoke `service power_profile`.

## Dependencies And Integration
Installed only for `powerpc` by the Makefile. Relies on PMU event fields and userland utilities.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/apple.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/asus.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/asus.conf

## Purpose
Defines ASUS and ASUS-Eee ACPI hotkey event actions.

## Main Elements
- Matches ACPI ASUS notify codes for mute, volume down, and volume up.
- Provides commented examples for additional EeePC user hotkeys.

## Dependencies And Integration
Installed when ACPI support is enabled. Actions call `mixer`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/asus.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/autofs.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/autofs.conf

## Purpose
Refreshes autofs caches on GEOM device events.

## Main Elements
- A `notify 100` rule matches `system=GEOM`, `subsystem=DEV`.
- Action runs `/usr/sbin/automount -c`.

## Dependencies And Integration
Installed when autofs is enabled. Supports media-style automount maps responding to device changes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/autofs.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/bluetooth.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/bluetooth.conf

## Purpose
Starts and stops Bluetooth service for USB Bluetooth device attach/detach events.

## Main Elements
- `attach 100` for `ubt[0-9]+` runs `service bluetooth quietstart`.
- `detach 100` for `ubt[0-9]+` runs `service bluetooth quietstop`.

## Dependencies And Integration
Installed when Bluetooth support is enabled. Uses attach/detach device-name matching.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/bluetooth.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devd.cc -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/devd.cc

## Purpose
Implements the device event daemon: parses configuration, listens to `/dev/devctl`, exposes client sockets, expands event variables, matches rules, and runs actions.

## Main Elements
- Classes: `var_list`, `match`, `media`, `action`, `event_proc`, and `config`.
- `my_system()`: fork/execs `/bin/sh -c`, closes descriptors except stdio, and preserves signal state.
- Matching: regular-expression match with optional leading `!` inversion, media-type checks through `SIOCGIFMEDIA`, and priority-sorted attach/detach/nomatch/notify rule lists.
- Config parsing: reads main config, then `.conf` files from configured directories, sorts rule lists by descending priority, and manages pidfile lifecycle.
- Expansion: supports `$var`, `$*`, `$_`, `$$`, and leaves `$(...)` shell command substitutions intact; shell action variables are shell-quoted.
- Event processing: parses `!`, `?`, `+`, and `-` devctl records into variables, adds timestamp and `vm_guest`, then runs the first matching rule list entry.
- Client sockets: creates world-writable stream and seqpacket Unix sockets under `/var/run`, tracks up to configurable clients, sends events, and drops unresponsive clients.
- `main()`: checks/enables `hw.bus.devctl_queue`, parses `-d`, `-f`, `-l`, `-n`, `-q`, loads config, daemonizes when requested, installs signal handlers, and enters the event loop.

## Dependencies And Integration
Uses lexer/parser generated from `token.l` and `parse.y`, `libutil` pidfile helpers, `/dev/devctl`, sysctls, Unix-domain sockets, and shell/userland actions.

## Risk Notes
Actions run as shell commands with expanded event variables. The implementation shell-quotes variable substitutions but intentionally preserves `$(...)` command substitution in config strings. Event storms are bounded by socket send buffers and client limits.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devd.cc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devd.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/devd.conf

## Purpose
Default main `devd` configuration.

## Main Elements
- Options add `/etc/devd` and `/usr/local/etc/devd`, set pidfile, and define `wifi-driver-regex`.
- Network rules run `/etc/pccard_ether` on IFNET attach and wireless driver attach/detach.
- Example override for `ed50`.
- ACPI thermal warning and suspend/resume rc hooks.
- Large commented example block for ACPI, RCTL, coredumps, and DEVFS tty creation.

## Dependencies And Integration
Parsed first by `devd`, then extra directories are scanned. Establishes base event behavior and variables used by later rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devd.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devd.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/devd.h

## Purpose
C-compatible declarations shared between the C lexer/parser and C++ daemon implementation.

## Main Elements
- Parser callback declarations for adding rule blocks, directories, pidfile, variables, and event processing statements.
- Lexer/parser entry points and `lineno`.
- Constants `PATH_DEVCTL` and `DEVCTL_MAXBUF`.

## Dependencies And Integration
Included by `parse.y`, `token.l`, and `devd.cc`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devd.hh -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/devd.hh

## Purpose
Declares the C++ object model for `devd`.

## Main Elements
- `var_list`: scoped event/global variable table.
- `eps`: abstract event-processing statement.
- `match`, `media`, `action`: concrete statement types.
- `event_proc`: priority-tagged group of match/action statements.
- `config`: stores directories, pidfile, variable stack, rule vectors, parsing, expansion, and event lookup methods.

## Dependencies And Integration
Implemented by `devd.cc`. Separates parser-facing construction from runtime matching/execution.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devd.hh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devmatch.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/devmatch.conf

## Purpose
Connects `devd` NOMATCH events to the `devmatch` service.

## Main Elements
- High-priority ignores for events lacking useful location/PNP data.
- Ignores ACPI `_HID=none`.
- Generic `nomatch 100` action runs `service devmatch quietstart $*`.
- Comments document how to override with higher-priority no-op rules or rc.conf.

## Dependencies And Integration
Works with `devmatch(8)` and kernel NOMATCH event strings.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/devmatch.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/dhclient.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/dhclient.conf

## Purpose
Starts `dhclient` when DHCP-capable network links come up.

## Main Elements
- IFNET `LINK_UP` with Ethernet media starts `service dhclient quietstart $subsystem`.
- IFNET `LINK_UP` with 802.11 media does the same.
- No link-down rule; comments state `dhclient` exits automatically on link down.

## Dependencies And Integration
Uses `media-type` match support implemented in `devd.cc`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/dhclient.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/hyperv.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/hyperv.conf

## Purpose
Defines Hyper-V-specific device event behavior.

## Main Elements
- Starts/stops `hv_kvp_daemon` on `hv_kvp_dev` create/destroy.
- Starts/stops `hv_vss_daemon` on `hv_fsvss_dev` create/destroy.
- Handles non-transparent network VF workflow with `hyperv_vfup` and `hyperv_vfattach`.

## Dependencies And Integration
Installed when Hyper-V support is enabled. Integrates DEVFS events, Hyper-V VF events, and Ethernet attach events with Hyper-V helper scripts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/hyperv.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/moused.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/moused.conf

## Purpose
Starts or stops `moused` for mouse-like device nodes.

## Main Elements
- Starts `moused` for `atp`, `ums`, `wsp`, and `input/event` device creation.
- Stops `moused` for `ums` destroy events.

## Dependencies And Integration
Matches DEVFS CDEV create/destroy notifications and calls `service moused`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/moused.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/nvmf.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/nvmf.conf

## Purpose
Reconnects NVMe over Fabrics host controllers when requested.

## Main Elements
- Matches `system=nvme`, `subsystem=controller`, `type=RECONNECT`.
- Runs `nvmecontrol reconnect $name`.

## Dependencies And Integration
Installed in the NVMe tools package group.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/nvmf.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/parse.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/parse.y

## Purpose
Yacc grammar for `devd.conf` files.

## Main Elements
- Supports `options`, `attach`, `detach`, `nomatch`, and `notify` blocks.
- Option statements: `directory`, `pid-file`, and `set`.
- Event statements: `match`, shorthand `device-name`, `media-type`, `class`, `subdevice`, and `action`.
- Semantic actions call C-compatible constructors declared in `devd.h`.

## Dependencies And Integration
Generated parser is built into `devd`. Tokens are produced by `token.l`; runtime objects are created in `devd.cc`.

## Risk Notes
Empty event blocks are allowed by grammar but do not add event processors.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/power_profile.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/power_profile.conf

## Purpose
Switches power profile on AC line state changes.

## Main Elements
- Matches ACPI `ACAD` notifications.
- Runs `service power_profile $notify`.

## Dependencies And Integration
Installed on i386, amd64, and arm64 in the ACPI package group.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/power_profile.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/snd.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/snd.conf

## Purpose
Redirects virtual audio endpoints when sound devices connect or disconnect.

## Main Elements
- SND `CONN` `IN` for `dsp[0-9]+`: tells `virtual_oss_cmd` to use recording device.
- SND `CONN` `OUT`: tells `virtual_oss_cmd` to use playback device.
- SND `CONN` `NODEV`: redirects to `/dev/null` to avoid repeated errors.

## Dependencies And Integration
Uses `sysrc` to find `virtual_oss_default_control_device` and calls `virtual_oss_cmd` if present.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/snd.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/syscons.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/syscons.conf

## Purpose
Switches syscons keyboard device when USB keyboard `ukbd0` appears or disappears.

## Main Elements
- Attach `ukbd0`: `service syscons setkeyboard /dev/ukbd0`.
- Detach `ukbd0`: `service syscons setkeyboard /dev/kbd0`.

## Dependencies And Integration
Installed in the console-tools group.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/syscons.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/tests/Makefile

## Purpose
Builds ATF tests for `devd` client sockets.

## Main Elements
- `ATF_TESTS_C=client_test`
- Requires `/var/run/devd.pid`, `devd`, root user, and 15-second timeout.
- `WARNS?=5`
- Includes `<bsd.test.mk>`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/tests/client_test.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/tests/client_test.c

## Purpose
Tests that `devd` client sockets deliver complete device events.

## Main Elements
- `create_two_events()`: creates and destroys a small `md(4)` null device to trigger DEVFS create/destroy events.
- `common_setup()`: connects to a `devd` Unix socket and triggers events.
- `seqpacket` test: reads from `/var/run/devd.seqpacket.pipe` and expects create/destroy events on separate packet reads.
- `stream` test: reads from `/var/run/devd.pipe` into a large buffer and searches for both event substrings.
- ATF registration adds both tests.

## Dependencies And Integration
Requires root because it uses `mdconfig`. Validates both SOCK_SEQPACKET and SOCK_STREAM client protocols implemented by `devd.cc`.

## Risk Notes
Tests may observe unrelated system events, so they search until target patterns are found or timeout/buffer limit is reached.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/tests/client_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/token.l -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/token.l

## Purpose
Lex scanner for `devd` configuration files.

## Main Elements
- Tracks `lineno`.
- Skips whitespace and `#`, `//`, and `/* ... */` comments.
- Emits block punctuation, semicolons, numbers, keywords, IDs, and quoted strings.
- Quoted strings support backslash-newline continuations with following whitespace skipped.
- `yyerror()` logs parse errors with line number and token text.

## Dependencies And Integration
Includes `devd.h` and generated `y.tab.h`; feeds tokens to `parse.y`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/token.l -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/uath.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/uath.conf

## Purpose
Loads firmware for supported Atheros USB wireless devices.

## Main Elements
- Multiple `notify 100` rules match USB DEVICE ATTACH events.
- Rules match vendor/product combinations for Accton, Atheros, Conceptronic, D-Link, Gigaset, Global Sun, Netgear, U-MEDIA, Wistron, Z-Com, and related AR5523 devices.
- Action runs `/usr/sbin/uathload -d /dev/$cdev`.

## Dependencies And Integration
Installed when USB support is enabled. Matches USB event variables emitted by the kernel/devctl path.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/uath.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/ulpt.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/ulpt.conf

## Purpose
Provides an example USB printer rule.

## Main Elements
- Entire notify rule is commented out.
- Example matches USB INTERFACE ATTACH for printer class/subclass/protocol.
- Example action changes ownership of `/dev/$cdev`.

## Dependencies And Integration
Installed when USB support is enabled, but inert by default.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/ulpt.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/zfs.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devd/zfs.conf

## Purpose
Logs sample ZFS problem reports from `devd`.

## Main Elements
- Matches checksum, I/O, data, zpool, vdev, catastrophic I/O, probe, log replay, config-cache write, removed, autoreplace, and statechange ZFS event types.
- Actions call `logger` with pool/vdev/path/error variables.

## Dependencies And Integration
Installed when ZFS support is enabled. Intended as sample event reporting rather than full remediation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devd/zfs.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/devfs/Makefile

## Purpose
Builds the `devfs` control utility and installs default config/rules files.

## Main Elements
- `CONFS=devfs.conf devfs.rules`
- Installs `devfs.rules` under `/etc/defaults` with mode `600`.
- `PROG=devfs`
- `SRCS=devfs.c rule.c`
- `MAN=devfs.8`
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/devfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/devfs/devfs.c

## Purpose
Top-level command dispatcher and utility helpers for controlling devfs mount rules.

## Main Elements
- Opens target mount point from `-m` or defaults to `/dev`.
- Dispatches `rule` and `ruleset` commands.
- Numeric helpers: `atonum()`, `eatoi()`, and `eatonum()`.
- `efgetln()`: malloc-backed line reader that handles newline and non-newline-terminated lines.
- `tokenize()`: splits a rule line into argv-style tokens while preserving one allocated backing string.
- `usage()`: prints command forms.

## Dependencies And Integration
Shares `mpfd` mount-point descriptor with `rule.c`. Includes declarations from `extern.h`.

## Risk Notes
`tokenize()` returns early with allocated `wline` when there are zero tokens, which is acceptable for short-lived command execution but notable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/devfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/devfs.conf -->
# File Research: sources/os/bsd/freebsd-src/sbin/devfs/devfs.conf

## Purpose
Example `/etc/rc.d/devfs` device adjustment configuration.

## Main Elements
- Documents `link`, `perm`, and `own` examples.
- Shows sample aliases for `cd0`, permissions for `smb0`, speaker, and `bpf`.
- All example actions are commented.

## Dependencies And Integration
Read by rc scripts, not directly by `devfs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/devfs.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/devfs.rules -->
# File Research: sources/os/bsd/freebsd-src/sbin/devfs/devfs.rules

## Purpose
Default devfs rulesets for hiding/unhiding common devices, especially for jails.

## Main Elements
- `devfsrules_hide_all=1`: hide everything.
- `devfsrules_unhide_basic=2`: unhide null, zero, crypto, random, urandom.
- `devfsrules_unhide_login=3`: unhide pty/tty, ptmx, pts, fd, stdin/stdout/stderr.
- `devfsrules_jail=4`: include base sets and unhide fuse/zfs.
- `devfsrules_jail_vnet=5`: include jail sets and unhide pf.

## Dependencies And Integration
Installed under `/etc/defaults`. Lines are intended for expansion/application by rc scripts invoking `devfs`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/devfs.rules -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/extern.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/devfs/extern.h

## Purpose
Shared declarations for the `devfs` command implementation.

## Main Elements
- Includes kernel devfs ioctl structures from `<fs/devfs/devfs.h>`.
- Defines command table types.
- Declares `rule_main`, `ruleset_main`, parsing helpers, and global `mpfd`.

## Dependencies And Integration
Included by `devfs.c` and `rule.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/rule.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/devfs/rule.c

## Purpose
Implements `devfs rule` and `devfs ruleset` subcommands by translating textual rules into devfs ioctls.

## Main Elements
- Rule command table: `add`, `apply`, `applyset`, `del`, `delset`, `show`, and `showsets`.
- `rule_main()`: parses optional `-s ruleset` and dispatches rule commands.
- `ruleset_main()`: switches active ruleset via `DEVFSIO_SUSE`.
- `rulespec_infp()` / `rulespec_instr()` / `rulespec_intok()`: parse rules from stdin, strings, or argv tokens into `struct devfs_rule`.
- Rule grammar supports optional rule number, conditions `type` and `path`, and actions `hide`, `unhide`, `user`, `group`, `mode`, and `include`.
- `rulespec_outfp()`: prints kernel rules back in parseable form.

## Dependencies And Integration
Uses devfs ioctls on `mpfd`, password/group lookups, and mode parsing via `setmode()`/`getmode()`.

## Risk Notes
Rules directly affect device visibility and permissions in a devfs mount. User/group numeric fallbacks use `eatoi()` with comments noting overflow concerns.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devfs/rule.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devmatch/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/devmatch/Makefile

## Purpose
Builds the `devmatch` utility.

## Main Elements
- `PACKAGE=devmatch`
- `PROG=devmatch`
- `MAN=devmatch.8`
- `LIBADD=devinfo`
- Includes `<bsd.prog.mk>`.

## Dependencies And Integration
Links `libdevinfo` to inspect the device tree.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devmatch/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devmatch/devmatch.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/devmatch/devmatch.c

## Purpose
Matches unattached or NOMATCH devices against kernel module linker hints and prints modules that may bind them.

## Main Elements
- Options: all, dump, hints path, nomatch string, quiet, unbound, verbose.
- `read_linker_hints()`: reads explicit or `kern.module_path` linker.hints files, validates versions, and merges multiple hint files.
- Hint readers: `getint()` and `getstr()` decode aligned linker-hints records.
- `pnpval_as_int()` / `pnpval_as_str()`: extract PNP key values from event/device PNP info strings.
- `search_hints()`: walks module/PNP hint records, applies numeric/string/mask/key matching rules, prints matching modules, dumps hints, or reports unbound devices.
- `find_unmatched()`: walks the devinfo tree for enabled, unattached/unbound devices and searches hints.
- `find_nomatch()`: parses a NOMATCH event string, filters devices already attached once, and searches hints for that event.
- `main()`: reads hints, optionally dumps, initializes devinfo, and searches either NOMATCH or all devices.

## Dependencies And Integration
Used by `devd/devmatch.conf` through `service devmatch quietstart $*`. Reads kernel module hints and the live device tree.

## Risk Notes
PNP string parsing is specialized and contains comments about imperfect key override handling and simple quoted copying. Matching quality depends on linker.hints metadata format and device event strings.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/devmatch/devmatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/Makefile

## Purpose
Builds the FreeBSD `dhclient` program, script, manpages, and tests.

## Main Elements
- Installs `dhclient.conf`.
- Builds many ISC/OpenBSD-derived source files including parser, BPF, packet, options, dispatch, and privilege-separation code.
- Installs `dhclient-script`.
- Links `libutil`; conditionally links Casper/cap_syslog when dynamic root and Casper are enabled.
- Sets `NO_WCAST_ALIGN=yes` and enables tests subdirectory.

## Dependencies And Integration
Part of the `dhclient` package and used by `devd/dhclient.conf` link-up events.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/alloc.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/alloc.c

## Purpose
Provides small allocation helpers for DHCP client data structures.

## Main Elements
- `new_string_list(size)`: allocates a `struct string_list` plus inline string storage and points `string` into the tail.
- `new_hash_table(count)`: allocates a hash table sized for `count` buckets and records `hash_count`.
- `new_hash_bucket()`: allocates a zeroed hash bucket.

## Dependencies And Integration
Included through `dhcpd.h`. Used by parser and option/hash table code.

## Risk Notes
These helpers return `NULL` on allocation failure; most callers treat allocation failure as fatal.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/bpf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/bpf.c

## Purpose
Handles DHCP packet input/output through BPF and raw sockets, with privilege-separated send support.

## Main Elements
- `if_register_bpf()`: opens `/dev/bpfN`, attaches it to an interface, and optionally sets VLAN PCP.
- Write BPF filter: restricts outbound BPF writes to expected IPv4 UDP DHCP traffic.
- `if_register_send()`: configures write BPF, locks filter, limits Capsicum rights, and opens raw UDP socket for unicast sends.
- Read BPF filter: accepts IPv4 UDP packets to the local DHCP port, including VLAN VID 0 priority-tagged traffic.
- `if_register_receive()`: configures read BPF immediate mode, allocates read buffer, installs/locks filter, and limits rights/ioctls.
- `send_packet_unpriv()` / `send_packet_priv()`: marshal DHCP packet send requests over imsg-style buffers to privileged code, then send via BPF broadcast or raw socket unicast.
- `receive_packet()`: reads BPF buffers, walks BPF packet headers, validates complete captures, decodes hardware/IP/UDP headers, and returns DHCP payload.

## Dependencies And Integration
Uses `dhcpd.h`, `privsep.h`, BPF ioctls, Capsicum rights, raw sockets, packet assembly/decoding helpers, and dhclient interface state.

## Risk Notes
BPF packet buffering requires careful offset alignment with `BPF_WORDALIGN()`. Send request validation checks message lengths and packet size before privileged transmission.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/bpf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/clparse.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/clparse.c

## Purpose
Parses `dhclient.conf` and lease files into client configuration, interface state, options, and lease lists.

## Main Elements
- `read_client_conf()`: initializes option universes and top-level defaults, reads config statements if the config file exists, and ensures the active interface has client/config structures.
- `read_client_leases()`: reads lease file entries and stops on corruption.
- `parse_client_statement()`: handles send/default/supersede/prepend/append options, media, hardware, request/require/ignore lists, timers, VLAN PCP, script, interface blocks, leases, aliases, and reject lists.
- `parse_X()`: parses hex byte sequences or strings.
- `parse_option_list()`: parses comma-separated option names.
- `parse_interface_declaration()`: applies nested config to a named real or dummy interface.
- `interface_or_dummy()`, `make_client_state()`, `make_client_config()`: manage real/dummy interface configuration objects.
- `parse_client_lease_statement()` / `parse_client_lease_declaration()`: parse leases, associate with interfaces, maintain active and historical lease lists.
- `parse_option_decl()`: parses option values according to option format strings into `option_data`.
- `parse_string_list()` and `parse_reject_statement()`: parse media lists and rejected server address lists.

## Dependencies And Integration
Uses lexer functions from `conflex.c`, token definitions from `dhctoken.h`, DHCP option tables/universes, and dhclient global interface/time state.

## Risk Notes
Option data is accumulated in a fixed 1024-byte hunk buffer with explicit overflow checks. Lease ordering matters: the last lease for an interface becomes active unless superseded/expired.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/clparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/conflex.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/conflex.c

## Purpose
Lexical scanner for dhclient configuration and lease parsers.

## Main Elements
- Tracks source name, line/column, current/previous line buffers, and a one-token peek buffer.
- `new_parse()`: resets lexer state for a file.
- `get_char()`: reads characters while maintaining line buffers and positions.
- `get_token()`, `next_token()`, `peek_token()`: tokenize whitespace/comments, strings, numbers, identifiers, and punctuation.
- `read_string()`: handles quoted strings with backslash escaping.
- `read_number()` and `read_num_or_name()`: read numeric and identifier-like tokens.
- `intern()`: maps known dhclient/dhcp keywords to token constants, otherwise returns the default token class.

## Dependencies And Integration
Included by `clparse.c` and other dhclient parsers through `dhcpd.h` and `dhctoken.h`.

## Risk Notes
Token text uses a fixed 1500-byte buffer with warnings and truncation if exceeded. Identifier interning is extensive and case-insensitive.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dhclient/conflex.c -->