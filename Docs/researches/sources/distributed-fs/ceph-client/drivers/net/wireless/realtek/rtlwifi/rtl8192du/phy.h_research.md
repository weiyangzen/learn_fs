# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/phy.h

Purpose: Declares the RTL8192DU PHY service API used by USB driver glue, hardware setup, RF setup, channel switching, calibration, and power control.

Important APIs/types: Exposes BB register accessors, MAC/BB/RF configuration, RF table loading, bandwidth and channel switching, RF power-state setting, power-on/off coordination, LC/IQ calibration, IQK reload, BB/RF reconfiguration, and PA-bias initialization. It uses common rtlwifi/mac80211 types such as `struct ieee80211_hw`, `enum nl80211_channel_type`, `enum rf_content`, `enum radio_path`, and `enum rf_pwrstate`.

Control flow/integration: `sw.c` installs many functions into `rtl_hal_ops`; `rf.c` uses RF configuration and peer-PHY helpers; hardware/common rtl8192d code calls power and calibration functions during initialization and runtime.

State and persistence: The header owns no state. Implementations mutate `rtl_priv`, `rtl_hal`, `rtl_phy`, and power-save state attached to `ieee80211_hw`.

Dependencies: Relies on rtlwifi/mac80211 definitions being included before the header by C files. It has include guards and no inline logic.

Risks/test signals: Prototype drift is the main risk. Compile with `CONFIG_RTL8192DU` and exercise initialization, channel switching, and power management.
