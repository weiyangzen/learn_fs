# sources/distributed-fs/ceph-client/drivers/mfd/hi6421-pmic-core.c

## Purpose
`hi6421-pmic-core.c` is the MMIO MFD parent for HiSilicon HI6421 and HI6421V530 PMICs. It creates a regmap over the PMIC register aperture, applies a HI6421 over-current debounce setting, and registers the correct regulator child.

## Important APIs, Types, and Functions
`hi6421_regmap_config` defines 32-bit bus addresses with 4-byte stride and 8-bit values. `of_hi6421_pmic_match` maps compatibles to `enum hi6421_type`. `hi6421_pmic_probe()` performs all setup. `hi6421_devs[]` and `hi6421v530_devs[]` select the regulator child name for each PMIC type.

## Control Flow
Probe gets match data, allocates `struct hi6421_pmic`, maps the MMIO resource, initializes a clockless MMIO regmap, stores driver data, switches by PMIC type, writes over-current debounce/enable bits for HI6421, selects the child cell list, and registers children with `devm_mfd_add_devices()`.

## State and Persistence
Per-device state is the PMIC regmap. Hardware register state includes HI6421 OCP debounce/autostop bits. No explicit persistence or IRQ state is managed by this file.

## Dependencies and Integration Points
The file depends on OF matching, platform MMIO resources, regmap-mmio, MFD core, and Hi6421 PMIC register macros. It integrates mainly with regulator child drivers.

## Risks and Edge Cases
Unknown match data fails probe. OCP debounce setup ignores the return value from `regmap_update_bits()`, so a failed write does not abort. There is no IRQ support here; regulator faults must be handled elsewhere or not at all.

## Test Signals
Probe both compatibles, verify regmap bus address translation, confirm HI6421 OCP debounce bits are written, ensure the correct regulator child appears, and inject MMIO/regmap init failures.
