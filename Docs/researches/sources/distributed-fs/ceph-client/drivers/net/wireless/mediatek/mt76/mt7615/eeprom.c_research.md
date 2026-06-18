# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/eeprom.c

Purpose: EEPROM/efuse loading and hardware capability parsing for MT7615, MT7622, and MT7663.

Important APIs/functions: implements efuse block reads (`mt7615_efuse_read()`), OTP snapshot initialization, `mt7615_eeprom_init()`, EEPROM chip validation, band/chain capability parsing, target-power index helpers, power-delta lookup, and optional OTP calibration merge (`mediatek,eeprom-merge-otp`). Exports `mt7615_eeprom_init()`.

Control flow: EEPROM init allocates the full calibration buffer through mt76, reads efuse/OTP when present, validates the chip ID in EEPROM, falls back to OTP contents if EEPROM is invalid, otherwise marks `flash_eeprom` and optionally merges calibration-free OTP fields. It then derives band support, DBDC support, chainmask/antenna mask, copies the base MAC address, and lets mt76 apply EEPROM overrides. Power-index helpers branch by chip, band, chain, TSSI/external PA state, and 5 GHz channel group.

State and persistence: fills `dev->mt76.eeprom.data`, optional `dev->mt76.otp.data`, `dev->flash_eeprom`, `dev->dbdc_support`, `dev->chainmask`, `mphy` band capability flags, antenna/chain masks, and MAC address. EEPROM/OTP are persistent hardware data; parsed fields become runtime driver state.

Dependencies and integration: uses Linux OF properties, mt76 EEPROM helpers, register efuse access, `eeprom.h` offsets, and mac80211 band/channel types. Later init, MCU, and txpower code consume parsed chainmask, band capabilities, calibration flags, and power offsets.

Risks: efuse reads operate in 16-byte blocks and treat all-ones/invalid blocks as zero data; bad calibration can reduce performance. The fallback path copies OTP only if EEPROM validation fails, otherwise merges only selected calibration fields when explicitly requested. Chainmask parsing differs for MT7663 versus MT7615/MT7622 and relies on strap/eeprom bits being sane.

Test signals: valid EEPROM chip IDs `0x7615`, `0x7622`, or `0x7663`; expected 2 GHz/5 GHz/DBDC capabilities in wiphy; correct MAC address; sane antenna masks; txpower limits per channel; successful RX DCOC/TX DPD calibration when flash calibration bits are set.
