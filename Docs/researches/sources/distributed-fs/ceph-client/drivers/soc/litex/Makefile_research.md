
# sources/distributed-fs/ceph-client/drivers/soc/litex/Makefile

## Purpose
Builds the LiteX SoC controller driver when selected.

## Important APIs, Types, and Functions
No runtime APIs. Rule: `obj-$(CONFIG_LITEX_SOC_CONTROLLER) += litex_soc_ctrl.o`.

## Control Flow
Kernel build includes the controller object according to the tristate symbol.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes `CONFIG_LITEX_SOC_CONTROLLER`.

## Risks
The SPDX tag uses `SPDX-License_Identifier`, matching the Kconfig typo.

## Test Signals
Build with controller enabled as module/built-in and license tooling checks.
