# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/phy.h

Purpose: `phy.h` defines RTL8723AE PHY constants, small data structures, enums, and exported PHY/RF-control prototypes.

Important APIs/types: constants size channel-switch command arrays, IQK backup arrays, RF path count, tx-power maxima, EFUSE offsets, and calibration tolerance. Enums describe hardware register blocks, baseband config types, rate-adaptive offset areas, and antenna-path bit combinations. Structs describe antenna selection bitfields, a compact EFUSE content layout, and `tx_power_struct` for per-path/channel power indexes and MCS offsets. Prototypes expose RF register access, MAC/BB/RF config, tx-power management, scan backup, bandwidth/channel switching, IQ/LC calibration, RF path switch, IO command handling, and RF power-state changes.

Control flow: no executable flow, but constants and prototypes directly shape `phy.c` control paths. `MAX_PRECMD_CNT`, `MAX_RFDEPENDCMD_CNT`, and `MAX_POSTCMD_CNT` bound channel command arrays; IQK constants bound calibration backup and retry behavior.

State and persistence: the structures describe state later embedded in rtlwifi private structures or used as temporary views. The header itself persists no data.

Dependencies/integration: consumed by `phy.c`, `rf.c`, `hw.c`, `trx.c`, and `sw.c`. It relies on rtlwifi/mac80211 types and shared enums such as `enum radio_path`, `enum io_type`, and `enum rf_pwrstate`.

Risks: there are duplicate definitions of `IQK_ADDA_REG_NUM` and `IQK_DELAY_TIME`, and the prototype `rtl92c_phy_config_rf_with_feaderfile` appears misspelled and is not the implemented `rtl8723e_phy_config_rf_with_headerfile`. `RT_CANNOT_IO(hw)` is defined as `false`, so sleep/unload I/O protection is effectively disabled for this driver slice. EFUSE offset constants overlap with `reg.h` definitions and must stay consistent.

Test signals: compile checks for prototype consistency, channel-switch array bounds, IQK backup sizing, and tx-power structures. Runtime signals come through all `phy.c` paths that use these constants.
