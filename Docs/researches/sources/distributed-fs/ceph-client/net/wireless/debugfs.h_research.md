# sources/distributed-fs/ceph-client/net/wireless/debugfs.h

## Purpose
This header gates cfg80211 debugfs registration behind `CONFIG_CFG80211_DEBUGFS`.

## Important APIs, types, and functions
When debugfs is enabled, it declares `cfg80211_debugfs_rdev_add(struct cfg80211_registered_device *rdev)`. Otherwise it provides an empty inline function with the same name.

## Control flow
Callers can unconditionally call `cfg80211_debugfs_rdev_add()` from registration code. The preprocessor selects either the real implementation or the no-op.

## State and persistence
The header stores no state and creates no files by itself.

## Dependencies and integration points
It depends on `struct cfg80211_registered_device` from cfg80211 internals and is included by `core.c`.

## Risks
The no-op must remain signature-compatible with the real function. Missing the config guard would either break builds without debugfs or accidentally expose debugfs code.

## Test signals
Build cfg80211 with `CONFIG_CFG80211_DEBUGFS=y` and without it, verifying that registration compiles and works in both cases.
