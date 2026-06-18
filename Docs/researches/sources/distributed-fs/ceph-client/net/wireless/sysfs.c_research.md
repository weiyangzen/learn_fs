# sources/distributed-fs/ceph-client/net/wireless/sysfs.c

## Purpose
`sysfs.c` registers the `/sys/class/ieee80211/<wiphy>/` class and default attributes for cfg80211 wireless PHY devices. It also provides wiphy device release, network-namespace attribution, and suspend/resume behavior for cfg80211 devices.

## Important APIs, Types, And Functions
The file defines `ieee80211_class`, attribute show handlers for `index`, `macaddress`, `address_mask`, `addresses`, and `name`, `wiphy_dev_release()`, optional PM callbacks `wiphy_suspend()` and `wiphy_resume()`, and module-level `wiphy_sysfs_init()`/`wiphy_sysfs_exit()`. `dev_to_rdev()` converts the embedded device back to `struct cfg80211_registered_device`.

## Control Flow
Class registration installs the sysfs class with its attribute group and release function. Attribute reads format values from the owning rdev/wiphy, with `addresses_show()` returning either the permanent address or every advertised address. On suspend, cfg80211 records suspend time, tries WoWLAN suspend if configured, otherwise leaves all interfaces and calls driver suspend without WoWLAN after processing pending cfg80211 work. On resume, scan results are aged by suspend duration, driver resume is called if registered, cfg80211 work is queued, and failed resume shuts down all interfaces.

## State And Persistence
Sysfs state is the global `ieee80211_class` registration plus each wiphy's embedded device and attributes. Suspend state uses `rdev->suspend_at` and `rdev->suspended`; it also affects scan-cache timestamps via `cfg80211_bss_age()`. Device release transfers final cleanup to `cfg80211_dev_free()`.

## Dependencies And Integration Points
The file integrates with the Linux driver core, sysfs class infrastructure, network namespace operations, PM sleep hooks, rtnetlink, cfg80211 leave/shutdown helpers, work processing, BSS aging from `scan.c`, and driver suspend/resume operations from `rdev-ops.h`.

## Risks And Edge Cases
Suspend has two different paths depending on whether WoWLAN can be configured; driver return value `1` is treated as refusal and falls back to disconnecting/leaving interfaces. Lock ordering uses RTNL around wiphy work and driver PM operations. Resume failure forces interface shutdown, so callers must expect connection loss. Attribute formatting uses `sprintf()` into sysfs buffers and assumes address arrays remain stable for registered wiphys.

## Test Signals
Signals include class register/unregister success, sysfs attribute contents for single and multiple MAC addresses, namespace visibility, suspend with successful WoWLAN, suspend fallback after WoWLAN refusal, resume BSS aging, resume failure interface shutdown, and register/unregister loops under PM, lockdep, and KASAN.
