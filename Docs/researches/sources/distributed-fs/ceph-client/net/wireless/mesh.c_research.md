# sources/distributed-fs/ceph-client/net/wireless/mesh.c

## Purpose
This file provides cfg80211 mesh defaults and join/leave/channel setup helpers for mesh point interfaces.

## Important APIs, types, and functions
`default_mesh_config` and `default_mesh_setup` define HWMP, TTL, retry, peer link, power mode, beacon interval, DTIM, and security defaults. `__cfg80211_join_mesh()` validates mesh interface state, security support, mesh ID, driver support, CAC state, channel selection, basic rates, DFS requirements, regulatory beacon permission, then calls `rdev_join_mesh()`. `cfg80211_set_mesh_channel()` either invokes a legacy libertas driver hook or stores a preset chandef before join. `cfg80211_leave_mesh()` delegates to the driver and clears mesh state.

## Control flow
Join uses an explicitly supplied channel, then a preset channel, then the first usable non-NO_IR, non-disabled, non-radar channel. If no basic rates are set, 2.4 GHz uses 1 Mbps compatibility behavior while other bands use mandatory rates. DFS-required channels are rejected unless userspace handles DFS. Regulatory beacon permission is checked before driver join.

## State and persistence
Mesh state is stored in `wdev->u.mesh`: mesh ID, chandef, beacon interval, and preset chandef. Leave clears active ID and chandef and resets QoS map. Defaults are static const data.

## Dependencies and integration points
The file depends on channel/regulatory helpers, DFS scheduling, nl80211 mesh types, and driver `join_mesh`, `leave_mesh`, or legacy `libertas_set_mesh_channel` ops.

## Risks
Automatic channel selection must not choose radar/NO_IR/disabled channels. DFS userspace-handling requirements must be enforced before beaconing. The libertas workaround is intentionally nonstandard and should remain isolated.

## Test signals
Cover join with explicit, preset, and automatic channels; secure mesh without auth support; missing mesh ID; CAC busy; DFS-required rejection/acceptance with userspace DFS; leave cleanup; and libertas channel restrictions.
