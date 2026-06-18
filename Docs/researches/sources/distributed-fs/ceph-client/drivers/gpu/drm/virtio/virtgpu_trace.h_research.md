<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace.h

## Purpose
`virtgpu_trace.h` declares VirtIO GPU tracepoints for command queueing and command responses on virtqueues.

## Important APIs, Types, and Functions
It defines trace system `virtio_gpu`, an event class `virtio_gpu_cmd`, and events `virtio_gpu_cmd_queue` and `virtio_gpu_cmd_response`. Captured fields include virtio device index, virtqueue index/name, command type, flags, fence ID, context ID, free descriptor count, and vbuffer sequence number.

## Control Flow
Transport code includes this header and emits queue/response events around virtqueue operations. `virtgpu_trace_points.c` instantiates the tracepoints by defining `CREATE_TRACE_POINTS`.

## State and Persistence Behavior
Tracepoints do not own driver state. They expose snapshots of command headers and queue state to ftrace/perf consumers.

## Dependencies and Integration Points
The header depends on Linux tracepoint infrastructure, virtqueue and VirtIO GPU command header definitions from `virtgpu_drv.h`, and a relative `TRACE_INCLUDE_PATH` for generated trace code.

## Risks
Trace fields must remain safe to read at emit time. The relative include path is fragile if the source tree layout changes. Adding fields changes trace ABI expectations for tooling.

## Test Signals
Build with tracing enabled, enable both trace events during command submission, and verify decoded type/fence/context/queue fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_trace.h -->
