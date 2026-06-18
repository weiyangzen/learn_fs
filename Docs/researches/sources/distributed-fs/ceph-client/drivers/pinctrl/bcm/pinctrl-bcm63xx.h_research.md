<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.h

## Purpose
This header defines the shared data contract between the BCM63xx common pinctrl implementation and the SoC-specific BCM6318/6328/6358/6362/6368/63268 files.

## Important APIs, Types, And Functions
`struct bcm63xx_pinctrl_soc` packages the pinctrl and pinmux operation tables, pin descriptor array, pin count, and GPIO count that each SoC file passes into the common probe. `struct bcm63xx_pinctrl` is the common runtime state: device, regmap, descriptor, registered pinctrl device, and opaque SoC `driver_data`. `BCM_PIN_GROUP(n)` creates a one-line `pingroup` from a `n_pins` array. `bcm63xx_bank_pin()` maps a global pin to a 0-31 bank bit. `bcm63xx_pinctrl_probe()` is the exported common probe entry.

## Control Flow
SoC files include this header, build static `bcm63xx_pinctrl_soc` descriptors, and call `bcm63xx_pinctrl_probe()` from their platform probe. Their callbacks later retrieve `struct bcm63xx_pinctrl` with `pinctrl_dev_get_drvdata()`.

## State And Persistence
The header itself stores no state. It defines how common state and optional SoC-private state are linked for the life of the platform device.

## Dependencies And Integration Points
Depends on Linux pinctrl type definitions and platform device declarations. It provides the ABI-like local interface that keeps SoC tables separate from common GPIO/regmap setup.

## Risks
Because the structure is shared across multiple SoC files, field changes must be coordinated across all users. `BCM_PIN_GROUP` assumes a matching `n_pins` symbol exists, so table naming consistency matters.

## Test Signals
Build coverage across all BCM63xx drivers is the main signal. Runtime signals are successful retrieval of `driver_data`, correct GPIO counts, and expected group tables in debugfs pinctrl output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.h -->
