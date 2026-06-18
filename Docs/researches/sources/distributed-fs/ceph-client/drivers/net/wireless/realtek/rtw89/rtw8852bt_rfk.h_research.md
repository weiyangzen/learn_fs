# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk.h

Purpose: Declares the public RTL8852BT RF calibration and RF channel-control API implemented by `rtw8852bt_rfk.c`.

Important APIs and types: Declares RCK, DACK, IQK, RX DCK, DPK init/run/track, TSSI run/scan/scan-notify, RF channel setting, MCC channel info, and RFK channel-context callback functions.

Control flow: No executable logic. The prototypes define the boundary used by `rtw8852bt.c` chip ops and channel-context listener callbacks.

State and persistence: No direct state, but signatures expose operations that depend on `phy_idx`, `chanctx_idx`, and `struct rtw89_chan`, making channel-context state part of the contract.

Dependencies and integration points: Includes `core.h`; implemented by `rtw8852bt_rfk.c`; consumed by `rtw8852bt.c`.

Risks: Signature drift breaks builds. Semantic drift around who stops TX, notifies BTC, or restores state can cause runtime RFK regressions.

Test signals: Build coverage and runtime execution of RFK hooks during init, channel change, scan, MCC, and periodic tracking.
