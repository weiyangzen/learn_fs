# sources/distributed-fs/ceph-client/drivers/staging/nvec/Kconfig

## Purpose
Kconfig menu for the NVIDIA Embedded Controller staging MFD and its keyboard, PS/2 mouse, power-supply, and PAZ00 LED child drivers.

## Important APIs, Types, And Functions
Defines `MFD_NVEC`, `KEYBOARD_NVEC`, `SERIO_NVEC_PS2`, `NVEC_POWER`, and `NVEC_PAZ00`. `MFD_NVEC` depends on `I2C`, `GPIOLIB`, and `ARCH_TEGRA`, and selects `MFD_CORE`; child drivers depend on `MFD_NVEC` plus their subsystem core.

## Control Flow
The parent MFD option builds the EC transport. Child symbols enable platform drivers that bind to MFD cells created by `nvec.c`.

## State And Persistence
No runtime state. The selected symbols persist in the kernel configuration.

## Dependencies And Integration Points
Integrates Kbuild with MFD, input, serio, power_supply, LED class, and Tegra platforms.

## Risks
The parent is Tegra-specific and staging-only. Enabling children without hardware support yields unused modules. The child modules depend on the parent creating matching platform devices.

## Test Signals
Kconfig dependency checks, module builds for each selected symbol, and parent MFD probe creating cells named `nvec-kbd`, `nvec-mouse`, `nvec-power`, and `nvec-paz00`.
