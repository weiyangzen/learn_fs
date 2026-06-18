# sources/distributed-fs/ceph-client/drivers/mfd/twl4030-power.c

## Purpose
`twl4030-power.c` programs TWL4030 PM master/receiver power scripts and resource configuration. It loads sleep/wakeup/warm-reset scripts into PM memory, maps resources to device groups/types/remap states, supplies several OMAP3 default power configurations from device tree match data, and can install the TWL4030 system power-off callback.

## Important APIs, Types, And Functions
Script-writing helpers are `twl4030_write_script_byte()`, `twl4030_write_script_ins()`, and `twl4030_write_script()`. Sequence config helpers are `twl4030_config_wakeup3_sequence()`, `twl4030_config_wakeup12_sequence()`, `twl4030_config_sleep_sequence()`, and `twl4030_config_warmreset_sequence()`. Resource logic is in `twl4030_configure_resource()`, `twl4030_patch_rconfig()`, and `twl4030_power_configure_resources()`. Public functions are `twl4030_remove_script()` and `twl4030_power_off()`. Probe is `twl4030_power_probe()`.

## Control Flow
Probe requires platform data or an OF node, unlocks PM master protected registers, obtains match data for OF configurations, loads all scripts sequentially starting at `twl4030_start_script_address`, configures resources, optionally verifies/sets `SEQ_OFFSYNC` and assigns `pm_power_off`, then relocks protected registers. Script loading checks memory bounds, writes each instruction as four bytes, and updates sequence-address registers according to script flags. Wakeup12 configuration can clear charger start triggers for known charger quirks or legacy OMAP machines.

## State, Persistence, And Dependencies
Persistent hardware state is central: PM script memory, sequence address registers, P1/P2/P3 software events, transition start masks, resource group/type/remap registers, and power-off/start behavior. Static default OMAP3 script/resource configurations are used as OF match data and may be patched by board-specific resource overrides. Dependencies include TWL core I2C helpers, PM master protected-key protocol, platform data structures from `linux/mfd/twl.h`, OF match data, machine type checks, and global `pm_power_off`.

## Integration Points
This platform driver is populated beneath the TWL core. OF compatibles select generic, reset-only, idle, idle-osc-off, and OMAP3 board quirk configurations. `twl4030_power_off()` is installed when platform data or DT indicates a system power controller and no existing `pm_power_off` is set.

## Risks
The script `order` variable in `load_twl4030_script()` is static, so previous loads can affect later warnings. `twl4030_patch_rconfig()` mutates the common resource config array in place, and OF match data points at static arrays; a board override can permanently modify shared defaults. `twl4030_starton_mask_and_set()` always attempts relock and can mask an earlier unlock error path. Power-off disables start on charger/VBUS before setting DEVOFF, so incorrect wiring/properties can make the board hard to restart. Many paths program protected PM state, making partial failures risky.

## Test Signals
Test script memory bounds, instruction byte ordering and END_OF_SCRIPT linkage, each script flag path, wakeup/sleep/warm-reset sequence-address writes, resource group/type/remap writes, board-config patching side effects, protected unlock/relock failure injection, power-off STARTON mask and DEVOFF writes, OF compatible selection, charger quirk behavior, and repeated probe/remove/reprobe with static configs.
