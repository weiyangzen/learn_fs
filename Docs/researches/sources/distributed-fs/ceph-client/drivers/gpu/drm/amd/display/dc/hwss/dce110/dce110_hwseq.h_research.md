# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce110/dce110_hwseq.h

Purpose: public header for the DCE110 hardware sequencer implementation. It exposes the base DCE HWSS constructor and the subset of stream, audio, panel, bandwidth, backlight, link-output, and FBC helpers that other DCE generation files or adjacent display modules reuse.

Important APIs, types, and functions: declarations cover `dce110_hw_sequencer_construct()`, context application helpers, stream enable/disable/blank/unblank, audio stream enable/disable, info-frame updates, AV mute, accelerated-mode and power-down hooks, safe/display bandwidth hooks, eDP power/backlight/HPD helpers, backlight level and ABM helpers, link-output enable/disable helpers for LVDS/TMDS/DP, `build_audio_output()`, `translate_to_dto_source()`, `populate_audio_dp_link_info()`, and `enable_fbc()`. It forward-declares `struct dc`, `struct dc_state`, and `struct dm_pp_display_configuration`, and includes core DC and private HW sequencer types.

Control flow: the header itself has no executable flow, but it defines the reusable interface consumed by constructors in DCE60, DCE80, DCE112, DCE120, and link/display sequencing code. The primary construction flow is to call `dce110_hw_sequencer_construct(dc)` and then optionally override fields in `dc->hwss` or `dc->hwseq->funcs`.

State and persistence: no state is stored in the header. Its function signatures expose stateful objects, especially `dc`, `dc_state`, `pipe_ctx`, `dc_link`, `link_resource`, `dc_link_settings`, and `audio_output`, whose state is mutated by the implementation.

Dependencies and integration points: depends on `core_types.h` and `hw_sequencer_private.h`. It is the cross-generation contract for legacy DCE HWSS code and lets smaller generation shims reuse DCE110 behavior without duplicating the large sequencer implementation.

Risks and test signals: because it is a shared interface, signature drift or missing prototypes can break generation-specific builds or cause inconsistent hook wiring. Compile coverage across DCE60/DCE80/DCE110/DCE112/DCE120 configurations is the key test signal, followed by runtime smoke tests for any exported helper reused outside `dce110_hwseq.c`.
