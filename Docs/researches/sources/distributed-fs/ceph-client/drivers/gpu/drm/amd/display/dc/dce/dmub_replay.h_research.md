# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_replay.h

Purpose: declares the DMUB Replay object and function table used by DC code to control Panel Replay through firmware.

Important types and APIs: `struct dmub_replay` stores a DC context and function table. `struct dmub_replay_funcs` includes state query, enable/disable, settings copy, power optimization, general command send, coasting vtotal, residency, and combined power-opt/coasting-vtotal commands. Lifecycle APIs are `dmub_replay_create()` and `dmub_replay_destroy()`.

Control flow role: callers use this vtable after allocation to setup replay context, enable/disable firmware replay, collect residency, and issue specialized firmware messages without knowing the command-union layout.

State and persistence: object state is minimal and non-owning except for allocation. Firmware owns persistent Replay state after commands are sent. Caller-provided `dc_link`, `replay_context`, and command-union inputs are consumed synchronously.

Dependencies and integration: includes `dc_types.h` and `dmub_cmd.h`, and forward-declares `struct dc_link`. It integrates with eDP Replay policy and link-service code.

Risks and test signals: API compatibility depends on `enum replay_state`, `enum replay_FW_Message_type`, `union dmub_replay_cmd_set`, and residency mode definitions in shared headers. Test signals include lifecycle, vtable completeness, settings-copy then enable ordering, and all residency/general-command paths compiling across firmware command revisions.
