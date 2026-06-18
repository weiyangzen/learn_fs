# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh29.h

## Purpose
`lnbh29.h` defines the public configuration interface for the LNBH29 LNB supply driver.

## Important APIs, Types, and Functions
It defines `LNBH29_DATA_COMP` for the DATA register compensation option. `struct lnbh29_config` carries the I2C address and initial DATA register configuration. `lnbh29_attach()` is declared when `CONFIG_DVB_LNBH29` is reachable and stubbed otherwise.

## Control Flow
Board code supplies config to attach; the implementation copies the DATA option byte, installs `set_voltage`, and probes with output off.

## State and Persistence
The header owns no state. The DATA config becomes a mutable runtime cache in `fe->sec_priv`.

## Dependencies and Integration Points
It depends on Linux I2C and DVB frontend headers and integrates with satellite frontend SEC setup.

## Risks and Edge Cases
Only the compensation option is named publicly; other DATA register bits may need board-specific values in `data_config` without symbolic documentation here. The implementation shifts `i2c_address` right by one.

## Test Signals
Build-test Kconfig enabled/disabled paths and verify board-provided DATA bits survive voltage changes.
