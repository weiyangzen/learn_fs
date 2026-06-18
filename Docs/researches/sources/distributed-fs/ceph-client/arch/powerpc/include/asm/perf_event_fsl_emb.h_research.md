<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_fsl_emb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_fsl_emb.h

## Purpose
This header describes Freescale embedded PMU capabilities and registration for PowerPC perf events.

## Important APIs, Types, And Functions
It defines `MAX_HWEVENTS`, event attribute bits `FSL_EMB_EVENT_VALID` and `FSL_EMB_EVENT_RESTRICTED`, threshold masks `FSL_EMB_EVENT_THRESHMUL` and `FSL_EMB_EVENT_THRESH`, `struct fsl_emb_pmu`, and `register_fsl_emb_pmu()`. The PMU struct carries name, counter count, supported event table, cache event map, and callbacks for constraints, event config, event disabling, interrupt handling, and overflow behavior.

## Control Flow
Platform PMU code fills `struct fsl_emb_pmu` and registers it. Perf core calls the callbacks to validate events, program counters, handle interrupts, and disable counters.

## State And Persistence Behavior
The PMU instance persists after registration and describes hardware event state. Per-event counter state is owned by perf core and PMU implementation.

## Dependencies And Integration Points
It depends on Linux types and hardware interrupt helpers. It integrates with Freescale embedded PMU drivers and generic perf.

## Risks And Edge Cases
Event validity/restriction bits must match hardware tables. Counter count is small. Threshold fields in event IDs must be decoded consistently by implementation callbacks.

## Test Signals
Run perf on FSL embedded CPUs, validate event rejection, restricted events, thresholds, overflow interrupts, and cache event aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_fsl_emb.h -->
