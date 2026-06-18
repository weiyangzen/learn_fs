# sources/distributed-fs/ceph-client/include/linux/power/bq25890_charger.h

Purpose: provides minimal platform data for the TI bq25890 charger driver.

Important APIs and types: `struct bq25890_platform_data` contains regulator init data for charger regulator integration.

Control flow: board data passes regulator constraints at probe; the driver uses them when registering or configuring charger-related regulators.

State and persistence: static probe-time platform data only.

Dependencies and integration points: forward-declares `struct regulator_init_data` and integrates bq25890 charger support with regulator core policy.

Risks and test signals: risks include wrong regulator constraints, missing platform data on non-DT systems, and lifetime assumptions. Test probe with regulator configuration, regulator constraints, charger enable/disable, and compile coverage.
