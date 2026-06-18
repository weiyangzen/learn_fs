# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/eeprom.c

## Purpose
`eeprom.c` parses the Atheros EEPROM/NVRAM layout into `ah->ah_capabilities.cap_eeprom`. It validates the header/checksum, decodes supported modes, antenna and RF settings, per-channel power calibration piers, per-rate target powers, conformance test limits, spur channels, RFKill metadata, PCIe SERDES presence, and exposes cleanup plus channel-to-EEPROM-mode mapping. The data it builds is later consumed by PHY, RF register, regulatory, TX power, RFKill, and reset code.

## Important APIs and Control Flow
`ath5k_eeprom_init()` is the top-level initializer. It calls `ath5k_eeprom_init_header()`, `ath5k_eeprom_init_modes()`, `ath5k_eeprom_read_pcal_info()`, `ath5k_eeprom_read_ctl_info()`, and `ath5k_eeprom_read_spur_chans()`. Any `AR5K_EEPROM_READ()` failure returns `-EIO`, so parse failure aborts device initialization.

Header parsing reads magic/protect/regdomain/version/header words, validates custom EEPROM sizes against a fail-safe limit, XOR-checks the data region against `AR5K_EEPROM_INFO_CKSUM`, reads versioned misc words, older OB/DB defaults, HB63 flag, RFKill GPIO/polarity, and SERDES marker. Mode parsing uses `ath5k_eeprom_read_ants()` and `ath5k_eeprom_read_modes()` for 11a/11b/11g offsets, including old-version overrides for threshold/noise defaults.

Power calibration is the file's largest state machine. `ath5k_eeprom_read_pcal_info()` selects one parser by EEPROM version/EEMAP: RF5111, RF5112, or RF2413. Each parser reads version-specific packed bitfields, frequency piers, PD gain masks, and raw curve points, then converts them to common `struct ath5k_pdgain_info` arrays through `ath5k_eeprom_convert_pcal_info_5111()`, `_5112()`, or `_2413()`. Target-rate power parsing and CTL edge parsing convert EEPROM binary channel values via `ath5k_eeprom_bin2freq()`.

## State, Dependencies, and Integration
Persistent state is `struct ath5k_eeprom_info`: mode arrays, power pier arrays, rate power tables, CTL edge tables, spur channels, and dynamically allocated `pd_curves` plus their `pd_step` and `pd_pwr` arrays. `ath5k_eeprom_detach()` releases those dynamic allocations by calling `ath5k_eeprom_free_pcal_info()` for all modes. Dependencies include the bus NVRAM read callback, `eeprom.h` constants/layout macros, `slab.h` allocation, and ath5k debug/error logging.

## Risks and Test Signals
Risks include malformed EEPROM offsets producing invalid loops, signed/unsigned bitfield interpretation errors, memory leaks on partial calibration allocation, selecting the wrong calibration format, unsupported PD-gain masks returning `-EINVAL`, and silent regulatory/power errors from misdecoded CTLs. Test signals include successful attach across EEPROM 3.x/4.x/5.x cards, valid checksum rejection logs for corrupt images, no kmemleak after failed probe/detach, sane channel pier counts, expected RFKill pin/polarity, and TX power calibration matching known hardware dumps.
