# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom.h

Purpose: Defines the ath9k EEPROM ABI: magic values, regulatory/control constants, per-layout packed calibration structures, common helper prototypes, and the `struct eeprom_ops` dispatch table used by hardware setup code.

Important APIs and types: Key persistent structures include `base_eep_header`, `modal_eep_header`, `ar5416_eeprom_def`, `ar5416_eeprom_4k`, and `ar9287_eeprom`. Calibration helpers include `cal_data_per_freq`, `cal_target_power_leg`, `cal_target_power_ht`, and CTL edge tables. `enum eeprom_param` provides a common query surface for MAC address words, regulatory domains, masks, gain types, open-loop control, temperature slopes, power table offsets, and antenna gain. `struct eeprom_ops` defines layout callbacks for fill, check, dump, board programming, optional ADDAC programming, TX power programming, spur lookup, and EEPROM misc access.

Control flow: Silicon-specific code fills the union inside `struct ath_hw`, validates it, and exposes values through `get_eeprom()`. Hardware reset/channel changes call `set_board_values()`, `set_addac()`, and `set_txpower()` through the ops table. Static inline `ath9k_hw_fbin2freq()` and `ar5416_get_ntxchains()` are used by shared calibration math.

State and persistence: The packed structs mirror persistent EEPROM/flash/firmware contents and must stay byte-layout compatible with device calibration images. Runtime callbacks interpret that data but do not persist changes back to NVRAM.

Dependencies and integration points: Includes shared ath definitions, cfg80211 regulatory types, and AR9003 EEPROM definitions. It is included by hardware setup, debugfs EEPROM dump code, USB HTC EEPROM helpers, and all EEPROM implementation files.

Risks: Layout drift, endian annotation mistakes, or bitfield-order changes would break calibration parsing. The duplicate `extern const struct eeprom_ops eep_ar9287_ops;` declaration is harmless for C but signals header hygiene risk. Many constants are hardware ABI values, so off-by-one array counts can become register programming errors.

Test signals: Compile all supported endian/config combinations, validate struct sizes against expected EEPROM lengths, dump base/modal EEPROM through debugfs, boot devices for each ops table, and verify regulatory domain, MAC address, chain masks, spur channels, and TX power limits.
