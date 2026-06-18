# sources/distributed-fs/ceph-client/drivers/memory/mvebu-devbus.c

## Purpose
`mvebu-devbus.c` configures the Marvell EBU/Orion device bus controller for attached NOR, NAND, SRAM, or FPGA-like devices. It converts device-tree timing properties from picoseconds to controller ticks and programs Orion or Armada register layouts before creating child devices.

## Important APIs, Types, And Functions
`struct devbus` stores device, mapped base, and clock tick in picoseconds. `struct devbus_read_params` and `struct devbus_write_params` hold decoded timing and bus-width values. `get_timing_param_ps()` reads one DT timing property and converts it to ticks. `devbus_get_timing_params()` parses required bus width and timing properties, with extra read setup/hold and sync-enable fields for `marvell,mvebu-devbus`. `devbus_orion_set_timing_params()` and `devbus_armada_set_timing_params()` encode the parsed values for different hardware layouts.

## Control Flow
Probe allocates state, maps registers, enables the clock, computes `tick_ps`, optionally skips programming when `devbus,keep-config` is set, otherwise parses timing data and writes either Orion or Armada registers. It then calls `of_platform_populate()` so children probe after bus timing is programmed.

## State And Persistence
The driver does not keep state after probe beyond devm allocations. Hardware timing registers are persistent until reset or reprogramming. Clock enable is devm-managed.

## Dependencies And Integration Points
It uses platform driver probing, OF timing properties, clock framework, MMIO writes, and child platform population. Supported compatibles are `marvell,mvebu-devbus` and `marvell,orion-devbus`.

## Risks
Timing fields are not range-checked against their register widths before shifting; invalid DT values can truncate into hardware fields. Missing required properties fail probe. The `devbus,keep-config` escape hatch relies on bootloader setup and can hide incorrect DT data.

## Test Signals
Tests should validate tick conversion at expected clock rates, missing-property failures, 8-bit and 16-bit bus-width encoding, Orion extended-bit encoding, Armada read/write register values, `devbus,keep-config` behavior, and child creation ordering.
