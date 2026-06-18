# sources/distributed-fs/ceph-client/include/linux/power/bq24190_charger.h

Purpose: provides platform data for the TI bq24190 charger driver.

Important APIs and types: `struct bq24190_platform_data` carries a pointer to regulator init data used when the charger exposes or consumes regulator functionality.

Control flow: platform registration supplies the regulator constraints during probe; the charger driver forwards them to regulator registration/configuration.

State and persistence: no runtime state is held; the struct is static probe-time configuration.

Dependencies and integration points: depends on `linux/regulator/machine.h` and integrates the bq24190 charger driver with regulator core policy.

Risks and test signals: risks include NULL or mismatched regulator constraints, lifetime of platform data, and board files diverging from DT/ACPI properties. Test charger probe with regulator init data, regulator enable/current constraints, and builds without board-data users.
