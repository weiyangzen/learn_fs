# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/Makefile

## Purpose
Builds the Marvell PXA pinctrl objects selected by Kconfig.

## Important APIs, Types, And Functions
`CONFIG_PINCTRL_PXA25X` builds `pinctrl-pxa2xx.o` plus `pinctrl-pxa25x.o`; `CONFIG_PINCTRL_PXA27X` builds `pinctrl-pxa2xx.o` plus `pinctrl-pxa27x.o`.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` assignments and links the common implementation with the selected chip-specific table/probe file.

## State And Persistence
This is build-time state only. It does not persist runtime data.

## Dependencies And Integration Points
Integrates with `pxa/Kconfig`, the common exported `pxa2xx_pinctrl_init()` symbol, and the chip-specific platform drivers.

## Risks
If both chip drivers are built into the same linked object scope, `pinctrl-pxa2xx.o` appears in both object lists; Kbuild normally handles duplicate object references, but changes should preserve one common implementation for both variants.

## Test Signals
Build `CONFIG_PINCTRL_PXA25X=m`, `CONFIG_PINCTRL_PXA27X=m`, and both enabled together to verify object selection and symbol resolution.
