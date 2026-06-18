<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bytcrc_pwrsrc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bytcrc_pwrsrc.c

## Purpose
Provides Bay Trail Crystal Cove PMIC power-source reporting and reset/wake-source debugfs diagnostics, with optional `power_supply` registration for boards that request it.

## Important APIs, Types, And Functions
`struct crc_pwrsrc_data` stores regmap, debugfs dentries, optional power_supply, and latched reset/wake values. `crc_pwrsrc_read_and_clear()` snapshots and clears sticky source registers. `crc_pwrsrc_psy_get_property()` reports `POWER_SUPPLY_PROP_ONLINE` when USB or DC input is present. Debugfs show handlers decode named bit reasons.

## Control Flow
Probe reads and clears reset source and wake source registers before debugfs is used. If the parent has `linux,register-pwrsrc-power_supply`, probe registers a mains power_supply and IRQ handler; the handler clears PMIC power-source IRQ bits and calls `power_supply_changed()`. Debugfs files `pwrsrc`, `resetsrc`, and `wakesrc` are always created.

## State And Persistence
Resetsrc and wakesrc are sticky hardware registers that are copied into driver state and cleared. Current power-source state is read live. Debugfs state is removed on driver remove.

## Dependencies And Integration Points
Depends on parent `intel_soc_pmic` regmap, POWER_SUPPLY, debugfs, platform IRQs, and device properties.

## Risks And Test Signals
Leaving wakesrc uncleared can affect reboot/poweroff behavior on some tablets. Other risks are optional power_supply property misuse and IRQ acknowledgement failures. Test debugfs decoded output, AC online transitions, IRQ-driven uevents, and reboot behavior after wake-source bit 0 was set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bytcrc_pwrsrc.c -->
