<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/num/bounded.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/num/bounded.rs

## Purpose
Implements `Bounded<T, N>`, a transparent integer wrapper whose value is guaranteed to fit in `N` low-order bits of an integer backing type. The abstraction is aimed at bitfield-style kernel code where compile-time or runtime proofs about representable ranges are useful.

## APIs, Types, and Functions
Core APIs are `Bounded::new::<VALUE>()`, `try_new`, `from_expr`, `get`, `extend`, `try_shrink`, `cast`, `shl`, and `shr`. `TryIntoBounded` provides fallible conversion from arbitrary integer types. The file implements comparison, arithmetic/bitwise operator forwarding, formatting traits, primitive `From` conversions gated by local size-marker traits, and single-bit bool conversions. `fits_within!` and `fits_within()` are the central range predicates and work for signed and unsigned integer types by shift-roundtripping.

## Control Flow, State, and Persistence
Construction is the only state transition that matters: every public constructor proves the value fits, then delegates to unsafe `__new`, which enforces `N != 0` and `N <= T::BITS` with const assertions. `Deref` rechecks the invariant and uses `unreachable_unchecked` to feed optimizer range knowledge. Arithmetic returns the primitive backing type rather than a new bounded value, avoiding accidental false range guarantees. There is no persistent runtime state.

## Dependencies and Integration
Depends on `kernel::num::Integer`, `Zeroable`, `build_assert`, `const_assert`, and core numeric/formatting traits. It integrates with the kernel Rust numeric module and supports const-generic callers that need type-level bit-width evidence.

## Risks and Test Signals
The main risks are invariant unsoundness in `__new` callers, misuse of `from_expr` on expressions the optimizer cannot prove, signed shift semantics assumptions, and the large macro-generated conversion lattice missing a width or signedness case. Useful test signals are doctests for boundary values, compile-fail tests for invalid bit widths and conversions, runtime signed/unsigned edge checks, bool conversion tests, and generated assembly or MIR inspection for `from_expr` assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/num/bounded.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/of.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/of.rs

## Purpose
Provides Rust wrappers for Open Firmware / Device Tree match identifiers and a macro for exporting OF device-id tables to the kernel module infrastructure.

## APIs, Types, and Functions
`DeviceId` is a transparent wrapper over `bindings::of_device_id`. `DeviceId::new` builds a const-compatible ID from a static compatible string by zero-initializing the C struct and copying bytes into `compatible`. `IdTable<T>` aliases the shared `device_id::IdTable` abstraction. `of_device_table!` builds an `IdArray` and emits `MODULE_DEVICE_TABLE(of, ...)` metadata through `module_device_table!`.

## Control Flow, State, and Persistence
There is no dynamic control flow beyond const construction. Match table entries persist as static data in the module image. `RawDeviceIdIndex::index` reads the C `data` field and treats it as an index into the Rust sidecar info table.

## Dependencies and Integration
Depends on generated `bindings::of_device_id`, `device_id::{RawDeviceId, RawDeviceIdIndex}`, `CStr`, and module alias generation. It is consumed by platform drivers through `platform::Driver::OF_ID_TABLE`.

## Risks and Test Signals
Risks include overlong compatible strings overflowing the fixed C array at compile time, incorrect `data` offset breaking sidecar info lookup, and modpost alias regressions if the macro layout changes. Test signals include compile tests for generated OF tables, modinfo alias inspection, and platform probe tests that verify matched `IdInfo` is delivered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/of.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/opp.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/opp.rs

## Purpose
Wraps the Linux OPP subsystem for Rust drivers. It models dynamic operating performance points, device OPP configuration, OPP table lookup and mutation, optional cpufreq table generation, energy-model registration, and refcounted OPP handles.

## APIs, Types, and Functions
Unit wrappers `MicroVolt` and `MicroWatt` convert to `c_ulong`; `Data` builds `dev_pm_opp_data` for dynamic entries; `Token` removes a dynamic OPP on drop. `SearchType` selects exact, floor, or ceil lookup. `ConfigOps` exposes optional clock and regulator callbacks through a vtable-style trait, and `Config<T>` accumulates property names, clock names, regulator names, supported hardware, and required-device settings before `set` returns a `ConfigToken`. `Table` wraps `opp_table` and exposes `from_dev`, OF constructors, count/latency/suspend queries, sharing CPU helpers, voltage adjustment, rate and OPP setting, frequency/level/bandwidth lookup, enable/disable, cpufreq table creation, and energy-model registration. `OPP` wraps `dev_pm_opp` and exposes frequency, voltage, level, power, required pstate, and turbo state.

## Control Flow, State, and Persistence
Most operations are thin checked calls into `dev_pm_opp_*`. RAII drives persistence: `Token::drop` removes dynamic OPPs, `ConfigToken::drop` clears OPP config, `Table::drop` releases the table reference and conditionally unregisters EM or removes OF/cpumask tables, `FreqTable::drop` frees cpufreq tables, and `ARef<OPP>` releases OPP refs through `AlwaysRefCounted`. `Config::set` builds temporary null-terminated pointer arrays from owned `CString`s and relies on the OPP core not retaining those arrays after the call. C callbacks recover `Device`, `Table`, and `OPP` references and translate Rust `Result` to errno.

## Dependencies and Integration
Depends on `Device`, `ARef`, `Cpumask`, `CpumaskVar`, `Hertz`, `CString`, `KVec`, generated OPP/cpufreq/regulator bindings, `CONFIG_OF`, `CONFIG_CPU_FREQ`, and `CONFIG_ENERGY_MODEL`. Integration points are power management, cpufreq, regulator/clock callbacks, device tree OPP tables, and the energy model.

## Risks and Test Signals
Risks include wrong lifetime assumptions for config pointer arrays, double-removal or missing removal of OF/cpumask tables, lookup APIs returning owned refs with mismatched refcount expectations, exact frequency lookup requiring an `available` value, and callback default vtable methods being used unintentionally. Test signals include dynamic add/drop tests, config-token cleanup tests, OF table add/remove tests under `CONFIG_OF`, refcount leak checks, mocked callback error propagation, and cpufreq/EM cleanup under feature-gated builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/opp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/page.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/page.rs

## Purpose
Provides Rust allocation, ownership, borrowing, mapping, and raw byte-access primitives for kernel pages.

## APIs, Types, and Functions
Exports `PAGE_SHIFT`, `PAGE_SIZE`, `PAGE_MASK`, and `page_align`. `Page` owns a `struct page` allocated by `alloc_pages`; `BorrowedPage<'a>` wraps a non-owning page pointer using `ManuallyDrop<Page>`; `AsPageIter` abstracts page iterators from owning containers. `Page` exposes `alloc_page`, `as_ptr`, `nid`, `read_raw`, `write_raw`, `fill_zero_raw`, and `copy_from_user_slice_raw`.

## Control Flow, State, and Persistence
`alloc_page` converts allocation failure into `AllocError` and transfers page ownership into `Page`; `Drop` releases it with `__free_pages`. Access methods funnel through `with_pointer_into_page`, which validates offset/length against `PAGE_SIZE`, maps the page with `kmap_local_page`, invokes a closure, then unmaps with `kunmap_local`. Borrowed pages deliberately avoid drop-time free.

## Dependencies and Integration
Depends on allocation flags, generated page bindings, `UserSliceReader`, `NonNull`, and local mapping APIs. It integrates with vmalloc-backed allocators through `BorrowedPage` and with user access code through raw copy-from-user support.

## Risks and Test Signals
Risks include integer overflow in `off + len` bounds checking, caller-violated race-freedom requirements for raw reads/writes, using mapped pointers outside the closure or on another task, and treating a borrowed page as owned. Test signals include offset/length boundary tests including overflow-sized inputs, allocation/free leak checks, user-copy short-read/error tests, and KASAN/KCSAN stress around concurrent mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/page.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pci.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/pci.rs

## Purpose
Defines Rust PCI bus abstractions: driver registration, PCI ID table construction, basic device metadata/resource helpers, context conversions, DMA-device integration, and refcount handling.

## APIs, Types, and Functions
`Adapter<T>` implements the generic driver registration traits for `bindings::pci_driver`. `module_pci_driver!` declares a PCI module. `DeviceId` provides constructors equivalent to `PCI_DEVICE`, `PCI_DEVICE_CLASS`, and class-plus-vendor matching. `Driver` requires an ID table and `probe`, with optional `unbind`. `Device<Ctx>` exposes vendor/device/revision/subsystem/class identifiers, BDF ID, BAR resource start/length, `enable_device_mem`, and `set_master`.

## Control Flow, State, and Persistence
Registration fills the C driver name, probe/remove callbacks, and ID table before calling `__pci_register_driver`; unregister calls `pci_unregister_driver`. Probe casts the C `pci_dev` to `Device<CoreInternal>`, maps the matched raw ID to sidecar info, runs `T::probe`, and stores pinned driver data in `drvdata`. Remove retrieves that data and calls `T::unbind`. Device references are persisted through C refcounts via `pci_dev_get` and `pci_dev_put`.

## Dependencies and Integration
Depends on `driver`, `device`, `device_id`, `container_of`, `ARef` support through `AlwaysRefCounted`, PCI generated bindings, and submodules `pci::id`, `pci::io`, and `pci::irq`. It integrates with module aliasing, the PCI core, devres-based resources, IRQ helpers, and DMA traits.

## Risks and Test Signals
Risks include mismatched struct offsets, invalid assumptions in casts from C callbacks, probe failures after partial resource setup, ID sidecar index corruption, and context misuse between normal/core/bound devices. Test signals include probe/remove lifecycle tests, modinfo PCI alias checks, `TryFrom<&device::Device>` negative tests, BAR range validation, and refcount/leak instrumentation around `ARef`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pci.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pci/id.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/pci/id.rs

## Purpose
Centralizes typed PCI class-code and vendor-ID wrappers plus generated constants and formatting for use by PCI match tables and device logging.

## APIs, Types, and Functions
`Class` stores a 24-bit class code, with `from_raw`, `as_raw`, `Debug`, and generated `Display` names. `ClassMask` supports full 24-bit or class/subclass matching and implements `TryFrom<u32>`. `Vendor` stores a 16-bit vendor ID, exposes `from_raw` and `as_raw`, and has generated constants plus `Debug`/`Display`.

## Control Flow, State, and Persistence
The file is mostly static constant generation through macros. `Class::to_24bit_class` normalizes 16-bit class constants by shifting them into the upper 16 bits while leaving full 24-bit constants unchanged. Formatting matches known constants by value and falls back to hex debug output. There is no runtime state.

## Dependencies and Integration
Depends on generated PCI class/vendor bindings and kernel formatting/error aliases. It is re-exported by `pci.rs` and used by `DeviceId` constructors and `Device::pci_class`/`vendor_id`.

## Risks and Test Signals
Risks include stale generated constants relative to C headers, ambiguous display names for duplicate numeric constants, incorrect 16-bit-to-24-bit normalization, and incomplete class-mask support. Test signals include compile-time constant equality checks against bindings, formatting tests for known and unknown IDs, `ClassMask::try_from` boundary tests, and generated table smoke tests using class/vendor match constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pci/id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pci/io.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/pci/io.rs

## Purpose
Provides PCI configuration-space I/O and RAII-managed BAR MMIO mapping for bound PCI devices.

## APIs, Types, and Functions
`ConfigSpaceSize`, marker types `Normal` and `Extended`, and `ConfigSpaceKind` describe 256-byte and 4096-byte configuration spaces. `ConfigSpace<'a, S>` implements `Io`, `IoKnownSize`, and typed `IoCapable` for `u8`, `u16`, and `u32` using `pci_read_config_*` and `pci_write_config_*`. `Bar<SIZE>` owns a requested and ioremapped BAR, derefs to `Mmio<SIZE>`, and validates BAR indices. Bound devices expose `iomap_region_sized`, `iomap_region`, `cfg_size`, `config_space`, and `config_space_extended`.

## Control Flow, State, and Persistence
BAR mapping first checks resource length, requests the PCI region, maps it with `pci_iomap`, wraps the mapping in `MmioRaw`, and unwinds each acquired resource on error. `Drop` unmaps and releases the region. `iomap_region*` returns a devres-managed initializer so the BAR lifetime is tied to the bound device. Config-space access ignores C helper return values in the infallible `IoCapable` path and relies on higher-level bounds from the `Io` traits.

## Dependencies and Integration
Depends on PCI device wrappers, `devres::Devres`, `io::{Io, IoCapable, IoKnownSize, Mmio, MmioRaw}`, and C PCI config/resource/iomap helpers. It integrates with driver probe code after a device reaches bound context.

## Risks and Test Signals
Risks include ignored config read/write errors, assuming only 256 or 4096 cfg sizes, resource length truncation to `usize`, stale mappings after device removal if devres ownership is bypassed, and BAR index validation that accepts non-BAR resources because it uses `PCI_NUM_RESOURCES`. Test signals include fault-injection for request/map failures, drop-order cleanup checks, extended-config rejection on normal devices, and MMIO bounds tests for sized and unsized BARs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pci/io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pci/irq.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/pci/irq.rs

## Purpose
Wraps PCI IRQ vector allocation and converts allocated vectors into generic Rust IRQ registration objects.

## APIs, Types, and Functions
`IrqType` maps INTx, MSI, and MSI-X to kernel flags. `IrqTypes` is a bitset builder with `all` and `with`. `IrqVector<'a>` ties a vector index to the bound PCI device that owns it and implements `TryInto<IrqRequest<'a>>`. `Device<Bound>` exposes `alloc_irq_vectors`, `request_irq`, and `request_threaded_irq`.

## Control Flow, State, and Persistence
`IrqVectorRegistration::register` calls `pci_alloc_irq_vectors`, builds an inclusive range from vector 0 to count-1, and registers a guard with devres. The guard holds an `ARef<Device>` and frees all PCI IRQ vectors on drop. Request helpers convert a vector to a concrete IRQ number with `pci_irq_vector` inside a `pin_init_scope`, then construct the generic IRQ registration.

## Dependencies and Integration
Depends on PCI device wrappers, `devres`, generic `irq` request/registration APIs, `CStr`, and PCI IRQ allocation bindings. It integrates with bound PCI drivers that need MSI/MSI-X/INTx allocation before registering interrupt handlers.

## Risks and Test Signals
Risks include allowing `min_vecs == 0` even though range construction assumes `count >= 1`, passing a vector from one allocation after vectors were freed, devres registration failure after allocation, and mismatched handler lifetimes. Test signals include vector allocation failure injection, min/max boundary tests, devres cleanup checks, threaded and non-threaded handler registration smoke tests, and validation that stale vectors cannot be constructed by safe APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pci/irq.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pid_namespace.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/pid_namespace.rs

## Purpose
Provides a transparent, thread-safe Rust reference type for kernel `struct pid_namespace` values.

## APIs, Types, and Functions
`PidNamespace` wraps `Opaque<bindings::pid_namespace>`. `as_ptr` returns the raw C pointer, and unsafe `from_ptr` builds a borrowed reference from a valid raw pointer. `AlwaysRefCounted` increments with `get_pid_ns` and decrements with `put_pid_ns`.

## Control Flow, State, and Persistence
The wrapper itself has no active behavior beyond pointer conversion and refcount operations. Ownership persistence is handled by `ARef` users through the `AlwaysRefCounted` implementation; borrowed references from `from_ptr` rely entirely on the caller's lifetime guarantee.

## Dependencies and Integration
Depends on pid namespace bindings, `Opaque`, `AlwaysRefCounted`, and `NonNull`. It integrates with kernel code that exposes pid namespace pointers to Rust subsystems needing borrowed or owned references.

## Risks and Test Signals
Risks include unsafe `from_ptr` on null or stale namespace pointers, refcount misuse outside `ARef`, and assuming all namespace fields are immutable without C-side synchronization. Test signals include refcount leak checks, null/stale pointer audits at call sites, and thread handoff tests for `ARef<PidNamespace>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pid_namespace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/platform.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/platform.rs

## Purpose
Defines Rust platform-bus driver registration, platform device wrappers, memory resource lookup, IRQ request helpers, DMA integration, context conversion, and refcount handling.

## APIs, Types, and Functions
`Adapter<T>` bridges `platform::Driver` to `bindings::platform_driver`. `module_platform_driver!` declares a module. `Driver` supports optional OF and ACPI ID tables plus `probe` and optional `unbind`. `Device<Ctx>` exposes memory `resource_by_index`, `resource_by_name`, bound-only `io_request_by_index/name`, IRQ lookup by index/name with optional variants, and generated request helpers for regular and threaded IRQ registrations.

## Control Flow, State, and Persistence
Registration fills platform driver name, probe/remove callbacks, OF and ACPI match tables, then calls `__platform_driver_register`; unregister calls `platform_driver_unregister`. Probe casts the C platform device, resolves optional sidecar match info through the generic driver adapter, initializes pinned driver state, and stores it in `drvdata`. Remove retrieves pinned state and calls `unbind`. Resource and IRQ helpers query the C platform core and convert negative IRQ returns into `Error`.

## Dependencies and Integration
Depends on `acpi`, `of`, `device`, `driver`, `io::Resource`, `IoRequest`, generic IRQ APIs, `container_of`, generated platform bindings, and `AlwaysRefCounted`. It integrates with OF/ACPI matching, devres-backed MMIO requests, IRQ registration, DMA traits, and module driver macros.

## Risks and Test Signals
Risks include incorrect match-info resolution when both OF and ACPI tables exist, storing/borrowing wrong drvdata type, optional IRQ APIs still surfacing negative errors that callers must interpret, resource pointers outliving the platform device, and context misuse around `Bound`. Test signals include OF and ACPI probe tests, resource-by-name/index tests, optional IRQ absence tests, regular/threaded IRQ registration smoke tests, and refcount checks for `get_device`/`platform_device_put`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/platform.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/prelude.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/prelude.rs

## Purpose
Defines the common import surface for Rust kernel code, bundling core traits, C FFI aliases, macros, pin-init helpers, allocator types, errors, logging macros, and frequently used kernel utilities.

## APIs, Types, and Functions
Re-exports selected `core::mem` functions and `Pin`, FFI scalar aliases and `CStr`, procedural/helper macros, pin-init traits/macros, allocator containers and flags, build assertions, current task, device and printk logging macros, `Error`/`Result` and errno constants, `InPlaceInit`, `UserPtr`, `ThisModule`, and `dbg`.

## Control Flow, State, and Persistence
There is no runtime control flow or state. The file controls namespace visibility and compile-time ergonomics for downstream modules that use `kernel::prelude::*`.

## Dependencies and Integration
Depends on the crate's allocator, error, init, string, uaccess, print, and macro modules plus external `ffi`, `macros`, and `pin_init` crates. It is imported by most Rust kernel modules and affects public API discoverability.

## Risks and Test Signals
Risks include accidental API bloat, name collisions, making hidden implementation details part of common usage, or removing an export relied on by many drivers. Test signals are broad build coverage, doctests using `prelude::*`, rustdoc visibility checks, and compile-fail tests for intentionally non-prelude APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/prelude.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/print.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/print.rs

## Purpose
Implements Rust printk support, including severity macros, continuation logging, `%pA` formatting bridge support, and lightweight once-only logging macros.

## APIs, Types, and Functions
`rust_fmt_argument` is the C-callable `%pA` formatter for `fmt::Arguments`. `format_strings` generates static `_printk` format strings for each kernel log level. Hidden helpers `call_printk` and `call_printk_cont` invoke `_printk`. Public macros include `pr_emerg!`, `pr_alert!`, `pr_crit!`, `pr_err!`, `pr_warn!`, `pr_notice!`, `pr_info!`, `pr_debug!`, `pr_cont!`, `do_once_lite!`, and `pr_*_once!`. `OnceLite` is a relaxed atomic call-once primitive.

## Control Flow, State, and Persistence
Print macros build `fmt::Arguments` outside the unsafe call and pass the module prefix plus fixed format string to `_printk` when `CONFIG_PRINTK` is enabled. `pr_debug!` is gated by `debug_assertions`. `do_once_lite!` creates a static `OnceLite` in `.data..once`; the first caller swaps state to complete and runs the closure, while later callers return without synchronization guarantees.

## Dependencies and Integration
Depends on generated printk bindings, `RawFormatter`, the Rust formatting system, atomic wrappers, module-generated `__LOG_PREFIX`, and kernel printk `%pA` integration. It is re-exported through the prelude and used pervasively by Rust kernel code.

## Risks and Test Signals
Risks include unsafety in `%pA` pointer interpretation, module prefix lifetime/null-termination assumptions, no dynamic-debug support for `pr_debug!`, relaxed `OnceLite` being mistaken for a synchronization primitive, and behavior differences when `CONFIG_PRINTK` is disabled. Test signals include printk macro compile tests, once-only concurrent stress, `%pA` formatting tests with bounded buffers, and builds with/without `CONFIG_PRINTK` and `testlib`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/print.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/processor.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/processor.rs

## Purpose
Provides a minimal Rust wrapper for processor relaxation in spin-wait loops.

## APIs, Types, and Functions
`cpu_relax()` calls the architecture/kernel `cpu_relax` binding. It is inline and safe because the C helper is safe to call and acts as a low-power hint or compiler barrier.

## Control Flow, State, and Persistence
There is no state. Each invocation forwards directly to the C binding.

## Dependencies and Integration
Depends on generated processor bindings and mirrors `include/linux/processor.h`. It integrates with polling loops and lock-free wait paths in Rust kernel code.

## Risks and Test Signals
Risks are limited but include missing import of `bindings` if module scope changes and callers using it where a stronger memory ordering primitive is required. Test signals are build coverage on supported architectures and review of spin loops to ensure explicit atomic orderings surround relaxation calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/processor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/ptr.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/ptr.rs

## Purpose
Provides pointer and address utility types: validated power-of-two alignments, alignment operations on unsigned integers, compile-time/dynamic-size helpers, const alignment, and re-export of raw pointer projection support.

## APIs, Types, and Functions
`Alignment` wraps `NonZero<usize>` and exposes const `new`, `new_checked`, `of<T>`, `as_usize`, `as_nonzero`, `log2`, and `mask`. `Alignable` defines `align_down` and overflow-checked `align_up`, implemented for `u8`, `u16`, `u32`, `u64`, and `usize`. `KnownSize` generalizes `size_of` for sized types and slices. `const_align_up` is a const-compatible `usize` alignment helper. The module exports `projection` and aliases `project_pointer!` as `ptr::project!`.

## Control Flow, State, and Persistence
Construction of `Alignment` validates the power-of-two invariant. Alignment operations compute masks, handle alignments larger than the target integer by aligning down to zero, and return `None` when aligning up would overflow or the alignment does not fit in the target type. There is no persistent state.

## Dependencies and Integration
Depends on `core::mem`, `NonZero`, and crate build assertions. It supports allocator, MMIO, DMA, and raw-pointer code that needs explicit alignment reasoning.

## Risks and Test Signals
Risks include callers assuming `align_up` succeeds for alignments wider than the integer type, arithmetic overflow regressions in const and runtime paths, and unsafely relying on `KnownSize` for invalid DST metadata. Test signals include power-of-two validation tests, integer-width edge tests, `usize::MAX` overflow checks, slice-size tests, and compile tests for `Alignment::of`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/ptr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/ptr/projection.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/ptr/projection.rs

## Purpose
Implements `ptr::project!`, a raw-pointer projection macro for field and index access that preserves provenance and supports fallible bounds checking without requiring the base pointer to be dereferenceable.

## APIs, Types, and Functions
`OutOfBound` converts to `ERANGE`. Unsafe trait `ProjectIndex<T>` defines `get` and build-checked `index`; implementations cover arrays through slice forwarding, `usize`, `Range`, `RangeTo`, `RangeFrom`, and `RangeFull`. Unsafe trait `ProjectField<const DEREF: bool>` computes field offsets, with a guard implementation for `Deref` types to reject projections that could invoke custom deref behavior. `project_pointer!` parses `.field`, `[index]`, and `[index]?` chains for const and mutable raw pointers.

## Control Flow, State, and Persistence
Index projection either returns `None`/`OutOfBound` for runtime-checked forms or triggers `build_error!` when compile-time checking cannot prove safety. Field projection creates an uninitialized local allocation solely to compute field offsets with raw field pointers, then applies the offset to the original base using wrapping byte offsets. Macro expansion repeatedly shadows the projected pointer through each projection component. There is no runtime state.

## Dependencies and Integration
Depends on `MaybeUninit`, `Deref`, `build_error`, `Error`, and the parent `ptr` module. It integrates with low-level code that must compute subobject pointers for MMIO, DMA, packed-compatible checks, or non-address-space pointers.

## Risks and Test Signals
Risks include incorrect unsafe `ProjectIndex` implementations, projection through `Deref` or indexing traits that would be unsound, unaligned field access assumptions, and compiler changes around raw field pointer validity. Test signals include compile-fail tests for out-of-bounds static indexes and `Deref` bases, runtime `ERANGE` tests for `[index]?`, provenance-sensitive Miri-style tests where possible, and packed/unaligned field projection build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/ptr/projection.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pwm.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/pwm.rs

## Purpose
Provides Rust abstractions for PWM devices and chips, including waveform conversion, consumer-side waveform operations, driver operation callbacks, vtable generation, chip allocation, registration, refcounting, and platform-driver module glue.

## APIs, Types, and Functions
`Waveform` mirrors `struct pwm_waveform`; `RoundingOutcome` reports whether rounding was exact/down or up; `Device` wraps `pwm_device` and exposes `hwpwm`, `chip`, `label`, `set_waveform`, `round_waveform`, and `get_waveform`. `PwmOps` defines driver hooks for request, capture, waveform round-trip conversion, hardware read, and hardware write with associated `WfHw`. `RoundedWaveform<WfHw>` carries callback status and hardware form. `Adapter<T>` serializes/deserializes hardware waveforms, bridges C callbacks, and installs a release callback. `PwmOpsVTable`, `create_pwm_ops`, `Chip<T>`, `UnregisteredChip`, `Registration`, and `module_pwm_platform_driver!` cover controller registration and cleanup.

## Control Flow, State, and Persistence
Consumer methods convert between Rust and C waveforms and call `*_might_sleep` PWM helpers. Driver registration allocates a `pwm_chip` plus private data, pinned-initializes `T` in the private area, installs a release callback and static ops table, wraps the chip in `ARef`, and returns an `UnregisteredChip`. `register` calls `__pwmchip_add`, then devres-registers a `Registration` guard whose drop calls `pwmchip_remove`. Final device release drops the Rust driver data and delegates to `pwmchip_release`. Refcounting is implemented via the chip's embedded `struct device`.

## Dependencies and Integration
Depends on PWM generated bindings, `device`, `devres`, `ARef`, `AlwaysRefCounted`, `container_of`, `PinInit`, and platform-driver macros. It integrates with the C PWM core, parent bound devices, devres cleanup, and the `PWM` namespace import through `module_pwm_platform_driver!`.

## Risks and Test Signals
Risks include `WfHw` size exceeding `PWM_WFHWSIZE`, incorrect serialization of non-plain-old-data hardware representations, callback assumptions that parent devices are bound, cleanup gaps if devres registration fails after `__pwmchip_add`, and double-drop risks around custom release handling. Test signals include chip allocation failure injection, `WfHw` size compile checks, callback error propagation tests, register/drop cleanup tests, waveform round-trip tests, and namespace/module build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/pwm.rs -->
