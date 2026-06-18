<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.h

Purpose: MT76x2 MAC helper declarations. It exposes MAC stop and an inline resume helper that re-enables MAC TX/RX.

Important APIs/types/functions: `mt76x2_mac_stop()` and `mt76x2_mac_resume()`.

Control flow: declarative header with one inline register write for resume. Channel switch and reset paths stop MAC, adjust PHY/channel, then resume.

State and persistence: resume writes `MT_MAC_SYS_CTRL_ENABLE_TX|RX`; stop implementation manipulates MAC/BBP state.

Dependencies/integration: included by `mt76x2.h` and PCI/PHY code; depends on shared register definitions through mt76x2 includes.

Risks: callers must pair stop/resume under appropriate locks/tasklet disable; resume without reinitializing RX filter/DMA can expose stale state. Test signals include channel switch, calibration stop/resume, and watchdog recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.h -->
