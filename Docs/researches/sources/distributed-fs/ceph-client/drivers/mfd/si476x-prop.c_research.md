# sources/distributed-fs/ceph-client/drivers/mfd/si476x-prop.c

## Purpose
`si476x-prop.c` exposes Silicon Labs Si476x radio chip properties through a custom regmap. It validates property IDs by chip revision and adapts regmap reads and writes to the device command protocol.

## Important APIs, Types, and Functions
`struct si476x_property_range` models inclusive property ranges. `si476x_core_element_is_in_array()` and `si476x_core_element_is_in_range()` implement table lookups. Revision predicates `si476x_core_is_valid_property_a10()`, `si476x_core_is_valid_property_a20()`, and `si476x_core_is_valid_property_a30()` layer newer property sets on older revisions. `si476x_core_is_readonly_property()` blocks writes to revision-specific read-only properties. Regmap callbacks are `si476x_core_regmap_readable_register()`, `si476x_core_regmap_writable_register()`, `si476x_core_regmap_read()`, and `si476x_core_regmap_write()`. The exported entry point is `devm_regmap_init_si476x()`.

## Control Flow
Consumers call `devm_regmap_init_si476x()`, which installs a 16-bit register and 16-bit value regmap with `REGCACHE_MAPLE`. Each regmap access consults the current `struct si476x_core` stored on the I2C client. Reads call `si476x_core_cmd_get_property()` and return the command result as the register value. Writes call `si476x_core_cmd_set_property()`.

## State and Persistence
The file has no persistent state of its own. Runtime behavior depends on `core->revision`, the I2C client data, the regmap cache, and device-resident property values.

## Dependencies and Integration Points
It depends on `linux/mfd/si476x-core.h`, I2C client data, the regmap core, and Si476x command helpers supplied by the core driver. The exported initializer is used by Si476x subdrivers that want property access via regmap.

## Risks and Edge Cases
`BUG_ON()` fires if the revision is invalid or not initialized, so callers must set revision before regmap use. Property tables are hard-coded and incomplete tables can reject valid hardware properties or expose unsupported ones. Read-only filtering is revision-sensitive.

## Test Signals
Useful checks include successful regmap creation after revision detection, readable and writable table behavior for A10/A20/A30-only properties, read-only write rejection, get/set command error propagation, and regcache behavior across repeated property access.
