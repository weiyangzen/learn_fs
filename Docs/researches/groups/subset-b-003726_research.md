# subset-b-003726 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600d.h

## Purpose

`r600d.h` is a hardware definition header for the Radeon R600/R700 generation and adjacent display/media blocks. It provides register offsets, PM4 packet encoders, bit masks, bitfield setters/getters, format enumerations, and hardware limits used by the Radeon DRM driver when programming command processor rings, display/audio engines, memory controllers, shader resources, color/depth buffers, DMA engines, interrupt handlers, power-management PLLs, and UVD video decode blocks.

The file does not own runtime behavior directly. Its purpose is to make the rest of the driver speak the R600 hardware ABI consistently through symbolic constants instead of duplicated magic numbers.

## Important APIs, types, and definitions

This header exports preprocessor definitions only; it declares no C structs or functions. Important groups include:

- Command packets: `CP_PACKET2`, `PACKET2(v)`, `PACKET0(reg, n)`, `PACKET3(op, n)`, and many `PACKET3_*` opcodes such as `PACKET3_SURFACE_SYNC`, `PACKET3_EVENT_WRITE`, `PACKET3_CP_DMA`, and `PACKET3_SET_CONTEXT_REG`.
- Hardware limits: `R6XX_MAX_SH_GPRS`, `R6XX_MAX_SH_THREADS`, `R6XX_MAX_BACKENDS`, `R6XX_MAX_SIMDS`, and `R6XX_MAX_PIPES`.
- Tiling modes: `ARRAY_LINEAR_GENERAL`, `ARRAY_LINEAR_ALIGNED`, `ARRAY_1D_TILED_THIN1`, `ARRAY_2D_TILED_THIN1`, plus parallel register-specific `V_*_ARRAY_*` values.
- Color/depth resources: `CB_COLOR*_BASE`, `CB_COLOR*_INFO`, `CB_COLOR*_SIZE`, `CB_COLOR*_VIEW`, `CB_COLOR*_MASK`, `DB_DEPTH_*`, `DB_HTILE_*`, `R_0280A0_CB_COLOR0_INFO`, `R_028010_DB_DEPTH_INFO`, and associated `S_`, `G_`, `C_`, and `V_` helpers.
- Shader and texture resources: `SQ_CONFIG`, `SQ_GPR_RESOURCE_MGMT_*`, `SQ_THREAD_RESOURCE_MGMT`, `SQ_STACK_RESOURCE_MGMT_*`, `SQ_PGM_START_*`, `SQ_VTX_CONSTANT_WORD*`, `R_038000_SQ_TEX_RESOURCE_WORD0_0`, `R_038004_SQ_TEX_RESOURCE_WORD1_0`, and texture format/swizzle helpers.
- Command processor and ring control: `CP_RB_*`, `CP_ME_RAM_*`, `CP_PFP_UCODE_*`, `R_0086D8_CP_ME_CNTL`, `CP_INT_CNTL`, and `CP_INT_STATUS`.
- Memory and VM: `MC_VM_*`, `VM_CONTEXT0_*`, `VM_L2_*`, `MC_VM_L1_TLB_*`, and address aperture masks.
- DMA/IH/RLC: `DMA_*` register definitions and `DMA_PACKET(...)`, `IH_RB_*`, `IH_CNTL`, `RLC_*`, and `SRBM_SOFT_RESET`.
- Display, HPD, vblank, page flip, HDMI/audio, and AFMT blocks: `DISP_INTERRUPT_STATUS*`, `DC_HPD*`, `D1GRPH_INTERRUPT_*`, `AZ_*`, `HDMI0_*`, `AFMT_*`, and `FMT_*`.
- Power management and PLL: `CG_SPLL_FUNC_CNTL`, `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, `MCLK_PWRMGT_CNTL`, clock step registers, `CG_UPLL_FUNC_CNTL`, and temperature interrupt/status fields.

The `S_`, `G_`, and `C_` naming convention is central: setters shift a value into a bitfield, getters extract one, and clear masks preserve all bits except a target field. These helpers are often consumed by `WREG32_P`, direct packet emission, or register sequence tables.

## Control flow and state behavior

There is no executable control flow in this file. Runtime control flow is indirect:

1. ASIC-specific init/resume/reset code includes this header.
2. The driver builds register values or PM4 packets using these macros.
3. Values are written through MMIO helpers, indirect register helpers, or ring emission functions from `radeon.h`.
4. Hardware state changes in GPU blocks, ring pointers, caches, tiling state, interrupts, power states, and display/audio engines.

The persistent state affected by users of this header lives in GPU registers, command rings, writeback memory, firmware-visible scratch fields, VRAM/GART mappings, and driver-owned mirrors such as `struct radeon_device::config`, `ring`, `irq`, `mc`, `pm`, `uvd`, and `audio`. The header itself stores nothing and has no initialization/fini path.

## Dependencies and integration points

`PACKET2(v)` depends on the `REG_SET` helper from `radeon.h`, so include order matters in C files that use this macro. The register constants integrate with:

- `r600.c`, `rv770.c`, and related ASIC files for startup, reset, VM, CP, DMA, IH, RLC, and power management programming.
- Command submission validation and emission paths that generate `PACKET0`/`PACKET3`/DMA packet streams.
- Display and audio code that programs vblank, page flip, HPD, HDMI infoframes, ACR, audio descriptors, and formatter dithering.
- UVD setup and ring code that uses `UVD_*` and `CG_UPLL_*` definitions.
- Lockup/reset code that polls `GRBM_STATUS`, `SRBM_STATUS`, and related busy/soft-reset bitfields.

Because this header represents hardware contracts, it also couples to firmware expectations, VBIOS-derived configuration, userspace-visible command submission validation, and platform power behavior.

## Risks and edge cases

- Bitfield mistakes can cause silent hardware misprogramming. A wrong shift, mask, or enum value can corrupt rendering, hang rings, break display output, or damage power sequencing.
- Several names describe generation-specific behavior, such as r6xx-only HDMI1 base, DCE3 alternate HDMI1 base, DCE3.2 HPD/AUX interrupts, and r7xx-only packet or register behavior. Code must select constants for the active ASIC family.
- Some helpers do not mask inputs, while many `S_` helpers do. Callers must avoid passing out-of-range values into simple shift macros such as `CB_FORMAT(x)` or `BACKEND_DISABLE(x)`.
- Register ranges overlap different address spaces: MMIO, indirect MC/PCIE, config, context, resource, and packet register spaces. Passing a value to the wrong access path can target the wrong hardware block.
- PM4 packet count fields and register offsets are encoded in dwords; off-by-one packet lengths or unaligned register values are high-risk.
- Cache/flush definitions such as `PACKET3_SURFACE_SYNC`, `VGT_CACHE_INVALIDATION`, VM invalidation, and HDP coherency registers are ordering-sensitive and must match fence/IB scheduling semantics.

## Test signals

Useful validation signals are mostly integration-level:

- Boot/resume logs for R600/R700-family hardware should show successful CP, DMA, IH, UVD, display, and PM setup without ring test failures.
- `radeon_ib_ring_tests`, DMA tests, fence completion, and lockup detection exercise packet and ring definitions.
- KMS page flip, vblank, HPD, HDMI/DP audio, and backlight/display mode tests exercise display/audio register groups.
- Piglit/IGT rendering and texture-format coverage can expose CB/DB/SQ/TEX format and tiling mistakes.
- Suspend/resume, runtime PM, thermal interrupt, and DPM tests cover PLL and power-management fields.
- Static review should compare new or changed constants against AMD register documentation and sibling headers for adjacent ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon.h

## Purpose

`radeon.h` is the central internal interface for the Radeon DRM kernel driver. It defines the main driver state object, subsystem data structures, hardware abstraction callback tables, register access macros, module parameter declarations, and cross-file prototypes for memory management, command submission, rings, fences, virtual memory, power management, display, media, ACPI, audio, and ASIC-specific operations.

The header is not a leaf interface. It is the contract that binds the Radeon KMS driver together: most implementation files include it to access `struct radeon_device`, subsystem helpers, ASIC dispatch macros, and shared constants.

## Important APIs, types, and definitions

Important exported configuration and constants include module parameters such as `radeon_modeset`, `radeon_dpm`, `radeon_runtime_pm`, `radeon_uvd`, `radeon_vce`, ring indices (`RADEON_RING_TYPE_GFX_INDEX`, DMA, UVD, VCE, CP1/CP2), timeouts, reset flags, clock/power gating flags, VM limits, GPU page flags, writeback offsets, cursor sizes, and PCIe speed values.

Core state types:

- `struct radeon_device`: the root object. It embeds the DRM device, PCI device, ASIC family/configuration, MMIO and indirect register locks/accessors, BIOS state, clock/MC/GART/mode/scratch/doorbell/MM/TM state, fences, rings, IRQ state, ASIC callback pointer, GEM/TTM state, PM/DPM state, UVD/VCE/audio state, firmware pointers, work items, ACPI notifier and ATIF/ATCS state, VM manager, reset counters, and pinned-memory accounting.
- `union radeon_asic_config` plus per-generation config structs (`r100_asic`, `r300_asic`, `r600_asic`, `rv770_asic`, `evergreen_asic`, `cayman_asic`, `si_asic`, `cik_asic`) store discovered hardware geometry, tiling configuration, backend maps, active SIMD/CU masks, and generation-specific capacities.
- `struct radeon_asic` and `struct radeon_asic_ring` define the function-pointer dispatch layer for init/fini, reset, GART, VM, ring operations, IRQs, display, copy engines, surfaces, HPD, PM, DPM, and page flipping.
- Memory and object types: `struct radeon_bo`, `radeon_bo_list`, `radeon_bo_va`, `radeon_mman`, `radeon_gem`, `radeon_gart`, `radeon_mc`, `radeon_sa_manager`, and `radeon_dummy_page`.
- Synchronization and submission types: `struct radeon_fence_driver`, `radeon_fence`, `radeon_semaphore`, `radeon_sync`, `radeon_ib`, `radeon_ring`, `radeon_cs_chunk`, `radeon_cs_parser`, and `radeon_cs_packet`.
- VM types: `radeon_vm_pt`, `radeon_vm_id`, `radeon_vm`, `radeon_vm_manager`, and `radeon_fpriv`.
- Power/media/display support types: `radeon_clock`, `radeon_pm`, `radeon_dpm`, `radeon_power_state`, clock/voltage dependency tables, fan/thermal structs, `radeon_uvd`, `radeon_vce`, `r600_audio`, `r600_audio_pin`, IRQ stat unions, and ACPI `radeon_atif`/`radeon_atcs` structs.

Important inline helpers and macros include `r100_mm_rreg`, `r100_mm_wreg`, `RREG*`, `WREG*`, `REG_SET`, `REG_GET`, indirect register access macros, `rdev_to_drm`, `to_radeon_fence`, `radeon_get_ib_value`, `radeon_fence_later`, `radeon_fence_is_earlier`, `radeon_ring_write`, ASIC family predicates such as `ASIC_IS_AVIVO`, and high-level dispatch macros such as `radeon_init`, `radeon_ring_test`, `radeon_copy`, `radeon_set_backlight_level`, and `radeon_dpm_enable`.

## Control flow and lifecycle

The header documents the expected initialization flow: `radeon_device_init` performs common object/mutex setup; ASIC init configures memory layout and fatal one-time hardware setup; ASIC startup brings acceleration online after memory-controller setup. Runtime behavior is spread across implementation files but generally follows this model:

1. Probe code allocates/initializes `struct radeon_device` and sets family, flags, MMIO mappings, BIOS data, and `rdev->asic`.
2. Generic code calls dispatch macros such as `radeon_init`, `radeon_resume`, `radeon_suspend`, ring callbacks, VM callbacks, PM callbacks, and display callbacks.
3. ASIC-specific implementations use `rdev->config`, MMIO helpers, firmware pointers, and register headers to program hardware.
4. Userspace IOCTLs create GEM BOs, submit command streams through `radeon_cs_parser`, map virtual addresses, and synchronize with fences.
5. Interrupt handlers, delayed work, ACPI notifications, PM, UVD/VCE idle workers, and hotplug/audio work update shared state asynchronously.
6. Fini/suspend paths unwind rings, fences, GART/VM, GEM/TTM, PM, media firmware allocations, ACPI notifier, and MMIO-facing state.

The file is mostly declarations, but the inline helpers do enforce behavior: direct MMIO reads/writes fast-path registers within `rmmio_size` or `RADEON_MIN_MMIO_SIZE`, indirect paths fall back to slow indexed helpers, `radeon_ring_write` updates write pointer/free counters and emits an error on overrun, and fence comparison helpers require both fences to be on the same ring.

## State and persistence behavior

`struct radeon_device` is persistent per GPU and owns most driver state until device teardown. It contains locks for register index spaces, `exclusive_lock` for high-level exclusion, `ring_lock`, per-VM mutexes/spinlocks, PM mutex/semaphore, IRQ spinlock, work items, and atomic counters. Persistent or long-lived allocations include firmware blobs, BOs for rings/writeback/UVD/VCE/RLC, GART tables, page tables, dummy pages, scratch registers, suballocation managers, and mode/audio/I2C resources.

Userspace-visible state is mediated through GEM BOs, VM mappings, command submission, fences, PRIME sharing, tiling metadata, HyperZ/CMASK ownership, and media handles. Hardware-visible state is mirrored in ring pointers, writeback offsets, page tables, scratch registers, IRQ masks, clock/power state, display/audio state, and firmware memory.

ACPI state is stored in `rdev->atif`, `rdev->atcs`, and `rdev->acpi_nb`. This is the state consumed by `radeon_acpi.c`.

## Dependencies and integration points

External kernel subsystems include DRM core, GEM, TTM, DMA fences, DRM execution helpers, DRM suballocation, audio component binding, AGP, PCI, firmware loading, workqueues, wait queues, MMU notifiers, ACPI when enabled, and architecture/platform MMIO APIs.

Internal dependencies include `radeon_family.h`, `radeon_mode.h`, `radeon_reg.h`, `clearstate_defs.h`, `radeon_object.h`, VBIOS/ATOM helpers, ASIC implementation files, display encoder code, command parser code, memory manager code, UVD/VCE code, power-management code, and ACPI code.

The ASIC callback table is the major integration point. Generic code should call the dispatch macros and shared helpers, while per-family files populate `struct radeon_asic` and `struct radeon_asic_ring` with generation-specific behavior.

## Risks and edge cases

- This header is a high-blast-radius interface. Changing struct layout, callback signatures, constants, or macros can affect nearly every Radeon implementation file.
- Function-like macros often evaluate arguments directly and assume valid `rdev` and callback pointers. Callers must not use them before ASIC setup or after teardown.
- `REG_GET(FIELD, v)` appears to apply shift/mask in the same direction as `REG_SET`; users should verify intended semantics before adding new uses because many register-specific `G_*` helpers are clearer and already shift right.
- Ring and fence helpers assume ring indices and same-ring comparisons are correct; cross-ring fence ordering is represented separately through `radeon_sync`.
- MMIO direct/indirect selection depends on register size and address-space knowledge. Using `RREG32` for an indirect-only register can be wrong.
- Many state fields are concurrency-sensitive. Ring writes cannot sleep between begin/end, BO/VM lists have reservation or mutex requirements, IRQ fields need spinlock/atomic discipline, and PM/DPM state is protected by dedicated locks.
- `CONFIG_ACPI`, `CONFIG_AGP`, and `CONFIG_MMU_NOTIFIER` change available APIs through stubs. Callers must handle no-op or `-ENODEV` behavior.
- Hardware generations differ heavily. ASIC predicate macros and callback tables must be kept consistent with family flags and PCI IDs.

## Test signals

Validation should combine build coverage and hardware/runtime testing:

- Compile with `CONFIG_ACPI`, `CONFIG_AGP`, and `CONFIG_MMU_NOTIFIER` both enabled and disabled where feasible to cover stubs and declarations.
- Boot representative ASIC generations and verify `radeon_device_init`, ASIC init/startup, suspend/resume, reset, and teardown.
- Run GEM/TTM memory tests, command submission tests, IB/ring tests, fence waits, VM bind/unbind/update tests, and PRIME/userptr paths.
- Exercise display modesetting, page flips, vblank, HPD, backlight, audio component binding, HDMI/DP audio, and runtime PM.
- Run UVD/VCE create/destroy and idle paths on supported hardware.
- Use lockdep/KASAN/KCSAN where available because this header coordinates many locks, atomics, workqueues, and list lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_acpi.c

## Purpose

`radeon_acpi.c` implements the Radeon driver's ACPI integration for AMD ATIF and ATCS methods. It verifies firmware-provided ACPI interfaces, records supported ATIF/ATCS features in `struct radeon_device`, registers an ACPI notifier, handles selected ACPI power/display events, forwards AC power changes into Radeon power management, handles SBIOS brightness and dGPU display events, and exposes helpers for PCIe performance requests through ATCS.

The code is compiled only when the Radeon ACPI hooks are enabled by `CONFIG_ACPI`; `radeon.h` provides no-op stubs otherwise.

## Important APIs, types, and functions

Local packed ACPI buffer structures mirror firmware return/input layouts:

- `struct atif_verify_interface`: ATIF size, version, notification mask, and function bitmask.
- `struct atif_system_params`: ATIF notification configuration, valid mask, flags, and optional command code.
- `struct atif_sbios_requests`: pending SBIOS request bits plus brightness, thermal, forced power, and power source payload fields.
- `struct atcs_verify_interface`: ATCS size, version, and function bitmask.
- `struct atcs_pref_req_input` and `struct atcs_pref_req_output`: ATCS PCIe performance request input and return value.

Important internal functions:

- `radeon_atif_call()` and `radeon_atcs_call()` evaluate ACPI `ATIF`/`ATCS` methods with a function selector and optional buffer argument, returning an allocated ACPI object buffer or `NULL`.
- `radeon_atif_parse_notification()` and `radeon_atif_parse_functions()` translate ATIF masks into booleans in `rdev->atif`.
- `radeon_atif_verify_interface()` calls `ATIF_FUNCTION_VERIFY_INTERFACE`, validates minimum buffer size, copies the bounded output, and fills notification/function support.
- `radeon_atif_get_notification_params()` calls `ATIF_FUNCTION_GET_SYSTEM_PARAMETERS` and decides whether notifications are disabled, fixed at `0x81`, or use a firmware-provided command code.
- `radeon_atif_get_sbios_requests()` calls `ATIF_FUNCTION_GET_SYSTEM_BIOS_REQUESTS`, validates/copies the request structure, and returns the number of pending request bits.
- `radeon_atif_handler()` filters ACPI video events, fetches SBIOS requests, handles brightness hotkeys and dGPU display events, and returns `NOTIFY_BAD` after consuming a Radeon-specific ATIF event.
- `radeon_atcs_parse_functions()` and `radeon_atcs_verify_interface()` fill `rdev->atcs` supported-function booleans.
- `radeon_acpi_event()` is the registered notifier callback; it handles AC adapter class events and delegates ATIF video notifications.

Exported functions:

- `radeon_acpi_init()` verifies ATCS/ATIF, finds the backlight encoder if needed, configures notification handling, and registers the ACPI notifier.
- `radeon_acpi_fini()` unregisters the notifier.
- `radeon_acpi_is_pcie_performance_request_supported()` checks for both ATCS PCIe performance request and device-ready support.
- `radeon_acpi_pcie_notify_device_ready()` invokes the ATCS device-ready notification.
- `radeon_acpi_pcie_performance_request()` sends an ATCS PCIe link-speed request with optional capability advertisement.

## Control flow and lifecycle

Initialization:

1. `radeon_acpi_init()` obtains the ACPI handle from the PCI device.
2. It exits successfully without registering ACPI support when the ASIC is not AVIVO-class, BIOS is absent, or no ACPI handle exists.
3. It verifies ATCS first. ATCS failure is logged but not fatal for the rest of ATIF setup.
4. It verifies ATIF. ATIF failure is returned after jumping to the common notifier registration path.
5. If brightness notifications are supported, it scans DRM encoder objects for an LCD encoder with a valid backlight device and stores it in `atif->encoder_for_bl`.
6. If SBIOS requests are supported but system parameters are not advertised, it enables the system-params path as a compatibility workaround.
7. If system parameters are supported, it reads notification configuration and disables notifications on failure.
8. It sets `rdev->acpi_nb.notifier_call` and registers with the ACPI notifier chain.

Event handling:

1. `radeon_acpi_event()` receives all ACPI bus events from the notifier chain.
2. AC adapter class events call `radeon_pm_acpi_event_handler(rdev)` after checking current system supply state.
3. All events are passed to `radeon_atif_handler()`.
4. `radeon_atif_handler()` accepts only `ACPI_VIDEO_CLASS` events matching the configured ATIF command code.
5. It reads pending SBIOS requests. Brightness requests update the selected Radeon encoder backlight and force a backlight hotkey update through the kernel backlight device. dGPU display events on PX systems temporarily runtime-resume the GPU, emits a DRM HPD event, and autosuspends again.
6. Consumed ATIF events return `NOTIFY_BAD` to stop propagation because firmware overloads generic video notify values.

ATCS PCIe request handling:

1. The exported helper validates the ACPI handle and advertised support bit.
2. It fills `atcs_pref_req_input` with PCI client ID, valid flags, wait-for-completion, optional advertise-caps, request type `ATCS_PCIE_LINK_SPEED`, and requested speed.
3. It calls ATCS up to three times while firmware reports `ATCS_REQUEST_IN_PROGRESS`, delaying 10 usec between tries.
4. It returns `0` for complete, `-EINVAL` for refused/invalid/small output, and `-EIO` for call failure. If all retries report in-progress, the current code returns `0`.

## State and persistence behavior

Persistent state is stored on `struct radeon_device`:

- `rdev->atif.notifications`, `rdev->atif.functions`, and `rdev->atif.notification_cfg` store firmware capability and event routing data.
- `rdev->atif.encoder_for_bl` caches the encoder/backlight device to update on firmware brightness requests.
- `rdev->atcs.functions` stores ATCS capabilities for PCIe and external state helpers.
- `rdev->acpi_nb` stores the notifier block until `radeon_acpi_fini()`.

ACPI method return buffers are allocated by ACPICA through `ACPI_ALLOCATE_BUFFER` and freed with `kfree()` after parsing. Runtime PM references around dGPU display events are transient and balanced with autosuspend. Backlight changes persist in display/backlight subsystem state and usually hardware registers through the ASIC display callback.

## Dependencies and integration points

Kernel dependencies include ACPI core, ACPI video/bus events, PCI helpers, runtime PM, power supply, backlight, slab allocation, and DRM probe helper HPD notification. Radeon dependencies include `atom.h`, `radeon.h`, `radeon_acpi.h`, `radeon_pm.h`, display encoder private structs, `radeon_set_backlight_level`, `rdev_to_drm`, `ASIC_IS_AVIVO`, `RADEON_IS_PX`, and `radeon_pm_acpi_event_handler`.

The file integrates with VGA switcheroo through `radeon_atpx_dgpu_req_power_for_displays()` when configured. It also integrates with dynamic power management through AC adapter events and with PCIe link management through ATCS performance request methods.

## Risks and edge cases

- ACPI firmware buffers are trusted enough to dereference the leading size field before type/length checks. Malformed firmware objects could expose robustness issues unless ACPICA guarantees a buffer object for these methods.
- `radeon_atif_call()` and `radeon_atcs_call()` return `buffer.pointer` even for `AE_NOT_FOUND`; callers generally treat `NULL` as failure, but a non-buffer or unexpected pointer content would still be risky.
- `radeon_acpi_init()` registers the notifier even after ATIF verification failure via the `out` label. That means the notifier may run with mostly zeroed ATIF state; current filtering should make this benign, but it is an important lifecycle detail.
- The PCIe performance request returns success after exhausting retries while firmware repeatedly reports `IN_PROGRESS`. That may mask a link-speed change that never completed.
- Backlight handling assumes `enc->enc_priv` matches `rdev->is_atom_bios` and contains a valid backlight pointer. The init scan checks this, but later encoder/backlight teardown ordering must keep `encoder_for_bl` safe until notifier unregister.
- Consuming events with `NOTIFY_BAD` intentionally suppresses generic video notifications. Incorrect command-code configuration can hide events from userspace.
- Runtime PM get/put around dGPU display events assumes the device can safely resume in notifier context and that HPD processing does not require longer-lived power references.

## Test signals

Useful tests and observations include:

- Boot on systems with and without ATIF/ATCS firmware methods and verify init returns harmlessly when unsupported.
- AC adapter plug/unplug should trigger `radeon_pm_acpi_event_handler()` and expected PM policy changes.
- Brightness hotkeys on ATIF-capable laptops should update both hardware brightness and backlight subsystem state.
- PX/switchable graphics systems should emit DRM HPD events on dGPU display notifications without runtime PM reference leaks.
- PCIe DPM paths should verify `radeon_acpi_is_pcie_performance_request_supported()`, device-ready notification, and performance request return handling.
- Suspend/resume and module unload should show no ACPI notifier use-after-free after `radeon_acpi_fini()`.
- Fault injection or ACPI table variation tests should cover short buffers, missing methods, refused ATCS requests, and in-progress retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_acpi.c -->
