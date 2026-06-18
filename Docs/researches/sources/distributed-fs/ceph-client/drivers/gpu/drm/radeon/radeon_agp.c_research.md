# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_agp.c

## Purpose

`radeon_agp.c` implements Radeon AGP initialization, resume, suspend, and teardown. When `CONFIG_AGP` is enabled, it acquires the kernel AGP backend, applies known hostbridge/GPU/subsystem AGP mode quirks, enables a safe AGP transfer mode, and maps the AGP aperture into Radeon memory-controller GTT fields. When AGP support is absent, the public init path becomes a no-op.

The file exists to keep legacy Radeon AGP systems usable despite old bridge and laptop quirks, while allowing the rest of the driver to treat the resulting aperture as the GTT window.

## Important APIs, Types, And Functions

`struct radeon_agpmode_quirk` describes one compatibility override: hostbridge vendor/device, Radeon chip vendor/device, subsystem vendor/device, and forced default AGP mode. `radeon_agpmode_quirk_list` is a sentinel-terminated table of old Intel, VIA, ATI, ASRock, IBM, Dell, Sony, Acer, Asus, and other combinations that need AGP 1x, 2x, 4x, or 8x for stability.

`radeon_agp_head_init(struct drm_device *dev)` allocates and populates `struct radeon_agp_head` from the kernel AGP bridge info. It tries `agp_find_bridge()` first, falls back to `agp_backend_acquire()`, copies `agp_kern_info`, rejects `NOT_SUPPORTED`, initializes the memory list, and records aperture capabilities such as `cant_use_aperture`, `page_mask`, and base address.

The private helpers `radeon_agp_head_acquire()`, `radeon_agp_head_release()`, `radeon_agp_head_enable()`, and `radeon_agp_head_info()` wrap AGP backend ownership, mode enabling, and information transfer into Radeon-local structures. The public lifecycle consists of `radeon_agp_init()`, `radeon_agp_resume()`, `radeon_agp_suspend()`, and `radeon_agp_fini()`.

## Control Flow

`radeon_agp_init()` is the central path. It acquires the AGP backend, queries AGP info, rejects apertures smaller than 32 MiB, computes a default transfer mode from the intersection of host mode and Radeon AGP status, applies table-driven quirks, validates or substitutes the module parameter `radeon_agpmode`, clears the AGP mode bits, sets the chosen 1x/2x/4x or v3 4x/8x bit, disables fast writes, enables AGP through the backend, then initializes `rdev->mc.agp_base`, `gtt_size`, `gtt_start`, and `gtt_end`.

For older pre-R200 chips, successful init also sets a workaround bit pattern in `RADEON_AGP_CNTL`. Error paths release the AGP backend after failed info retrieval, too-small apertures, or enable failures. `radeon_agp_resume()` simply re-runs init when `RADEON_IS_AGP` is set. `radeon_agp_suspend()` delegates to `radeon_agp_fini()`, which releases the backend if acquired.

## State And Persistence Behavior

The file mutates `rdev->agp` state (`bridge`, `agp_info`, `acquired`, `enabled`, `mode`, list head and aperture metadata) and `rdev->mc` GTT placement (`agp_base`, `gtt_size`, `gtt_start`, `gtt_end`). It also reads and may overwrite the global/module-level `radeon_agpmode` when an illegal user-provided value is replaced with the computed default.

The AGP backend state is persistent across the active driver lifetime but must be released on suspend/fini and reacquired on resume. Hardware register state is not assumed persistent; resume calls the full init path.

## Dependencies And Integration Points

The file depends on Linux PCI and AGP backend APIs, DRM device wrappers, Radeon device state from `radeon.h`, Radeon register access macros, and AGP register constants from Radeon headers. It integrates with `radeon_asic.c` because AGP can be disabled elsewhere and replaced by PCI/PCIe GART callbacks, while this file handles the true AGP aperture path.

The memory-controller setup feeds Radeon GART/TTM memory management. The chosen AGP mode depends on hostbridge capabilities, Radeon status registers for older chips, the user `radeon.agpmode` parameter, and subsystem-specific quirks gathered from historical bug reports.

## Risks And Edge Cases

Legacy hardware compatibility is the main risk. Too aggressive an AGP mode can cause hangs, while too conservative a mode hurts performance. The quirk table is exact-match and subsystem-sensitive, so a near-identical board not in the table may still fail. The code intentionally disables fast writes, reflecting known instability risk.

There are subtle ownership risks around backend acquire/release on error paths and resume. The 32 MiB aperture minimum avoids unusable apertures but can disable AGP on firmware with small aperture settings. Chips bridged from AGP to PCIe skip the AGP status register and trust the host mode, so incorrect bridge reporting can affect mode selection.

## Test Signals

Regression signals include boot logs showing AGP acquisition, selected AGP mode, aperture size, and GTT address range; suspend/resume with AGP reinitialization; module-parameter tests for legal and illegal `radeon.agpmode`; known-quirk hardware booting at the forced mode; failure handling for no bridge, unsupported chipset, and tiny aperture; and GPU memory stress tests using GTT/TTM on AGP systems. Watch for `Unable to acquire AGP`, `Unable to get AGP info`, `AGP aperture too small`, and `Unable to enable AGP` messages.
