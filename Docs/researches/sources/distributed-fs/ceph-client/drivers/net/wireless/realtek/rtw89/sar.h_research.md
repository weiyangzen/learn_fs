# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/sar.h

Purpose: public SAR/TAS interface for the rtw89 driver.

Important APIs/types: defines MAC TX power clamp range `RTW89_SAR_TXPWR_MAC_MIN/MAX`, `struct rtw89_sar_parm` for center frequency, TX-stream count, and optional RF-path forcing, and `struct rtw89_sar_handler` for source-specific SAR query callbacks. Exports `rtw89_sar_capa` for cfg80211 and prototypes for SAR query/printing, cfg80211 SAR application, TAS reset/scan/channel hooks, firmware timer control, init, and tracking.

Control flow/integration: consumers build `rtw89_sar_parm` and call `rtw89_query_sar()` during chip TX-power setup. Debugfs-style printers call `rtw89_print_sar()` and `rtw89_print_tas()`. mac80211 operations route set-SAR into `rtw89_ops_set_sar_specs()`.

State and persistence: this header declares interfaces only; state is carried in `struct rtw89_dev` members from `core.h`.

Dependencies: includes `core.h` for driver-wide types, RF path, ntx, channel state, and device definitions.

Risks/test signals: header/API changes affect chip TX-power code, debug output, and cfg80211 operation registration. Build tests should catch signature drift; runtime tests should confirm callers hold the wiphy lock where implementation requires it.
