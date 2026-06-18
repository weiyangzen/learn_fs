# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/Makefile

## Purpose
This Makefile maps Microchip pinctrl Kconfig symbols to compiled driver objects.

## Important APIs, Types, and Entries
- `obj-$(CONFIG_PINCTRL_PIC64GX) += pinctrl-pic64gx-gpio2.o`
- `obj-$(CONFIG_PINCTRL_POLARFIRE_SOC) += pinctrl-mpfs-iomux0.o`
- `obj-$(CONFIG_PINCTRL_POLARFIRE_SOC) += pinctrl-mpfs-mssio.o`

## Control Flow
There is no runtime control flow. Kbuild includes objects based on the evaluated `CONFIG_*` variables.

## State and Persistence
Build state comes from the kernel configuration. No runtime state is defined here.

## Dependencies and Integration Points
It integrates the local Kconfig symbols with Kbuild and the C driver files in the same directory.

## Risks
`CONFIG_PINCTRL_POLARFIRE_SOC` always builds both PolarFire pinctrl objects together; platforms needing only one still compile both. Object names must stay synchronized with source filenames and Kconfig symbol names.

## Test Signals
Use `make drivers/pinctrl/microchip/` or full kernel builds with each symbol toggled. Confirm the object list matches the Kconfig selections.
