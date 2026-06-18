# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_freesync.h

Purpose: declares the FreeSync/VRR module interface and the shared VRR parameter structures used by AMD display code.

Important APIs/types: `struct mod_freesync` is opaque. `struct mod_freesync_caps` reports support and min/max refresh in microhertz. `enum mod_vrr_state` models unsupported, disabled, inactive, active variable, and active fixed states. `struct mod_freesync_config` is the input policy surface. `struct mod_vrr_params` stores computed timing adjustment, fixed-refresh, BTR, flip-interval workaround, and info-frame state.

Control flow role: the header declares lifecycle (`mod_freesync_create`, `mod_freesync_destroy`), packet construction (`mod_freesync_build_vrr_infopacket`), parameter calculation (`mod_freesync_build_vrr_params`), preflip/vupdate handlers, nominal field-rate and vtotal calculation helpers, and `mod_freesync_get_freesync_enabled`.

State and persistence: module state is external/opaque; callers persist `mod_vrr_params` across flips and vupdates. Counters in BTR/fixed/flip-interval substructures track frame insertion, ramping, and workaround detection.

Dependencies and integration: includes `mod_shared.h` and references DC stream/plane/timing types and `dc_info_packet`. It integrates FreeSync with info-packet building, timing adjustment, and display-manager update cadence.

Risks: units are mixed but explicit (`uhz`, `us`); wrong conversions can break VRR range, BTR, or fixed refresh. The legacy `mod_freesync_caps` TODO indicates compatibility debt.

Test signals: VRR state transitions, BTR frame insertion, ramp completion, flip-interval workaround cleanup, info-packet generation for each packet type, and refresh/vtotal conversion boundaries.
