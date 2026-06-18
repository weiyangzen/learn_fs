# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/tdls.h

## Purpose
Defines firmware ABI for Tunneled Direct Link Setup (TDLS) support, especially TDLS channel switching, PTI templates, peer station bookkeeping, and sequence-number handoff for firmware-generated TDLS traffic.

## Important APIs, Types, And Functions
Key definitions include `IWL_TDLS_STA_COUNT`, `enum iwl_tdls_channel_switch_type`, `iwl_tdls_channel_switch_timing`, `iwl_tdls_channel_switch_frame`, `iwl_tdls_channel_switch_cmd`, `iwl_tdls_channel_switch_notif`, `iwl_tdls_sta_info`, `iwl_tdls_config_cmd`, `iwl_tdls_config_sta_info_res`, and `iwl_tdls_config_res`.

## Control Flow
The driver configures TDLS peer state with station IDs, reserved TIDs, initial SSNs, initiator flags, and PTI request template data. For channel switch, it sends a command describing whether to request, respond and move, or just move channel; the command includes peer timing from received frames, target channel info, TX parameters, and a frame template. Firmware reports channel-switch start status and returns last sequence numbers in config responses.

## State And Persistence
Firmware persists TDLS peer configuration for up to four peers, including per-peer station IDs, reserved TX TIDs, SSN counters, initiator state, and AP-facing TX sequence state. Channel-switch command data is transient, but firmware-generated PTI and channel-switch frames depend on stored templates and offsets.

## Dependencies And Integration Points
Includes `fw/api/tx.h` for TX command parameters and `fw/api/phy-ctxt.h` for channel information. Integrates with mac80211 TDLS operations, iwlwifi station table management, off-channel scheduling, template TX, and sequence-number synchronization with host state.

## Risks
Frame template offsets must point to valid timing/PTI data inside variable payloads. Sequence-number handoff between firmware-generated frames and host queues can duplicate or skip sequence numbers if responses are ignored. TDLS channel timing is in microseconds and tied to peer-provided IEs, so unit mistakes can break off-channel rendezvous. The fixed peer count limits concurrent TDLS links.

## Test Signals
Exercise TDLS peer add/remove, PTI request generation, channel-switch request/response/move flows, off-channel duration handling, and teardown while switching. Validate sequence numbers after firmware-based TX and confirm firmware notifications match mac80211 TDLS state transitions.
