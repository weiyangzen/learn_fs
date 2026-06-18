# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/avivod.h

## Purpose
This header provides a small set of AVIVO-era display and VGA register offsets and bit masks used by Radeon display initialization, suspend/resume, power management, and low-level modeset code. It covers CRTC enable/status/update-lock registers, graphics surface address registers, VGA control registers, VGA memory control, and VGA render status masking.

## Important APIs, Types, and Functions
There are no functions or types. The exported constants include `D1CRTC_CONTROL`, `CRTC_EN`, `D1CRTC_STATUS`, `D1CRTC_UPDATE_LOCK`, `D1GRPH_PRIMARY_SURFACE_ADDRESS`, `D1GRPH_SECONDARY_SURFACE_ADDRESS`, equivalent D2 CRTC/graphics-address registers, `D1VGA_CONTROL`, `D2VGA_CONTROL`, `VGA_HDP_CONTROL`, `VGA_MEMORY_BASE_ADDRESS`, `VGA_RENDER_CONTROL`, and bit masks such as `DVGA_CONTROL_MODE_ENABLE`, `DVGA_CONTROL_TIMING_SELECT`, `DVGA_CONTROL_SYNC_POLARITY_SELECT`, `DVGA_CONTROL_OVERSCAN_TIMING_SELECT`, `DVGA_CONTROL_OVERSCAN_COLOR_EN`, `DVGA_CONTROL_ROTATE`, `VGA_MEM_PAGE_SELECT_EN`, `VGA_MEMORY_DISABLE`, `VGA_RBBM_LOCK_DISABLE`, `VGA_SOFT_RESET`, and `VGA_VSTATUS_CNTL_MASK`.

## Control Flow
The header has no executable control flow. Its values are consumed by C files that perform register reads and writes through Radeon MMIO helpers. Typical flows include disabling legacy VGA memory before ASIC initialization, checking whether CRTC pipes are enabled, saving/restoring VGA HDP control across suspend, and programming or preserving AVIVO display state.

## State and Persistence Behavior
The header stores no runtime state. It names persistent hardware registers whose contents survive across parts of the driver lifecycle until overwritten or reset by hardware/firmware. Consumers use these definitions to mutate VGA memory aperture behavior, CRTC enable state, update locks, and graphics surface addresses.

## Dependencies and Integration Points
Consumers include `radeon_pm.c`, `r600.c`, `rv770.c`, `evergreen.c`, `cik.c`, `rv515.c`, `rs600.c`, `radeon_device.c`, and display modeset code that also uses broader register headers such as `r500_reg.h`, `evergreen_reg.h`, `cikd.h`, or ASIC-specific `*d.h` files. The constants integrate with `RREG32`/`WREG32` MMIO accessors and with save/restore structures in family-specific initialization code.

## Risks
Because the header defines raw numeric offsets, any mismatch with ASIC generation or duplicate definitions in other register headers can lead to writes to the wrong display register. The short names lack the `AVIVO_` prefix used by some parallel definitions, so include ordering and naming collisions matter. These registers affect VGA memory decode and CRTC enablement, so incorrect use can blank displays, break resume restore, or expose legacy VGA aperture behavior unexpectedly.

## Test Signals
Build coverage across AVIVO/R600/RV770/Evergreen/CIK code checks macro availability and naming conflicts. Runtime signals include successful ASIC initialization with VGA memory disabled, suspend/resume preserving scanout, CRTC enabled-state detection during PM, and absence of display blanking when VGA HDP and CRTC control registers are touched.
