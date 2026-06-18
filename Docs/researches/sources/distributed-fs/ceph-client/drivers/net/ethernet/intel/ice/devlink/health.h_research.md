# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/health.h

## Purpose
`health.h` defines the ICE devlink health interface and the PF-owned health state container. It lets the rest of the driver initialize health reporters and report firmware health, MDD, and Tx hang events without depending on implementation details in `health.c`.

## Important APIs, Types, And Functions
`enum ice_mdd_src` names the hardware source blocks for MDD events: TX PQM, TX TCLAN, TX TDPU, and RX. `struct ice_health` stores reporter pointers for firmware, MDD, port, and Tx hang reporters, a grouped Tx hang staging buffer, and the last firmware and port admin-queue health elements.

The public functions are `ice_process_health_status_event()`, `ice_health_init()`, `ice_health_deinit()`, `ice_health_clear()`, `ice_prep_tx_hang_report()`, `ice_report_mdd_event()`, and `ice_report_tx_hang()`.

## Control Flow
Driver startup initializes `struct ice_health` as part of PF setup. Firmware AQ health events are routed to `ice_process_health_status_event()`. Tx timeout code first calls `ice_prep_tx_hang_report()` from a context where allocating or dumping may be unsuitable, then reports later via `ice_report_tx_hang()`. MDD detection calls `ice_report_mdd_event()` directly with event metadata. Reset completion calls `ice_health_clear()` to mark transient reporters healthy.

## State And Persistence
All state is runtime PF state. The grouped `tx_hang_buf` is intentionally preallocated inside `struct ice_health` to carry minimal hang metadata from constrained contexts into the devlink reporter path. Firmware and port status elements hold the last known syndrome for diagnose/dump.

## Dependencies And Integration Points
The header forward-declares admin-queue health elements, PF, Tx ring, and receive queue event info to minimize includes, but includes Linux types. It is included by `ice.h`, making `struct ice_health` part of the central `struct ice_pf` layout.

## Risks And Test Signals
Layout changes in `struct ice_health` affect `struct ice_pf`. The Tx hang buffer depends on the referenced ring remaining valid until report generation. Test signals are build coverage, successful reporter initialization/deinitialization, and devlink health dumps for each event type.
