# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_init.c

## Purpose

`dcn10_init.c` wires the DCN10 hardware sequencer into the Display Core object model. It builds two static function tables: the public `hw_sequencer_funcs` installed as `dc->hwss`, and the private `hwseq_private_funcs` installed as `dc->hwseq->funcs`.

This file is the generation-specific dispatch layer for DCN10. It does little direct hardware work itself; its importance is deciding which implementation functions are used for mode-set, plane updates, power, color, timing, link, audio, logging, and diagnostics.

## Important APIs, Types, And Functions

`dcn10_hw_sequencer_construct(struct dc *dc)` is the only exported function defined here. It copies `dcn10_funcs` into `dc->hwss` and `dcn10_private_funcs` into `dc->hwseq->funcs`.

`dcn10_funcs` maps high-level hooks such as `init_hw`, `power_down_on_boot`, `apply_ctx_to_hw`, `program_front_end_for_ctx`, `post_unlock_program_front_end`, `update_plane_addr`, `program_output_csc`, `pipe_control_lock`, `interdependent_update_lock`, `prepare_bandwidth`, `optimize_bandwidth`, timing sync, stream/audio/link control, logging, cursor, clock, underflow, DCC, and visual confirm to DCN10/DCE/DCN20 routines.

`dcn10_private_funcs` maps lower-level sequencing hooks such as `init_pipes`, `plane_atomic_disconnect`, `program_pipe`, `update_mpcc`, transfer functions, power-down, blanking, reset, stream timing, vupdate interrupt, underflow, VGA disable, BIOS golden init, plane atomic power, plane power gating, DPP/HUBP power gating, HDR multiplier, and p-state verification.

## Control Flow

The construction path is simple: resource construction code calls `dcn10_hw_sequencer_construct`, after which all later DC code invokes operations indirectly through function tables. There are no branches in the constructor itself.

The table composition is meaningful. DCN10 uses `dce110_apply_ctx_to_hw`, `dce110_enable_accelerated_mode`, stream/audio/link/backlight helpers from DCE110, and `dcn20_program_front_end_for_ctx` for front-end programming. This means DCN10 dispatch is a hybrid rather than a file-local implementation set.

## State And Persistence Behavior

The file mutates only the `struct dc` function-table fields. After construction, those function pointers persist for the lifetime of the `dc` instance and determine all hardware sequencing behavior for that device. There is no dynamic allocation, file I/O, register programming, or persistent data in this file.

Several slots are explicitly set to `NULL`, such as `apply_ctx_for_surface`, private stream gating hooks, `init_blank`, and DSC power-gating control. Callers must guard optional hooks before invocation or use generation-specific fallbacks.

## Dependencies And Integration Points

The file includes `hw_sequencer_private.h`, `dce110/dce110_hwseq.h`, `dcn10/dcn10_hwseq.h`, and `dcn20/dcn20_hwseq.h`. The `dcn20` dependency is notable because DCN10's public `program_front_end_for_ctx` hook points to `dcn20_program_front_end_for_ctx`, implying a shared or backported front-end sequencing path.

It integrates with all higher-level Display Core commit code through `dc->hwss` and private hwseq dispatch. A mismapped function pointer changes runtime behavior globally for the generation.

## Risks And Edge Cases

The largest risk is table mismatch: a hook may point to a routine with subtly different assumptions than the DCN10 resource set. For example, a DCN20 front-end routine includes ODM/SubVP/update-flag concepts that must remain compatible with the DCN10 configuration it is used for in this tree.

Optional `NULL` hooks require careful checks throughout the call sites. Adding a new caller that assumes a hook is present can break DCN10.

Because many hooks are inherited from DCE110, changes in older shared helpers can affect DCN10 even if DCN10 implementation files are untouched.

## Test Signals

Build tests catch signature mismatches. Runtime smoke tests should confirm that construction occurs before any mode-set path and that every important hook invoked by DCN10 commit flows is non-NULL or intentionally guarded. Mode-set, plane update, link output, audio, cursor, color, bandwidth, and suspend/resume tests validate that the chosen cross-generation function mix is coherent.
