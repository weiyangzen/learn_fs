
# sources/distributed-fs/ceph-client/arch/powerpc/perf/8xx-pmu.c

## Purpose

This file registers a minimal no-interrupt perf PMU for PPC 8xx processors. It exposes CPU cycles, instruction count, ITLB load misses, and DTLB load misses using timebase, instruction-count support, and patched TLB miss paths rather than a conventional programmable PMC block.

## Important APIs, Types, And Functions

- `event_type()` maps generic hardware/cache perf events to internal `PERF_8xx_ID_*` identifiers.
- `get_insn_ctr()` combines the software `instruction_counter` high part with `SPRN_COUNTA` into a stable instruction counter.
- `mpc8xx_pmu_event_init()` validates that the requested event is supported.
- `mpc8xx_pmu_add()` snapshots initial counter values and enables instruction counting or patches ITLB/DTLB miss exit sites on first use.
- `mpc8xx_pmu_read()` computes deltas for timebase cycles, descending instruction count, and TLB miss counters, updating `event->count`.
- `mpc8xx_pmu_del()` reads the final value and disables the underlying instrumentation when the last user of that counter type goes away.
- `init_mpc8xx_pmu()` initializes ICTRL/CMPA/COUNTA and registers the PMU as `"cpu"`.

## Control Flow

Perf calls `event_init`, then `add` snapshots a baseline and may enable backing instrumentation. Reads recompute deltas using `local64_cmpxchg()` on `prev_count`. Deletion reads one last time, decrements per-event-type reference counts, and restores original TLB miss instructions or disables instruction counting when no users remain.

## State And Persistence

State is held in external counters `itlb_miss_counter`, `dtlb_miss_counter`, and `instruction_counter`, plus local atomic reference counts `insn_ctr_ref`, `itlb_miss_ref`, and `dtlb_miss_ref`. The file patches kernel instruction sites while TLB miss events are active. No persistent storage is used.

## Dependencies And Integration Points

It depends on PPC 8xx SPRs (`ICTRL`, `CMPA`, `COUNTA`), timebase `get_tb()`, text patching symbols for TLB miss paths, and generic perf PMU callbacks. It integrates with low-level TLB miss handlers through `patch_branch_site()` and `patch_instruction_site()`.

## Risks And Edge Cases

Instruction counting uses a high/low read loop to avoid torn values. TLB patching must be exactly paired with reference counts or the kernel may retain unnecessary instrumentation. The PMU declares `PERF_PMU_CAP_NO_INTERRUPT` and `PERF_PMU_CAP_NO_NMI`, so sampling-style expectations are not supported. The instruction delta wraps a 48-bit-style value and counts down, which is easy to regress.

## Test Signals

Test with `perf stat` for supported events, unsupported hardware/cache/raw events returning the right errors, concurrent users of the same event type, add/delete reference-count behavior, and post-delete verification that TLB miss exits are restored. Build coverage requires `CONFIG_PPC_8xx`.
