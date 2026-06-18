# sources/distributed-fs/ceph-client/drivers/memory/da8xx-ddrctl.c

## Purpose
`da8xx-ddrctl.c` is a small TI DA8xx DDR2/mDDR controller tuning driver. It applies hard-coded board-specific performance register settings where Linux lacks a general framework for these controller knobs.

## Important APIs, Types, And Functions
`struct da8xx_ddrctl_config_knob` describes a named register field: register offset, mask, and shift. `struct da8xx_ddrctl_setting` binds a knob name to a value, and `struct da8xx_ddrctl_board_settings` maps machine compatibles to setting arrays. The only present knob is `da850-pbbpr` at offset `0x20`, and the only board configuration is `ti,da850-lcdk` setting that field to `0x20`.

`da8xx_ddrctl_match_knob()` resolves a setting name to the supported knob table. `da8xx_ddrctl_get_board_settings()` checks `of_machine_is_compatible()` against board settings. `da8xx_ddrctl_probe()` maps the controller resource, validates register offsets against resource size, masks and inserts each setting value, then writes the result.

## Control Flow
Probe first selects a settings array based on the root machine compatible. Without a supported board it returns `-EINVAL`. For each setting it finds a knob, checks the register fits in the mapped resource, reads the current register value, clears or preserves bits according to `mask`, inserts `val << shift`, and writes the register.

## State And Persistence
There is no private runtime state after probe. The only persistent effect is the hardware register programming, which is not saved/restored by this driver and is expected to be reapplied by reprobe after reboot.

## Dependencies And Integration Points
The driver is a platform driver matched by `ti,da850-ddr-controller`, but policy is gated by root-machine compatible. It uses device tree, platform MMIO mapping, and normal Linux module/platform-driver registration.

## Risks
The mask semantics are easy to misread: the code keeps bits covered by `mask` and ORs the shifted value, so adding knobs needs careful review. Unsupported boards fail probe noisily. There is no PM restore path if low-power states reset the DDR controller register.

## Test Signals
Tests should boot on `ti,da850-lcdk`, confirm register `0x20` receives the expected field value, verify unsupported boards return `-EINVAL`, and exercise the resource-size guard by checking that out-of-range knob offsets are skipped with warnings.
