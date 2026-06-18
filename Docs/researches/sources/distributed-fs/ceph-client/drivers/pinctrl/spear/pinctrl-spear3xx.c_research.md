<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.c

## Purpose
This file provides the shared SPEAr3xx pin definitions, common pin groups, common functions, and GPIO fallback mappings reused by SPEAr300, SPEAr310, and SPEAr320 variant drivers.

## Important APIs, Types, And Data
- `spear3xx_pins[]` publishes pins 0..101 using `SPEAR_PIN_0_TO_101`.
- Common groups include FIRDA, I2C0, SSP chip selects, SSP0, MII0, GPIO0 pins 0..5, UART0 modem, UART0, and timer groups.
- For each common group, a `struct spear_pingroup` describes pins and a `struct spear_function` maps the exported function name to group strings.
- Initial group mux registers use `.reg = -1`; variant drivers later call `pmx_init_addr()` to set the actual `PMX_CONFIG_REG`.
- `DEFINE_MUXREG()` and `GPIO_PINGROUP()` create GPIO fallback mux records for common groups.
- `spear3xx_machdata` contains common pins and common GPIO pingroups; variant drivers fill the groups/functions and mode data.

## Control Flow And Integration
This file has no platform driver. It is linked as shared data for SPEAr3xx variant drivers. At variant probe time, SPEAr300/310/320 set `spear3xx_machdata.groups`, `functions`, mode fields, and register offsets, then call `spear_pinctrl_probe()`. The common SPEAr core later consumes the group/function arrays for pinctrl operations and the GPIO pingroup array for GPIO request mux handling.

## State And Persistence
Static common tables are process-global and reused. The externally visible `spear3xx_machdata` is mutable because each variant probe completes it with SoC-specific arrays and register addresses. Hardware persistence is indirect: common groups program the variant's mux register once their `.reg` placeholders have been initialized.

## Dependencies
It depends on Linux pinctrl descriptors and local `pinctrl-spear3xx.h`/`pinctrl-spear.h` macros. It depends on variant drivers to finish machdata setup before registration.

## Risks And Review Notes
- Common data is mutable and shared; tests that instantiate multiple SPEAr3xx variants in one kernel lifetime should be careful.
- `.reg = -1` placeholders are invalid until `pmx_init_addr()` runs. Missing initialization would produce bad register writes.
- Function group matching is string-based; variant files must preserve exact common group names.
- Common GPIO fallback entries assume clearing a function bit returns the pad to GPIO. That polarity must remain valid for every variant that reuses them.

## Test Signals
Compile all SPEAr3xx variants. For each variant, confirm common groups and functions are registered and that register addresses in common mux entries are updated to the SoC-specific `PMX_CONFIG_REG`. Exercise common functions FIRDA, I2C0, SSP0, MII0, UART0, timers, and GPIO request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.c -->
