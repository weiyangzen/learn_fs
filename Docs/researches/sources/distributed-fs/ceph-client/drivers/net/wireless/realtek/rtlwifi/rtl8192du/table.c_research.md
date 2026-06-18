# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/table.c

Purpose: Provides RTL8192DU constant hardware programming tables for MAC, BB/PHY, RF, AGC, internal-PA RF, and power-index initialization.

Important data exports: `rtl8192du_phy_reg_2tarray`, `rtl8192du_phy_reg_array_pg`, `rtl8192du_radioa_2tarray`, `rtl8192du_radiob_2tarray`, `rtl8192du_radioa_2t_int_paarray`, `rtl8192du_radiob_2t_int_paarray`, `rtl8192du_mac_2tarray`, `rtl8192du_agctab_array`, `rtl8192du_agctab_5garray`, and `rtl8192du_agctab_2garray`.

Control flow: `phy.c` consumes the arrays with fixed strides: most are register/value pairs, while `rtl8192du_phy_reg_array_pg` is register/mask/value triples. Table selection depends on interface index, current band, and EFUSE internal-PA flags.

State and persistence: Arrays are `const`; they do not mutate software state. They initialize volatile device registers when written by `phy.c`.

Dependencies/integration: Includes `table.h` for declarations and length macros. Runtime consumers are MAC config, BB config, BB power-group config, AGC loading, and RF header-file loading in `phy.c`.

Risks: Length macros must match initializer element counts and expected stride. Opaque vendor register values are hard to review; wrong literals can break bring-up, RF performance, power limits, or calibration.

Test signals: Successful compile, probe, RF calibration, 2.4/5 GHz association, throughput/RSSI sanity, and regulatory/channel behavior.
