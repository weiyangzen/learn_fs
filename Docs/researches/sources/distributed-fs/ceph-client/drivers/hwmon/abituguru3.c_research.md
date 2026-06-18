# sources/distributed-fs/ceph-client/drivers/hwmon/abituguru3.c

## Purpose
`abituguru3.c` supports later Abit uGuru3 motherboard monitor chips. It exposes voltage, temperature, fan, alarm, mask, and label attributes for known motherboard IDs, but unlike `abituguru.c` it is read-only from sysfs and relies on a static motherboard sensor table.

## Important APIs, Types, And Functions
`struct abituguru3_sensor_info` describes each logical sensor name, controller port, sensor type, scaling multiplier/divisor, and offset. `struct abituguru3_motherboard_info` maps uGuru3 board IDs and optional DMI names to sensor tables. `struct abituguru3_data` stores hwmon state, I/O address, validity flags, generated sysfs attributes/names, the selected sensor table, 48 alarm bits, 48 values, and 48 setting triplets. The controller protocol is implemented by wait/synchronize/read helpers, and sysfs callbacks are `show_value`, `show_alarm`, `show_mask`, `show_label`, and `show_name`.

## Control Flow
`abituguru3_init` first checks DMI via `abituguru3_dmi_detect`; if the board is not exactly matched or `force` is set, it falls back to fixed-port manual detection. It then registers a platform driver and synthetic platform device at `ABIT_UGURU3_BASE`. `abituguru3_probe` reads the motherboard ID from the miscellaneous bank, performs a full update, chooses the matching static motherboard table, dynamically formats sysfs attributes in sensor order, creates them, and registers hwmon. Updates synchronize the protocol state machine for every command, read the alarm bytes, read values and settings for the 32 voltage/temp ports, then read values and 2-byte settings for 16 fan ports. Data is cached for one second.

## State And Persistence
Runtime state is a cache of all 48 ports plus the selected static metadata table. The driver does not provide sysfs stores, so it should not persist user changes to the chip. It still reads persistent alarm/limit masks from the controller. Suspend locks `update_lock` to stop command traffic; resume releases it.

## Dependencies And Integration Points
The driver depends on fixed I/O port access, DMI, platform devices, hwmon sysfs helpers, jiffies, and a large in-driver board table. It uses module parameters `force` and `verbose`. Integration with userspace is via manually generated legacy sysfs attributes such as `in*_input`, `temp*_input`, `fan*_input`, `*_alarm`, `*_label`, and `name`.

## Risks And Test Signals
The main risks are incorrect or incomplete motherboard tables, manual fixed-port probing on unsupported boards, fragile command synchronization, and read-only attributes that may not reflect writable hardware capabilities. Scaling correctness depends on per-board multipliers and offsets. Test signals include DMI table matching, board ID lookup failure reporting, complete sysfs attribute creation for each table entry, no buffer overrun in `sysfs_names`, correct one-second cache refresh, and successful handling of busy/read timeouts without leaving `valid` true after partial refreshes.
