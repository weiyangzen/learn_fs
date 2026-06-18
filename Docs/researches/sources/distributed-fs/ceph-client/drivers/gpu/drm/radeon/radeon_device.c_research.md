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
