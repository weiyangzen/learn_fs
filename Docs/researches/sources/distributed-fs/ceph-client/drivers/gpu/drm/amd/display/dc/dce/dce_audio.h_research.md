# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h

Purpose: declares the DCE audio hardware wrapper and the register/mask/shift lists used by ASIC-specific resource construction. It exposes construction, destruction, initialization, Azalia enable/disable/configure, and wall DTO setup entry points for the DCE audio implementation.

Important APIs and types: `AUD_COMMON_REG_LIST()` lists Azalia endpoint, codec parameter, and DCCG audio DTO registers. `AUD_COMMON_MASK_SH_LIST_BASE()`, `AUD_COMMON_MASK_SH_LIST()`, and optional `AUD_DCE60_MASK_SH_LIST()` generate bitfield metadata. `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` carry addresses and field encodings. `struct dce_audio` embeds `struct audio base` and points to those metadata tables. Public functions include `dce_audio_create()`, `dce_aud_destroy()`, `dce_aud_hw_init()`, `dce_aud_az_enable()`, `dce_aud_az_disable()`, `dce_aud_az_disable_hbr_audio()`, `dce_aud_az_configure()`, and `dce_aud_wall_dto_setup()`.

Control flow and integration: this header is consumed by resource builders that instantiate audio blocks with ASIC-specific register tables, and by `dce_audio.c` to downcast from `struct audio` to `struct dce_audio`. The header does not implement behavior; it defines the ABI between generic DC audio code and DCE-specific register programming.

State and persistence: the only persistent state described here is in-memory object state and hardware register metadata. There is no external persistence. Correctness depends on matching each ASIC's generated register list with the mask/shift list selected at compile/resource-build time.

Dependencies and risks: depends on `audio.h` for base interfaces and audio data structures. Risks are primarily table mismatch risks: a wrong register list, missing optional DTO 512-FBR fields, or DCE60 mask divergence can make the implementation write incorrect fields. Test signals include successful resource construction for each DCE/DCN generation, non-null audio callbacks, register programming traces matching expected addresses, and compile coverage for `CONFIG_DRM_AMD_DC_SI`.
