# sources/distributed-fs/ceph-client/include/uapi/linux/surface_aggregator/dtx.h

## Purpose
Defines the `/dev/surface/dtx` userspace ABI for Surface Book clipboard/base detachment control and event reporting.

## Important APIs, Types, and Constants
Status category macros include `SDTX_STATUS`, `SDTX_ERR_RT`, `SDTX_ERR_HW`, `SDTX_UNKNOWN`, `SDTX_CATEGORY`, and `SDTX_SUCCESS`. Values cover latch open/closed, base detached/attached, runtime errors such as infeasible or timed-out detach, and hardware errors. Base type macros distinguish HID and SSH bases. `enum sdtx_device_mode` describes tablet, laptop, and studio modes. `struct sdtx_event` is a variable-length read event, `enum sdtx_event_code` names request/cancel/base/latch/mode events, and `struct sdtx_base_info` returns connection state and base id. Ioctls enable events, lock/unlock/request/confirm/heartbeat/cancel latch operations, and query base info, device mode, and latch status.

## Control Flow, State, and Persistence
Userspace enables events, reads event stream records, and drives detach through request, confirm, heartbeat, and cancel ioctls. Kernel/device state includes latch state, base connection, detach feasibility, and current mode.

## Dependencies and Integration Points
Depends on ioctl and fixed-width types. Integrates with Surface DTX driver, SSAM/EC communication, and desktop detach policy agents.

## Risks and Test Signals
Risks include wrong sequencing of latch operations, unknown future event codes, critical hardware error handling, and packed variable-length event parsing. Test successful and failed detach state machines, event enable/disable, unknown event skipping, base info queries, and privilege checks.
