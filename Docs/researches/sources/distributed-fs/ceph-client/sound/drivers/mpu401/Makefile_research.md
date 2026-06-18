# sources/distributed-fs/ceph-client/sound/drivers/mpu401/Makefile

## Purpose

This Makefile builds the ALSA MPU-401 UART support modules. It separates the generic platform/PnP front-end from the reusable UART-mode rawmidi implementation.

## Important APIs, Types, and Functions

`snd-mpu401-y := mpu401.o` defines the generic MPU-401 card driver module. `snd-mpu401-uart-y := mpu401_uart.o` defines the reusable UART helper module. `obj-$(CONFIG_SND_MPU401_UART)` and `obj-$(CONFIG_SND_MPU401)` include the helper and front-end modules according to Kconfig.

## Control Flow

Kbuild composes each module object from its source object and includes it when the matching config symbol is enabled. Since `SND_MPU401` selects `SND_MPU401_UART`, normal front-end builds include both modules.

## State and Persistence Behavior

No runtime state exists. Build state is the generated built-in object or loadable modules selected by Kconfig.

## Dependencies and Integration Points

It depends on `sound/drivers/Kconfig` symbols and Kbuild. The modules produced here provide `snd_mpu401` and `snd_mpu401_uart`, with the front-end calling the exported `snd_mpu401_uart_new()` helper.

## Risks

Build risks are symbol/object mismatches and missing helper inclusion if Kconfig select relationships change. Because the UART helper exports APIs for other drivers, changing module boundaries can affect link dependencies.

## Test Signals

Build `CONFIG_SND_MPU401_UART=m`, `CONFIG_SND_MPU401=m`, and built-in variants; verify both modules are generated and that `snd-mpu401` resolves `snd_mpu401_uart_new`.
