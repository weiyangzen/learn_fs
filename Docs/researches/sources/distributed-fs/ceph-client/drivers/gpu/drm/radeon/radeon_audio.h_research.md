# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_audio.h

Purpose: declares the Radeon audio abstraction used by core display code and generation-specific HDMI/DP audio implementations.

Important APIs/types/functions: `struct radeon_audio_basic_funcs` abstracts endpoint register reads/writes and pin enable; `struct radeon_audio_funcs` abstracts per-encoder audio operations such as pin selection, SAD/speaker allocation writes, latency fields, DTO, ACR, packet programming, mute, mode set, and DPMS. Public prototypes include audio lifecycle hooks, endpoint accessors, pin lookup, mode/DPMS handling, DFS divider decoding, and DCE3.2 helper functions. `RREG32_ENDPOINT` and `WREG32_ENDPOINT` route endpoint register access through `rdev->audio.funcs`.

Control flow: no runtime control flow is implemented in the header. It defines callback contracts consumed by `radeon_audio.c` and generation-specific files.

State and persistence: no state is stored here. The structs describe callbacks installed into `rdev->audio` and `radeon_encoder->audio` at runtime.

Dependencies and integration: includes Linux integer types and forward-declares `struct cea_sad`. It relies on Radeon/DRM types visible to including compilation units and is shared with DCE/R600 audio implementation files.

Risks: callback signature drift will break generation-specific implementations. The macros assume a local `rdev` variable exists, which is convenient but can be error-prone in new call sites. Optional callbacks require callers to null-check before use.

Test signals: kernel build coverage across all Radeon audio generation files; runtime HDMI/DP audio mode setting that exercises callback dispatch; static analysis for macro call sites and null callback handling.
