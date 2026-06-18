# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom.c

Purpose: Provides shared EEPROM/NVRAM helpers for ath9k calibration data loading, byte swapping, checksum/version validation, interpolation, target-power lookup, regulatory edge limiting, PDADC table generation, and EEPROM ops selection.

Important APIs and functions: `ath9k_hw_nvram_read()` abstracts reads from nvmem, firmware blob, or bus EEPROM. `ath9k_hw_nvram_swap_data()`, `ath9k_hw_nvram_validate_checksum()`, and `ath9k_hw_nvram_check_version()` validate persistent calibration contents. `ath9k_hw_get_legacy_target_powers()`, `ath9k_hw_get_target_powers()`, `ath9k_hw_get_max_edge_power()`, `ath9k_hw_get_scaled_power()`, and `ath9k_hw_get_gain_boundaries_pdadcs()` are consumed by all layout-specific EEPROM implementations. `ath9k_hw_eeprom_init()` selects `eep_ar9300_ops`, `eep_ar9287_ops`, `eep_4k_ops`, or `eep_def_ops`.

Control flow: Probe code calls `ath9k_hw_eeprom_init()`, which chooses an ops table by silicon revision, fills `ah->eeprom`, then delegates validation. Later channel setup calls shared interpolation helpers to convert calibration piers and target power records into per-channel values and PDADC curves. NVRAM read errors are logged through ath common debug/error paths.

State and persistence: The persistent input is EEPROM, flash/nvmem, or firmware-provided calibration data. Runtime state is stored in `ah->eeprom`, `ah->eep_ops`, regulatory max power, and `ah->initPDADC` for open-loop paths. The code modifies only in-memory swapped copies, not the backing NVRAM.

Dependencies and integration points: Depends on `hw.h`, bus ops, firmware/nvmem blobs, endian helpers, channel-center helpers, silicon revision macros, regulatory state, and layout structs from `eeprom.h`. It is a central dependency for `eeprom_def.c`, `eeprom_4k.c`, `eeprom_9287.c`, and AR9300 EEPROM code.

Risks: EEPROM endianness detection and `AH_NO_EEP_SWAP` handling can corrupt all following calibration if wrong. `ath9k_hw_get_gain_boundaries_pdadcs()` uses static temporary VPD tables, so callers rely on serialized hardware configuration. Boundary and interpolation math is sensitive to unused pier markers, chain counts, and half-dB units.

Test signals: Exercise nvmem, firmware-blob, USB register, and bus EEPROM reads; invalid magic and checksum failures; big-endian EEPROM data; 2 GHz and 5 GHz HT20/HT40 target interpolation; regulatory edge limits; and PDADC output for AR9285/AR9271, AR9287, and default layouts.
