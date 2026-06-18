# Group Research: group_1281_netbsd_src_sources_os_bsd_netbsd_src_sys_sys_common_int_limits_h_so_6bcdd2e2b80e

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_limits.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_limits.h

Defines the C99 `<stdint.h>`/`<inttypes.h>` integer limit macros using compiler-provided builtin macros such as `__INT8_MAX__`, `__UINTPTR_MAX__`, and `__SIZE_MAX__`.

Key content:
- Exact-width limits: `INT8_MIN/MAX`, `UINT8_MAX`, through 64-bit.
- Least/fast integer limits: `INT_LEAST*`, `UINT_FAST*`.
- Pointer and maximum-width limits: `INTPTR_*`, `UINTPTR_MAX`, `INTMAX_*`.
- Other type limits: `PTRDIFF_*`, `SIG_ATOMIC_*`, `SIZE_MAX`.

Important behavior:
- Fails preprocessing if the compiler lacks `__SIG_ATOMIC_MAX__`.
- Signed minima are expressed as `(-MAX-1)` to avoid direct unrepresentable literal constants.
- This is ABI-sensitive infrastructure for system headers, not runtime code.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_limits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_mwgwtypes.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_mwgwtypes.h

Provides common typedefs for minimum-width, fastest minimum-width, and greatest-width C99 integer types from compiler builtin type macros.

Key content:
- `int_least8_t` through `int_least64_t` and unsigned variants.
- `int_fast8_t` through `int_fast64_t` and unsigned variants.
- `intmax_t` and `uintmax_t`.

Important behavior:
- Requires `__UINT_FAST64_TYPE__`; otherwise emits a preprocessor error.
- Relies entirely on compiler ABI definitions, keeping NetBSD integer typedefs aligned with the target compiler.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_mwgwtypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_types.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_types.h

Defines NetBSD internal exact-width integer typedefs and pointer-sized integer typedefs from compiler builtin type macros.

Key content:
- Internal exact-width types: `__int8_t`, `__uint8_t`, through `__int64_t`, `__uint64_t`.
- Defines `__BIT_TYPES_DEFINED__`.
- Pointer integer types: `__intptr_t`, `__uintptr_t`.

Important behavior:
- Requires `__UINTPTR_TYPE__`; otherwise emits a preprocessor error.
- This header is a low-level ABI bridge used by public type headers.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_limits.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_limits.h

Defines common scalar limits for `<limits.h>`-style consumers using compiler builtin constants and NetBSD feature-test gates.

Key content:
- Character, short, int, long, and unsigned limits.
- C99/NetBSD long long limits: `LLONG_*`, `ULLONG_MAX`.
- POSIX/XOpen/NetBSD values such as `SSIZE_MAX`, `LONG_BIT`, `WORD_BIT`.
- NetBSD-only aliases: `SSIZE_MIN`, `SIZE_T_MAX`, `UQUAD_MAX`, `QUAD_*`.
- Floating-point limit exposure under XOpen/NetBSD: `DBL_*`, `FLT_*`, optionally `LDBL_*`.

Important behavior:
- Uses `<sys/featuretest.h>` to control namespace exposure.
- Unsigned maxima are computed from signed maxima for core integer types.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_limits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_lock.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_lock.h

Implements machine-dependent simple spinlock primitives using compiler atomic builtins, intended for ports that use the shared implementation.

Key content:
- Lock state tests: `__SIMPLELOCK_LOCKED_P`, `__SIMPLELOCK_UNLOCKED_P`.
- Direct state setters/initializers.
- Spin acquisition via `__atomic_exchange_n(..., __ATOMIC_ACQUIRE)`.
- Try-lock and release via `__atomic_store_n(..., __ATOMIC_RELEASE)`.

Important behavior:
- Assumes `__cpu_simple_lock_t`, `__SIMPLELOCK_LOCKED`, and `__SIMPLELOCK_UNLOCKED` are supplied by machine headers.
- Clear/set/init currently use direct stores under `#if 1`, with atomic-store alternatives retained but disabled.
- Provides low-level synchronization semantics used below higher-level kernel locks.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_wchar_limits.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_wchar_limits.h

Defines wide-character and wide-integer limit macros from compiler-provided builtin limits.

Key content:
- `WCHAR_MIN`, `WCHAR_MAX`.
- `WINT_MIN`, `WINT_MAX`.

Important behavior:
- Fails preprocessing if `__WCHAR_MIN__`/`__WCHAR_MAX__` or `__WINT_MIN__`/`__WINT_MAX__` are unavailable.
- Keeps wide-character ABI limits aligned with compiler target definitions.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_wchar_limits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/compat_stub.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/compat_stub.h

Central registry of module hooks and legacy vectors used to decouple optional compatibility modules from core kernel code.

Key content:
- Includes `module_hook.h`, `param.h`, socket and signal type headers.
- Legacy direct vectors for NTP and SCTP compatibility callbacks.
- `MODULE_HOOK` declarations for old USB structs, ccd, clockctl, sppp, cryptodev, RAIDframe, puffs, wscons, sysmon, vnd, ieee80211, if/tty/socket/routing compatibility, old modstat, netbsd32, SunOS emulation, random ioctl, sysvipc, coredump formats, amd64 old syscall handling, and removed IPv6 neighbor-discovery compatibility.
- Exposes `kern_sig_43_pgid_mask`.

Important behavior:
- Header warns that changes require kernel version updates in `sys/param.h` so kernel/modules remain synchronized.
- Mostly forward-declares structs to avoid broad includes.
- Critical for loadable compatibility code paths and ABI preservation across NetBSD releases.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/compat_stub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/condvar.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/condvar.h

Declares NetBSD kernel condition variable type and operations.

Key content:
- `kcondvar_t` is an opaque two-pointer structure.
- Kernel APIs: `cv_init`, `cv_destroy`, wait variants, timed wait variants, signal, broadcast.
- Timed APIs support tick-based and `bintime` timeout forms, with interruptible `_sig` variants.
- Introspection helpers: `cv_has_waiters`, `cv_is_valid`.
- Global `lbolt`, awakened once per second by the clock interrupt.

Important behavior:
- Declarations are only exposed to `_KERNEL`.
- Wait APIs pair with `struct kmutex`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/condvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/conf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/conf.h

Defines core block/character device switch interfaces, line discipline tables, and device major/minor conversion helpers.

Key content:
- Device flag classes: `D_TAPE`, `D_DISK`, `D_TTY`, `D_MPSAFE`, `D_NEGOFFSAFE`.
- `struct bdevsw` and `struct cdevsw` operation vectors.
- Kernel helpers to attach/detach and look up device switches.
- Typedefs and macros for driver operation signatures.
- Default no-op/error operation aliases such as `noopen`, `nullopen`, `nommap`, `nokqfilter`.
- Block and character wrapper declarations: `bdev_open`, `cdev_read`, etc.
- `struct linesw` and line discipline registration/lookup APIs.
- `/dev/mem`, `/dev/null`, `/dev/zero`, `/dev/full` minor constants.
- `struct devsw_conv` for dev node metadata and conversion tables.
- Root/swap configuration declarations.

Important behavior:
- Forms a major part of the kernel device-driver ABI.
- Pulls in `device_if.h`, `queue.h`, and `types.h`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/conf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/container_of.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/container_of.h

Provides type-checked `container_of` and `const_container_of` macros for recovering an enclosing structure from an embedded field pointer.

Key content:
- Includes `<sys/stddef.h>` for `offsetof`.
- Validation macros compare the supplied pointer type with the target field type through a zero-sized arithmetic expression.
- Coverity/LGTM builds skip validation to avoid analyzer warnings.

Important behavior:
- `container_of(PTR, TYPE, FIELD)` subtracts `offsetof(TYPE, FIELD)` from `PTR`.
- `const_container_of` preserves constness.
- The validation expression is compile-time only and should not affect generated code.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/container_of.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/core.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/core.h

Defines the traditional NetBSD core dump file header and segment header formats.

Key content:
- Magic constants: `COREMAGIC`, `CORESEGMAGIC`.
- `CORE_GETMAGIC`, `CORE_GETMID`, `CORE_GETFLAG`, `CORE_SETMAGIC` for packed network-byte-order `c_midmag`.
- Segment flags: `CORE_CPU`, `CORE_DATA`, `CORE_STACK`.
- `struct core` and `struct coreseg`.
- 32-bit variants: `struct core32`, `struct coreseg32`.

Important behavior:
- Includes `<sys/endian.h>` for `ntohl`/`htonl`.
- Uses `MAXCOMLEN` via included machine/a.out context.
- File format is ABI-visible to crash/core analysis tools.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/core.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cprng.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cprng.h

Declares the kernel cryptographic pseudo-random number generator interface.

Key content:
- Includes NIST hash DRBG and fast CPRNG headers.
- `CPRNG_MAX_LEN` aliases `NIST_HASH_DRBG_MAX_REQUEST_BYTES`.
- Opaque `cprng_strong_t`.
- Initialization and lifecycle APIs: `cprng_init`, `cprng_strong_create`, `cprng_strong_destroy`.
- Random extraction: `cprng_strong`, `cprng_strong32`, `cprng_strong64`.
- Flags: `CPRNG_INIT_ANY`, `CPRNG_REKEY_ANY`, `CPRNG_USE_CV`, `CPRNG_HARD`.
- Global generators: `kern_cprng`, `user_cprng`.

Important behavior:
- Header guard deliberately remains `_CPRNG_H` for external compatibility.
- Intended for kernel entropy consumers at different IPL/thread constraints.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cprng.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cpu.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cpu.h

Declares machine-independent CPU management hooks and scheduler/preemption interfaces.

Key content:
- Includes `<machine/cpu.h>` and `<sys/lwp.h>`.
- Optional MD overrides for `cpu_idle`, `cpu_need_resched`, and CPU iteration.
- CPU lookup/model/state/intr APIs.
- Kernel preemption entry/exit helpers.
- Interrupt accounting and topology functions.
- Globals: `cpu_lock`, `maxcpus`, `cpu_infos`, `kcpuset_attached`, `kcpuset_running`.
- Inline helpers: `cpu_index`, `cpu_name`.
- CPU microcode support under `CPU_UCODE`.
- Reschedule flags: `RESCHED_REMOTE`, `RESCHED_IDLE`, `RESCHED_UPREEMPT`, `RESCHED_KPREEMPT`.

Important behavior:
- Wrapped to exclude most C declarations from `_LOCORE`.
- Acts as MI facade over MD CPU structures.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cpu_data.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cpu_data.h

Defines the machine-independent per-CPU data embedded in each machine-dependent `cpu_info`.

Key content:
- `enum cpu_count` enumerates per-CPU counters for context switches, syscalls, traps, interrupts, faults, UVM page/fault stats, and sync activity.
- `enum cpu_rel` describes topology peer rings: core, package, first CPU per package.
- `struct cpu_data` stores CPU index, cross-call state, pserialize depth, pending IPIs, scheduler state, topology IDs/siblings, idle LWP, lock counters, softints, UVM/callout/select/vfs-cache per-CPU pointers, lockdebug state, cycle counter metadata, CPU name, per-CPU kcpuset, PCU current LWPs, counters, and heartbeat tracking.
- Many `ci_*` compatibility macros map `struct cpu_info` fields to `ci_data`.
- `CPU_COUNT(idx, d)` updates counters with preemption disabled.
- `cpu_count_get`, `cpu_count`, and `cpu_count_sync`.

Important behavior:
- Comments require adding counters in blocks of 8.
- Structure layout is size-sensitive because many ports embed it in constrained MD CPU structures.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cpu_data.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cpufreq.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cpufreq.h

Defines the CPU frequency state interface shared between kernel and ioctl-facing structures.

Key content:
- Limits: `CPUFREQ_NAME_MAX`, `CPUFREQ_STATE_MAX`, `CPUFREQ_LATENCY_MAX`.
- State markers: `CPUFREQ_STATE_ENABLED`, `CPUFREQ_STATE_DISABLED`.
- `struct cpufreq_state`: frequency in MHz, power in mW, latency in usec, index, reserved fields.
- `struct cpufreq`: name, state counts/target/current, reserved fields, CPU/backend index, plus kernel-only backend state and xcall callbacks.
- Kernel APIs to register/deregister, suspend/resume, get/set frequencies, and query states.

Important behavior:
- Kernel builds include `sys/xcall.h`.
- Non-kernel builds include `stdbool.h`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cpufreq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cpuio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cpuio.h

Defines user/kernel ioctl ABI for CPU state control and CPU microcode updates.

Key content:
- `cpustate_t` contains CPU id, online/intr flags, last modification time split fields, name, interrupt count, hardware id, and reserved fields.
- Ioctls: `IOC_CPU_SETSTATE`, `IOC_CPU_GETSTATE`, `IOC_CPU_GETCOUNT`, `IOC_CPU_MAPID`.
- Microcode version structure `cpu_ucode_version`.
- i386-specific 64-bit compatibility structure for amd64 kernels.
- `struct cpu_ucode` with loader version, CPU selector, firmware name.
- CPU selector constants: `CPU_UCODE_ALL_CPUS`, `CPU_UCODE_CURRENT_CPU`.
- Ioctls: `IOC_CPU_UCODE_GET_VERSION`, `IOC_CPU_UCODE_APPLY`.

Important behavior:
- Includes `PATH_MAX` for firmware name sizing outside the kernel.
- Stable ABI for `/dev/cpu`-style control paths.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cpuio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/crashme.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/crashme.h

Declares the kernel crashme node registration interface used for controlled crash/panic testing hooks.

Key content:
- `crashme_fn` callback type returning `int`.
- `struct crashme_node` stores short name, long name, callback, sysctl id, and linked-list pointer.
- APIs: `crashme_add`, `crashme_remove`.

Important behavior:
- Comments explicitly avoid marking callbacks `__dead`; crashme failures should return to the caller so setup or errors can be handled.
- Callback returns zero on success and nonzero when plain `panic()` should be called.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/crashme.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/csan.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/csan.h

Declares KCSAN kernel concurrency sanitizer initialization hooks.

Key content:
- Includes `opt_kcsan.h` when `_KERNEL_OPT` is defined.
- Includes `<sys/types.h>`.
- Under `KCSAN`: declares `kcsan_init` and `kcsan_cpu_init`.
- Without `KCSAN`: both macros compile to `__nothing`.

Important behavior:
- Provides zero-cost stubs when sanitizer support is disabled.
- `kcsan_cpu_init` takes `struct cpu_info *` without a local forward declaration, relying on surrounding kernel context.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/csan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ctype_bits.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ctype_bits.h

Defines character classification bit masks and declares ctype lookup tables.

Key content:
- Classification bits: alpha, control, digit, graph, lower, punct, space, upper, xdigit, blank, print, ideogram, special, phonogram.
- Declares active locale/table pointers: `_ctype_tab_`, `_tolower_tab_`, `_toupper_tab_`.
- Declares C locale backing tables: `_C_ctype_tab_`, `_C_toupper_tab_`, `_C_tolower_tab_`.

Important behavior:
- Uses `__BEGIN_DECLS`/`__END_DECLS` for C++ compatibility.
- Shared by inline ctype macro definitions.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ctype_bits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ctype_inline.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ctype_inline.h

Defines inline macro implementations for classic ctype and case conversion APIs.

Key content:
- Includes `sys/cdefs.h`, `sys/featuretest.h`, and `sys/ctype_bits.h`.
- Macros: `isalnum`, `isalpha`, `iscntrl`, `isdigit`, `isgraph`, `islower`, `isprint`, `ispunct`, `isspace`, `isupper`, `isxdigit`, `tolower`, `toupper`.
- XOpen/NetBSD extensions: `isascii`, `toascii`, `_tolower`, `_toupper`.
- C99/POSIX/NetBSD `isblank` exposure.

Important behavior:
- Uses `(_ctype_tab_ + 1)[c]` table indexing, supporting EOF-style indexing conventions.
- Namespace exposure is controlled by feature-test macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ctype_inline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/debug.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/debug.h

Declares small kernel debug initialization and free-check instrumentation hooks.

Key content:
- Requires `_KERNEL`; user-level inclusion is rejected with `#error`.
- `debug_init`.
- `freecheck_out` and `freecheck_in`.
- Macros `FREECHECK_OUT` and `FREECHECK_IN`.

Important behavior:
- Free-check macros call real functions only when both `DEBUG` and `_HARDKERNEL` are defined.
- Otherwise they compile away.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/device.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/device.h

Public NetBSD autoconfiguration and device framework header.

Key content:
- Device classes: generic, CPU, disk, network, tape, tty, audio, display, bus, virtual.
- Device activation enums and typedefs for `device_t`, `cfdata_t`, `cfdriver_t`, `cfattach_t`.
- `devhandle_t` abstraction for ACPI/OpenFirmware/FDT/OpenBoot/private handles.
- Device compatibility entries and handle implementation types.
- Device call registration macros and descriptors.
- Configuration data structures: locators, interface attributes, parents, `cfdata`, `cftable`, `cfattach`, `cfdriver`, `cfattachinit`.
- Attach declaration macros and detach flags.
- Search/attach argument structure `cfargs` and `CFARGS` helper.
- Kernel APIs for config initialization, attach/detach, deferred config, device lookup/refcounting, registration, properties, compatibility matching, power management, iteration, shutdown traversal, and generic device calls.

Important behavior:
- Separates public framework contracts from private layout in `device_impl.h`.
- Device property API supports typed access and defaults for data, strings, booleans, and integer sizes.
- Core header for driver attachment and runtime device tree operations.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/device.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/device_calls.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/device_calls.h

Generated typed wrappers for generic device autoconfiguration calls.

Key content:
- Generated from `device_calls`; file warns not to edit manually.
- Includes `<sys/device.h>`.
- `device-enumerate-children` args and binding macro.
- `device-register` args and binding macro.
- `device-is-system-todr` optional RTC/TODR filter.
- `device-get-property` args and binding macro, with extensive contract documentation for property type, size, encoding, and errors.

Important behavior:
- Uses `struct device_call_generic` compatibility so typed wrappers can be passed to `device_call`/`devhandle_call`.
- Documents strict property retrieval rules for data, strings, numbers, booleans, and unknown-type queries.
- Error contract includes `ENOENT`, `EFBIG`, `EFTYPE`, `EINVAL`, and `EIO`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/device_calls.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/device_if.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/device_if.h

Minimal public device type declarations used by many kernel and user-kmem headers.

Key content:
- Includes `<sys/stdint.h>`.
- Forward declares `struct device`.
- Defines `device_t` as `struct device *`.
- Under `_KERNEL` or `_KMEMUSER`, defines `devact_level_t`, `DEVACT_LEVEL_*`, forward declarations for device locks/suspensors, `devgen_t`, and related typedefs.

Important behavior:
- Keeps lightweight device identity available without pulling in the full autoconf framework.
- `DEVACT_LEVEL_FULL` aliases class-level activation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/device_if.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/device_impl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/device_impl.h

Private autoconf-internal device layout and power-management helpers.

Key content:
- Explicit warning: do not use outside autoconf internals.
- `struct device_lock` with wait/lock counts, holder, mutex, condition variable.
- `DEVICE_SUSPENSORS_MAX`.
- Full `struct device` layout: handle, class, global list entry, config data, driver/attach pointers, unit/name, parent/depth, flags, private storage, locators, property dictionary, localcount, pending config state, attach/detach state, activity handlers, driver/bus/class PM callbacks, generation numbers, lock, suspensor arrays, garbage list.
- Private flags: active, power handlers registered, class/driver/bus suspended, attach in progress.
- PM helper declarations for driver/class registration, suspend/resume/shutdown, locks, and registration checks.

Important behavior:
- Complements `device.h`; the public API intentionally hides this layout.
- Flags must not overlap with `cfattach::ca_flags` values noted in `device.h`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/device_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/devmon.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/devmon.h

Declares the device monitor event insertion interface.

Key content:
- Includes `<prop/proplib.h>`.
- `int devmon_insert(const char *, prop_dictionary_t);`

Important behavior:
- Small bridge for reporting device events with proplib dictionaries.
- Header guard begins after the proplib include.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/devmon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dir.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/dir.h

Backward-compatibility header mapping old BSD `struct direct` usage to modern `struct dirent`.

Key content:
- Rejects kernel use with `#error "Please use <sys/dirent.h> instead"`.
- Includes `<dirent.h>`.
- Defines `direct` as `dirent`.
- Defines compatibility `DIRSIZ(dp)` record length macro.

Important behavior:
- Exists for old user-level source compatibility only.
- `DIRSIZ` computes minimum record length rounded to a 4-byte boundary.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dirent.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/dirent.h

Defines NetBSD directory entry ABI and directory record helper macros.

Key content:
- `struct dirent`: inode number, record length, name length, file type, fixed maximum name buffer.
- NetBSD-source `MAXNAMLEN` set to 511.
- File type constants: `DT_UNKNOWN`, `DT_FIFO`, `DT_CHR`, `DT_DIR`, `DT_BLK`, `DT_REG`, `DT_LNK`, `DT_SOCK`, `DT_WHT`.
- Alignment and record macros: `_DIRENT_ALIGN`, `_DIRENT_NAMEOFF`, `_DIRENT_RECLEN`, `_DIRENT_SIZE`, `_DIRENT_NEXT`, `_DIRENT_MINSIZE`.
- Mode conversion: `IFTODT`, `DTTOIF`.

Important behavior:
- Comments warn macros are used both with exposed `struct dirent` and UFS/FFS `struct direct`, so they remain type-polymorphic.
- Modern `struct dirent` uses 8-byte alignment via inode field size.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dirhash.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/dirhash.h

Declares an in-memory directory hash table used to accelerate directory entry lookup and free-space tracking.

Key content:
- Hash sizing: 5 bits, 32 buckets.
- `struct dirhash_entry`: hash value, directory offset, name length, entry size, list linkage.
- `struct dirhash`: flags, byte size, refcount, number of files, entry buckets, free-entry list, global tailq linkage.
- Flags: purged, complete, broken on read-in, compactable.
- APIs: initialize, purge, ref/unref, enter/remove entries, record freed space, lookup names/free entries, emptiness check.

Important behavior:
- Includes `sys/queue.h` and `sys/dirent.h`.
- Stores `d_namlen` to avoid costly fid-to-dirent translations.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dirhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disk.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/disk.h

Defines NetBSD disk device metadata, wedge interfaces, disk geometry, bad-sector reporting, strategy configuration, and kernel disk lifecycle APIs.

Key content:
- Disk info and geometry dictionary documentation.
- `struct dkwedge_info` and `struct dkwedge_list`.
- Common wedge partition type strings, including FFS, FAT, LFS, UDF, ZFS, CGD, RAIDframe, NTFS, ext2fs, VMFS, and aliases matching disklabel filesystem symbols.
- `struct disk_geom`.
- `struct disk_badsectors`, `struct disk_badsecinfo`.
- `struct disk_strategy` and `struct disk_sectoralign`.
- Kernel-only wedge discovery method registration macro.
- Extensive partition dictionary property schema documentation.
- `struct disk`: global link, name, info dictionary, geometry, open masks, state, block/byte shifts, I/O stats, driver, raw vnode state, wedge list, disklabel/cpulabel pointers.
- `struct dkdriver` operation vector.
- Disk states: closed/opening/read-label/open/raw.
- Disk and wedge lifecycle/query APIs.

Important behavior:
- Bridges disk drivers, disklabel handling, wedge autodiscovery, and user-visible disk metadata.
- Includes `dkio.h`, `time.h`, `queue.h`, and `iostat.h`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disklabel.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/disklabel.h

Defines the classic NetBSD disklabel on-disk/in-core format, disk type constants, filesystem partition type constants, and kernel disklabel helpers.

Key content:
- Includes machine disklabel parameters unless building tools with `HAVE_NBTOOL_CONFIG_H`.
- `MAXMAXPARTITIONS` capped at 22.
- Device macros: `DISKUNIT`, `DISKPART`, `DISKMINOR`, `MAKEDISKDEV`.
- Magic: `DISKMAGIC`.
- `struct partition`.
- `struct disklabel` with magic fields, drive type/subtype/name, pack/bootstrap union, geometry, spare/alternative cylinders, hardware timing/skew fields, flags, drive-specific data, checksum, partition count, boot/superblock sizes, and partition table.
- Optional `struct olddisklabel`.
- Assembly offsets under `_LOCORE`.
- `DKTYPE_DEFN` list and generated enum/name support.
- `FSTYPE_DEFN` list and generated fsck/mount name support.
- Drive flags and drive-specific aliases.
- `struct format_op` and kernel `struct partinfo`.
- Kernel APIs for reading/writing/converting disklabels, bounds checking, disk errors, and fstype names.

Important behavior:
- Comments document alignment and LP32/LP64 ABI complications.
- Stored on existing disks, so layout compatibility is critical.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disklabel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disklabel_acorn.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/disklabel_acorn.h

Defines Acorn FileCore and RISCiX partition structures and helpers for disklabel integration.

Key content:
- Partition type/format constants for unused, ADFS, RISCiX, and RISCBSD.
- FileCore boot sector location.
- RISCiX partition table constants and structures.
- `struct filecore_bootblock` with geometry, root, disk size/id/name/type, partition cylinder range, and checksum.
- Kernel prototypes: `filecore_label_read` and `filecore_label_locate`.

Important behavior:
- Kernel helpers are guarded by `_KERNEL` and not assembler.
- Used by disklabel read/write paths to recognize Acorn partitioning.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disklabel_acorn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disklabel_gpt.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/disklabel_gpt.h

Defines EFI GUID Partition Table header, entry structures, attributes, and known partition type GUID constants.

Key content:
- `struct gpt_hdr` matching GPT header fields.
- GPT signature, revision, primary header block number, header size.
- `struct gpt_ent` with type GUID, unique GUID, start/end LBA, attributes, UCS-2 name.
- Attributes for required partition, no block I/O protocol, legacy BIOS bootable, and FreeBSD boot flags.
- GUID constants for EFI, MBR, NetBSD swap/FFS/LFS/RAID/CCD/CGD, FreeBSD types, OpenBSD data, Microsoft reserved/basic/recovery/LDM, Linux data/RAID/swap/LVM/xbootldr, Apple HFS/UFS, BIOS boot, VMware, and SiFive BBL.

Important behavior:
- Notes all GPT fields are little-endian per EFI specification.
- Header is pure structure/constant ABI, with no functions.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disklabel_gpt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disklabel_rdb.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/disklabel_rdb.h

Defines Amiga Rigid Disk Block partitioning structures and filesystem type identifiers.

Key content:
- `RDBNULL`, `RDB_MAXBLOCKS`.
- `struct rdblock`: RDSK header, checksum fields, linked-list heads for bad/partition/fs blocks, disk geometry, controller/disk inquiry strings.
- RDB flags for last drive/LUN/unit, reselection, disk/controller id, sync.
- `struct ados_environ`: partition filesystem environment table.
- `struct partblock`, `struct badblock`, `struct fsblock`, `struct lsegblock`.
- Block ID constants: `RDSK`, `PART`, `BADB`, `FSHD`, `LSEG`.
- DOS type constants for BSD, NetBSD root/swap/user, AmigaDOS, AMIX, ext2, Linux swap, RAID, MSDOS, SFS.
- `struct adostype`, architecture type constants, and `ISFSARCH_NETBSD`.

Important behavior:
- Represents big legacy on-disk structures with linked blocks.
- Used to translate Amiga partition metadata into NetBSD disklabel semantics.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/disklabel_rdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dkbad.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/dkbad.h

Defines DEC STD 144 bad-sector table layout and related constants.

Key content:
- `NBT_BAD` maximum of 126 bad sectors.
- `struct dkbad` with cartridge serial, flags, and `bt_bad` array of cylinder/track-sector pairs.
- `HAS_BAD144_HANDLING` capability marker.
- Error constants: `ECC`, `SSE`, `BSE`, `CONT`.
- Kernel `isbad` prototype.

Important behavior:
- Comments describe storage in the first five even-numbered sectors of the last track and replacement-sector allocation rules.
- Legacy disk bad-block remapping support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dkbad.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dkio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/dkio.h

Defines disk-specific ioctl command numbers and cache/wedge/disk-info constants.

Key content:
- Disklabel ioctls: get/set/write default/clear label, plus old-label variants under compatibility.
- Raw format ioctls.
- Step/retry/write-label/keep-label/eject/lock controls.
- Bad-sector and cache controls.
- Cache flags: read/write enabled, changeable, save, FUA, DPO.
- `DKCACHE_COMBINE` macro.
- Wedge ioctls: add/get/delete/list/make/remove wedges.
- Strategy ioctls.
- Disk info dictionary ioctl.
- Test-unit-ready, sector size/media size, sector alignment ioctls.

Important behavior:
- Includes `sys/ioccom.h` and `prop/plistref.h`.
- Some numbers are reserved because of historical 6.99 discard ioctls.
- Kernel-only `DIOCGPARTINFO` and 32-bit compatibility adjustment are present.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dkio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dkstat.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/dkstat.h

Very small header exposing historical disk/terminal I/O counters to kernel code.

Key content:
- Under `_KERNEL`, declares `tk_cancc`, `tk_nin`, `tk_nout`, and `tk_rawcc` as `uint64_t`.

Important behavior:
- No user-visible declarations beyond the guard.
- Legacy statistics plumbing.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dkstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/domain.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/domain.h

Defines the network protocol domain structure and domain registration machinery.

Key content:
- Includes mbuf, socket, and route headers.
- `struct domain` fields for address family/name, init, rights externalize/dispose, protocol switch range, route table attach, route key metadata, interface up/down/attach/detach/link-state hooks, sockaddr address access/comparison/externalization, wildcard sockaddr, domain ifqueues, list linkage, mbuf owner, and sockaddr comparison offsets.
- Domain list heads.
- Kernel macros/functions: `DOMAIN_DEFINE`, `DOMAIN_FOREACH`, `domains`, `domain_attach`, `domaininit`, `domaininit_post`.

Important behavior:
- Provides the core registration contract for protocol families such as inet, inet6, unix, etc.
- Uses link sets for static domain registration.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/domain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/drvctlio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/drvctlio.h

Defines the experimental `/dev/drvctl` user/kernel ioctl interface for device management.

Key content:
- Device path: `DRVCTLDEV`.
- Argument structs for detach, list children, power-management operations, and bus rescan.
- `DEVPM_F_SUBTREE` flag.
- Ioctls: detach device, rescan bus, generic plist command, resume, list, get event, suspend.
- Detailed documentation for `DRVCTLCOMMAND` request and response dictionaries.
- Documents `get-properties` command.

Important behavior:
- Uses proplib dictionaries through `plistref` for extensible commands.
- Interface is explicitly marked experimental.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/drvctlio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dtrace_bsd.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/dtrace_bsd.h

Provides BSD/NetBSD shim declarations for imported DTrace code and kernel hook integration.

Key content:
- Includes kernel, memory, proc, and DTrace option headers.
- Cyclic clock hook type and array.
- Trap/invop/doubletrap hook types and globals.
- Virtual time switch hook.
- Fasttrap fork/exec/exit hooks.
- `dtmalloc` probe hook.
- NFS client DTrace provider hooks for access cache, attribute cache, and NFSv2/v3 RPC events.
- `dtrace_gethrtime`, `dtrace_gethrestime`.
- Fixed DTrace process/thread opaque storage sizes.
- Inline constructors/destructors allocating/freeing `p_dtrace` and `l_dtrace` when `KDTRACE_HOOKS` is enabled.

Important behavior:
- Wraps optional instrumentation so core proc/lwp lifecycle can support DTrace without always allocating storage.
- Intended for kernel-only DTrace integration.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dtrace_bsd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dvdio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/dvdio.h

Defines DVD-ROM specific ioctl ABI and DVD authentication/structure data layouts.

Key content:
- Ioctls: `DVD_READ_STRUCT`, `DVD_WRITE_STRUCT`, `DVD_AUTH`.
- SCSI command constants for DVD structure/key operations.
- DVD structure types: physical, copyright, disk key, BCA, manufacture.
- Structures for physical layers, copyright info, disk key, BCA, manufacture info.
- `dvd_struct` union.
- Authentication state constants for AGID, challenge/key exchange, title key, ASF, RPC state.
- Key/challenge typedefs.
- Authentication payload structs and `dvd_authinfo` union.
- `dvd_rpc_state_t`.

Important behavior:
- Uses C bitfields heavily for protocol fields.
- User/kernel ABI for optical media drivers and tools.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/dvdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/efiio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/efiio.h

Defines EFI runtime table and variable ioctl ABI.

Key content:
- EFI variable attribute flags: non-volatile, boot service, runtime, hardware error record, authenticated write, time-based authenticated write, append write, enhanced authenticated access.
- `struct efi_get_table_ioc`: buffer, UUID, table length, buffer length.
- `struct efi_var_ioc`: UTF-16 variable name buffer, name size, vendor UUID, attributes, data buffer, data size.
- Ioctls: `EFIIOC_GET_TABLE`, `EFIIOC_VAR_GET`, `EFIIOC_VAR_NEXT`, `EFIIOC_VAR_SET`.

Important behavior:
- Includes `sys/uuid.h`.
- Provides typed ABI for EFI table retrieval and variable enumeration/get/set.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/efiio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/endian.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/endian.h

Defines byte-order constants, host/network conversion interfaces, host-to/from endian macros, and unaligned endian encode/decode helpers.

Key content:
- `_LITTLE_ENDIAN`, `_BIG_ENDIAN`, `_PDP_ENDIAN`.
- Feature-gated typedefs for `in_addr_t`, `in_port_t` and declarations for `htonl`, `htons`, `ntohl`, `ntohs`.
- Includes machine endian and bswap headers.
- Defines `_QUAD_HIGHWORD`/`_QUAD_LOWWORD`.
- XOpen/NetBSD traditional `LITTLE_ENDIAN`, `BIG_ENDIAN`, `PDP_ENDIAN`, `BYTE_ORDER`.
- Network conversion macros optimized for native big-endian or bswap otherwise.
- `htobe*`, `htole*`, `be*toh`, `le*toh` and in-place uppercase variants.
- NetBSD-source endian stream helpers: `be16enc/dec`, `be32enc/dec`, `be64enc/dec`, `le16enc/dec`, `le32enc/dec`, `le64enc/dec`.

Important behavior:
- Uses builtin memcpy-based helpers when supported to avoid alignment issues; otherwise falls back to byte-wise encoding/decoding.
- Namespace exposure depends on feature-test macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/entropy.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/entropy.h

Declares kernel entropy subsystem interfaces.

Key content:
- Kernel-only header; user inclusion triggers an error.
- Includes libkern entropy pool definitions.
- `ENTROPY_CAPACITY` aliases `ENTPOOL_CAPACITY`.
- Extraction flags: `ENTROPY_WAIT`, `ENTROPY_SIG`, `ENTROPY_HARDFAIL`.
- APIs: boot request, reset, gather, consolidate, epoch, readiness query, extract, poll, kqfilter, ioctl.

Important behavior:
- Integrates random-device readiness, polling, kqueue, and ioctl paths.
- Header is intentionally not a public userland API.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/entropy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/envsys.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/envsys.h

Defines ENVSYS 2 environmental sensor units, states, ioctls, and legacy compatibility structures.

Key content:
- Limits: `ENVSYS_MAXSENSORS`, `ENVSYS_DESCLEN`.
- Sensor units: temperature, fan RPM, AC/DC volts, ohms, watts, amps, watt/amp hours, indicator, integer, drive, battery capacity/charge, humidity, lux, pressure.
- Sensor states: valid, invalid, critical, warn/critical under/over.
- Drive state enum and legacy drive state macros.
- Battery capacity and indicator states.
- Dictionary ioctls: get/set/remove properties.
- Legacy `envsys_tre_data_t` with current/min/max/avg data, warning flags, valid flags, units.
- Warning and valid flag constants.
- Legacy `envsys_basic_info_t` and `ENVSYS_GTREINFO`.
- Optional unit/status name arrays under `ENVSYSUNITNAMES`.

Important behavior:
- Modern interface is proplib dictionary based.
- Compatibility keeps old envsys ioctl consumers working for data/info reads.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/envsys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/epoll.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/epoll.h

Defines NetBSD’s Linux-compatible epoll API constants, structures, and declarations.

Key content:
- `EPOLL_CLOEXEC` aliases `O_CLOEXEC`.
- Event flags: `EPOLLIN`, `EPOLLPRI`, `EPOLLOUT`, `EPOLLERR`, `EPOLLHUP`, normal/band read/write, message, read-half-hup, wakeup, oneshot, edge-triggered.
- Control operations: add, delete, modify.
- Kernel max events: `EPOLL_MAX_EVENTS`.
- Kernel `epoll_data_t` as `uint64_t`; userland `union epoll_data`.
- `struct epoll_event`.
- Kernel common implementations: `epoll_ctl_common`, `epoll_wait_common`.
- Userland declarations under `_NETBSD_SOURCE`: `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, `epoll_pwait2`.

Important behavior:
- Bridges Linux API semantics into NetBSD’s kernel/user ABI.
- Uses feature-test gating for public function declarations.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/epoll.h -->