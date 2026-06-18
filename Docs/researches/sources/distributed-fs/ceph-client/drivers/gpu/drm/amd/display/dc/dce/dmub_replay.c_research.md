# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_replay.c

Purpose: implements DMUB-backed Panel Replay control: state query, enable/disable, settings copy, power optimization, coasting vtotal, residency collection, combined power/vtotal command, and generic replay command dispatch.

Important functions: `dmub_replay_get_state()` queries firmware by GPINT. `dmub_replay_enable()` sends `DMUB_CMD__REPLAY_ENABLE` and optionally waits up to about 500 ms for state transition. `dmub_replay_copy_settings()` locates the active eDP pipe, fills hardware instance IDs and replay policy data, handles DSC/FEC and ALPM details, then sends `DMUB_CMD__REPLAY_COPY_SETTINGS`. `dmub_replay_residency()` maps residency modes to GPINT parameters with bounded retries. `dmub_replay_send_cmd()` dispatches higher-level message enum values to concrete DMUB subtypes.

Control flow: setup scans current resource context for a pipe whose stream link matches the target eDP link. It copies AUX/DIG/DPP/OTG/DPPHY instance data, line time, panel instance, debug flags, PR DPCD deviation fields, SMU/timing-sync/fast-resync options, FEC/DSC flags, sink-specific TPS3 wakeup workaround, and AUX-less ALPM timing/LTTPR data. Runtime commands are synchronous DMUB submissions; residency GPINT retries twenty times with 100 us delays before returning zero.

State and persistence: `struct dmub_replay` stores only context and function table. Firmware owns Replay runtime state and copied context. Link `replay_settings`, DPCD `pr_info`, FEC/DSC state, debug ALPM timings, and LTTPR count are captured into firmware payloads.

Dependencies and integration: depends on `link_service`, `dc_dmub_srv`, `dmub_cmd`, current DC resource context, link encoder transmitter IDs, and DC debug/capability settings. It integrates with eDP Replay feature enablement and hardware lock policy.

Risks: fixed `MAX_PIPES=6` and multi-eDP TODO mirror PSR limitations. State query retries can assert after persistent invalid state. General command dispatch silently returns for unsupported messages or null inputs. Combined command payload sizes must match firmware layouts. Test signals include Replay enable/disable waits, copy settings with no pipe, AUX-less ALPM payloads, FEC/DSC sink workaround, residency retry failure returning zero, and every `replay_FW_Message_type` branch.
