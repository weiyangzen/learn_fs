<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/pmu.yaml

## Purpose
This schema describes ARM CPU Performance Monitor Unit nodes used for counting CPU and cache events.

## Important APIs, Types, And Functions
The `compatible` enum covers many ARM, Apple, Qualcomm, NVIDIA, Samsung, Broadcom, Cavium, and Ampere/APM PMUs. Optional properties include `interrupts`, `interrupt-affinity`, Qualcomm `qcom,no-pc-write`, and `secure-reg-access` for ARMv7 secure-state setup.

## Control Flow
Validation requires only `compatible`; interrupt properties are shape-checked when present. `additionalProperties: false` makes the PMU node strict.

## State And Persistence
The DT records PMU identity and interrupt routing. Runtime state is in perf/PMU drivers and hardware counters.

## Dependencies And Integration Points
It integrates with interrupt controller bindings, CPU phandles for affinity, and Linux perf PMU drivers.

## Risks
Incorrect interrupt affinity causes per-CPU counter interrupts to be routed incorrectly. `secure-reg-access` is valid only for a narrow ARMv7 secure-state case and can be harmful if copied blindly.

## Test Signals
`dtbs_check` validates compatible and affinity shape. Runtime signals include PMU driver probe, perf event counting, and interrupt delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/pmu.yaml -->
