# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_efuse.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_efuse.c` provides common EFUSE read and shadow-map helpers for the RTL8723BS driver. It reads one-byte EFUSE hardware cells, powers and reads the full logical EFUSE map through HAL helpers, and exposes typed reads from the cached EFUSE/EEPROM shadow data. The file was read completely as a 261-line source file.

## Important APIs, Types, and Functions

`Efuse_CalculateWordCnts()` counts enabled 2-byte words from a Realtek EFUSE word-enable mask, where cleared bits mean present/write-enabled words. `EFUSE_Read1Byte()` performs a bounded direct one-byte read from `EFUSE_CTRL` after checking the real content length. `efuse_OneByteRead()` is a second one-byte read helper that manipulates register `0x34`/`EFUSE_CTRL`, waits with `mdelay(1)`, and returns a boolean-like result while writing the byte through an output pointer.

`EFUSE_ShadowMapUpdate()` refreshes `eeprom_priv.efuse_eeprom_data` from hardware or fills it with `0xff` if autoload failed. `EFUSE_ShadowRead()` dispatches to static `efuse_ShadowRead1Byte()`, `efuse_ShadowRead2Byte()`, or `efuse_ShadowRead4Byte()` to read little-endian values from the cached shadow array. `Efuse_ReadAllMap()` powers EFUSE on, queries `TYPE_EFUSE_MAP_LEN`, calls `Hal_ReadEFuse()`, and powers EFUSE off.

## Control Flow

Single-byte direct reads program the low and high EFUSE address bits into `EFUSE_CTRL + 1` and `EFUSE_CTRL + 2`, clear bit 7 of `EFUSE_CTRL + 3` to start a read, poll until bit 7 is set, then fetch the data byte from `EFUSE_CTRL`. `EFUSE_Read1Byte()` polls up to 1000 tight iterations and returns `0xff` for addresses beyond the HAL-reported real content length. `efuse_OneByteRead()` clears `BIT11` in register `0x34`, polls up to 1000 milliseconds, writes `0xff` on timeout, and treats reads with `tmpidx < 100` as successful.

Full-map refresh uses HAL abstraction rather than open-coded parsing: power switch on, get map length, read EFUSE into the shadow buffer, power switch off. Shadow reads do no hardware I/O; they index `efuse_eeprom_data` directly and pack bytes into 1-, 2-, or 4-byte values.

## State and Persistence Behavior

Hardware EFUSE is persistent, one-time-programmed device configuration. This file does not write EFUSE; it only reads. Runtime cached state is `struct eeprom_priv::efuse_eeprom_data` plus `bautoload_fail_flag`. A failed autoload causes the shadow map to become all `0xff`, matching erased EFUSE semantics and letting higher layers fall back to defaults.

The shadow read helpers do not validate offset bounds against the EFUSE map length; callers must pass valid offsets for the selected type width. Direct read helpers depend on HAL-provided content/map lengths and hardware register readiness.

## Dependencies and Integration Points

Direct includes are `drv_types.h`, `hal_data.h`, and `linux/jiffies.h`. The file depends on HAL EFUSE definitions through `Hal_GetEfuseDefinition()`, `Hal_EfusePowerSwitch()`, and `Hal_ReadEFuse()`, and on `rtw_io.c` register accessors `rtw_read8()`, `rtw_write8()`, `rtw_read16()`, and `rtw_write16()`. `GET_EEPROM_EFUSE_PRIV()` connects the helpers to adapter-owned EEPROM/EFUSE state.

Callers elsewhere in the driver use the shadow map for MAC address, regulatory, RF, power, and board-configuration data. `rtw_ieee80211.c` can consume the resulting MAC address through higher-level EEPROM/device setup paths when configuring the netdev address.

## Risks and Edge Cases

Polling behavior is hardware-sensitive. `EFUSE_Read1Byte()` uses a tight loop, while `efuse_OneByteRead()` can delay up to roughly one second; misuse in atomic context would be problematic. `efuse_OneByteRead()` checks `tmpidx < 100` rather than `< 1000` for success, so slow reads between 100 and 999 iterations are treated as failures despite the loop not timing out.

Shadow reads can read past the map if callers provide an invalid offset, especially for 2- and 4-byte reads near the end. Direct reads return `0xff` on out-of-range or timeout, which can be indistinguishable from an erased EFUSE byte unless the boolean result from `efuse_OneByteRead()` is checked. Register `0x34` manipulation is device-specific and should not be generalized without chipset review.

## Test Signals

Unit-style tests with mocked I/O ops should cover enabled-word counting for all 16 word-enable masks, address programming into `EFUSE_CTRL`, polling success, timeout, and out-of-range behavior. Integration tests should verify `EFUSE_ShadowMapUpdate()` for normal and autoload-fail devices, typed shadow reads for little-endian 1/2/4-byte values, and MAC/regulatory defaults when shadow bytes are all `0xff`. Hardware smoke tests should include repeated reads across EFUSE boundaries and suspend/resume or power-cycle cases where EFUSE power switching matters.
