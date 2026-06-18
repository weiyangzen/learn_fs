## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw88xxa.c

Purpose: shared RTL8821A/8811A/8812A hardware support for rtw88, especially USB-attached 88xxa chips. It owns EFUSE interpretation, USB-oriented power-on/off, LLT and queue setup, RF/BB initialization, channel/band switching, PHY status parsing, TX power programming, false alarm counters, IQK helpers, thermal power tracking, and CCK packet detection control.

Important APIs/functions: exported entry points include `rtw88xxa_efuse_grant`, `rtw88xxa_read_efuse`, `rtw88xxa_power_on`, `rtw88xxa_power_off`, `rtw88xxa_phy_read_rf`, `rtw88xxa_set_channel`, `rtw88xxa_query_phy_status`, `rtw88xxa_set_tx_power_index`, `rtw88xxa_false_alarm_statistics`, IQK backup/restore/configure helpers, `rtw88xxa_iqk_finish`, `rtw88xxa_phy_pwrtrack`, and `rtw88xxa_phy_cck_pd_set`.

Control flow: power-on checks `RTW_FLAG_POWERON`, runs HCI setup, resets partially initialized hardware, executes chip power sequence, configures FIFO/LLT, waits/downloads firmware, loads MAC/BB/RF tables, configures queues, EDCA, aggregation, ARFR, security, PHY/DM, coexistence, then starts HCI. Power-off stops HCI, disables interrupts/RX, runs LPS/off sequences, resets MCU, and clears power state. Channel setting first switches band-specific RFE/basic-rate/CCK behavior, then writes RF channel and bandwidth registers.

State and persistence: mutates `rtwdev->efuse`, `hal`, `fifo`, `dm_info`, `flags`, register state, firmware state, and RF path configuration. EFUSE-derived RFE and USB capabilities persist in memory for later PHY decisions.

Dependencies and integration: depends heavily on `main.h`, `mac.h`, `phy.h`, `coex.h`, `efuse.h`, `usb.h`, register definitions, chip table loaders, firmware helpers, and common HCI ops. It is called from chip ops and supplies shared behavior to 8821A/8812A USB variants.

Risks and test signals: high risk areas are power sequencing timeouts, EFUSE/RFE misclassification, USB2/USB3 quirks, channel/band register programming, single-stream overrides, and thermal tracking boundaries. Test signals include successful firmware download, association on 2.4/5 GHz at 20/40/80 MHz, RF path reporting, stable suspend/remove, valid RSSI/EVM, tx power compliance, and no LLT/RF polling errors.
