# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.h

### Purpose
`intel_gt_requests.h` declares GT and engine request-retirement helpers.

### Important APIs, Types, And Functions
It declares `intel_gt_retire_requests_timeout()`, inline `intel_gt_retire_requests()`, engine retire init/add/fini helpers, and GT request init/park/unpark/fini helpers.

### Control Flow
Callers can request immediate best-effort retirement with timeout zero or wait for fences with a positive timeout. PM and engine code use the lifecycle helpers around GT park/unpark and engine setup.

### State, Persistence, And Dependencies
The header stores no state. It forward-declares GT, engine, and timeline structures.

### Integration Points
Used by PM, engine setup/teardown, request submission, and driver release paths.

### Risks
The inline no-timeout retirement does not wait for outstanding work, so callers that require quiescence must use the timeout API or higher-level idle waits.

### Test Signals
Build coverage and runtime request retirement behavior under active and idle workloads validate the interface.
