# sources/distributed-fs/ceph-client/drivers/mfd/vexpress-sysreg.c

## Purpose
`vexpress-sysreg.c` exposes ARM Versatile Express system-register subfunctions as MFD children. The sysreg block is a mixed MMIO register area containing LEDs, MMC control pseudo-GPIOs, flash control pseudo-GPIOs, and system configuration registers.

## Important APIs, Types, And Functions
Static software nodes define labels and GPIO counts for `sys_led`, `sys_mci`, and `sys_flash`. `vexpress_sysreg_cells[]` creates three `basic-mmio-gpio` cells and one `vexpress-syscfg` cell with fixed offsets. The only active function is `vexpress_sysreg_probe()`, plus OF match table and platform driver registration.

## Control Flow
Probe obtains the first memory resource, maps the full sysreg range with `devm_ioremap()`, creates a duplicate generic GPIO chip for `SYS_MCI` compatibility with older device trees, sets its data register to `base + SYS_MCI`, forces `ngpio = 2`, and registers it with devm gpiolib. It then calls `devm_mfd_add_devices()` with the original parent memory resource and child cells. Each MFD cell receives relative memory resources for its portion of the sysreg block.

## State, Persistence, And Dependencies
The driver keeps no private runtime state after devm setup. Persistent state is in the sysreg hardware registers manipulated by child drivers. Dependencies include platform MMIO resources, OF matching on `"arm,vexpress-sysreg"`, generic MMIO GPIO helpers, software nodes/property entries, and MFD resource offset handling.

## Integration Points
The `basic-mmio-gpio` children expose LED, MCI, and flash bits using software-node properties for labels and line counts. The duplicate `SYS_MCI` gpiochip exists directly under the sysreg device for compatibility with older trees that referenced the sysreg node itself for MMC control lines. `vexpress-syscfg` receives the `SYS_MISC` through `SYS_CFGSTAT` register span.

## Risks
The full resource is mapped with `devm_ioremap()` rather than a reservation helper, so conflict detection depends on platform resource ownership. The compatibility MCI gpiochip duplicates the MFD child view of the same register, so concurrent users could race on `SYS_MCI`. Fixed offsets and sizes assume the expected Versatile Express sysreg layout. The driver does not validate resource size against the highest child range. There is no remove callback because devm handles cleanup.

## Test Signals
Probe should be tested with correct and missing memory resources, validating MFD child creation and duplicate MCI gpiochip registration. GPIO tests should toggle LED, MCI, and flash lines and verify MMIO writes hit `SYS_LED`, `SYS_MCI`, and `SYS_FLASH`. Compatibility tests should exercise old MMC bindings using the parent sysreg GPIO provider. Syscfg tests should confirm child access to the `SYS_MISC` register window.
