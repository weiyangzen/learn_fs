# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pub.h

Purpose: Defines the public brcmsmac common-driver API, public state, PHY/rate/channel constants, and exported control entry points used by the OS-facing layer and other brcmsmac modules.

Important APIs/types: Defines `brcms_c_rateset`, `brcms_bss_info`, `brcms_pub`, `brcms_antselcfg`, PHY type constants, bandwidth constants, RSSI thresholds, rate masks, TX/RX antenna and chain defaults, feature bitmasks, protection modes, gmode values, and all major `brcms_c_*` functions for attach/detach/up/down, interrupt handling, TX, AMPDU, module registration, MAC suspend/enable, scan, channel/rateset/power/TSF/beacon/probe/SSID operations.

Control flow and state: No executable code, but `struct brcms_pub` is the stable public portion of common driver state. It persists interface status, hardware status, unit/corerev, SI handle, association state, N/AMPDU capability flags, MAC address, radio-disabled reasons, board metadata, counters, and debugfs directory.

Dependencies and integration: Includes BCMA, `brcmu_wifi.h`, `types.h`, and `defs.h`; integrates mac80211-facing code, BMAC/core code, AMPDU, debugfs, and board/SROM state. Risks include broad coupling, duplicated constants with other headers, and ABI churn affecting many modules. Test signals include build coverage, attach/up/down, interrupt/DPC, rateset/channel/power ioctls, AP/STA/IBSS starts, beacon/probe update, and debugfs/counter visibility.
