
# sources/distributed-fs/ceph-client/include/linux/platform_data/hsmmc-omap.h

## Purpose
This header defines OMAP HSMMC platform data and device attributes for MMC/SD/eMMC controllers.

## Important APIs And Types
Flags describe dual-voltage support, broken multiblock read erratum, and missing software wakeup. `struct omap_hsmmc_dev_attr` stores controller flags. `struct omap_hsmmc_platform_data` includes back-link device, max bus frequency, controller flags, register offset deviation, MMC capability and PM capability masks, nonremovable and regulator-off quirks, feature bits for PBIAS/reset/HSPE support, version string, name, and OCR mask.

## Control Flow, State, And Persistence
No code flow is defined here. The MMC host driver consumes the platform data during probe, sets caps/OCR/frequency limits, applies errata, and manages regulator behavior. Runtime state is MMC host/card state and hardware registers.

## Dependencies And Integration Points
It integrates OMAP platform data with the Linux MMC core, regulators/PBIAS, PM wake capabilities, and hardware-module attributes.

## Risks And Test Signals
Risks include advertising unsupported voltage, missing broken-multiblock workaround, disabling eMMC regulator incorrectly, and wrong register offset. Test signals include card detect/probe, single and multiblock transfers, voltage switching, suspend/resume wake behavior, eMMC power sequencing, and max-frequency enforcement.
