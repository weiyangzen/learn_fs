<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Amlogic SD / eMMC controller for S905/GXBB family SoCs`. The MMC 5.1 compliant host controller on Amlogic provides the interface for SD, eMMC and SDIO devices It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 4 tokens: `amlogic,t7-mmc`, `amlogic,meson-axg-mmc`, `amlogic,meson-gx-mmc`, `amlogic,meson-gxbb-mmc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `amlogic,dram-access-quirk`, `power-domains`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Neil Armstrong <neil.armstrong@linaro.org>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml -->
