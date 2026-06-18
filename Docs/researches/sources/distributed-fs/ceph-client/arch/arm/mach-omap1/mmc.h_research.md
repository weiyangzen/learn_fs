<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mmc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mmc.h

## Purpose
Provides OMAP1 MMC controller constants and the optional `omap1_init_mmc()` declaration used by board files.

## Important APIs, Types, and Functions
Defines controller counts, base addresses, register size, and a real or stub `omap1_init_mmc(struct omap_mmc_platform_data **, int)` depending on `CONFIG_MMC_OMAP`.

## Control Flow
No runtime flow in the header. Board code calls `omap1_init_mmc()` and either registers controllers in enabled builds or compiles to a no-op when the driver is absent.

## State and Persistence Behavior
No state. Runtime state is owned by the implementation and MMC core.

## Dependencies and Integration Points
Depends on `linux/mmc/host.h` and `linux/platform_data/mmc-omap.h`; consumers rely on the base/size constants for OMAP1 controller registration.

## Risks
The no-op stub can hide missing MMC support. Fixed controller counts differ between OMAP15xx and OMAP16xx, so board code must pass the right number of platform-data entries.

## Test Signals
Build with `CONFIG_MMC_OMAP` enabled and disabled. On OMAP16xx, verify both base addresses can be registered when requested; on OMAP15xx, verify only one controller is exposed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mmc.h -->
