# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_requests.c

### Purpose
`intel_gt_requests.c` handles request retirement, engine retirement work, periodic GT retirement while awake, submission flushing for idle waits, and request watchdog cancellation.

### Important APIs, Types, And Functions
Public functions are `intel_engine_init_retire()`, `intel_engine_add_retire()`, `intel_engine_fini_retire()`, `intel_gt_retire_requests_timeout()`, `intel_gt_init_requests()`, `intel_gt_park_requests()`, `intel_gt_unpark_requests()`, `intel_gt_fini_requests()`, and `intel_gt_watchdog_work()`. Internals include `retire_requests()`, `flush_submission()`, `engine_retire()`, `add_retire()`, and `retire_work_handler()`.

### Control Flow
Idle timelines are queued to an engine retirement work item using a tagged lockless list in `tl->retire`. Engine retire work tries to lock each timeline and retire completed requests. GT retirement scans `gt->timelines.active_list`, optionally waits on the last request fence with a timeout, retires requests under the timeline mutex, releases inactive timelines after dropping the list spinlock, and flushes submission/idle-barrier work before and after scanning. GT unpark schedules periodic retirement; park cancels it.

### State, Persistence, And Dependencies
State includes active timeline lists, timeline request lists, `tl->last_request`, `tl->retire`, engine retire work, engine wakeref work, GT delayed retire work, watchdog llist, and request references. Dependencies include dma fences, workqueues, timeline locking/refcounts, engine submission flushes, PM awake state, and request cancel/retire primitives.

### Integration Points
GT PM uses park/unpark and idle waits; engine code queues idle timelines; request completion and watchdog paths use this file to retire or cancel hung work; driver late release drains retirement and watchdog work.

### Risks
Retirement is best-effort when timeline mutexes are busy. List iteration temporarily drops `timelines->lock`, so reference pinning and list reset are critical. Timeout semantics feed suspend/idle decisions. Watchdog cancellation must put request references exactly once.

### Test Signals
Tests should cover idle timeline retirement, busy timeline retry, timeout waits, signal interruption through callers, park/unpark periodic work, virtual engine exclusion in `intel_engine_add_retire()`, watchdog expiry cancellation, and teardown with pending retirement work.
