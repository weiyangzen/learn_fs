# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_dcbnl.c

## Purpose
`fm10k_dcbnl.c` exposes limited IEEE DCBNL support for fm10k PF devices. It supports traffic-class priority mapping with strict priority only and PFC state tracking.

## Important APIs, types, and functions
The DCBNL ops are `fm10k_dcbnl_ieee_getets`, `fm10k_dcbnl_ieee_setets`, `fm10k_dcbnl_ieee_getpfc`, `fm10k_dcbnl_ieee_setpfc`, `fm10k_dcbnl_getdcbx`, and `fm10k_dcbnl_setdcbx`, collected in `fm10k_dcbnl_ops`. The exported `fm10k_dcbnl_set_ops` installs the ops only for PF MACs.

## Control flow
ETS get reports eight traffic classes, no CBS, zero bandwidth weights, strict TSA, and the current netdev priority-to-TC map. ETS set rejects nonzero shaping bandwidth and non-strict TSA, derives the required TC count from `prio_tc`, calls `fm10k_setup_tc` if TC count changes, and writes priority mappings. PFC get/set reads and writes `interface->pfc_en`; when running, PFC changes update RX drop enable state.

## State and persistence behavior
Persistent state is in netdev TC mappings and `interface->pfc_en`. Hardware queue mapping is updated indirectly through `fm10k_setup_tc`, and pause/drop behavior is updated through `fm10k_update_rx_drop_en`.

## Dependencies and integration points
This file depends on `CONFIG_DCB`, Linux DCBNL structs, netdev TC helpers, and fm10k PF setup paths. `fm10k.h` provides a no-op stub when DCB is disabled.

## Risks
The implementation intentionally rejects bandwidth shaping and non-IEEE DCBX modes; user tooling expecting full DCB support may fail. TC changes can reconfigure queue layout, so error propagation from `fm10k_setup_tc` matters. PFC changes affect packet drops only when propagated to running hardware.

## Test signals
Use `dcb`/`lldptool` or equivalent netlink calls to verify strict ETS only, priority mapping changes, PFC enable storage, PF-only ops installation, and queue/drop behavior after changing TC count while the interface is up.
