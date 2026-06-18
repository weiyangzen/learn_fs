# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/health.c

## Purpose
`health.c` implements ICE devlink health reporters. It converts firmware health status events, malicious-driver-detection events, and Tx hang reports into devlink health reports with diagnostic or dump payloads.

## Important APIs, Types, And Functions
`struct ice_health_status` maps firmware health status codes to user-facing descriptions, possible solutions, and labels for two auxiliary data words. `ice_health_status_lookup[]` must remain sorted because `ice_get_health_status()` uses `bsearch()`. `ice_describe_status_code()` formats syndrome, description, solution, and internal data into a `devlink_fmsg`.

Firmware and port health reporters use `ice_fw_reporter_diagnose()`, `ice_fw_reporter_dump()`, `ice_port_reporter_diagnose()`, and `ice_port_reporter_dump()` against the last stored firmware or port health element in `pf->health_reporters`. `ice_process_health_status_event()` validates the firmware-provided element count, classifies global versus PF/port event sources, stores the last element, and reports through devlink. Unknown health codes are logged at debug level as internal-only events.

MDD reporting uses `struct ice_mdd_event`, `ice_mdd_src_to_str()`, `ice_mdd_reporter_dump()`, and `ice_report_mdd_event()`. Tx hang reporting uses a pre-filled `struct ice_health_tx_hang_buf`, then `ice_report_tx_hang()` builds a dump with queue indices, descriptor pointers, descriptor binary data, and skb data.

## Control Flow
`ice_health_init()` creates MDD and Tx hang reporters unconditionally, then creates firmware and port reporters only when firmware health reporting is supported. It enables firmware health event delivery via `ice_aq_set_health_status_cfg()`. On event reception, the AQ event handler calls `ice_process_health_status_event()`, which copies relevant status data and invokes `devlink_health_report()`. `ice_health_deinit()` destroys reporters and disables firmware event delivery. `ice_health_clear()` marks MDD and Tx hang reporters healthy after reset.

## State And Persistence
The health state lives in `pf->health_reporters`: reporter pointers, the Tx hang staging buffer, and the last firmware/port health status elements. It is runtime diagnostic state only. Firmware event enablement is programmed through the admin queue and is disabled at deinit.

## Dependencies And Integration Points
This file depends on devlink health APIs, `ice_adminq_cmd.h` health status enums and event buffer structures, `ice.h` PF/ring definitions, and firmware admin queue helpers. It integrates with AQ event processing, MDD detection, Tx timeout handling, and reset recovery.

## Risks And Test Signals
Risks include the sorted lookup table requirement, event count validation, pointer lifetime for Tx hang ring/skb dump data, and the fact that firmware/port reporters are conditional on firmware support. Test signals include health event injection or firmware-triggered health reports, `devlink health show/dump/diagnose`, Tx hang report dumps with descriptor payloads, MDD reports, and clean reporter destruction on remove or reset.
