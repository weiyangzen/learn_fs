# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-raspberrypi.c

## Purpose
Implements Raspberry Pi firmware-controlled clocks as common-clock providers. It uses firmware mailbox properties instead of direct register access so firmware can continue managing thermal and undervoltage constraints, especially for PLLB/ARM and shared display/media clocks.

## Important APIs, Types, And Functions
Key types are `raspberrypi_clk`, `raspberrypi_clk_data`, `raspberrypi_clk_variant`, `raspberrypi_firmware_prop`, and `rpi_firmware_get_clocks_response`. Important routines include `raspberrypi_clock_property`, `raspberrypi_fw_is_prepared`, `raspberrypi_fw_get_rate`, `raspberrypi_fw_set_rate`, `raspberrypi_fw_dumb_determine_rate`, `raspberrypi_fw_prepare`, `raspberrypi_fw_unprepare`, `raspberrypi_clk_register`, `raspberrypi_discover_clocks`, `raspberrypi_clk_probe`, and `raspberrypi_clk_remove`.

## Control Flow
Probe locates the firmware node, obtains an `rpi_firmware` handle, allocates onecell data, discovers available firmware clocks, filters for exported variants, queries min/max rates, registers each `clk_hw`, optionally registers clkdev aliases, enforces variant minimum rates, adds the OF provider, and spawns the Raspberry Pi cpufreq platform device. Clock operations translate prepare, unprepare, rate get, and rate set into firmware tags.

## State And Persistence
Persistent state includes the firmware handle, one `clk_hw` per exported firmware clock, variant policy flags (`minimize`, `maximize`, `min_rate`, `CLK_IS_CRITICAL`, `CLK_IGNORE_UNUSED`), rate ranges stored in CCF, and the child cpufreq platform device. Actual clock state persists in firmware.

## Dependencies And Integration Points
Depends on `soc/bcm2835/raspberrypi-firmware.h`, platform devices, OF provider APIs, clkdev aliases for CPU clock consumers, and firmware property tags such as `GET_CLOCKS`, `GET/SET_CLOCK_RATE`, `GET_MIN/MAX_CLOCK_RATE`, and `GET/SET_CLOCK_STATE`.

## Risks And Edge Cases
Firmware discovery can report unknown IDs. `determine_rate` cannot know firmware rounding. `unprepare` deliberately sets rate to minimum before disabling because firmware may not fully power off clocks. Shared clocks use minimize/maximize policies that can surprise consumers expecting exact requested rates. Missing firmware node defers or fails probe.

## Test Signals
Mock firmware responses for discovery, min/max, state, and rate changes; exported-only clocks in the onecell provider; cpufreq child creation/removal; minimum-rate enforcement for M2MC; critical clocks staying enabled; and rate restoration for maximize variants.
