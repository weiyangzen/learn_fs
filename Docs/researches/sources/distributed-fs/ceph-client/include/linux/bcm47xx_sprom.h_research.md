# sources/distributed-fs/ceph-client/include/linux/bcm47xx_sprom.h

## Purpose
Declares BCM47xx SPROM filling and fallback registration helpers used to populate shared SSB/BCMA SPROM data from board-specific NVRAM sources.

## Important APIs, types, and functions
- `bcm47xx_fill_sprom()` fills an `ssb_sprom` using an optional prefix and fallback flag.
- `bcm47xx_sprom_register_fallbacks()` registers fallback callbacks for devices lacking physical SPROM contents.
- Disabled-config stubs do nothing or return `-ENOTSUPP`.

## Control flow and state
Platform initialization registers fallbacks, then bus/device code asks for SPROM contents. The fill helper maps NVRAM key prefixes into SPROM fields when support is compiled in.

## State and persistence behavior
SPROM data reflects persistent board calibration/configuration but is represented in memory in `struct ssb_sprom`. This header does not expose writeback to persistent storage.

## Dependencies and integration points
Depends on errno/types/vmalloc and forward-declares `struct ssb_sprom`. Integrated with SSB/BCMA bus probing and BCM47xx NVRAM.

## Risks
Incorrect prefix or fallback selection can apply wrong board calibration data to a wireless device. Callers must handle `-ENOTSUPP` when platform support is absent.

## Test signals
Test SPROM population from representative NVRAM sets, fallback registration with missing physical SPROM, disabled support builds, and multi-device prefix selection.
