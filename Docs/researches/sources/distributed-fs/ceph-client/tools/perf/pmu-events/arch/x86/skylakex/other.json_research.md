# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/other.json

## Purpose

`other.json` is a small Skylake Server PMU event manifest for events that do not fit the main topic files. It defines 6 aliases: four core power license/throttle events, one hardware interrupt counter, and one memory-disambiguation history reset event.

The filename gives these aliases the perf topic `other`. They are converted by `jevents.py` into generated C event entries for the SkylakeX CPU event table.

## Important Schema, APIs, and Event Families

The schema is the standard PMU event array schema. Each object includes `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and descriptions where available.

The main families are:

- `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE`, all on event `0x28` with different umasks. These classify cycles by power-delivery/turbo license level, including non-AVX/SSE/low-current AVX, AVX2-class, and AVX-512-class operation.
- `CORE_POWER.THROTTLE`, also on event `0x28`, umask `0x40`, for cycles throttled due to pending power-level requests.
- `HW_INTERRUPTS.RECEIVED`, event `0xCB`, umask `0x1`, for hardware interrupts received by the processor.
- `MEMORY_DISAMBIGUATION.HISTORY_RESET`, event `0x09`, umask `0x1`, with a terse self-description.

## Control Flow and Integration

`jevents.py` processes this as a normal event JSON file. The generated topic is `other`, the default PMU is `default_core`, and each alias is included in the SkylakeX generated event table. Users access these through `perf list other` or by naming the lower-case alias in perf event selectors.

The four `CORE_POWER.*` entries share the same event selector and are differentiated by umask, so they integrate as related aliases over one architectural event family.

## State and Persistence Behavior

The file is static metadata. The generated perf binary persists alias definitions and descriptions. Runtime counter state is owned by the PMU and perf. Default sampling periods are `200003` for core power events, `203` for hardware interrupts, and `2000003` for memory-disambiguation history resets.

## Dependencies

Dependencies include:

- Skylake Server core PMU support for event `0x28`, `0xCB`, and `0x09`.
- `jevents.py` standard event-field conversion.
- Perf alias display and runtime event parsing.

## Risks and Edge Cases

The `CORE_POWER.*` events describe license levels where turbo may be clipped; they should not be interpreted as direct package power or frequency readings. Platform firmware, AVX offset behavior, and workload instruction mix can affect interpretation.

`MEMORY_DISAMBIGUATION.HISTORY_RESET` lacks a meaningful public description, so users may have less context from `perf list` than with other aliases. Documentation-only improvements here would be low risk if event encoding remains unchanged.

The interrupt event uses a very small default sample period (`203`), which may have higher sampling overhead if used in record mode on interrupt-heavy workloads.

## Test Signals

Useful checks are:

- `jq empty other.json`.
- Build perf and verify topic `other` includes all 6 aliases.
- `perf stat -e core_power.lvl0_turbo_license,core_power.throttle <workload>` on SkylakeX hardware.
- `perf stat -e hw_interrupts.received sleep 1` to check interrupt alias programming.
