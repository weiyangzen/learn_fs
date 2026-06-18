# sources/distributed-fs/ceph-client/drivers/mfd/hi6421-spmi-pmic.c

## Purpose
`hi6421-spmi-pmic.c` is the SPMI MFD parent for the HiSilicon Hi6421v600 PMIC. It creates an extended SPMI regmap and registers IRQ and regulator children.

## Important APIs, Types, and Functions
`hi6421v600_devs[]` lists `hi6421v600-irq` and `hi6421v600-regulator` children. `regmap_config` uses 16-bit registers, 8-bit values, full 0xffff range, and `fast_io`. `hi6421_spmi_pmic_probe()` initializes regmap and children. `hi6421_spmi_pmic_driver` binds to `hisilicon,hi6421-spmi`.

## Control Flow
Probe creates a regmap with `devm_regmap_init_spmi_ext()`, stores it as driver data for children, and registers the two MFD children. Failures from child registration are logged and returned.

## State and Persistence
The regmap pointer is device driver data. PMIC state is in SPMI registers and owned by child drivers. No local persistence, IRQ handling, or power management is implemented.

## Dependencies and Integration Points
It depends on the SPMI framework, regmap SPMI extended accessors, MFD core, and child drivers for Hi6421v600 IRQ and regulators.

## Risks and Edge Cases
The parent has no hardware ID validation; compatible matching is trusted. Child drivers must agree on using the parent driver data as a regmap. `fast_io` assumes low-latency serialized access is safe for this bus/provider combination.

## Test Signals
Validate SPMI regmap reads/writes across 16-bit addresses, child creation, child access to parent regmap, OF compatible binding, and failure propagation when regmap or child registration fails.
