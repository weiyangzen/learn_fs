# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_rfk.h

Purpose: This header declares the public RTL8852B RF calibration entry points implemented in `rtw8852b_rfk.c`. It is the contract used by `rtw8852b.c` chip ops and channel-context callbacks to invoke RFK phases without exposing internal calibration helpers.

Important APIs and types: It includes `core.h` for `struct rtw89_dev`, `struct rtw89_chan`, `enum rtw89_phy_idx`, and `enum rtw89_chanctx_idx`. Declared functions cover RCK, DACK, IQK, RX DCK, DPK initialization/calibration/tracking, TSSI setup and scan handling, scan notifications, RF channel setting, MCC channel info capture, and RFK channel-context state callbacks.

Control flow: The header has no executable code. It enables the higher-level chip file to install RFK functions into `rtw89_chip_ops` and the channel-context listener. At runtime those call sites enter `rtw8852b_rfk.c` for initial calibration, per-channel calibration, scan TSSI updates, periodic DPK tracking, and MCC start/stop handling.

State and persistence: No state is stored in the header. The declared functions mutate `struct rtw89_dev` RFK/TSSI/DPK/IQK/DACK state and hardware registers when called.

Dependencies and integration points: Paired with `rtw8852b_rfk.c` and included by `rtw8852b.c`. It also depends on common RTW89 channel and PHY index types from `core.h`. Function signatures must remain synchronized with chip ops and channel-context listener expectations.

Risks: Declaration drift breaks builds or silently discourages use of the intended RFK lifecycle if callers switch to incomplete alternatives. Since all routines accept `struct rtw89_dev *` and enum indexes, invalid phy/channel-context arguments are only checked in deeper helper logic, so call-site discipline matters. Adding new RFK phases should preserve BTC notification, scheduler pause, and state-restore conventions used by the implementation.

Test signals: Compile/link catches missing definitions. Runtime coverage comes from chip probe initial RFK, channel RFK, scan start/end, DPK tracking, RF channel changes, and MCC channel-context callbacks. Debug output from the implementation is the main confirmation that calls reached the expected phases.
