# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt.c

Purpose: Defines the RTL8852BT chip profile. It supplies HFC/DLE layouts, register maps, interrupt masks, RF kill, DIG/EDCCA, coexistence parameters, power sequencing, RFK hook ordering, chip operations, firmware metadata, and exported `rtw8852bt_chip_info`.

Important APIs and functions: Key functions are `rtw8852bt_pwr_on_func()`, `rtw8852bt_pwr_off_func()`, `rtw8852bt_bb_reset()`, `rtw8852bt_set_channel()`, `rtw8852bt_set_channel_help()`, RFK wrappers, BTC RFE setup, and WL TX power control. `rtw8852bt_chip_ops` and `rtw8852bt_chip_info` are the central integration objects.

Control flow: Probe reaches this file via `rtw8852bt_chip_info`. Power-on sequences SYS power, XTAL SI, isolation, and DMAC/CMAC enables with readiness polls. Channel changes combine common 8852Bx MAC/BB helpers with `rtw8852bt_set_channel_rf()`. RFK initialization runs DPK init, RCK, DACK, and RX DCK; per-channel RFK runs RX DCK, IQK, TSSI, and DPK with BTC notifications.

State and persistence: Mutates `rtwdev->is_tssi_mode`, `rfk_mcc`, DPK/TSSI/IQK state, BTC module info, efuse-derived RFE data, scheduler stop state, and hardware registers. Chip-info constants persist as driver-wide capability limits.

Dependencies and integration points: Uses RTW89 core, firmware, MAC, PHY, coexistence, registers, `rtw8852b_common`, and RFK APIs. `rtw8852bte.c` points PCI devices at this chip info.

Risks: Power and RFK sequences are timing-sensitive. Incorrect chip-info fields can break firmware loading, efuse parsing, DMA queues, channel contexts, or security CAM sizing.

Test signals: Firmware load for `rtw89/rtw8852bt_fw`, BTE probe, power on/off, 2G/5G channel switching, 20/40/80 MHz operation, MCC, WoWLAN stub, RFK logs, BTC notifications, and DPK/TSSI tracking.
