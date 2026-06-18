<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/starfive,jh8100-starlink-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/starfive,jh8100-starlink-pmu.yaml

## Purpose
StarFive JH8100 StarLink PMU is a performance monitoring unit binding. StarFive's JH8100 StarLink PMU integrates one or more CPU cores with a shared L3 memory system. The PMU support overflow interrupt, up to 16 programmable 64bit event counters, and an independent 64bit cycle counter. StarFive's JH8100 StarLink PMU is accessed via MMIO. Maintainers: Ji Sheng Teoh <jisheng.teoh@starfivetech.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/starfive,jh8100-starlink-pmu.yaml#`. compatible values `starfive,jh8100-starlink-pmu`. required properties `compatible`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `interrupts`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/starfive,jh8100-starlink-pmu.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/starfive,jh8100-starlink-pmu.yaml -->
