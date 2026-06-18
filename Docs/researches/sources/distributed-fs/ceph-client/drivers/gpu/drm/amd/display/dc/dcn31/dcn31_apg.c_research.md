# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.c

Purpose: Implements the DCN31 APG audio packet generator abstraction for DP audio setup, reset, enable, and disable.

Important APIs/types/functions: `apg31_construct()` initializes the object and `dcn31_apg_funcs`. `apg31_enable()` resets APG and enables it. `apg31_disable()` clears `APG_ENABLE`. `apg31_se_audio_setup()` configures stream id, channel enable, and memory power force.

Control flow: Enable asserts `APG_RESET`, waits for `APG_RESET_DONE`, deasserts reset, waits for reset done to clear, then sets `APG_ENABLE`. Audio setup ignores `az_inst`, asserts non-null `audio_info`, sets DP audio stream id to `0`, enables all debug audio channels with `0xFF`, and clears forced APG memory power off.

State/persistence: Software state is base context/instance and register metadata. Hardware state is APG reset, enable, stream id, debug channel mask, and APG memory power force.

Dependencies/integration: Provides `struct apg_funcs` used by DCN31 audio/display code. Depends on register helpers and `struct audio_info` from the display stack.

Risks: `setup_hdmi_audio` exists in the function type but is not implemented in the function table. `audio_info` content is not actually used after the null check, so speaker/channel-specific policy is elsewhere. Reset waits have fixed retry counts.

Test signals: Confirm reset sequencing, enable/disable bit writes, null `audio_info` handling, DP stream id `0`, and all-channel debug mask programming.
