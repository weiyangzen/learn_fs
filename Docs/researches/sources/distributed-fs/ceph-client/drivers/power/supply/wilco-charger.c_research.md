# sources/distributed-fs/ceph-client/drivers/power/supply/wilco-charger.c

## Purpose
`wilco-charger.c` exposes Wilco EC charge-control settings through a power-supply device. It maps EC byte properties for charge mode and charge start/end thresholds to standard power-supply charge type and charge-control threshold properties.

## Important APIs, Types, And Functions
Property IDs are `PID_CHARGE_MODE`, `PID_CHARGE_LOWER_LIMIT`, and `PID_CHARGE_UPPER_LIMIT`. `enum charge_mode` defines EC modes. `psp_val_to_charge_mode()` and `charge_mode_to_psp_val()` convert between power-supply values and EC values. `wilco_charge_get_property()` and `wilco_charge_set_property()` call `wilco_ec_get_byte_property()`/`wilco_ec_set_byte_property()`. The descriptor `wilco_ps_desc` exposes three writable properties.

## Control Flow
Probe retrieves the parent `wilco_ec_device`, sets it as power-supply drvdata, and registers a mains-type supply named `wilco-charger`. Reads select the EC property id, fetch a byte, and convert charge mode if needed. Writes validate charge mode or threshold ranges and update the EC property.

## State, Persistence, And Dependencies
The driver holds no private state; all persistence lives in the EC. It depends on the Wilco EC platform data API and power-supply core.

## Integration Points
The platform driver name and alias are `wilco-charger`. Userspace sees `CHARGE_TYPE`, `CHARGE_CONTROL_START_THRESHOLD`, and `CHARGE_CONTROL_END_THRESHOLD`, matching ABI docs referenced in the file header.

## Risks
`wilco_charge_property_is_writeable()` returns true for every property the core asks about, not just the three descriptor properties; current descriptor scope makes this low risk. Start and end thresholds are individually range-checked but not cross-validated, so userspace might set a start threshold greater than or equal to the end threshold if the EC does not reject it. Unknown EC charge-mode values return `-EBADMSG`.

## Test Signals
Test all charge-mode round trips, invalid mode and threshold writes, EC communication errors, unknown raw EC mode handling, start/end threshold ordering at the EC level, and power-supply registration with missing parent drvdata.
