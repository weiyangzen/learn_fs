# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh.c

## Purpose
Implements the G200EH server variant, including shared EH register defaults, 33.333 MHz PLL search, PLL lock programming sequence, BMC-aware VGA pipeline, and device factory.

## Important APIs, types, and functions
- `mgag200_g200eh_init_registers()` is also reused by EH3/EH5.
- `mgag200_g200eh_pixpllc_atomic_check()` searches m/n/p for a 400-800 MHz VCO.
- `mgag200_g200eh_pixpllc_atomic_update()` powers down/reprograms the EH PLL, selects PLL output, re-enables the clock, and polls `MGAREG_VCOUNT` for lock.
- `mgag200_g200eh_device_create()` creates the EH DRM device.

## Control flow
Atomic check stores PLL values in CRTC state. Atomic enable uses the common CRTC helper, which calls the EH PLL updater after mode register programming. The update loop tries up to 33 programming attempts and treats vertical-count progress as lock indication.

## State and persistence
Device info caps modes at 2048x2048 and 37.5 GiB/s-style bandwidth units as used by the driver. PLL values persist in CRTC state and hardware DAC PLL registers. The BMC-aware VGA connector can signal BMC coordination based on `sync_bmc`, which is false for this info table.

## Dependencies and integration points
Reuses shared mgag200 KMS helpers, BMC-aware VGA output initialization, and shared EH init/update routines for later EH variants.

## Risks
PLL locking uses polling heuristics rather than a direct lock bit. The update function does not return an error if it fails to observe lock. EH register defaults skip specific DAC ranges, so changes can disturb variant compatibility.

## Test signals
Modeset stability on G200EH, debug/trace inspection of PLL retries, EDID fallback behavior, and successful output after repeated mode switches are useful signals.
