# sources/distributed-fs/ceph-client/drivers/power/supply/sbs-manager.c

## Purpose
Driver for SBS Smart Battery System Managers, including LTC1760. It exposes manager AC/charge-type properties, multiplexes access to up to four downstream smart batteries at address 0x0b, optionally provides GPIOs for battery presence, and forwards SMBus alerts to child battery drivers.

## Important APIs, Types, and Functions
`struct sbsm_data` tracks the manager client, I2C mux, power supply, selected channel, GPIO chip, LTC1760 capability flag, supported batteries, and last alert states. Key functions are `sbsm_probe()`, `sbsm_select()`, `sbsm_get_property()`, `sbsm_set_property()`, `sbsm_alert()`, `sbsm_gpio_setup()`, and `sbsm_do_alert()`.

## Control Flow
Probe validates address 0x0a and SMBus word support, reads supported battery mask, creates a locked I2C mux with one adapter per present battery, registers optional GPIO chip, and registers the manager mains power supply. Property reads query AC present and charge battery bits. LTC1760 supports writable fast/trickle charge type through the TURBO bit. Alerts compare current state against cached state and call child drivers' `alert()` callback under the selected mux child adapter.

## State and Persistence
`cur_chan`, `supported_bats`, `last_state`, and `last_state_cont` are volatile caches. The manager writes BATSYSSTATE to select a downstream battery and writes LTC TURBO for charge type.

## Dependencies and Integration Points
Depends on I2C, i2c-mux, GPIO provider APIs, power_supply, and firmware properties. Compatible strings are `sbs,sbs-manager` and `lltc,ltc1760`.

## Risks and Test Signals
Correct mux channel numbering is critical because `chan` is encoded directly into SMB_BAT bits. Alert forwarding walks child devices at address 0x0b and assumes child drivers implement alert. Test multi-battery mux access, LTC1760 charge-type writes, optional GPIO registration, AC-change notifications, and alert propagation to `sbs-battery`.
