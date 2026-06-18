<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nvidia,tegra194-ccplex.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nvidia,tegra194-ccplex.yaml

## Purpose
This binding describes the `cpus` node-level NVIDIA Tegra194 CPU complex, including a BPMP phandle used to query CPU operating point data.

## Important APIs, Types, And Functions
It requires `$nodename = cpus`, compatible `nvidia,tegra194-ccplex`, and optional `nvidia,bpmp` phandle. The example contains Carmel CPU child nodes using PSCI enable-method.

## Control Flow
Validation applies to the `cpus` node rather than the root. Additional properties are allowed so standard CPU topology and child CPU nodes can coexist.

## State And Persistence
The DT records CPU-complex identity and firmware link to BPMP. Runtime state is managed by CPU, PSCI, cpufreq/OPP, and BPMP drivers.

## Dependencies And Integration Points
It integrates with Tegra BPMP firmware bindings, CPU nodes, PSCI, and operating point discovery.

## Risks
Missing or wrong BPMP phandle can prevent CPU OPP queries. Applying the compatible to the wrong node name would fail schema validation and driver expectations.

## Test Signals
`dtbs_check` validates `cpus` node shape; CPU enumeration and cpufreq/OPP probing validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nvidia,tegra194-ccplex.yaml -->
