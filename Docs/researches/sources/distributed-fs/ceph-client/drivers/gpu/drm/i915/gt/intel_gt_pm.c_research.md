# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.c

### Purpose
`intel_gt_pm.c` manages GT runtime power state, suspend/resume sequencing, park/unpark behavior, user forcewake preservation, engine sanitization, and awake-time accounting.

### Important APIs, Types, And Functions
Public functions include `intel_gt_pm_init_early()`, `intel_gt_pm_init()`, `intel_gt_pm_fini()`, `intel_gt_resume_early()`, `intel_gt_resume()`, `intel_gt_suspend_prepare()`, `intel_gt_suspend_late()`, `intel_gt_runtime_suspend()`, `intel_gt_runtime_resume()`, and `intel_gt_get_awake_time()`. Key internals are `__gt_unpark()`, `__gt_park()`, `gt_sanitize()`, `wait_for_suspend()`, `user_forcewake()`, `runtime_begin()`, and `runtime_end()`.

### Control Flow
Early init creates the GT wakeref and stats seqcount. On unpark, the GT holds a display `POWER_DOMAIN_GT_IRQ`, unparks RC6/RPS, notifies PMU/GuC busyness, starts request retirement, and begins awake accounting. On park, it ends accounting, parks requests/busyness/VMA/PMU/RPS/RC6, synchronizes IRQs, and asynchronously drops the display power reference. Resume sanitizes MCR locks, uncore, faults, engines, UC, RPS, and RC6, initializes hardware, restarts engines, enables RC6/RPS/LLC, resumes UC, and restores user forcewake counts. Suspend marks bind context unready, drains requests, optionally disables power-management features for non-s2idle, and sanitizes hardware.

### State, Persistence, And Dependencies
State includes `gt->wakeref`, `gt->awake`, `gt->stats`, `gt->user_wakeref`, bind-context readiness, reset flags, RC6/RPS/LLC/UC state, and engine serials. Dependencies include runtime PM, display power domains, forcewake, IRQ synchronization, engine reset/resume hooks, request retirement, GuC busyness, PXP PM, MCR, and suspend target state.

### Integration Points
Engine submission paths hold GT wakerefs; suspend/resume and runtime PM call this file; debugfs forcewake users adjust `user_wakeref`; PMU and GuC busyness depend on park/unpark notifications.

### Risks
Suspend must not race active requests or user forcewake refs. Park/unpark ordering affects interrupt latency and display DC state behavior. Resume failure wedges the GT. Awake-time seqcount updates disable local IRQs and rely on the wakeref mutex as the associated lock.

### Test Signals
Runtime PM idle/wake cycles, system suspend/resume including s2idle and deeper sleep, forcewake debugfs open across suspend, wedged GT resume, engine resume failure, request drain timeout, and awake-time accounting are high-value signals.
