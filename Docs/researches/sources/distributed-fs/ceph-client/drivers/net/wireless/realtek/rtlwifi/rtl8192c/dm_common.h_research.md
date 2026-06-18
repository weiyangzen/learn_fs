# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/dm_common.h

`dm_common.h` declares shared RTL8192C dynamic-management thresholds, flags, enums, state helpers, and exported function prototypes.

Important definitions include DIG/false-alarm thresholds, OFDM/CCK swing table lengths, TX high-power levels, near-field thresholds, dynamic function flags, DM type flags, and RSSI selectors. It defines `struct swat_t` for software antenna switching state and enums for DIG operation type, CCA mode, RF saving state, and antenna switch state.

The header has no control flow. It shapes the state transitions implemented in `dm_common.c` and exposes hooks used by chip-specific PHY/DM code. It includes rtlwifi `wifi.h`, rtl8192ce `def.h`/`reg.h`, and `fw_common.h`, coupling common DM code to 8192CE naming.

Risks include threshold changes affecting sensitivity or compliance, enum/flag drift relative to `rtl_priv` fields, and dependency expansion. Test signals are build coverage for consumers plus runtime DIG, dynamic TX power, BT coexistence, RF saving, and calibration behavior.
