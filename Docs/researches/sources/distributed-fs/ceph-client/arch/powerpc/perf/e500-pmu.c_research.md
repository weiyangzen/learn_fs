
# sources/distributed-fs/ceph-client/arch/powerpc/perf/e500-pmu.c

## Purpose

This model driver supplies e500-family event maps and validation for the Freescale embedded PMU core.

## Important APIs, Types, And Functions

- `e500_generic_events[]` maps standard perf hardware events to e500 raw event codes.
- `e500_cache_events[][][]` maps perf cache event tuples to e500 raw event codes, with `0` unsupported and `-1` nonsensical.
- `e500_xlate_event()` validates raw event range, marks events 76-81 as restricted threshold-capable events, accepts threshold fields only for those events, and returns `FSL_EMB_EVENT_VALID` plus optional restriction/threshold bits.
- `e500_pmu` describes the PMU as `"e500 family"` with four counters and two restricted-capable counters.
- `init_e500_pmu()` checks PVR for e500v1/e500v2/e500mc/e5500, adjusts `num_events` to 256 for e500mc/e5500, and registers with `register_fsl_emb_pmu()`.

## Control Flow

At early init, PVR detection chooses whether this driver applies. If so, the PMU descriptor is registered. Later, the core calls `e500_xlate_event()` during perf event initialization and uses the generic/cache maps for standard perf event translation.

## State And Persistence

The file holds static event map tables and mutable `num_events`, changed during init for newer e500 variants. Runtime per-event/per-CPU state is managed by `core-fsl-emb.c`.

## Dependencies And Integration Points

It depends on PowerPC PVR constants, Freescale embedded event flag definitions, perf event enum values, and `register_fsl_emb_pmu()`.

## Risks And Edge Cases

Threshold bits on non-threshold events are rejected. The restricted event range must match hardware documentation. Generic cache mappings intentionally collapse or omit several cache concepts, so user-facing perf cache events may be unsupported or approximate.

## Test Signals

Test PVR-specific registration, raw events below and above `num_events`, threshold and non-threshold validation, restricted event group capacity through the core, and standard perf cache/hardware events.
