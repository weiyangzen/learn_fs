# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/counter.json

## Purpose

This file defines the HaswellX PMU counter capacity table. It tells perf's generated PMU metadata how many fixed and generic counters are available for the core PMU and each listed uncore PMU unit.

## Important APIs, Types, And Data

The file is an array of records with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. It contains 11 units: `core` with 3 fixed and 4 generic counters; uncore `CBOX`, `HA`, `PCU`, `QPI`, `R2PCIe`, `SBOX`, and `iMC` with 4 generic counters; `IRP` and `UBOX` with 2 generic counters; and `R3QPI` with 3 generic counters. All uncore units list zero fixed counters.

This is metadata rather than an event list. Its effective API is the counter-info portion of the perf PMU event JSON schema.

## Control Flow

At build time, the PMU event generator reads counter records and emits generated counter-capacity metadata alongside event aliases. Runtime perf can use this metadata to understand PMU constraints, display PMU information, and reason about grouping pressure when scheduling events.

## State And Persistence Behavior

The file persists static hardware-capacity declarations. It does not represent allocated counters or active event groups. Runtime allocation, multiplexing, and scheduling state are maintained by perf and the kernel PMU subsystem.

## Dependencies And Integration Points

This file integrates with HaswellX model mapping, generated PMU metadata, event scheduling, and uncore unit naming. Its unit names must match event-file `Unit` values and kernel PMU naming conventions for HaswellX uncore devices.

## Risks And Edge Cases

Incorrect counter counts can make perf overestimate or underestimate how many events can be grouped without multiplexing. Unit-name mismatches can disconnect capacity metadata from the corresponding event aliases. The table is HaswellX-specific and should not be reused for desktop Haswell or later server generations.

## Test Signals

Validate JSON syntax and generation. Compare generated counter metadata against expected HaswellX PMU capacities, and run grouped `perf stat` workloads to check whether multiplexing behavior is plausible for core and uncore groups. Alias checks should confirm that units with events elsewhere in the HaswellX directory have matching counter-capacity entries.
