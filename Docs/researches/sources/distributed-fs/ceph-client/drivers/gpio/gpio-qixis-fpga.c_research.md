<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-qixis-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-qixis-fpga.c

## Purpose
Thin gpio-regmap adapter for NXP Layerscape QIXIS FPGA/CPLD 8-bit registers, with board-specific fixed-output masks and status-style input bits.

## Important APIs, types, and functions
`struct qixis_cpld_gpio_config` stores output-capable lines. Probe reads `reg`, obtains a parent regmap or creates an MMIO regmap, fills `gpio_regmap_config`, converts the fixed output mask, and registers.

## Control flow
If the parent exposes a regmap, DT `reg` is used as the data/set base. Otherwise probe maps its own resource and creates an 8-bit regmap with base zero. `fixed_direction_output` defines which lines are outputs.

## State and persistence behavior
No private mutable state remains after registration. Values and direction capability live in the underlying register and match data. No PM handling.

## Dependencies and integration points
Uses platform/OF match data, optional parent regmap, optional direct MMIO, regmap, and gpio-regmap.

## Risks and edge cases
`reg` is mandatory. The fixed output bitmap is local to probe, so gpio-regmap must consume it safely. Bad match data can expose status bits as outputs.

## Test signals
Both compatibles, parent-regmap and fallback-MMIO paths, register offset, fixed direction, and gpio-regmap read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-qixis-fpga.c -->
