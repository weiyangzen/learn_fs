# Research: subset-b-005925

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uidgid.h -->
# sources/distributed-fs/ceph-client/include/linux/uidgid.h

Purpose: provides the kernel's typed UID/GID helpers, separating internal kernel IDs (`kuid_t`, `kgid_t`) from userspace `uid_t`/`gid_t` values so user namespace translation cannot be accidentally skipped.

Important APIs and types: `KUIDT_INIT`, `KGIDT_INIT`, `GLOBAL_ROOT_UID/GID`, and `INVALID_UID/GID` define canonical constants. Inline comparators (`uid_eq`, `uid_gt`, `uid_gte`, `uid_lt`, `uid_lte` and GID variants) compare wrapped IDs through `__kuid_val()`/`__kgid_val()`. `uid_valid()`/`gid_valid()` reject the all-ones sentinel. With `CONFIG_USER_NS`, external translation APIs include `make_kuid()`, `make_kgid()`, `from_kuid()`, `from_kgid()`, munged overflow variants, and low-level `map_id_*()` helpers over `struct uid_gid_map`; without namespaces they collapse to identity mappings.

Control flow: callers construct or receive kernel IDs, compare them only through the typed helpers, and translate at user namespace boundaries. The mapping path is config-dependent: user namespace builds call real mapping code, while non-namespace builds inline identity conversions and overflow fallback.

State and persistence: this header owns no storage. Persistent identity state lives in credentials, inodes, IPC objects, and namespace UID/GID maps; these helpers control how that state is interpreted when crossing namespaces.

Dependencies and integration points: depends on `uidgid_types.h`, `highuid.h`, `struct user_namespace`, and `struct uid_gid_map`. It is used by VFS, credentials, capabilities, procfs/sysfs, IPC, and filesystem protocol code that must not confuse global kernel IDs with namespace-local user-visible IDs.

Risks and test signals: risks include direct `.val` access bypassing namespace conversion, treating invalid IDs as root in non-multiuser builds, missing overflowuid/overflowgid handling, and range mapping bugs. Test with user namespace ID maps, unmapped IDs, filesystem ownership display, chown across namespaces, and build matrices with `CONFIG_MULTIUSER`/`CONFIG_USER_NS` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uidgid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uidgid_types.h -->
# sources/distributed-fs/ceph-client/include/linux/uidgid_types.h

Purpose: defines the opaque wrapper structs used for kernel-internal user and group IDs.

Important APIs and types: `kuid_t` wraps a `uid_t val`; `kgid_t` wraps a `gid_t val`. The wrappers intentionally make raw userspace ID values type-incompatible with internal kernel IDs unless code explicitly converts.

Control flow: this is a pure type header. Higher-level conversion, comparison, and validity helpers live in `uidgid.h`.

State and persistence: no state is stored here. The fields are embedded in credentials and ownership-bearing objects elsewhere.

Dependencies and integration points: depends only on `linux/types.h`; it is a low-level include for credential, VFS, namespace, and security code that needs type declarations without the full mapping API.

Risks and test signals: risks are mostly misuse of `.val` directly or ABI-width assumptions about `uid_t`/`gid_t`. Test signals are compile-time type checking and namespace/ownership tests that catch missing conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uidgid_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uio.h -->
# sources/distributed-fs/ceph-client/include/linux/uio.h

Purpose: defines kernel scatter/gather buffer descriptors and the `iov_iter` abstraction used to copy, pin, extract, and advance over user buffers, kernel vectors, bio vectors, folio queues, xarrays, and discard sinks.

Important APIs and types: `struct kvec` describes kernel vectors. `enum iter_type` identifies `ITER_UBUF`, `ITER_IOVEC`, `ITER_BVEC`, `ITER_KVEC`, `ITER_FOLIOQ`, `ITER_XARRAY`, and `ITER_DISCARD`. `struct iov_iter` stores direction (`data_source`), nofault mode, current offset/count, segment state, and a union of backing representations. `struct iov_iter_state` snapshots offset/count/segment state; `struct uio_meta` wraps protection metadata plus an iterator. Key helpers include type predicates, `iov_iter_rw()`, `iov_iter_count()`, `iov_iter_truncate()/reexpand()`, `iov_iter_save_state()/restore()`, copy helpers (`copy_to_iter`, `copy_from_iter`, full/reverting variants, nofault/nocache/flushcache/machine-check variants), page extraction helpers, import helpers (`import_iovec`, `import_ubuf`, `iovec_from_user`), and `extract_iter_to_sg()`.

Control flow: syscall and I/O paths import user iovecs or initialize kernel iterators, validate total lengths, then repeatedly copy or extract pages while `iov_iter_advance()` moves the cursor. Full-copy wrappers revert partial progress on short copy. Page extraction returns pinned pages for user-backed iterators and unpinned references for other iterator classes, signaled by `iov_iter_extract_will_pin()`.

State and persistence: iterator state is transient per I/O operation: current offset, remaining count, segment index, and backing pointer. It does not persist data, but incorrect advancement or failure rollback can corrupt higher-level file/socket/block I/O semantics.

Dependencies and integration points: depends on UAPI `linux/uio.h`, memory/folio/page types, `check_copy_size()`, architecture copy features, xarray, scatterlist, and bio vectors. It is central to VFS read/write, networking, block direct I/O, splice-like paths, and filesystem data movement.

Risks and test signals: risks include length overflow before validation, copying in the wrong direction, failing to revert on partial full-copy helpers, misinterpreting user-backed pin lifetime, `ITER_UBUF` overlay assumptions, and config-specific copy semantics. Test with vectored read/write, short copy fault injection, direct I/O page pin accounting, xarray/bvec/kvec iterators, nofault paths, and KASAN/UBSAN coverage around bounds and alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uio_driver.h -->
# sources/distributed-fs/ceph-client/include/linux/uio_driver.h

Purpose: declares the Userspace I/O driver interface, allowing simple device drivers to expose memory/port regions, interrupts, and minimal callbacks through `/dev/uioX`.

Important APIs and types: `struct uio_mem` describes mappable memory regions with address, DMA address, offset, size, type, internal mapping, and DMA device. `struct uio_port` describes port I/O regions. `struct uio_device` is the core-owned runtime device with minor, event counter, async queue, waitqueue, info lock, and sysfs kobjects. `struct uio_info` is supplied by a driver and contains name/version, memory/port arrays, IRQ information, private data, IRQ handler, mmap/open/release hooks, and `irqcontrol()`. Registration APIs are `uio_register_device()`, `uio_unregister_device()`, `devm_uio_register_device()`, and `uio_event_notify()`.

Control flow: a hardware driver fills `uio_info`, registers it, optionally handles interrupts in `handler()`, and calls `uio_event_notify()` to wake/poll userspace. Userspace maps listed regions and can enable/disable IRQs through writes when `irqcontrol()` is implemented. Devm registration ties cleanup to parent device lifetime.

State and persistence: runtime state lives in `struct uio_device`: minor assignment, event count, waiters, fasync subscribers, sysfs map/port objects, and the bound `uio_info`. No persistent storage is owned.

Dependencies and integration points: integrates the device model, character device file operations, IRQ subsystem, DMA coherent memory, sysfs maps, and user drivers. Memory type constants distinguish physical, logical, virtual, IOVA, and legacy coherent DMA mappings.

Risks and test signals: risks include exporting unsafe MMIO or DMA memory to userspace, stale `uio_info` after unregister, IRQ enable races, mis-sized page-aligned mappings, and misuse of deprecated `UIO_MEM_DMA_COHERENT` in new drivers. Test registration/unregistration, mmap offsets, poll/read event counts, IRQ control, devm cleanup, and hot-unplug while userspace holds `/dev/uioX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uio_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/driver.h -->
# sources/distributed-fs/ceph-client/include/linux/ulpi/driver.h

Purpose: defines the Linux device/driver wrapper for ULPI USB PHY devices.

Important APIs and types: `struct ulpi` embeds a `struct device`, an `ulpi_device_id`, and bus I/O ops. `struct ulpi_driver` carries an ID table, `probe()`/`remove()` callbacks, and the underlying `device_driver`. Helpers include `to_ulpi_dev()`, `to_ulpi_driver()`, `ulpi_set_drvdata()`, `ulpi_get_drvdata()`, `ulpi_register_driver()`, `ulpi_unregister_driver()`, `module_ulpi_driver()`, `ulpi_read()`, and `ulpi_write()`.

Control flow: interface providers register a ULPI device, ULPI PHY drivers match on the device ID table, probe configures the PHY via register reads/writes, and remove unwinds device-specific state.

State and persistence: state is device-model lifetime data plus driver private data and hardware PHY register state. Nothing is persisted by the header.

Dependencies and integration points: depends on `mod_devicetable.h`, `device.h`, and `struct ulpi_ops` from the interface layer. It connects USB controller glue code, PHY drivers, module autoloading, and ULPI register access.

Risks and test signals: risks include missing module ownership, accessing ULPI registers after unregister, wrong ID matching, and unsynchronized PHY register changes during controller role/power transitions. Test probe/remove, module autoload aliases, register read/write error propagation, suspend/resume, and controller integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/interface.h -->
# sources/distributed-fs/ceph-client/include/linux/ulpi/interface.h

Purpose: declares the provider-side ULPI bus interface used by controllers that can read and write ULPI PHY registers.

Important APIs and types: `struct ulpi_ops` supplies `read(struct device *, u8 addr)` and `write(struct device *, u8 addr, u8 val)` callbacks. `ulpi_register_interface()` creates a `struct ulpi` from a parent device and ops; `ulpi_unregister_interface()` removes it.

Control flow: a USB controller or glue driver registers ULPI access ops, the ULPI core enumerates/identifies the PHY, and matched PHY drivers call through `ulpi_read()`/`ulpi_write()` to these ops.

State and persistence: this header owns no state; provider implementations keep bus/register access state and the ULPI core owns the created device.

Dependencies and integration points: depends on `linux/types.h` and forward declarations of `struct device`/`struct ulpi`. It bridges host/device controller drivers to ULPI PHY drivers.

Risks and test signals: risks include ops that sleep in invalid contexts, bad register address handling, and unregistering while a PHY driver is active. Test interface registration failure paths, read/write error returns, and remove ordering with active USB controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/regs.h -->
# sources/distributed-fs/ceph-client/include/linux/ulpi/regs.h

Purpose: provides ULPI 1.1 register offsets, set/clear register address helpers, and bit definitions for PHY function, interface, OTG, interrupt, debug, and carkit controls.

Important APIs and types: `ULPI_SET()`/`ULPI_CLR()` derive adjacent write-only set/clear offsets. Register macros cover vendor/product IDs, `ULPI_FUNC_CTRL`, `ULPI_IFC_CTRL`, `ULPI_OTG_CTRL`, USB interrupt enable/status/latch registers, scratch/debug, carkit optional registers, extended access, and vendor-specific ranges. Bit macros define transceiver speed, opmode, reset/suspend, serial/carkit modes, VBUS/ID/pulldown controls, interrupt events, and carkit pulse/control bits.

Control flow: PHY drivers and controller glue read ID registers, configure function/interface/OTG bits, use set/clear offsets to avoid read-modify-write races when supported by the PHY, and service interrupt/latch bits.

State and persistence: state is hardware register state in the ULPI PHY. The header only names fields.

Dependencies and integration points: relies on `BIT()` being available to includers. It integrates with ULPI read/write users in USB PHY and controller drivers.

Risks and test signals: risks include using `ULPI_SET/CLR` on unsupported registers, wrong speed/opmode combinations, failing to preserve reserved bits, and carkit/OTG bit drift from the spec. Test PHY identification, reset/suspend/resume, OTG VBUS/ID behavior, interrupt latch handling, and hardware-specific register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/umh.h -->
# sources/distributed-fs/ceph-client/include/linux/umh.h

Purpose: declares the kernel usermode-helper API for launching userspace programs from kernel context and for globally disabling helper execution during freezer/shutdown-sensitive periods.

Important APIs and types: wait flags `UMH_NO_WAIT`, `UMH_WAIT_EXEC`, `UMH_WAIT_PROC`, `UMH_KILLABLE`, and `UMH_FREEZABLE` control synchronization and signal/freezer behavior. `struct subprocess_info` carries work item, completion, executable path, argv/envp, wait mode, return value, credential-init hook, cleanup hook, and caller data. APIs include `call_usermodehelper()`, setup/exec split helpers, `usermodehelper_disable()/enable()`, lower-level disable-depth setters, and read-lock APIs for callers that need to serialize against disable.

Control flow: callers either invoke `call_usermodehelper()` directly or allocate a `subprocess_info`, customize credentials with `init`, and execute it with a selected wait mode. System suspend/freezer paths can raise disable depth and wait for readers so helpers are not launched in unsafe phases.

State and persistence: each helper request is transient workqueue state with completion/result fields. Global disable depth and read-lock state live in the implementation; no persistent user data is stored.

Dependencies and integration points: depends on GFP allocation, workqueues, completions, credentials, errno, and sysctl integration. It is used by firmware loading, hotplug/modprobe paths, core dumps, request-key, and other kernel-to-userspace escape hatches.

Risks and test signals: risks include deadlocks while waiting for userspace from reclaim/freezer paths, wrong credentials/environment, helper launch while disabled, leaked argv/envp buffers, and unbounded helper spawning. Test wait modes, killable/freezable waits, disable/enable during suspend, credential init failure cleanup, and helper failure return propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/umh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unaligned.h -->
# sources/distributed-fs/ceph-client/include/linux/unaligned.h

Purpose: provides generic helpers for safe unaligned loads and stores in native, little-endian, big-endian, 24-bit, and 48-bit formats.

Important APIs and types: generic `get_unaligned()`/`put_unaligned()` use typed packed-struct access. Endian helpers cover `get_unaligned_le16/32/64`, `put_unaligned_le16/32/64`, `get_unaligned_be16/32/64`, `put_unaligned_be16/32/64`, plus manual byte assembly for 24-bit little/big endian and 48-bit big endian values.

Control flow: parsers and protocol code call these helpers when fields may not be naturally aligned. Fixed-width helpers read or write packed values and convert to/from CPU endian order; 24/48-bit helpers explicitly combine bytes.

State and persistence: no state is stored. Effects are immediate memory reads/writes at caller-provided addresses.

Dependencies and integration points: includes packed-struct unaligned primitives, architecture byteorder conversions, and VDSO unaligned helpers. It is used heavily by filesystem, networking, USB, storage, and binary protocol parsers.

Risks and test signals: risks include pointer type side effects in generic macros, assuming buffer length is sufficient, endian confusion, truncating 24/48-bit values, and architectures with strict unaligned access rules. Test protocol parsing on strict-alignment architectures, KASAN bounds checks, endian conversion tests, and round-trip put/get cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unaligned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unaligned/packed_struct.h -->
# sources/distributed-fs/ceph-client/include/linux/unaligned/packed_struct.h

Purpose: implements the generic CPU-endian unaligned access primitives using packed wrapper structs.

Important APIs and types: packed structs `__una_u16`, `__una_u32`, and `__una_u64` wrap 16/32/64-bit values. Helpers `__get_unaligned_cpu16/32/64()` and `__put_unaligned_cpu16/32/64()` perform direct loads/stores through packed pointers.

Control flow: higher-level unaligned macros cast an arbitrary address to a packed wrapper pointer, then load or store the wrapped field so the compiler emits safe unaligned access code for the target architecture.

State and persistence: no independent state exists. Stores modify caller-provided memory.

Dependencies and integration points: depends on `linux/types.h` and compiler support for `__packed`. It backs `linux/unaligned.h` and any architecture-generic unaligned access path.

Risks and test signals: risks include compiler behavior around packed accesses, insufficient buffer length, and accidental use for types larger than the wrappers. Test on strict-alignment architectures and with compiler warning/sanitizer coverage around packed pointer access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unaligned/packed_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unicode.h -->
# sources/distributed-fs/ceph-client/include/linux/unicode.h

Purpose: declares the kernel Unicode/UTF-8 normalization and casefolding interface used by filesystems and dcache name handling.

Important APIs and types: Unicode versions are encoded with `UNICODE_AGE()` and decoded by `unicode_major/minor/rev()`, with `UTF8_LATEST` set to 12.1.0. `enum utf8_normalization` supports `UTF8_NFDI` and `UTF8_NFDICF`. `struct unicode_map` stores the selected version, normalization tables, and table metadata. APIs validate, compare, case-insensitively compare, normalize, casefold, hash folded names, load/unload maps, and parse version strings.

Control flow: filesystems load a Unicode map for a version, validate and normalize/casefold `qstr` names on lookup/create/hash paths, and unload the map at teardown. Case-insensitive lookup can compare raw names or a pre-folded form.

State and persistence: `struct unicode_map` is an in-memory reference to Unicode tables. Normalized/casefolded names may influence persistent directory entries or lookup hashes in filesystems, but the header itself stores no persistent data.

Dependencies and integration points: depends on dcache `qstr`, init annotations, and generated UTF-8 data tables. It integrates with ext4/f2fs casefolding and any VFS-facing filesystem that needs Unicode normalization.

Risks and test signals: risks include version mismatch for persisted casefold policy, invalid UTF-8 acceptance, hash/compare inconsistency, buffer truncation in normalize/casefold, and default-ignorable handling changes. Test with Unicode conformance vectors, invalid sequences, casefold collisions, filesystem lookup/create/rename, and mount options selecting Unicode versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unicode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/union_find.h -->
# sources/distributed-fs/ceph-client/include/linux/union_find.h

Purpose: declares a generic disjoint-set union-find data structure for kernel code that groups nodes into equivalence classes.

Important APIs and types: `struct uf_node` stores a parent pointer and rank. `UF_INIT_NODE(node)` and `uf_node_init()` initialize a singleton set. `uf_find()` returns the representative root, and `uf_union()` merges two sets, likely using rank and path compression in the implementation.

Control flow: embedding code initializes one `uf_node` per object, calls `uf_union()` when two objects become equivalent, and calls `uf_find()` to compare representatives or compress paths.

State and persistence: state is entirely in embedded `uf_node` parent/rank fields. It persists only as long as the owning objects and must be reinitialized if objects are reused.

Dependencies and integration points: the header has no includes; documentation is in `Documentation/core-api/union_find.rst`. It can be embedded in graph, component, clustering, or allocation algorithms needing disjoint sets.

Risks and test signals: risks include using uninitialized nodes, freeing a node still referenced as another node's parent, missing locking around concurrent unions/finds, and assuming deterministic representatives. Test singleton initialization, repeated union idempotence, path compression, rank behavior, and concurrent caller locking in each consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/union_find.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/units.h -->
# sources/distributed-fs/ceph-client/include/linux/units.h

Purpose: centralizes common unit scale constants and temperature conversion helpers for kernel drivers and subsystems.

Important APIs and types: metric scale macros cover `PETA` through `FEMTO` as integer multipliers/divisors by convention. Ratio scales include `PERCENT`, `PERMILLE`, `PERMYRIAD`, and `PERCENTMILLE`. Frequency, power, energy, and bit/byte conversion constants include `NANOHZ_PER_HZ`, `HZ_PER_MHZ`, `MICROWATT_PER_WATT`, and `BYTES_PER_GBIT`. Temperature helpers convert among milliKelvin, milliCelsius, Kelvin, Celsius, and deciKelvin, using `ABSOLUTE_ZERO_MILLICELSIUS` and rounded division.

Control flow: consumers include this header and use named constants or inline conversions rather than open-coded scaling. Temperature conversions add or subtract absolute-zero offset and round when reducing precision.

State and persistence: no state is stored. Results are pure arithmetic values used by sensors, thermal, power, clock, and hardware-monitoring paths.

Dependencies and integration points: depends on `bits.h` for `BITS_PER_BYTE` and `math.h` for `DIV_ROUND_CLOSEST`. It integrates with drivers that exchange values in hardware-specific units and kernel/user-visible standard units.

Risks and test signals: risks include overflow when multiplying before conversion, confusion between numerator-style macros such as `MILLI` and SI fractional meanings, negative temperature rounding surprises, and unit mismatch in ABI attributes. Test boundary temperatures, large frequency/power values, byte/bit conversions, and hardware-monitoring sysfs expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/units.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unroll.h -->
# sources/distributed-fs/ceph-client/include/linux/unroll.h

Purpose: provides compiler loop-unroll pragmas and a preprocessor macro for explicit macro expansion across small fixed counts.

Important APIs and types: `unrolled`, `unrolled_count(n)`, `unrolled_full`, and `unrolled_none` emit Clang or GCC pragmas through `__pick_unrolled()`. `UNROLL(N, MACRO, args...)` expands `MACRO(index, args...)` for N from 0 through 20 via generated `__UNROLL_N` macros.

Control flow: performance-sensitive code places an unroll directive immediately before a loop or uses `UNROLL()` to generate repeated code at compile time. Clang receives `clang loop` pragmas; GCC receives `GCC unroll` pragmas where supported.

State and persistence: no runtime state is stored. It changes generated code shape and object size.

Dependencies and integration points: depends on `linux/args.h`, compiler config `CONFIG_CC_IS_CLANG`, `_Pragma`, and macro concatenation. It integrates with hot paths where manual or hinted unrolling is beneficial.

Risks and test signals: risks include object-code bloat, invalid `UNROLL()` counts beyond 20, hidden side effects in macro arguments, compiler-specific pragma drift, and performance regressions from forced unrolling. Test compile with GCC/Clang, inspect generated code for hot users, benchmark affected loops, and keep all macro arguments side-effect safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unroll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_deferred.h -->
# sources/distributed-fs/ceph-client/include/linux/unwind_deferred.h

Purpose: declares deferred user-space stack unwinding hooks and per-task cleanup/reset helpers for builds with `CONFIG_UNWIND_USER`.

Important APIs and types: mask bits `UNWIND_PENDING` and `UNWIND_USED` track whether unwinding has been requested or used. Enabled-build APIs initialize/free per-task unwind state, perform faultable user unwinding, initialize/request/cancel deferred work, and handle task exit. `unwind_reset_info()` clears per-task unwind IDs and cached stack entries after a kernel entry if no pending task work remains. Disabled builds provide no-op or `-ENOSYS` stubs.

Control flow: task setup initializes unwind info; tracing/profiling code requests deferred unwind work; task_work later performs unwinding and invokes the callback. On return-to-user boundaries, `unwind_reset_info()` atomically clears used state unless another pending unwind is queued.

State and persistence: state lives in `current->unwind_info`: atomic mask, unique ID, optional cache, and task_work. It is per-task, transient, and reset across kernel exits or task teardown.

Dependencies and integration points: depends on `task_work`, `unwind_user.h`, `unwind_deferred_types.h`, atomics, and current task state. It integrates with tracing/profiling consumers that need user stack traces without faulting in unsafe contexts.

Risks and test signals: risks include races clearing `unwind_mask`, stale cached stack entries, callbacks after task exit, pending work surviving reset, and config stubs hiding missing feature handling. Test enabled/disabled builds, deferred request/cancel, task exit with pending unwind, signal-return paths, and concurrent trace requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_deferred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_deferred_types.h -->
# sources/distributed-fs/ceph-client/include/linux/unwind_deferred_types.h

Purpose: defines the data structures used by deferred user-space unwinding.

Important APIs and types: `struct unwind_cache` stores completion state, entry count, and a flexible array of stack entries. `union unwind_task_id` combines CPU number and per-CPU counter into a nonzero 64-bit ID. `struct unwind_task_info` holds an atomic mask, cache pointer, task_work callback head, and current ID. `unwind_callback_t` is the deferred callback signature. `struct unwind_work` links queued work, stores the callback, and records a bit index.

Control flow: unwind users allocate or embed `unwind_work`, initialize it with a callback, queue requests that assign or reuse a task ID, and receive a stacktrace/cookie when deferred processing runs.

State and persistence: all state is per-task or per-work in memory. Cache entries are reusable within a task's kernel-entry window and are cleared by reset/exit paths.

Dependencies and integration points: depends on `types.h`, `atomic.h`, `list_head`, `callback_head`, and `struct unwind_stacktrace` from the generic unwind types. It is consumed by `unwind_deferred.h` and implementation code.

Risks and test signals: risks include flexible-array sizing mistakes, ID wrap or zero generation, list lifetime errors, cache reuse after free, and missing synchronization around the atomic mask. Test allocation sizes, repeated request IDs, cache reset, and task exit teardown under tracing load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_deferred_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_user.h -->
# sources/distributed-fs/ceph-client/include/linux/unwind_user.h

Purpose: declares the generic entry point and architecture hooks for unwinding user-space stack traces from kernel context.

Important APIs and types: includes `struct unwind_stacktrace` and state types from `unwind_user_types.h` plus architecture-specific definitions from `asm/unwind_user.h`. Fallback macros define no-op frame initialization when architecture frame-pointer support hooks are absent. `unwind_user_at_function_start()` defaults to false unless an architecture overrides it. `unwind_user()` fills stacktrace entries up to a maximum.

Control flow: tracing or diagnostic code prepares an `unwind_stacktrace`, then calls `unwind_user()`. Architecture code initializes user frame state and may identify function-entry IPs to improve unwinding semantics.

State and persistence: no state is owned here. It operates on caller-supplied stacktrace buffers and architecture-visible register/user stack state.

Dependencies and integration points: depends on generic unwind types and `asm/unwind_user.h`. It integrates with perf/tracing/deferred unwind code and architecture stack walking implementations.

Risks and test signals: risks include architecture hooks missing or inconsistent, user memory faults during stack walking, frame-pointer ABI assumptions, and truncated traces. Test per-architecture unwinding, invalid user stacks, signal/trampoline frames, max-entry limits, and builds without frame-pointer support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_user_types.h -->
# sources/distributed-fs/ceph-client/include/linux/unwind_user_types.h

Purpose: defines generic user-stack unwinding data structures and type-selection flags.

Important APIs and types: `enum unwind_user_type_bits` currently defines frame-pointer unwinding as the first priority bit. `enum unwind_user_type` provides `UNWIND_USER_TYPE_NONE` and `UNWIND_USER_TYPE_FP`. `struct unwind_stacktrace` carries output count and entries buffer. `struct unwind_user_frame` describes CFA, return-address, and frame-pointer offsets. `struct unwind_user_state` tracks current IP/SP/FP, selected/current type mask, topmost/done flags, and architecture working state.

Control flow: architecture unwind code advances `unwind_user_state` frame by frame, selecting available methods by priority and writing IPs into `unwind_stacktrace`.

State and persistence: state is temporary for one stack walk. No storage is persistent.

Dependencies and integration points: depends on `linux/types.h` and is shared by generic and architecture-specific unwind implementations.

Risks and test signals: risks include wrong signed offsets, failing to mark done, type priority drift as new methods are added, and stacktrace buffer overruns. Test frame-pointer walks, malformed frames, empty/maxed output buffers, and mixed architecture implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_user_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uprobes.h -->
# sources/distributed-fs/ceph-client/include/linux/uprobes.h

Purpose: declares the internal userspace probes interface for planting breakpoints in user mappings, single-stepping original instructions, and handling return probes.

Important APIs and types: `struct uprobe_consumer` defines handler, return-handler, and filter callbacks plus registration ID. Enabled builds define task states (`UTASK_*`), hybrid return-probe lifetime states (`HPROBE_*`), `struct hprobe`, `struct uprobe_task`, `struct return_instance`, `struct return_consumer`, `struct uprobes_state`, `uprobe_write_verify_t`, and many generic/arch hooks. Registration/control APIs include `uprobe_register()`, `uprobe_apply()`, `uprobe_unregister_nosync()`, `uprobe_unregister_sync()`, mmap/munmap/dup hooks, task copy/free hooks, pre/post single-step notifiers, resume notification, state clear/init, trampoline handling, and opcode write helpers. Disabled builds provide stubs returning `-ENOSYS` or no-ops.

Control flow: a consumer registers an inode/offset probe, mmap hooks install breakpoints into matching VMAs, a trap enters uprobe handling, the original instruction is executed out-of-line, and post-step handling restores user execution. Uretprobes hijack return addresses, track return instances on a task stack, and call return handlers through trampoline handling. Hybrid `hprobe` state allows return instances to transition from SRCU-protected to refcounted lifetime.

State and persistence: per-task uprobe state stores single-step status, return-instance stack/pool/timer/seqcount, active uprobe, XOL address, and signal-denial state. Per-mm state stores XOL area and optional trampolines. Probe definitions are in-memory registrations tied to inode offsets and consumers; breakpoint changes affect mapped process text while active.

Dependencies and integration points: depends on rbtrees, wait queues, timers, seqcounts, mutexes, `asm/uprobes.h`, VMAs, mm lifecycle hooks, task fork/exit, exception notifiers, instruction decoding, and tracing/perf consumers.

Risks and test signals: high-risk areas include instruction patching races, VMA lifetime during mmap/munmap/dup, XOL slot management, signal delivery during denied windows, uretprobe depth and lifetime transitions, stale consumer removal, and architecture decode mismatches. Test perf uprobes/uretprobes, concurrent mmap/unmap, fork/exec/exit, nested return probes to `MAX_URETPROBE_DEPTH`, signal-heavy workloads, disabled config builds, and architecture single-step fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb.h -->
# sources/distributed-fs/ceph-client/include/linux/usb.h

Purpose: defines the kernel host-side USB core API: parsed descriptors, device/interface state, driver registration, power management, URBs, synchronous transfers, scatter/gather I/O, endpoint pipe helpers, notifications, and misc support macros.

Important APIs and types: descriptor wrappers include `struct usb_host_endpoint`, `usb_host_interface`, `usb_interface`, `usb_interface_cache`, `usb_host_config`, and `usb_host_bos`. Topology and device state live in `struct usb_bus` and `struct usb_device`. Driver-facing objects include `struct usb_driver`, `usb_device_driver`, `usb_class_driver`, dynamic ID lists, and registration helpers (`usb_register`, `usb_deregister`, `usb_register_dev`, device-driver variants). Transfer APIs center on `struct urb`, `struct usb_anchor`, URB flags, `usb_fill_control_urb()`, `usb_fill_bulk_urb()`, `usb_fill_int_urb()`, allocation/submission/cancel/anchor APIs, coherent/noncoherent allocation, synchronous control/bulk/interrupt helpers, descriptor/string/configuration helpers, and `struct usb_sg_request`. Pipe macros encode direction, device address, endpoint, and transfer type.

Control flow: usbcore parses raw descriptors into host wrappers, selects/configures devices, binds interface or device drivers from ID tables, and drivers submit URBs to endpoints. URBs complete asynchronously in interrupt context, while sync helpers wrap URB submission/wait. PM helpers manage autosuspend, remote wakeup, LPM/LTM, resets, interface rebinding, and offload locks. Device matching macros build `usb_device_id` tables for hotplug and module autoload.

State and persistence: USB state is runtime device-model state: topology, current configuration/altsetting, endpoint queues, URB refs, anchors, PM/LPM flags, string caches, dynamic IDs, bus address bitmap, bandwidth counters, open usbfs files, and device authorization. Persistent hardware identity is read from descriptors, but kernel state is rebuilt on enumeration.

Dependencies and integration points: depends on USB chapter 9 descriptors, device model, krefs, completions, mutexes/spinlocks, runtime PM, ACPI optional power hooks, USB monitors, notifiers, debugfs, LED triggers, HCDs, hubs, usbfs, and class drivers. It is the primary integration surface for all host USB client drivers.

Risks and test signals: risks include URB lifetime and completion-context misuse, DMA buffer mapping errors, endpoint/pipe type mismatches, PM reference leaks, reset/disconnect races, descriptor parsing quirks, altsetting ordering assumptions, dynamic ID locking, LPM disable-count imbalance, and short-transfer semantics. Test with USB core selftests where available, hotplug/disconnect under I/O, suspend/resume/runtime PM, reset during active URBs, scatter/gather and coherent DMA paths, malformed descriptor devices, usbmon traces, and driver probe/disconnect races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/audio-v2.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/audio-v2.h

Purpose: defines USB Audio Class 2.0 descriptor layouts, control-bit decoders, class-specific constants, and selector codes.

Important APIs and types: `uac_v2v3_control_is_readable()` and `uac_v2v3_control_is_writeable()` decode two-bit `bmControls` fields. Packed descriptor structs model AC headers, format type I, clock source/selector/multiplier, input/output terminals, feature/effect units, AS headers, isochronous endpoint descriptors, connector control blocks, and interrupt messages. `DECLARE_UAC2_FEATURE_UNIT_DESCRIPTOR(ch)` builds fixed-size feature-unit descriptors. Constants define function categories, descriptor subtypes, effect/process/encoder/decoder types, request codes, clock/terminal/mixer/selector/feature/effect/processing/extension/AS/endpoint control selectors, and raw-data format bits.

Control flow: USB audio host and gadget code parse class-specific descriptor streams using these packed structures, inspect `bmControls` through helpers, build requests with selector constants, and generate descriptors for gadget functions.

State and persistence: no runtime state is stored. The structs describe on-wire descriptor data and request parameters supplied by devices or gadget descriptors.

Dependencies and integration points: depends on fixed-width Linux types and common USB Audio 1.0 definitions in `audio.h` for shared constants. It integrates with ALSA USB audio parsing, UAC2 gadget functions, and USB descriptor validation.

Risks and test signals: risks include variable-length descriptor under/over-read, little-endian field handling, invalid `bmControls` selector numbers, spec typo compatibility, and channel-count size calculations. Test with real UAC2 devices, descriptor fuzzing, gadget enumeration against hosts, control read/write requests, and malformed feature/effect units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/audio-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/audio-v3.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/audio-v3.h

Purpose: defines USB Audio Class 3.0 descriptor layouts and constants, including high-capability descriptors, clusters, power domains, BADD profile IDs, and UAC3-specific selectors.

Important APIs and types: packed structs include high-capability descriptor headers, cluster headers/segments, AC header, input/output terminals, feature units, clock source/selector/multiplier, power domains, AS header, isochronous endpoint descriptor, insertion control blocks, and interrupt messages. Macros create fixed feature-unit and power-domain descriptor structs. Constants define function subclasses/categories, descriptor types, cluster segment types, channel purposes/relationships, AC subtypes, process types, request codes, terminal/processing controls, BADD entity IDs, BADD endpoint max-packet sizes, fixed sample rate, and recovery times.

Control flow: UAC3-aware host and gadget code parse or generate class-specific descriptors, walk variable-length cluster/power-domain arrays, and issue class-specific requests using UAC3 selector constants. Shared v2/v3 control decoding comes from `audio-v2.h`.

State and persistence: no in-kernel state is owned. The definitions mirror device-provided or gadget-generated descriptors and control request fields.

Dependencies and integration points: depends on fixed-width Linux types and shared UAC1/UAC2 definitions. It integrates with USB audio class drivers, BADD profile gadget implementations, descriptor parsers, and ALSA control setup.

Risks and test signals: risks include duplicate/ambiguous constants, variable-length descriptor bounds bugs, 32/64-bit format bitmap interpretation, power-domain recovery-time interpretation, and host compatibility with BADD profiles. Test UAC3 descriptor parsing/generation, BADD enumeration, high-capability descriptor requests, and fuzzed malformed segment chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/audio-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/audio.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/audio.h

Purpose: provides kernel-side USB Audio common definitions and small control helper structures, while including the UAPI Audio Class definitions.

Important APIs and types: `struct usb_audio_control` links a named control with type, small integer data array, and set/get callbacks. `struct usb_audio_control_selector` links selectors to controls, IDs, type, name, and descriptor pointer. The header imports `<uapi/linux/usb/audio.h>` for standard descriptor and selector constants.

Control flow: USB audio gadget or helper code can group controls under selectors, then dispatch class-specific get/set requests through the callback pointers.

State and persistence: control lists and callback data are runtime driver state. Actual control values may map to device hardware or gadget function state; the header itself stores nothing.

Dependencies and integration points: depends on list heads and USB descriptor types from included UAPI/kernel headers. It integrates with USB audio class code and newer Audio v2/v3 headers that reuse common definitions.

Risks and test signals: risks include callback lifetime after descriptor teardown, insufficient `data[5]` interpretation discipline, and descriptor pointer validity. Test class request dispatch, control list teardown, and descriptor parsing across UAC versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/c67x00.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/c67x00.h

Purpose: defines platform data and SIE configuration macros for Cypress C67X00 USB controller chips.

Important APIs and types: SIE modes identify unused, host, peripheral A, and peripheral B roles. `c67x00_sie_config(config, n)` extracts a two-bit SIE mode from a packed config. `C67X00_SIE1_*` and `C67X00_SIE2_*` macros build platform config values. `struct c67x00_platform_data` carries SIE configuration and HPI register spacing.

Control flow: board/platform code fills platform data, and the C67X00 driver decodes per-SIE mode to initialize host/peripheral behavior and HPI access layout.

State and persistence: no state is owned here. Platform data is static boot-time configuration.

Dependencies and integration points: no explicit includes. It integrates board files/platform devices with the C67X00 USB host/peripheral driver.

Risks and test signals: risks include wrong SIE nibble selection, unsupported role combinations, and incorrect HPI register step causing bad MMIO access. Test board probe, both SIE roles, HPI register reads/writes, and platform-data validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/c67x00.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ccid.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ccid.h

Purpose: defines the USB Chip/Smart Card Interface Device class code and packed CCID functional descriptor layout.

Important APIs and types: `USB_INTERFACE_CLASS_CCID` is class `0x0b`. `struct ccid_descriptor` mirrors the CCID descriptor fields including spec version, slot/voltage/protocol support, clock/data-rate ranges, IFSD, sync/mechanical/features bitmaps, message length, class envelope/get-response values, LCD layout, PIN support, and busy-slot count.

Control flow: CCID drivers parse this descriptor during probe to determine supported card slots, protocols, rates, message size, and optional PIN/LCD features.

State and persistence: no state is stored here. Descriptor values are device-provided capabilities cached by drivers.

Dependencies and integration points: depends on `linux/types.h` for packed little-endian fields. It integrates with USB smart-card reader drivers and user-facing CCID stacks.

Risks and test signals: risks include trusting malformed descriptor lengths, endian mistakes for capability bitmaps, and feature flags inconsistent with endpoint behavior. Test probe against diverse readers, descriptor fuzzing, multi-slot handling, and maximum message length enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ccid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc-wdm.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/cdc-wdm.h

Purpose: declares the registration hook for the USB CDC WDM subdriver used by modem/WWAN management interfaces.

Important APIs and types: `usb_cdc_wdm_register()` binds a CDC WDM subdriver to a USB interface and endpoint descriptor, with buffer size, WWAN port type, and optional power-management callback.

Control flow: parent composite drivers call this helper after parsing a suitable management endpoint; the WDM layer creates the character/WWAN management port and uses `manage_power()` to coordinate interface power state.

State and persistence: runtime state is owned by the CDC WDM driver and returned `struct usb_driver`; this header owns none.

Dependencies and integration points: depends on WWAN port types, CDC WDM UAPI, USB interface and endpoint descriptors. It integrates MBIM/QMI-like modem drivers with the shared CDC WDM character device implementation.

Risks and test signals: risks include endpoint mismatch, buffer too small for management messages, power callback races, and teardown ordering with parent drivers. Test modem probe/remove, suspend/resume, management reads/writes, and parent-driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc-wdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/cdc.h

Purpose: provides kernel CDC helper declarations and a parsed-header aggregate for USB Communications Device Class functional descriptors.

Important APIs and types: `CDC_PHONET_MAGIC_NUMBER` names a nonstandard marker. `struct usb_cdc_parsed_header` stores pointers to parsed CDC union, header, call-management, ACM, country, network terminal, Ethernet, DMM, MDLM, MDLM detail, OBEX, NCM, MBIM, and MBIM extended descriptors plus a Phonet magic flag. `cdc_parse_cdc_header()` parses raw descriptor bytes from an interface.

Control flow: CDC class drivers pass an interface and descriptor buffer to `cdc_parse_cdc_header()`, then inspect the aggregate to select ACM/NCM/MBIM/Ethernet behavior and locate companion interfaces/endpoints.

State and persistence: parsed pointers refer into descriptor memory owned by usbcore; no independent storage is owned here.

Dependencies and integration points: includes CDC UAPI definitions and forward-declares `struct usb_interface`. It integrates with USB serial, network, modem, and WWAN CDC drivers.

Risks and test signals: risks include duplicate descriptors, malformed lengths, stale pointers if descriptor storage lifetime is misunderstood, and ambiguous vendor-specific CDC layouts. Test parsing of ACM/NCM/MBIM devices, descriptor fuzzing, Phonet quirks, and multi-interface union descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc_ncm.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/cdc_ncm.h

Purpose: declares common state, constants, flags, and helper APIs for USB CDC Network Control Model and MBIM network transfers.

Important APIs and types: constants define NCM/MBIM alternate settings, NDP16/32 minimum lengths, default/max NTB sizes, datagram limits, timer thresholds, and driver flags. Macros identify MBIM communication/data interfaces. `struct cdc_ncm_ctx` stores parsed functional descriptors, usbnet/control/data interfaces, TX aggregation skb state, delayed NDP pointers, spinlock/stop flag, timer/tasklet, frame/datagram sizing and alignment fields, sequence numbers, and TX/RX statistics. APIs include altsetting selection, MTU change, bind/unbind, TX frame fill/fixup, RX NTH/NDP verification, and RX fixup.

Control flow: usbnet-based drivers bind through `cdc_ncm_bind_common()`, negotiate NCM parameters, collect outgoing datagrams into NTBs with timers/tasklets, verify incoming NTB headers/NDPs, split datagrams, and handle MBIM-specific alternate settings and descriptors.

State and persistence: all state is per-interface runtime state in `cdc_ncm_ctx`: active skb aggregation, timers, sequence numbers, negotiated sizes, flags, descriptor pointers, and stats. Nothing persists across disconnect.

Dependencies and integration points: depends on CDC UAPI NCM/MBIM descriptors, usbnet, net_device/sk_buff/tasklet/hrtimer/spinlock consumers in implementation, and USB interface descriptors. It integrates CDC NCM/MBIM class networking with Linux networking.

Risks and test signals: risks include NTB/NDP bounds validation, sequence handling, timer/tasklet races on disconnect, low-memory TX aggregation behavior, altsetting toggles for MBIM, MTU/max-datagram negotiation, and alignment/modulus mistakes. Test with NCM and MBIM devices, malformed NTBs, MTU changes, suspend/resume, disconnect under traffic, high-throughput aggregation stats, and packet fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc_ncm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ch9.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ch9.h

Purpose: wraps USB chapter 9 UAPI definitions and declares kernel helpers for descriptor/speed/state strings, maximum speed discovery, SuperSpeed Plus rate discovery, endpoint interval decoding, and trace formatting.

Important APIs and types: `enum usb_ssp_rate` classifies SuperSpeed Plus generation/lane combinations. Helpers include `usb_ep_type_string()`, `usb_speed_string()`, `usb_get_maximum_speed()`, `usb_get_maximum_ssp_rate()`, `usb_state_string()`, `usb_decode_interval()`, and tracing-only `usb_decode_ctrl()`.

Control flow: USB host and gadget code use this header for common chapter 9 constants, user-readable diagnostics, firmware/property maximum-speed lookup, interval decoding from endpoint descriptors, and tracepoint control-request formatting.

State and persistence: no state is stored. Helpers query device properties or decode descriptor fields.

Dependencies and integration points: includes `<uapi/linux/usb/ch9.h>` and forward-declares `struct device`. It is shared by usbcore, gadget, HCD, and class drivers.

Risks and test signals: risks include incorrect speed/property mapping, interval decoding differences across speeds/transfer types, and trace formatting buffer truncation. Test with device-tree/ACPI maximum-speed properties, endpoint interval matrices, tracepoints, and all USB speed enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ch9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/chipidea.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/chipidea.h

Purpose: defines platform data, flags, cable state, hooks, and device-management APIs for the ChipIdea dual-role USB controller driver.

Important APIs and types: `struct ci_hdrc_cable` tracks extcon cable connection/change/enabled state and notifier registration. `struct ci_hdrc_platform_data` carries register offsets, power budget, PHY pointers/mode, many quirk flags, dual-role mode, notifier callback, VBUS regulator, OTG caps, TPL support, interrupt/burst tuning, VBUS/ID extcon state, PHY clock gate delay, pinctrl states, hub-control hook, and low-power-mode hook. APIs add/remove a ChipIdea platform device and query available role.

Control flow: glue drivers fill platform data and call `ci_hdrc_add_device()`. The ChipIdea core uses flags and hooks to initialize host/device/OTG roles, manage PHY/regulator/pinctrl/extcon state, notify platform events, handle role switching, and apply hardware workarounds.

State and persistence: platform data is boot/probe-time configuration; cable structs hold runtime extcon state. Hardware controller state and role state live in the ChipIdea driver.

Dependencies and integration points: depends on extcon, USB OTG, regulators, PHY, pinctrl, platform devices, and hub-control integration. It bridges SoC glue layers to the generic ChipIdea controller.

Risks and test signals: risks include incompatible flag combinations, extcon notification races, VBUS/regulator ordering, dual-role-not-OTG confusion, DMA alignment constraints, and platform hook failures. Test host/device/dual-role modes, cable insertion/removal, suspend/resume, role switching, pinctrl transitions, and SoC-specific quirk coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/chipidea.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/composite.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/composite.h

Purpose: declares the USB gadget composite framework, which lets gadget drivers combine multiple functions and configurations into one USB device.

Important APIs and types: OS descriptor types include `usb_os_desc_ext_prop`, `usb_os_desc`, and `usb_os_desc_table`. `struct usb_function` defines per-function descriptors, OS descriptors, bind/unbind/free hooks, altsetting, setup, suspend/resume, status, and function-suspend callbacks plus endpoint bitmap and instance link. `struct usb_configuration` groups functions and descriptor metadata. `struct usb_composite_driver` wraps device descriptor template, strings, max speed, bind/unbind/disconnect/suspend/resume hooks, and `usb_gadget_driver`. `struct usb_composite_dev` stores the gadget, EP0 requests, active config, OS/WebUSB metadata, descriptor/string state, deactivation and delayed-status counters, and setup-pending flags. Function-driver/configfs APIs include function registration, get/put instance/function, add/remove function/config, string ID allocation, descriptor overwrite options, and module helper macros.

Control flow: a composite driver registers, bind allocates strings/configurations/functions, functions bind and autoconfigure endpoints, the gadget handles EP0 setup by dispatching standard/config/function requests, and host set-configuration/set-interface calls activate or disable functions. Delayed status lets functions pause control completion until ready. Configfs function drivers allocate instances and functions dynamically.

State and persistence: runtime state includes active configuration, function lists, endpoint allocations, string IDs, OS/WebUSB descriptor buffers, deactivation count, delayed status count, and configfs instance objects. Module parameters can override descriptor IDs/strings at load time; no long-term persistent storage is managed.

Dependencies and integration points: depends on USB gadget API, chapter 9 descriptors, WebUSB, configfs, bcd/version helpers, and module infrastructure. It is the main integration layer for gadget functions such as HID, mass storage, CDC, FunctionFS, and configfs-composed gadgets.

Risks and test signals: risks include EP0 delayed-status leaks, function bind/unbind lifetime errors, string/interface ID exhaustion, endpoint autoconfig mismatch across speeds, OS/WebUSB descriptor bounds, configfs reference leaks, and suspend/resume ordering across functions. Test gadget enumeration at full/high/super speeds, multi-function configs, set_alt reset semantics, delayed setup continuation, configfs create/remove, module parameter overrides, and disconnect during active requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/composite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci-dbgp.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ehci-dbgp.h

Purpose: declares EHCI debug-port register layout and optional early-printk/Xen integration hooks.

Important APIs and types: `struct ehci_dbg_port` maps debug-port control, PID, data, and address registers. Bit macros describe ownership, enable/done/in-use/error/go/out/length fields, error codes, PID packing, and endpoint address packing. Optional APIs include `early_dbgp_init`, `early_dbgp_console`, `dbgp_reset_prep()`, `dbgp_external_startup()`, and Xen-specific reset/startup hooks with stubs when configs are disabled.

Control flow: early console/debug code initializes the EHCI debug port, takes ownership, sends/receives debug packets through the register block, and EHCI host reset/startup paths call debug prep hooks so debug-port use survives controller initialization where possible.

State and persistence: hardware debug-port registers hold transient transfer state. Early console state is owned by the debug driver; the header stores none.

Dependencies and integration points: depends on console/types, `struct usb_hcd`, EHCI host driver reset paths, `CONFIG_EARLY_PRINTK_DBGP`, and Xen dom0 hooks.

Risks and test signals: risks include conflicting ownership with EHCI driver, early-boot MMIO access before mapping is stable, wrong non-config stubs, and Xen handoff differences. Test early printk over EHCI debug devices, EHCI reset with debug enabled, Xen dom0 paths, and builds with configs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci-dbgp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci_def.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ehci_def.h

Purpose: defines EHCI host-controller capability and operational register layouts plus bitfield macros.

Important APIs and types: `struct ehci_caps` maps capability registers (`hc_capbase`, `hcs_params`, `hcc_params`, `portroute`) and macros decode cap length, version, debug port, companion controllers, port counts, PPC, LPM, prefetch, periodic size, 64-bit addressing, and extended caps. `struct ehci_regs` maps command, status, interrupt enable, frame index, segment, periodic/async list pointers, TX tuning, config flag, port status/control, USBMODE, HOSTPC/Broadcom extension registers, and USBMODE_EX. Macros define command/status, port, mode, and hostpc bits including write-clear port change bits.

Control flow: EHCI HCDs ioremap controller registers, decode caps, reset/start the controller via command bits, configure schedules and port ownership/power/reset/suspend, service status interrupts, and apply platform-specific register extensions.

State and persistence: all state is hardware MMIO state plus DMA schedule pointers programmed by the HCD. The header only defines layouts and bit masks.

Dependencies and integration points: includes EHCI debug-port definitions and relies on HCD helpers such as `ehci_big_endian_capbase()` supplied by implementation code. It integrates generic EHCI core with PCI/platform/SoC HCDs.

Risks and test signals: risks include endian/capbase decoding errors, write-one-to-clear mishandling of port bits, invalid port count assumptions, 64-bit DMA segment setup bugs, and extension register conflicts. Test EHCI on big/little-endian systems, port reset/suspend/resume, interrupt status handling, companion-controller handoff, and SoC-specific HOSTPC/Broadcom paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci_pdriver.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ehci_pdriver.h

Purpose: defines platform data for the generic platform EHCI host-controller driver.

Important APIs and types: `struct usb_ehci_pdata` carries capability-register offset, integrated TT flag, hardware quirk flags for Synopsys, endian descriptors/MMIO, watchdog, reset-on-resume, 64-bit DMA, spurious overcurrent, and platform hooks for power on/off/suspend and pre-setup.

Control flow: platform glue provides this data at probe; the generic EHCI platform driver powers clocks/regulators, applies pre-setup quirks, configures endian/DMA/watchdog behavior, and handles suspend/resume power transitions through hooks.

State and persistence: platform data is static configuration plus callback pointers. Runtime controller state is owned by the EHCI HCD and platform driver.

Dependencies and integration points: forward-declares platform devices and USB HCDs. It integrates board/SoC glue with generic EHCI core.

Risks and test signals: risks include wrong caps offset, endian flags mismatched to hardware, power hook ordering failures, reset-on-resume data loss, and spurious overcurrent masking real faults. Test platform probe/remove, power transitions, suspend/resume, DMA mask selection, and quirk-specific controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci_pdriver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ezusb.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ezusb.h

Purpose: declares helper APIs for Cypress EZ-USB FX1 reset control and Intel HEX firmware download.

Important APIs and types: `ezusb_fx1_set_reset()` toggles the FX1 reset bit on a USB device. `ezusb_fx1_ihex_firmware_download()` downloads firmware from a named Intel HEX firmware file to the device.

Control flow: device drivers put the FX1 into reset, load firmware records, then release reset so the device can renumerate or start its programmed behavior.

State and persistence: state is hardware device reset state and volatile downloaded firmware. The firmware path references persistent firmware storage, but the header owns none.

Dependencies and integration points: forward-declared `struct usb_device` is expected from USB includes. It integrates USB device drivers with firmware-loading and vendor-control-transfer implementation code.

Risks and test signals: risks include leaving devices in reset, partial firmware downloads, firmware path errors, and renumeration timing races. Test successful and failed firmware load, reset release, disconnect during download, and device re-enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ezusb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/func_utils.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/func_utils.h

Purpose: provides utility macros and request allocation helpers for USB gadget function drivers.

Important APIs and types: VLA layout macros `vla_group`, `vla_group_size`, `vla_item`, `vla_item_with_sz`, and `vla_ptr` compute aligned offsets and total sizes for packed variable-length allocations with overflow detection. `alloc_ep_req()` allocates a gadget endpoint request and buffer, with OUT endpoint buffer length aligned to maxpacket. `free_ep_req()` frees the buffer and request.

Control flow: function drivers compute one allocation layout using VLA macros, allocate storage, derive typed subobject pointers with `vla_ptr()`, allocate endpoint requests with `alloc_ep_req()`, and release them with `free_ep_req()`.

State and persistence: VLA macros produce local offset/size variables. USB request state lives in allocated `struct usb_request` objects and buffers until freed.

Dependencies and integration points: depends on USB gadget API and overflow helpers. It integrates with composite gadget function implementations that need compact dynamic descriptors or request buffers.

Risks and test signals: risks include using VLA offsets after overflow set total size to `SIZE_MAX`, mismatched free paths, buffer length assumptions for OUT endpoints, and `WARN_ON` if freeing a request with a null buffer. Test variable-size allocation overflow, alignment of generated layouts, request allocation/free under endpoint maxpacket variants, and error unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/func_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/functionfs.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/functionfs.h

Purpose: kernel wrapper that exposes FunctionFS UAPI definitions to kernel code.

Important APIs and types: this header defines no new symbols; it includes `<uapi/linux/usb/functionfs.h>`.

Control flow: FunctionFS implementation and gadget code include this wrapper when they need descriptor/event/ioctl constants shared with userspace.

State and persistence: no state is stored here. Runtime FunctionFS state lives in the FunctionFS filesystem and gadget function implementation.

Dependencies and integration points: integrates kernel FunctionFS code with the UAPI contract used by userspace gadget daemons.

Risks and test signals: risks are UAPI drift or include-order breakage. Test FunctionFS descriptor submission, event delivery, endpoint I/O, and kernel/userspace header compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/functionfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/g_hid.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/g_hid.h

Purpose: defines the platform/config descriptor passed to the legacy USB HID gadget driver.

Important APIs and types: `struct hidg_func_descriptor` carries HID subclass, protocol, report length, report descriptor length, and flexible report descriptor bytes.

Control flow: board or gadget setup code supplies this descriptor; the HID gadget function uses it to expose the HID interface and report descriptor to the USB host and to size report I/O.

State and persistence: descriptor data is static gadget configuration. Runtime HID reports and endpoint state are owned by the HID gadget driver.

Dependencies and integration points: no explicit includes. It integrates legacy platform-data HID gadgets with USB composite/gadget HID implementation.

Risks and test signals: risks include report descriptor length mismatch, invalid HID report descriptors, and subclass/protocol values binding the wrong host driver behavior. Test HID gadget enumeration, descriptor reads, report send/receive lengths, and host compatibility for boot keyboard/mouse protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/g_hid.h -->
