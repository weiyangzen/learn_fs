<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_event.h

Purpose: Defines the PowerPC perf event configuration bit used to request Event Based Branching.

Important APIs/types/functions: `PERF_EVENT_CONFIG_EBB_SHIFT` as bit 63 of `perf_event_attr.config`.

Control flow: Userspace sets bit 63 in perf config; PowerPC perf code interprets it as an EBB request during event creation.

State and persistence: No state here; it controls per-event perf configuration state.

Dependencies and integration points: Integrated with perf_event ABI and PowerPC PMU/EBB implementation.

Risks: The high bit must not collide with raw PMU event encoding. Misinterpretation can enable wrong event delivery mode.

Test signals: perf EBB selftests, event creation validation, and perf tool compile tests.

Source read size: 19 lines, 565 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_event.h -->
