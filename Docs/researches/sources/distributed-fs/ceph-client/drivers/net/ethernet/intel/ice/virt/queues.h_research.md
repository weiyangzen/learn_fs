# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/queues.h

## Purpose
Declares virtchnl queue-management handlers for VFs.

## Important APIs
Exports max frame size calculation, enable/disable queues, IRQ map config, per-queue bandwidth config, queue quanta config, queue pair config, and queue request handling.

## Control Flow and State
The header has no control flow. The implementation operates on `struct ice_vf` and virtchnl message buffers.

## Dependencies and Integration Points
Includes Linux types and forward-declares `struct ice_vf`. Included by the virtchnl dispatch layer that routes queue opcodes.

## Risks
All handlers accept raw `u8 *msg` buffers and rely on dispatch-side message size validation. Any new caller must ensure correct virtchnl payload length before invoking these functions.

## Test Signals
Compile dispatch users and test each exported opcode path with valid and malformed payloads.
