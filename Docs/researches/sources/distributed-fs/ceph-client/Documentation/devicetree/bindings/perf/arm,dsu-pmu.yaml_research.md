<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,dsu-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,dsu-pmu.yaml

## Purpose
ARM DynamIQ Shared Unit (DSU) Performance Monitor Unit (PMU) is a performance monitoring unit binding. ARM DynamIQ Shared Unit (DSU) integrates one or more CPU cores with a shared L3 memory system, control logic and external interfaces to form a multicore cluster. The PMU enables gathering various statistics on the operation of the DSU. The PMU provides independent 32-bit counters that can count any of the supported events, along with a 64-bit cycle counter. The PMU is accessed via CPU system registers and has no MMIO component. Maintainers: Suzuki K Poulose <suzuki.poulose@arm.com>, Robin Murphy <robin.murphy@arm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/arm,dsu-pmu.yaml#`. compatible values `arm,dsu-pmu`, `arm,dsu-110-pmu`. required properties `compatible`, `interrupts`, `cpus`. notable properties `compatible`, `interrupts`, `cpus`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,dsu-pmu.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,dsu-pmu.yaml -->
