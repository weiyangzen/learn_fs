# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/hw_sequencer.h

## Purpose

`hw_sequencer.h` is the public hardware sequencing contract for AMD Display Core. It ties high-level DC state transitions to ASIC-specific HWSS implementations through a large `struct hw_sequencer_funcs` vtable and a newer block-sequence layer for batching register actions, including DMUB-assisted fast paths.

## Important APIs, Types, And Functions

Key exported structures include many `*_params` wrappers, `union block_sequence_params`, `enum block_sequence_func`, `struct block_sequence`, `struct block_sequence_state`, and `struct hw_sequencer_funcs`. The vtable covers initialization, context application, plane enable/disable, pipe locking, timing synchronization, stream blanking, bandwidth, infoframes, cursor offload, color programming, VM setup, writeback, clocks, audio, link output, MALL/SubVP/FAMS, power gating, DSC, DCCG, HUBP/DPP/MPC operations, and memory QoS measurement. Helper APIs include `hwss_execute_sequence`, `hwss_build_fast_sequence`, many `hwss_*` executor functions, and many `hwss_add_*` builders that append typed block-sequence steps.

## Control Flow

The traditional path calls function pointers in `dc->hwss` for whole operations such as `apply_ctx_to_hw`, `enable_plane`, `update_dchubp_dpp`, or `pipe_control_lock`. The block-sequence path stores one enum plus a matching params union member per step, then `hwss_execute_sequence` dispatches each step to its `hwss_*` executor. Builders such as `hwss_add_hubp_setup`, `hwss_add_dsc_enable_with_opp`, and `hwss_add_optc_set_odm_combine` encode the operation and arguments without immediately touching hardware.

## State And Persistence Behavior

The header itself has no persistence, but it describes hardware-mutating callbacks. State flows through `struct dc`, `struct dc_state`, `struct pipe_ctx`, resource objects, DMUB command buffers, and per-pipe cached registers. `block_sequence_state` persists a temporary ordered command list and a step count during a commit. Runtime effects include register programming, power and clock state, stream/plane enablement, cursor updates, DWB state, ABM state, MALL/SubVP state, and debug/log snapshots.

## Dependencies And Integration Points

It depends on DC public types, clock source, timing generator, OPP, link encoder, core status, shared HW types, and DSC. It integrates with `core_types.h` through `pipe_ctx`, `dc_state`, resource objects, and the per-context block-sequence arrays. ASIC-specific HWSS files populate `hw_sequencer_funcs` and implement the block executors. DMUB, HUBP, DPP, MPC, HUBBUB, DCCG, DSC, ABM, writeback, and link code are all integration points.

## Risks And Edge Cases

The enum, union, builder functions, and executor dispatch table must remain synchronized. `MAX_HWSS_BLOCK_SEQUENCE_SIZE` scales from enum count times `MAX_PIPES`; missing bounds checks around builders would corrupt a sequence. Many callbacks are optional by ASIC generation, so callers must guard unsupported operations. Pointer-heavy params can outlive their source if sequences are retained too long. Fast DMUB/control-lock paths are sensitive to ordering, pipe topology, SubVP phantom pipes, ODM combines, DSC enablement, and pending register updates.

## Test Signals

Kernel builds catch signature drift and enum/union mismatches. Runtime validation should exercise full commits, surface-only updates, plane enable/disable, DSC/ODM transitions, cursor offload, SubVP/FAMS/MALL paths, writeback enable/disable, ABM, power-gating, and underflow recovery. Useful signals include blank-complete waits, pending-update waits, underflow debug data, visual-confirm colors, hardware-state logs, DMUB command success, and memory QoS readings.
