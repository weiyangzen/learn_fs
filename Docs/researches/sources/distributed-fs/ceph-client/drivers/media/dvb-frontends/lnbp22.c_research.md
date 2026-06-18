# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp22.c

## Purpose
`lnbp22.c` implements a simple LNBP22 LNB supply/control helper. It attaches voltage and high-voltage compensation callbacks to an existing DVB frontend and writes a four-byte I2C config frame.

## Important APIs, Types, and Functions
`struct lnbp22` stores a four-byte config array and I2C adapter. `lnbp22_set_voltage()` resets byte 3 to power-down base `0x60`, then applies EN/VSEL for off/13 V/18 V and writes to fixed I2C address `0x08`. `lnbp22_enable_high_lnb_voltage()` toggles LLC in byte 3. `lnbp22_release()` powers off and frees state. `lnbp22_attach()` seeds default bytes, probes with voltage off, and installs SEC callbacks.

## Control Flow
Attach allocates state, initializes four undocumented/default bytes, stores `fe->sec_priv`, calls set-voltage off as detection, and then overrides `release_sec`, `set_voltage`, and `enable_high_lnb_voltage`. Voltage and LLC operations write all four bytes each time.

## State and Persistence
The config array is volatile runtime state. Release powers off and frees it. No fault status is read and no persistent storage exists.

## Dependencies and Integration Points
The file depends on Linux I2C, module parameters for debug output, and DVB frontend SEC callbacks. It exports `lnbp22_attach()`.

## Risks and Edge Cases
The I2C address is hard-coded to `0x08`, unlike newer helpers that take a config address. Tone control is not implemented. The first three config bytes are marked unknown in comments, and byte 3 is reset on every voltage change, which can discard prior LLC state unless LLC is set after voltage.

## Test Signals
Validate attach/probe at address `0x08`, off/13/18 V writes, LLC toggle persistence across expected call order, release power-off, and debug/error behavior on I2C failure.
