# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_state.h

## Purpose
Defines Iris core and instance lifecycle states, instance sub-state bitflags, and state-machine APIs.

## Important APIs And Types
- `enum iris_core_state`: DEINIT, INIT, ERROR.
- `enum iris_inst_state`: DEINIT, INIT, INPUT_STREAMING, OUTPUT_STREAMING, STREAMING, ERROR.
- `enum iris_inst_sub_state`: FIRST_IPSC, DRC, DRC_LAST, DRAIN, DRAIN_LAST, INPUT_PAUSE, OUTPUT_PAUSE, LOAD_RESOURCES.
- Public helpers include main/sub-state transitions, DRC/drain/pause helpers, command admission, and pending-state predicates.

## Control Flow And Integration Points
Included by instance, core, vb2, V4L2 command, HFI response, and codec files. The documented ASCII diagrams describe legal lifecycle movement and are implemented in `iris_state.c`.

## State And Persistence Behavior
Defines the values stored in `iris_core.state`, `iris_inst.state`, and `iris_inst.sub_state`.

## Dependencies
Uses Linux `BIT()` macro through included contexts and forward-declares `struct iris_inst`.

## Risks
The enum integer values are used in debug and state comparisons; changing order affects persisted in-memory behavior and should be treated as ABI-like inside the driver.

## Test Signals
Build coverage plus lifecycle tests through V4L2 stream-on/off and command ioctls.
