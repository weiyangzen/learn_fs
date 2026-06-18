# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_init.c

## Purpose
`dcn32_init.c` constructs the public and private hw sequencer function tables for DCN32. It is the binding layer that makes the DCN32-specific implementation active inside `dc->hwss` and `dc->hwseq->funcs`.

## Important APIs, types, and functions
The file defines `dcn32_funcs`, `dcn32_private_funcs`, and `dcn32_hw_sequencer_init_functions`. Public hooks bind `dcn32_init_hw`, `dcn32_unblank_stream`, `dcn32_prepare_bandwidth`, `dcn32_apply_idle_power_optimizations`, `dcn32_commit_subvp_config`, phantom stream hooks, DSC PG update, topology transition checks, pixel-divider calculation, and outstanding-update programming. Private hooks bind DCN32 transfer functions, power-gating, ODM/DSC, MALL, p-state, FIFO resync, DP pixel-rate policy, init blank, and inherited DCN10/20/30 helpers.

## Control flow
Construction is simple assignment: `dcn32_hw_sequencer_init_functions` copies the static public table into `dc->hwss` and the private table into `dc->hwseq->funcs`. Runtime behavior is entirely through later indirect calls.

## State and persistence behavior
This file initializes the callback state stored on the `dc` object. Those function pointers persist for the lifetime of the DC instance and define which generation-specific operations will be used by modeset, bandwidth, plane, stream, idle, and teardown paths.

## Dependencies and integration points
The table composes helpers from DCE110 and DCN10/20/21/30/31/32 plus a DCN401 include. It integrates DCN32 code into the common Display Core dispatch layer without duplicating inherited behavior.

## Risks and edge cases
Misbinding a callback can route a DCN32 ASIC through incompatible register sequences. Several entries are intentionally `NULL`, such as `apply_ctx_for_surface` and `does_plane_fit_in_mall`; callers must handle those omissions. The table also relies on private functions matching hardware capabilities such as DSC count, DPP/HUBP domains, DMUB support, and SubVP support.

## Test signals
Compile/link coverage catches missing symbols. Runtime validation should include modeset, plane update, idle optimization, DSC/ODM, SubVP, phantom, and link-disable scenarios that exercise the table entries rather than only direct unit-style calls.
