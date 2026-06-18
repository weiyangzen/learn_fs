# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/Kconfig

This Kconfig file defines the Broadcom wireless vendor menu. `WLAN_VENDOR_BROADCOM` is a bool defaulting to `y`; when enabled it sources `b43/Kconfig`, `b43legacy/Kconfig`, and `brcm80211/Kconfig`.

The file has no direct build output and no runtime state. Its persisted state is the `.config` value that controls whether Broadcom wireless subdriver prompts are reachable. It integrates with the parent wireless Kconfig hierarchy and organizes b43, b43legacy, and brcm80211 under one vendor gate.

The risk is reachability rather than code behavior: setting it to `n` hides all nested Broadcom wireless options even though it does not itself affect the kernel image. Test signals are Kconfig/menuconfig visibility and successful selection/build of child Broadcom drivers when the vendor symbol is enabled.
