# Group Research: group_1399_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_unwind_c_sources_9041afd34531

Scope confirmed against `Docs/research_subset_a.md`: all listed files are under `sources/os/bsd/openbsd-src`, which is included in subset A. Each source file listed in the work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/unwind.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/unwind.c

This is the main supervisor for OpenBSD `unwind`, a privilege-separated DNS resolver daemon. It parses command-line options, validates configuration, daemonizes when not in debug mode, creates IPC socketpairs, starts resolver and frontend child processes, and then drives the main libevent loop.

Key behavior:
- Supports main, resolver-child, and frontend-child modes through `-E` and `-F`.
- Uses `imsg` with fd passing to connect main, frontend, and resolver processes.
- Opens loopback DNS sockets for UDP/TCP IPv4 and IPv6 and passes them to the frontend.
- Creates and passes control, route, trust-anchor, and blocklist fds.
- Handles reload by parsing a fresh config, sending it to children, then merging it into the live `main_conf`.
- Handles shutdown by clearing imsg buffers, closing fds, freeing config, and waiting for children.

Important structures/functions:
- `main()`: daemon setup, child spawning, fd setup, pledge, startup signaling.
- `start_child()`: forks and re-execs self with child role flags.
- `main_dispatch_frontend()` / `main_dispatch_resolver()`: parent-side imsg dispatch.
- `main_imsg_send_config()`: serializes config across imsg messages.
- `merge_config()` / `config_clear()` / `config_new_empty()`: live config ownership and cleanup.
- `open_ports()`: binds localhost DNS sockets.
- `solicit_dns_proposals()`: emits routing proposal solicitation.
- `imsg_receive_config()`: shared config deserializer used by child processes.

Filesystem/OS relevance:
- Uses `/etc/unwind.conf`, `/var/db/unwind.key`, `/dev/unwind.sock`, and optional blocklist files.
- Exercises OpenBSD process privilege separation, route sockets, pledge, fd passing, daemon lifecycle, and config reload semantics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/unwind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/unwind.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/unwind.h

This is the shared internal header for `unwind`. It defines paths, option bits, resolver type enums, imsg types, config structures, and cross-module function prototypes.

Key contents:
- Runtime paths: `/etc/unwind.conf`, `/dev/unwind.sock`, daemon user `_unwind`.
- DNSSEC root trust anchor constants for KSK2017 and KSK2024.
- Resolver types: recursor, autoconf, oDoT autoconf, ASR stub, forwarder, oDoT forwarder, DoT.
- `struct imsgev`: imsg buffer plus libevent state.
- `enum imsg_type`: all control/config/socket/query/status messages used between processes.
- `struct uw_forwarder`, `struct force_tree_entry`, `struct resolver_preference`, `struct uw_conf`.
- Query/answer wire structs for resolver/frontend communication.

Filesystem/OS relevance:
- Captures the daemon’s internal control protocol and config ownership model.
- Uses OpenBSD queue/tree primitives and imsg/event APIs.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/unwind.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/vnconfig/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/vnconfig/Makefile

Builds the `vnconfig` program.

Key contents:
- `PROG=vnconfig`
- Links against `libutil` through `LDADD=-lutil` and `DPADD=${LIBUTIL}`.
- Enables `-Wall` diagnostics through `CDIAGFLAGS`.
- Installs `vnconfig.8`.
- Includes OpenBSD `bsd.prog.mk`.

Filesystem/OS relevance:
- `vnconfig` is a block-device configuration utility for vnode-backed disk images.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/vnconfig/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/vnconfig/vnconfig.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/vnconfig/vnconfig.c

This is the `vnconfig` utility for configuring, unconfiguring, and inspecting vnode disk devices.

Key behavior:
- Default action configures a file as a `vnd` device.
- `-l` lists configured vnode devices, defaulting to scanning from `vnd0`.
- `-u` clears a configured device.
- `-t disktype` applies disklabel geometry/type defaults.
- `-k` uses a direct passphrase key; `-K rounds [-S saltfile]` derives a key using PBKDF2 and an optional salt file.
- Warns users to consider softraid crypto when using legacy encrypted vnd options.
- Auto-selects the first available `vndN` if no device is supplied.

Important functions:
- `main()`: option parsing and action dispatch.
- `get_pkcs_key()`: reads passphrase, creates/reads salt file, derives Blowfish-sized key material.
- `getinfo()`: calls `VNDIOCGET` and prints or scans device state.
- `config()`: fills `struct vnd_ioctl` and issues `VNDIOCSET`.
- `unconfig()`: issues `VNDIOCCLR`.
- `usage()`: command syntax.

Filesystem/OS relevance:
- Directly configures block devices backed by regular files.
- Uses OpenBSD device-opening helpers, disklabel defaults, vnode disk ioctls, and secure key cleanup via `explicit_bzero`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/vnconfig/vnconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/Makefile

Builds `wsconsctl`, except on `octeon` where `NOPROG=yes`.

Key contents:
- Source list: `display.c`, `keyboard.c`, `keysym.c`, `map_parse.y`, `map_scan.l`, `mouse.c`, `mousecfg.c`, `util.c`, `wsconsctl.c`.
- Adds include paths for current source and build directories.
- Generates `keysym.h` from `/usr/include/dev/wscons/wsksymdef.h` using `mkkeysym.sh`.
- Declares `keysym.o` dependency on generated `keysym.h`.
- Installs `wsconsctl.8`.

Filesystem/OS relevance:
- Demonstrates OpenBSD make integration with yacc/lex sources and generated headers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/display.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/display.c

Implements display-device fields for `wsconsctl`.

Key behavior:
- Defines `display_field_tab` for display type, dimensions, font metrics, emulations, screen types, focus, brightness, contrast, backlight, screen blanking, activity triggers, and font selection.
- `display_get_values()` maps selected fields to `WSDISPLAYIO_*` ioctls, caching shared ioctl results for burner and framebuffer info.
- `display_put_values()` maps writable fields to display ioctls, including focus changes, parameter updates, burner settings, and font selection.
- Unsupported ioctls with `ENOTTY` mark fields `FLG_DEAD`.
- `display_next_device()` enumerates `/dev/ttyC0` through `/dev/ttyJ0`.

Filesystem/OS relevance:
- Userland control surface for wsdisplay kernel drivers.
- Uses ioctl discovery and per-field liveness to support diverse hardware.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/display.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/keyboard.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/keyboard.c

Implements keyboard-device fields for `wsconsctl`.

Key behavior:
- Defines fields for keyboard type, bell parameters/defaults, keymap, key repeat/defaults, LEDs, encoding, and keyboard backlight.
- `keyboard_get_values()` reads selected fields using `WSKBDIO_*` ioctls.
- `keyboard_put_values()` writes selected fields using corresponding setter ioctls.
- Maintains global `kbmap` backed by `mapdata`, shared with the parser and utility printer.
- Calls `ksymenc()` after reading keyboard encoding so key symbol printing can prefer encoding-specific names.
- Backlight support is optional and marks field dead on `ENOTTY`.

Filesystem/OS relevance:
- Userland bridge to wskbd driver state and keymap mutation.
- Important for studying ioctl-style device configuration and mutable keyboard maps.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/keyboard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/keysym.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/keysym.c

Provides key symbol name/value conversion for `wsconsctl`.

Key behavior:
- Includes generated `keysym.h`, which provides `ksym_tab_by_name`.
- Builds a second sorted table by numeric keysym on first use.
- `ksym2name()` converts numeric keysyms to names, preferring current encoding and falling back to ISO.
- `name2ksym()` converts names to numeric keysyms and supports `unknown_N` round-tripping.
- `ksymenc()` maps keyboard encoding to ISO/L2/L5/L7/KOI lookup preference.
- `ksym_upcase()` maps function-key and Latin-1 lowercase symbols to uppercase variants for parser defaults.

Filesystem/OS relevance:
- Supports human-readable serialization and parsing of kernel keyboard maps.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/keysym.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/map_parse.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/map_parse.y

Yacc grammar for parsing keyboard map assignments.

Accepted forms:
- `keysym sym1 = sym2`: copies the key entry containing `sym2` to the position containing `sym1`.
- `keycode N = [command] sym ...`: assigns command and group symbols for a numeric keycode.

Key behavior:
- Initializes `newkbmap` with `KS_voidSymbol` entries.
- Uses current `kbmap` to resolve existing keysyms for copy operations.
- Automatically fills missing shifted/group symbols using `ksym_upcase()` or group defaults.
- Rejects keycodes >= `KS_NUMKEYCODES`.
- Exposes `newkbmap` for `util.c` to merge back into `kbmap`.

Filesystem/OS relevance:
- Converts textual keymap edits into `struct wskbd_map_data` suitable for kernel ioctls.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/map_parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/map_scan.l -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/map_scan.l

Lex scanner for keyboard map input.

Key behavior:
- Skips whitespace.
- Returns tokens for `=`, `keycode`, and `keysym`.
- Converts key symbol names through `name2ksym()`.
- Classifies command keysyms separately from ordinary keysyms.
- Parses decimal numbers with `strtonum()`.
- Rejects illegal characters with printable or octal diagnostics.
- `map_scan_setinput()` feeds a string into the scanner with `yy_scan_string()`.

Filesystem/OS relevance:
- Provides robust input validation before keymap data reaches wskbd ioctls.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/map_scan.l -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/mkkeysym.sh -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/mkkeysym.sh

Generates `keysym.h` from `dev/wscons/wsksymdef.h`.

Key behavior:
- Uses `awk`.
- Reads only definitions inside `/*BEGINKEYSYMDECL*/` and `/*ENDKEYSYMDECL*/`.
- Emits encoding constants, `struct ksym`, and `ksym_tab_by_name[]`.
- Strips `KS_` from emitted names.
- Classifies encodings by symbol prefix: `KS_L2_`, `KS_L5_`, `KS_L7_`, `KS_Cyrillic_`; defaults to ISO.

Filesystem/OS relevance:
- Build-time bridge from kernel wscons key symbol definitions to userland lookup tables.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/mkkeysym.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/mouse.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/mouse.c

Implements mouse and touchpad fields for `wsconsctl`.

Key behavior:
- Defines fields for resolution, samplerate, type, rawmode, calibration scale, reverse scrolling, touchpad tapping, multitouch buttons, scaling, swapsides, disable, edges, and raw parameter access.
- `mouse_init()` calls `mousecfg_init()` and hides unsupported configuration fields depending on device type and feature availability.
- `mouse_get_values()` reads mouse type and calibration data, then reads mousecfg-backed fields.
- `mouse_put_values()` writes resolution, calibration/raw mode, and mousecfg parameters.
- `mouse_next_device()` enumerates `/dev/wsmouseN`.

Filesystem/OS relevance:
- Shows combined legacy wsmouse calibration ioctls and newer parameter-array based configuration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/mouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/mousecfg.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/mousecfg.c

Implements reusable wsmouse parameter handling for mouse and touchpad configuration.

Key behavior:
- Defines grouped `struct wsmouse_parameters` presets for tapping, multitouch buttons, scaling, edges, side swapping, disable, reverse scrolling, and raw param access.
- `mousecfg_init()` detects touchpad devices, reads calibration resolution, builds a parameter buffer, and reads base/touchpad parameter ranges with `WSMOUSEIO_GETPARAMS`.
- `index_of()` maps enum parameter keys into the local buffer across supported ranges.
- `mousecfg_get_field()` copies values from the cached buffer into a field.
- `mousecfg_put_field()` writes changed values with `WSMOUSEIO_SETPARAMS`, then immediately reads normalized values back.
- Input helpers parse tapping triples, edge percentages, scaling factors, and raw `key:value` parameter lists.
- Print helpers serialize fields in stable human-readable forms.

Filesystem/OS relevance:
- Good example of kernel parameter discovery, caching, normalization, and userland validation around ioctl arrays.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/mousecfg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/mousecfg.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/mousecfg.h

Header for `mousecfg.c`.

Key contents:
- Extern declarations for global `struct wsmouse_parameters` field groups.
- Extern `cfg_touchpad` flag.
- Prototypes for initialization, get/put, print, and parse helpers.

Filesystem/OS relevance:
- Exposes mouse parameter groups to `mouse.c` and generic field formatting code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/mousecfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/util.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/util.c

Shared formatting, parsing, and lookup utilities for `wsconsctl`.

Key behavior:
- Provides name tables for keyboard, mouse, display, keyboard encoding, and keyboard variants.
- `field_by_name()` resolves dotted variable names after the device prefix.
- `field_by_value()` resolves a field from its backing storage address.
- `pr_field()` prints all supported formats: integers, bools, percentages, device types, keyboard encodings, maps, calibration scale, emulations, screen types, strings, and mousecfg values.
- `rd_field()` parses input for the same formats, including merge operations, percentages with clamping, keyboard encodings/variants, keymaps through lexer/parser, calibration tuples, strings, and mousecfg values.
- `print_kmap()` serializes non-empty keymap entries.
- `print_emul()` and `print_screen()` iterate display ioctls by index.

Filesystem/OS relevance:
- Centralizes userland parsing/printing for device ioctl state.
- Keymap handling demonstrates structured parsing instead of ad hoc string mutation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/wsconsctl.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/wsconsctl.c

Main program for `wsconsctl`.

Key behavior:
- Defines the device-type switch table for keyboard, mouse, and display, including field tables and get/put/enumeration callbacks.
- Supports `-a` for all auto-printable fields, `-f file` to force a device node, `-n` to suppress separators, and compatibility `-w`.
- Without args, defaults to `-a`.
- Opens devices read-write when possible, otherwise read-only.
- For set operations, parses `name=value`, `name+=value`, and `name-=value`.
- For modify/init fields, reads current state before applying a change.
- Writes one field at a time, optionally reads back, and prints resulting values unless suppressed by flags.
- `tab_by_name()` parses optional numeric device suffixes like `mouse1.param`.

Filesystem/OS relevance:
- Command dispatcher for wscons device control.
- Shows field-driven ioctl orchestration and multi-device enumeration under `/dev`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/wsconsctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/wsconsctl.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/wsconsctl.h

Shared header for `wsconsctl`.

Key contents:
- Defines `struct field`, field formats, and field flags.
- Format classes include numeric, boolean, percentage, keyboard/mouse/display types, keyboard encoding/map, mouse scale, display emulation/screen, strings, and mousecfg parameter groups.
- Flags distinguish read-only, write-only, no-auto, modifiable, no-readback, get, set, init, and dead fields.
- Declares shared helper functions and per-device callbacks.
- Includes `dev/wscons/wsksymvar.h` for key symbol/map types.

Filesystem/OS relevance:
- Encodes the field-table abstraction used across keyboard, mouse, and display ioctl modules.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/wsconsctl/wsconsctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/Makefile

Kernel support Makefile for generated syscall files and tags.

Key behavior:
- `all` intentionally does nothing and suggests `make syscalls`.
- `syscalls` target regenerates `init_sysent.c`.
- `init_sysent.c`, `syscalls.c`, `../sys/syscall.h`, and `../sys/syscallargs.h` depend on `makesyscalls.sh` and `syscalls.master`.
- Defines architecture list for tags generation.
- Builds per-architecture tags and creates symlinks through `/var/db/sys_tags`.
- `DGEN` lists generic kernel/source directories receiving tag links, including VFS and filesystem directories such as `kern`, `ufs`, `msdosfs`, `nfs`, and `miscfs`.

Filesystem/OS relevance:
- Maintains syscall table generation and kernel source navigation metadata.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/clock_subr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/clock_subr.c

Generic date/time conversion helpers.

Key behavior:
- `clock_ymdhms_to_secs()` converts `struct clock_ymdhms` to POSIX seconds since 1970.
- `clock_secs_to_ymdhms()` converts POSIX seconds back to calendar fields and weekday.
- Uses Gregorian leap-year logic with optimized common-case modulo avoidance.
- Handles February leap-day adjustment.

Filesystem/OS relevance:
- Kernel time conversion helper used by platform clock code and timekeeping paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/clock_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/dma_alloc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/dma_alloc.c

Small DMA-safe allocation pool implementation.

Key behavior:
- Creates DMA pools for object sizes from 2^4 through 2^16.
- `dma_alloc_init()` initializes pools, names them `dma<size>`, and applies `kp_dma_contig` constraints.
- `dma_alloc_index()` selects the smallest bucket fitting a requested size.
- `dma_alloc()` returns `pool_get()` from the selected bucket.
- `dma_free()` returns memory to the matching pool.

Filesystem/OS relevance:
- Provides constrained contiguous memory allocation for DMA-capable kernel subsystems, including storage/device drivers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/dma_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/exec_conf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/exec_conf.c

Exec format registration and initialization.

Key behavior:
- Defines `execsw[]` with two executable formats:
  - shell scripts via `exec_script_makecmds`
  - ELF binaries via `exec_elf_makecmds`
- Exports `nexecs` and `exec_maxhdrsz`.
- `init_exec()` computes the maximum required executable header size from registered formats.

Filesystem/OS relevance:
- Connects `execve` format probing to script and ELF loaders.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/exec_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/exec_elf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/exec_elf.c

ELF executable loader and ELF core dump writer.

Key exec-loader behavior:
- `elf_check_header()` validates ELF magic, class, endianness, version, target machine, and program-header count.
- `elf_load_psection()` converts `PT_LOAD` segments into vmcmds, enforces W^X by withholding execute permission from writable segments, applies immutable mapping where safe, handles file-backed and zero-filled portions, and accounts for textrel/mutable sections.
- `elf_read_from()` reads from an executable vnode with `vn_rdwr`.
- `elf_load_file()` loads the dynamic linker/interpreter as `ET_DYN`, validates noexec mounts and read permission, maps segments, handles randomize/mutable/syscall-pin program headers, and marks text vnodes.
- `exec_elf_makecmds()` validates the main executable, rejects writable text vnodes with `ETXTBSY`, reads program headers, handles `PT_INTERP`, OpenBSD notes, PIE base randomization, `DT_TEXTREL`, segment sizing, syscall pin tables, aux args, and stack setup.
- `exec_elf_fixup()` loads the interpreter in phase II, processes vmcmds, and writes ELF auxiliary vector entries to user stack.
- OpenBSD note handling recognizes `PT_OPENBSD_WXNEEDED`, `PT_OPENBSD_NOBTCFI`, and profiling notes.

Key core-dump behavior:
- `coredump_elf()` writes ELF core files unless `SMALL_KERNEL`.
- Uses `uvm_coredump_walkmap()` to build program headers.
- Handles large segment counts with extended section-header layout.
- Writes OpenBSD notes for process info, auxv, optional write cookie, and per-thread register/fpreg data.
- Special-cases execute-only sigcode by writing from kernel mapping.

Filesystem/OS relevance:
- Central executable file-to-address-space path.
- Heavily uses vnodes, mount flags, `vn_rdwr`, text vnode marking, UVM mappings, immutable memory, syscall pinning, and coredump file emission.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/exec_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/exec_script.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/exec_script.c

Interpreter-script exec handler.

Key behavior:
- Detects `#!` scripts and prevents recursive script processing with `EXEC_INDIR`.
- Requires interpreter line termination within `MAXINTERP`.
- Parses interpreter path and optional single argument.
- Preserves script setuid/setgid metadata for later application.
- If the script is unreadable or set-id, opens it as an fd and passes `/dev/fd/N` to the interpreter.
- Rewrites `nameidata` to point at the interpreter and calls `check_exec()` recursively.
- Builds fake argv: interpreter name, optional interpreter arg, script path or `/dev/fd/N`.
- On success, closes or retains the script vnode as appropriate, frees old namei buffer, sets `EXEC_HASARGL | EXEC_SKIPARG`, and updates credentials metadata.
- On failure, releases fd/vnode, path buffers, fake argv, and vmcmds.

Filesystem/OS relevance:
- Important vnode/namei/file-descriptor interaction during `execve`.
- Shows how OpenBSD handles unreadable and set-id scripts safely through `/dev/fd`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/exec_script.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/exec_subr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/exec_subr.c

Shared exec vmcmd helpers.

Key behavior:
- `new_vmcmd()` appends a vm command and holds referenced vnodes.
- `vmcmdset_extend()` doubles vmcmd storage.
- `kill_vmcmds()` releases vnode references and resets command storage.
- `exec_process_vmcmds()` executes vmcmds, handles relative mappings, and then clears the set.
- `vmcmd_map_pagedvn()` maps page-aligned executable segments directly from vnode objects with copy-on-write/fixed mapping.
- `vmcmd_map_readvn()` maps memory, reads bytes from a vnode into userspace, then restores requested protections.
- `vmcmd_map_zero()` maps anonymous zero-filled regions, including stacks.
- `vmcmd_mutable()` clears immutability over a region.
- `vmcmd_randomize()` fills a user region with random bytes, chunking large regions.
- `exec_setup_stack()` computes randomized stack bounds and emits guard plus writable stack vmcmds.

Filesystem/OS relevance:
- Bridges executable vnodes to UVM mappings.
- Central to demand-paged executable loading and non-demand-paged segment reads.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/exec_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/genassym.sh -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/genassym.sh

Generates assembly-visible constants from a compact input language.

Key behavior:
- Optional `-c` mode generates C, compiles, and executes it to print constants.
- Default mode emits inline assembly markers, compiles to assembly, and extracts `#define` lines from `XYZZY` markers.
- Supports directives: `config`, `include`, preprocessor conditionals, `struct`, `union`, `member`, `export`, `define`, and `quote`.
- Automatically emits `_KERNEL` and a local `offsetof` macro.
- Uses a temporary directory under `/tmp` and cleans it via trap.

Filesystem/OS relevance:
- Kernel build utility for keeping assembly offsets synchronized with C structs.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/genassym.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/init_main.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/init_main.c

Main OpenBSD kernel startup path.

Key behavior:
- Initializes process 0, CPU/current process state, timeouts, console, locks, UVM, disk subsystem, tty subsystem, random source, mbufs, sockets, SRP/SMR, process tables, file descriptors, pipes, kqueues, futexes, credentials, scheduler, task queues, network interface trees, and routing.
- Configures devices and pseudo-devices.
- Initializes VFS with `vfsinit()` and later mounts root through `mountroot`.
- Sets proc0 and init process current directories to the root vnode.
- Starts clocks, optional SysV IPC, crypto, domains, profiling, per-CPU subsystems, exec subsystem, and scheduler.
- Forks process 1 but blocks its `exec` until root is mounted.
- Creates kernel threads: pagedaemon, reaper, cleaner, update/syncer, aiodoned, page zeroing thread, and SMR thread.
- Boots secondary CPUs when configured.
- `start_init()` builds a minimal user stack and tries `/sbin/init`, `/sbin/oinit`, then `/sbin/init.bak`.
- `check_console()` validates `/dev/console`.

Filesystem/OS relevance:
- Core boot lifecycle file.
- Contains root filesystem mount, root vnode acquisition, process CWD setup, VFS initialization, swap initialization, and syncer/cleaner thread startup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/init_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/init_sysent.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/init_sysent.c

Generated OpenBSD syscall switch table.

Key behavior:
- Declares `const struct sysent sysent[]`.
- Generated from `syscalls.master`; explicitly marked do-not-edit.
- Each entry records argument count, argument struct size, flags such as `SY_NOLOCK`, and handler function.
- Includes conditional syscall entries for `PTRACE`, `ACCOUNTING`, NFS, SysV IPC, and other compile-time options.
- Filesystem-heavy entries include `open`, `close`, `link`, `unlink`, `chdir`, `fchdir`, `mknod`, `chmod`, `chown`, `mount`, `unmount`, `stat`, `lstat`, `fstatat`, `sync`, `revoke`, `symlink`, `readlink`, `execve`, `chroot`, `getfsstat`, `statfs`, `fstatfs`, `fhstatfs`, `fsync`, `getdents`, `rename`, `flock`, `mkfifo`, `quotactl`, `getfh`, `truncate`, `ftruncate`, `pathconf*`, `fhopen`, `fhstat`, `__getcwd`, and the `*at` family.

Filesystem/OS relevance:
- Kernel dispatch table tying user ABI numbers to filesystem, VM, process, and device syscalls.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/init_sysent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_acct.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_acct.c

Process accounting implementation.

Key behavior:
- `sys_acct()` enables or disables accounting after root check.
- Opens accounting file for append/write, requires a regular vnode, and stores it in `acctp`.
- Uses `acct_lock` to protect active and suspended accounting vnodes.
- `acct_process()` writes one accounting record on process exit, including command, user/system/elapsed time, memory, disk I/O counts, UID/GID, tty, flags, and pid.
- Uses `vn_rdwr()` with `IO_APPEND | IO_UNIT | IO_NOLIMIT`.
- `encode_comp_t()` converts time/count values into historical compact accounting format.
- `acct_thread()` periodically checks filesystem free space with `VFS_STATFS`, suspending below `acctsuspend` percent and resuming above `acctresume`.
- Handles forcibly unmounted accounting files by checking `VBAD`.
- `acct_shutdown()` closes accounting vnode during shutdown.

Filesystem/OS relevance:
- Direct interaction between process accounting and filesystem free-space state.
- Shows vnode lifecycle, append writes, statfs checks, and mount-removal resilience.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_acct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_bufq.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_bufq.c

Kernel buffer queue implementation for block I/O scheduling.

Key behavior:
- Provides pluggable queue implementations through `struct bufq_impl`.
- Supports FIFO and n-scan queue types.
- `bufq_init()` initializes per-queue mutex, high/low outstanding thresholds, implementation storage, and global queue registration.
- Thresholds are reduced when buffer-cache KVA slots are limited, preventing writes from consuming all buffer KVA.
- `bufq_queue()`, `bufq_dequeue()`, and `bufq_peek()` wrap implementation operations with locking.
- `bufq_wait()` throttles when outstanding buffers reach high water.
- `bufq_done()` decrements outstanding count and wakes waiters below low water.
- `bufq_drain()` completes all pending buffers with `ENXIO`.
- `bufq_quiesce()` stops queue mutation and waits for outstanding buffers to drain.
- `bufq_restart()` resumes all queues and wakes blocked initializers/queuers.
- FIFO uses `SIMPLEQ`.
- N-scan keeps a sorted segment plus FIFO backlog, sorting up to `BUFQ_NSCAN_N` requests by block number.

Filesystem/OS relevance:
- Directly tied to block-device buffer scheduling and filesystem writeback behavior.
- Quiesce/restart behavior is relevant to suspend, detach, and storage reset paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_bufq.c -->