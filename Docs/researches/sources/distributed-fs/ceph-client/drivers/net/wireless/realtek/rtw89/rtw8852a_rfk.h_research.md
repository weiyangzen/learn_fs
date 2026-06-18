# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk.h

## Purpose
This header declares the RTL8852A RF calibration interface used by the main chip file. It separates RFK implementation details in `rtw8852a_rfk.c` from chip operation wiring in `rtw8852a.c`.

## Important APIs, Types, and Data
- Declares one-shot/init calibration entry points: `rtw8852a_rck()`, `rtw8852a_dack()`, `rtw8852a_iqk()`, `rtw8852a_rx_dck()`, `rtw8852a_dpk()`, and `rtw8852a_tssi()`.
- Declares periodic or contextual calibration helpers: `rtw8852a_dpk_track()`, `rtw8852a_tssi_scan()`, `rtw8852a_tssi_track()`, and `rtw8852a_wifi_scan_notify()`.
- Function signatures consistently pass `struct rtw89_dev *`, PHY index, channel context index, and sometimes channel pointer or scan-start boolean.

## Control Flow and Integration
`rtw8852a.c` uses these declarations in chip callbacks:
- RFK init calls RCK, DACK, and RX DCK.
- Channel RFK calls RX DCK, IQK, TSSI, and DPK.
- Band changes call TSSI scan refresh.
- Scan notifications call Wi-Fi scan TSSI handling.
- Periodic tracking calls DPK and TSSI tracking.
The header itself has no control flow.

## State and Persistence
No state is declared in the header. Implementations mutate `rtw89_dev` calibration substructures and hardware registers. The API shape makes channel-context and PHY selection explicit for multi-channel/DBCC-aware calibration.

## Dependencies
Includes `core.h` for `struct rtw89_dev`, `enum rtw89_phy_idx`, `enum rtw89_chanctx_idx`, and `struct rtw89_chan`.

## Risks
- These prototypes are a narrow contract between chip operations and RFK internals; signature changes require coordinated updates in `rtw8852a.c`.
- Missing declarations for newly added RFK functions would push callers toward local externs or reduce compile coverage.
- The API exposes calibration at a coarse level, so ordering guarantees live in callers and implementation rather than the header.

## Test Signals
- Build coverage validates all declared functions against `rtw8852a_rfk.c`.
- Runtime RFK logs from chip callbacks confirm the declared entry points are reached during init, channel change, scan, and tracking.
