## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_sched.h

### Purpose
`etnaviv_sched.h` declares the small scheduler interface between submit code and GPU scheduler implementation.

### Important APIs, Types, And Functions
The inline `to_etnaviv_submit()` converts a `struct drm_sched_job` to its containing `struct etnaviv_gem_submit`. The header declares `etnaviv_sched_init()`, `etnaviv_sched_fini()`, and `etnaviv_sched_push_job()`.

### Control Flow
No standalone control flow exists beyond the container conversion helper.

### State, Persistence, And Dependencies
The header depends on `<drm/gpu_scheduler.h>` and forward declarations for Etnaviv GPU/submit types. It encodes the structural invariant that `struct etnaviv_gem_submit` contains a member named `sched_job`.

### Integration Points
Submit, GPU bind/unbind, and scheduler implementation all include this header. It is the narrow public surface for initializing the scheduler and enqueueing jobs.

### Risks
Changing the submit structure member name or embedding pattern breaks `to_etnaviv_submit()`. The header must stay minimal to avoid circular includes between submit, GPU, and scheduler files.

### Test Signals
Compile coverage is the primary signal. Runtime validation comes from successful submit enqueue, scheduler timeout, and free-job callbacks using the conversion helper.
