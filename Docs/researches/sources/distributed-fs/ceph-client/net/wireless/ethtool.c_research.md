# sources/distributed-fs/ceph-client/net/wireless/ethtool.c

## Purpose
This file fills ethtool driver information for wireless netdevices backed by cfg80211.

## Important APIs, types, and functions
`cfg80211_get_drvinfo()` reads `dev->ieee80211_ptr`, finds the parent `wiphy` device, and fills `struct ethtool_drvinfo` fields: driver name from the parent device driver or `"N/A"`, kernel release as version, wiphy firmware version or `"N/A"`, and bus info from `dev_name(pdev)`.

## Control flow
The function performs straightforward field population with `strscpy()` and is exported for wireless drivers or netdev ethtool ops to reuse.

## State and persistence
It reads live device and wiphy metadata only. No state is changed.

## Dependencies and integration points
It depends on `linux/utsname.h`, public cfg80211 structures, and device model metadata. It integrates cfg80211 devices with ethtool `get_drvinfo`.

## Risks
The function assumes `dev->ieee80211_ptr` and its wiphy are valid for the caller. Driver and firmware strings must be bounded by `strscpy()` sizes, which the code does.

## Test signals
Call ethtool on devices with and without parent driver names and with empty/non-empty `fw_version`, verifying returned strings and bus info.
