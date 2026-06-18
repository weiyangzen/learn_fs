# subset-b-000570 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8180x-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8180x-dpu.yaml

Purpose: Devicetree binding schema for Qualcomm SC8180X Display DPU, defining the SoC-specific Qualcomm DPU display-controller node under an MDSS parent. It accepts compatible values `qcom,sc8180x-dpu`. It narrows the common DPU contract to this hardware generation by fixing register regions, clock inputs, and clock-name ordering.

Important APIs/types/functions: this is declarative JSON schema, not executable code. The key contract is `$id`, `$schema`, `$ref` to `/schemas/display/msm/dpu-common.yaml#`, local `properties` (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), required fields (none declared locally), and the `unevaluatedProperties: false` gate. Compatible matching is the schema entry point used by dt-schema and by DTS authors to select the matching DPU hardware description.

Control flow: validation first applies the common DPU schema, then checks the local `compatible` value, `reg`/`reg-names` tuples, `clocks`, and `clock-names`. Example nodes show the expected runtime graph shape: the display controller is a child of `mdss`, receives MDSS interrupts, binds power/OPP data where present, and exposes `ports`/`endpoint` links toward DSI or other display interfaces. There are 1 example block(s) that exercise the schema in dt-binding checks.

State and persistence behavior: the file persists no runtime state. It constrains source-controlled DTS data that becomes part of the kernel device tree; the resulting boot-time node supplies immutable register, clock, interrupt, power-domain, and graph topology data to the MSM DRM/DPU drivers. Any stateful display behavior is in the drivers and hardware, outside this binding.

Dependencies/integration points: integrates with `/schemas/display/msm/dpu-common.yaml#`, the containing Qualcomm MDSS schema for the same SoC family, Linux dt-schema validation, display graph `ports`, clock-controller bindings, interrupt-controller bindings, power-domain/OPP bindings, and the DRM MSM DPU driver that consumes compatible-specific catalog data. Local properties are intentionally limited so common DPU behavior remains centralized.

Risks: clock and register ordering are ABI-like details; changing them can silently misbind driver resources even when property names still look valid. Compatible fallback lists must match driver catalog support exactly. Endpoint numbering must match the DPU interface catalog and the enclosing MDSS child-node examples. Overly broad compatibles can accept DTS files for unsupported hardware, while overly strict property closure can reject valid future extensions.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8180x-dpu.yaml` and validate real board DTS files with `make dtbs_check`. Useful negative checks are missing `reg-names`, reordered clocks, unsupported compatible strings, missing graph endpoints, and accidental extra properties blocked by `unevaluatedProperties: false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8180x-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8180x-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8180x-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SC8180X Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sc8180x-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (none declared locally), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8180x-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8180x-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8280xp-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8280xp-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SC8280XP Mobile Display Subsystem, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sc8280xp-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`), required fields (none declared locally), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8280xp-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc8280xp-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm670-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm670-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SDM670 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sdm670-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm670-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm670-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm845-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm845-dpu.yaml

Purpose: Devicetree binding schema for Qualcomm Display DPU on SDM845, defining the SoC-specific Qualcomm DPU display-controller node under an MDSS parent. It accepts compatible values `qcom,sdm670-dpu`, `qcom,sdm845-dpu`. It narrows the common DPU contract to this hardware generation by fixing register regions, clock inputs, and clock-name ordering.

Important APIs/types/functions: this is declarative JSON schema, not executable code. The key contract is `$id`, `$schema`, `$ref` to `/schemas/display/msm/dpu-common.yaml#`, local `properties` (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), required fields (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), and the `unevaluatedProperties: false` gate. Compatible matching is the schema entry point used by dt-schema and by DTS authors to select the matching DPU hardware description.

Control flow: validation first applies the common DPU schema, then checks the local `compatible` value, `reg`/`reg-names` tuples, `clocks`, and `clock-names`. Example nodes show the expected runtime graph shape: the display controller is a child of `mdss`, receives MDSS interrupts, binds power/OPP data where present, and exposes `ports`/`endpoint` links toward DSI or other display interfaces. There are 1 example block(s) that exercise the schema in dt-binding checks.

State and persistence behavior: the file persists no runtime state. It constrains source-controlled DTS data that becomes part of the kernel device tree; the resulting boot-time node supplies immutable register, clock, interrupt, power-domain, and graph topology data to the MSM DRM/DPU drivers. Any stateful display behavior is in the drivers and hardware, outside this binding.

Dependencies/integration points: integrates with `/schemas/display/msm/dpu-common.yaml#`, the containing Qualcomm MDSS schema for the same SoC family, Linux dt-schema validation, display graph `ports`, clock-controller bindings, interrupt-controller bindings, power-domain/OPP bindings, and the DRM MSM DPU driver that consumes compatible-specific catalog data. Local properties are intentionally limited so common DPU behavior remains centralized.

Risks: clock and register ordering are ABI-like details; changing them can silently misbind driver resources even when property names still look valid. Compatible fallback lists must match driver catalog support exactly. Endpoint numbering must match the DPU interface catalog and the enclosing MDSS child-node examples. Overly broad compatibles can accept DTS files for unsupported hardware, while overly strict property closure can reject valid future extensions.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm845-dpu.yaml` and validate real board DTS files with `make dtbs_check`. Useful negative checks are missing `reg-names`, reordered clocks, unsupported compatible strings, missing graph endpoints, and accidental extra properties blocked by `unevaluatedProperties: false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm845-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm845-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm845-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SDM845 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sdm845-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm845-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sdm845-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-dpu.yaml

Purpose: Devicetree binding schema for Qualcomm Display DPU on SM6115, defining the SoC-specific Qualcomm DPU display-controller node under an MDSS parent. It accepts compatible values `qcom,sm6115-dpu`. It narrows the common DPU contract to this hardware generation by fixing register regions, clock inputs, and clock-name ordering.

Important APIs/types/functions: this is declarative JSON schema, not executable code. The key contract is `$id`, `$schema`, `$ref` to `/schemas/display/msm/dpu-common.yaml#`, local `properties` (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), required fields (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), and the `unevaluatedProperties: false` gate. Compatible matching is the schema entry point used by dt-schema and by DTS authors to select the matching DPU hardware description.

Control flow: validation first applies the common DPU schema, then checks the local `compatible` value, `reg`/`reg-names` tuples, `clocks`, and `clock-names`. Example nodes show the expected runtime graph shape: the display controller is a child of `mdss`, receives MDSS interrupts, binds power/OPP data where present, and exposes `ports`/`endpoint` links toward DSI or other display interfaces. There are 1 example block(s) that exercise the schema in dt-binding checks.

State and persistence behavior: the file persists no runtime state. It constrains source-controlled DTS data that becomes part of the kernel device tree; the resulting boot-time node supplies immutable register, clock, interrupt, power-domain, and graph topology data to the MSM DRM/DPU drivers. Any stateful display behavior is in the drivers and hardware, outside this binding.

Dependencies/integration points: integrates with `/schemas/display/msm/dpu-common.yaml#`, the containing Qualcomm MDSS schema for the same SoC family, Linux dt-schema validation, display graph `ports`, clock-controller bindings, interrupt-controller bindings, power-domain/OPP bindings, and the DRM MSM DPU driver that consumes compatible-specific catalog data. Local properties are intentionally limited so common DPU behavior remains centralized.

Risks: clock and register ordering are ABI-like details; changing them can silently misbind driver resources even when property names still look valid. Compatible fallback lists must match driver catalog support exactly. Endpoint numbering must match the DPU interface catalog and the enclosing MDSS child-node examples. Overly broad compatibles can accept DTS files for unsupported hardware, while overly strict property closure can reject valid future extensions.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-dpu.yaml` and validate real board DTS files with `make dtbs_check`. Useful negative checks are missing `reg-names`, reordered clocks, unsupported compatible strings, missing graph endpoints, and accidental extra properties blocked by `unevaluatedProperties: false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM6115 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm6115-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6125-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6125-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM6125 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm6125-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (none declared locally), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6125-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6125-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6150-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6150-dpu.yaml

Purpose: Devicetree binding schema for Qualcomm SM6150 Display DPU, defining the SoC-specific Qualcomm DPU display-controller node under an MDSS parent. It accepts compatible values `qcom,sm6150-dpu`. It narrows the common DPU contract to this hardware generation by fixing register regions, clock inputs, and clock-name ordering.

Important APIs/types/functions: this is declarative JSON schema, not executable code. The key contract is `$id`, `$schema`, `$ref` to `/schemas/display/msm/dpu-common.yaml#`, local `properties` (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), required fields (none declared locally), and the `unevaluatedProperties: false` gate. Compatible matching is the schema entry point used by dt-schema and by DTS authors to select the matching DPU hardware description.

Control flow: validation first applies the common DPU schema, then checks the local `compatible` value, `reg`/`reg-names` tuples, `clocks`, and `clock-names`. Example nodes show the expected runtime graph shape: the display controller is a child of `mdss`, receives MDSS interrupts, binds power/OPP data where present, and exposes `ports`/`endpoint` links toward DSI or other display interfaces. There are 1 example block(s) that exercise the schema in dt-binding checks.

State and persistence behavior: the file persists no runtime state. It constrains source-controlled DTS data that becomes part of the kernel device tree; the resulting boot-time node supplies immutable register, clock, interrupt, power-domain, and graph topology data to the MSM DRM/DPU drivers. Any stateful display behavior is in the drivers and hardware, outside this binding.

Dependencies/integration points: integrates with `/schemas/display/msm/dpu-common.yaml#`, the containing Qualcomm MDSS schema for the same SoC family, Linux dt-schema validation, display graph `ports`, clock-controller bindings, interrupt-controller bindings, power-domain/OPP bindings, and the DRM MSM DPU driver that consumes compatible-specific catalog data. Local properties are intentionally limited so common DPU behavior remains centralized.

Risks: clock and register ordering are ABI-like details; changing them can silently misbind driver resources even when property names still look valid. Compatible fallback lists must match driver catalog support exactly. Endpoint numbering must match the DPU interface catalog and the enclosing MDSS child-node examples. Overly broad compatibles can accept DTS files for unsupported hardware, while overly strict property closure can reject valid future extensions.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6150-dpu.yaml` and validate real board DTS files with `make dtbs_check`. Useful negative checks are missing `reg-names`, reordered clocks, unsupported compatible strings, missing graph endpoints, and accidental extra properties blocked by `unevaluatedProperties: false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6150-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6150-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6150-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM6150 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm6150-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (none declared locally), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6150-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6150-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6350-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6350-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM6350 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm6350-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (none declared locally), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6350-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6350-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6375-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6375-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM6375 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm6375-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (none declared locally), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6375-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6375-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm7150-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm7150-dpu.yaml

Purpose: Devicetree binding schema for Qualcomm SM7150 Display Processing Unit (DPU), defining the SoC-specific Qualcomm DPU display-controller node under an MDSS parent. It accepts compatible values `qcom,sm7150-dpu`. It narrows the common DPU contract to this hardware generation by fixing register regions, clock inputs, and clock-name ordering.

Important APIs/types/functions: this is declarative JSON schema, not executable code. The key contract is `$id`, `$schema`, `$ref` to `/schemas/display/msm/dpu-common.yaml#`, local `properties` (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), required fields (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), and the `unevaluatedProperties: false` gate. Compatible matching is the schema entry point used by dt-schema and by DTS authors to select the matching DPU hardware description.

Control flow: validation first applies the common DPU schema, then checks the local `compatible` value, `reg`/`reg-names` tuples, `clocks`, and `clock-names`. Example nodes show the expected runtime graph shape: the display controller is a child of `mdss`, receives MDSS interrupts, binds power/OPP data where present, and exposes `ports`/`endpoint` links toward DSI or other display interfaces. There are 1 example block(s) that exercise the schema in dt-binding checks.

State and persistence behavior: the file persists no runtime state. It constrains source-controlled DTS data that becomes part of the kernel device tree; the resulting boot-time node supplies immutable register, clock, interrupt, power-domain, and graph topology data to the MSM DRM/DPU drivers. Any stateful display behavior is in the drivers and hardware, outside this binding.

Dependencies/integration points: integrates with `/schemas/display/msm/dpu-common.yaml#`, the containing Qualcomm MDSS schema for the same SoC family, Linux dt-schema validation, display graph `ports`, clock-controller bindings, interrupt-controller bindings, power-domain/OPP bindings, and the DRM MSM DPU driver that consumes compatible-specific catalog data. Local properties are intentionally limited so common DPU behavior remains centralized.

Risks: clock and register ordering are ABI-like details; changing them can silently misbind driver resources even when property names still look valid. Compatible fallback lists must match driver catalog support exactly. Endpoint numbering must match the DPU interface catalog and the enclosing MDSS child-node examples. Overly broad compatibles can accept DTS files for unsupported hardware, while overly strict property closure can reject valid future extensions.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm7150-dpu.yaml` and validate real board DTS files with `make dtbs_check`. Useful negative checks are missing `reg-names`, reordered clocks, unsupported compatible strings, missing graph endpoints, and accidental extra properties blocked by `unevaluatedProperties: false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm7150-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm7150-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm7150-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM7150 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm7150-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm7150-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm7150-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8150-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8150-dpu.yaml

Purpose: Devicetree binding schema for Qualcomm SM8150 Display DPU, defining the SoC-specific Qualcomm DPU display-controller node under an MDSS parent. It accepts compatible values `qcom,sm8150-dpu`, `qcom,sm8250-dpu`. It narrows the common DPU contract to this hardware generation by fixing register regions, clock inputs, and clock-name ordering.

Important APIs/types/functions: this is declarative JSON schema, not executable code. The key contract is `$id`, `$schema`, `$ref` to `/schemas/display/msm/dpu-common.yaml#`, local `properties` (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), required fields (none declared locally), and the `unevaluatedProperties: false` gate. Compatible matching is the schema entry point used by dt-schema and by DTS authors to select the matching DPU hardware description.

Control flow: validation first applies the common DPU schema, then checks the local `compatible` value, `reg`/`reg-names` tuples, `clocks`, and `clock-names`. Example nodes show the expected runtime graph shape: the display controller is a child of `mdss`, receives MDSS interrupts, binds power/OPP data where present, and exposes `ports`/`endpoint` links toward DSI or other display interfaces. There are 1 example block(s) that exercise the schema in dt-binding checks.

State and persistence behavior: the file persists no runtime state. It constrains source-controlled DTS data that becomes part of the kernel device tree; the resulting boot-time node supplies immutable register, clock, interrupt, power-domain, and graph topology data to the MSM DRM/DPU drivers. Any stateful display behavior is in the drivers and hardware, outside this binding.

Dependencies/integration points: integrates with `/schemas/display/msm/dpu-common.yaml#`, the containing Qualcomm MDSS schema for the same SoC family, Linux dt-schema validation, display graph `ports`, clock-controller bindings, interrupt-controller bindings, power-domain/OPP bindings, and the DRM MSM DPU driver that consumes compatible-specific catalog data. Local properties are intentionally limited so common DPU behavior remains centralized.

Risks: clock and register ordering are ABI-like details; changing them can silently misbind driver resources even when property names still look valid. Compatible fallback lists must match driver catalog support exactly. Endpoint numbering must match the DPU interface catalog and the enclosing MDSS child-node examples. Overly broad compatibles can accept DTS files for unsupported hardware, while overly strict property closure can reject valid future extensions.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8150-dpu.yaml` and validate real board DTS files with `make dtbs_check`. Useful negative checks are missing `reg-names`, reordered clocks, unsupported compatible strings, missing graph endpoints, and accidental extra properties blocked by `unevaluatedProperties: false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8150-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8150-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8150-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM8150 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm8150-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (none declared locally), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8150-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8150-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8250-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8250-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM8250 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm8250-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8250-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8250-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8350-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8350-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM8350 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm8350-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`), required fields (none declared locally), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8350-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8350-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8450-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8450-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM8450 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm8450-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8450-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8450-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8550-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8550-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM8550 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm8550-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8550-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8550-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8650-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8650-dpu.yaml

Purpose: Devicetree binding schema for Qualcomm SM8650 Display DPU, defining the SoC-specific Qualcomm DPU display-controller node under an MDSS parent. It accepts compatible values `qcom,eliza-dpu`, `qcom,glymur-dpu`, `qcom,kaanapali-dpu`, `qcom,sa8775p-dpu`, `qcom,sm8650-dpu`, `qcom,sm8750-dpu`, `qcom,x1e80100-dpu`, `qcom,qcs8300-dpu`. It narrows the common DPU contract to this hardware generation by fixing register regions, clock inputs, and clock-name ordering.

Important APIs/types/functions: this is declarative JSON schema, not executable code. The key contract is `$id`, `$schema`, `$ref` to `/schemas/display/msm/dpu-common.yaml#`, local `properties` (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), required fields (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), and the `unevaluatedProperties: false` gate. Compatible matching is the schema entry point used by dt-schema and by DTS authors to select the matching DPU hardware description.

Control flow: validation first applies the common DPU schema, then checks the local `compatible` value, `reg`/`reg-names` tuples, `clocks`, and `clock-names`. Example nodes show the expected runtime graph shape: the display controller is a child of `mdss`, receives MDSS interrupts, binds power/OPP data where present, and exposes `ports`/`endpoint` links toward DSI or other display interfaces. There are 1 example block(s) that exercise the schema in dt-binding checks.

State and persistence behavior: the file persists no runtime state. It constrains source-controlled DTS data that becomes part of the kernel device tree; the resulting boot-time node supplies immutable register, clock, interrupt, power-domain, and graph topology data to the MSM DRM/DPU drivers. Any stateful display behavior is in the drivers and hardware, outside this binding.

Dependencies/integration points: integrates with `/schemas/display/msm/dpu-common.yaml#`, the containing Qualcomm MDSS schema for the same SoC family, Linux dt-schema validation, display graph `ports`, clock-controller bindings, interrupt-controller bindings, power-domain/OPP bindings, and the DRM MSM DPU driver that consumes compatible-specific catalog data. Local properties are intentionally limited so common DPU behavior remains centralized.

Risks: clock and register ordering are ABI-like details; changing them can silently misbind driver resources even when property names still look valid. Compatible fallback lists must match driver catalog support exactly. Endpoint numbering must match the DPU interface catalog and the enclosing MDSS child-node examples. Overly broad compatibles can accept DTS files for unsupported hardware, while overly strict property closure can reject valid future extensions.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8650-dpu.yaml` and validate real board DTS files with `make dtbs_check`. Useful negative checks are missing `reg-names`, reordered clocks, unsupported compatible strings, missing graph endpoints, and accidental extra properties blocked by `unevaluatedProperties: false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8650-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8650-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8650-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM8650 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm8650-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8650-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8650-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8750-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8750-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm SM8750 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,sm8750-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^dsi@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8750-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm8750-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,x1e80100-mdss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,x1e80100-mdss.yaml

Purpose: Devicetree binding schema for Qualcomm X1E80100 Display MDSS, the Qualcomm MDSS wrapper node for a specific SoC display subsystem. It accepts compatible values `qcom,x1e80100-mdss`. It describes the MDSS container that owns common registers, interrupts, clocks, IOMMU/interconnect wiring, and child display blocks such as DPU, DSI, DP/eDP, and DSI PHY nodes.

Important APIs/types/functions: this declarative schema uses `$id`, `$schema`, `$ref` to `/schemas/display/msm/mdss-common.yaml#`, local `properties` (`compatible`, `clocks`, `iommus`, `interconnects`, `interconnect-names`), required fields (`compatible`), `patternProperties` for child nodes (`^display-controller@[0-9a-f]+$`, `^displayport-controller@[0-9a-f]+$`, `^phy@[0-9a-f]+$`), and `unevaluatedProperties: false`. The child-node compatible constraints are the main integration API: they route DPU, DSI controller, DP/eDP controller, and PHY subnodes to their own bindings while keeping them under the MDSS address space.

Control flow: dt-schema starts with the common MDSS schema, then enforces this SoC compatible, clock/interconnect cardinality, optional IOMMU shape, and child-node regexes. During DTS validation, child nodes named like `display-controller@...`, `displayport-controller@...`, `dsi@...`, or `phy@...` are checked for the SoC-specific compatibles listed here while their detailed properties are left to the child schemas through `additionalProperties: true` inside each pattern. The 1 example block(s) model the full graph from MDSS to DPU and output interfaces.

State and persistence behavior: the schema itself has no mutable state. It defines persistent DTS source that becomes the boot-time MDSS hardware description: address ranges, clock handles, interrupt controller data, IOMMU stream IDs, bandwidth interconnects, power domains, and child-device topology. Kernel state is created later by the MSM DRM, DSI, DP, PHY, clock, interconnect, IOMMU, and power-domain drivers using this static description.

Dependencies/integration points: depends on `/schemas/display/msm/mdss-common.yaml#`, child schemas for DPU/DSI/DP/DSI PHY, graph endpoint bindings, Qualcomm dispcc/gcc/rpmh or rpm power-domain bindings as shown in examples, SMMU bindings, interconnect providers, and the MSM DRM MDSS platform driver. The pattern properties are the handoff points between the MDSS wrapper and child display component bindings.

Risks: the MDSS node is a resource hub, so wrong clock order, missing interconnect names, incorrect IOMMU stream IDs, or mismatched child compatibles can break several display blocks at once. Pattern nodes deliberately allow additional child properties, so detailed errors may appear only when child schemas are also selected. Board DTS files must keep graph endpoints consistent across DPU, DSI/DP, PHY, panel, and bridge nodes.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,x1e80100-mdss.yaml` plus `make dtbs_check` on SoC boards using the compatible. Negative tests should cover unsupported child compatibles, missing required compatible, clock/interconnect count mistakes, extra wrapper properties blocked by `unevaluatedProperties: false`, and incomplete graph links between MDSS children and panels/bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,x1e80100-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/abt,y030xx067a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/abt,y030xx067a.yaml

Purpose: Devicetree binding schema for Asia Better Technology 3.0" (320x480 pixels) 24-bit IPS LCD panel. It accepts compatible values `abt,y030xx067a`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`), required fields (`compatible`, `reg`, `power-supply`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/abt,y030xx067a.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/abt,y030xx067a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/advantech,idk-1110wr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/advantech,idk-1110wr.yaml

Purpose: Devicetree binding schema for Advantech IDK-1110WR 10.1" WSVGA LVDS Display Panel. It accepts compatible values `advantech,idk-1110wr`, `panel-lvds`. It documents a LVDS dual-link panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/display/lvds.yaml#`, local `properties` (`compatible`, `data-mapping`, `width-mm`, `height-mm`, `panel-timing`, `port`), required fields (`compatible`, `data-mapping`, `width-mm`, `height-mm`, `panel-timing`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/advantech,idk-1110wr.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/advantech,idk-1110wr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/advantech,idk-2121wr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/advantech,idk-2121wr.yaml

Purpose: Devicetree binding schema for Advantech IDK-2121WR 21.5" Full-HD dual-LVDS panel. It accepts compatible values `advantech,idk-2121wr`. It documents a LVDS dual-link panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `/schemas/display/lvds-dual-ports.yaml#`, `panel-common.yaml#`, local `properties` (`compatible`, `width-mm`, `height-mm`, `data-mapping`, `panel-timing`, `ports`), required fields (`compatible`, `width-mm`, `height-mm`, `data-mapping`, `panel-timing`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/advantech,idk-2121wr.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/advantech,idk-2121wr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/anbernic,rg35xx-plus-panel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/anbernic,rg35xx-plus-panel.yaml

Purpose: Devicetree binding schema for Anbernic RG35XX series (WL-355608-A8) 3.5" 640x480 24-bit IPS LCD panel. It accepts compatible values `anbernic,rg35xx-plus-panel`, `anbernic,rg35xx-2024-panel`, `anbernic,rg35xx-h-panel`, `anbernic,rg35xx-sp-panel`. It documents a SPI-controlled panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `spi-3wire`), required fields (`compatible`, `reg`, `port`, `power-supply`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/anbernic,rg35xx-plus-panel.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/anbernic,rg35xx-plus-panel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/apple,summit.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/apple,summit.yaml

Purpose: Devicetree binding schema for Apple "Summit" display panel. It accepts compatible values `apple,j293-summit`, `apple,j493-summit`, `apple,summit`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/leds/backlight/common.yaml#`, local `properties` (`compatible`, `reg`), required fields (`compatible`, `reg`, `max-brightness`, `port`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/apple,summit.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/apple,summit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/arm,rtsm-display.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/arm,rtsm-display.yaml

Purpose: Devicetree binding schema for Arm RTSM Virtual Platforms Display. It accepts compatible values `arm,rtsm-display`. It documents a display panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `port`), required fields (`compatible`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 0; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/arm,rtsm-display.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/arm,rtsm-display.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/arm,versatile-tft-panel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/arm,versatile-tft-panel.yaml

Purpose: Devicetree binding schema for ARM Versatile TFT Panels. It accepts compatible values `arm,versatile-tft-panel`. It documents a display panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `port`), required fields (`compatible`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/arm,versatile-tft-panel.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/arm,versatile-tft-panel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/armadeus,st0700-adapt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/armadeus,st0700-adapt.yaml

Purpose: Devicetree binding schema for Armadeus ST0700 Adapter. It accepts compatible values `armadeus,st0700-adapt`. It documents a display panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `power-supply`, `backlight`, `port`), required fields (`compatible`, `power-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 0; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/armadeus,st0700-adapt.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/armadeus,st0700-adapt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/asus,z00t-tm5p5-nt35596.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/asus,z00t-tm5p5-nt35596.yaml

Purpose: Devicetree binding schema for ASUS Z00T TM5P5 NT35596 5.5" 1080x1920 LCD Panel. It accepts compatible values `asus,z00t-tm5p5-n35596`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `reset-gpios`, `vdd-supply`, `vddio-supply`), required fields (`compatible`, `reg`, `vdd-supply`, `vddio-supply`, `reset-gpios`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/asus,z00t-tm5p5-nt35596.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/asus,z00t-tm5p5-nt35596.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/auo,a030jtn01.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/auo,a030jtn01.yaml

Purpose: Devicetree binding schema for AUO A030JTN01 3.0" (320x480 pixels) 24-bit TFT LCD panel. It accepts compatible values `auo,a030jtn01`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`), required fields (`compatible`, `reg`, `power-supply`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/auo,a030jtn01.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/auo,a030jtn01.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/bananapi,s070wv20-ct16.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/bananapi,s070wv20-ct16.yaml

Purpose: Devicetree binding schema for Banana Pi 7" (S070WV20-CT16) TFT LCD Panel. It accepts compatible values `bananapi,s070wv20-ct16`. It documents a display panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `power-supply`, `backlight`, `enable-gpios`, `port`), required fields (`compatible`, `power-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 0; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/bananapi,s070wv20-ct16.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/bananapi,s070wv20-ct16.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,bf060y8m-aj0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,bf060y8m-aj0.yaml

Purpose: Devicetree binding schema for BOE BF060Y8M-AJ0 5.99" 1080x2160 AMOLED Panel. It accepts compatible values `boe,bf060y8m-aj0`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `elvdd-supply`, `elvss-supply`, `vcc-supply`, `vci-supply`, `vddio-supply`, `port`, `reset-gpios`), required fields (`compatible`, `elvdd-supply`, `elvss-supply`, `vcc-supply`, `vci-supply`, `vddio-supply`, `reg`, `reset-gpios`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,bf060y8m-aj0.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,bf060y8m-aj0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,himax8279d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,himax8279d.yaml

Purpose: Devicetree binding schema for Boe Himax8279d 1200x1920 TFT LCD panel. It accepts compatible values `boe,himax8279d8p`, `boe,himax8279d10p`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `enable-gpios`, `pp33-gpios`, `pp18-gpios`), required fields (`compatible`, `reg`, `enable-gpios`, `pp33-gpios`, `pp18-gpios`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,himax8279d.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,himax8279d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,td4320.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,td4320.yaml

Purpose: Devicetree binding schema for BOE TD4320 MIPI-DSI panels. It accepts compatible values `boe,td4320`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `iovcc-supply`, `vsn-supply`, `vsp-supply`), required fields (`compatible`, `reg`, `reset-gpios`, `port`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,td4320.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,td4320.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,th101mb31ig002-28a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,th101mb31ig002-28a.yaml

Purpose: Devicetree binding schema for BOE TH101MB31IG002-28A WXGA DSI Display Panel. It accepts compatible values `boe,th101mb31ig002-28a`, `starry,er88577`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `enable-gpios`, `reset-gpios`, `power-supply`, `port`, `rotation`), required fields (`compatible`, `reg`, `enable-gpios`, `power-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 1; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,th101mb31ig002-28a.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,th101mb31ig002-28a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,tv101wum-ll2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,tv101wum-ll2.yaml

Purpose: Devicetree binding schema for BOE TV101WUM-LL2 DSI Display Panel. It accepts compatible values `boe,tv101wum-ll2`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `reset-gpios`, `vsp-supply`, `vsn-supply`, `port`, `rotation`), required fields (`compatible`, `reg`, `reset-gpios`, `vsp-supply`, `vsn-supply`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,tv101wum-ll2.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,tv101wum-ll2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,tv101wum-nl6.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,tv101wum-nl6.yaml

Purpose: Devicetree binding schema for BOE TV101WUM-NL6 DSI Display Panel. It accepts compatible values `boe,tv101wum-nl6`, `auo,kd101n80-45na`, `boe,tv101wum-n53`, `auo,b101uan08.3`, `boe,tv105wum-nw0`, `boe,tv110c9m-ll3`, `innolux,hj110iz-01a`, `starry,2081101qfh032011-53g`, `starry,ili9882t`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `enable-gpios`, `pp1800-supply`, `pp3300-supply`, `avdd-supply`, `avee-supply`, `backlight`, `port`, `rotation`), required fields (`compatible`, `reg`, `enable-gpios`, `pp1800-supply`, `avdd-supply`, `avee-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,tv101wum-nl6.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/boe,tv101wum-nl6.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/display-timings.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/display-timings.yaml

Purpose: generic Devicetree binding schema for a `display-timings` child node that lists one or more panel timing modes and optionally marks a native/default mode. It is shared by simple panels and display interfaces that need datasheet timing values in DTS rather than hard-coded driver tables.

Important APIs/types/functions: the schema defines `$nodename: display-timings`, optional `native-mode` as a phandle, `patternProperties` for timing child nodes matching `^timing`, and references `panel-timing.yaml#` for each timing entry. It uses `additionalProperties: false` to keep the timing container limited to the native-mode selector and timing children.

Control flow: validation accepts a node named `display-timings`, checks that `native-mode` points at one of the timing children when present, and validates each `timing*` child through `panel-timing.yaml`. If `native-mode` is absent, the binding documentation states that consumers treat the first timing node as native.

State and persistence behavior: there is no runtime state. The file standardizes persistent DTS timing data: pixel clock, active area, porches, sync lengths, and polarity flags. Drivers read those values at probe time to program display controller timings.

Dependencies/integration points: integrates with `panel-timing.yaml#`, `panel-common.yaml#` users that allow `display-timings`, simple-panel style drivers, and board DTS panel nodes. It is transport-neutral and can describe timings for RGB, LVDS, or other fixed-timing panels.

Risks: phandle mistakes or relying on implicit first-node ordering can select the wrong mode. Timing triplets must use min/typ/max ordering understood by `panel-timing.yaml`; incorrect units or polarity flags can produce a valid but unusable display mode. Because this schema is generic, panel-specific electrical constraints must be enforced elsewhere.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/display-timings.yaml` and validate DTS nodes that include multiple timing children, no native-mode, and a native-mode phandle. Negative cases should include non-`timing*` children, unknown container properties, invalid timing property shapes, and stale phandle labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/display-timings.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/dlc,dlc0700yzg-1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/dlc,dlc0700yzg-1.yaml

Purpose: Devicetree binding schema for DLC Display Co. DLC0700YZG-1 7.0" WSVGA TFT LCD panel. It accepts compatible values `dlc,dlc0700yzg-1`. It documents a display panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reset-gpios`, `enable-gpios`, `backlight`, `port`), required fields (`compatible`, `power-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 0; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/dlc,dlc0700yzg-1.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/dlc,dlc0700yzg-1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ebbg,ft8719.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ebbg,ft8719.yaml

Purpose: Devicetree binding schema for EBBG FT8719 MIPI-DSI LCD panel. It accepts compatible values `ebbg,ft8719`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `vddio-supply`, `vddpos-supply`, `vddneg-supply`), required fields (`compatible`, `reg`, `vddio-supply`, `vddpos-supply`, `vddneg-supply`, `reset-gpios`, `port`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ebbg,ft8719.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ebbg,ft8719.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/elida,kd35t133.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/elida,kd35t133.yaml

Purpose: Devicetree binding schema for Elida KD35T133 3.5in 320x480 DSI panel. It accepts compatible values `elida,kd35t133`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `port`, `reset-gpios`, `rotation`, `iovcc-supply`, `vdd-supply`), required fields (`compatible`, `reg`, `backlight`, `port`, `iovcc-supply`, `vdd-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/elida,kd35t133.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/elida,kd35t133.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/fascontek,fs035vg158.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/fascontek,fs035vg158.yaml

Purpose: Devicetree binding schema for Fascontek FS035VG158 3.5" (640x480 pixels) 24-bit IPS LCD panel. It accepts compatible values `fascontek,fs035vg158`. It documents a SPI-controlled panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `spi-3wire`), required fields (`compatible`, `reg`, `port`, `power-supply`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/fascontek,fs035vg158.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/fascontek,fs035vg158.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/feixin,k101-im2ba02.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/feixin,k101-im2ba02.yaml

Purpose: Devicetree binding schema for Feixin K101 IM2BA02 10.1" MIPI-DSI LCD panel. It accepts compatible values `feixin,k101-im2ba02`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `reset-gpios`, `avdd-supply`, `dvdd-supply`, `cvdd-supply`), required fields (`compatible`, `reg`, `avdd-supply`, `dvdd-supply`, `cvdd-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/feixin,k101-im2ba02.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/feixin,k101-im2ba02.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/feiyang,fy07024di26a30d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/feiyang,fy07024di26a30d.yaml

Purpose: Devicetree binding schema for Feiyang FY07024DI26A30-D 7" MIPI-DSI LCD Panel. It accepts compatible values `feiyang,fy07024di26a30d`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `avdd-supply`, `dvdd-supply`, `port`, `reset-gpios`, `backlight`), required fields (`compatible`, `reg`, `avdd-supply`, `dvdd-supply`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/feiyang,fy07024di26a30d.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/feiyang,fy07024di26a30d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/focaltech,gpt3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/focaltech,gpt3.yaml

Purpose: Devicetree binding schema for Focaltech GPT3 3.0" (640x480 pixels) IPS LCD panel. It accepts compatible values `focaltech,gpt3`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`), required fields (`compatible`, `reg`, `power-supply`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/focaltech,gpt3.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/focaltech,gpt3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx8279.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx8279.yaml

Purpose: Devicetree binding schema for Himax HX8279/HX8279-D based MIPI-DSI panels. It accepts compatible values `aoly,sl101pm1794fog-v15`, `startek,kd070fhfid078`, `himax,hx8279`. It documents a MIPI-DSI dual-link panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common-dual.yaml#`, local `properties` (`compatible`, `reg`, `iovcc-supply`, `vdd-supply`), required fields (`compatible`, `reg`, `backlight`, `reset-gpios`, `iovcc-supply`, `vdd-supply`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx8279.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx8279.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83102.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83102.yaml

Purpose: Devicetree binding schema for Himax HX83102 MIPI-DSI LCD panel controller. It accepts compatible values `boe,nv110wum-l60`, `csot,pna957qt1-1`, `holitech,htf065h045`, `ivo,t109nw41`, `kingdisplay,kd110n11-51ie`, `starry,2082109qfh040022-50e`, `starry,himax83102-j02`, `himax,hx83102`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `enable-gpios`, `pp1800-supply`, `avdd-supply`, `avee-supply`, `backlight`, `port`, `rotation`), required fields (`compatible`, `reg`, `enable-gpios`, `pp1800-supply`, `avdd-supply`, `avee-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83102.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83102.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83112a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83112a.yaml

Purpose: Devicetree binding schema for Himax HX83112A-based DSI display panels. It accepts compatible values `djn,9a-3r063-1102b`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `vdd1-supply`, `vsn-supply`, `vsp-supply`), required fields (`compatible`, `reg`, `reset-gpios`, `vdd1-supply`, `vsn-supply`, `vsp-supply`, `port`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83112a.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83112a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83112b.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83112b.yaml

Purpose: Devicetree binding schema for Himax HX83112B-based DSI display panels. It accepts compatible values `djn,98-03057-6598b-i`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `iovcc-supply`, `vsn-supply`, `vsp-supply`), required fields (`compatible`, `reg`, `reset-gpios`, `iovcc-supply`, `vsn-supply`, `vsp-supply`, `port`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83112b.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83112b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83121a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83121a.yaml

Purpose: Devicetree binding schema for Himax HX83121A based DSI display Panels. It accepts compatible values `boe,ppc357db1-4`, `csot,ppc357db1-4`, `himax,hx83121a`. It documents a MIPI-DSI dual-link panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common-dual.yaml#`, local `properties` (`compatible`, `reg`, `reset-gpios`, `avdd-supply`, `avee-supply`, `vddi-supply`, `backlight`, `ports`), required fields (`compatible`, `reg`, `vddi-supply`, `reset-gpios`, `ports`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83121a.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx83121a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx8394.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx8394.yaml

Purpose: Devicetree binding schema for Himax HX8394 MIPI-DSI LCD panel controller. It accepts compatible values `hannstar,hsd060bhw4`, `microchip,ac40t08a-mipi-panel`, `powkiddy,x55-panel`, `himax,hx8394`, `huiling,hl055fhav028c`, `himax,hx8399c`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `reset-gpios`, `backlight`, `rotation`, `port`, `vcc-supply`, `iovcc-supply`), required fields (`compatible`, `reg`, `backlight`, `port`, `vcc-supply`, `iovcc-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 1; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx8394.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/himax,hx8394.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/hydis,hv101hd1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/hydis,hv101hd1.yaml

Purpose: Devicetree binding schema for Hydis HV101HD1 DSI Display Panel. It accepts compatible values `hydis,hv101hd1`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `vdd-supply`, `vio-supply`, `backlight`, `port`), required fields (`compatible`, `vdd-supply`, `vio-supply`, `backlight`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/hydis,hv101hd1.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/hydis,hv101hd1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,il79900a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,il79900a.yaml

Purpose: Devicetree binding schema for Ilitek IL79900a based MIPI-DSI panels. It accepts compatible values `tianma,tl121bvms07-00`, `ilitek,il79900a`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `enable-gpios`, `avdd-supply`, `avee-supply`, `pp1800-supply`, `backlight`), required fields (`compatible`, `reg`, `enable-gpios`, `avdd-supply`, `avee-supply`, `pp1800-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,il79900a.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,il79900a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9163.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9163.yaml

Purpose: Devicetree binding schema for Ilitek ILI9163 display panels. It accepts compatible values `newhaven,1.8-128160EF`, `ilitek,ili9163`. It documents a SPI-controlled panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `spi-max-frequency`, `dc-gpios`), required fields (`compatible`, `reg`, `dc-gpios`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9163.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9163.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9322.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9322.yaml

Purpose: Devicetree binding schema for Ilitek ILI9322 TFT panel driver with SPI control bus. It accepts compatible values `dlink,dir-685-panel`, `ilitek,ili9322`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `vcc-supply`, `iovcc-supply`, `vci-supply`), required fields (`compatible`, `reg`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9322.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9322.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9341.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9341.yaml

Purpose: Devicetree binding schema for Ilitek-9341 Display Panel. It accepts compatible values `adafruit,yx240qv29`, `st,sf-tc240t-9370-t`, `canaan,kd233-tft`, `ilitek,ili9341`. It documents a SPI-controlled panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `dc-gpios`, `spi-3wire`, `spi-max-frequency`, `vci-supply`, `vddi-supply`, `vddi-led-supply`), required fields (`compatible`, `reg`, `dc-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9341.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9341.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9805.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9805.yaml

Purpose: Devicetree binding schema for Ilitek ILI9805 based MIPI-DSI panels. It accepts compatible values `giantplus,gpm1790a0`, `tianma,tm041xdhg01`, `ilitek,ili9805`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `avdd-supply`, `dvdd-supply`), required fields (`compatible`, `avdd-supply`, `dvdd-supply`, `reg`, `reset-gpios`, `port`, `backlight`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9805.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9805.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9806e.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9806e.yaml

Purpose: Devicetree binding schema for Ilitek ILI9806E based panels. It accepts compatible values `densitron,dmt028vghmcmi-1d`, `ortustech,com35h3p70ulc`, `rocktech,rk050hr345-ct106a`, `ilitek,ili9806e`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `vdd-supply`, `vccio-supply`), required fields (`compatible`, `reg`, `vdd-supply`, `reset-gpios`, `backlight`, `port`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 2; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9806e.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9806e.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9881c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9881c.yaml

Purpose: Devicetree binding schema for Ilitek ILI9881c based MIPI-DSI panels. It accepts compatible values `ampire,am8001280g`, `bananapi,lhr050h41`, `bestar,bsd1218-a101kl68`, `feixin,k101-im2byl02`, `raspberrypi,dsi-5inch`, `raspberrypi,dsi-7inch`, `startek,kd050hdfia020`, `tdo,tl050hdv35`, `wanchanglong,w552946aaa`, `wanchanglong,w552946aba`, `ilitek,ili9881c`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `port`, `power-supply`, `reset-gpios`, `rotation`), required fields (`compatible`, `power-supply`, `reg`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9881c.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/ilitek,ili9881c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,ee101ia-01d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,ee101ia-01d.yaml

Purpose: Devicetree binding schema for Innolux Corporation 10.1" EE101IA-01D WXGA (1280x800) LVDS panel. It accepts compatible values `innolux,ee101ia-01d`, `panel-lvds`. It documents a LVDS dual-link panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/display/lvds.yaml#`, local `properties` (`compatible`, `backlight`, `data-mapping`, `enable-gpios`, `power-supply`, `width-mm`, `height-mm`, `panel-timing`, `port`), required fields (`compatible`, `data-mapping`, `width-mm`, `height-mm`, `panel-timing`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 0; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,ee101ia-01d.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,ee101ia-01d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,ej030na.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,ej030na.yaml

Purpose: Devicetree binding schema for Innolux EJ030NA 3.0" (320x480 pixels) 24-bit TFT LCD panel. It accepts compatible values `innolux,ej030na`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`), required fields (`compatible`, `reg`, `power-supply`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,ej030na.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,ej030na.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,p097pfg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,p097pfg.yaml

Purpose: Devicetree binding schema for Innolux P097PFG 9.7" 1536x2048 TFT LCD panel. It accepts compatible values `innolux,p097pfg`. It documents a MIPI-DSI dual-link panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common-dual.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `enable-gpios`, `avdd-supply`, `avee-supply`, `port`, `ports`), required fields (`compatible`, `reg`, `avdd-supply`, `avee-supply`, `enable-gpios`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,p097pfg.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/innolux,p097pfg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jadard,jd9365da-h3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jadard,jd9365da-h3.yaml

Purpose: Devicetree binding schema for Jadard JD9365DA-HE WXGA DSI panel. It accepts compatible values `anbernic,rg-ds-display-bottom`, `anbernic,rg-ds-display-top`, `chongzhou,cz101b4001`, `kingdisplay,kd101ne3-40ti`, `melfas,lmfbx101117480`, `radxa,display-10hd-ad001`, `radxa,display-8hd-ad002`, `taiguanck,xti05101-01a`, `jadard,jd9365da-h3`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `vdd-supply`, `vccio-supply`, `reset-gpios`, `backlight`, `rotation`, `port`), required fields (`compatible`, `reg`, `vdd-supply`, `vccio-supply`, `reset-gpios`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jadard,jd9365da-h3.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jadard,jd9365da-h3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jdi,lpm102a188a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jdi,lpm102a188a.yaml

Purpose: Devicetree binding schema for JDI LPM102A188A 2560x1800 10.2" DSI Panel. It accepts compatible values `jdi,lpm102a188a`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `enable-gpios`, `reset-gpios`, `power-supply`, `backlight`, `ddi-supply`, `link2`), required fields (`compatible`, `reg`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jdi,lpm102a188a.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jdi,lpm102a188a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jdi,lt070me05000.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jdi,lt070me05000.yaml

Purpose: Devicetree binding schema for JDI model LT070ME05000 1200x1920 7" DSI Panel. It accepts compatible values `jdi,lt070me05000`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `enable-gpios`, `reset-gpios`, `vddp-supply`, `iovcc-supply`, `dcdc-en-gpios`, `port`), required fields (`compatible`, `reg`, `vddp-supply`, `iovcc-supply`, `enable-gpios`, `reset-gpios`, `dcdc-en-gpios`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jdi,lt070me05000.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/jdi,lt070me05000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/kingdisplay,kd035g6-54nt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/kingdisplay,kd035g6-54nt.yaml

Purpose: Devicetree binding schema for King Display KD035G6-54NT 3.5" (320x240 pixels) 24-bit TFT LCD panel. It accepts compatible values `kingdisplay,kd035g6-54nt`. It documents a SPI-controlled panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `spi-3wire`), required fields (`compatible`, `power-supply`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/kingdisplay,kd035g6-54nt.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/kingdisplay,kd035g6-54nt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk035c5444t.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk035c5444t.yaml

Purpose: Devicetree binding schema for Leadtek ltk035c5444t 3.5" (640x480 pixels) 24-bit IPS LCD panel. It accepts compatible values `leadtek,ltk035c5444t`. It documents a SPI-controlled panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `spi-3wire`), required fields (`compatible`, `reg`, `port`, `power-supply`, `reset-gpios`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk035c5444t.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk035c5444t.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk050h3146w.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk050h3146w.yaml

Purpose: Devicetree binding schema for Leadtek LTK050H3146W 5.0in 720x1280 DSI panel. It accepts compatible values `leadtek,ltk050h3146w`, `leadtek,ltk050h3146w-a2`, `leadtek,ltk050h3148w`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `port`, `reset-gpios`, `iovcc-supply`, `vci-supply`), required fields (`compatible`, `reg`, `backlight`, `iovcc-supply`, `vci-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk050h3146w.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk050h3146w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk500hd1829.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk500hd1829.yaml

Purpose: Devicetree binding schema for Leadtek LTK500HD1829 5.0in 720x1280 DSI panel. It accepts compatible values `leadtek,ltk101b4029w`, `leadtek,ltk500hd1829`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `backlight`, `port`, `reset-gpios`, `iovcc-supply`, `vcc-supply`), required fields (`compatible`, `reg`, `backlight`, `iovcc-supply`, `vcc-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk500hd1829.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/leadtek,ltk500hd1829.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,ld070wx3-sl01.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,ld070wx3-sl01.yaml

Purpose: Devicetree binding schema for LG Corporation 7" WXGA TFT LCD panel. It accepts compatible values `lg,ld070wx3-sl01`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `vdd-supply`, `vcc-supply`, `backlight`, `port`), required fields (`compatible`, `vdd-supply`, `vcc-supply`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,ld070wx3-sl01.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,ld070wx3-sl01.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,lg4573.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,lg4573.yaml

Purpose: Devicetree binding schema for LG LG4573 TFT Liquid Crystal Display with SPI control bus. It accepts compatible values `lg,lg4573`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`), required fields (`compatible`, `reg`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,lg4573.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,lg4573.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,sw43408.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,sw43408.yaml

Purpose: Devicetree binding schema for LG SW43408 AMOLED DDIC. It accepts compatible values `lg,sw43408-lh546wf1-ed01`, `lg,sw43408`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `port`, `vddi-supply`, `vpnl-supply`, `reset-gpios`), required fields (`compatible`, `vddi-supply`, `vpnl-supply`, `reset-gpios`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,sw43408.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lg,sw43408.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lgphilips,lb035q02.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lgphilips,lb035q02.yaml

Purpose: Devicetree binding schema for LG.Philips LB035Q02 Panel. It accepts compatible values `lgphilips,lb035q02`. It documents a SPI-controlled panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `spi-cpha`, `spi-cpol`), required fields (`compatible`, `enable-gpios`, `port`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lgphilips,lb035q02.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lgphilips,lb035q02.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/logicpd,type28.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/logicpd,type28.yaml

Purpose: Devicetree binding schema for Logic PD Type 28 4.3" WQVGA TFT LCD panel. It accepts compatible values `logicpd,type28`. It documents a display panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `power-supply`, `enable-gpios`, `backlight`, `port`), required fields (`compatible`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/logicpd,type28.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/logicpd,type28.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lxd,m9189a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lxd,m9189a.yaml

Purpose: Devicetree binding schema for LXD M9189A DSI Display Panel. It accepts compatible values `lxd,m9189a`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml`, local `properties` (`compatible`, `reg`, `standby-gpios`, `reset-gpios`, `power-supply`, `backlight`, `port`), required fields (`compatible`, `reg`, `standby-gpios`, `reset-gpios`, `power-supply`, `backlight`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lxd,m9189a.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/lxd,m9189a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mantix,mlaf057we51-x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mantix,mlaf057we51-x.yaml

Purpose: Devicetree binding schema for Mantix MLAF057WE51-X 5.7" 720x1440 TFT LCD panel. It accepts compatible values `mantix,mlaf057we51-x`, `ys,ys57pss36bh5gq`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `avdd-supply`, `avee-supply`, `vddi-supply`, `mantix,tp-rstn-gpios`, `backlight`, `port`, `reset-gpios`), required fields (`compatible`, `reg`, `avdd-supply`, `avee-supply`, `vddi-supply`, `reset-gpios`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mantix,mlaf057we51-x.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mantix,mlaf057we51-x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mitsubishi,aa104xd12.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mitsubishi,aa104xd12.yaml

Purpose: Devicetree binding schema for Mitsubishi AA104XD12 10.4" XGA LVDS Display Panel. It accepts compatible values `mitsubishi,aa104xd12`, `panel-lvds`. It documents a LVDS dual-link panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/display/lvds.yaml#`, local `properties` (`compatible`, `vcc-supply`, `data-mapping`, `width-mm`, `height-mm`, `backlight`, `panel-timing`, `port`), required fields (`compatible`, `data-mapping`, `width-mm`, `height-mm`, `panel-timing`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mitsubishi,aa104xd12.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mitsubishi,aa104xd12.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mitsubishi,aa121td01.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mitsubishi,aa121td01.yaml

Purpose: Devicetree binding schema for Mitsubishi AA121TD01 12.1" WXGA LVDS Display Panel. It accepts compatible values `mitsubishi,aa121td01`, `panel-lvds`. It documents a LVDS dual-link panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/display/lvds.yaml#`, local `properties` (`compatible`, `vcc-supply`, `data-mapping`, `width-mm`, `height-mm`, `panel-timing`, `port`), required fields (`compatible`, `vcc-supply`, `data-mapping`, `width-mm`, `height-mm`, `panel-timing`, `port`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mitsubishi,aa121td01.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/mitsubishi,aa121td01.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/motorola,mot-panel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/motorola,mot-panel.yaml

Purpose: Devicetree binding schema for Atrix 4G and Droid X2 DSI Display Panel. It accepts compatible values `motorola,mot-panel`. It documents a MIPI-DSI panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, local `properties` (`compatible`, `reg`, `vdd-supply`, `vddio-supply`, `backlight`, `reset-gpios`, `port`), required fields (`compatible`), compatible matching, and `additionalProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/motorola,mot-panel.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/motorola,mot-panel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/nec,nl8048hl11.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/nec,nl8048hl11.yaml

Purpose: Devicetree binding schema for NEC NL8048HL11 4.1" WVGA TFT LCD panel. It accepts compatible values `nec,nl8048hl11`. It documents a SPI-controlled panel node and constrains the supplies, GPIOs, backlight, timing, and graph endpoint data needed by panel drivers.

Important APIs/types/functions: this is a dt-schema contract rather than executable code. It uses `$id`, `$schema`, references `panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, local `properties` (`compatible`, `reg`, `spi-max-frequency`), required fields (`compatible`, `reg`, `reset-gpios`, `port`), compatible matching, and `unevaluatedProperties: false`. Conditional/allOf fragments count: 0; these are used for inherited common-panel requirements, bus-specific SPI/LVDS constraints, or compatible-specific allowances.

Control flow: validation selects the schema by the panel compatible, applies the referenced common panel schema, checks required power/reset/control properties, and rejects properties outside the declared set. Example count is 1; examples usually place the panel below a DSI or SPI bus, set `reg` when the bus has addressable children, attach regulators and GPIOs, and connect `port`/`ports` endpoints to a display controller or bridge. For LVDS-style files, `data-mapping`, physical dimensions, `panel-timing`, and one or two ports are part of the display pipeline contract.

State and persistence behavior: the schema stores no mutable runtime state. It constrains DTS source that persists board-specific panel wiring, power rails, reset/enable GPIOs, optional backlight, rotation, and display graph links. At boot, panel, bridge, DRM, regulator, GPIO, SPI/DSI, and backlight drivers turn that static description into runtime probe and power-sequencing state.

Dependencies/integration points: integrates with `panel-common.yaml#` or the referenced LVDS/dual-panel schema, graph endpoint bindings, regulator and GPIO bindings, optional backlight nodes, bus bindings for SPI or DSI `reg` addressing, and the Linux DRM panel driver selected by the compatible string. Compatible fallback pairs are the handoff between board-specific panel names and shared controller drivers.

Risks: required rails and GPIO names encode driver expectations, so renaming or omitting them can make probe fail even when the physical panel is present. Compatible fallback order must be exact for shared controller drivers. `additionalProperties: false` catches typos but also requires schema updates for new wiring. Display graph endpoint mistakes, missing backlights, wrong LVDS data mapping, or incomplete timing data can pass driver probe but produce a blank or unstable panel.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/nec,nl8048hl11.yaml` and `make dtbs_check` for boards using the compatible. Useful negative tests are missing each required property, malformed `reg`, extra typo properties, absent `port`/`ports` endpoints, invalid compatible fallback order, omitted regulators/GPIOs, and LVDS timing or data-mapping mismatches where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/nec,nl8048hl11.yaml -->
