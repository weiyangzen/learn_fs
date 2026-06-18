# sources/distributed-fs/ceph-client/net/wireless/sysfs.h

## Purpose
`sysfs.h` is the small internal declaration header for cfg80211 wiphy sysfs support.

## Important APIs, Types, And Functions
It declares `wiphy_sysfs_init()`, `wiphy_sysfs_exit()`, and the global `struct class ieee80211_class` defined in `sysfs.c`.

## Control Flow
The header has no runtime control flow. It lets cfg80211 initialization call class registration and teardown call class unregistration while allowing other code to reference the class object.

## State And Persistence
The persistent object exposed by the header is `ieee80211_class`, which exists while cfg80211 sysfs support is registered.

## Dependencies And Integration Points
The header is included by cfg80211 core/sysfs code that needs to initialize, exit, or attach devices to the ieee80211 class.

## Risks And Edge Cases
Because the header exposes a global class, initialization order must ensure users do not register wiphy devices before `wiphy_sysfs_init()` succeeds or after `wiphy_sysfs_exit()` starts.

## Test Signals
Compile coverage and cfg80211 module load/unload are the main signals; runtime class registration tests in `sysfs.c` validate the declarations indirectly.
