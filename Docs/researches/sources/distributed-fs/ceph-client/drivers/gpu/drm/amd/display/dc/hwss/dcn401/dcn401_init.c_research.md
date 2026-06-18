# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_init.c

## Purpose
`dcn401_init.c` installs the DCN401 hardware sequencer vtables. It maps the generic DC hardware sequencing contract to a mix of DCN401-specific functions and inherited helpers from DCE110, DCN10, DCN20, DCN21, DCN30, DCN31, DCN32, and DCN35.

## Important APIs and Tables
- `static const struct hw_sequencer_funcs dcn401_funcs` is the public sequencer dispatch table stored into `dc->hwss`.
- `static const struct hwseq_private_funcs dcn401_private_funcs` is the private sequencer dispatch table stored into `dc->hwseq->funcs`.
- `dcn401_hw_sequencer_init_functions(struct dc *dc)` performs the assignment.

The table selects DCN401 implementations for hardware init, gamut remap, front-end programming, post-unlock programming, stream enable/unblank, bandwidth prepare/optimize/update, cursor position/offload pipe update, idle power optimization, link disable, DCC metadata wait, DMUB hardware locks, FAMS2, pipe change detection, plane/MPCC/writeback sequence helpers, ODM sequence helpers, MALL sequence, and recovery hooks. It reuses mature earlier-generation helpers for context application, plane address update, DCHUB update, infoframes, audio, DRR, status, eDP controls, writeback immediate functions, VM/system context, GSL flip control, phantom streams, DCS power gating, and several workarounds.

## Control Flow and State Behavior
The file has no runtime control flow beyond initialization. Its state effect is decisive: after `dcn401_hw_sequencer_init_functions()` runs, every later commit path invokes the selected function pointers. `NULL` entries are also meaningful; for example `apply_ctx_for_surface`, `does_plane_fit_in_mall`, `calculate_dccg_k1_k2_values`, and private `populate_mcm_luts` are intentionally absent.

## Dependencies and Integration Points
This file integrates DCN401 with the generic Display Core by including the headers for all reused generation helpers. It is typically called during DC resource construction for the ASIC. Because it mixes generations, behavioral changes in inherited helpers can affect DCN401 even when this file is unchanged.

## Risks and Test Signals
Risks center on vtable mismatches and stale inherited behavior. A wrong function pointer can cause subtle ordering regressions, especially between immediate and sequence variants. Build coverage validates signatures; runtime test signals include full display bring-up, modesets, suspend/resume, multi-plane commits, link enable/disable, cursor offload, FAMS2/idle power, and sequence-enabled paths.
