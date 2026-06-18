<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/perf_event.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/perf_event.h

**Purpose:** Acts as the Alpha architecture perf-event header placeholder. It satisfies generic include expectations without declaring extra Alpha perf interfaces here.

**Important APIs/types/functions:** Only the include guard is present.

**Control flow:** No runtime or compile-time behavior beyond preventing missing-header failures.

**State and persistence behavior:** No state.

**Dependencies and integration points:** Included by generic perf-event code when Alpha perf support is configured elsewhere.

**Risks:** Adding declarations here without matching implementation can break perf builds; leaving it empty means callers must not assume architecture-specific perf helpers.

**Test signals:** Build with `CONFIG_PERF_EVENTS` and run perf compile/smoke tests on Alpha.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/perf_event.h -->
