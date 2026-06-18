# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon.h

## Purpose

`radeon.h` is the central internal interface for the Radeon DRM kernel driver. It defines the main driver state object, subsystem data structures, hardware abstraction callback tables, register access macros, module parameter declarations, and cross-file prototypes for memory management, command submission, rings, fences, virtual memory, power management, display, media, ACPI, audio, and ASIC-specific operations.

The header is the contract that binds the Radeon KMS driver together: most implementation files include it to access `struct radeon_device`, subsystem helpers, ASIC dispatch macros, and shared constants.

## Important APIs, types, and definitions

Important declarations include module parameters, ring indices, timeouts, reset flags, clock/power gating flags, VM limits, GPU page flags, writeback offsets, cursor sizes, and PCIe speed values.

Core state types include `struct radeon_device`, `union radeon_asic_config`, `struct radeon_asic`, `struct radeon_asic_ring`, BO/GEM/TTM/GART/MC types, fence/semaphore/sync/IB/ring/CS parser types, VM types, PM/DPM/clock-voltage tables, UVD/VCE/audio structs, IRQ status structs, and ACPI `radeon_atif`/`radeon_atcs` structs.

Important inline helpers and macros include `r100_mm_rreg`, `r100_mm_wreg`, `RREG*`, `WREG*`, `REG_SET`, `REG_GET`, indirect register access macros, `rdev_to_drm`, `to_radeon_fence`, `radeon_get_ib_value`, `radeon_fence_later`, `radeon_fence_is_earlier`, `radeon_ring_write`, ASIC family predicates, and high-level ASIC dispatch macros such as `radeon_init`, `radeon_ring_test`, `radeon_copy`, `radeon_set_backlight_level`, and `radeon_dpm_enable`.

## Control flow and lifecycle

The header documents the expected initialization flow: `radeon_device_init` performs common object/mutex setup; ASIC init configures memory layout and fatal one-time hardware setup; ASIC startup brings acceleration online after memory-controller setup. Runtime behavior flows through ASIC dispatch tables: generic code calls `radeon_init`, ring callbacks, VM callbacks, IRQ/display/copy/PM/DPM callbacks, and ASIC-specific implementation files program hardware through `rdev`, register helpers, and generation-specific headers.

Inline behavior matters: MMIO helpers select direct versus slow indexed access, `radeon_ring_write` updates write pointer/free counters and reports ring overrun, and fence comparison helpers require same-ring fences.

## State and persistence behavior

`struct radeon_device` is persistent per GPU and owns nearly all driver state until teardown: DRM/PCI identity, ASIC family/configuration, MMIO mappings and locks, BIOS state, clock/MC/GART/mode/scratch/doorbell/MM state, fences, rings, IRQs, GEM/TTM, PM/DPM, UVD/VCE/audio, firmware pointers, work items, ACPI notifier and ATIF/ATCS data, VM manager, reset counters, and pinned-memory accounting.

Userspace-visible state is mediated through GEM BOs, VM mappings, command submission, fences, PRIME sharing, tiling metadata, HyperZ/CMASK ownership, and media handles. Hardware-visible state is mirrored in ring pointers, writeback offsets, page tables, scratch registers, IRQ masks, clock/power state, display/audio state, and firmware memory.

## Dependencies and integration points

External dependencies include DRM core, GEM, TTM, DMA fences, DRM execution helpers, DRM suballocation, audio component binding, AGP, PCI, firmware loading, workqueues, wait queues, MMU notifiers, ACPI, and MMIO APIs. Internal dependencies include `radeon_family.h`, `radeon_mode.h`, `radeon_reg.h`, `clearstate_defs.h`, `radeon_object.h`, VBIOS/ATOM helpers, ASIC implementation files, display encoder code, command parser code, memory manager code, UVD/VCE code, power-management code, and ACPI code.

The ASIC callback table is the major integration point. Generic code should call dispatch macros and shared helpers, while per-family files populate `struct radeon_asic` and `struct radeon_asic_ring`.

## Risks and edge cases

This is a high-blast-radius interface. Struct layout, callback signatures, constants, and macros affect most Radeon files. Function-like macros assume valid `rdev` and callback pointers. Ring/fence helpers depend on correct ring ownership. MMIO direct/indirect selection depends on address-space knowledge. `CONFIG_ACPI`, `CONFIG_AGP`, and `CONFIG_MMU_NOTIFIER` alter available APIs through stubs. Many fields are concurrency-sensitive and require the locks, reservations, or atomics implied by their subsystem.

## Test signals

Validation should compile with ACPI/AGP/MMU-notifier variants; boot representative ASIC generations; exercise device init, reset, suspend/resume, GEM/TTM, command submission, IB/ring tests, fence waits, VM bind/update/unbind, PRIME/userptr, display modesetting, page flips, vblank, HPD, backlight, HDMI/DP audio, UVD/VCE, runtime PM, and lockdep/KASAN/KCSAN where available.
