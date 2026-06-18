<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13783-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mc13783-regulator.c

## Purpose
Defines the MC13783-specific regulator table and platform driver on top of the shared MC13xxx regulator core. It covers switchers, LDOs, GPO outputs, and power gate outputs for the Freescale/NXP MC13783 PMIC.

## Important APIs, Types, And Functions
`mc13783_regulators[]` is an indexed array of `struct mc13xxx_regulator` descriptors built with MC13xxx macros and MC13783 voltage tables. The special GPO/power-gate path is implemented by `mc13783_powermisc_rmw()`, `mc13783_gpo_regulator_enable()`, `mc13783_gpo_regulator_disable()`, `mc13783_gpo_regulator_is_enabled()`, and `mc13783_gpo_regulator_ops`. Probe is `mc13783_regulator_probe()`.

## Control Flow
The platform driver binds to `mc13783-regulator`, determines regulator count from DT `regulators` children or platform data, allocates `struct mc13xxx_regulator_priv`, attaches the parent `struct mc13xxx`, parses DT regulator init data through the shared core, and registers each requested descriptor. Normal regulators use exported MC13xxx ops for register read/modify/write. GPO and power-gate regulators use the local POWERMISC helper to preserve power-gate state and handle the inverted enable value for `PWGT1SPI` and `PWGT2SPI`.

## State And Persistence
The private state stores the parent PMIC pointer, descriptor array pointer, regulator devices, and `powermisc_pwgt_state`, which mirrors inverted power-gate bits so mixed writes to POWERMISC do not lose gate state. Persistent state is PMIC register state only.

## Dependencies And Integration Points
Depends on the MC13xxx MFD API (`mc13xxx_reg_read`, `mc13xxx_reg_rmw`, locking), shared `mc13xxx.h`/core ops, platform data or OF regulator parsing, and regulator framework. The platform device is normally created by the parent MC13783 MFD.

## Risks And Test Signals
Risks include wrong voltage tables for duplicated selectors, active-low power-gate semantics, POWERMISC updates racing without the MC13xxx lock, and mismatch between DT child names and descriptor names. Test by DT and platform-data registration, voltage table listing for every rail, GPO/power-gate enable/disable/is_enabled cycles, and concurrent POWERMISC updates under debug tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13783-regulator.c -->
