# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-controls.h

## Purpose
`ivtv-controls.h` exposes the ivtv control operation tables and decoder timing helper to the rest of the driver.

## Important APIs, Types, and Functions
It declares `ivtv_cxhdl_ops`, `ivtv_hdl_out_ops`, and `ivtv_g_pts_frame(struct ivtv *itv, s64 *pts, s64 *frame)`.

## Control Flow
The header has no executable control flow. `ivtv-driver.c` wires these ops into the cx2341x and V4L2 control handlers during probe, and control callbacks later call into firmware, subdevs, and VBI state.

## State and Persistence
No state is stored here. The declarations operate on `struct ivtv` state owned by `ivtv-driver.h`.

## Dependencies and Integration Points
Consumers must include this after the core ivtv types are visible. It links control setup in `ivtv-driver.c` with the implementation in `ivtv-controls.c` and with ioctl/control users that need timing values.

## Risks and Edge Cases
The header is small, so risk is primarily ABI drift inside the driver: changing operation names or callback signatures without updating probe and control setup will break compilation. `ivtv_g_pts_frame()` depends on decoder firmware state even though that dependency is not visible from the prototype.

## Test Signals
Build coverage should confirm the operation tables match V4L2 and cx2341x callback signatures. Runtime signals are successful control handler initialization and valid decoder PTS/frame control reads.
