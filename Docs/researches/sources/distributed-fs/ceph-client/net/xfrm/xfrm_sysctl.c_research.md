# sources/distributed-fs/ceph-client/net/xfrm/xfrm_sysctl.c

## Purpose

`xfrm_sysctl.c` initializes and optionally exposes per-network-namespace XFRM sysctls under `net/core`. These knobs control async event notification thresholds, larval/acquire packet handling, and acquire-state lifetime.

## Important APIs, Types, and Functions

`__xfrm_sysctl_init()` sets defaults: `sysctl_aevent_etime = XFRM_AE_ETIME`, `sysctl_aevent_rseqth = XFRM_AE_SEQT_SIZE`, `sysctl_larval_drop = 1`, and `sysctl_acq_expires = 30`.

Under `CONFIG_SYSCTL`, `xfrm_table[]` defines `xfrm_aevent_etime`, `xfrm_aevent_rseqth`, `xfrm_larval_drop`, and `xfrm_acq_expires`. `xfrm_sysctl_init()` duplicates the table per namespace, wires each entry to the namespace's `net->xfrm` fields, hides entries from non-init user namespaces by registering a zero-sized table, and stores the registration header. `xfrm_sysctl_fini()` unregisters and frees the duplicated table. Without `CONFIG_SYSCTL`, init only applies defaults.

## Control Flow

Per-net initialization calls `xfrm_sysctl_init()` after policy/state/statistics setup. The function always initializes defaults first, then registers writable sysctls when configured. Per-net exit calls `xfrm_sysctl_fini()` in the sysctl-enabled build.

## State and Persistence Behavior

The actual persistent values are fields in `net->xfrm`, scoped to the network namespace. The sysctl table is per-namespace heap state so each table entry can point at the correct namespace fields. `sysctl_acq_expires` controls acquire state hard-add lifetime; `sysctl_larval_drop` controls whether missing-SA outbound traffic is dropped or queued; the async event knobs control replay notification behavior.

## Dependencies and Integration Points

Dependencies are sysctl infrastructure, slab allocation, net namespaces, user namespace checks, and XFRM definitions. Integration points include `xfrm_policy.c` queue/dummy bundle behavior, `xfrm_state.c` acquire timer setup, and `xfrm_replay.c` async event notification thresholds.

## Risks and Edge Cases

The sysctl table must be duplicated before assigning `.data`; sharing the static table would point all namespaces at the same fields. The unprivileged-user-namespace path registers no visible entries but still keeps defaults active. `xfrm_sysctl_fini()` assumes `net->xfrm.sysctl_hdr` is valid in the `CONFIG_SYSCTL` path, matching successful init ordering.

## Test Signals

Tests should read and write the four sysctls in the initial user namespace, verify defaults in a fresh net namespace, verify sysctls are hidden for unprivileged user namespaces, and confirm behavior changes: `xfrm_larval_drop` affects missing-SA queue/drop behavior, `xfrm_acq_expires` changes acquire expiry, and async event settings affect replay notification cadence.
