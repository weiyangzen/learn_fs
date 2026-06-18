# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/hw_sequencer_private.h

## Purpose

`hw_sequencer_private.h` defines private HWSS state and generation-specific helper callbacks used behind the public sequencer interface. It is the internal companion to `hw_sequencer.h`, concentrating workarounds, power-gating controls, stream/plane helper hooks, and the `struct dce_hwseq` object.

## Important APIs, Types, And Functions

Important types are `enum pipe_gating_control`, `struct dce_hwseq_wa`, `struct hwseq_wa_state`, `struct hwseq_private_funcs`, and `struct dce_hwseq`. Private callbacks cover stream gating, pipe initialization/reset, atomic plane disconnect/disable/power-down, MPCC updates, transfer functions, blanking, stream timing, vupdate interrupts, underflow checks, VGA disable, golden init, root-clock and power-gating controls, DSC power status/control, ODM/writeback programming, HDR multiplier, p-state verification, pipe programming, color LUTs, MALL, DCCG dividers, FIFO resync, controller application, and CM histogram programming.

## Control Flow

Public HWSS callbacks delegate lower-level generation details into `dce_hwseq.funcs`. Several callbacks have paired sequence-producing variants, such as atomic disconnect, blank pixel data, plane power down, update ODM, writeback programming, HDR multiplier, p-state verification, program pipe, and MALL pipe config. Workaround flags in `wa` decide whether specific code paths run, while `wa_state` records whether a workaround is currently applied.

## State And Persistence Behavior

`dce_hwseq` persists for the DC instance and stores register tables, masks/shifts, workaround configuration, current workaround state, private callbacks, and framebuffer/UMA aperture locations. Its effects are hardware state changes and in-memory workaround bookkeeping. There is no disk persistence.

## Dependencies And Integration Points

It includes `dc_types.h` and the public HWSS header. It forward-declares core DC/resource/HW objects to avoid exposing implementation headers. ASIC-specific DCE/DCN sequencer implementations initialize `dce_hwseq`, use `block_sequence_state` from the public header, and consume resources from `core_types.h`.

## Risks And Edge Cases

Workaround flags are hardware-generation-sensitive; applying them on the wrong ASIC can cause blanking, underflow, p-state, or power-gating regressions. Sequence and non-sequence callback variants must remain behaviorally equivalent. `wa_state` contains frame-sensitive state for multi-plane self-refresh transitions, so stale state can incorrectly block self refresh or skip blanking. Power/root-clock controls require strict ordering around DPP/HUBP/DSC use.

## Test Signals

Builds catch callback signature drift. Runtime tests should cover boot init, S0i3/golden init, plane atomic transitions, stream timing enable, ODM changes, MALL/SubVP programming, DSC power gating, p-state allow/disallow, underflow detection, and reset/back-end recovery. Underflow logs, power-gating status, DSC PG status, and visual or blanking artifacts are primary signals.
