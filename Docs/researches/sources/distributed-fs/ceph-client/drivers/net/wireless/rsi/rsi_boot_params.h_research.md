# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_boot_params.h

## Purpose
This header defines the packed boot-parameter structures and PLL/clock constants sent from the host to RSI firmware during early WLAN bring-up for 9113-style and 9116-style devices.

## Important APIs, Types, and Functions
Important macros include `VALID_20`, `VALID_40`, `UMAC_CLK_20BW`, `UMAC_CLK_40BW`, PLL M/N/P values, switch-clock bit flags, `LOADED_TOKEN`, `ROM_TOKEN`, `BT_COEXIST`, and `BOOTUP_MODE`. Data types include `tapll_info`, `pll960_info`, `afepll_info`, `pll_config`, `pll_config_9116`, `switch_clk`, `switch_clk_9116`, `device_clk_info`, `device_clk_info_9116`, `bootup_params`, and `bootup_params_9116`.

## Control Flow
There is no executable control flow. `rsi_91x_mgmt.c` instantiates concrete 20 MHz and 40 MHz boot tables from these layouts and copies them into management command SKBs after card-ready and when channel width changes.

## State and Persistence Behavior
The header stores no runtime state, but its packed little-endian structures become hardware-visible configuration for PLLs, clocks, wakeup waits, watchdog values, DCDC mode, sleep clock source, and boot mode. Incorrect field ordering or packing would persist into firmware until reset.

## Dependencies and Integration Points
It depends on Linux endian types and `BIT()`. It is tightly coupled to firmware management frame definitions in `rsi_mgmt.h` and to the init FSM in `rsi_91x_mgmt.c`.

## Risks
These layouts are firmware ABI. Changing field order, size, packing, endian conversion, or valid-bit masks can prevent boot, break RF clocks, or misprogram power/reset behavior. Macros such as `CUR_DEV_MODE_9116` reference an object name and are unsafe outside the expected initializer context.

## Test Signals
Build-time structure size/packing checks, firmware boot on 20/40 MHz modes, 9113 and 9116 card-ready transitions, channel-width changes that reload boot params, and hardware logs for PLL/clock programming are the relevant signals.
