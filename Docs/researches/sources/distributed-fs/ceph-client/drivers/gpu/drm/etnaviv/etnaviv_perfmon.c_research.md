## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_perfmon.c

### Purpose
`etnaviv_perfmon.c` implements Etnaviv performance-monitor domain discovery, signal discovery, request validation, and counter sampling. It presents pipe-specific performance counters to userspace and services submit-time PMR requests.

### Important APIs, Types, And Functions
Private table types are `struct etnaviv_pm_signal`, `struct etnaviv_pm_domain`, and `struct etnaviv_pm_domain_meta`. Public functions are `etnaviv_pm_query_dom()`, `etnaviv_pm_query_sig()`, `etnaviv_pm_req_validate()`, and `etnaviv_perfmon_process()`. Sampling helpers include `perf_reg_read()`, `pipe_select()`, `pipe_perf_reg_read()`, `pipe_reg_read()`, and model-specific HI cycle readers.

### Control Flow
Static domain tables describe 3D, 2D, and VG pipe counters. Query functions count only domains whose pipe feature bits are present in `gpu->identity.features`, then iterate domain or signal names with sentinel iterator values. Submit validation indexes the domain metadata by exec state and checks domain/signal bounds. Processing picks the requested domain and signal, invokes the signal sampling callback, and writes the sampled value into the mapped PMR buffer at the requested offset.

### State, Persistence, And Dependencies
The tables are immutable. Sampling mutates hardware profile config registers and, for multi-pixel-pipe reads, temporarily changes `VIVS_HI_CLOCK_CONTROL_DEBUG_PIXEL_PIPE`. PMR results persist in userspace-provided GEM buffers. Dependencies include generated HI profile register constants, GPU identity, `gpu->lock` for pipe selection, and submit sync-point ordering.

### Integration Points
`etnaviv_gem_submit.c` validates PMRs and maps target BOs. `etnaviv_gpu.c` invokes `etnaviv_perfmon_process()` from pre/post sync-point events with clock gating temporarily disabled and writes sequence completion values for userspace.

### Risks
Domain metadata indexing assumes exec-state constants align with the `doms_meta` order. Pipe selection must be restored to pipe 0 to avoid GPU hangs. Sampling shares profile registers with hangcheck primitive-id reads, requiring lock coordination. Offset units must match submit-side validation.

### Test Signals
Tests should query domains/signals for GPUs with 3D-only, 2D-only, and mixed features; validate invalid domain/signal ids; sample multi-pipe counters under lockdep; verify PMR pre/post sequencing; and confirm sequence writes do not clobber counter values.
