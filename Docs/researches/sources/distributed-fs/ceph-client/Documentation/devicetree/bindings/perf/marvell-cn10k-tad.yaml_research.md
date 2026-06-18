<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-tad.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-tad.yaml

## Purpose
Marvell CN10K LLC-TAD performance monitor is a performance monitoring unit binding. The Tag-and-Data units (TADs) maintain coherence and contain CN10K shared on-chip last level cache (LLC). The tad pmu measures the performance of last-level cache. Each tad pmu supports up to eight counters.  The DT setup comprises of number of tad blocks, the sizes of pmu regions, tad blocks and overall base address of the HW. Maintainers: Bhaskara Budiredla <bbudiredla@marvell.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/marvell-cn10k-tad.yaml#`. compatible values `marvell,cn10k-tad-pmu`. required properties `compatible`, `reg`, `marvell,tad-cnt`, `marvell,tad-page-size`, `marvell,tad-pmu-page-size`. notable properties `compatible`, `reg`, `marvell,tad-cnt`, `marvell,tad-page-size`, `marvell,tad-pmu-page-size`. schema refs `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `uint32`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-tad.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-tad.yaml -->
