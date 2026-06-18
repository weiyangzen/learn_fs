# Research: subset-b-003791

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/commands.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/commands.rs

Purpose: Rust wrapper layer for a small set of NVIDIA GSP firmware command payloads. It turns generated bindgen ABI structs into typed Nova-Core command objects that can be initialized safely enough for command queue submission.

Important APIs and types: `GspSetSystemInfo::init()` builds `bindings::GspSystemInfo` from PCI BAR resources, PCI IDs, and fixed configuration mirror values. `PackedRegistryEntry::new()` creates DWORD registry entries. `PackedRegistryTable::init()` creates a variable-length table header. `GspStaticConfigInfo::gpu_name_str()` exposes the firmware-provided GPU name bytes.

Control flow: callers construct command payloads through in-place initializers, then serialize them through `AsBytes` for GSP RPC paths. `GspSetSystemInfo` depends on `pci::Device<Bound>` resource reads, so initialization can fail before any command is sent.

State and persistence: no persistent state is owned here; all data is transient command payload state. The ABI values are persisted only when copied into command buffers.

Dependencies and integration: depends on generated `r570_144` bindings, kernel PCI/device APIs, `GSP_PAGE_SIZE`, and kernel transmute traits. It integrates with higher GSP firmware command modules by providing byte-compatible payload wrappers.

Risks: unsafe `AsBytes`/`FromBytes` implementations intentionally accept padding because the data stays inside the kernel; ABI layout drift or uninitialized padding assumptions would be high risk. `maxUserVa` is hard-coded and noted as questionable relative to upstream RM behavior.

Test signals: no direct tests. Confidence should come from GSP boot/RPC integration tests, command-size assertions, and failures in firmware initialization if system info or registry payloads are malformed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/commands.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/r570_144.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/r570_144.rs

Purpose: firmware ABI import module for the R570.144 GSP interface. It centralizes inclusion of bindgen-generated structs, constants, unions, and enum values.

Important APIs and types: `include!("r570_144/bindings.rs")` exposes all generated ABI symbols. The module suppresses lint noise expected from C-bindgen output and implements `Zeroable` for `__IncompleteArrayField<T>`.

Control flow: there is no runtime control flow beyond module inclusion. Parent modules are expected to abstract or re-export only the needed symbols instead of using this generated surface directly.

State and persistence: no runtime state. It defines layout contracts that other GSP code copies into queues, WPR metadata, registry tables, sequencer messages, and system-info structures.

Dependencies and integration: depends on `kernel::ffi` C type aliases and `pin_init::MaybeZeroable`. It integrates with `commands.rs`, sequencer wrappers, command queue code, and firmware metadata builders.

Risks: generated bindings are broad and easy to misuse directly. ABI drift between firmware version and Rust wrappers can produce silent layout incompatibility. The unsafe `Zeroable` implementation for incomplete arrays is correct only because the type is zero-sized.

Test signals: no direct tests. Build failures, static assertions in wrapper modules, and boot-time GSP command failures are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/r570_144.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/r570_144/bindings.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/r570_144/bindings.rs

Purpose: bindgen-generated Rust representation of the NVIDIA R570.144 GSP firmware ABI. It provides constants and C-layout types for vGPU/GSP RPC functions, events, WPR metadata, message queues, registry data, static GPU info, system info, and CPU sequencer command payloads.

Important APIs and types: `NV_VGPU_MSG_FUNCTION_*` and `NV_VGPU_MSG_EVENT_*` enumerate firmware RPC functions and events. Key structs include `GspSystemInfo`, `GspStaticConfigInfo_t`, `GspFwWprMeta`, `GSP_ARGUMENTS_CACHED`, `rpc_message_header_v`, `GSP_MSG_QUEUE_ELEMENT`, `PACKED_REGISTRY_TABLE`, `PACKED_REGISTRY_ENTRY`, `rpc_run_cpu_sequencer_v17_00`, and `GSP_SEQUENCER_BUFFER_CMD`. `__IncompleteArrayField<T>` models C flexible arrays.

Control flow: no driver logic is implemented here. Runtime behavior arises when higher-level wrappers read or write these layouts into firmware queues and shared buffers.

State and persistence: these definitions describe persistent shared-memory formats exchanged with GSP firmware. WPR metadata and queue headers carry boot and RPC state; static config carries discovered GPU capabilities.

Dependencies and integration: generated from C ABI headers and consumed by `r570_144.rs`, GSP command code, command queue code, sequencer parsing, and firmware boot metadata setup.

Risks: this file is layout-critical. Manual edits, bindgen option changes, endian assumptions, default zeroing of unions, and flexible-array sizing can break firmware communication. The surface is intentionally low-level and should remain wrapped by safer modules.

Test signals: compile-time layout compatibility is partial. Real validation requires GSP boot, command queue traffic, CPU sequencer execution, and static-info retrieval on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/r570_144/bindings.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/sequencer.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/sequencer.rs

Purpose: executes the pre-Hopper GSP CPU sequencer command stream received from firmware during boot. It converts raw sequencer buffer bytes into typed operations over BAR0 registers and Falcon cores.

Important APIs and types: `GspSequence` implements `MessageFromGsp` for `fw::MsgFunction::GspRunCpuSequencer`. `GspSeqCmd` represents register write/modify/poll/store, delay, core reset/start/wait/resume. `GspSeqIter` parses command bytes. `GspSequencer::run()` receives the firmware message and executes commands with `GspSequencerParams`.

Control flow: `run()` loops on `cmdq.receive_msg`, ignoring `ERANGE`, then builds a sequencer and iterates command data. Each parsed command dispatches to register access or Falcon control. `CoreResume` resets GSP, writes libOS DMA handle mailboxes, starts SEC2, waits for GSP reload completion, checks SEC2 errors, writes bootloader version, and verifies RISC-V active.

State and persistence: transient state includes command data, current parse offset, command count, libOS DMA handle, and bootloader version. Persistent hardware state is changed through BAR0 registers and Falcon core state.

Dependencies and integration: depends on `Cmdq`, firmware payload wrappers, `Bar0`, `Falcon<Gsp>`, `Falcon<Sec2>`, polling/delay APIs, and `SBufferIter` for command-buffer collection.

Risks: command parsing zero-pads tail bytes and stops silently on parse errors inside the iterator, so malformed firmware streams need careful logging. Hardware sequencing order is critical; timeout defaults, mailbox values, and active-core checks are boot blockers.

Test signals: no unit tests. Signals are GSP boot success, sequencer debug logs, register-poll timeout behavior, SEC2 mailbox error reporting, and hardware bring-up coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/sequencer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/nova_core.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/nova_core.rs

Purpose: top-level Rust module entry for the Nova Core GPU driver. It wires submodules, PCI registration, debugfs root lifetime, firmware module metadata, and kernel module metadata.

Important APIs and types: `NovaCoreModule` implements `InPlaceModule`; `DebugfsRootGuard` clears the global debugfs root on drop; `MODULE_NAME` exposes kernel module metadata. Submodules include driver, falcon, firmware, gfw, gpu, gsp, regs, sbuffer, and vbios.

Control flow: module initialization creates `debugfs::Dir("nova_core")`, stores it in the global `DEBUGFS_ROOT`, then registers `driver::NovaCore` as a PCI adapter. Drop order unregisters the driver before clearing debugfs state.

State and persistence: uses a mutable static `DEBUGFS_ROOT` as temporary per-module global state. Driver registration persists for module lifetime and is released automatically by field drop order.

Dependencies and integration: integrates with the Rust kernel module system, PCI adapter registration, debugfs, firmware metadata builder, and all Nova-Core submodules.

Risks: `DEBUGFS_ROOT` is a `static mut` guarded only by initialization/drop ordering assumptions. Future concurrent probe or per-module data support changes should revisit this. Firmware list is supplied through `kernel::module_firmware!(firmware::ModInfoBuilder)`.

Test signals: build/module-load tests, PCI probe/unprobe behavior, debugfs directory lifetime checks, and firmware metadata generation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/nova_core.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/num.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/num.rs

Purpose: numeric conversion helper module staging safe cast utilities for Nova-Core until equivalent kernel crate support is available.

Important APIs and types: `impl_safe_as!` generates const lossless widening conversion functions such as `u32_as_usize`. `FromSafeCast<T>` and `IntoSafeCast<T>` provide infallible architecture-checked conversions. `impl_const_into!` generates compile-time checked narrowing for constants. `bounded_enum!` creates enums backed by `kernel::num::Bounded` with `From` or `TryFrom` conversion behavior.

Control flow: all logic is compile-time or simple inline conversion. `bounded_enum!` uses match arms and `EINVAL` for unknown bounded values when a `TryFrom` mode is requested.

State and persistence: no runtime state. The module preserves numeric invariants at compile time and call sites.

Dependencies and integration: depends on `kernel::static_assert!`, `build_assert!`, `kernel::num::Bounded`, and `paste`. Used by register, firmware, and VBIOS code to avoid lossy `as` conversions.

Risks: conversion availability is architecture-config dependent. Missing implementations can surface only on 32-bit or 64-bit build variants. Macro-generated code must stay consistent with kernel-supported integer widths.

Test signals: doctest-like examples in comments, compile coverage for both CONFIG_32BIT and CONFIG_64BIT, and call-site type checking are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/num.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/regs.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/regs.rs

Purpose: typed register map for Nova-Core GPU, framebuffer, GSP/Falcon, GC6, display, fuse, and chip-specific register access.

Important APIs and types: register macros define `NV_PMC_BOOT_0`, `NV_PMC_BOOT_42`, PBUS scratch, PFB flush and WPR registers, `NV_PGSP_QUEUE_HEAD`, GC6 scratch registers, VGA workspace register, fuse arrays, many `NV_PFALCON_*` registers, PFALCON2/RISC-V registers, and chip-specific display fuse status modules. Helper methods derive chipset, usable framebuffer size, WPR bounds, VGA workspace address, memory-scrubbing state, DMA command memory target, engine reset, and GFW boot completion.

Control flow: mostly pure register field interpretation. `NV_PFALCON_FALCON_ENGINE::reset_engine()` writes reset true, sleeps 10 us, then writes reset false.

State and persistence: no owned state, but methods read and write persistent hardware registers via `Bar0`.

Dependencies and integration: depends on kernel `register!`, `Io`, `Bar0`, Falcon enums/base types, GPU architecture/chipset enums, and safe numeric casts. Used throughout Falcon boot, framebuffer setup, firmware boot, and hardware discovery.

Risks: register offsets and bitfields are hardware-contract sensitive. Some arrays are deliberately conservative because upstream documentation does not specify full sizes. Incorrect bit extraction can misidentify chipset, memory size, WPR bounds, or Falcon state.

Test signals: hardware boot on supported chipsets, register readback logging, chipset detection, WPR programming validation, and Falcon reset/start paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/regs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/sbuffer.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/sbuffer.rs

Purpose: stream-like abstraction over multiple discontiguous byte slices for reading from and writing into scatter buffers.

Important APIs and types: `SBufferIter<I>` stores a current non-empty slice plus remaining slices. `new_reader()` and `new_writer()` construct reader/writer views. Reader methods include `read_exact()`, `flush_into_kvec()`, and `Iterator<Item = u8>`. Writer method `write_all()` copies a source byte stream across mutable slices.

Control flow: construction skips empty slices. `get_slice_internal()` returns either a whole current slice or splits it, advancing to the next non-empty slice as needed. Reader/writer loops repeat until the requested data is consumed or return `EINVAL`/`ETOOSMALL`.

State and persistence: state is only iterator position and the current slice remainder. It mutates destination slices for writers and consumes reader position.

Dependencies and integration: depends on kernel allocation flags and `KVec`. Used by GSP command/message code, including sequencer message collection from split command buffers.

Risks: lifetime correctness depends on typed reader/writer constructors. `flush_into_kvec()` allocates and can fail. Iterator byte-by-byte reading is simple but may be inefficient for large buffers.

Test signals: documented examples cover split writes and byte summing. Integration signals include GSP command serialization/deserialization across multiple queue buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/sbuffer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/vbios.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/vbios.rs

Purpose: extracts and parses NVIDIA VBIOS ROM images from BAR0 to locate FwSec Falcon firmware descriptors, code/data, and signatures.

Important APIs and types: `Vbios::new()` scans ROM images and builds a `FwSecBiosImage`. `VbiosIterator` reads ROM data incrementally from `ROM_OFFSET`. `BiosImage`, `PcirStruct`, `NpdeStruct`, `PciRomHeader`, `BitHeader`, `BitToken`, `PciAtBiosImage`, `FwSecBiosBuilder`, `PmuLookupTable`, and `FwSecBiosImage` model the PCI ROM, BIT table, PMU lookup table, and FwSec firmware image. Public accessors are `fwsec_image()`, `FwSecBiosImage::header()`, `ucode()`, and `sigs()`.

Control flow: the iterator reads an initial 1 KiB header window, determines image size, reads the full image, advances on 512-byte alignment, and stops on last image or scan limit. `Vbios::new()` requires a PC-AT image plus first and second FwSec images. The builder resolves Falcon data through BIT token 0x70, compensates for image contiguity assumptions, finds the production FWSEC PMU entry, then exposes descriptor, ucode bytes, and RSA signatures.

State and persistence: `Vbios` owns copied VBIOS image data in `KVec`s and no longer reads BAR0 after construction. Parsed offsets persist inside `FwSecBiosImage`.

Dependencies and integration: depends on `Bar0`, firmware descriptor/signature types, alignment helpers, `FromBytes`, and safe casts. It feeds firmware-secure boot code.

Risks: parsing is bounds-sensitive and assumes little-endian table fields. Offset compensation across PC-AT, EFI, and FwSec images is fragile. `sigs()` uses raw pointer casting after bounds checks and depends on alignment/layout of signature structures.

Test signals: no direct tests. Firmware load success, descriptor debug logging, bounds-error logs, and hardware coverage across ROM layouts are the practical validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/vbios.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/tests/Makefile

Purpose: Kbuild fragment for GPU KUnit tests.

Important APIs and targets: builds `gpu_buddy_tests-y` from `gpu_buddy_test.o` and `gpu_random.o`, and includes the resulting object under `obj-$(CONFIG_GPU_BUDDY_KUNIT_TEST)`.

Control flow: no runtime flow; Kbuild conditionally compiles the test module when the config is enabled.

State and persistence: no state.

Dependencies and integration: depends on the `CONFIG_GPU_BUDDY_KUNIT_TEST` symbol and the local test/random helper sources. Integrates with kernel KUnit and the GPU buddy allocator test suite.

Risks: if new helper objects are added to the tests but not listed here, KUnit builds will miss them. The Makefile assumes the config symbol is defined elsewhere.

Test signals: successful KUnit build and discovery of the `gpu_buddy` suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_buddy_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_buddy_test.c

Purpose: KUnit validation suite for the generic GPU buddy allocator, covering allocation limits, range allocation, alignment, fragmentation, clear/dirty state, contiguous allocation, and pathological split/merge behavior.

Important APIs and functions: test cases include `gpu_test_buddy_alloc_limit`, `alloc_optimistic`, `alloc_pessimistic`, `alloc_pathological`, `alloc_contiguous`, `alloc_clear`, `alloc_range`, `alloc_range_bias`, `fragmentation_performance`, `alloc_exceeds_max_order`, `offset_aligned_allocation`, and `subtree_offset_alignment_stress`. The suite uses `gpu_buddy_init`, `gpu_buddy_alloc_blocks`, `gpu_buddy_free_list`, `gpu_buddy_free_block`, block offset/size/order helpers, and clear-state helpers.

Control flow: suite init chooses a nonzero random seed. Tests allocate synthetic address spaces, perform expected-success and expected-failure allocations, inspect returned block lists, free in controlled or randomized orders, and verify allocator metadata such as `avail`, `max_order`, root count, and `subtree_max_alignment`.

State and persistence: state is isolated per test in local `struct gpu_buddy` instances and temporary lists. Randomness is deterministic per suite run once the seed is printed.

Dependencies and integration: depends on KUnit, `linux/gpu_buddy.h`, kernel list helpers, prime/random utilities, sizes, and `gpu_random` helpers.

Risks: slow fragmentation tests can be expensive because they model multi-GiB spaces. Randomized tests improve coverage but failures need the printed seed for reproduction. Some tests inspect internal allocator fields, so allocator refactors may require test updates.

Test signals: the file itself is the primary signal for GPU buddy correctness and performance regressions. `KUNIT_CASE_SLOW` marks the long fragmentation/performance path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_buddy_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_random.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_random.c

Purpose: small randomization helper library for GPU tests.

Important APIs and functions: `gpu_prandom_u32_max_state()` scales `prandom_u32_state()` into `[0, ep_ro)` using high 32 bits of a 64-bit product. `gpu_random_reorder()` shuffles an order array. `gpu_random_order()` allocates and initializes an index array before shuffling it. All three are exported symbols.

Control flow: `gpu_random_order()` allocates with `kmalloc_array`, fills `0..count-1`, calls `gpu_random_reorder()`, and returns the array. `gpu_random_reorder()` performs repeated swaps using a random index.

State and persistence: no global state. Callers own the `rnd_state` and allocated order array.

Dependencies and integration: depends on kernel random, slab, bitops, and swap helpers. Used by `gpu_buddy_test.c` randomized range-bias tests.

Risks: the shuffle is not Fisher-Yates because each iteration chooses from the whole range; that is acceptable for stress ordering but not uniform permutation generation. `count == 0` behavior depends on allocator and loop behavior at callers.

Test signals: indirect through GPU KUnit randomized tests and reproducibility via seeded `rnd_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_random.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_random.h

Purpose: declarations and convenience macros for GPU test pseudo-random helpers.

Important APIs and macros: `GPU_RND_STATE_INITIALIZER(seed__)` creates and seeds a `struct rnd_state`; `GPU_RND_STATE(name__, seed__)` declares a seeded state variable. Function declarations cover `gpu_random_order`, `gpu_random_reorder`, and `gpu_prandom_u32_max_state`.

Control flow: macro expansion seeds local PRNG state before test code calls helper functions.

State and persistence: state is caller-owned `struct rnd_state`; there is no global state.

Dependencies and integration: includes `linux/prandom.h` and pairs with `gpu_random.c`. Used by GPU KUnit tests requiring reproducible randomized orders.

Risks: macros create block-expression values and are kernel/GNU C specific. Callers must preserve and log seeds when debugging randomized failures.

Test signals: indirect through KUnit tests that use `GPU_RND_STATE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/trace/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/trace/Kconfig

Purpose: configuration switch for GPU memory usage tracepoints.

Important symbols: `TRACE_GPU_MEM` is a boolean option titled "Enable GPU memory usage tracepoints", defaulting to `n`.

Control flow: no runtime logic; the symbol controls whether the tracepoint provider object is built.

State and persistence: no state.

Dependencies and integration: intended for global and per-process GPU memory profiling and Android requirements. Its availability depends on GPU drivers emitting the trace events.

Risks: enabling the option exposes tracepoints but does not guarantee every driver reports useful data. The option is off by default, so tracing consumers must ensure kernel config support.

Test signals: build inclusion of `trace_gpu_mem.o` and runtime availability of `gpu_mem_total` tracepoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/trace/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/trace/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/trace/Makefile

Purpose: Kbuild fragment for GPU memory tracepoint provider.

Important targets: `obj-$(CONFIG_TRACE_GPU_MEM) += trace_gpu_mem.o`.

Control flow: no runtime flow; conditional compilation only.

State and persistence: no state.

Dependencies and integration: tied to the `TRACE_GPU_MEM` Kconfig symbol and `trace_gpu_mem.c`.

Risks: if tracepoint implementation grows into multiple objects, this Makefile must be updated.

Test signals: successful object build when `CONFIG_TRACE_GPU_MEM=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/trace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/trace/trace_gpu_mem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/trace/trace_gpu_mem.c

Purpose: instantiates GPU memory tracepoints.

Important APIs: defines `CREATE_TRACE_POINTS` before including `<trace/events/gpu_mem.h>`, then exports `gpu_mem_total` with `EXPORT_TRACEPOINT_SYMBOL`.

Control flow: no active runtime logic. The tracepoint infrastructure emits events when producers call the generated trace hooks.

State and persistence: no file-local state; tracepoint registration is handled by kernel trace infrastructure.

Dependencies and integration: depends on `linux/module.h` and trace event definitions in `trace/events/gpu_mem.h`. GPU drivers and tracing tools integrate through the exported tracepoint.

Risks: this file only creates the tracepoint symbols; event schema changes happen in the trace header. Consumers depend on stable trace event fields.

Test signals: tracepoint visible in tracing filesystem and successful driver emission of `gpu_mem_total`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/trace/trace_gpu_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/vga/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/vga/Kconfig

Purpose: configuration entry for laptop hybrid graphics switching support.

Important symbols: `VGA_SWITCHEROO` is a boolean option depending on X86, ACPI, PCI, and framebuffer console compatibility; it selects `VGA_ARB`.

Control flow: no runtime logic. The symbol controls compilation of the switcheroo subsystem.

State and persistence: no state.

Dependencies and integration: targets muxed and muxless hybrid graphics laptops, including ATI PowerXpress and NVIDIA HybridPower style systems. Integrates with VGA arbitration and framebuffer console constraints.

Risks: platform dependencies are strict; enabling on unsupported architectures is blocked. Runtime usefulness still depends on GPU drivers and mux/power handlers registering.

Test signals: build inclusion of `vga_switcheroo.o` and debugfs switch interface on systems with two GPU clients plus a handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/vga/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/vga/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/vga/Makefile

Purpose: Kbuild fragment for VGA switcheroo.

Important targets: `obj-$(CONFIG_VGA_SWITCHEROO) += vga_switcheroo.o`.

Control flow: no runtime flow; conditional build only.

State and persistence: no state.

Dependencies and integration: tied to `CONFIG_VGA_SWITCHEROO` and `vga_switcheroo.c`.

Risks: minimal; new source splits require updating the object list.

Test signals: object built when the config is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/vga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/vga/vga_switcheroo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/vga/vga_switcheroo.c

Purpose: Linux hybrid graphics coordination subsystem for laptops with muxed or muxless dual GPUs. It coordinates GPU clients, audio clients, mux/power handlers, debugfs user commands, DDC switching, delayed switches, and runtime PM power switching.

Important APIs and functions: exported APIs include handler registration/unregistration, client/audio-client registration, probe-defer checks, client state lookup, framebuffer association, DDC lock/unlock, delayed-switch processing, and runtime-PM domain helpers. Internal state lives in `struct vgasr_priv`; clients are `struct vga_switcheroo_client`.

Control flow: switcheroo becomes active once two VGA clients and a handler are registered. Debugfs `switch` parses `OFF`, `ON`, `IGD`, `DIS`, delayed variants, and mux-only variants. Full switching runs stage 1 to power on the target and set default VGA device, then stage 2 to mark active state, remap fbcon, call handler `switchto`, reprobe, power off old client, and update audio state. Delayed switches store target state until clients report switchability.

State and persistence: singleton global `vgasr_priv` tracks active status, clients, handler callbacks, handler flags, debugfs root, delayed target, and DDC owner. State is protected by `vgasr_mutex` and `mux_hw_lock`.

Dependencies and integration: integrates with PCI, ACPI/apple-gmux, fbcon, debugfs, VGA arb, runtime PM, HDA audio clients, and DRM/fb GPU drivers through `vga_switcheroo_client_ops` and handler callbacks.

Risks: global singleton design limits multi-instance systems. Lock ordering around global mutex and mux lock is critical. Debugfs commands are low-level and can blank displays on mux-only switching. Runtime PM mode makes manual ON/OFF no-ops for driver-managed clients.

Test signals: practical signals are debugfs state output, successful GPU switch with fbcon remap, delayed switch completion after clients close, DDC EDID probing for inactive GPU, runtime suspend/resume power handler calls, and absence of client refusal logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/vga/vga_switcheroo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/greybus/Kconfig

Purpose: configuration menu for Greybus core and host-controller drivers.

Important symbols: `GREYBUS` is a tristate depending on SYSFS. `GREYBUS_BEAGLEPLAY` depends on SERIAL_DEV_BUS and selects CRC_CCITT, FW_LOADER, and FW_UPLOAD. `GREYBUS_ES2` depends on USB.

Control flow: no runtime flow; symbols control module compilation.

State and persistence: no state.

Dependencies and integration: enables the Greybus core module, BeaglePlay CC1352 SVC transport, and Toshiba ES3 USB host controller bridge.

Risks: transport-specific symbols pull in firmware and serial/USB dependencies. Users may enable Greybus core without a host controller, yielding no functional bus.

Test signals: expected modules build as `greybus.ko`, `gb-beagleplay.ko`, and `gb-es2.ko` depending on configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/greybus/Makefile

Purpose: Kbuild manifest for Greybus core and host-controller modules.

Important targets: `greybus-y` aggregates core, debugfs, host device, manifest, module, interface, bundle, connection, control, SVC, watchdog, and operation objects. `obj-$(CONFIG_GREYBUS)` builds `greybus.o`; `obj-$(CONFIG_GREYBUS_BEAGLEPLAY)` builds `gb-beagleplay.o`; `gb-es2-y := es2.o` and `obj-$(CONFIG_GREYBUS_ES2)` builds the ES2 module. `ccflags-y += -I$(src)` supports local trace event includes.

Control flow: no runtime flow; build composition only.

State and persistence: no state.

Dependencies and integration: maps Greybus Kconfig symbols to core and transport objects.

Risks: object ordering matters for built-in initialization dependencies. New Greybus core files must be added to `greybus-y` or they will not link.

Test signals: successful module builds and trace include resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/arpc.h -->
# sources/distributed-fs/ceph-client/drivers/greybus/arpc.h

Purpose: wire-format definitions for APBridgeA RPC messages used by Greybus-related host transport code.

Important APIs and types: `enum arpc_result` defines success, memory, invalid, timeout, and unknown-error result codes. `arpc_request_message` and `arpc_response_message` define packed RPC headers. Request type constants cover CPort connected, quiesce, clear, flush, and shutdown. Packed request payload structs carry CPort IDs, peer space, timeout, and shutdown phase.

Control flow: no executable flow; consumers serialize and parse these packed layouts.

State and persistence: no owned state. Fields are on-wire little-endian where declared with `__le16`.

Dependencies and integration: included by APBridge/transport code that maps Greybus CPort lifecycle operations to ARPC commands.

Risks: packed wire formats require careful alignment and endian conversion. Header `size` includes header plus payload, so callers must compute it consistently.

Test signals: transport-level CPort lifecycle tests and interoperability with APBridgeA firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/arpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/bundle.c -->
# sources/distributed-fs/ceph-client/drivers/greybus/bundle.c

Purpose: Greybus bundle device management. A bundle groups interface CPorts and exposes device-model state for Greybus protocol drivers.

Important APIs and functions: sysfs attributes expose `bundle_class`, `bundle_id`, and writable `state`. `gb_bundle_create()`, `gb_bundle_add()`, and `gb_bundle_destroy()` manage lifecycle. Runtime PM helpers suspend/resume bundles, disable/enable all connections when protocol PM callbacks are absent, and notify the interface control protocol.

Control flow: creation validates bundle ID uniqueness, initializes device fields and connection list, links into the interface bundle list, and traces creation. Add registers the device. Destroy deletes the device if registered, removes it from the interface list, and drops the device reference. Runtime suspend calls driver PM if available or disables all connections, then sends control bundle suspend; on failure it resumes/enables connections.

State and persistence: each `gb_bundle` owns class/id/version fields, `state` string, CPort descriptors, device object, and connection list. Sysfs `state_store` replaces the stored state string and notifies userspace.

Dependencies and integration: depends on Greybus bus/device types, control protocol, connection APIs, runtime PM, sysfs, and tracepoints.

Risks: sysfs state is free-form and allocated from user input. Runtime PM rollback must match whichever path suspended the bundle. Bundle IDs are assumed serialized during interface initialization.

Test signals: device registration under Greybus bus, sysfs attribute behavior, runtime suspend/resume of bundles, connection disable/enable traces, and control PM operation results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/bundle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/connection.c -->
# sources/distributed-fs/ceph-client/drivers/greybus/connection.c

Purpose: core Greybus connection lifecycle and state machine. A connection represents a bidirectional link between a host CPort and a remote interface CPort and owns active operation state.

Important APIs and functions: creation APIs cover static, control, normal, flagged, and offloaded connections. Runtime APIs include `gb_connection_enable`, `enable_tx`, `disable_rx`, `disable`, `disable_forced`, `destroy`, latency-tag enable/disable, and mode-switch prepare/complete. `greybus_data_rcvd()` dispatches host-driver received data to the matching connection.

Control flow: creation serializes against destroy, checks remote CPort reuse, allocates a host CPort, initializes locks/workqueue/kref, and links the connection into host and bundle lists. Enable performs host CPort enable, SVC route creation, host connected notification, state transition to TX or full RX/TX, then control connected notification. Disable transitions to disconnecting, cancels operations, flushes host CPort, sends control disconnecting, performs two-phase CPort shutdown with quiesce between phases, sends disconnected/mode-switch handling, destroys SVC route, clears and disables the host CPort.

State and persistence: connection state includes IDs, flags, mode-switch flag, operation cycle, operation list, ordered workqueue, kref, and state enum. Global host connection lookup is protected by `gb_connections_lock`; lifecycle serialization uses `gb_connection_mutex` and per-connection mutex/spinlock.

Dependencies and integration: depends on host-device CPort driver callbacks, SVC connection management, Greybus control operations, operation core, bundles, interfaces, workqueues, and tracepoints.

Risks: state transitions and lock ordering are complex. Forced disable skips remote communication for disconnected interfaces. Error unwind in enable must mirror teardown. Offloaded connections depend on host driver shutdown support.

Test signals: Greybus device enumeration, connect/disconnect traces, operation cancellation behavior, CPort shutdown/quiesce logs, mode-switch paths, and host-driver callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/control.c -->
# sources/distributed-fs/ceph-client/drivers/greybus/control.c

Purpose: Greybus interface control-protocol implementation. It owns the control connection and provides synchronous operations for version negotiation, manifest retrieval, CPort lifecycle notifications, bundle/interface PM, and mode switching.

Important APIs and functions: `gb_control_create`, `enable`, `disable`, `suspend`, `resume`, `add`, `del`, `get`, `put`, and mode-switch helpers manage the control device. Operation helpers include version and bundle-version queries, manifest size/data reads, connected/disconnected/disconnecting notifications, mode switch, bundle suspend/resume/deactivate/activate, interface suspend/deactivate prepare, and hibernate abort.

Control flow: enable brings the control connection up in TX mode, negotiates protocol version, sets feature flags for bundle version and activation, and disables the connection on failure. Operation helpers mostly call `gb_operation_sync`; disconnecting and mode-switch use explicit core operations. Disable chooses normal or forced connection teardown depending on interface disconnected state.

State and persistence: `struct gb_control` stores protocol version, feature flags, vendor/product strings, device object, interface pointer, and control connection. Sysfs exposes vendor and product strings. Device release destroys the connection and frees strings/control.

Dependencies and integration: depends on Greybus operation core, connection core, interface and bundle structures, sysfs device model, and Greybus protocol request/response definitions.

Risks: protocol feature detection is partly version-based and partly quirk-based. PM status codes must be mapped correctly to Linux errno. Control connection failure blocks manifest parsing and bundle setup.

Test signals: successful version negotiation, manifest retrieval, bundle version population, PM operation status handling, and connection teardown behavior during disconnects and mode switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/greybus/control.c -->
