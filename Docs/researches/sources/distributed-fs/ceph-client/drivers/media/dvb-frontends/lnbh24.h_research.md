# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh24.h

## Purpose
`lnbh24.h` provides the public interface and register bit definitions for LNBH24 satellite LNB supply control, implemented through the shared LNBP21/LNBH24 C file.

## Important APIs, Types, and Functions
The header defines system register bits such as `LNBH24_OLF`, `LNBH24_OTF`, `LNBH24_EN`, `LNBH24_VSEL`, `LNBH24_LLC`, `LNBH24_TEN`, `LNBH24_TTX`, and `LNBH24_PCL`. `lnbh24_attach()` accepts a frontend, I2C adapter, override set/clear masks, and I2C address when `CONFIG_DVB_LNBP21` is reachable.

## Control Flow
Callers attach LNBH24 support to an existing satellite frontend. The implementation routes this to `lnbx2x_attach()` with an LNBH24 default config bit, then overrides the frontend SEC voltage/tone callbacks.

## State and Persistence
The header defines bit constants only. Runtime state in `lnbp21.c` keeps one volatile config byte and board override masks.

## Dependencies and Integration Points
It depends on DVB frontend types and is tied to `CONFIG_DVB_LNBP21` because LNBH24 shares that implementation.

## Risks and Edge Cases
The override masks can force bits on or off for every write; incorrect masks can permanently disable tone, power, or protection behavior. The header has no type-safe config structure, only raw masks and address.

## Test Signals
Validate attach through the LNBP21 implementation, 13 V/18 V/off writes at the supplied address, tone callback availability depending on override masks, and Kconfig-disabled stubs.
