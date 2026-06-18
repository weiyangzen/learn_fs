# sources/distributed-fs/ceph-client/net/mac80211/mesh_sync.c

## Purpose
`mesh_sync.c` implements the mesh synchronization method registry and the neighbor-offset synchronization method for mac80211 mesh interfaces. Its job is to measure TSF offset and clock drift from neighbor beacons, choose a stable offset setpoint, schedule deferred TSF adjustment work, and apply TSF corrections through driver operations.

## Important APIs, Types, and Functions
`struct sync_method` maps an IEEE 802.11 mesh sync method ID to `struct ieee80211_mesh_sync_ops`. The only registered method here is `IEEE80211_SYNC_METHOD_NEIGHBOR_OFFSET`, with `mesh_sync_offset_rx_bcn_presp()` as the beacon/probe-response receive hook and `mesh_sync_offset_adjust_tsf()` as the beacon-adjust hook. `ieee80211_mesh_sync_ops_get()` returns the ops for a configured method or `NULL`.

`mesh_sync_offset_rx_bcn_presp()` ignores non-beacon frames, obtains the receive timestamp either from hardware RX timestamp calculation or current TSF, looks up the transmitting STA, skips peers currently advertising TBTT adjustment, computes `sta->mesh->t_offset`, initializes or validates `t_offset_setpoint`, and updates `ifmsh->sync_offset_clockdrift_max` when drift is within the allowed jump threshold. `mesh_sync_offset_adjust_tsf()` compares the maximum drift against `TOFFSET_MINIMUM_ADJUSTMENT` and sets `MESH_WORK_DRIFT_ADJUST` for deferred correction. `mesh_sync_adjust_tsf()` consumes `sync_offset_clockdrift_max`, applies a bounded negative TSF delta, and uses `drv_offset_tsf()` when available or falls back to get/set TSF.

## Control Flow, State, and Persistence
The receive path records per-STA timing state: `t_offset`, `t_offset_setpoint`, and `WLAN_STA_TOFFSET_KNOWN`. The interface aggregates the largest observed positive clock drift in `ifmsh->sync_offset_clockdrift_max`, protected by `sync_offset_lock`. Beacon generation or mesh housekeeping calls the sync adjust op; if enough drift exists, a deferred work flag is set because driver TSF setters may block. The actual adjustment later subtracts either the whole maximum drift, if below a small beacon-interval fraction, or a fractional beacon interval to avoid overcorrection.

## Dependencies and Integration
This file depends on `ieee80211_i.h`, `mesh.h`, driver TSF operations in `driver-ops.h`, RX timestamp helpers, mesh config IE capability bits, STA mesh timing fields, mesh work scheduling via `wrkq_flags`, and method selection during mesh startup in `mesh.c`. It integrates with beacon/probe response processing and with the mesh work item that handles `MESH_WORK_DRIFT_ADJUST`.

## Risks
Synchronization is sensitive to timestamp quality. Without hardware RX timestamps, current TSF is only an approximation. Large offset jumps clear the known setpoint to handle peer restart/reset, but repeated noisy timestamps may prevent convergence. Only beacons are used despite the generic hook name, and TODO comments note missing support for non-peer non-MBSS neighbors. Driver TSF operations may have latency, so the margin and fractional adjustment constants are heuristic and can under- or over-correct on unusual hardware.

## Test Signals
Tests should validate method lookup, ignoring non-beacons, skipping peers with TBTT-adjusting capability, setpoint initialization, drift accumulation under `sync_offset_lock`, large-jump invalidation, minimum-adjustment filtering, deferred work flag setting, and both `offset_tsf` and get/set TSF adjustment paths. Hwsim-style tests can simulate two mesh peers with controlled timestamp drift and verify convergence without repeated large corrections.
