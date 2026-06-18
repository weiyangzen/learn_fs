# subset-b-003730 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_device.c

## Purpose

`radeon_device.c` is the central Radeon KMS device lifecycle implementation. It translates PCI/platform state into a populated `struct radeon_device`, initializes common GPU services, wires ATOM/COMBIOS firmware accessors, handles runtime power/switcheroo, and provides suspend, resume, and GPU reset recovery paths. It also owns small shared allocators for scratch registers and doorbells, writeback memory setup, memory-controller address layout, and boot/post detection.

## Important APIs, Types, and Functions

- `radeon_device_init()` initializes locks, GEM state, ASIC callbacks, DMA masks, MMIO/IO mappings, VGA switcheroo state, core hardware via `radeon_init()`, debugfs, audio components, ring tests, optional test/benchmark hooks, and AGP fallback.
- `radeon_device_fini()` tears down audio, core Radeon state, switcheroo/VGA clients, IO/MMIO mappings, and doorbells.
- `radeon_suspend_kms()` and `radeon_resume_kms()` coordinate display shutdown/restore, BO eviction, fence draining, BIOS scratch save/restore, AGP, PCI power state, HPD, DPM/PM, and client notifications.
- `radeon_gpu_reset()` serializes reset with `exclusive_lock`, backs up ring command streams, resets ASIC state, restores rings or forces fence completion, reinitializes display/PM, and retries ring tests.
- `radeon_atombios_init()` and `radeon_atombios_fini()` allocate the AtomBIOS `card_info`, install register/PLL/MC/IO callbacks, parse BIOS tables, initialize Atom locks, and manage Atom scratch memory.
- `radeon_scratch_*`, `radeon_doorbell_*`, and `radeon_wb_*` manage shared GPU communication resources used by rings and fences.
- `radeon_vram_location()` and `radeon_gtt_location()` derive GPU address windows from MC limits, aperture sizes, AGP overlap, and module limits.

## Control Flow

Probe reaches this file through `radeon_driver_load_kms()` in `radeon_kms.c`. `radeon_device_init()` first sets stable defaults and synchronization primitives, then validates module parameters through `radeon_check_arguments()`. ASIC-specific function tables are installed by `radeon_asic_init()` before MMIO access. The function maps MMIO, optional doorbells, and PCI IO space, registers VGA/switcheroo callbacks, then calls `radeon_init()` for hardware-specific bring-up. If AGP acceleration fails, it resets, tears down, disables AGP, and retries with PCI/PCIe GART behavior.

Suspend disables polling, turns off connectors, unpins cursor/front buffers where safe, evicts VRAM, waits for all rings or force-completes fences, saves scratch registers, suspends hardware, finalizes HPD, evicts again for VRAM-backed GART tables, and optionally powers down PCI. Resume restores PCI/AGP, resumes hardware, retests rings, reestablishes PM/DPM state, restores scratch registers, repins cursors, reinitializes Atom encoders and HPD, forces modes, and resumes clients.

Reset follows a similar but in-kernel recovery path under `exclusive_lock`: save scratch, suspend hardware, back up rings, ASIC reset, restore/resume hardware, restore or discard ring backups, restart PM/display, force modes, then run IB tests.

## State and Persistence Behavior

Persistent state lives in `struct radeon_device`: family/flags, MMIO mappings, ring IDs, fence context, memory-controller limits, writeback object, scratch register bitmap, doorbell bitmap, Atom context, runtime-PM/switcheroo state, and reset flags. The file mutates global module parameters when invalid values are corrected. Hardware state is persisted across suspend/reset by BIOS scratch save/restore and by ring backup/restore. `exclusive_lock` separates reset from fence waits and page-flip work; many initialization mutexes are created here for use by other modules.

## Dependencies and Integration Points

This file depends on PCI, DMA mask setup, EFI checks, VGA arbiter/switcheroo, runtime PM, DRM KMS helpers, TTM/Radeon BO helpers, firmware parsers (`atom.c`, COMBIOS), ASIC-specific function tables, AGP, HPD, audio, DPM/PM, fences, and IB tests. `radeon_drv.c` reaches it through probe and PM callbacks; `radeon_display.c` relies on its suspend/resume and Atom encoder reinitialization; `radeon_fence.c` relies on writeback and scratch allocation.

## Risks and Edge Cases

- Error paths after MMIO, IO, switcheroo, or domain-PM registration are partial; callers must rely on upper-layer unload or probe failure handling to avoid leaks.
- Scratch and doorbell allocators are simple bitmaps without local locking, so callers need external serialization.
- `radeon_atombios_fini()` manually frees Atom internals rather than calling `atom_destroy()`, so lifecycle ownership must stay synchronized with `atom.c`.
- Suspend/resume and reset contain many best-effort operations; failures in cursor pinning, ring tests, PM late init, or ring backup restore can leave degraded acceleration.
- Address sizing depends on global module parameters and family checks; invalid limits are clamped but still affect memory layout.

## Test Signals

Useful signals include PCI probe/unload under KMS, runtime PM on PX systems, suspend/resume with active displays and fbcon, forced GPU reset via debugfs/fence lockup, AGP fallback paths, Atom and COMBIOS initialization on old/new ASICs, writeback disabled/enabled modes, ring tests after resume/reset, and module-parameter validation for GART/VRAM/VM sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_device.h

## Purpose

`radeon_device.h` is a very small private header for the Radeon device layer. In this snapshot it only exposes the virtualization probe helper needed outside `radeon_device.c`, while preserving the long-standing private-header include guard and license block.

## Important APIs, Types, and Functions

- `bool radeon_device_is_virtual(void);` reports whether the driver appears to run under a hypervisor. The implementation is architecture-dependent: on x86 it checks `X86_FEATURE_HYPERVISOR`; on non-x86 it returns false.

## Control Flow

The header contributes no control flow by itself. Consumers include it when they need the virtualization query without depending on the full `radeon.h` implementation details. `radeon_drv.c` includes it as part of driver entry setup, and `radeon_device.c` provides the implementation used during boot/post checks and virtualized ASIC handling.

## State and Persistence Behavior

There is no persistent state in the header. The exported function reads CPU/platform capability state at runtime and does not cache results here.

## Dependencies and Integration Points

The file integrates the device lifecycle code with other Radeon components through a single declaration. Its guard name, `__RADEON_DEVICE_H__`, prevents repeated inclusion. The actual implementation depends on kernel CPU feature helpers when built on x86.

## Risks and Edge Cases

- The API is intentionally coarse: non-x86 platforms always report false in the current implementation even if a hypervisor is present.
- Because the header is private and minimal, adding more declarations should be weighed against using `radeon.h` or a more focused subsystem header.

## Test Signals

Build coverage should ensure every include compiles without requiring hidden transitive headers. Runtime coverage should check pass-through behavior that uses `radeon_device_is_virtual()` to force ASIC init for newer families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_display.c

## Purpose

`radeon_display.c` implements common Radeon KMS display management: CRTC allocation, gamma/LUT programming, page-flip scheduling and completion, display connector setup, pixel PLL calculations, framebuffer creation, mode properties, AFMT/HDMI audio block allocation, mode-setting init/fini, scaling decisions, and scanout-position reporting for vblank timestamping.

## Important APIs, Types, and Functions

- LUT paths `legacy_crtc_load_lut()`, `avivo_crtc_load_lut()`, `dce4_crtc_load_lut()`, `dce5_crtc_load_lut()`, and `radeon_crtc_load_lut()` program family-specific gamma hardware.
- Page-flip paths `radeon_crtc_page_flip_target()`, `radeon_flip_work_func()`, `radeon_crtc_handle_vblank()`, and `radeon_crtc_handle_flip()` pin the new BO, wait on fences, program the flip, send events, put vblank references, and asynchronously unpin the old BO.
- `radeon_crtc_init()` allocates each `struct radeon_crtc`, creates its high-priority workqueue, installs CRTC funcs, sets cursor bounds, and dispatches Atom or legacy CRTC initialization.
- `radeon_compute_pll_avivo()` and `radeon_compute_pll_legacy()` calculate pixel-clock dividers under family/PLL constraints.
- `radeon_framebuffer_init()` and `radeon_user_framebuffer_create()` bridge GEM BOs to DRM framebuffers, rejecting imported dma-buf scanout.
- `radeon_modeset_init()` and `radeon_modeset_fini()` create DRM mode config, properties, I2C, CRTCs, connectors/encoders, HPD, AFMT, polling, and late PM state.
- `radeon_crtc_scaling_mode_fixup()` and `radeon_get_crtc_scanoutpos()` handle panel/HDMI scaling and vblank position queries.

## Control Flow

Mode-setting initialization starts with `drm_mode_config_init()`, max dimension selection by ASIC generation, property creation, I2C setup, optional hardcoded COMBIOS EDID loading, CRTC allocation, BIOS-derived connector/encoder setup, Atom encoder/PLL init, HPD init, AFMT allocation, polling init, and PM late init. Connector setup first tries Atom supported-device or object tables, then COMBIOS or fallback legacy tables, then configures clone masks and logs topology.

Page flips are split between IOCTL context and workqueues. The IOCTL path allocates `radeon_flip_work`, references the old BO, pins the new BO into VRAM, captures a write fence from the new reservation object, calculates legacy base offsets/tiling adjustment when needed, marks the CRTC pending under `event_lock`, swaps `primary->fb`, and queues work. The worker waits for the fence, may trigger GPU reset on `-EDEADLK`, waits out unsafe vblank windows, enables page-flip IRQs, programs hardware, and marks submitted. IRQ/vblank completion sends the event and queues old-BO unpin.

## State and Persistence Behavior

Persistent display state is in `rdev->mode_info`: CRTC pointers, properties, hardcoded EDID, AFMT blocks, backlight encoder, HPD data, and `mode_config_initialized`. Each CRTC tracks flip status, flip work, native/scaling values, cursor limits, workqueue, and vblank lead lines. Page flip state is protected by DRM `event_lock`; reset interaction is protected by `exclusive_lock`.

## Dependencies and Integration Points

The file depends on DRM CRTC/mode/fb/vblank helpers, runtime PM, TTM/GEM BOs, Radeon IRQ, fence, Atom/COMBIOS connector parsers, I2C, HPD, PM, backlight/encoder code, and family register definitions. `radeon_fbdev.c` reuses `radeon_framebuffer_init()`, while `radeon_device.c` calls mode init/fini and resume/reset reinitializes Atom display blocks.

## Risks and Edge Cases

- Page-flip completion has known race windows on older ASICs; the code mixes pflip IRQs and vblank polling depending on `radeon_use_pflipirq`.
- Imported dma-buf framebuffer creation is rejected because the BO cannot be migrated to VRAM for scanout.
- PLL computation is constraint-heavy and can produce poor clocks if BIOS limits are wrong.
- `radeon_modeset_init()` returns `ret` directly when connector setup fails, but `ret` is boolean in that block, so failure is returned as 0/false-style success semantics only because caller context expects nonzero as success earlier; this path needs careful review if refactored.
- AFMT allocation is best-effort and sparse; users must tolerate missing blocks.

## Test Signals

Test page flips with and without pflip IRQs, async flips, fenced BOs, reset during flip, legacy and DCE scanout, gamma updates, framebuffer creation rejection for imported dma-buf, PLL results for known modes, HDMI underscan/scaling properties, suspend/resume display restore, and vblank timestamp accuracy across CRTC families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_dp_auxch.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_dp_auxch.c

## Purpose

`radeon_dp_auxch.c` implements the native DisplayPort AUX channel transfer hook for Radeon DCE hardware. It translates DRM DP AUX messages into writes and reads of the Radeon AUX software-control registers, handling native AUX and AUX-I2C read/write requests for up to 16 payload bytes.

## Important APIs, Types, and Functions

- `radeon_dp_aux_transfer_native(struct drm_dp_aux *aux, struct drm_dp_aux_msg *msg)` is the sole exported implementation. It is installed as `aux.transfer` by DisplayPort setup code.
- `AUX_RX_ERROR_FLAGS` groups hardware status bits that mean the AUX transaction failed.
- `aux_offset[]` maps AUX engine instances to register offsets.
- `BARE_ADDRESS_SIZE` documents the three-byte DP AUX address header.

## Control Flow

The transfer function validates message size and request type, derives write/read direction, computes the number of bytes to push into the hardware FIFO, and locks the owning `radeon_i2c_chan` mutex. It switches the pad into AUX mode through the DDC mask clock register, programs `AUX_CONTROL` with HPD selection and enable bits, writes the request/address/size header and optional payload into `AUX_SW_DATA`, clears pending completion, starts the transaction with `AUX_SW_GO`, and polls `AUX_SW_STATUS` up to about 100-200 ms total. On success it reads the reply byte and any returned payload bytes, acknowledges completion, sets `msg->reply`, and returns the transferred byte count.

## State and Persistence Behavior

The function does not own persistent state, but it mutates AUX engine registers and the pad mode for the selected I2C/AUX channel. Per-channel serialization is via `chan->mutex`. The caller-provided `msg->buffer` is filled for reads, and `msg->reply` is updated when the hardware transaction succeeds.

## Dependencies and Integration Points

This file depends on DRM DP AUX definitions, `struct radeon_i2c_chan`, Radeon MMIO helpers, HPD/DDC records, and DCE register definitions from `nid.h`. `atombios_dp.c` selects this native path when configured; otherwise AUX may use AtomBIOS paths. The transfer result feeds DRM DP link training, DPCD reads, EDID-over-AUX, and AUX-I2C operations.

## Risks and Edge Cases

- Only payloads up to 16 bytes are accepted; callers must split larger AUX operations.
- Polling is used instead of IRQ completion, so hung hardware can block for the full retry window.
- `instance = chan->rec.i2c_id & 0xf` assumes the low nibble indexes `aux_offset[]`; invalid firmware records could index past the six-entry table.
- The register mask update `tmp &= AUX_HPD_SEL(0x7)` is unusual because it preserves only selected bits before ORing new control bits; changes need hardware validation.
- Returned byte count includes the ACK byte, so read payload length is `bytes - 1`.

## Test Signals

Test DPCD reads/writes, EDID reads over AUX-I2C, timeout/error status handling, disconnect during AUX, each AUX engine instance, HPD selection, invalid request rejection, maximum-size payloads, and concurrent AUX/DDC access on the same channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_dp_auxch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_drv.c

## Purpose

`radeon_drv.c` is the Linux module, PCI, DRM driver, IOCTL, and power-management entry point for the Radeon KMS driver. It declares module parameters, exposes supported PCI IDs, selects whether Radeon or AMDGPU should bind SI/CIK devices, probes PCI devices, wraps DRM IOCTLs with runtime PM, and registers the `drm_driver` and `pci_driver`.

## Important APIs, Types, and Functions

- Global module parameters such as `radeon_modeset`, `radeon_gart_size`, `radeon_dpm`, `radeon_runtime_pm`, `radeon_use_pflipirq`, `radeon_si_support`, and `radeon_cik_support` configure broad driver behavior.
- `radeon_support_enabled()` arbitrates SI/CIK ownership against AMDGPU support and module parameters.
- `radeon_pci_probe()` removes conflicting apertures, allocates `struct radeon_device` embedded in DRM, enables PCI, loads KMS, registers DRM, and starts generic DRM client setup.
- PM callbacks `radeon_pmops_*()` route system sleep, hibernation, runtime suspend/resume/idle, and PX power transitions to `radeon_suspend_kms()` and `radeon_resume_kms()`.
- `radeon_drm_ioctl()` obtains a runtime PM reference around `drm_ioctl()`.
- `radeon_ioctls_kms[]`, `radeon_driver_kms_fops`, and `kms_driver` define the KMS ABI surface.
- `radeon_module_init()` and `radeon_module_exit()` register/unregister the PCI driver and ATPX handler.

## Control Flow

Module init disables binding when firmware-only drivers are requested and modeset was not forced, then registers ATPX and the PCI driver. PCI probe rejects disabled ASIC families or switcheroo-deferred devices, removes firmware framebuffer apertures, allocates the DRM/Radeon device, enables PCI, installs driver data, calls `radeon_driver_load_kms()`, registers the DRM device, and creates initial DRM clients with a conservative fb format for very small VRAM devices.

IOCTL calls enter `radeon_drm_ioctl()` from file ops, take a runtime-PM reference, dispatch through DRM's IOCTL table, and drop the reference. Runtime suspend only allows PX devices, disables polling, suspends KMS without client notification, saves/disables PCI, and powers down via ATPX or PCI D-state; runtime resume reverses that and calls `radeon_resume_kms()`.

## State and Persistence Behavior

Module parameters are global mutable configuration consumed throughout the driver. PCI probe persists `struct drm_device` in PCI drvdata and stores `struct radeon_device` as `dev_private`. Runtime PM state is represented in DRM `switch_power_state`, PCI power state, and autosuspend state.

## Dependencies and Integration Points

The file integrates Linux module/PIC infrastructure, DRM core, DRM GEM mmap/read/poll/open/release helpers, aperture removal, fb client setup, VGA switcheroo, runtime PM, MMU notifier synchronization, and all KMS/GEM/CS/info IOCTL implementations in other Radeon files.

## Risks and Edge Cases

- Many module parameters are read globally without local locking; they are mostly immutable after load but permissions vary.
- Runtime suspend refuses non-PX devices and active CRTCs, so display state drives power behavior.
- Probe error path disables PCI but relies on devm/DRM unload behavior for already-initialized driver state.
- Legacy non-KMS IOCTL numbers remain in the table as `drm_invalid_op`; ABI numbering must not be disturbed.

## Test Signals

Test PCI binding and rejection for SI/CIK with AMDGPU options, module parameter parsing via sysfs/modprobe, runtime PM on PX systems, IOCTLs waking suspended devices, compat IOCTL routing, probe failure cleanup, DRM client setup on low-VRAM boards, and module unload after open/render-node use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_drv.h

## Purpose

`radeon_drv.h` is the private driver-entry header for the Radeon DRM driver. It centralizes driver identity strings, the historical non-KMS DRM ABI version, KMS load/open/close prototypes, the Radeon IOCTL wrapper prototype, and ATPX/vga-switcheroo handler declarations or stubs.

## Important APIs, Types, and Functions

- Driver metadata macros: `DRIVER_AUTHOR`, `DRIVER_NAME`, and `DRIVER_DESC`.
- Legacy DRM ABI version macros: `DRIVER_MAJOR`, `DRIVER_MINOR`, and `DRIVER_PATCHLEVEL`, with an in-file history of old UMS/DRI interface changes.
- Entry prototypes: `radeon_drm_ioctl()`, `radeon_driver_load_kms()`, `radeon_driver_unload_kms()`, `radeon_driver_open_kms()`, and `radeon_driver_postclose_kms()`.
- ATPX/switcheroo prototypes: `radeon_register_atpx_handler()`, `radeon_unregister_atpx_handler()`, `radeon_has_atpx_dgpu_power_cntl()`, and `radeon_is_atpx_hybrid()`, with inline no-op/false stubs when `CONFIG_VGA_SWITCHEROO` is disabled.

## Control Flow

The header does not execute logic, but it determines which external functions `radeon_drv.c` can call during module init/probe/open/close and whether ATPX behavior is compiled as real calls or stubs. Including `radeon_family.h` makes family and flag values available to PCI ID and entry code.

## State and Persistence Behavior

There is no runtime state here. The macros define stable identity and ABI constants that become part of module metadata and DRM driver registration. The compile-time switcheroo stubs change behavior by configuration rather than runtime state.

## Dependencies and Integration Points

This file depends on Linux firmware/platform headers and `radeon_family.h`. It is used by `radeon_drv.c` and KMS support code to share prototypes without exposing broader Radeon internals. The ATPX declarations integrate with the platform power management implementation built when switcheroo is enabled.

## Risks and Edge Cases

- The legacy ABI version history is documentation and should not be casually edited; userspace may rely on version reporting.
- Stubs hide ATPX functionality at compile time, so code paths must be safe when hybrid graphics detection always returns false.
- Adding broad declarations here can increase coupling between driver entry code and lower-level subsystems.

## Test Signals

Build both with and without `CONFIG_VGA_SWITCHEROO`, verify module metadata and DRM driver names, ensure KMS open/postclose/load prototypes stay synchronized with implementations, and check that legacy ABI constants match expected userspace-visible values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_encoders.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_encoders.c

## Purpose

`radeon_encoders.c` provides common encoder and connector helper logic for Radeon display setup. It derives clone masks, maps firmware-supported device bits and DAC selections to Atom encoder object IDs, links encoders to connectors, initializes backlight support, resolves active connectors/external encoders, adjusts panel modes to native timing, determines dual-link requirements, and classifies digital encoders.

## Important APIs, Types, and Functions

- `radeon_setup_encoder_clones()` sets `possible_clones` for all encoders through `radeon_encoder_clones()`.
- `radeon_get_encoder_enum()` maps Atom device support masks and DAC numbers to encoder enum IDs, with family-specific exceptions.
- `radeon_link_encoder_connector()` attaches matching encoders to connectors and invokes backlight setup for LCD devices.
- `radeon_encoder_set_active_device()`, `radeon_get_connector_for_encoder()`, and `radeon_get_connector_for_encoder_init()` maintain or query the active device mask relationship.
- `radeon_get_external_encoder()` and `radeon_encoder_get_dp_bridge_encoder_id()` find external bridge encoders such as Travis/Nutmeg.
- `radeon_panel_mode_fixup()` replaces adjusted mode timing with native panel timing while preserving blank/sync relationships.
- `radeon_dig_monitor_is_duallink()` and `radeon_encoder_is_digital()` answer link capability/type questions used by mode validation and encoder programming.

## Control Flow

After BIOS connector/encoder objects are created, display setup calls clone configuration and later links encoders to connectors by intersecting Radeon device masks. When an LCD encoder is linked, `radeon_encoder_add_backlight()` applies module-parameter and quirk logic, initializes Atom or legacy native backlight if allowed, and falls back to ACPI video backlight registration if no native encoder is active. During modeset, active connector selection updates `active_device`, panel mode fixup copies native timing into the adjusted mode, and dual-link checks inspect connector type, HDMI status, DP sink type, ASIC generation, and pixel clock thresholds.

## State and Persistence Behavior

State is stored in DRM encoder/connector objects and Radeon extensions: `possible_clones`, `radeon_encoder->active_device`, `devices`, `native_mode`, backlight encoder state in `rdev->mode_info.bl_encoder`, and connector private DP sink data. The file also reads global `radeon_backlight`.

## Dependencies and Integration Points

The helpers depend on DRM mode objects, EDID display info, ACPI video backlight, Atom object IDs, legacy encoder code, family macros, and `radeon_display.c` connector setup. Atom/legacy mode-set files consume the helper answers when programming encoder hardware.

## Risks and Edge Cases

- Clone restrictions are conservative and family-specific; incorrect device masks from BIOS can attach wrong encoders.
- Backlight selection mixes module parameter, quirks, compile-time PPC behavior, native init success, and ACPI fallback.
- `radeon_dig_monitor_is_duallink()` assumes connector lookup succeeds; malformed topology could produce NULL dereference risk.
- HDMI 1.3 340 MHz threshold is only used for DCE6+ HDMI displays; other hardware uses 165 MHz.

## Test Signals

Test BIOS topologies with LVDS, DVI-I, HDMI, DP/eDP, TV/CV, external bridges, clone configurations on pre-R600, backlight module parameter modes, ACPI fallback, dual-link decisions around 165/340 MHz, and panel native-mode fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_encoders.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_family.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_family.h

## Purpose

`radeon_family.h` defines the canonical Radeon chip-family enumeration and packed chip flag bits shared by KMS and non-KMS/PCI-ID code. It is the low-level taxonomy used to select ASIC functions, feature gates, memory limits, display generation behavior, and driver ownership decisions.

## Important APIs, Types, and Functions

- `enum radeon_family` lists ASIC families from `CHIP_R100` through `CHIP_MULLINS`, ending with `CHIP_LAST`.
- `enum radeon_chip_flags` defines bit masks embedded with the family in PCI ID `driver_data`: `RADEON_FAMILY_MASK`, `RADEON_FLAGS_MASK`, and flags such as mobility, IGP, single CRTC, AGP, HierZ, PCIe, new memmap, PCI, IGP GART, and PX.

## Control Flow

The header has no executable control flow. Its values drive switch statements and macro predicates throughout the driver. `radeon_drv.c` reads family values from PCI ID flags for AMDGPU/Radeon arbitration. `radeon_device.c`, `radeon_display.c`, GEM/GART/fence code, and ASIC-specific files compare families to select register layouts, memory masks, DMA behavior, GART defaults, display limits, writeback behavior, and reset paths.

## State and Persistence Behavior

The family and flags are persisted in `rdev->family` and `rdev->flags` after probe decodes PCI ID `driver_data`. The constants are ABI-like internal contracts; their numeric values must remain consistent with PCI ID tables and family-name arrays.

## Dependencies and Integration Points

This header is included by `radeon_drv.h` and transitively by driver entry code. The enum ordering is mirrored by arrays such as `radeon_family_name` in `radeon_device.c` and by many range checks like `family >= CHIP_R600` or `family >= CHIP_BONAIRE`.

## Risks and Edge Cases

- Reordering enum values would break PCI ID driver data, family-name indexing, and generation range checks.
- Adding new families requires updating name arrays, support arbitration, ASIC init tables, register family macros, and feature gates.
- Flag bits share the same integer with the low-family mask; new flags must not overlap `RADEON_FAMILY_MASK`.

## Test Signals

Build-time checks should cover PCI ID table initialization and array bounds. Runtime smoke tests should verify each supported family binds to the correct ASIC hooks, display generation checks, GART defaults, DMA masks, and SI/CIK ownership behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_family.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_fbdev.c

## Purpose

`radeon_fbdev.c` implements the DRM fbdev helper backend for Radeon. It creates a pinned VRAM GEM object for fbcon, wraps it in a DRM framebuffer, maps it for CPU access, fills `fb_info`, manages runtime-PM references for fbdev opens, and destroys the pinned object when fbdev is torn down.

## Important APIs, Types, and Functions

- `radeon_fbdev_driver_fbdev_probe()` is the fbdev probe callback used by `RADEON_FBDEV_DRIVER_OPS`.
- `radeon_fbdev_create_pinned_object()` calculates pitch/size, creates a VRAM GEM object, optionally applies tiling/swap flags, pins it with legacy CRTC restrictions, and maps it.
- `radeon_fbdev_destroy_pinned_object()` unmaps, unpins, unreserves, and drops the GEM reference.
- `radeon_fbdev_fb_open()` and `radeon_fbdev_fb_release()` pair runtime PM get/put around fbdev users.
- `radeon_fbdev_fb_destroy()` finalizes the fb helper, unregisters/cleans the framebuffer, frees it, releases the pinned object, and releases the DRM client.

## Control Flow

Probe receives desired surface dimensions/depth, coerces 24 bpp to 32 bpp on AVIVO scanout hardware, converts legacy bpp/depth to a DRM format, creates the pinned object, allocates and initializes a Radeon framebuffer with `radeon_framebuffer_init()`, assigns helper funcs and fb ops, fills `fb_info`, computes the physical aperture address from BO GPU offset and VRAM aperture base, points `screen_base` at the mapped BO, clears the framebuffer with `memset_io()`, and logs mapping details.

## State and Persistence Behavior

Fbdev state is anchored in `drm_fb_helper`, `fb_info`, the DRM framebuffer, and the pinned Radeon BO. The BO remains pinned and CPU-mapped for console use until fbdev destruction. Runtime PM references persist while fbdev is open.

## Dependencies and Integration Points

The file depends on Linux fbdev, DRM fb helper, DRM GEM framebuffer helpers, Radeon GEM/BO creation, pitch alignment from `radeon_gem.c`, framebuffer initialization from `radeon_display.c`, runtime PM, and ASIC family checks. It is connected to the DRM driver through `RADEON_FBDEV_DRIVER_OPS` in `radeon_mode.h`.

## Risks and Edge Cases

- `fb_tiled` is hardcoded false but the code contains tiling paths; enabling it would need broad scanout and CPU mapping testing.
- 24 bpp on AVIVO is silently adjusted to 32 bpp.
- Legacy CRTC pinning restricts addresses to 27 bits; failures must unwind object state exactly once.
- Runtime PM open tolerates `-EACCES` but releases the PM reference for other failures.

## Test Signals

Test fbcon creation/destruction, low-VRAM format selection from driver probe, suspend/resume with fbcon, runtime PM open/release, panic/console writes to `screen_base`, legacy pre-AVIVO address restrictions, big-endian swap flag behavior, and error unwinding after create/pin/map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_fence.c

## Purpose

`radeon_fence.c` implements Radeon GPU/CPU synchronization through per-ring sequence fences integrated with Linux `dma_fence`. It emits fences into GPU rings, reads completion from writeback memory or scratch registers, wakes waiters, detects lockups, supports inter-ring sync bookkeeping, exposes debugfs diagnostics, and provides DMA-fence operations for generic reservation-object users.

## Important APIs, Types, and Functions

- `radeon_fence_emit()` allocates a `struct radeon_fence`, assigns a per-ring sequence, initializes `dma_fence`, emits the GPU fence packet, traces it, and schedules lockup checking.
- `radeon_fence_process()` and `radeon_fence_activity()` update `last_seq` from hardware and wake waiters when progress occurs.
- `radeon_fence_wait_timeout()`, `radeon_fence_wait()`, `radeon_fence_wait_next()`, and `radeon_fence_wait_empty()` wait for specific or aggregate ring progress and return `-EDEADLK` when reset is needed.
- `radeon_fence_enable_signaling()` registers waitqueue callbacks and enables software IRQs or delayed IRQ enablement.
- `radeon_fence_driver_start_ring()`, `radeon_fence_driver_init()`, `radeon_fence_driver_fini()`, and `radeon_fence_driver_force_completion()` manage per-ring fence backend state.
- `radeon_fence_need_sync()` and `radeon_fence_note_sync()` track cross-ring synchronization points.
- `radeon_fence_ops` supplies DMA-fence driver/timeline names, signaling, wait, and status callbacks.

## Control Flow

Fence emission assumes ring emission serialization by the caller. Completion can be discovered by IRQ-driven `radeon_fence_process()`, explicit polling in status checks, wait paths, or delayed lockup work. `radeon_fence_activity()` reads the current hardware sequence, merges 32-bit hardware values into 64-bit software sequence space, atomically advances `last_seq`, reschedules checks if uncompleted fences remain, and wakes the shared fence queue. If delayed work observes no progress and `radeon_ring_is_lockup()` reports a hang, it sets `rdev->needs_reset` and wakes waiters. Waiters then return `-EDEADLK`, letting higher layers trigger `radeon_gpu_reset()`.

## State and Persistence Behavior

Each ring has `rdev->fence_drv[ring]` state: scratch register, CPU/GPU writeback addresses, per-source-ring `sync_seq[]`, atomic `last_seq`, initialized flag, delayed IRQ flag, and lockup work. `rdev->fence_queue` is the shared waitqueue. Fence objects persist through DMA-fence reference counting and carry ring, sequence, owning device, and VM-update marker state.

## Dependencies and Integration Points

The file depends on Radeon ring emit helpers, IRQ enable/disable, writeback memory initialized in `radeon_device.c`, scratch registers, UVD firmware memory for UVD fences, DMA-fence, waitqueues, debugfs, tracepoints, and reset handling. GEM, TTM reservations, IB submission, page flips, suspend, and reset all consume fence APIs.

## Risks and Edge Cases

- Hardware exposes 32-bit fence values while software uses 64-bit sequences; wrap reconstruction must remain correct.
- Lockup work uses try-lock behavior around reset; delayed IRQ enablement is subtle.
- `radeon_fence_driver_force_completion()` writes the last emitted sequence to unblock waiters even if work did not really complete, appropriate only for reset/unload failure paths.
- Wait paths can return `-EDEADLK`, requiring callers to reset and retry where safe.
- Scratch register allocation/free is external-resource-sensitive.

## Test Signals

Test fence emission/completion on every active ring, writeback enabled/disabled, scratch fallback, sequence wrap, interrupt and polling completion, timeout and signal interruption, forced GPU reset via debugfs, suspend drain, unload with stuck fences, cross-ring sync bookkeeping, and DMA-fence reservation waits from GEM/page-flip paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_gart.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_gart.c

## Purpose

`radeon_gart.c` implements common internal GART management. The GART lets the GPU see scattered system pages as a contiguous GPU aperture. This file allocates and frees GART page tables in system RAM or VRAM, initializes dummy-page-backed page-entry arrays, binds/unbinds CPU pages into GPU page entries, and flushes the GPU TLB when table contents change.

## Important APIs, Types, and Functions

- `radeon_gart_table_ram_alloc()` and `radeon_gart_table_ram_free()` allocate coherent system-memory GART tables for older/internal-GART ASICs, with x86 cache attribute adjustments for selected IGP families.
- `radeon_gart_table_vram_alloc()`, `radeon_gart_table_vram_pin()`, `radeon_gart_table_vram_unpin()`, and `radeon_gart_table_vram_free()` manage VRAM-resident GART tables for PCIe/newer ASICs.
- `radeon_gart_bind()` maps pages/DMA addresses into the aperture and writes GPU page-table entries when the table is currently mapped.
- `radeon_gart_unbind()` replaces entries with the dummy page.
- `radeon_gart_init()` allocates the dummy page and software page/page-entry arrays.
- `radeon_gart_fini()` unbinds, frees arrays, clears readiness, and releases the dummy page.

## Control Flow

Initialization checks GPU page size compatibility, creates the dummy DMA page, computes CPU-page and GPU-page counts from `rdev->mc.gtt_size`, allocates `pages` and `pages_entry`, and fills all GPU entries with the dummy page. ASIC-specific code later allocates the actual hardware-visible page table in RAM or VRAM. When a VRAM table is pinned and mapped, the function restores all previously accumulated `pages_entry` values into hardware and flushes the TLB. Bind/unbind update software arrays first, optionally write the mapped table, issue a memory barrier, and flush the TLB.

## State and Persistence Behavior

Persistent GART state is in `rdev->gart`: `pages`, `pages_entry`, `num_cpu_pages`, `num_gpu_pages`, table BO or RAM pointer, table address, readiness, and table size. Entries may be updated before the table is mapped; `pages_entry` persists the intended state until pin time. The dummy page state is shared with `radeon_device.c`.

## Dependencies and Integration Points

The file depends on PCI DMA allocation, vmalloc/vcalloc, x86 `set_memory_uc/wb`, Radeon BO pin/kmap APIs, dummy page helpers, ASIC-specific `radeon_gart_get_page_entry()`, `radeon_gart_set_page()`, and `radeon_gart_tlb_flush()`. TTM calls `radeon_gart_bind()` for GTT-backed BOs.

## Risks and Edge Cases

- Bind/unbind require `rdev->gart.ready`; misuse emits WARN and fails or returns.
- Offset and page counts are not locally bounds-checked against array sizes, so callers must validate aperture ranges.
- Cache attribute changes are family-specific and must be balanced on free.
- VRAM table unpin ignores reserve failure and leaves state unchanged.
- The table can be temporarily unmapped, so software and hardware entries can diverge until repin restores them.

## Test Signals

Test GART init/fini, RAM-table and VRAM-table ASIC paths, bind/unbind of single and multi-GPU-page CPU pages, dummy-page fallback after unbind, TLB flush ordering, suspend/resume table repin, invalid uninitialized calls, cache attribute balance on x86 IGPs, and TTM GTT BO migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_gart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_gem.c

## Purpose

`radeon_gem.c` implements Radeon GEM object creation, lifetime hooks, mmap/fault handling, userptr support, domain and tiling IOCTLs, buffer busy/wait queries, GPU virtual-address mapping, dumb-buffer creation, and GEM debugfs reporting. It bridges DRM GEM APIs to Radeon BO/TTM memory management and per-file GPUVM state.

## Important APIs, Types, and Functions

- `radeon_gem_object_create()` validates size/alignment, applies the unpinned-GTT maximum, creates a Radeon BO, records the creating PID, and tracks it in `rdev->gem.objects`.
- `radeon_gem_object_funcs` wires free/open/close/export/pin/unpin/sg-table/vmap/mmap/vm-ops into DRM GEM.
- `radeon_gem_fault()` handles CPU faults under `pm.mclk_lock`, reserves the TTM BO, applies Radeon fault notification, and delegates to TTM fault handling.
- IOCTLs include GEM info/create/userptr/set-domain/mmap/busy/wait-idle/set-tiling/get-tiling/VA/op and dumb create/map.
- `radeon_gem_object_open()` and `radeon_gem_object_close()` maintain per-file VM BO references for Cayman+ acceleration.
- `radeon_gem_va_update_vm()` locks VM-related BOs with `drm_exec`, clears freed VM entries, and updates page tables opportunistically.

## Control Flow

Creation IOCTLs take `exclusive_lock`, round sizes, create BOs, export handles, and translate `-EDEADLK` through `radeon_gem_handle_lockup()` to reset/retry behavior. Userptr creation validates page alignment and flags, rejects unsafe writable non-anonymous or unregistered mappings, creates a CPU-domain BO, installs the user pointer and optional MMU notifier, optionally validates into GTT under `mmap_read_lock()`, and returns a GEM handle. VA IOCTL validates VM availability, reserved address ranges, flags, and operation, finds the per-file `bo_va`, maps or unmaps it, and updates VM page tables if possible.

## State and Persistence Behavior

GEM state persists in Radeon BOs, DRM handles, TTM reservation objects, per-file `radeon_vm` BO-VA records, userptr/MMU notifier registration, tiling flags, initial domain, and the debug list `rdev->gem.objects`. CPU fault handling temporarily holds `pm.mclk_lock` to coordinate memory-clock changes with CPU access. Many IOCTLs read current TTM placement from `robj->tbo.resource`.

## Dependencies and Integration Points

The file depends on DRM GEM/TTM helpers, dma-buf PRIME hooks from `radeon_prime.c`, Radeon BO and placement APIs, MMU notifier/userptr support, GPUVM code, `drm_exec`, reservation objects, fence/reset behavior, debugfs, and mode/fbdev paths that use dumb buffers and mmap offsets.

## Risks and Edge Cases

- Userptr writable mappings require anonymous memory plus MMU notifier registration; relaxing this risks stale DMA mappings.
- Imported/shared BOs cannot be migrated to VRAM in some paths, and userptr BOs are blocked from mmap/op operations.
- `radeon_gem_va_update_vm()` treats update errors as non-fatal, so failures may surface later at command submission.
- Object close can leak BO-VA state if reservation fails.
- Size limits depend on unpinned GTT size; large VRAM-only expectations can fail or fall back to GTT during creation.

## Test Signals

Test GEM create limits and VRAM-to-GTT fallback, PRIME import/export restrictions, CPU mmap faults, busy/wait-idle with HDP flush, userptr flag validation/MMU notifier invalidation, tiling set/get, VM map/unmap reserved-range rejection, close/open VM refcounts, reset-on-`-EDEADLK`, dumb buffer pitch/size, and debugfs object reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_gem.c -->
