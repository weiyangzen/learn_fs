<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/apm,xgene-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/apm,xgene-pmu.yaml

## Purpose
APM X-Gene SoC PMU is a performance monitoring unit binding. This is APM X-Gene SoC PMU (Performance Monitoring Unit) module. The following PMU devices are supported:    L3C            - L3 cache controller   IOB            - IO bridge   MCB            - Memory controller bridge   MC             - Memory controller Maintainers: Khuong Dinh <khuong@os.amperecomputing.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/apm,xgene-pmu.yaml#`. compatible values `apm,xgene-pmu`, `apm,xgene-pmu-v2`. required properties `compatible`, `regmap-csw`, `regmap-mcba`, `regmap-mcbb`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`, `interrupts`, `regmap-csw`, `regmap-mcba`, and 1 more. schema refs `phandle`, `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle`, `uint32`; property closure is constrained mostly by referenced schemas.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/apm,xgene-pmu.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/apm,xgene-pmu.yaml -->
