# sources/distributed-fs/ceph-client/drivers/input/mouse/Kconfig

## Purpose
`drivers/input/mouse/Kconfig` defines the build-time configuration menu for Linux mouse and touchpad drivers. It gates PS/2 protocol extensions, serial/USB/I2C/SMBus/GPIO/platform mouse drivers, and architecture-specific mouse support.

## Important APIs, Types, and Functions
The top-level `menuconfig INPUT_MOUSE` controls visibility but does not itself affect the kernel. Key symbols include `MOUSE_PS2` and its protocol extensions (`ALPS`, `BYD`, `LOGIPS2PP`, `SYNAPTICS`, `ELANTECH`, `TRACKPOINT`, etc.), companion SMBus helpers, `MOUSE_SERIAL`, Apple USB touchpad drivers, `MOUSE_CYAPA`, `MOUSE_ELAN_I2C` plus transport suboptions, Amiga/Atari/RiscPC/DEC/GPIO/Maple/Synaptics variants. Dependencies and selects wire these options to SERIO, I2C, USB, DMI, platform architecture, and helper libraries.

## Control Flow
There is no runtime flow. Kconfig evaluation exposes options under `INPUT_MOUSE`, enforces dependencies, applies defaults, and sets `CONFIG_*` symbols. Kbuild then includes or omits driver objects/modules according to the selected symbols. Boolean PS/2 protocol extensions are built into the `psmouse` driver when enabled.

## State and Persistence Behavior
The file persists configuration state in `.config`. Tristate options determine built-in/module/disabled driver builds; boolean extension options alter compiled feature sets inside composite drivers. It has no runtime driver state.

## Dependencies and Integration Points
The menu integrates the input subsystem with SERIO, I8042/GSC PS/2 controllers, I2C/SMBus, USB host support, architecture symbols (`AMIGA`, `ATARI`, `ARCH_ACORN`, `MAPLE`), DMI, hypervisor guest support, and helper selections such as `CRC_ITU_T`, `SERIO_LIBPS2`, and `MOUSE_PS2_SMBUS`.

## Risks and Edge Cases
Defaults enable many PS/2 extensions, so build/test matrices must cover both expert-disabled and default-enabled combinations. Transport suboptions such as `MOUSE_ELAN_I2C_I2C`/`SMBUS` can create partially enabled drivers if dependencies change. `select` statements force lower-level support and can expose unmet dependency bugs. Help text includes legacy URLs and may lag current userspace recommendations.

## Test Signals
Test Kconfig resolution for `y/m/n` where applicable, dependency-disabled visibility, allmodconfig/allnoconfig/randconfig builds, PS/2 extension combinations, I2C/USB dependency matrices, architecture-specific build coverage, and expected module names such as `psmouse`, `sermouse`, `appletouch`, `bcm5974`, `cyapa`, `elan_i2c`, `gpio_mouse`, and `synaptics_usb`.
