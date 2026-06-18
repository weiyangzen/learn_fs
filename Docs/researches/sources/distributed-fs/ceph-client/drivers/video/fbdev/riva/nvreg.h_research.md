# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nvreg.h

## Purpose
`nvreg.h` is a legacy macro layer for NVIDIA register bitfields and device register access. In this kernel driver it primarily supplies bitfield helpers used by `fbdev.c` timing construction, while much of the older direct `nvCONTROL`/port-I/O macro surface remains as compatibility baggage from XFree86-era code.

## Important APIs, types, and functions
- `BITMASK`, `MASKEXPAND`, `SetBF`, `GetBF`, and `MaskAndSetBF` implement compile-time bitfield packing/unpacking for mask expressions such as `8:8`.
- `DEVICE_*` and per-device wrappers (`PFB_*`, `PRAMDAC_*`, `PFIFO_*`, etc.) address an external `nvCONTROL` aperture.
- `CRTC_*`, `PCRTC_*`, and `SR_*` wrap legacy port I/O.
- `NVChipType` and `GetChipType()` are declared but not used by the modern fbdev files in this subset.

## Control flow
There is no normal runtime control flow beyond macro expansion. `fbdev.c` uses `SetBF`/`GetBF` through local wrappers to construct overflow bits in VGA CRTC timing registers and extended screen/horizontal fields.

## State and persistence behavior
No owned runtime state exists, but the macros can read and write hardware registers when used. The declared global `nvCONTROL` would be a process/global MMIO base in older code; this subset's active RIVA paths use `NV_RD32`/`NV_WR32` from `riva_hw.h` instead.

## Dependencies and integration points
Integration is mostly compile-time: `fbdev.c` includes this header for bitfield helpers, and older register names may still document intended hardware blocks. It depends on the C preprocessor's treatment of `x:y` macro arguments and on architecture port I/O helpers if the legacy macros are ever used.

## Risks and test signals
Risks include confusing dead/legacy macros, typo `PTIEMR` in `PTIMER_Val`, duplicate `PMC_*` definitions, unsafe side effects in assignment macros, and portability issues with raw port I/O. Test signals are clean builds with all call sites, correct computed CRTC overflow fields in mode tests, and static analysis confirming unused legacy macros do not hide active bugs.
