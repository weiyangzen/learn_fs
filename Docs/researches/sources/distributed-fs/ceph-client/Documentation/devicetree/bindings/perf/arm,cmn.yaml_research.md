<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,cmn.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,cmn.yaml

## Purpose
Arm CMN (Coherent Mesh Network) Performance Monitors is a performance monitoring unit binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Robin Murphy <robin.murphy@arm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/arm,cmn.yaml#`. compatible values `arm,cmn-600`, `arm,cmn-650`, `arm,cmn-700`, `arm,cmn-s3`, `arm,ci-700`. required properties `compatible`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `interrupts`, `arm,root-node`. schema refs `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `uint32`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,cmn.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,cmn.yaml -->
