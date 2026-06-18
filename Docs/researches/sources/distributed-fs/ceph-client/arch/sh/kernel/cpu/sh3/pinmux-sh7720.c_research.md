# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/pinmux-sh7720.c

## Purpose
`pinmux-sh7720.c` registers the SH7720 PFC/pinmux device when gpiolib support is enabled.

## Important APIs, Types, And Functions
It defines `sh7720_pfc_resources` for the PFC register window, and `plat_pinmux_setup()` which registers a `platform_device` named for the SH PFC driver.

## Control Flow
At `arch_initcall`, `plat_pinmux_setup()` creates the PFC platform device with its MMIO resource. The pinctrl/GPIO driver later binds and exposes pin configuration.

## State And Persistence
The file has no runtime state beyond static resources. Hardware pin function state is managed by the bound PFC driver.

## Dependencies And Integration Points
It is selected by the SH3 Makefile for SH7720 with `CONFIG_GPIOLIB`. It integrates with the SuperH PFC/pinmux subsystem and board-level pin requests.

## Risks
Wrong resource bounds prevent pinmux register access. If this object is omitted, device drivers may probe but fail to acquire required pin functions.

## Test Signals
Boot logs for PFC registration, GPIO enumeration, and successful pin configuration for SH7720 serial/USB/board peripherals provide validation.
