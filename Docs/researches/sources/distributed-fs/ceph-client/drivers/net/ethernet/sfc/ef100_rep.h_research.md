<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.h

## Purpose
Defines the EF100 representor data model and public representor lifecycle/RX/lookup helpers used by EF100 MAE, TC, netdev, and RX code.

## Important APIs, Types, And Functions
- `struct efx_rep_sw_stats` contains atomic RX/TX packet, byte, drop, and error counters.
- `struct efx_rep` stores parent PF, representor netdev, mport/VF identity, pseudo-ring counters and size, default TC rule, list node, RX list/lock, NAPI object, stats, and devlink port.
- Public functions include `efx_ef100_vfrep_create()`, `efx_ef100_vfrep_destroy()`, `efx_ef100_fini_vfreps()`, `efx_ef100_rep_rx_packet()`, `efx_ef100_find_rep_by_mport()`, `efx_ef100_init_reps()`, `efx_ef100_fini_reps()`, `ef100_mport_on_local_intf()`, and `ef100_mport_is_vf()`.
- Exports `efx_ef100_rep_netdev_ops`.

## Control Flow
No implementation exists here. The declarations support representor creation/destruction from SR-IOV/MAE control paths, RX dispatch from EF100 receive processing, mport-to-representor lookup under RCU, and TC/default-rule lifecycle in `ef100_rep.c`.

## State And Persistence
The primary state contract is `struct efx_rep`, whose lifetime is bound to a representor netdevice and parent PF. Software counters are atomic because updates can occur from TX/RX paths. The RX list and pseudo-ring counters persist queued packets until NAPI drains them.

## Dependencies And Integration Points
Includes common SFC driver types and TC rule definitions. Forward-declares `struct devlink_port` and `struct mae_mport_desc` to connect representors with devlink and MAE without exposing their full definitions here.

## Risks And Edge Cases
Cross-file users must respect locking documented in comments: mport lookup callers must hold `rcu_read_lock()`. RX queue fields require `rx_lock` protection. Default-rule state is embedded, so lifecycle code must initialize and deconfigure it exactly once. Adding fields used in fast paths may require cacheline/locking review.

## Test Signals
Build coverage validates users of the declarations. Runtime signals include correct representor allocation, TC rule binding, RX delivery via `efx_ef100_rep_rx_packet()`, safe RCU lookup by mport, accurate atomic stats, and clean teardown with no list or NAPI use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.h -->
