# Group Research: group_442_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_chio_h_sources_os_bsd_d8f220d2b604

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/chio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/chio.h

## Purpose
Defines the user/kernel ioctl ABI for SCSI media changer devices: moving media, exchanging media, positioning pickers, querying changer geometry, reading element status, and setting volume tags.

## Main Elements
- Element type IDs: `CHET_MT`, `CHET_ST`, `CHET_IE`, `CHET_DT`; comments warn that `sys/scsi/ch.c` relies on their numeric order.
- Command payloads: `changer_move`, `changer_exchange`, `changer_position`, `changer_params`.
- Element status ABI: `changer_voltag`, `changer_element_status`, `changer_element_status_request`, including SMC3 fields for medium type, protocol ID, association, designator type/code set, and designator bytes.
- Volume tag update ABI: `changer_set_voltag_request` with set, replace, clear, and alternate-tag flags.
- Ioctls: `CHIOMOVE`, `CHIOEXCHANGE`, `CHIOPOSITION`, `CHIOGPICKER`, `CHIOSPICKER`, `CHIOGPARAMS`, `CHIOIELEM`, `OCHIOGSTATUS`, `CHIOSETVOLTAG`, `CHIOGSTATUS`.

## Dependencies And Integration
Includes `sys/ioccom.h` and, outside the kernel, `sys/types.h`. It is consumed by changer drivers and userland tools that issue `ch(4)` ioctls.

## Risk Notes
This is ABI-sensitive. Struct layout, ioctl numbers, element type values, and fixed-size volume/designator buffers must remain compatible with existing userland and the SCSI changer driver.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/chio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ck.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ck.h

## Purpose
Provides a small compatibility shim for Concurrency Kit queue/epoch interfaces across kernel and non-kernel builds.

## Main Elements
- In `_KERNEL`, includes `<ck_queue.h>` and `<ck_epoch.h>`.
- Outside `_KERNEL`, includes `<sys/queue.h>` and maps `CK_STAILQ_*`, `CK_LIST_*`, and `CK_SLIST_*` names to standard BSD queue macros.

## Dependencies And Integration
Used by code that wants CK-style queue type names while still compiling in userland without kernel CK headers.

## Risk Notes
The userland aliases cover only type/head/entry macro names, not the full CK API. Kernel code depends on actual CK headers being available.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/clock.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/clock.h

## Purpose
Declares kernel-only calendrical and time-of-day clock services for RTC drivers, timezone/localtime conversions, BCD conversion, FAT timestamp conversion, and clock registration.

## Main Elements
- `struct clocktime` stores binary calendar fields and nanoseconds.
- `struct bcd_clocktime` stores BCD calendar fields plus AM/PM state.
- Conversion APIs: `clock_ct_to_ts()`, `clock_ts_to_ct()`, `clock_bcd_to_ts()`, `clock_ts_to_bcd()`.
- RTC registration APIs: `clock_register()`, `clock_register_flags()`, `clock_schedule()`, `clock_unregister()`.
- Clock flags control whether set/get paths apply timestamps, UTC offset, and resolution/accuracy adjustment.
- FAT helpers: `timespec2fattime()` and `fattime2timespec()`.
- Debug/print helpers for clocktime, BCD clocktime, and timespec values.

## Dependencies And Integration
Only exposes content under `_KERNEL`. Used by RTC and filesystem code that must translate hardware/local calendar formats into kernel timespecs.

## Risk Notes
Year interpretation is deliberately nuanced for two-digit RTCs, century-bit hardware, and full years. Incorrect use can produce bad filesystem or RTC timestamps, especially when localtime and UTC offsets differ.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/clock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cnv.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cnv.h

## Purpose
Declares cookie-based nvlist accessors for inspecting, retrieving, taking, and freeing name/value pairs without re-looking them up by name.

## Main Elements
- Metadata helpers: `cnvlist_name()` and `cnvlist_type()`.
- Get APIs for bool, number, string, nvlist, binary, and arrays.
- Userland-only descriptor accessors are included outside `_KERNEL`.
- Take APIs remove the item and transfer ownership to the caller.
- Free APIs remove and free the item identified by a cookie.

## Dependencies And Integration
Uses `sys/_nv.h`; outside the kernel it includes standard bool/int/stdarg/stdio headers and `sys/nv_namespace.h`.

## Risk Notes
Pointer-returning get APIs expose internal storage that must not be freed by the caller. Take APIs transfer ownership and require matching cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cnv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/compressor.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/compressor.h

## Purpose
Declares the kernel compression stream abstraction used by crash dump and related kernel-output paths.

## Main Elements
- Supported formats: `COMPRESS_GZIP` and `COMPRESS_ZSTD`.
- `compressor_cb_t` callback writes compressed chunks with size and offset.
- Opaque `struct compressor` lifecycle: `compressor_init()`, `compressor_reset()`, `compressor_flush()`, `compressor_fini()`.
- Streaming API: `compressor_write()`, `compressor_format()`, `compressor_avail()`.

## Dependencies And Integration
Kernel-only header. Used by kernel dump code and other in-kernel compression consumers.

## Risk Notes
The callback contract is central: write ordering, max I/O size, and flush/fini behavior must be honored by callers to avoid corrupt compressed output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/compressor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/condvar.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/condvar.h

## Purpose
Defines FreeBSD kernel condition variables and their wait/signal API.

## Main Elements
- `struct cv` stores a wait-channel description and waiter count.
- Lifecycle: `cv_init()` and `cv_destroy()`.
- Wait variants: regular, unlock-on-wait, signal-interruptible, timed, and timed signal-interruptible.
- Public macros adapt lock objects from mutex/rw-style lock structs to internal `_cv_*` functions.
- Wake APIs: `cv_signal()` and `cv_broadcastpri()`; `cv_broadcast()` maps to priority 0.

## Dependencies And Integration
Kernel-only APIs operate on `struct lock_object`; timed waits use `sbintime_t`, `tick_sbt`, and callout flags.

## Risk Notes
The waiter count is protected by the caller’s associated condition mutex. Correct usage requires holding the same lock across predicate checks, waits, and signal/broadcast operations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/condvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/conf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/conf.h

## Purpose
Defines FreeBSD character device objects, character device switch ABI, devfs device creation/destruction entry points, clone-device hooks, and kernel dump device plumbing.

## Main Elements
- `struct cdev` describes devfs-visible devices: flags, timestamps, credentials, refs, children/aliases, driver private pointers, switch pointer, I/O sizing, and name.
- Driver callback typedefs cover open, fdopen, close, read, write, ioctl, poll, mmap, strategy, kqueue filter, purge, and mmap-single.
- Device classes and flags: `D_TAPE`, `D_DISK`, `D_TTY`, `D_MEM`, `D_TRACKCLOSE`, `D_MMAP_ANON`, `D_NEEDGIANT`, `D_NEEDMINOR`.
- `struct cdevsw` is the driver operation table with versioning and internal device lists.
- Device registration helpers: `DEV_MODULE*`, `make_dev*`, `make_dev_alias*`, `destroy_dev*`, `dev_ref*`, `dev_rel*`, `dev_depends()`.
- Clone support: `clone_setup()`, `clone_create()`, `clone_cleanup()`, `dev_stdclone()`, `dev_clone` eventhandler.
- Kernel dump support: dumper callback typedefs, `struct dumperinfo`, `dump_savectx()`, dumper insert/remove/create/destroy, and dump write lifecycle functions.

## Dependencies And Integration
Integrates with devfs, vnode device references, kernel modules, eventhandlers, credentials, GEOM/dump code, and the implementation in `sys/kern/kern_conf.c`.

## Risk Notes
This is a core driver ABI. `struct cdevsw` versioning, `struct cdev` lifetime, devfs private data ownership, and kernel dump callback contracts are compatibility- and concurrency-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/conf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cons.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cons.h

## Purpose
Defines the machine-independent console driver interface and kernel console entry points.

## Main Elements
- `struct consdev_ops` contains probe, init, term, getc, putc, grab, ungrab, and optional resume callbacks.
- `struct consdev` stores ops, priority, driver argument, capability flags, and console name.
- Console priorities: dead, low, normal, internal, remote.
- Flags: debugger-disabled and temporarily unavailable.
- `CONSOLE_DEVICE()` and `CONSOLE_DRIVER()` register console devices in the `cons_set` linker set.
- Kernel APIs include console init, add/remove/select, availability changes, grab/ungrab/resume, input polling/blocking, line input, output, constty attach/detach, and vty selection.

## Dependencies And Integration
Consumed by console drivers and implemented by `kern_cons.c`; integrates with tty redirection, message buffers, debugger paths, and `sc(4)`/`vt(4)` coexistence.

## Risk Notes
Console paths run during early boot and debugger/panic contexts. Driver callbacks must tolerate restricted locking and partial system initialization.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cons.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/consio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/consio.h

## Purpose
Defines the historical console/vty/video ioctl ABI for keyboard display mode, fonts, mouse cursor control, virtual terminal switching, screenshots, and video mode switching.

## Main Elements
- KD ioctls control text/graphics/pixel modes and raster text setup.
- Screen map, text attribute/color, blanking, saver, bell, history, and cursor shape ioctls.
- Mouse ioctl structs: `mouse_data`, `mouse_mode`, `mouse_event`, `mouse_info`.
- Font ioctls support fixed 8x8/8x14/8x16 fonts and variable fonts (`vfnt_t`).
- Video info/adapter wrappers mirror framebuffer ioctls.
- `scrshot` and `CONS_SCRSHOT` expose screen snapshots.
- `term_info` exposes terminal emulator metadata.
- VT ioctls support open query, process/kernel/auto switching mode, acknowledge release/acquire, activate, wait-active, get active/index, and switch locking.
- Large `SW_*` ioctl set maps legacy text/VGA/VESA mode names to mode IDs.

## Dependencies And Integration
Includes `sys/ioccom.h` and `sys/font.h`; used by syscons/vt drivers and userland console tools.

## Risk Notes
This is a broad legacy ABI. Ioctl numbers and struct layouts must remain stable even where names and behavior are historical or compatibility-only.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/consio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/copyright.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/copyright.h

## Purpose
Defines compiled-in FreeBSD copyright and trademark strings.

## Main Elements
- `COPYRIGHT_Vendor` can be supplied externally or defaults to empty.
- `COPYRIGHT_FreeBSD`, `TRADEMARK_Foundation`, and `COPYRIGHT_UCB` string macros.
- Defines global `copyright[]` and `trademark[]`.

## Dependencies And Integration
Used by kernel/userland components that embed or print system copyright and trademark text.

## Risk Notes
This header defines objects, not just declarations. Including it in multiple compilation units would create duplicate definitions unless the build expects that pattern.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/copyright.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/counter.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/counter.h

## Purpose
Declares the kernel scalable 64-bit counter interface and simple rate-check helper API.

## Main Elements
- `counter_u64_t` is a pointer-like opaque counter handle.
- Kernel APIs allocate/free, zero, and fetch counters.
- Array macros allocate, free, copy/fetch, and zero arrays of counters.
- `struct counter_rate` API supports rate checking and retrieving current rate.
- `COUNTER_U64_DEFINE_EARLY()` and sysinit/sysuninit helpers support early counters that become regular per-CPU counters later.

## Dependencies And Integration
In `_KERNEL`, includes `<machine/counter.h>` for MD counter primitives and early counter definitions.

## Risk Notes
Counters are optimized for concurrent updates. Consumers should use fetch/zero interfaces rather than assuming direct scalar storage semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/counter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/coverage.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/coverage.h

## Purpose
Defines shared kernel coverage comparison metadata and kernel registration hooks for coverage tracing.

## Main Elements
- Userspace must include through `sys/kcov.h`, enforced by a preprocessor error.
- Comparison flags encode constant comparisons and operand size.
- Kernel hook typedefs: program-counter trace and comparison trace callbacks.
- Registration APIs install/uninstall comparison and PC trace callbacks.

## Dependencies And Integration
Used by kernel coverage/KCOV instrumentation paths.

## Risk Notes
The callback interface is global. Registration and unregistration must coordinate with instrumented code paths that can execute on arbitrary CPUs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/coverage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cpu.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cpu.h

## Purpose
Declares CPU device ivars and the machine-independent cpufreq framework ABI.

## Main Elements
- CPU ivars expose `pcpu`, nominal MHz, and CPUID data.
- Inline helpers read CPU ivars from parent bus.
- `struct cf_setting` describes driver-provided frequency/voltage/power/latency settings.
- `struct cf_level` combines absolute and relative settings into exported CPU frequency levels.
- Cpufreq type flags distinguish absolute, relative, info-only, and uncached drivers.
- Priority constants arbitrate user, kernel, and emergency frequency requests.
- APIs: `cpufreq_register()`, `cpufreq_unregister()`, `cpufreq_settings_changed()`, `cpu_est_clockrate()`.
- Eventhandlers notify pre-change, post-change, and levels-changed listeners.

## Dependencies And Integration
Uses device/bus ivars, eventhandlers, TAILQ levels, and implementation in `kern_cpu.c`.

## Risk Notes
Frequency changes affect scheduling, thermal control, and power policy. Driver settings must use `CPUFREQ_VAL_UNKNOWN` for unknown fields and respect cpufreq method contracts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cpuctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cpuctl.h

## Purpose
Defines the `/dev/cpuctl` ioctl ABI for reading/writing MSRs, issuing CPUID, updating CPU microcode, and refreshing CPU feature evaluation.

## Main Elements
- `cpuctl_msr_args_t` carries MSR number and 64-bit data.
- `cpuctl_cpuid_args_t` carries CPUID level and four registers.
- `cpuctl_cpuid_count_args_t` adds CPUID level type/subleaf.
- `cpuctl_update_args_t` carries a user pointer and size for update data.
- Ioctls: `CPUCTL_RDMSR`, `CPUCTL_WRMSR`, `CPUCTL_CPUID`, `CPUCTL_UPDATE`, bit set/clear MSR ops, `CPUCTL_CPUID_COUNT`, `CPUCTL_EVAL_CPU_FEATURES`.

## Dependencies And Integration
Used by the cpuctl character device and privileged CPU management tools.

## Risk Notes
This ABI exposes privileged CPU state. Kernel handlers must validate CPU capabilities, permissions, update sizes, and architecture support.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cpuctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cpuset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cpuset.h

## Purpose
Defines CPU affinity bitset operations, cpuset selector constants, kernel cpuset structures, and userland cpuset syscall prototypes.

## Main Elements
- CPU bitset macros wrap generic `__BIT_*` operations for fixed and size-parametrized sets.
- Allocation macros support dynamic CPU set buffers.
- `CPU_LEVEL_*` and `CPU_WHICH_*` constants define affinity query/set targets.
- Reserved cpuset IDs: invalid and default.
- Kernel `struct cpuset` tracks refs, flags, hierarchy links, NUMA domain policy, ID, parent, and CPU mask.
- Kernel APIs manage refs, thread/process affinity, jail roots, interrupt-thread affinity, and string conversions.
- Userland prototypes expose `cpuset()`, set/get ID, and set/get affinity.

## Dependencies And Integration
Includes `_cpuset`, bitset, and queue headers. Implemented by `kern_cpuset.c` and tied to domainset, scheduler affinity, jails, and interrupt routing.

## Risk Notes
Bitset sizes are ABI-relevant. Kernel readers of `cs_mask` may see inconsistent results unless using the documented locking/ref rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cpuset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/crc16.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/crc16.h

## Purpose
Provides a table-driven inline CRC-16 calculation helper.

## Main Elements
- Declares external `crc16_table[256]`.
- `crc16()` updates an initial CRC over a byte buffer and returns the final 16-bit value.

## Dependencies And Integration
Includes `sys/types.h`; shared by kernel/userland code needing the same CRC implementation.

## Risk Notes
The table definition must match the intended polynomial. Callers must provide the correct initial CRC for their protocol.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/crc16.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/csan.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/csan.h

## Purpose
Declares conditional kernel concurrency sanitizer CPU initialization.

## Main Elements
- If `KCSAN` is enabled, declares `kcsan_cpu_init(u_int)`.
- Otherwise maps `kcsan_cpu_init(ci)` to a no-op.

## Dependencies And Integration
Includes `sys/types.h`. Used by CPU bring-up code without needing preprocessor conditionals at call sites.

## Risk Notes
The no-op fallback means callers cannot infer sanitizer availability from successful compilation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/csan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ctf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ctf.h

## Purpose
Defines the Compact C Type Format ABI structures and macros for CTF v2/v3 data embedded in ELF files.

## Main Elements
- Header structures: `ctf_preamble_t`, `ctf_header_t`, compression flag.
- Type records for v2/v3 short and long types, arrays, members, large members, labels, and enums.
- Magic/version constants with current `CTF_VERSION_3`.
- v2/v3 limits for vlen, size, large-size sentinel, type IDs, and parent/child encoding.
- Macros pack/unpack type info, names, integer/float encodings, large type sizes, and large member offsets.
- Defines CTF kind values for integer, float, pointer, array, function, struct, union, enum, forward, typedef, and qualifiers.
- Compatibility typedefs and macros map unsuffixed names to v2.

## Dependencies And Integration
Used by CTF generation/loading code and kernel linker CTF support. Includes `sys/_types.h`.

## Risk Notes
This is a binary format contract. Version-specific field widths and ID encodings must be matched by parsers, generators, and debugger consumers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ctf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ctype.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ctype.h

## Purpose
Provides simple kernel-only ASCII character classification and case conversion helpers.

## Main Elements
- Inline helpers: `isspace`, `isascii`, `isupper`, `islower`, `isalpha`, `isdigit`, `isxdigit`, `isprint`, `toupper`, `tolower`.
- All definitions are guarded by `_KERNEL`.

## Dependencies And Integration
Used by kernel code that cannot rely on libc ctype.

## Risk Notes
These are ASCII-only and do not perform locale-aware classification. Inputs outside plain byte/ASCII ranges follow the simple arithmetic tests.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ctype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/devctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/devctl.h

## Purpose
Declares kernel devctl event notification hooks.

## Main Elements
- `devctl_process_running()` reports whether the devctl consumer process is active.
- `devctl_notify()` sends system/subsystem/type/data events.
- `devctl_safe_quote_sb()` quotes strings into an sbuf.
- Hook type `send_event_f` and setters install or remove notification hooks.

## Dependencies And Integration
Kernel-only header used by device, devfs, bus, and subsystem code that emits devctl events.

## Risk Notes
Event payload strings are externally visible. Callers should quote and format data carefully to avoid ambiguous or unsafe devd input.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/devctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/devicestat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/devicestat.h

## Purpose
Defines the kernel/user ABI and kernel APIs for block/device I/O statistics exposed through devstat.

## Main Elements
- Constants: `DEVSTAT_NAME_LEN`, `DEVSTAT_DEVICE_NAME`, `DEVSTAT_VERSION`.
- Enums describe supported statistic features, transaction direction, tag type, priority/list ordering, and device type/interface flags.
- `struct devstat` records sequence counters, active/completed operations, busy time, creation time, block size, bytes/operations/durations per direction, tag counts, identity, and device metadata.
- Kernel APIs create/remove entries and start/end transactions directly or from `bio`.

## Dependencies And Integration
Includes queue and time headers; kernel side integrates with storage drivers, GEOM, CAM, and bio accounting.

## Risk Notes
`DEVSTAT_VERSION` must change when ABI-relevant layout or enum ordering changes. Sequence counters are used to read coherent snapshots from userland.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/devicestat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/devmap.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/devmap.h

## Purpose
Declares kernel static device mapping support for early boot MMU setup on platforms with `__HAVE_STATIC_DEVMAP`.

## Main Elements
- `struct devmap_entry` maps virtual address, physical address, and region size.
- APIs query last mapped KVA, add auto-allocated entries, register a platform table, bootstrap mappings, and print mappings.

## Dependencies And Integration
Kernel-only; used by MD early boot code and platform memory map setup.

## Risk Notes
Static mappings are established very early. Wrong address/size values can corrupt kernel virtual address layout or overlap other early mappings.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/devmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dirent.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/dirent.h

## Purpose
Defines the FreeBSD directory entry ABI returned by `getdirentries(2)` and helper sizing macros.

## Main Elements
- Declares `ino_t` and `off_t` if needed.
- `struct dirent` includes inode, next offset, record length, type, name length, explicit padding, and NUL-terminated `d_name`.
- `freebsd11_dirent` preserves the older ABI for compatibility/kernel use.
- Defines `DT_*` file type constants and `IFTODT`/`DTTOIF`.
- `_GENERIC_DIRLEN`, `_GENERIC_DIRSIZ`, min/max directory entry size macros.
- Kernel `dirent_terminate()` zeroes padding and NUL-terminates names.

## Dependencies And Integration
Consumed by filesystems, VFS directory reading, libc, and compatibility code.

## Risk Notes
Layout is ABI-critical. Comments explicitly note that `d_name` must remain last and padding is intentional to avoid LP64 ABI surprises.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/disk.h

## Purpose
Defines generic disk ioctls for geometry, media size, flushing, deletion, identifiers, physical paths, attributes, zoned commands, and kernel dump configuration.

## Main Elements
- Basic ioctls: sector size, media size, firmware sectors/heads, flush, delete.
- Identity/path ioctls: `DIOCGIDENT`, `DIOCGPROVIDERNAME`, `DIOCGPHYSPATH`.
- Optimal I/O layout ioctls: stripe size and stripe offset.
- Generic attribute structure `diocgattr_arg`.
- Zoned disk command ioctl `DIOCZONECMD`.
- Netdump/kernel dump ABI: `diocskerneldump_arg`, sentinel indices for remove/all/dev/append, and `DIOCSKERNELDUMP`/`DIOCGKERNELDUMP`.
- Kernel `disk_err()` declaration.

## Dependencies And Integration
Includes `ioccom`, `kerneldump`, `disk_zone`, socket/network headers for netdump, and is used by GEOM/disk providers and disk utilities.

## Risk Notes
Disk identifiers are documented as optional and not guaranteed unique except under specific physical-storage assumptions. Kernel dump fields include user pointers and encryption/compression metadata requiring careful validation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk/apm.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/disk/apm.h

## Purpose
Defines Apple Partition Map on-disk structures and known partition type strings.

## Main Elements
- `struct apm_ddr` driver descriptor record with signature, block size, and block count.
- `struct apm_ent` partition map entry with signature, map block count, start, size, name, and type.
- Constants for APM signatures and name/type field lengths.
- Partition type strings for self/free, FreeBSD variants, Apple boot/HFS/UFS.

## Dependencies And Integration
Includes `sys/types.h`; consumed by partition parsing and GEOM partition code.

## Risk Notes
Fields model an on-disk big-endian historical format. Parsers must handle byte order and fixed-size non-NUL-padded strings correctly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk/apm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk/bsd.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/disk/bsd.h

## Purpose
Defines the historical BSD disklabel on-disk structure, partition records, magic values, drive types, filesystem type codes, and disk flags.

## Main Elements
- `BSD_MAGIC`, min/max partition counts, bootblock size, raw and swap partition indices.
- `struct disklabel` stores geometry, hardware characteristics, flags, drive data, checksum, and partition table.
- `struct partition` stores size, offset, filesystem fragment details, filesystem type, and cylinders per group.
- Drive type constants include SCSI, ESDI, ST506, floppy, CCD, Vinum, RAID, JFS2.
- Filesystem type constants cover swap, FFS, MSDOS, LFS, ISO9660, boot, Vinum, RAID, ext2, NTFS, HAMMER/HAMMER2, UDF, ZFS, NANDFS.
- Disk flags include removable, ECC, bad-sector forwarding, RAM disk, and chained transfers.

## Dependencies And Integration
Included by `sys/disklabel.h` and partition/disklabel parsing code.

## Risk Notes
The structure is an on-disk ABI. The compile-time size assertion documents expected layout for the minimum partition count.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk/bsd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk/gpt.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/disk/gpt.h

## Purpose
Defines GPT header/entry structures and a large catalog of known GPT partition type GUID constants.

## Main Elements
- Generic `gpt_uuid` definition unless callers provide `GPT_UUID_TYPE`.
- `struct gpt_hdr` models the EFI GPT header and includes explicit padding to keep `hdr_size`/`offsetof` behavior predictable.
- `GPT_MIN_RESERVED` documents the UEFI-required 16 KiB entry reservation.
- `struct gpt_ent` models 128-byte GPT entries with type GUID, entry GUID, LBA range, attributes, and UTF-16 name.
- Entry attributes include platform-required, bootme, bootonce, and bootfailed.
- GUID constants cover unused, EFI, MBR, FreeBSD variants, Microsoft, Linux, VMware, Apple, NetBSD, DragonFlyBSD, ChromeOS, OpenBSD, Solaris, HiFive, U-Boot env, XBOOTLDR, and BIOS boot.

## Dependencies And Integration
Used by GPT partition readers/writers and GEOM partition code.

## Risk Notes
GPT structure sizes are ABI/on-disk critical. GUID byte order follows GPT/DCE layout and must match parser formatting/conversion code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk/gpt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk/mbr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/disk/mbr.h

## Purpose
Defines MBR layout constants, DOS partition type IDs, and the 16-byte MBR partition entry structure.

## Main Elements
- Offsets for boot sector, drive serial, partition table, magic, and partition entry size/count.
- Partition type constants for FAT, NTFS, extended, PReP, LDM, DragonFlyBSD, Linux, FreeBSD/386BSD, Apple, protective GPT, EFI, VMware, RAID.
- `struct dos_partition` stores CHS start/end, type, absolute start sector, and sector count.
- `DPSECT` and `DPCYL` decode CHS sector/cylinder fields.

## Dependencies And Integration
Used by MBR partition parsing and `sys/diskmbr.h`.

## Risk Notes
The size assertion fixes `struct dos_partition` at 16 bytes. CHS fields are legacy and should not be trusted for modern addressing when LBA fields exist.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk/mbr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk_zone.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/disk_zone.h

## Purpose
Defines the generic ioctl payloads and constants for zoned block devices using SCSI ZBC or ATA ZAC semantics.

## Main Elements
- `disk_zone_disk_params` reports zone mode, supported commands, optimal/max open/sequential zone counts.
- `disk_zone_rwp` describes reset-write-pointer/open/close/finish targets and all-zones flag.
- `disk_zone_rep_header` and `disk_zone_rep_entry` describe report-zones output.
- `disk_zone_report` carries report request options, entry allocation/fill counts, and user entry pointer.
- `disk_zone_args` selects zone command: open, close, finish, report, reset write pointer, get params.
- Constants define zone modes, feature flags, same-layout values, zone types, conditions, flags, and report filters.

## Dependencies And Integration
Included by `sys/disk.h` for `DIOCZONECMD` and consumed by zoned disk drivers and tools.

## Risk Notes
The entry pointer and counts cross the ioctl boundary. Kernel handlers must carefully bound copyin/copyout and account for future SCSI/ATA values not yet named here.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disk_zone.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disklabel.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/disklabel.h

## Purpose
Wraps BSD disklabel definitions with FreeBSD naming, checksum, endian encode/decode declarations, and optional userland helpers.

## Main Elements
- Includes `sys/disk/bsd.h` and maps `DISKMAGIC`, `BBSIZE`, `RAW_PART`, `SWAP_PART`, `NDDATA`, and `NSPARE`.
- Defines label sector and offset.
- `dkcksum()` computes the XOR checksum over label data through active partitions.
- Optional `dktypenames` and `fstypenames` tables are emitted when requested by macros.
- Declares little-endian partition and disklabel encode/decode helpers.
- Userland declares `getdiskbyname()`.

## Dependencies And Integration
Used by disklabel consumers in kernel and userland, including compatibility and partitioning tools.

## Risk Notes
Checksum range depends on `d_npartitions`; corrupted or untrusted labels must validate partition count before relying on checksum traversal.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/disklabel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/diskmbr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/diskmbr.h

## Purpose
Provides the historical MBR write ioctl definition.

## Main Elements
- Includes MBR layout definitions and ioctl helpers.
- Defines `DIOCSMBR` as an ioctl writing a 512-byte MBR buffer.

## Dependencies And Integration
Used by disk management tools/drivers that update MBR contents.

## Risk Notes
Writing raw MBR data is destructive if misused. Kernel handlers must enforce permissions and device safety policy.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/diskmbr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dkstat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/dkstat.h

## Purpose
Compatibility header for disk statistics-related consumers.

## Main Elements
- Contains licensing/header guard.
- Includes `sys/resource.h`.

## Dependencies And Integration
Provides a legacy include name for code expecting `<sys/dkstat.h>`.

## Risk Notes
This header does not define disk statistics structures itself; consumers need the actual resource/devstat interfaces for data.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dkstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dnv.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/dnv.h

## Purpose
Declares default-returning nvlist lookup and take helpers.

## Main Elements
- `dnvlist_get_*` returns a typed value or caller-provided default when the named value is absent or of another type.
- `dnvlist_take_*` removes and returns the typed value or returns caller-provided default.
- Supported types include bool, number, string, nvlist, descriptor, and binary.

## Dependencies And Integration
Uses `sys/_nv.h`; outside kernel it includes standard types and `sys/nv_namespace.h`.

## Risk Notes
Pointer defaults and returned pointers have different ownership semantics depending on get versus take. Callers must not free internal get results.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dnv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/domain.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/domain.h

## Purpose
Defines networking protocol domain registration structures and kernel domain add/remove hooks.

## Main Elements
- `struct domain` contains list linkage, address family, protocol switch count/name, flags, optional probe, routing table attach/detach hooks, and flexible `protosw` array.
- Domain flag `DOMF_UNLOADABLE`.
- Kernel exports domain initialization status and global domain list.
- `domain_add()` and `domain_remove()` manage registered domains.
- `DOMAIN_SET()` creates SYSINIT/SYSUNINIT registration for a domain.

## Dependencies And Integration
Used by protocol families, routing table setup, VIMAGE virtual network initialization, and network stack domain discovery.

## Risk Notes
Protocol domain arrays and routing hooks are core network ABI inside the kernel. Module unloadability requires careful teardown ordering.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/domain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/domainset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/domainset.h

## Purpose
Defines NUMA memory-domain bitset operations, domainset policies, kernel domainset structures, and userland cpuset-domain APIs.

## Main Elements
- `DOMAINSET_*` macros wrap generic bitset operations over `DOMAINSET_SETSIZE`.
- `DOMAINSETBUFSIZ` sizes textual domainset formatting with policy and max domain values.
- Policies: invalid, round-robin, first-touch, prefer, interleave.
- Kernel `struct domainset` stores allowed mask, policy, preferred domain, count, and iteration order.
- Predefined domainsets: first-touch, interleave, fixed, prefer, round-robin.
- Kernel APIs initialize, create/intern, remove empty VM domains, and populate/validate domainsets.
- Userland APIs: `cpuset_getdomain()` and `cpuset_setdomain()`.

## Dependencies And Integration
Works with cpuset, VM memory domains, jails/process affinity, and `kern_cpuset.c`.

## Risk Notes
Policy/mask validation is crucial: empty or out-of-range domain masks can break allocation policy. `domainid_t` width changes with `MAXMEMDOM`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/domainset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dtrace_bsd.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/dtrace_bsd.h

## Purpose
Declares FreeBSD shims and hook variables used by DTrace and related providers.

## Main Elements
- Trap hooks: `dtrace_trap_func`, `dtrace_doubletrap_func`.
- pid/return probe hooks and virtual-time switch hook.
- Fasttrap fork/exec/exit hooks.
- malloc probe hook.
- NFS client provider hooks for access cache, attribute cache, and RPC start/done probes across old/new NFS client naming.
- Kernel DTrace private storage sizing and constructor/destructor hooks for proc/thread.
- Time helpers: `dtrace_gethrtime()` and `dtrace_gethrestime()`.

## Dependencies And Integration
Used by DTrace modules, trap handling, fork/exec/exit, malloc, NFS client code, and proc/thread lifecycle code.

## Risk Notes
Most entries are global function pointers invoked from hot or sensitive kernel paths. Registration must ensure null checks, module lifetime safety, and trap recursion avoidance.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dtrace_bsd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dvdio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/dvdio.h

## Purpose
Defines DVD authentication and structure-read ioctl ABI.

## Main Elements
- `struct dvd_layer` describes physical layer fields and sector ranges.
- `struct dvd_struct` carries read-structure format, layer, flags, length, and 2048-byte data buffer.
- `struct dvd_authinfo` carries CSS/RPC authentication state, region fields, LBA, and key/challenge bytes.
- Constants name DVD structure formats, report-key formats, send-key formats, and invalid AGID.
- Ioctls: `DVDIOCREPORTKEY`, `DVDIOCSENDKEY`, `DVDIOCREADSTRUCTURE`.

## Dependencies And Integration
Used by optical media drivers and userland DVD tools.

## Risk Notes
The ABI uses C bitfields, so it is compiler/layout sensitive within the supported platform ABI. Authentication data sizes are fixed and must be copied carefully.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/dvdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efi-edk2.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/efi-edk2.h

## Purpose
Adapts EDK2 type names, calling-convention macros, and processor defines for FreeBSD builds that reuse EDK2-derived headers/code.

## Main Elements
- Defines EDK2 integer, pointer, character, boolean, and void type aliases.
- Defines or suppresses EFI API syntax macros such as `EFIAPI`, `IN`, `OUT`, `CONST`, `OPTIONAL`, and `INTERFACE_DECL`.
- Undefines conflicting `NULL`, `EFI_PAGE_SIZE`, `EFI_PAGE_MASK`, `MAX`, and `MIN`.
- Sets `NO_MSABI_VA_FUNCS` outside standalone loader builds.
- Defines `MDE_CPU_*` based on compiler architecture.
- Defines `MAX_BIT` based on long width.

## Dependencies And Integration
Includes standard integer headers and is used when importing EDK2 headers into FreeBSD kernel/userland/loader contexts.

## Risk Notes
Calling convention handling differs for standalone amd64 loader versus kernel/userland. Include order with `sys/param.h` can matter due to `MAX`/`MIN` collisions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efi-edk2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efi-freebsd.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/efi-freebsd.h

## Purpose
Provides minimal FreeBSD definitions needed by EFI-related code without pulling in the full EDK2 compatibility layer.

## Main Elements
- Header guard and license.
- Includes `sys/_null.h`.

## Dependencies And Integration
Included by `sys/efi.h` to supply minimal FreeBSD-side definitions for EFI type compatibility.

## Risk Notes
Intentionally minimal; consumers needing EDK2 aliases must include the EDK2 adapter rather than assuming this header defines them.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efi-freebsd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efi.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/efi.h

## Purpose
Defines FreeBSD EFI/UEFI data structures, GUIDs, memory descriptors, runtime service interfaces, and kernel EFI operation wrappers.

## Main Elements
- Page constants and known configuration table GUIDs for SMBIOS, ESRT, properties, memory attributes, and Linux memreserve.
- EFI reset enum, EFI character/status types, and `efi_guid_t`.
- Configuration table, memory descriptor, time, time capabilities, table header, ESRT, properties, and memory attribute table structures.
- Kernel runtime table `struct efi_rt` when EFI ABI attributes are available.
- Kernel system table `struct efi_systbl` and `efi_systbl_phys`.
- Linux EFI memreserve linked-table structures.
- MD EFI functions for entering/leaving EFI calls, physical-to-KVA, runtime arch calls, and 1:1 maps.
- `struct efi_ops` virtualizes EFI runtime/table/variable/time operations.
- Inline public wrappers return `ENXIO` when the active operation is unavailable.
- `efi_status_to_errno()` maps EFI statuses to errno.

## Dependencies And Integration
Includes `machine/efi.h` and `sys/efi-freebsd.h`; integrates with EFI runtime services, loader-provided metadata, platform firmware, and `/dev/efi`.

## Risk Notes
Runtime EFI calls are firmware-sensitive and may require special mappings/calling conventions. The operation table permits hypervisor-specific backends, so callers must handle `ENXIO`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efi_map.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/efi_map.h

## Purpose
Declares kernel helpers for iterating and applying EFI memory map metadata.

## Main Elements
- `efi_map_entry_cb` callback type for `struct efi_md` entries.
- `efi_map_foreach_entry()` iterates entries in an EFI map header.
- `efi_map_add_entries()` and `efi_map_exclude_entries()` apply map entries to kernel memory management.
- `efi_map_print_entries()` prints entries.

## Dependencies And Integration
Kernel-only; includes `sys/efi.h` and `machine/metadata.h`.

## Risk Notes
EFI memory map interpretation affects physical memory availability and exclusions. Misclassification can reserve usable memory or use firmware-reserved memory unsafely.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efi_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efiio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/efiio.h

## Purpose
Defines `/dev/efi` ioctl payloads for EFI table lookup, time, variable, and wake-time operations.

## Main Elements
- `efi_get_table_ioctl` carries userspace buffer pointer, EFI GUID, table length, and buffer length.
- `efi_var_ioctl` carries wide-char variable name, vendor GUID, attributes, data pointer, and byte size.
- `efi_waketime_ioctl` carries wake time and enabled/pending flags.
- Ioctls: get table, get/set time, variable get/next/set, get/set wake time.
- Compatibility `_WANT_EFI_IOC` structures preserve old `struct uuid` field names for pre-16 userland.
- Static assertions verify UUID and EFI GUID size/layout compatibility for ioctl structs.

## Dependencies And Integration
Includes `ioccom`, `uuid`, and `efi`. Used by EFI device driver and userland EFI variable/table tools.

## Risk Notes
The new ABI uses `efi_guid_t`; old compatibility structs are planned for removal in FreeBSD 16. Ioctl handlers must validate user pointers and byte-vs-wide-character sizes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/efiio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/elf.h

## Purpose
Solaris-compatible umbrella header for ELF definitions.

## Main Elements
- Includes `sys/types.h`, machine-specific ELF definitions, `sys/elf32.h`, and `sys/elf64.h`.

## Dependencies And Integration
Used by code expecting `<sys/elf.h>` to provide both class-independent and class-specific ELF types.

## Risk Notes
Actual machine relocation and ABI constants come from `machine/elf.h` and common ELF headers, not this wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf32.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/elf32.h

## Purpose
Defines class-dependent ELF32 scalar types, structures, and field packing macros common to all 32-bit ELF architectures.

## Main Elements
- ELF32 scalar typedefs for addresses, offsets, words, signed words, sizes, and hash elements.
- Structures: ELF header, MIPS liblist, section header, program header, dynamic entry, relocations, RELR, note header, move entry, capabilities, symbol table, version definitions/needs, symbol info, and compressed section header.
- Macros pack/unpack relocation info, move info, symbol binding/type, and symbol visibility.

## Dependencies And Integration
Includes `sys/elf_common.h`; used by loaders, linkers, kernel module code, debuggers, and ELF parsers.

## Risk Notes
Structure layouts mirror the ELF specification. Architecture-specific relocation IDs and machine flags are defined elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf64.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/elf64.h

## Purpose
Defines class-dependent ELF64 scalar types, structures, and field packing macros common to all 64-bit ELF architectures.

## Main Elements
- ELF64 scalar typedefs for addresses, offsets, words, extended words, sizes, signed sizes, and hash elements.
- Structures: ELF header, MIPS liblist, section header, program header, dynamic entry, relocations, RELR, note header, move entry, capabilities, symbol table, version definitions/needs, symbol info, and compressed section header.
- Macros pack/unpack relocation info, including type-data/type-id variants, move info, symbol binding/type, and symbol visibility.

## Dependencies And Integration
Includes `sys/elf_common.h`; used by ELF consumers across kernel and userland for 64-bit objects.

## Risk Notes
`Elf64_Hashelt` is noted as inconsistent among 64-bit architectures, so machine-dependent headers may override or refine expectations. Structure layout is ELF ABI-critical.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf64.h -->