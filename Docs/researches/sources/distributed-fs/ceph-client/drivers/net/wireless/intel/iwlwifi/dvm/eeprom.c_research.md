# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/eeprom.c

## Purpose

`eeprom.c` reads DVM-era EEPROM/OTP NVM images from hardware and parses them into `struct iwl_nvm_data` for mac80211 registration and device initialization. It translates indirect EEPROM sections, validates signatures, reads OTP linked-list images when needed, builds regulatory channel maps, computes maximum TX power, extracts MAC/radio/SKU/calibration data, and initializes supported-band/rate/HT capability structures.

## Important APIs, Types, and Functions

Externally used functions are `iwl_read_eeprom()` and `iwl_parse_eeprom_data()`. Important local helpers include `iwl_eeprom_query16()`, `eeprom_indirect_address()`, `iwl_eeprom_query_addr()`, `iwl_eeprom_read_calib()`, `iwl_get_max_txpwr_half_dbm()`, `iwl_eeprom_enh_txp_read_element()`, `iwl_eeprom_enhanced_txpower()`, `iwl_init_band_reference()`, `iwl_mod_ht40_chan_info()`, `iwl_init_channel_map()`, EEPROM semaphore helpers, signature validation, OTP access helpers, `iwl_read_otp_word()`, `iwl_is_otp_empty()`, `iwl_find_otp_image()`, and `iwl_init_sbands()`.

The file defines EEPROM offsets, indirect-section link offsets, SKU/radio masks, regulatory channel flag structures, enhanced TX power entries, static EEPROM band channel lists, and static mac80211 rate tables.

## Control Flow

`iwl_read_eeprom()` determines whether the device uses OTP or EEPROM, allocates a raw image buffer sized from hardware config, validates the signature, acquires the EEPROM semaphore, and reads 16-bit words. OTP flow activates the NIC, configures OTP access, clears ECC status, optionally traverses the OTP linked list to locate the valid image, then reads each word with ECC checks. EEPROM flow polls `CSR_EEPROM_REG` for valid data for each address. All success paths release the semaphore and return the blob.

`iwl_parse_eeprom_data()` allocates flexible `iwl_nvm_data`, reads MAC address count, calibration header, crystal and temperature calibration values, radio config masks, SKU capabilities, NVM version, optional antenna overrides, validates nonzero antennas, then calls `iwl_init_sbands()`. Channel initialization loops through regulatory bands 1-5 to add valid 2.4/5 GHz channels and set `NO_IR`, `RADAR`, `NO_HT40`, and max power. Enhanced TX power entries may raise per-channel max power and set `max_tx_pwr_half_dbm`; otherwise channel limits are used. HT40 bands 6-7 clear HT40 plus/minus restrictions where EEPROM permits.

## State and Persistence Behavior

The raw EEPROM blob is owned by `priv->eeprom_blob`; parsed data is owned by `priv->nvm_data`. `iwl_nvm_data` persists MAC addresses, antenna masks, SKU flags, calibration versions/values, max power, channel array, supported bands, and HT capabilities. Hardware state touched during reads includes CSR EEPROM/OTP registers, EEPROM ownership semaphore bits, NIC activation state, OTP ECC acknowledgment bits, and shadow RAM power-management disables.

## Dependencies and Integration Points

The file depends on transport register access (`iwl_read32()`, `iwl_write32()`, `iwl_poll_bits()`), CSR/PRPH constants, `iwl_trans_activate_nic()`, NVM utility helpers `iwl_init_sband_channels()` and `iwl_init_ht_hw_capab()`, mac80211 channel/rate structures, module parameters such as `disable_11n`, and per-device `cfg->eeprom_params`.

## Risks and Edge Cases

Most accessors use `WARN_ON()` for bounds and return zero/NULL, so malformed NVM can degrade into parse failure or wrong defaults. `iwl_eeprom_enhanced_txpower()` assumes the TX power length pointer is valid before dereferencing. OTP reads must handle correctable and uncorrectable ECC differently; uncorrectable ECC aborts, correctable ECC logs and continues. OTP linked-list traversal depends on `max_ll_items` and skips the link pointer by adding two bytes. Regulatory correctness depends on EEPROM flags and enhanced TX power data being interpreted precisely.

## Test Signals

Test with EEPROM and OTP devices, shadow-RAM and non-shadow-RAM OTP, bad signature cases, semaphore timeout injection, OTP ECC injection, truncated/malformed blobs, antenna override configs, 2.4/5 GHz channel count validation, HT40 enablement checks, enhanced TX power parsing, and NVM version rejection in `main.c`.
