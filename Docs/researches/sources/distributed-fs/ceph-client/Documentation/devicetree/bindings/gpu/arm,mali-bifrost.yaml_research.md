<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml` defines the GPU or 2D accelerator binding titled `ARM Mali Bifrost GPU`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 23 tokens: `allwinner,sun50i-h616-mali`, `amlogic,meson-g12a-mali`, `mediatek,mt8183-mali`, `mediatek,mt8183b-mali`, `mediatek,mt8186-mali`, `mediatek,mt8365-mali`, `realtek,rtd1619-mali`, `renesas,r9a07g044-mali`, `renesas,r9a07g054-mali`, `renesas,r9a09g047-mali`, `renesas,r9a09g056-mali`, `renesas,r9a09g057-mali`, `rockchip,px30-mali`, `rockchip,rk3562-mali`, and 9 more. Top-level properties are `$nodename`, `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `mali-supply`, `sram-supply`, `operating-points-v2`, `power-domains`, `power-domain-names`, `resets`, `reset-names`, `#cooling-cells`, `dynamic-power-coefficient`, `dma-coherent`, `nvmem-cell-names`, `nvmem-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`. Pattern properties are none. The highest-risk API details are register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Rob Herring <robh@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include DRM/GPU drivers, power management, clock/reset providers, interconnects, IOMMUs, firmware loaders, and board DTS GPU nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to register region ordering, interrupt names, clock and reset topology, OPP or power-domain links, and SoC-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/arm,mali-bifrost.yaml -->
