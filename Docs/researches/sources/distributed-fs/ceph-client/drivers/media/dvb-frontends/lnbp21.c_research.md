# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp21.c

## Purpose
`lnbp21.c` implements SEC helper support for ST LNBP21 and LNBH24 LNB supply/control ICs. It attaches to an existing DVB frontend and overrides voltage, high-voltage compensation, tone, and release callbacks.

## Important APIs, Types, and Functions
`struct lnbp21` stores one config byte, force-set/force-clear masks, I2C adapter, and I2C address. `lnbp21_set_voltage()` maps DVB off/13 V/18 V to EN/VSEL bits, applies overrides, and writes one byte. `lnbp21_enable_high_lnb_voltage()` toggles LLC. `lnbp21_set_tone()` toggles TEN. `lnbp21_release()` powers off and frees `sec_priv`. The shared `lnbx2x_attach()` handles allocation, default config, override masks, presence probe, and callback installation. Public wrappers are `lnbh24_attach()` and `lnbp21_attach()`.

## Control Flow
LNBH24 attach calls the shared helper with the caller-supplied I2C address and `LNBH24_TTX` as default config. LNBP21 attach uses address `0x08` and `LNBP21_ISEL` as default config. The shared helper powers off as a presence probe, installs callbacks, and suppresses `set_tone` when the LNBH24 TEN bit is forced clear.

## State and Persistence
Runtime state is one mutable config byte plus override masks. Every SEC operation re-applies overrides before I2C write. Release powers off and frees state. There is no persistent storage or fault-status polling.

## Dependencies and Integration Points
The file depends on DVB frontend SEC callbacks, Linux I2C, and bit definitions from `lnbp21.h` and `lnbh24.h`. It exports both attach functions for board drivers.

## Risks and Edge Cases
The presence probe only checks that an I2C write succeeds; read-only fault bits are never inspected. Incorrect override masks can force power/tone/protection bits into unsafe states. If attach fails, `fe->sec_priv` is not explicitly cleared in the shared helper after freeing. Tone callback installation depends on an LNBH24 bit even when using the shared helper.

## Test Signals
Validate LNBP21 and LNBH24 attach paths, off/13/18 V writes, LLC toggle, TEN tone toggle or suppression, override set/clear behavior, release power-off, and failed I2C probe cleanup.
