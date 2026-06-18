# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/rf.c

## Purpose
`rf.c` programs the RTL8192SE RF6052 radio path, bandwidth, and CCK/OFDM transmit power. It turns EFUSE calibration data, regulatory mode, channel width, antenna differences, and dynamic high-power state into baseband/RF register writes.

## APIs, Types, And Functions
Public entry points are `rtl92s_phy_rf6052_config`, `rtl92s_phy_rf6052_set_bandwidth`, `rtl92s_phy_rf6052_set_ccktxpower`, and `rtl92s_phy_rf6052_set_ofdmtxpower`. Internal helpers compute OFDM/MCS power bases, clamp antenna A/B deltas, apply regulatory policy, and write the six OFDM TX power registers.

## Control Flow, State, And Persistence
Power programming starts with per-channel EFUSE power levels and `rtlphy->current_chan_bw`, then adjusts for legacy/HT20 differences and regulatory mode 0-3. Dynamic TX high-power levels can override writes to low fixed values. RF config iterates each available RF path, enables the 3-wire RF environment, calls PHY RF table programming, then restores RFENV control. Register writes persist until later channel, bandwidth, power, or reset operations.

## Dependencies And Integration Points
The file depends on `reg.h`, `def.h`, `phy.h`, `dm.h`, EFUSE fields, `rtl_set_bbreg`, `rtl_set_rfreg`, and `rtl92s_phy_config_rf`. It is called from PHY channel/bandwidth setup and dynamic management.

## Risks And Test Signals
Key risks are out-of-range power, regulatory violations, A/B path underflow/overflow, and failed RF path initialization. Test signals are successful association, expected RSSI/EVM, channel-width transitions, tx power changes under near-field dynamic power, and no RF init errors.
