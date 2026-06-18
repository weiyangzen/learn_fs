<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.c

Purpose: MT76x2 EEPROM/eFUSE parser and power calibration source. It loads EEPROM/OTP, optionally merges calibration-free OTP data, validates chip IDs, reads MAC address, derives RX gain, rate-power tables, per-channel power info, and temperature compensation data.

Important APIs/types/functions: `mt76x2_eeprom_init()`, `mt76x2_read_rx_gain()`, `mt76x2_get_rate_power()`, `mt76x2_get_power_info()`, `mt76x2_get_temp_comp()`, and calibration-free helpers.

Control flow: EEPROM load initializes a 512-byte EEPROM buffer, checks EEPROM chip ID if found, allocates OTP, reads eFUSE, merges selected OTP bytes when DT property `mediatek,eeprom-merge-otp` and cal-free pattern match, or falls back to eFUSE. Init parses hardware capabilities, reads/overrides MAC, and clears local-admin-derived bit. Power helpers map channels into 5 GHz groups, select delta indexes, decode signed optional fields, and compute target/TSSI/temp data.

State and persistence: fills `dev->mt76.eeprom`, `dev->mt76.otp`, `mphy.macaddr`, band caps, and calibration RX fields. It reads persistent EEPROM/eFUSE but writes only runtime copies.

Dependencies/integration: mt76 EEPROM core, OF properties, shared mt76x02 EEPROM helpers, mt76x2 PHY/channel setup, and regulatory power initialization.

Risks: incomplete eFUSE accepted by FIXME path, DT merge policy, group/delta indexing, invalid field fallbacks, and MAC override behavior. Test signals include valid EEPROM, OTP-only boards, cal-free merge, invalid chip IDs, MAC override, 2G/5G power tables, and temp/TSSI enable bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.c -->
