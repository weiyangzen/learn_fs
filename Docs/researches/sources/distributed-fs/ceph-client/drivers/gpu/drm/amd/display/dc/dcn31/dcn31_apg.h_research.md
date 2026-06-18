# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h

Purpose: Declares the DCN31 APG base abstraction and concrete register-backed implementation.

Important APIs/types/functions: `DCN31_APG_FROM_APG()` casts from `struct apg`. `APG_DCN31_REG_LIST()` lists APG control, control2, memory power, and debug generation registers. Field macros cover reset, reset done, enable, DP audio stream id, debug channel enable, and memory power force. `struct apg_funcs` exposes setup, enable, and disable callbacks.

Control flow: No runtime flow in the header; consumers call the function table populated by `apg31_construct()`.

State/persistence: `struct apg` stores function table, context, and instance. `struct dcn31_apg` adds register/shift/mask table pointers.

Dependencies/integration: Used by DCN31 resource creation and audio path code. The header declares its own base `struct apg`, making it the local interface owner for APG users.

Risks: The include guard says `AGP` instead of `APG`, a spelling issue but functionally harmless if unique. The `setup_hdmi_audio` callback signature has no parameters beyond `struct apg *`, so HDMI support would require care if added.

Test signals: Compile coverage plus APG register programming tests for reset, enable, stream id, and memory-power fields.
