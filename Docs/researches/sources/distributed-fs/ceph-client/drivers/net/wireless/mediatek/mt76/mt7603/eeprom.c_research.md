# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/eeprom.c

## Purpose
MT7603-specific EEPROM/efuse initialization. It reads OTP efuse data, optionally merges calibration-free OTP fields into external EEPROM, validates chip IDs, derives MAC address and antenna capabilities, and invokes common MAC override handling.

## Important APIs, Types, And Functions
- `mt7603_efuse_read()` reads a 16-byte efuse block through `MT_EFUSE_CTRL` and `MT_EFUSE_RDATA()`, returning all `0xff` for invalid rows.
- `mt7603_efuse_init()` allocates `dev->mt76.otp.data` and reads the full `MT7603_EEPROM_SIZE` when efuse is not empty.
- `mt7603_has_cal_free_data()` checks required OTP fields for cal-free merge validity.
- `mt7603_apply_cal_free_data()` merges selected OTP calibration bytes into EEPROM only when DT has `mediatek,eeprom-merge-otp`, with MT7628-specific skips.
- `mt7603_eeprom_load()` delegates external EEPROM allocation/loading to `mt76_eeprom_init()` and then reads efuse.
- `mt7603_check_eeprom()` accepts chip IDs `0x7628`, `0x7603`, and `0x7600`.
- `mt7603_eeprom_init()` decides whether OTP supplements or replaces EEPROM, sets 2 GHz capability, copies MAC, computes 1SS/2SS antenna mask, sets chainmask, and calls `mt76_eeprom_override()`.

## Control Flow
Hardware init calls `mt7603_eeprom_init()`. It loads external EEPROM and efuse. If OTP exists and external EEPROM validates, optional cal-free bytes are merged; if external EEPROM is invalid, OTP becomes the EEPROM image. Then the driver initializes PHY capabilities from EEPROM fields and SoC revision probes, and applies OF MAC override/random fallback.

## State And Persistence
Persistent board/calibration data is held in `dev->mt76.eeprom.data`; raw OTP is held in `dev->mt76.otp.data` for debugfs/diagnostics. Runtime PHY fields set here include `dev->mphy.cap.has_2ghz`, `macaddr`, `antenna_mask`, and `chainmask`.

## Dependencies And Integration Points
Depends on common mt76 EEPROM helpers, OF property checks, efuse register definitions, chip helpers such as `is_mt7628()`, and `mt76_eeprom_override()`. Later MCU and txpower code consumes the populated EEPROM buffer.

## Risks
Efuse reads use polling and fixed 16-byte rows; timeout blocks probe. Cal-free merge is gated by DT and validity checks, but wrong DT can blend incompatible calibration. Invalid external EEPROM is silently replaced by OTP when available. `is_mt7688()` reads an efuse register directly and affects antenna count, so incorrect detection reduces throughput.

## Test Signals
Probe devices with external flash EEPROM, efuse-only data, cal-free merge enabled/disabled, MT7628/MT7688 variants, and invalid MAC/chip IDs. Validate debugfs EEPROM/OTP blobs, antenna count reported by `iw phy`, and firmware txpower programming.
