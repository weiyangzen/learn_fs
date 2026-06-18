# sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/Makefile

## Purpose
The Makefile connects the Allwinner A10 EMAC driver to kbuild.

## Important build rules
- `obj-$(CONFIG_SUN4I_EMAC) += sun4i-emac.o` builds the platform driver when selected.

## Control flow and integration
kbuild includes the single driver object based on `CONFIG_SUN4I_EMAC`. There are no composite objects in this directory.

## State and persistence behavior
No runtime state exists. It only controls build outputs.

## Dependencies and integration points
The rule depends on the Kconfig symbol and the `sun4i-emac.c` source file.

## Risks and edge cases
Renaming the config or source requires updating this rule. Otherwise the file is intentionally low risk.

## Test signals
Build with `SUN4I_EMAC=y`, `m`, and `n` and confirm the expected object/module inclusion.
