# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/mem-events.h

Purpose: Defines architecture memory event aliases for `perf mem`.

Important APIs/types/functions: `_ARM64_MEM_EVENTS_H`.

Control flow: Populates `perf_mem_event` entries with tag, display name, PMU event string, default load latency, and auxiliary-event flag.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on PMU event names exposed by the architecture and common perf mem code.

Risks: Stale event names fail at record time or silently omit expected memory operations.

Test signals: Run `perf mem record/list` on supported systems and verify alias expansion.

Source coverage: researched from the complete local file (8 lines, 202 bytes).
