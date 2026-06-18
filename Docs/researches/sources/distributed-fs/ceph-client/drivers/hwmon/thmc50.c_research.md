
# sources/distributed-fs/ceph-client/drivers/hwmon/thmc50.c

Purpose: I2C hwmon driver for THMC50 and ADM1022 temperature monitors. It exposes two base temperature channels, optional ADM1022 third temperature channel, temperature limits/critical values, alarms/faults, and a DC PWM analog output.

Important APIs, types, and functions: `struct thmc50_data` stores client, dynamic groups, chip type, optional temp3 mode, cache, temperature registers, analog output, and alarms. `thmc50_update_device()` refreshes data after 200 ms for ADM1022 or about 1.2 seconds for THMC50. `thmc50_detect()` validates company/revision/config and can enable ADM1022 temp3 mode via the `adm1022_temp3` module parameter. `thmc50_init_client()` starts the chip and ensures analog output is nonzero.

Control flow, state, and persistence: probe initializes hardware, builds the group list with optional temp3 attributes, and registers hwmon groups. Store handlers update min/max temperatures and analog output; analog output also toggles the fan-off config bit.

Dependencies and integration points: uses I2C class scanning at 0x2c-0x2e, SMBus byte data, module parameter pairs for ADM1022 temp3, and hwmon sysfs.

Risks and test signals: update reads do not check every SMBus return before caching. ADM1022 temp3 enable is controlled by adapter/address pairs and writes config during detection. Test both company IDs, temp3 parameter parsing, analog output zero behavior, nFANOFF updates, alarm bit mapping, cache timeout differences, and min/max clamping.
