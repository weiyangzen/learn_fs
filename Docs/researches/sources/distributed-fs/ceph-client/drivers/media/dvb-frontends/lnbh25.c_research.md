# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh25.c

## Purpose
`lnbh25.c` drives the ST LNBH25 satellite LNB supply/control IC. It attaches SEC voltage control to an existing DVB frontend, writes DATA1/DATA2 over I2C, and verifies voltage monitor status after enabling output.

## Important APIs, Types, and Functions
`struct lnbh25_priv` stores the I2C adapter, 7-bit I2C address, and a three-byte write buffer starting at DATA1 register `0x02`. `lnbh25_set_voltage()` maps DVB `SEC_VOLTAGE_OFF`, `SEC_VOLTAGE_13`, and `SEC_VOLTAGE_18` to `LNBH25_VSEL_*` values and writes the config. `lnbh25_read_vmon()` reads six status bytes and rejects over-current or voltage-monitor faults. `lnbh25_release()` powers off and frees `sec_priv`; `lnbh25_attach()` allocates state, probes by powering off, and overrides `release_sec` and `set_voltage`.

## Control Flow
Attach converts the supplied 8-bit address to a 7-bit I2C address, seeds config bytes, stores `fe->sec_priv`, and calls `lnbh25_set_voltage(OFF)` as presence detection. Setting voltage writes all three bytes, waits 120 ms for 13/18 V before reading status, or 20 ms for off.

## State and Persistence
State is one allocated `lnbh25_priv` and the last DATA1/DATA2 config bytes. Hardware output state is volatile and explicitly forced off on release. There is no persistent storage.

## Dependencies and Integration Points
The file depends on Linux I2C, delays, module infrastructure, and DVB frontend SEC callbacks. It exports `lnbh25_attach()` for board drivers and uses `struct lnbh25_config` from the header.

## Risks and Edge Cases
Status read is split into two single-message transfers instead of one combined `i2c_transfer()` call; adapters must tolerate that sequence. Only voltage control is implemented, not tone or DiSEqC. Any VMON/OFL bit after the fixed delay is treated as `-EIO`, so slow or heavily loaded hardware may fail attach or voltage changes.

## Test Signals
Test attach/probe at the configured address, off/13 V/18 V transitions, DATA2 option preservation, VMON/OFL fault reporting, release power-off, and frontend SEC callback replacement.
