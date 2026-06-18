# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_state.c

## Purpose
Implements the Iris instance state machine and sub-state transitions for stream lifecycle, dynamic resolution change, drain, pause, and command admission.

## Important APIs And Functions
- `iris_allow_inst_state_change()` encodes legal transitions among INIT, input-streaming, output-streaming, streaming, and deinit states.
- `iris_inst_change_state()` applies a state transition, with ERROR allowed from any non-error state and no-op behavior after error.
- `iris_inst_state_change_streamon()` and `iris_inst_state_change_streamoff()` translate V4L2 plane stream-on/off into instance state transitions.
- `iris_inst_allow_sub_state()` validates sub-state bits against the current main state.
- `iris_inst_change_sub_state()` atomically clears and sets sub-state bits after conflict/range validation.
- `iris_inst_sub_state_change_drc()`, `_drain_last()`, `_drc_last()`, and `_pause()` encode higher-level DRC/drain/pause sequences.
- `iris_drc_pending()` and `iris_drain_pending()` report complete pending DRC/drain last-buffer conditions.
- `iris_allow_cmd()` gates V4L2 START/STOP decoder/encoder commands based on queue streaming state and sub-state.

## Control Flow And Integration Points
vb2 stream-on/off paths call the plane transition helpers through codec/HFI processing. HFI response handling and codec command paths set DRC/drain sub-states. `iris_vidc.c` command ioctls call `iris_allow_cmd()` before dispatching to decoder/encoder start/stop handlers. `iris_vb2.c` uses pending DRC/drain sub-states to synthesize LAST/EOS on capture buffers.

## State And Persistence Behavior
Mutates `inst->state` and `inst->sub_state`. These persist for the instance lifetime and are protected by caller-held `inst->lock` in most call paths. Error state is sticky: state-change helpers no-op once in `IRIS_INST_ERROR`.

## Dependencies
Depends on V4L2 mem2mem queue helpers and `iris_instance.h` definitions.

## Risks
- A debug message in `iris_inst_change_state()` prints `inst->state` after assignment as both old/new source; the message does not show the true old state.
- Sub-state validation uses bitmask comparisons; new sub-states must update `IRIS_INST_SUB_STATES`, allowed-state logic, and command logic.
- Incorrect DRC/drain sequencing can deadlock clients waiting for LAST/EOS or reject valid START commands.

## Test Signals
- Stream-on/off permutations for output-only, capture-only, both queues, and teardown.
- Decoder dynamic-resolution-change tests with source-change events and LAST buffer.
- Decoder/encoder drain STOP then START command tests.
- Error injection should make subsequent state transitions no-op and queue operations fail cleanly.
