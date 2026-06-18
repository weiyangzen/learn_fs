# subset-b-004262 Research Report

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/link.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/link.c

Purpose: implements the low-level OpenCAPI link abstraction shared by PCI functions in the same device slot. It allocates a Shared Process Area (SPA), wires platform-specific OpenCAPI/NPU setup through `pnv_ocxl_*`, handles translation-fault interrupts, manages process elements keyed by PASID, and exports link IRQ allocation helpers.

Important APIs, types, and functions: internal types `struct ocxl_link`, `struct spa`, and `struct pe_data` track slot identity, SPA memory, radix-tree PE lookup, fault work, ATSD/TLBI state, and per-PE `mm_struct` ownership. Exported APIs are `ocxl_link_setup()`, `ocxl_link_release()`, `ocxl_link_add_pe()`, `ocxl_link_remove_pe()`, `ocxl_link_irq_alloc()`, and `ocxl_link_free_irq()`, with `ocxl_link_update_pe()` declared internally. Fault helpers include `xsl_fault_handler()`, `xsl_fault_handler_bh()`, `read_irq()`, and `ack_irq()`.

Control flow: `ocxl_link_setup()` reuses an existing slot link from `links_list` or calls `alloc_link()`, which allocates SPA pages, maps XSL fault registers, requests the platform XSL IRQ, calls `pnv_ocxl_spa_setup()`, and optionally maps an LPAR ATSD register. `ocxl_link_add_pe()` fills the big-endian `struct ocxl_process_element`, registers copro/mmu-notifier state for user contexts, inserts `pe_data` in the radix tree, and pins the `mm` with `mmgrab()`. Translation faults are acknowledged in two phases: hard IRQ reads DSISR/DAR/PE, finds PE metadata under RCU, takes an `mm_users` reference with `mmget_not_zero()`, and schedules work; the work item calls `copro_handle_mm_fault()`, manually hashes pages on non-radix systems, invokes the AFU error callback on failure, and writes the TFC response. Removal clears the SPA entry, flushes platform context cache, unregisters mmu notifier, drops copro/mm refs, and frees `pe_data` via RCU.

State and persistence: SPA memory is page-allocated and zeroed per link; global `links_list` and krefs persist shared links until the last PCI function releases them. The radix tree maps live PASIDs to `pe_data`. IRQ quota is `atomic_t irq_available`. There is no disk persistence; state is hardware/MMIO/kernel-memory resident.

Dependencies and integration points: depends on powerpc/OpenCAPI platform hooks (`asm/pnv-ocxl.h`, `asm/copro.h`, XIVE, mmu notifier, radix/hash MMU behavior), `trace.h` events, and exported `misc/ocxl.h` symbols. It integrates upward with OCXL function/AFU setup code and context attach/detach paths.

Risks and test signals: high-risk areas are memory-management races with exiting processes, AFUs still issuing requests after PE removal, PASID bounds, mmu-notifier ordering, and interrupt acknowledgement correctness. Useful tests include AFU attach/detach under process exit, forced XSL translation faults for user and kernel contexts, radix and hash MMU coverage, IRQ exhaustion/release checks, and tracing `ocxl_fault`, `ocxl_fault_ack`, context add/remove, and mmu-notifier events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/main.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/main.c

Purpose: module entry/exit for the generic OpenCAPI driver. It validates that the platform can perform TLB invalidation, initializes the OCXL file layer, and registers the PCI driver.

Important APIs and functions: `init_ocxl()` is the module initializer, `exit_ocxl()` is the exit path, and the file uses the external `ocxl_pci_driver` plus `ocxl_file_init()`/`ocxl_file_exit()` from the OCXL subsystem.

Control flow: initialization fails early with `-EINVAL` if `tlbie_capable` is false. It then initializes file infrastructure and registers the PCI driver; on PCI registration failure it unwinds the file layer. Exit unregisters PCI first, then tears down file state, matching the order that prevents new probes while user-facing device nodes are being removed.

State and persistence: no direct state beyond registered kernel module resources. Runtime state lives in the PCI, file, and link layers.

Dependencies and integration points: depends on `linux/module.h`, `linux/pci.h`, powerpc `asm/mmu.h`, and `ocxl_internal.h`. It is the top-level integration point that makes `pci.c` active.

Risks and test signals: test with unsupported platforms to confirm `tlbie_capable` rejection, simulated `ocxl_file_init()` and `pci_register_driver()` failures for unwind coverage, and module load/unload cycles with no stale device nodes or registered PCI driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/mmio.c

Purpose: provides exported helper APIs for 32-bit and 64-bit global AFU MMIO reads, writes, set-bit, and clear-bit operations with caller-selected endian handling.

Important APIs and functions: exported symbols are `ocxl_global_mmio_read32()`, `ocxl_global_mmio_read64()`, `ocxl_global_mmio_write32()`, `ocxl_global_mmio_write64()`, `ocxl_global_mmio_set32()`, `ocxl_global_mmio_set64()`, `ocxl_global_mmio_clear32()`, and `ocxl_global_mmio_clear64()`. They operate on `struct ocxl_afu`, using `afu->global_mmio_ptr` and `afu->config.global_mmio_size`.

Control flow: each function checks that the requested offset leaves enough room for the access width, normalizes `OCXL_HOST_ENDIAN` to big-endian on big-endian builds, then selects `readl/readq/writel/writeq` or their `_be` variants. Set/clear helpers perform read-modify-write cycles.

State and persistence: no persistent state is held by this file. All state changes are direct MMIO writes to AFU global registers.

Dependencies and integration points: depends on OCXL AFU config and `enum ocxl_endian` from public/internal headers. These helpers are exported for other kernel OCXL clients.

Risks and test signals: offset checks can underflow if `global_mmio_size` is smaller than access width, so boundary tests should include zero and sub-width sizes. Read-modify-write helpers are not serialized here; callers must handle concurrent register updates. `ocxl_global_mmio_clear64()` performs a second unconditional `writeq(tmp, ...)` after the endian switch, which can duplicate the write and force little-endian/non-BE access even after a big-endian clear path; regression tests should cover BE behavior. MMIO fault-injection tests should verify no out-of-range access occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/ocxl_internal.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/ocxl_internal.h

Purpose: central internal header for the OCXL driver, defining shared function, AFU, file, context, fault, and process-element data structures plus cross-file prototypes.

Important APIs and types: `struct ocxl_fn` tracks PCI function device state, BAR use, function config, AFU list, PASID/ACTAG ranges, and link handle. `struct ocxl_afu` carries AFU config, context accounting, IDR/mutex state, MMIO addresses, IRQ offsets, and private data. `struct ocxl_file_info` binds a cdev/device/bin attribute to an AFU. `struct ocxl_context` contains PASID state, mapping, wait queue, XSL error tracking, IRQ IDR, and TID. `struct ocxl_process_element` defines the 128-byte SPA hardware layout.

Control flow and integration: prototypes connect file registration, PASID/ACTAG allocation, config discovery/update, link PE update, context mmap/detach, sysfs registration, and AFU IRQ helpers. `ocxl_pci_driver` is exported to module init. The header coordinates implementations across `pci.c`, `link.c`, `mmio.c`, `sysfs.c`, context/file/config code, and AFU IRQ support.

State and persistence: all structures are kernel-resident live driver state. The header encodes locking ownership with named mutexes/IDRs but does not implement locking itself.

Dependencies: includes Linux PCI, cdev, list, and public `<misc/ocxl.h>`. It is private to the driver and should change in lockstep with all OCXL source files.

Risks and test signals: ABI-sensitive risks include `struct ocxl_process_element` layout, PASID/context counters, IDR lifetime, and mismatched prototypes. Compile-time checks in `link.c` validate process-element size; tests should exercise AFU registration/unregistration, context lifecycle, sysfs attributes, IRQ allocation/free, and public export consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/ocxl_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/pasid.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/pasid.c

Purpose: implements simple ordered range allocation/free for per-function PASID and ACTAG subranges assigned to AFUs.

Important APIs and types: internal `struct id_range` records `[start,end]` allocations in a list. `range_alloc()` and `range_free()` implement common allocation logic. Public-internal APIs are `ocxl_pasid_afu_alloc()`, `ocxl_pasid_afu_free()`, `ocxl_actag_afu_alloc()`, and `ocxl_actag_afu_free()`.

Control flow: allocation scans the sorted list looking for the first gap larger than the requested size, inserts a new range after the prior entry, and returns the start ID or `-ENOSPC`. PASID maximum is derived from `fn->config.max_pasid_log`; ACTAG maximum is `fn->actag_enabled`. Free scans for an exact start/size match and warns if none is found.

State and persistence: state is maintained in `fn->pasid_list` and `fn->actag_list`, both in kernel memory and tied to the OCXL function lifetime.

Dependencies and integration points: depends on `struct ocxl_fn` from `ocxl_internal.h`. Callers must serialize access if these lists can be touched concurrently; this file itself contains no lock.

Risks and test signals: check for off-by-one behavior: `max_pasid = 1 << max_pasid_log` is passed as max ID, so callers should confirm whether the maximum is intended inclusive. Allocation uses `cur->start - last_end > size`, which is gap-size sensitive. Tests should allocate/free adjacent ranges, maximal ranges, impossible ranges, and invalid frees under debug/WARN observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/pasid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/pci.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/pci.c

Purpose: PCI driver binding for generic OpenCAPI devices using IBM device ID `0x062B`; opens the OCXL function and registers discovered AFUs with the file layer.

Important APIs and functions: `ocxl_probe()` opens the function with `ocxl_function_open()`, stores it in PCI drvdata, gets the AFU list with `ocxl_function_afu_list()`, and calls `ocxl_file_register_afu()` for each AFU. `ocxl_remove()` unregisters each AFU and closes the function. `ocxl_pci_driver` defines probe/remove/shutdown hooks and the PCI ID table.

Control flow: probe tolerates individual AFU registration failures by logging and continuing, relying on `ocxl_file_register_afu()` cleanup. Remove iterates AFUs and unregisters file devices before closing the function. Shutdown reuses remove behavior.

State and persistence: the PCI device stores `struct ocxl_fn *` in drvdata. AFU/file/link state is allocated by lower layers and released on remove.

Dependencies and integration points: integrates generic PCI matching, OCXL function discovery/config parsing, and character/sysfs registration. It is registered by `main.c`.

Risks and test signals: partial AFU registration can leave a function open with only some AFUs exposed; tests should cover sparse AFU lists and failures in file registration. Hot-unplug/shutdown tests should ensure unregister order prevents use-after-free and no AFU device node remains after `ocxl_function_close()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/sysfs.c

Purpose: creates per-AFU sysfs attributes and a binary global-MMIO file, including mmap support for the AFU global MMIO area.

Important APIs and functions: attribute show/store functions cover `global_mmio_size`, `pp_mmio_size`, `afu_version`, `contexts`, and `reload_on_reset`. `global_mmio_read()`, `global_mmio_fault()`, and `global_mmio_mmap()` implement the `global_mmio_area` bin attribute. Exported internal APIs are `ocxl_sysfs_register_afu()` and `ocxl_sysfs_unregister_afu()`.

Control flow: registration creates scalar device files, initializes `attr_global_mmio`, and creates the bin file. The mmap path validates requested pages, marks the VMA `VM_IO | VM_PFNMAP`, uses noncached protection, and inserts PFNs from `global_mmio_start` in the fault handler. Unregister removes all scalar files and the bin file.

State and persistence: sysfs files reflect live `struct ocxl_afu` state. Writes to `reload_on_reset` call OCXL config space setters, altering device behavior rather than stored driver state.

Dependencies and integration points: uses the file-layer `struct ocxl_file_info`, PCI config helpers, sysfs/bin_attribute APIs, and VM PFN insertion. The global MMIO pointer and physical start are supplied by AFU discovery.

Risks and test signals: `global_mmio_read()` does not clamp `count` to remaining size after validating `off`, so a large read near the end can overrun the mapped MMIO range. Mmap boundary checks should cover offsets, zero-size MMIO, and SIGBUS beyond range. `reload_on_reset` should be tested on hardware with and without the capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/trace.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/trace.c

Purpose: instantiates the OCXL tracepoints declared in `trace.h`.

Important APIs and functions: defines `CREATE_TRACE_POINTS` and includes `trace.h`; no runtime functions are declared here.

Control flow: compile-time tracepoint generation occurs through the Linux tracepoint infrastructure. Runtime behavior is driven by tracepoint call sites in other OCXL files.

State and persistence: no direct state. Generated tracepoint descriptors integrate with ftrace/perf infrastructure.

Dependencies and integration points: must be built exactly once in the OCXL module to materialize trace events. Depends on `trace.h` and `<trace/define_trace.h>` included from that header.

Risks and test signals: duplicate or missing inclusion can cause link errors or missing events. Build tests with tracepoints enabled and runtime tests under `/sys/kernel/tracing/events/ocxl/` should confirm all events appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/trace.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/trace.h

Purpose: declares OCXL trace events for MMU notifier activity, context lifecycle, PASID termination, XSL fault handling/acknowledgement, and AFU IRQ allocation/free/receive.

Important APIs and types: `TRACE_EVENT()` and `DECLARE_EVENT_CLASS()` definitions include `ocxl_mmu_notifier_range`, `ocxl_init_mmu_notifier`, `ocxl_release_mmu_notifier`, `ocxl_context_add`, `ocxl_context_remove`, `ocxl_terminate_pasid`, `ocxl_fault`, `ocxl_fault_ack`, `ocxl_afu_irq_alloc`, `ocxl_afu_irq_free`, and `ocxl_afu_irq_receive`.

Control flow: call sites pass PASID, PIDR/TIDR, SPA pointer, PE, DSISR/DAR/TFC, virtual/hardware IRQ data, and address ranges. The trace definitions format these fields for kernel tracing.

State and persistence: trace events are transient diagnostic data emitted into tracing buffers when enabled.

Dependencies and integration points: includes `<linux/tracepoint.h>` and uses the standard `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` pattern. It is consumed by `trace.c`, `link.c`, and IRQ/context code.

Risks and test signals: field-size mismatches can produce misleading diagnostics, especially pointer, PIDR, and 64-bit register formatting. Tests should enable each event, trigger the corresponding operation, and verify the expected payload names and values are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/open-dice.c -->
# sources/distributed-fs/ceph-client/drivers/misc/open-dice.c

Purpose: exposes a reserved-memory region containing Open Profile for DICE measured-boot data through `/dev/open-diceN`, allowing userspace to read the region size, mmap the contents read-only/shared-safe, and request a wipe.

Important APIs and types: `struct open_dice_drvdata` stores a mutex, reserved-memory pointer, miscdevice, and generated device name. File operations are `open_dice_read()`, `open_dice_write()`, and `open_dice_mmap_prepare()`. Platform lifecycle is `open_dice_probe()`, `open_dice_remove()`, `open_dice_init()`, and `open_dice_exit()`.

Control flow: probe looks up the device-tree reserved memory, validates nonzero `ULONG_MAX`-bounded page-aligned base/size, allocates driver data, and registers a 0600 misc device. Read returns the region size as an `unsigned long`. Write ignores the user buffer and wipes the reserved memory by `devm_memremap()` with write-combine attributes, `memset()` to zero, and `devm_memunmap()`. Mmap forbids writable shared mappings, clears future write permission, sets write-combine and dump/copy avoidance flags, and maps the reserved physical range.

State and persistence: only the reserved memory content persists outside driver structures. A wipe mutates that memory to zero. Device index is static and monotonically increments during probes.

Dependencies and integration points: depends on device-tree `google,open-dice`, reserved-memory bindings, miscdevice, new VMA descriptor mmap helpers, and userspace consumers of the DICE handoff.

Risks and test signals: the region contains sensitive boot material, so permissions, no-dump/no-copy VMA flags, and wipe behavior are critical. Tests should cover absent reserved memory, unaligned regions, read offsets, mmap permission transitions, concurrent wipe/mmap/read, and optional absence where init treats `-ENODEV` as success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/open-dice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pch_phub.c -->
# sources/distributed-fs/ceph-client/drivers/misc/pch_phub.c

Purpose: PCI driver for Intel EG20T and ROHM/LAPIS PHUB devices, exposing option-ROM firmware and MAC address sysfs access while applying device-specific prefetch, clock, and interrupt-delay configuration.

Important APIs and types: `struct pch_phub_reg` stores saved registers, MMIO mappings, ROM/MAC offsets, device type, and PCI pointer. Serial ROM helpers include `pch_phub_read_serial_rom()`, `pch_phub_write_serial_rom()`, `pch_phub_read/write_serial_rom_val()`, header setup helpers, and MAC helpers. User-facing paths are binary attribute `pch_firmware` via `pch_phub_bin_read/write()` and `pch_mac` via `show_pch_mac()`/`store_pch_mac()`.

Control flow: probe enables PCI, requests regions, maps BAR1, then branches on `id->driver_data` to create sysfs files, configure prefetch/clock registers, set ROM/MAC offsets, and apply board/OF quirks. ROM reads map the PCI ROM, validate signature `0xAA55`, compute option-ROM size, then copy bytes from serial ROM. Writes map the ROM and program bytes by enabling ROM writes, read-modify-writing aligned words, polling `PHUB_STATUS`, and disabling writes. Remove unregisters sysfs files, unmaps BAR, releases regions, disables PCI, and frees state.

State and persistence: writable serial ROM/MAC/option-ROM content persists in device firmware. Saved register fields are used by suspend/resume helpers to capture and restore PHUB registers when enabled.

Dependencies and integration points: depends on PCI, sysfs bin attributes, DMI board quirks, OF properties such as `intel,eg20t-prefetch`, Ethernet address parsing, and device IDs for Intel/ROHM variants.

Risks and test signals: sysfs writes can permanently modify option ROM and MAC data; bounds and authorization matter. `pch_phub_bin_read()` compares `orom_size < count` rather than remaining `off + count`, so boundary reads deserve review. Remove unconditionally removes both sysfs files even if a given variant did not create both. Tests should cover each device type branch, ROM absent/signature mismatch, timeout in write polling, invalid MAC strings, CM-iTC/Boston quirks, suspend/resume register restoration, and hot-unplug cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pch_phub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pci_endpoint_test.c -->
# sources/distributed-fs/ceph-client/drivers/misc/pci_endpoint_test.c

Purpose: host-side PCI endpoint test driver exposing `/dev/pci-endpoint-test.N` ioctls for validating endpoint BAR mappings, interrupt delivery, DMA/read/write/copy paths, dynamic inbound doorbells, and BAR subrange mapping.

Important APIs and types: `struct pci_endpoint_test` tracks PCI device, test register BAR, mapped BARs, IRQ completion, IRQ type/count, capabilities, alignment, and miscdevice. `struct pci_endpoint_test_data` carries per-device test BAR/alignment quirks. Major helpers include IRQ vector management, BAR tests, subrange setup/clear, `pci_endpoint_test_intx_irq()`, `pci_endpoint_test_msi_irq()`, `pci_endpoint_test_read/write/copy()`, `pci_endpoint_test_set_irq()`, `pci_endpoint_test_doorbell()`, `pci_endpoint_test_ioctl()`, probe/remove, and ID table entries.

Control flow: probe rejects bridges, allocates state, applies device-specific data, enables PCI, requests regions, maps memory BARs, selects the test register BAR, allocates a misc device name/IDA, reads endpoint capabilities, and registers the misc device. Ioctls are serialized by `test->mutex`; they reinitialize the IRQ completion, validate arguments, program endpoint test registers, wait for IRQ completion, then inspect status/CRC/IRQ number. DMA tests allocate aligned bounce buffers, map with streaming DMA APIs, write source/destination addresses to endpoint registers, and validate CRC32 or status bits. IRQ type selection frees old vectors and requests INTx/MSI/MSI-X vectors as requested or inferred from endpoint capabilities.

State and persistence: state is per PCI device and per open ioctl operation. Endpoint status/capability/test registers are MMIO state. No disk persistence exists.

Dependencies and integration points: depends on UAPI `<uapi/linux/pcitest.h>`, PCI endpoint test register protocol, miscdevice, DMA mapping, IRQ vector APIs, CRC32, and many vendor/device IDs. The endpoint function under test must implement the expected register protocol.

Risks and test signals: several operations wait indefinitely with `wait_for_completion()` rather than timeout, so malfunctioning endpoints can hang ioctl callers. Doorbell reads an endpoint-supplied BAR/offset and writes to `test->bar[bar] + addr`; capability validation and BAR bounds are critical. BAR tests intentionally write across endpoint BARs and must skip reserved/test BARs correctly. Tests should cover all ioctls, invalid BAR/IRQ arguments, vector allocation failure, DMA mapping failure, endpoint status failures, subrange cleanup after failure, SR-IOV devices, and hot-remove during userspace access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pci_endpoint_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/phantom.c -->
# sources/distributed-fs/ceph-client/drivers/misc/phantom.c

Purpose: PCI character driver for Sensable Phantom haptic devices behind a PLX 9050 bridge, exposing ioctl-driven register access, polling for device interrupts, and a class version attribute.

Important APIs and types: `struct phantom_device` stores mapped control/input/output BAR addresses, status flags, interrupt counter, waitqueue, cdev, open lock, register spinlock, and NOT_OH mode shadow registers. File operations are `phantom_open()`, `phantom_release()`, `phantom_ioctl()`, compat ioctl, and `phantom_poll()`. PCI lifecycle is `phantom_probe()`, `phantom_remove()`, suspend/resume, module init/exit.

Control flow: module init registers class, version file, char-device range, and PCI driver. Probe enables PCI, reserves a minor, requests regions, maps BAR0/BAR2/BAR3, disables IRQs, requests shared IRQ, adds a cdev, and creates `/dev/phantomN`. Ioctls read/write individual or multiple registers, enforce register index <= 7, start/stop IRQ mode via `phantom_status()`, preserve amplifier state in NOT_OH mode, and copy data to/from userspace. ISR checks control IRQ enable, acknowledges device registers, optionally replays shadow output regs/toggles amp in NOT_OH mode, increments a counter, and wakes poll waiters.

State and persistence: per-device kernel state includes minor allocation, open count, status flags, shadow regs, and interrupt counter. Hardware register writes affect device state until reset.

Dependencies and integration points: depends on `linux/phantom.h` UAPI, PCI PLX IDs, char devices, class devices, poll, compat ioctl handling, and shared IRQ semantics.

Risks and test signals: only one opener is allowed; races around open/remove need attention. The driver performs direct hardware register writes from userspace-provided values. ISR and ioctl share register state via spinlock, while open state uses mutexes. Tests should cover exclusive open, ioctl validation and compat sizes, poll behavior with IRQs disabled/enabled, NOT_OH mode before/after running, suspend/resume IRQ masking, probe error unwind, and multi-device minor exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/phantom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/Kconfig

Purpose: defines configuration switches for QEMU pvpanic support and its MMIO and PCI transport front ends.

Important symbols: `PVPANIC` is the bool parent option. `PVPANIC_MMIO` is tristate and depends on `HAS_IOMEM`, `(ACPI || OF)`, and `PVPANIC`. `PVPANIC_PCI` is tristate and depends on `PCI` and `PVPANIC`.

Control flow: build selection requires enabling the parent before either concrete transport can be built. Help text describes guest-to-host panic event notification.

State and persistence: no runtime state; it controls build inclusion.

Dependencies and integration points: drives `pvpanic/Makefile`, selecting shared `pvpanic.o` plus either transport object.

Risks and test signals: configuration tests should ensure transports cannot be selected without the parent and that MMIO honors ACPI/OF and IOMEM dependencies. Build matrix should include built-in and module combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/Makefile

Purpose: maps pvpanic Kconfig selections to object files.

Important build rules: `obj-$(CONFIG_PVPANIC_MMIO) += pvpanic.o pvpanic-mmio.o` and `obj-$(CONFIG_PVPANIC_PCI) += pvpanic.o pvpanic-pci.o`.

Control flow: each selected transport links the shared core `pvpanic.o` with the corresponding bus front end.

State and persistence: no runtime state; build-only file.

Dependencies and integration points: consumed by the kernel build system under `drivers/misc`.

Risks and test signals: selecting both transports may include `pvpanic.o` through two obj lines depending on build-system aggregation; build tests should cover MMIO only, PCI only, and both enabled as built-ins/modules to catch duplicate symbol or missing shared-core issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic-mmio.c -->
# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic-mmio.c

Purpose: platform/ACPI/OF front end for pvpanic devices exposed as IO or memory resources.

Important APIs and functions: `pvpanic_mmio_probe()` obtains resource 0 via `platform_get_mem_or_io()`, maps IO resources with `devm_ioport_map()` or memory resources with `devm_ioremap_resource()`, and calls shared `devm_pvpanic_probe()`. Match tables cover OF compatible `qemu,pvpanic-mmio` and ACPI ID `QEMU0001`.

Control flow: probe rejects missing or unsupported resource types, maps the resource with devm-managed lifetime, and delegates all capability/event/sys_off/list registration to the core. The platform driver exposes `pvpanic_dev_groups`.

State and persistence: transport-local state is only the mapped base pointer; persistent pvpanic state is in the shared core instance.

Dependencies and integration points: integrates platform devices from OF/ACPI with the shared `pvpanic.c` implementation and sysfs attribute groups.

Risks and test signals: test IORESOURCE_IO and IORESOURCE_MEM mapping paths, missing resources, devm unwind, ACPI and OF enumeration, and sysfs attributes on the platform device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic-mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic-pci.c -->
# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic-pci.c

Purpose: PCI front end for Red Hat/QEMU pvpanic devices.

Important APIs and functions: `pvpanic_pci_probe()` enables the PCI device with `pcim_enable_device()`, maps BAR0 with `pcim_iomap()`, and delegates to `devm_pvpanic_probe()`. The ID table matches vendor `PCI_VENDOR_ID_REDHAT` and device `0x0011`. The `pci_driver` exposes `pvpanic_dev_groups`.

Control flow: managed PCI helpers keep teardown simple; no explicit remove hook is needed because devm and pcim resources unwind automatically.

State and persistence: only BAR mapping is transport-local; core pvpanic instance state is maintained by `pvpanic.c`.

Dependencies and integration points: depends on PCI and the shared pvpanic header/core. Provides the same sysfs event/capability controls as MMIO.

Risks and test signals: test BAR0 absent or unmappable, PCI enable failure, sysfs group creation, and event delivery under panic/shutdown in a QEMU guest exposing the PCI pvpanic device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic.c -->
# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic.c

Purpose: shared pvpanic core that registers pvpanic instances, exposes capability/event sysfs controls, and sends panic/crash-loaded/shutdown events to hypervisor-visible IO/MMIO registers.

Important APIs and types: `struct pvpanic_instance` stores base register, capability mask, enabled events, optional sys_off handler, and list node. Exported APIs are `devm_pvpanic_probe()` and `pvpanic_dev_groups`. Core helpers include `pvpanic_send_event()`, panic notifier `pvpanic_panic_notify()`, `pvpanic_sys_off()`, `pvpanic_synchronize_sys_off_handler()`, sysfs show/store functions, and `pvpanic_remove()`.

Control flow: module init initializes the global list/spinlock and registers a high-priority panic notifier. Probe reads device-supported events from `ioread8(base)` masked by known bits, enables all supported events by default, conditionally registers a low-priority poweroff sys_off handler, adds the instance to a spinlocked global list, stores drvdata, and registers a devm cleanup action. Panic notification sends `PVPANIC_CRASH_LOADED` if a crash kernel is loaded, else `PVPANIC_PANICKED`. Shutdown sends `PVPANIC_SHUTDOWN`. The `events` sysfs store validates the requested mask against capability and toggles sys_off registration.

State and persistence: global in-memory instance list and per-device enabled event masks. Writes to the hypervisor register are transient event notifications. Sysfs `events` changes persist only until device/module lifetime ends.

Dependencies and integration points: depends on `uapi/misc/pvpanic.h`, panic notifier chain, kexec crash state, sys_off API, MMIO accessors, and the PCI/MMIO transport front ends.

Risks and test signals: `pvpanic_send_event()` uses `spin_trylock()` and silently drops events if contended, which is intentional for panic paths but should be understood. The expression in `pvpanic_synchronize_sys_off_handler()` is subtle; tests should cover enabling/disabling shutdown via sysfs. Event writes occur during panic context, so avoid sleeping and validate with QEMU host-side event observation, crash-kernel loaded/unloaded cases, multiple devices, and removal while sys_off is registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic.h -->
# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic.h

Purpose: small shared header between pvpanic core and bus front ends.

Important APIs and types: forward declares `struct attribute_group` and `struct device`, declares `devm_pvpanic_probe(struct device *dev, void __iomem *base)`, and exports `pvpanic_dev_groups`.

Control flow and integration: transport drivers include this header to map their hardware resource then delegate core registration and expose common sysfs groups.

State and persistence: no state.

Dependencies and risks: includes compiler types for `__iomem`. Any signature change must update both PCI/MMIO transports and the core. Build tests should compile both front ends independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/qcom-coincell.c -->
# sources/distributed-fs/ceph-client/drivers/misc/qcom-coincell.c

Purpose: configures the coincell/backup-battery charger block in Qualcomm PMICs through parent regmap registers.

Important APIs and types: `struct qcom_coincell` stores device, regmap, and base address. `qcom_coincell_chgr_config()` validates and writes resistor/voltage/enable settings. `qcom_coincell_probe()` reads DT properties and calls the configurator. Match table supports `qcom,pm8941-coincell`.

Control flow: probe gets the parent regmap, reads `reg` as base address, treats `qcom,charger-disable` as a disable request, otherwise requires `qcom,rset-ohms` and `qcom,vset-millivolts`. The config function disables by writing zero to enable register, or maps exact resistor/voltage values to indices, writes RSET and VSET, then writes enable bit.

State and persistence: no allocated long-lived driver state; the PMIC registers persist until hardware reset or another driver changes them.

Dependencies and integration points: depends on OF, platform bus, parent PMIC regmap, and DT binding values matching hardcoded maps.

Risks and test signals: invalid DT values reject probe. The comment notes voltage encoding differences for some PMICs, so compatible coverage is important. Tests should cover disabled mode, all valid resistor/voltage entries, invalid values, missing properties, regmap write failures, and parent regmap absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/qcom-coincell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/rp1/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/rp1/Kconfig

Purpose: defines the build option for Raspberry Pi RP1 PCIe-attached peripheral controller support.

Important symbol: `MISC_RP1` is a tristate depending on `OF_IRQ` and `PCI_MSI`. Help text says the driver enables the DT node after PCIe endpoint configuration and handles interrupts for RP1 child devices.

Control flow: selecting this option builds the RP1 PCI driver and requires device-tree IRQ and MSI support.

State and persistence: build-only configuration.

Dependencies and integration points: drives `rp1/Makefile` and the PCI/OF child-device population code in `rp1_pci.c`.

Risks and test signals: build matrix should cover module and built-in forms and ensure missing MSI/OF_IRQ prevents invalid configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/rp1/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/rp1/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/rp1/Makefile

Purpose: builds the RP1 PCI support object when `CONFIG_MISC_RP1` is selected.

Important build rule: `obj-$(CONFIG_MISC_RP1) += rp1_pci.o`.

Control flow/state: no runtime logic; kernel build-system mapping only.

Dependencies and integration points: consumed by `drivers/misc` build.

Risks and test signals: compile with `MISC_RP1=m` and `=y` to catch missing exports in PCI, MSI, IRQ domain, and OF platform APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/rp1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/rp1/rp1_pci.c -->
# sources/distributed-fs/ceph-client/drivers/misc/rp1/rp1_pci.c

Purpose: PCI driver for Raspberry Pi RP1 that maps the endpoint, allocates 61 MSI-X vectors, presents them as an OF IRQ domain for child devices, and populates RP1 subdevices from device tree.

Important APIs and types: `struct rp1_dev` stores PCI device, IRQ domain, backing PCI IRQ data per hardware IRQ, BAR1 mapping, and level-triggered flags. IRQ helpers are `msix_cfg_set/clr()`, `rp1_mask_irq()`, `rp1_unmask_irq()`, `rp1_irq_set_type()`, `rp1_chained_handle_irq()`, `rp1_irq_xlate()`, activate/deactivate hooks, and `rp1_unregister_interrupts()`. PCI lifecycle is `rp1_probe()`/`rp1_remove()`.

Control flow: probe requires an OF node, validates BAR1 length as firmware-initialized, enables PCI with pcim, maps BAR1, sets bus master, allocates exactly `RP1_INT_END` MSI-X vectors, creates a linear IRQ domain, maps each hwirq, sets the RP1 irq chip/handler, installs a chained handler on each PCI MSI-X vector, then calls `of_platform_default_populate()` to instantiate child devices. Chained handling masks through the parent MSI irq data, dispatches the mapped child virq, and acknowledges level-triggered interrupts via RP1 MSI-X config register.

State and persistence: per-device state is devm/pcim-managed except IRQ vectors/domain mappings, which are explicitly removed. Hardware MSI-X config bits persist until cleared/deactivated or device reset.

Dependencies and integration points: depends on OF IRQ domains, PCI MSI-X, Raspberry Pi vendor/device IDs, and child DT nodes for Ethernet/USB/I2C/SPI/UART and other RP1 blocks.

Risks and test signals: exact vector count is required; partial allocation fails. `rp1_irq_xlate()` trusts hwirq values from DT enough to index arrays, so DT validation matters. Cleanup should remove chained handlers/mappings before freeing vectors. Tests should cover missing OF node, short BAR/firmware-not-running case, vector allocation failure, level vs edge IRQ ack behavior, child device probe, and remove/depopulate ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/rp1/rp1_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/rpmb-core.c -->
# sources/distributed-fs/ceph-client/drivers/misc/rpmb-core.c

Purpose: implements the kernel RPMB class, allowing storage providers to register Replay Protected Memory Block devices and clients to find devices, hold references, and route RPMB request/response frames.

Important APIs and types: global `rpmb_ida` allocates class device IDs. Exported APIs are `rpmb_dev_get()`, `rpmb_dev_put()`, `rpmb_route_frames()`, `rpmb_dev_find_device()`, `rpmb_interface_register()`, `rpmb_interface_unregister()`, `rpmb_dev_register()`, and `rpmb_dev_unregister()`. `rpmb_class` defines class name and release callback.

Control flow: `rpmb_dev_register()` validates descriptor, copies the device ID, allocates an ID, initializes device name/class/parent, and registers the device. Release frees ID, copied dev_id, and object. Frame routing validates non-null request/response buffers and delegates to provider `descr.route_frames()` with the parent device. Unregister deletes the device and drops its reference. `subsys_initcall()` registers the class early; module exit destroys IDA and unregisters class.

State and persistence: class devices and IDA allocations are in kernel memory. The RPMB storage itself is external persistent secure storage; this file only routes frames.

Dependencies and integration points: depends on `<linux/rpmb.h>`, device class infrastructure, class interfaces, and provider drivers that supply `struct rpmb_descr`.

Risks and test signals: descriptor ownership is mixed: the struct is copied, but `dev_id` is deep-copied. Providers must unregister at the correct parent lifetime. Tests should cover invalid descriptors, allocation failure unwind, class interface notifications, find-device reference handling, route callback error propagation, and unregister/release sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/rpmb-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/Makefile

Purpose: builds the SGI GRU driver as a composite object.

Important build rules: `ccflags-$(CONFIG_SGI_GRU_DEBUG) := -DDEBUG` enables debug code. `obj-$(CONFIG_SGI_GRU) := gru.o` and `gru-y` links `grufile.o`, `grumain.o`, `grufault.o`, `grutlbpurge.o`, `gruprocfs.o`, `grukservices.o`, `gruhandles.o`, and `grukdump.o`.

Control flow/state: no runtime logic, but it defines which subsystem pieces form `gru.o`.

Dependencies and integration points: requires all listed SGI GRU source files and their x86 UV-platform dependencies.

Risks and test signals: build with and without `CONFIG_SGI_GRU_DEBUG`; link tests should catch missing symbols between researched files and non-researched companion files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gru.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gru.h

Purpose: public-ish GRU architectural and userspace option header defining cacheline/handle offsets, GSEG mapping page size, chiplet info, per-context statistics, and TLB-miss handling options.

Important APIs and types: defines `GRU_CACHE_LINE_BYTES`, `GRU_HANDLE_STRIDE`, `GRU_CB_BASE`, `GRU_DS_BASE`, x86-only `GRU_GSEG_PAGESIZE`, `struct gru_chiplet_info`, `struct gru_gseg_statistics`, and `GRU_OPT_MISS_*` option bits.

Control flow and integration: no functions; constants are consumed by file mmap/ioctls, instruction helpers, and userspace libraries. It enforces x86_64-only builds with `#error` otherwise.

State and persistence: no runtime state.

Dependencies and risks: ABI-sensitive constants define the memory layout expected by userspace and hardware. Tests should compile on supported x86_64 UV configs and ensure userspace tools agree on GSEG size, CB/DS offsets, and option bit semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gru_instructions.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gru_instructions.h

Purpose: defines GRU userspace/kernel inline instruction ABI: command formats, opcode/exception constants, cache flush/start helpers, instruction constructors, status polling wrappers, and pointer helpers for GSEG control/data segments.

Important APIs and types: `struct gru_instruction_bits`, `struct gru_instruction`, `struct control_block_extended_exc_detail`, `union gru_mesqhead`, and `struct gru_control_block_status` mirror hardware command/cacheline layout. Inline APIs issue VLOAD/VSTORE/IVLOAD/IVSTORE/VSET/IVSET/VFLUSH/NOP/BCOPY/BSTORE/GAM* and MESQ instructions, read AMO values, build message queue heads, check/wait/abort status, and locate GSEG/CB/data pointers.

Control flow: constructors fill command fields, data addresses, element counts, strides, operands, and call `gru_start_instruction()`, which ordered-stores the low command word with active/start bits, issues a memory barrier, and flushes the command cacheline. `gru_check_status()` falls back to `gru_check_status_proc()` for non-active statuses; `gru_wait()` and abort use external kernel implementations.

State and persistence: no allocated state, but inline functions mutate memory-mapped GRU control blocks and data segments visible to hardware.

Dependencies and integration points: x86_64 cache flushes via `clflush`, external service routines from `grukservices.c`, and hardware constants used by `grufault.c`/`gruhandles.c`. It is ABI-coupled to userspace libraries.

Risks and test signals: bitfield layout and endianness/compiler packing are critical. A wrong barrier/flush sequence can leave hardware seeing partial commands. Tests should validate each instruction encoding against hardware docs/emulator, check status handling for idle/active/exception/call-OS, and verify message queue/AMO helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gru_instructions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grufault.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grufault.c

Purpose: handles GRU-detected TLB misses and user "call OS" flows by translating user virtual addresses to guest physical addresses, dropping entries into GRU TLB fault handles, retrying or switching to user polling, and exposing exception/unload/flush/stat ioctls.

Important APIs and functions: key helpers include `gru_find_vma()`, `gru_find_lock_gts()`, `gru_alloc_locked_gts()`, `get_clear_fault_map()`, `atomic_pte_lookup()`, `non_atomic_pte_lookup()`, `gru_vtop()`, `gru_try_dropin()`, `gru_intr()`, `gru0_intr()`, `gru1_intr()`, `gru_intr_mblade()`, `gru_handle_user_call_os()`, `gru_get_exception_detail()`, `gru_user_unload_context()`, `gru_user_flush_tlb()`, `gru_get_gseg_statistics()`, and `gru_set_context_option()`.

Control flow: interrupt handlers clear CPU-private TFM fault/done maps, complete async waiters for done bits, and for miss bits try to handle faults atomically under `mmap_read_trylock()`. If atomic translation cannot proceed, hardware is switched to user polling mode. User call-OS path finds/locks the GTS, validates CB number and placement, refreshes CCH if required, then repeatedly waits for inactive range invalidations and calls `gru_try_dropin()`. Drop-in validates TFH exception state, reads fault vaddr/asid/write, blocks during range invalidation, translates PTEs, updates supported page-size state/CCH, optionally preloads BCOPY pages, marks CB active, and issues `tfh_write_restart()`.

State and persistence: updates per-thread GRU state, per-mm range-invalid flags/wait queues, user statistics, TFH/CBE hardware cachelines, and optional context placement preferences. No disk persistence.

Dependencies and integration points: tightly coupled with `grumain.c` context assignment, `grutlbpurge.c` mmu notifier/range invalidation, `gruhandles.c` TFH commands, `grutables.h` state, UV hardware, Linux GUP/PTE APIs, capabilities for global unload, and userspace GRU library ioctls.

Risks and test signals: races with mm teardown, range invalidation, context stealing, and hardware TFH state are central. `gru_get_gseg_statistics()` zeros `sizeof(gts->ustats)` in the no-GTS path even though `gts` is NULL in source expression form, relying on unevaluated member size; worth compiler scrutiny. Tests need real/emulated UV GRU: FMM interrupt fault, UPM call-OS fault, invalid addresses, write faults, hugepage/large-page handling, context relocation, concurrent invalidation, all ioctl paths, and privilege check for unload-all.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grufault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grufile.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grufile.c

Purpose: provides `/dev/gru` file operations, mmap setup, user ioctl dispatch, driver initialization, GRU table discovery, TLB IRQ setup, proc/kservices startup, and module teardown.

Important APIs and functions: globals include `gru_base[]`, `gru_start_paddr`, `gru_start_vaddr`, `gru_end_paddr`, `gru_max_gids`, and `gru_stats`. File operations are `gru_file_mmap()` and `gru_file_unlocked_ioctl()`. Initialization helpers include `gru_supported()`, `gru_init_chiplet()`, `gru_init_tables()`, `gru_setup_tlb_irqs()`, `gru_init()`, and `gru_exit()`. VMA close is `gru_vma_close()`.

Control flow: init only acts on supported x86 UV systems before UV3. It derives GRU physical overlay base from UV MMRs, registers misc device, initializes procfs, allocates per-blade GRU state pages, initializes chiplets/resources, sets up per-chiplet TLB IRQs, starts kernel services, and publishes version info. Mmap requires shared writable GSEG-page-aligned mapping, marks VMA IO/PFNMAP/locked/no-copy/no-dump, installs `gru_vm_ops`, and allocates VMA tracking. Ioctls dispatch context creation/options/exception/unload/flush/call-OS/stats/dump/config/ktest requests.

State and persistence: global GRU topology/state persists for module lifetime; per-VMA data tracks thread states and is freed on VMA close after unloading contexts. Hardware IRQ and GRU resource state persists until exit.

Dependencies and integration points: depends on UV hub APIs/MMRs, miscdevice, procfs, IRQ setup, `grumain.c`, `grufault.c`, `grutlbpurge.c`, `grukservices.c`, and `grukdump.c`.

Risks and test signals: init unwind crosses misc/proc/table/IRQ/kernel-service layers. `gru_free_tables()` uses an order based on `struct gru_state * chiplets` while allocation used `sizeof(struct gru_blade_state)`, which should be verified. Tests should cover unsupported platforms as no-op success, mmap alignment/permission rejection, each ioctl dispatch, VMA close unloading all contexts, IRQ setup/teardown on CPUless blades, and repeated module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grufile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruhandles.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruhandles.c

Purpose: implements privileged GRU MCS handle operations for context configuration, TLB invalidation, and TLB fault-handle dropins/restarts.

Important APIs and functions: exported-to-subsystem functions include `cch_allocate()`, `cch_start()`, `cch_interrupt()`, `cch_deallocate()`, `cch_interrupt_sync()`, `tgh_invalidate()`, `tfh_write_only()`, `tfh_write_restart()`, `tfh_user_polling_mode()`, and `tfh_exception()`. Internal helpers are `start_instruction()`, `wait_instruction_complete()`, `report_instruction_timeout()`, and `update_mcs_stats()`.

Control flow: each operation fills opcode-specific fields, calls `start_instruction()` to set command/status bits after a write barrier and cache flush, then either waits for handle status to leave ACTIVE or returns after issuing async restart-like commands. CCH allocate/deallocate call `sync_core()` to stop speculation into mapped/unmapped GSEG regions. Timeouts after roughly 10 seconds call `panic()` because hardware is considered malfunctioning.

State and persistence: updates hardware MCS handle cachelines and optional `mcs_op_statistics[]`. No file persistence.

Dependencies and integration points: depends on `gruhandles.h`, `grutables.h`, `gru_flush_cache()`, x86 TSC frequency, and consumers in GRU context load/unload, fault handling, and TLB purge code.

Risks and test signals: timeout panic is intentionally severe. Correct memory barriers/cache flushing are essential. Tests should exercise each handle opcode on emulator/hardware, exception status returns, stats accounting with `OPT_STATS`, CCH speculation barriers, and malformed/stuck handle timeout behavior in controlled environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruhandles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruhandles.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruhandles.h

Purpose: defines the GRU memory map, handle offsets/counts, address conversion helpers, hardware handle structures, state/operation enums, page-size encodings, and prototypes for MCS handle operations.

Important APIs and types: constants describe GSEG/MCS base, GRU size, counts for CB/DSR/TFM/TGH/CBE/TFH/CCH, user resource limits, allocation units, chiplet topology, and GSEG offsets. Inline helpers compute GSEG, CB, DS, TFM/TGH/CBE/TFH/CCH addresses and chiplet physical/virtual addresses. Structures mirror hardware handles: `gru_tlb_fault_map`, `gru_tlb_global_handle`, `gru_tlb_fault_handle`, `gru_context_configuration_handle`, and `gru_control_block_extended`.

Control flow and integration: no high-level runtime flow, but the inline helpers are used everywhere to locate MMIO/cacheline-backed hardware structures. Enums define valid opcodes/status/state/cause values consumed by `gruhandles.c`, `grufault.c`, and dump/proc code.

State and persistence: no allocated state; structure definitions interpret live hardware memory.

Dependencies and risks: layout and bitfields are hardware ABI. `GRU_PAGESIZE()`/`GRU_SIZEAVAIL()` must match hardware encoding. Tests should validate structure sizes/offsets, address arithmetic for every context/handle type, page-size encoding table, and lock/unlock helpers from `grutables.h` that operate on these handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruhandles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukdump.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukdump.c

Purpose: implements a diagnostic ioctl path that copies GRU chiplet state, TFM/TGH handles, context CCH/CB/TFH/CBE handles, and optional DSR data to a userspace buffer.

Important APIs and functions: `gru_dump_chiplet_request()` is the user entry point. Helpers include `gru_user_copy_handle()`, `gru_dump_tfm()`, `gru_dump_tgh()`, `gru_dump_context()`, and `gru_dump_context_data()`.

Control flow: request is copied from userspace, gid is bounds-checked and passed through `array_index_nospec()`, then TFM and TGH arrays are copied first. For each requested context, `gru_dump_context()` tries to lock the CCH up to `CCH_LOCK_ATTEMPTS`, copies the CCH, gathers owner pid/vaddr from `gs_gts`, computes allocated CBR/DSR counts, checks user buffer capacity, copies CB/TFH/CBE triplets and optional data segment, unlocks CCH, writes a `GRU_DUMP_MAGIC` header, and advances the output pointer. Return value is number of contexts dumped or a negative error.

State and persistence: read-only diagnostic snapshot except optional cache flushes and temporary CCH lock/delresp clearing in copied user image. No persistent state.

Dependencies and integration points: uses GRU handle layout helpers, `grutables.h` allocation-map iteration, nospec indexing, userspace dump request/header ABI from `grulib.h`, and ioctl dispatch in `grufile.c`.

Risks and test signals: buffer-size arithmetic and user-copy error handling are critical because large hardware state is copied to userspace. Tests should cover invalid gid, single/all-context dumps, too-small buffers, locked CCH behavior, `data_opt`, `flush_cbrs`, and concurrent context unload while dumping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukdump.c -->
