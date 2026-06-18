# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_arm_c9.h

## Purpose
Provides ARM Cortex-A9 BCMA DMU/CRU register offsets and bit masks for USB PLL and strap control.

## Important APIs, types, and functions
- Defines `BCMA_DMU_CRU_USB2_CONTROL` and masks/shifts for USB PLL NDIV/PDIV.
- Defines `BCMA_DMU_CRU_CLKSET_KEY`.
- Defines `BCMA_DMU_CRU_STRAPS_CTRL` bits for USB3 and 4-byte strap behavior.

## Control flow and state
No functions are declared. Platform or BCMA ARM code reads and writes DMU registers using these constants during SoC initialization or USB/strap configuration.

## State and persistence behavior
State is hardware register state. Strap fields may reflect boot-time configuration; writes to clock/PLL controls affect live hardware.

## Dependencies and integration points
Included by `bcma.h`; used by ARM-based Broadcom SoC initialization and USB clock setup.

## Risks
Wrong PLL mask/shift use can misprogram USB clocks. Strap bits may be read-only or boot-sensitive depending on chip, so callers must verify hardware revision.

## Test signals
Boot on supported ARM BCMA SoCs, verify USB2/USB3 enumeration, confirm strap decoding, and test clock setup against datasheet register dumps.
