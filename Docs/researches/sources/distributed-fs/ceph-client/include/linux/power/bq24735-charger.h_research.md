# sources/distributed-fs/ceph-client/include/linux/power/bq24735-charger.h

Purpose: defines board/platform configuration for the TI bq24735 charger driver.

Important APIs and types: `struct bq24735_platform` supplies charge current, charge voltage, input current, power-supply name, external-control flag, and supplied-to battery names/count.

Control flow: the charger driver reads this data at probe to configure initial charge/input limits, name the power-supply instance, decide whether hardware is externally controlled, and publish supplicant relationships.

State and persistence: no live state is held by the header; values are static board defaults.

Dependencies and integration points: integrates with `power_supply` naming/supplicant relationships and charger hardware programming.

Risks and test signals: risks include current/voltage unit mismatches, misdeclared external control causing unexpected charging, and invalid supplied-to arrays. Test probe, power_supply registration, limit programming, external-control mode, and charger-to-battery supply links.
