# subset-b-000617 research

Grouped research for Linux Devicetree thermal, timer, timestamp, TPM, and trigger-source YAML schemas under the Ceph client source tree. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/qcom-tsens.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/qcom-tsens.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/qcom-tsens.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `QCOM SoC Temperature Sensor (TSENS)` and documents: QCOM SoCs have TSENS IP to allow temperature measurement. There are currently three distinct major versions of the IP that is supported by a single driver. The IP versions are named v0.1, v1 and v2 in the driver, where v0.1 captures everything before v1 when there was no versioning information..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#qcom,sensors`, `#thermal-sensor-cells`, `compatible`, `interrupt-names`, `interrupts`, `nvmem-cell-names`, `nvmem-cells`, `reg`. Required keys across the schema are `#qcom,sensors`, `compatible`, `interrupt-names`, `interrupts`, `reg`. Compatible values exposed by the schema are `qcom,ipq8064-tsens`, `qcom,msm8960-tsens`, `qcom,mdm9607-tsens`, `qcom,msm8226-tsens`, `qcom,msm8909-tsens`, `qcom,msm8916-tsens`, `qcom,msm8939-tsens`, `qcom,msm8974-tsens`, `qcom,tsens-v0_1`, `qcom,ipq5018-tsens`, `qcom,msm8937-tsens`, `qcom,msm8956-tsens`, `qcom,msm8976-tsens`, `qcom,qcs404-tsens`, `qcom,tsens-v1`, `qcom,eliza-tsens`, `qcom,glymur-tsens`, `qcom,kaanapali-tsens`, `qcom,milos-tsens`, `qcom,msm8953-tsens`, `qcom,msm8996-tsens`, `qcom,msm8998-tsens`, `qcom,qcm2290-tsens`, `qcom,qcs8300-tsens`, and 28 more. Provider cell contracts are `#thermal-sensor-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, `#thermal-sensor-cells`, `nvmem-cells`, `nvmem-cell-names`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32`, `thermal-sensor.yaml#`, and then applies conditional branches `allOf`=1, `oneOf`=3, `if`=4, `then`=4. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32`, `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`, `#thermal-sensor-cells`, `nvmem-cells`, `nvmem-cell-names`. The file has 6 example block(s) and source signal 444 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `minItems=1`, `maxItems=2`, `minItems=5`, `maxItems=35`, `maxItems=51`, `minItems=8`, `minimum=1`, `maximum=16`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/qcom-tsens.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/qcom-tsens.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/qoriq-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/qoriq-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/qoriq-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Thermal Monitoring Unit (TMU) on Freescale QorIQ SoCs`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clocks`, `compatible`, `fsl,tmu-calibration`, `fsl,tmu-range`, `interrupts`, `little-endian`, `reg`. Required keys across the schema are `compatible`, `fsl,tmu-calibration`, `fsl,tmu-range`, `interrupts`, `reg`. Compatible values exposed by the schema are `fsl,qoriq-tmu`, `fsl,imx8mq-tmu`. Provider cell contracts are `#thermal-sensor-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `#thermal-sensor-cells`, `little-endian`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32-matrix`, `thermal-sensor.yaml#`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32-matrix`, `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `#thermal-sensor-cells`, `little-endian`. The file has 1 example block(s) and source signal 118 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maxItems=1`, `minItems=2`, `maxItems=7`, `minItems=1`, `maxItems=64`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/qoriq-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/qoriq-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rcar-gen3-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rcar-gen3-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rcar-gen3-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Renesas R-Car Gen3 Thermal Sensor` and documents: On most R-Car Gen3 and later SoCs, the thermal sensor controllers (TSC) control the thermal sensors (THS) which are the analog circuits for measuring temperature (Tj) inside the LSI..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `resets`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `resets`. Compatible values exposed by the schema are `renesas,r8a774a1-thermal`, `renesas,r8a774b1-thermal`, `renesas,r8a774e1-thermal`, `renesas,r8a7795-thermal`, `renesas,r8a7796-thermal`, `renesas,r8a77961-thermal`, `renesas,r8a77965-thermal`, `renesas,r8a77980-thermal`, `renesas,r8a779a0-thermal`, `renesas,r8a779f0-thermal`, `renesas,r8a779g0-thermal`, `renesas,r8a779h0-thermal`. Provider cell contracts are `#thermal-sensor-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`, follows referenced common schemas `thermal-sensor.yaml#`, and then applies conditional branches `if`=2, `then`=2, `else`=1, `not`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`. The file has 2 example block(s) and source signal 153 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maxItems=1`, `minItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/rcar-gen3-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rcar-gen3-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rcar-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rcar-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rcar-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Renesas R-Car Thermal`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `resets`. Required keys across the schema are `#thermal-sensor-cells`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `resets`. Compatible values exposed by the schema are `renesas,thermal-r8a73a4`, `renesas,thermal-r8a7779`, `renesas,rcar-thermal`, `renesas,thermal-r8a7742`, `renesas,thermal-r8a7743`, `renesas,thermal-r8a7744`, `renesas,rcar-gen2-thermal`, `renesas,thermal-r8a7790`, `renesas,thermal-r8a7791`, `renesas,thermal-r8a7792`, `renesas,thermal-r8a7793`, `renesas,thermal-r8a774c0`, `renesas,thermal-r8a77970`, `renesas,thermal-r8a77990`, `renesas,thermal-r8a77995`. Provider cell contracts are `#thermal-sensor-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=2, `then`=2, `not`=2. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`. The file has 3 example block(s) and source signal 155 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=4`, `maxItems=3`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/rcar-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rcar-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/renesas,r9a08g045-tsu.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/renesas,r9a08g045-tsu.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/renesas,r9a08g045-tsu.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Renesas RZ/G3S Thermal Sensor Unit` and documents: The thermal sensor unit (TSU) measures the temperature(Tj) inside the LSI..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clocks`, `compatible`, `io-channel-names`, `io-channels`, `power-domains`, `reg`, `resets`. Required keys across the schema are `#thermal-sensor-cells`, `clocks`, `compatible`, `io-channel-names`, `io-channels`, `power-domains`, `reg`, `resets`. Compatible values exposed by the schema are `renesas,r9a08g045-tsu`. Provider cell contracts are `#thermal-sensor-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`, `io-channels`, follows referenced common schemas `thermal-sensor.yaml#`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`, `io-channels`. The file has 1 example block(s) and source signal 93 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/renesas,r9a08g045-tsu.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/renesas,r9a08g045-tsu.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/renesas,r9a09g047-tsu.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/renesas,r9a09g047-tsu.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/renesas,r9a09g047-tsu.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Renesas RZ/G3E Temperature Sensor Unit (TSU)` and documents: The Temperature Sensor Unit (TSU) is an integrated thermal sensor that monitors the chip temperature on the Renesas RZ/G3E SoC. The TSU provides real-time temperature measurements for thermal management..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clocks`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `reg`, `renesas,tsu-trim`, `resets`. Required keys across the schema are `#thermal-sensor-cells`, `clocks`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `reg`, `renesas,tsu-trim`, `resets`. Compatible values exposed by the schema are `renesas,r9a09g047-tsu`, `renesas,r9a09g077-tsu`, `renesas,r9a09g056-tsu`, `renesas,r9a09g057-tsu`, `renesas,r9a09g087-tsu`. Provider cell contracts are `#thermal-sensor-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`, follows referenced common schemas `/schemas/types.yaml#/definitions/phandle-array`, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=2, `then`=2. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/phandle-array`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`. The file has 1 example block(s) and source signal 117 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/renesas,r9a09g047-tsu.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/renesas,r9a09g047-tsu.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rockchip-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rockchip-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rockchip-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Temperature Sensor ADC (TSADC) on Rockchip SoCs`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#address-cells`, `#size-cells`, `#thermal-sensor-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `nvmem-cell-names`, `nvmem-cells`, `reg`, `reset-names`, `resets`, `rockchip,grf`, `rockchip,hw-tshut-mode`, `rockchip,hw-tshut-polarity`, `rockchip,hw-tshut-temp`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `resets`, `rockchip,grf`. Compatible values exposed by the schema are `rockchip,px30-tsadc`, `rockchip,rk3228-tsadc`, `rockchip,rk3288-tsadc`, `rockchip,rk3328-tsadc`, `rockchip,rk3368-tsadc`, `rockchip,rk3399-tsadc`, `rockchip,rk3568-tsadc`, `rockchip,rk3576-tsadc`, `rockchip,rk3588-tsadc`, `rockchip,rv1108-tsadc`. Provider cell contracts are `#thermal-sensor-cells const `1``, `#address-cells const `1``, `#size-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `#thermal-sensor-cells`, `nvmem-cells`, `nvmem-cell-names`, follows referenced common schemas `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `thermal-sensor.yaml#`, and then applies conditional branches `allOf`=1, `if`=3, `then`=3, `else`=1, `not`=2. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `#thermal-sensor-cells`, `nvmem-cells`, `nvmem-cell-names`. The file has 1 example block(s) and source signal 178 lines with top-level schema blocks `properties`, `required`, `allOf`, `patternProperties`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, patternProperties `@[0-9a-f]+$`, limits `unevaluatedProperties=False`, `maxItems=1`, `minItems=2`, `maxItems=2`, `minItems=1`, `maxItems=3`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/rockchip-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rockchip-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rzg2l-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rzg2l-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rzg2l-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Renesas RZ/G2L Thermal Sensor Unit` and documents: On RZ/G2L SoCs, the thermal sensor unit (TSU) measures the temperature(Tj) inside the LSI..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. Required keys across the schema are `clocks`, `compatible`, `power-domains`, `reg`, `resets`. Compatible values exposed by the schema are `renesas,r9a07g043-tsu`, `renesas,r9a07g044-tsu`, `renesas,r9a07g054-tsu`, `renesas,rzg2l-tsu`. Provider cell contracts are `#thermal-sensor-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`, follows referenced common schemas `thermal-sensor.yaml#`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `clocks`, `resets`, `power-domains`, `#thermal-sensor-cells`. The file has 1 example block(s) and source signal 79 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/rzg2l-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/rzg2l-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/samsung,exynos-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/samsung,exynos-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/samsung,exynos-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Samsung Exynos SoC Thermal Management Unit (TMU)` and documents: For multi-instance tmu each instance should have an alias correctly numbered in "aliases" node..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `vtmu-supply`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `samsung,exynos3250-tmu`, `samsung,exynos4412-tmu`, `samsung,exynos4210-tmu`, `samsung,exynos5250-tmu`, `samsung,exynos5260-tmu`, `samsung,exynos5420-tmu`, `samsung,exynos5420-tmu-ext-triminfo`, `samsung,exynos5433-tmu`, `samsung,exynos7-tmu`. Provider cell contracts are `#thermal-sensor-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#thermal-sensor-cells`, follows referenced common schemas `/schemas/thermal/thermal-sensor.yaml`, and then applies conditional branches `allOf`=1, `if`=3, `then`=3. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/thermal/thermal-sensor.yaml`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#thermal-sensor-cells`. The file has 3 example block(s) and source signal 185 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=3`, `maxItems=1`, `minItems=2`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/samsung,exynos-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/samsung,exynos-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/socionext,uniphier-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/socionext,uniphier-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/socionext,uniphier-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Socionext UniPhier thermal monitor` and documents: This describes the devicetree bindings for thermal monitor supported by PVT(Process, Voltage and Temperature) monitoring unit implemented on Socionext UniPhier SoCs..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `compatible`, `interrupts`, `socionext,tmod-calibration`. Required keys across the schema are `compatible`, `interrupts`. Compatible values exposed by the schema are `socionext,uniphier-pxs2-thermal`, `socionext,uniphier-ld20-thermal`, `socionext,uniphier-pxs3-thermal`, `socionext,uniphier-nx1-thermal`. Provider cell contracts are `#thermal-sensor-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `interrupts`, `#thermal-sensor-cells`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`, `thermal-sensor.yaml#`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32-array`, `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `interrupts`, `#thermal-sensor-cells`. The file has 1 example block(s) and source signal 55 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maxItems=1`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/socionext,uniphier-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/socionext,uniphier-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/sprd-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/sprd-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/sprd-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Spreadtrum thermal sensor controller`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#address-cells`, `#size-cells`, `#thermal-sensor-cells`, `clock-names`, `clocks`, `compatible`, `nvmem-cell-names`, `nvmem-cells`, `reg`. Required keys across the schema are `#address-cells`, `#size-cells`, `clock-names`, `clocks`, `compatible`, `nvmem-cell-names`, `nvmem-cells`, `reg`. Compatible values exposed by the schema are `sprd,ums512-thermal`. Provider cell contracts are `#thermal-sensor-cells const `1``, `#address-cells const `1``, `#size-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `clocks`, `clock-names`, `#thermal-sensor-cells`, `nvmem-cells`, `nvmem-cell-names`, follows referenced common schemas `thermal-sensor.yaml#`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `clocks`, `clock-names`, `#thermal-sensor-cells`, `nvmem-cells`, `nvmem-cell-names`. The file has 1 example block(s) and source signal 112 lines with top-level schema blocks `properties`, `required`, `patternProperties`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, patternProperties `^([a-z]*-)?sensor(-section)?@[0-9]+$`, limits `unevaluatedProperties=False`, `maxItems=1`, `maxItems=2`, `additionalProperties=False`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/sprd-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/sprd-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,stih407-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,stih407-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,stih407-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `STMicroelectronics STi digital thermal sensor (DTS)`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `reg`. Compatible values exposed by the schema are `st,stih407-thermal`. Provider cell contracts are `#thermal-sensor-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#thermal-sensor-cells`, follows referenced common schemas `thermal-sensor.yaml`, and then applies conditional branches `allOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `thermal-sensor.yaml`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#thermal-sensor-cells`. The file has 1 example block(s) and source signal 58 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/st,stih407-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,stih407-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,stm32-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,stm32-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,stm32-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `STMicroelectronics STM32 digital thermal sensor (DTS)`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `st,stm32-thermal`. Provider cell contracts are `#thermal-sensor-cells const `0``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#thermal-sensor-cells`, follows referenced common schemas `thermal-sensor.yaml#`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#thermal-sensor-cells`. The file has 1 example block(s) and source signal 80 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/st,stm32-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,stm32-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,thermal-spear1340.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,thermal-spear1340.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,thermal-spear1340.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `SPEAr Thermal Sensor`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `reg`, `st,thermal-flags`. Required keys across the schema are `compatible`, `reg`, `st,thermal-flags`. Compatible values exposed by the schema are `st,thermal-spear1340`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 1 example block(s) and source signal 36 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/st,thermal-spear1340.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/st,thermal-spear1340.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml` is a Linux Devicetree YAML schema for generic thermal cooling-device capability schema. It preserves the binding title `Thermal cooling device` and documents: Thermal management is achieved in devicetree by describing the sensor hardware and the software abstraction of cooling devices and thermal zones required to take appropriate action to mitigate thermal overload. The following node types are used to completely describe a thermal management system in devicetree: - thermal-sensor: device that measures temperature, has SoC-specific bindings - cooling-device: device used to dissipate heat either passively or actively - thermal-zones: a container of the following node types used to describe all thermal data for the platform This binding describes....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#cooling-cells`. Required keys across the schema are none. Compatible values exposed by the schema are none. Provider cell contracts are `#cooling-cells const `2``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `#cooling-cells`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `#cooling-cells`. The file has 1 example block(s) and source signal 122 lines with top-level schema blocks `properties`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=True, limits `additionalProperties=True`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-idle.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-idle.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-idle.yaml` is a Linux Devicetree YAML schema for generic thermal idle cooling integration schema. It preserves the binding title `Thermal idle cooling device` and documents: The thermal idle cooling device allows the system to passively mitigate the temperature on the device by injecting idle cycles, forcing it to cool down. This binding describes the thermal idle node..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#cooling-cells`, `$nodename`, `duration-us`, `exit-latency-us`. Required keys across the schema are `#cooling-cells`. Compatible values exposed by the schema are none. Provider cell contracts are `#cooling-cells const `2``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `#cooling-cells`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `#cooling-cells`. The file has 1 example block(s) and source signal 152 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/thermal-idle.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-idle.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-sensor.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-sensor.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-sensor.yaml` is a Linux Devicetree YAML schema for generic thermal sensor provider or consumer helper schema. It preserves the binding title `Thermal sensor` and documents: Thermal management is achieved in devicetree by describing the sensor hardware and the software abstraction of thermal zones required to take appropriate action to mitigate thermal overloads. The following node types are used to completely describe a thermal management system in devicetree: - thermal-sensor: device that measures temperature, has SoC-specific bindings - cooling-device: device used to dissipate heat either passively or actively - thermal-zones: a container of the following node types used to describe all thermal data for the platform This binding describes the thermal-sensor.....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`. Required keys across the schema are `#thermal-sensor-cells`. Compatible values exposed by the schema are none. Provider cell contracts are `#thermal-sensor-cells enum `0`, `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `#thermal-sensor-cells`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `#thermal-sensor-cells`. The file has 1 example block(s) and source signal 77 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=True, limits `additionalProperties=True`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/thermal-sensor.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-sensor.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-zones.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-zones.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-zones.yaml` is a Linux Devicetree YAML schema for generic thermal-zone policy graph binding. It preserves the binding title `Thermal zone` and documents: Thermal management is achieved in devicetree by describing the sensor hardware and the software abstraction of cooling devices and thermal zones required to take appropriate action to mitigate thermal overloads. The following node types are used to completely describe a thermal management system in devicetree: - thermal-sensor: device that measures temperature, has SoC-specific bindings - cooling-device: device used to dissipate heat either passively or actively - thermal-zones: a container of the following node types used to describe all thermal data for the platform This binding describes....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `$nodename`. Required keys across the schema are `cooling-device`, `hysteresis`, `temperature`, `thermal-sensors`, `trip`, `type`. Compatible values exposed by the schema are none.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as none, follows referenced common schemas `/schemas/types.yaml#/definitions/int32`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/int32`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are none. The file has 1 example block(s) and source signal 356 lines with top-level schema blocks `properties`, `required`, `patternProperties`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, patternProperties `^[a-zA-Z][a-zA-Z0-9\-]{1,10}-thermal$`, `^map[-a-zA-Z0-9]*$`, limits `additionalProperties=False`, `maxItems=1`, `minimum=-273000`, `maximum=200000`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/thermal-zones.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-zones.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/ti,am654-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/ti,am654-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/ti,am654-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Texas Instruments AM654 VTM (DTS)`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `compatible`, `power-domains`, `reg`. Required keys across the schema are `compatible`, `power-domains`, `reg`. Compatible values exposed by the schema are `ti,am654-vtm`. Provider cell contracts are `#thermal-sensor-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `power-domains`, `#thermal-sensor-cells`, follows referenced common schemas `thermal-sensor.yaml#`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `power-domains`, `#thermal-sensor-cells`. The file has 1 example block(s) and source signal 57 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/ti,am654-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/ti,am654-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/ti,j72xx-thermal.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/ti,j72xx-thermal.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/ti,j72xx-thermal.yaml` is a Linux Devicetree YAML schema for SoC thermal sensor controller binding. It preserves the binding title `Texas Instruments J72XX VTM (DTS)` and documents: The TI K3 family of SoCs typically have a Voltage & Thermal Management (VTM) device to control up to 8 temperature diode sensors to measure silicon junction temperatures from different hotspots of the chip as well as provide temperature, interrupt and alerting information. The following polynomial equation can then be used to convert value returned by this device into a temperature in Celsius Temp(C) = (-9.2627e-12) * x^4 + (6.0373e-08) * x^3 + \ (-1.7058e-04) * x^2 + (3.2512e-01) * x + (-4.9003e+01).

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#thermal-sensor-cells`, `compatible`, `power-domains`, `reg`. Required keys across the schema are `compatible`, `power-domains`, `reg`. Compatible values exposed by the schema are `ti,j721e-vtm`, `ti,j7200-vtm`. Provider cell contracts are `#thermal-sensor-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `power-domains`, `#thermal-sensor-cells`, follows referenced common schemas `thermal-sensor.yaml#`, and then applies conditional branches `allOf`=1, `if`=1, `then`=1, `else`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `thermal-sensor.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `power-domains`, `#thermal-sensor-cells`. The file has 1 example block(s) and source signal 97 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `minItems=2`, `maxItems=1`, `minItems=3`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/ti,j72xx-thermal.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/ti,j72xx-thermal.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/actions,owl-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/actions,owl-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/actions,owl-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Actions Semi Owl timer` and documents: Actions Semi Owl SoCs provide 32bit and 2Hz timers. The 32bit timers support dynamic irq, as well as one-shot mode..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupt-names`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupt-names`, `interrupts`, `reg`. Compatible values exposed by the schema are `actions,s500-timer`, `actions,s700-timer`, `actions,s900-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `if`=2, `then`=2. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`. The file has 1 example block(s) and source signal 107 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`, `maxItems=6`, `minItems=4`, `maxItems=4`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/actions,owl-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/actions,owl-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/allwinner,sun4i-a10-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/allwinner,sun4i-a10-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/allwinner,sun4i-a10-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Allwinner A10 Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `allwinner,sun4i-a10-timer`, `allwinner,sun8i-a23-timer`, `allwinner,sun8i-v3s-timer`, `allwinner,suniv-f1c100s-timer`, `allwinner,sun20i-d1-timer`, `allwinner,sun50i-a64-timer`, `allwinner,sun50i-h6-timer`, `allwinner,sun50i-h616-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=3, `then`=3. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 101 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=2`, `maxItems=6`, `minItems=6`, `maxItems=2`, `minItems=3`, `maxItems=3`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/allwinner,sun4i-a10-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/allwinner,sun4i-a10-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/allwinner,sun5i-a13-hstimer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/allwinner,sun5i-a13-hstimer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/allwinner,sun5i-a13-hstimer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Allwinner A13 High-Speed Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`, `resets`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `allwinner,sun5i-a13-hstimer`, `allwinner,sun7i-a20-hstimer`, `allwinner,sun6i-a31-hstimer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `resets`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1, `if`=1, `then`=1, `else`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `resets`. The file has 1 example block(s) and source signal 77 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=2`, `maxItems=2`, `minItems=4`, `maxItems=4`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/allwinner,sun5i-a13-hstimer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/allwinner,sun5i-a13-hstimer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/altr,timer-1.0.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/altr,timer-1.0.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/altr,timer-1.0.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Altera Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-frequency`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `altr,timer-1.0`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 39 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/altr,timer-1.0.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/altr,timer-1.0.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/amlogic,meson6-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/amlogic,meson6-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/amlogic,meson6-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Amlogic Meson6 SoCs Timer Controller`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `amlogic,meson6-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 54 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `maxItems=4`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/amlogic,meson6-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/amlogic,meson6-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/andestech,plmt0.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/andestech,plmt0.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/andestech,plmt0.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Andes machine-level timer` and documents: The Andes machine-level timer device (PLMT0) provides machine-level timer functionality for a set of HARTs on a RISC-V platform. It has a single fixed-frequency monotonic time counter (MTIME) register and a time compare register (MTIMECMP) for each HART connected to the PLMT0. A timer interrupt is generated if MTIME >= MTIMECMP..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts-extended`, `reg`. Required keys across the schema are `compatible`, `interrupts-extended`, `reg`. Compatible values exposed by the schema are `andestech,qilai-plmt`, `andestech,plmt0`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 1 example block(s) and source signal 53 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`, `maxItems=32`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/andestech,plmt0.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/andestech,plmt0.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,arch_timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,arch_timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,arch_timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ARM architected timer` and documents: ARM cores may have a per-core architected timer, which provides per-cpu timers, or a memory mapped architected timer, which provides up to 8 frames with a physical and optional virtual timer per frame. The per-core architected timer is attached to a GIC to deliver its per-processor interrupts via PPIs. The memory mapped timer is attached to a GIC to deliver its interrupts via SPIs..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `allwinner,erratum-unknown1`, `always-on`, `arm,cpu-registers-not-fw-configured`, `arm,no-tick-in-suspend`, `clock-frequency`, `compatible`, `fsl,erratum-a008585`, `hisilicon,erratum-161010101`, `interrupt-names`, `interrupts`. Required keys across the schema are `compatible`, `interrupts`, `interrupts-extended`. Compatible values exposed by the schema are `arm,cortex-a15-timer`, `arm,armv7-timer`, `arm,armv8-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `interrupts`, `interrupt-names`, `arm,cpu-registers-not-fw-configured`, `always-on`, follows referenced common schemas none, and then applies conditional branches `oneOf`=3. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `interrupts`, `interrupt-names`, `arm,cpu-registers-not-fw-configured`, `always-on`. The file has 1 example block(s) and source signal 128 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `minItems=2`, `minItems=3`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/arm,arch_timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,arch_timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,arch_timer_mmio.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,arch_timer_mmio.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,arch_timer_mmio.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ARM memory mapped architected timer` and documents: ARM cores may have a memory mapped architected timer, which provides up to 8 frames with a physical and optional virtual timer per frame. The memory mapped timer is attached to a GIC to deliver its interrupts via SPIs..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#address-cells`, `#size-cells`, `always-on`, `arm,cpu-registers-not-fw-configured`, `arm,no-tick-in-suspend`, `clock-frequency`, `compatible`, `ranges`, `reg`. Required keys across the schema are `#address-cells`, `#size-cells`, `compatible`, `frame-number`, `interrupts`, `reg`. Compatible values exposed by the schema are `arm,armv7-timer-mem`. Provider cell contracts are `#address-cells enum `1`, `2``, `#size-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `arm,cpu-registers-not-fw-configured`, `always-on`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `arm,cpu-registers-not-fw-configured`, `always-on`. The file has 1 example block(s) and source signal 123 lines with top-level schema blocks `properties`, `required`, `patternProperties`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, patternProperties `^frame@[0-9a-f]+$`, limits `additionalProperties=False`, `maxItems=1`, `minimum=0`, `maximum=7`, `minItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/arm,arch_timer_mmio.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,arch_timer_mmio.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,armv7m-systick.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,armv7m-systick.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,armv7m-systick.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ARMv7M System Timer` and documents: ARMv7-M includes a system timer, known as SysTick..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-frequency`, `clocks`, `compatible`, `reg`. Required keys across the schema are `clock-frequency`, `clocks`, `compatible`, `reg`. Compatible values exposed by the schema are `arm,armv7m-systick`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `clocks`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `clocks`. The file has 2 example block(s) and source signal 54 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/arm,armv7m-systick.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,armv7m-systick.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,global_timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,global_timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,global_timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ARM Global Timer` and documents: Cortex-A9 are often associated with a per-core Global timer..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `reg`. Compatible values exposed by the schema are `arm,cortex-a5-global-timer`, `arm,cortex-a9-global-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 48 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/arm,global_timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,global_timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,mps2-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,mps2-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,mps2-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ARM MPS2 timer` and documents: The MPS2 platform has simple general-purpose 32 bits timers..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-frequency`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-frequency`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `arm,mps2-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 49 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/arm,mps2-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,mps2-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,sp804.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,sp804.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,sp804.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ARM sp804 Dual Timers` and documents: The Arm SP804 IP implements two independent timers, configurable for 16 or 32 bit operation and capable of running in one-shot, periodic, or free-running mode. The input clock is shared, but can be gated and prescaled independently for each timer. There is a viriant of Arm SP804: Hisilicon 64-bit SP804 timer. Some Hisilicon SoCs, such as Hi1212, should use the dedicated compatible: "hisilicon,sp804"..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `arm,sp804-has-irq`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `arm,sp804`, `hisilicon,sp804`, `arm,primecell`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32`, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 97 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=2`, `maxItems=1`, `minimum=1`, `maximum=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/arm,sp804.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,sp804.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,twd-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,twd-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,twd-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ARM Timer-Watchdog Timer` and documents: ARM 11MP, Cortex-A5 and Cortex-A9 are often associated with a per-core Timer-Watchdog (aka TWD), which provides both a per-cpu local timer and watchdog. The TWD is usually attached to a GIC to deliver its two per-processor interrupts..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `always-on`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `arm,cortex-a9-twd-timer`, `arm,cortex-a5-twd-timer`, `arm,arm11mp-twd-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `always-on`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `always-on`. The file has 1 example block(s) and source signal 56 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/arm,twd-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/arm,twd-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `BCM2835 System Timer` and documents: The System Timer peripheral provides four 32-bit timer channels and a single 64-bit free running counter. Each channel has an output compare register, which is compared against the 32 least significant bits of the free running counter values, and generates an interrupt..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-frequency`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `brcm,bcm2835-system-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 50 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcmbca-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcmbca-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcmbca-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Broadcom Broadband SoC timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `reg`. Required keys across the schema are `reg`. Compatible values exposed by the schema are `brcm,bcm6345-timer`, `brcm,bcm63138-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 1 example block(s) and source signal 40 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/brcm,bcmbca-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcmbca-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,kona-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,kona-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,kona-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Broadcom Kona family timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-frequency`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-frequency`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `brcm,kona-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 52 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/brcm,kona-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,kona-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cdns,ttc.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cdns,ttc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cdns,ttc.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Cadence TTC - Triple Timer Counter`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#pwm-cells`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `timer-width`. Required keys across the schema are `#pwm-cells`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `cdns,ttc`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32`, and then applies conditional branches `allOf`=1, `if`=1, `then`=1, `not`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`. The file has 2 example block(s) and source signal 72 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `maxItems=3`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/cdns,ttc.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cdns,ttc.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cirrus,clps711x-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cirrus,clps711x-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cirrus,clps711x-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Cirrus Logic CLPS711X Timer Counter`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `cirrus,ep7312-timer`, `cirrus,ep7209-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 45 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/cirrus,clps711x-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cirrus,clps711x-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cirrus,ep9301-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cirrus,ep9301-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cirrus,ep9301-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Cirrus Logic EP93xx timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts`, `reg`, `resets`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `cirrus,ep9301-timer`, `cirrus,ep9302-timer`, `cirrus,ep9307-timer`, `cirrus,ep9312-timer`, `cirrus,ep9315-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `resets`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `resets`. The file has 1 example block(s) and source signal 49 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/cirrus,ep9301-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cirrus,ep9301-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cnxt,cx92755-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cnxt,cx92755-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cnxt,cx92755-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Conexant Digicolor SoCs Timer Controller`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `cnxt,cx92755-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 49 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/cnxt,cx92755-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/cnxt,cx92755-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/csky,gx6605s-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/csky,gx6605s-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/csky,gx6605s-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `gx6605s SOC Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `csky,gx6605s-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 40 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/csky,gx6605s-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/csky,gx6605s-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/csky,mptimer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/csky,mptimer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/csky,mptimer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `C-SKY Multi-processors Timer` and documents: C-SKY multi-processors timer is designed for C-SKY SMP system and the regs are accessed by cpu co-processor 4 registers with mtcr/mfcr. - PTIM_CTLR "cr<0, 14>" Control reg to start reset timer. - PTIM_TSR "cr<1, 14>" Interrupt cleanup status reg. - PTIM_CCVR "cr<3, 14>" Current counter value reg. - PTIM_LVR "cr<6, 14>" Window value reg to trigger next event..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`. Required keys across the schema are `clocks`, `compatible`, `interrupts`. Compatible values exposed by the schema are `csky,mptimer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 46 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/csky,mptimer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/csky,mptimer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/econet,en751221-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/econet,en751221-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/econet,en751221-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `EcoNet EN751221 High Precision Timer (HPT)` and documents: The EcoNet High Precision Timer (HPT) is a timer peripheral found in various EcoNet SoCs, including the EN751221 and EN751627 families. It provides per-VPE count/compare registers and a per-CPU control register, with a single interrupt line using a percpu-devid interrupt mechanism..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `econet,en751221-timer`, `econet,en751627-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=1, `then`=1, `else`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 2 example block(s) and source signal 80 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=2`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/econet,en751221-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/econet,en751221-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ezchip,nps400-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ezchip,nps400-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ezchip,nps400-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `EZChip NPS400 Timers`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`. Required keys across the schema are `clocks`, `compatible`, `interrupts`. Compatible values exposed by the schema are `ezchip,nps400-timer0`, `ezchip,nps400-timer1`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `if`=1, `then`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 45 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/ezchip,nps400-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ezchip,nps400-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/faraday,fttmr010.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/faraday,fttmr010.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/faraday,fttmr010.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Faraday FTTMR010 timer` and documents: This timer is a generic IP block from Faraday Technology, embedded in the Cortina Systems Gemini SoCs and other designs..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `resets`, `syscon`. Required keys across the schema are `compatible`, `interrupts`, `reg`, `syscon`. Compatible values exposed by the schema are `moxa,moxart-timer`, `faraday,fttmr010`, `aspeed,ast2400-timer`, `aspeed,ast2500-timer`, `aspeed,ast2600-timer`, `cortina,gemini-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, follows referenced common schemas `/schemas/types.yaml#/definitions/phandle`, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=1, `then`=1, `else`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/phandle`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. The file has 1 example block(s) and source signal 89 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`, `maxItems=8`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/faraday,fttmr010.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/faraday,fttmr010.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,ftm-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,ftm-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,ftm-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Freescale FlexTimer Module (FTM) Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `big-endian`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `fsl,ftm-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `big-endian`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `big-endian`. The file has 1 example block(s) and source signal 62 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=4`, `maxItems=4`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/fsl,ftm-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,ftm-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,gtm.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,gtm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,gtm.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Freescale General-purpose Timers Module`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-frequency`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-frequency`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `fsl,mpc8308-gtm`, `fsl,mpc8313-gtm`, `fsl,mpc8315-gtm`, `fsl,mpc8360-gtm`, `fsl,gtm`, `fsl,mpc8360-qe-gtm`, `fsl,mpc8569-qe-gtm`, `fsl,qe-gtm`, `fsl,cpm2-gtm`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 2 example block(s) and source signal 83 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/fsl,gtm.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,gtm.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,imxgpt.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,imxgpt.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,imxgpt.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Freescale i.MX General Purpose Timer (GPT)`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `fsl,imx1-gpt`, `fsl,imx21-gpt`, `fsl,imx27-gpt`, `fsl,imx31-gpt`, `fsl,imx25-gpt`, `fsl,imx35-gpt`, `fsl,imx50-gpt`, `fsl,imx51-gpt`, `fsl,imx53-gpt`, `fsl,imx6q-gpt`, `fsl,imx6dl-gpt`, `fsl,imx6sl-gpt`, `fsl,imx6sx-gpt`, `fsl,imx7d-gpt`, `fsl,imx8mp-gpt`, `fsl,imxrt1050-gpt`, `fsl,imxrt1170-gpt`, `fsl,imx6ul-gpt`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=1, `then`=1, `else`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 108 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=2`, `maxItems=3`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/fsl,imxgpt.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,imxgpt.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,timrot.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,timrot.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,timrot.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Freescale MXS Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `fsl,imx23-timrot`, `fsl,imx28-timrot`, `fsl,timrot`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 48 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/fsl,timrot.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,timrot.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,vf610-pit.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,vf610-pit.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,vf610-pit.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Freescale Periodic Interrupt Timer (PIT)` and documents: The PIT module is an array of timers that can be used to raise interrupts and trigger DMA channels..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `fsl,vf610-pit`, `nxp,s32g2-pit`, `nxp,s32g3-pit`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 59 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/fsl,vf610-pit.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/fsl,vf610-pit.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/hpe,gxp-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/hpe,gxp-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/hpe,gxp-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `HPE GXP Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `hpe,gxp-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 47 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/hpe,gxp-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/hpe,gxp-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/img,pistachio-gptimer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/img,pistachio-gptimer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/img,pistachio-gptimer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Pistachio general-purpose timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `img,cr-periph`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `img,cr-periph`, `interrupts`, `reg`. Compatible values exposed by the schema are `img,pistachio-gptimer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas `/schemas/types.yaml#/definitions/phandle`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/phandle`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 69 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/img,pistachio-gptimer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/img,pistachio-gptimer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ingenic,sysost.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ingenic,sysost.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ingenic,sysost.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `SYSOST in Ingenic XBurst family SoCs` and documents: The SYSOST in an Ingenic SoC provides one 64bit timer for clocksource and one or more 32bit timers for clockevent..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#clock-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `#clock-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `ingenic,x1000-ost`, `ingenic,x2000-ost`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 63 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/ingenic,sysost.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ingenic,sysost.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ingenic,tcu.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ingenic,tcu.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ingenic,tcu.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Ingenic SoCs Timer/Counter Unit (TCU)` and documents: For a description of the TCU hardware and drivers, have a look at Documentation/arch/mips/ingenic-tcu.rst..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#address-cells`, `#clock-cells`, `#interrupt-cells`, `#size-cells`, `$nodename`, `assigned-clock-parents`, `assigned-clock-rates`, `assigned-clocks`, `clock-names`, `clocks`, `compatible`, `ingenic,pwm-channels-mask`, `interrupt-controller`, `interrupts`, `ranges`, `reg`. Required keys across the schema are `#clock-cells`, `#interrupt-cells`, `clock-names`, `clocks`, `compatible`, `interrupt-controller`, `interrupts`, `reg`. Compatible values exposed by the schema are `ingenic,jz4740-tcu`, `ingenic,jz4725b-tcu`, `ingenic,jz4760-tcu`, `ingenic,x1000-tcu`, `simple-mfd`, `ingenic,jz4780-tcu`, `ingenic,jz4770-tcu`, `ingenic,jz4760b-tcu`. Provider cell contracts are `#address-cells const `1``, `#size-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-rates`, follows referenced common schemas `/schemas/pwm/pwm.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/watchdog/watchdog.yaml#`, and then applies conditional branches `oneOf`=4. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/pwm/pwm.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/watchdog/watchdog.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-rates`. The file has 1 example block(s) and source signal 302 lines with top-level schema blocks `properties`, `required`, `oneOf`, `patternProperties`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, patternProperties `^pwm@[a-f0-9]+$`, `^timer@[a-f0-9]+$`, `^watchdog@[a-f0-9]+$`, limits `additionalProperties=False`, `maxItems=1`, `minItems=3`, `minItems=1`, `maxItems=8`, `minimum=0`, `maximum=255`, `unevaluatedProperties=False`, `minItems=6`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/ingenic,tcu.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ingenic,tcu.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/intel,ixp4xx-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/intel,ixp4xx-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/intel,ixp4xx-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Intel IXP4xx XScale Networking Processors Timers` and documents: This timer is found in the Intel IXP4xx processors..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `intel,ixp4xx-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 43 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/intel,ixp4xx-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/intel,ixp4xx-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/jcore,pit.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/jcore,pit.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/jcore,pit.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `J-Core Programmable Interval Timer and Clocksource`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `jcore,pit`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 43 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/jcore,pit.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/jcore,pit.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/loongson,ls1x-pwmtimer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/loongson,ls1x-pwmtimer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/loongson,ls1x-pwmtimer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Loongson-1 PWM timer` and documents: Loongson-1 PWM timer can be used for system clock source and clock event timers..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `loongson,ls1b-pwmtimer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 48 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/loongson,ls1x-pwmtimer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/loongson,ls1x-pwmtimer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/lsi,zevio-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/lsi,zevio-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/lsi,zevio-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `TI-NSPIRE timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `lsi,zevio-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `if`=1, `then`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 2 example block(s) and source signal 56 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=1`, `minItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/lsi,zevio-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/lsi,zevio-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/marvell,armada-370-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/marvell,armada-370-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/marvell,armada-370-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Marvell Armada 370, 375, 380 and XP Timers`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `marvell,armada-380-timer`, `marvell,armada-xp-timer`, `marvell,armada-375-timer`, `marvell,armada-370-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=1, `then`=1, `else`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 88 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=2`, `minItems=2`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/marvell,armada-370-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/marvell,armada-370-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/marvell,orion-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/marvell,orion-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/marvell,orion-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Marvell Orion SoC timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `marvell,orion-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 43 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/marvell,orion-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/marvell,orion-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mediatek,timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mediatek,timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mediatek,timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `MediaTek SoC timers` and documents: MediaTek SoCs have different timers on different platforms, CPUX (ARM/ARM64 System Timer), GPT (General Purpose Timer) and SYST (System Timer)..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `mediatek,mt6577-timer`, `mediatek,mt6765-timer`, `mediatek,mt6795-systimer`, `mediatek,mt2701-timer`, `mediatek,mt6572-timer`, `mediatek,mt6580-timer`, `mediatek,mt6582-timer`, `mediatek,mt6589-timer`, `mediatek,mt6795-timer`, `mediatek,mt7623-timer`, `mediatek,mt8127-timer`, `mediatek,mt8135-timer`, `mediatek,mt8173-timer`, `mediatek,mt8516-timer`, `mediatek,mt7629-timer`, `mediatek,mt8183-timer`, `mediatek,mt8186-timer`, `mediatek,mt8188-timer`, `mediatek,mt8192-timer`, `mediatek,mt8195-timer`, `mediatek,mt8196-timer`, `mediatek,mt8365-systimer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 87 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/mediatek,timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mediatek,timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mrvl,mmp-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mrvl,mmp-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mrvl,mmp-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Marvell MMP Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `$nodename`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `mrvl,mmp-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 46 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/mrvl,mmp-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mrvl,mmp-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mstar,msc313e-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mstar,msc313e-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mstar,msc313e-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Mstar MSC313e Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `mstar,msc313e-timer`, `sstar,ssd20xd-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 46 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/mstar,msc313e-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/mstar,msc313e-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nuvoton,npcm7xx-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nuvoton,npcm7xx-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nuvoton,npcm7xx-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Nuvoton NPCM7xx timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `nuvoton,wpcm450-timer`, `nuvoton,npcm750-timer`, `nuvoton,npcm845-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 54 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/nuvoton,npcm7xx-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nuvoton,npcm7xx-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nvidia,tegra-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nvidia,tegra-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nvidia,tegra-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `NVIDIA Tegra timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `nvidia,tegra210-timer`, `nvidia,tegra114-timer`, `nvidia,tegra124-timer`, `nvidia,tegra132-timer`, `nvidia,tegra30-timer`, `nvidia,tegra20-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `oneOf`=2, `if`=3, `then`=3. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 2 example block(s) and source signal 149 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=14`, `maxItems=6`, `maxItems=4`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/nvidia,tegra-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nvidia,tegra-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nvidia,tegra186-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nvidia,tegra186-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nvidia,tegra186-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `NVIDIA Tegra186 timer` and documents: The Tegra timer provides 29-bit timer counters and a 32-bit timestamp counter. Each NV timer selects its timing reference signal from the 1 MHz reference generated by USEC, TSC or either clk_m or OSC. Each TMR can be programmed to generate one-shot, periodic, or watchdog interrupts..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `nvidia,tegra186-timer`, `nvidia,tegra234-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=2, `then`=2. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 2 example block(s) and source signal 108 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `maxItems=10`, `maxItems=16`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/nvidia,tegra186-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nvidia,tegra186-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,lpc3220-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,lpc3220-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,lpc3220-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `NXP LPC3220 timer` and documents: The NXP LPC3220 timer is used on a wide range of NXP SoCs. This includes LPC32xx, LPC178x, LPC18xx and LPC43xx parts..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `resets`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `nxp,lpc3220-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. The file has 1 example block(s) and source signal 55 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/nxp,lpc3220-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,lpc3220-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,s32g2-stm.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,s32g2-stm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,s32g2-stm.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `NXP System Timer Module (STM)` and documents: The System Timer Module supports commonly required system and application software timing functions. STM includes a 32-bit count-up timer and four 32-bit compare channels with a separate interrupt source for each channel. The timer is driven by the STM module clock divided by an 8-bit prescale value..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `nxp,s32g2-stm`, `nxp,s32g3-stm`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 64 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/nxp,s32g2-stm.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,s32g2-stm.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,sysctr-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,sysctr-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,sysctr-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `NXP System Counter Module(sys_ctr)` and documents: The system counter(sys_ctr) is a programmable system counter which provides a shared time base to Cortex A15, A7, A53, A73, etc. it is intended for use in applications where the counter is always powered and support multiple, unrelated clocks. The compare frame inside can be used for timer purpose..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `nxp,no-divider`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `nxp,imx95-sysctr-timer`, `nxp,sysctr-timer`, `nxp,imx94-sysctr-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 65 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/nxp,sysctr-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,sysctr-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,tpm-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,tpm-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,tpm-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `NXP Low Power Timer/Pulse Width Modulation Module (TPM)` and documents: The Timer/PWM Module (TPM) supports input capture, output compare, and the generation of PWM signals to control electric motor and power management applications. The counter, compare and capture registers are clocked by an asynchronous clock that can remain enabled in low power modes. TPM can support global counter bus where one TPM drives the counter bus for the others, provided bit width is the same..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `fsl,imx7ulp-tpm`, `fsl,imx8ulp-tpm`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 65 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/nxp,tpm-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/nxp,tpm-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ralink,cevt-systick.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ralink,cevt-systick.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ralink,cevt-systick.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `System tick counter present in Ralink family SoCs`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `ralink,cevt-systick`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 38 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/ralink,cevt-systick.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ralink,cevt-systick.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ralink,rt2880-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ralink,rt2880-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ralink,rt2880-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Timer present in Ralink family SoCs`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `ralink,rt2880-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 44 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/ralink,rt2880-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ralink,rt2880-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/rda,8810pl-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/rda,8810pl-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/rda,8810pl-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `RDA Micro RDA8810PL Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupt-names`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupt-names`, `interrupts`, `reg`. Compatible values exposed by the schema are `rda,8810pl-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`. The file has 1 example block(s) and source signal 47 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=2`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/rda,8810pl-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/rda,8810pl-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/realtek,otto-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/realtek,otto-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/realtek,otto-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Realtek Otto SoCs Timer/Counter` and documents: Realtek SoCs support a number of timers/counters. These are used as a per CPU clock event generator and an overall CPU clocksource..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `$nodename`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `realtek,rtl9302-timer`, `realtek,otto-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 63 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/realtek,otto-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/realtek,otto-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/realtek,rtd1625-systimer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/realtek,rtd1625-systimer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/realtek,rtd1625-systimer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Realtek System Timer` and documents: The Realtek SYSTIMER (System Timer) is a 64-bit global hardware counter operating at a fixed 1MHz frequency. Thanks to its compare match interrupt capability, the timer natively supports oneshot mode for tick broadcast functionality..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `realtek,rtd1625-systimer`, `realtek,rtd1635-systimer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 47 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/realtek,rtd1625-systimer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/realtek,rtd1625-systimer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,cmt.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,cmt.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,cmt.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Renesas Compare Match Timer (CMT)` and documents: The CMT is a multi-channel 16/32/48-bit timer/counter with configurable clock inputs and programmable compare match. Channels share hardware resources but their counter and compare match values are independent. A particular CMT instance can implement only a subset of the channels supported by the CMT model. Channel indices represent the hardware position of the channel in the CMT and don't match the channel numbers in the datasheets..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `resets`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`. Compatible values exposed by the schema are `renesas,r8a7740-cmt0`, `renesas,r8a7740-cmt1`, `renesas,r8a7740-cmt2`, `renesas,r8a7740-cmt3`, `renesas,r8a7740-cmt4`, `renesas,sh73a0-cmt0`, `renesas,sh73a0-cmt1`, `renesas,sh73a0-cmt2`, `renesas,sh73a0-cmt3`, `renesas,sh73a0-cmt4`, `renesas,r8a73a4-cmt0`, `renesas,r8a7742-cmt0`, `renesas,r8a7743-cmt0`, `renesas,r8a7744-cmt0`, `renesas,r8a7745-cmt0`, `renesas,r8a77470-cmt0`, `renesas,r8a7790-cmt0`, `renesas,r8a7791-cmt0`, `renesas,r8a7792-cmt0`, `renesas,r8a7793-cmt0`, `renesas,r8a7794-cmt0`, `renesas,rcar-gen2-cmt0`, `renesas,r8a73a4-cmt1`, `renesas,r8a7742-cmt1`, and 46 more.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `power-domains`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=2, `then`=2. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `power-domains`. The file has 1 example block(s) and source signal 206 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`, `maxItems=8`, `minItems=2`, `maxItems=2`, `minItems=8`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/renesas,cmt.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,cmt.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,em-sti.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,em-sti.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,em-sti.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Renesas EMMA Mobile System Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `renesas,em-sti`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 46 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/renesas,em-sti.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,em-sti.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,mtu2.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,mtu2.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,mtu2.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Renesas Multi-Function Timer Pulse Unit 2 (MTU2)` and documents: The MTU2 is a multi-purpose, multi-channel timer/counter with configurable clock inputs and programmable compare match. Channels share hardware resources but their counter and compare match value are independent. The MTU2 hardware supports five channels indexed from 0 to 4..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `reg`. Compatible values exposed by the schema are `renesas,mtu2-r7s72100`, `renesas,mtu2`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`. The file has 1 example block(s) and source signal 76 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`, `maxItems=5`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/renesas,mtu2.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,mtu2.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,ostm.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,ostm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,ostm.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Renesas OS Timer (OSTM)` and documents: The OSTM is a multi-channel 32-bit timer/counter with fixed clock source that can operate in either interval count down timer or free-running compare match mode. Channels are independent from each other..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `resets`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `resets`. Compatible values exposed by the schema are `renesas,r7s72100-ostm`, `renesas,r7s9210-ostm`, `renesas,r9a07g043-ostm`, `renesas,r9a07g044-ostm`, `renesas,r9a07g054-ostm`, `renesas,r9a09g056-ostm`, `renesas,r9a09g057-ostm`, `renesas,ostm`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `power-domains`, follows referenced common schemas none, and then applies conditional branches `if`=1, `then`=1, `not`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `power-domains`. The file has 1 example block(s) and source signal 79 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/renesas,ostm.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,ostm.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,rz-mtu3.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,rz-mtu3.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,rz-mtu3.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Renesas RZ/G2L Multi-Function Timer Pulse Unit 3 (MTU3a)` and documents: This hardware block consists of eight 16-bit timer channels and one 32-bit timer channel. It supports the following specifications: - Pulse input/output: 28 lines max - Pulse input 3 lines - Count clock 11 clocks for each channel (14 clocks for MTU0, 12 clocks for MTU2, and 10 clocks for MTU5, four clocks for MTU1-MTU2 combination (when LWA = 1)) - Operating frequency Up to 100 MHz - Available operations [MTU0 to MTU4, MTU6, MTU7, and MTU8] - Waveform output on compare match - Input capture function (noise filter setting available) - Counter-clearing operation - Simultaneous writing to mult....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#pwm-cells`, `clocks`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `reg`, `resets`. Required keys across the schema are `clocks`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `reg`, `resets`. Compatible values exposed by the schema are `renesas,r9a07g043-mtu3`, `renesas,r9a07g044-mtu3`, `renesas,r9a07g054-mtu3`, `renesas,rz-mtu3`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `resets`, `power-domains`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `resets`, `power-domains`. The file has 1 example block(s) and source signal 306 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/renesas,rz-mtu3.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,rz-mtu3.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,tmu.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,tmu.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,tmu.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Renesas R-Mobile/R-Car Timer Unit (TMU)` and documents: The TMU is a 32-bit timer/counter with configurable clock inputs and programmable compare match. Channels share hardware resources but their counter and compare match value are independent. The TMU hardware supports up to three channels..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#renesas,channels`, `clock-names`, `clocks`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `reg`, `resets`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupt-names`, `interrupts`, `power-domains`, `reg`, `resets`. Compatible values exposed by the schema are `renesas,tmu-r8a73a4`, `renesas,tmu-r8a7740`, `renesas,tmu-r8a7742`, `renesas,tmu-r8a7743`, `renesas,tmu-r8a7744`, `renesas,tmu-r8a7745`, `renesas,tmu-r8a77470`, `renesas,tmu-r8a774a1`, `renesas,tmu-r8a774b1`, `renesas,tmu-r8a774c0`, `renesas,tmu-r8a774e1`, `renesas,tmu-r8a7778`, `renesas,tmu-r8a7779`, `renesas,tmu-r8a7790`, `renesas,tmu-r8a7791`, `renesas,tmu-r8a7792`, `renesas,tmu-r8a7793`, `renesas,tmu-r8a7794`, `renesas,tmu-r8a7795`, `renesas,tmu-r8a7796`, `renesas,tmu-r8a77961`, `renesas,tmu-r8a77965`, `renesas,tmu-r8a77970`, `renesas,tmu-r8a77980`, and 7 more.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `power-domains`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32`, and then applies conditional branches `if`=1, `then`=1, `not`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `power-domains`. The file has 1 example block(s) and source signal 136 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/renesas,tmu.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/renesas,tmu.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/riscv,timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/riscv,timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/riscv,timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `RISC-V timer` and documents: RISC-V platforms always have a RISC-V timer device for the supervisor-mode based on the time CSR defined by the RISC-V privileged specification. The timer interrupts of this device are configured using the RISC-V SBI Time extension or the RISC-V Sstc extension. The clock frequency of RISC-V timer device is specified via the "timebase-frequency" DT property of "/cpus" DT node which is described in Documentation/devicetree/bindings/riscv/cpus.yaml.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts-extended`, `riscv,timer-cannot-wake-cpu`. Required keys across the schema are `compatible`, `interrupts-extended`. Compatible values exposed by the schema are `riscv,timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`. The file has 1 example block(s) and source signal 52 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=4096`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/riscv,timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/riscv,timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/rockchip,rk-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/rockchip,rk-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/rockchip,rk-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Rockchip Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `rockchip,rk3288-timer`, `rockchip,rk3399-timer`, `rockchip,rv1108-timer`, `rockchip,rv1126-timer`, `rockchip,rk3036-timer`, `rockchip,rk3128-timer`, `rockchip,rk3188-timer`, `rockchip,rk3228-timer`, `rockchip,rk3229-timer`, `rockchip,rk3368-timer`, `rockchip,rk3576-timer`, `rockchip,rk3588-timer`, `rockchip,px30-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 66 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=2`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/rockchip,rk-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/rockchip,rk-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/samsung,exynos4210-mct.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/samsung,exynos4210-mct.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/samsung,exynos4210-mct.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Samsung Exynos SoC Multi Core Timer (MCT)` and documents: The Samsung's Multi Core Timer (MCT) module includes two main blocks, the global timer and CPU local timers. The global timer is a 64-bit free running up-counter and can generate 4 interrupts when the counter reaches one of the four preset counter values. The CPU local timers are 32-bit free running down-counters and generate an interrupt when the counter expires. There is one CPU local timer instantiated in MCT for every CPU in the system..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `samsung,frc-shared`, `samsung,local-timers`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `samsung,exynos4210-mct`, `samsung,exynos4412-mct`, `axis,artpec8-mct`, `axis,artpec9-mct`, `google,gs101-mct`, `samsung,exynos2200-mct-peris`, `samsung,exynos3250-mct`, `samsung,exynos5250-mct`, `samsung,exynos5260-mct`, `samsung,exynos5420-mct`, `samsung,exynos5433-mct`, `samsung,exynos850-mct`, `samsung,exynos8895-mct`, `samsung,exynos990-mct`, `tesla,fsd-mct`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32-array`, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=5, `then`=5, `not`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32-array`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 4 example block(s) and source signal 247 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=2`, `maxItems=1`, `minItems=1`, `maxItems=16`, `minItems=5`, `maxItems=20`, `minItems=8`, `maxItems=8`, `minItems=6`, `maxItems=6`, `minItems=12`, `maxItems=12`, `minItems=16`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/samsung,exynos4210-mct.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/samsung,exynos4210-mct.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/sifive,clint.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/sifive,clint.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/sifive,clint.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `SiFive Core Local Interruptor` and documents: SiFive (and other RISC-V) SOCs include an implementation of the SiFive Core Local Interruptor (CLINT) for M-mode timer and M-mode inter-processor interrupts. It directly connects to the timer and inter-processor interrupt lines of various HARTs (or CPUs) so RISC-V per-HART (or per-CPU) local interrupt controller is the parent interrupt controller for CLINT device. The clock frequency of CLINT is specified via "timebase-frequency" DT property of "/cpus" DT node. The "timebase-frequency" DT property is described in Documentation/devicetree/bindings/riscv/cpus.yaml T-Head C906/C910 CPU cores i....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts-extended`, `reg`, `sifive,fine-ctr-bits`. Required keys across the schema are `compatible`, `interrupts-extended`, `reg`, `sifive,fine-ctr-bits`. Compatible values exposed by the schema are `canaan,k210-clint`, `eswin,eic7700-clint`, `microchip,pic64gx-clint`, `sifive,fu540-c000-clint`, `spacemit,k1-clint`, `spacemit,k3-clint`, `starfive,jh7100-clint`, `starfive,jh7110-clint`, `starfive,jh8100-clint`, `tenstorrent,blackhole-clint`, `sifive,clint0`, `sifive,clint2`, `allwinner,sun20i-d1-clint`, `sophgo,cv1800b-clint`, `sophgo,cv1812h-clint`, `sophgo,sg2002-clint`, `thead,th1520-clint`, `thead,c900-clint`, `riscv,clint0`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1, `if`=1, `then`=1, `else`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 1 example block(s) and source signal 108 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`, `maxItems=4095`, `maximum=15`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/sifive,clint.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/sifive,clint.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,arc-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,arc-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,arc-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Synopsys ARC Local Timer` and documents: Synopsys ARC Local Timer with Interrupt Capabilities - Found on all ARC CPUs (ARC700/ARCHS) - Can be optionally programmed to interrupt on Limit - Two identical copies TIMER0 and TIMER1 exist in ARC cores and historically TIMER0 used as clockevent provider (true for all ARC cores) TIMER1 used for clocksource (mandatory for ARC700, optional for ARC HS).

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`. Required keys across the schema are `clocks`, `compatible`. Compatible values exposed by the schema are `snps,arc-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 45 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/snps,arc-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,arc-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,archs-gfrc.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,archs-gfrc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,archs-gfrc.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Synopsys ARC Free Running 64-bit Global Timer for ARC HS CPUs`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`. Required keys across the schema are `clocks`, `compatible`. Compatible values exposed by the schema are `snps,archs-gfrc`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `clocks`. The file has 1 example block(s) and source signal 30 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/snps,archs-gfrc.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,archs-gfrc.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,archs-rtc.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,archs-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,archs-rtc.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Synopsys ARC Free Running 64-bit Local Timer for ARC HS CPUs`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`. Required keys across the schema are `clocks`, `compatible`. Compatible values exposed by the schema are `snps,archs-rtc`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `clocks`. The file has 1 example block(s) and source signal 30 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/snps,archs-rtc.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,archs-rtc.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,dw-apb-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,dw-apb-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,dw-apb-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Synopsys DesignWare APB Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-frequency`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `resets`. Required keys across the schema are `clock-freq`, `clock-frequency`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `snps,dw-apb-timer`, `snps,dw-apb-timer-sp`, `snps,dw-apb-timer-osc`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, follows referenced common schemas none, and then applies conditional branches `oneOf`=2. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. The file has 3 example block(s) and source signal 84 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/snps,dw-apb-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/snps,dw-apb-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/socionext,milbeaut-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/socionext,milbeaut-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/socionext,milbeaut-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Milbeaut SoCs Timer Controller`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `socionext,milbeaut-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 40 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/socionext,milbeaut-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/socionext,milbeaut-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/sprd,sc9860-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/sprd,sc9860-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/sprd,sc9860-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Spreadtrum SC9860 timer` and documents: The Spreadtrum SC9860 platform provides 3 general-purpose timers. These timers can support 32bit or 64bit counter, as well as supporting period mode or one-shot mode, and they can be a wakeup source during deep sleep..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `sprd,sc9860-timer`, `sprd,sc9860-suspend-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, follows referenced common schemas none, and then applies conditional branches `allOf`=1, `if`=1, `then`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`. The file has 1 example block(s) and source signal 68 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/sprd,sc9860-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/sprd,sc9860-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,nomadik-mtu.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,nomadik-mtu.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,nomadik-mtu.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ST Microelectronics Nomadik Multi-Timer Unit MTU Timer` and documents: This timer is found in the ST Microelectronics Nomadik SoCs STn8800, STn8810 and STn8815 as well as in ST-Ericsson DB8500..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `st,nomadik-mtu`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 58 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `maxItems=2`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/st,nomadik-mtu.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,nomadik-mtu.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,spear-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,spear-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,spear-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `SPEAr ARM Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `st,spear-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 36 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/st,spear-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,spear-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,stm32-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,stm32-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,stm32-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `STMicroelectronics STM32 general-purpose 16 and 32 bits timers`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupts`, `reg`, `resets`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `st,stm32-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `resets`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `resets`. The file has 1 example block(s) and source signal 48 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/st,stm32-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/st,stm32-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ACLINT Machine-level Timer Device`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts-extended`, `reg`, `reg-names`. Required keys across the schema are `compatible`, `interrupts-extended`, `reg`, `reg-names`. Compatible values exposed by the schema are `sophgo,sg2042-aclint-mtimer`, `sophgo,sg2044-aclint-mtimer`, `thead,c900-aclint-mtimer`, `anlogic,dr1v90-aclint-mtimer`, `nuclei,ux900-aclint-mtimer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 1 example block(s) and source signal 56 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=4095`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,da830-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,da830-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,da830-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `TI DaVinci Timer` and documents: This is a 64-bit timer found on TI's DaVinci architecture devices. The timer can be configured as a general-purpose 64-bit timer, dual general-purpose 32-bit timers. When configured as dual 32-bit timers, each half can operate in conjunction (chain mode) or independently (unchained mode) of each other. The timer is a free running up-counter and can generate interrupts when the counter reaches preset counter values..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clocks`, `compatible`, `interrupt-names`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupt-names`, `interrupts`, `reg`. Compatible values exposed by the schema are `ti,da830-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`. The file has 1 example block(s) and source signal 68 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=2`, `maxItems=10`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/ti,da830-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,da830-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,keystone-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,keystone-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,keystone-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `TI Keystone timer` and documents: A 64-bit timer in the KeyStone architecture devices. The timer can be configured as a general-purpose 64-bit timer, dual general-purpose 32-bit timers. When configured as dual 32-bit timers, each half can operate in conjunction (chain mode) or independently (unchained mode) of each other. It is global timer is a free running up-counter and can generate interrupt when the counter reaches preset counter values. Documentation: https://www.ti.com/lit/ug/sprugv5a/sprugv5a.pdf.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupt-names`, `interrupts`, `reg`. Required keys across the schema are `clocks`, `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `ti,keystone-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 63 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/ti,keystone-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,keystone-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,timer-dm.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,timer-dm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,timer-dm.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `TI dual-mode timer` and documents: The TI dual-mode timer is a general purpose timer with PWM capabilities..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-names`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `ti,hwmods`, `ti,timer-alwon`, `ti,timer-dsp`, `ti,timer-pwm`, `ti,timer-secure`. Required keys across the schema are `compatible`, `interrupts`, `power-domains`, `reg`. Compatible values exposed by the schema are `ti,am335x-timer`, `ti,am335x-timer-1ms`, `ti,am654-timer`, `ti,dm814-timer`, `ti,dm816-timer`, `ti,omap2420-timer`, `ti,omap3430-timer`, `ti,omap4430-timer`, `ti,omap5430-timer`, `ti,am4372-timer`, `ti,am4372-timer-1ms`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, follows referenced common schemas `/schemas/types.yaml#/definitions/string`, and then applies conditional branches `allOf`=1, `oneOf`=1, `if`=3, `then`=3, `else`=2, `not`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/string`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. The file has 1 example block(s) and source signal 159 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/ti,timer-dm.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/ti,timer-dm.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/via,vt8500-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/via,vt8500-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/via,vt8500-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `VIA/Wondermedia VT8500 Timer` and documents: This is the timer block that is a standalone part of the system power management controller on VIA/WonderMedia SoCs (VIA VT8500 and alike). The hardware has a single 32-bit counter running at 3 MHz and four match registers, each of which is associated with a dedicated match interrupt, and the first of which can also serve as the system watchdog (if the watchdog function is enabled, it will reset the system upon match instead of triggering its respective interrupt).

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `via,vt8500-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 51 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/via,vt8500-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/via,vt8500-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/xlnx,xps-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/xlnx,xps-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/xlnx,xps-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `Xilinx LogiCORE IP AXI Timer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#pwm-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `xlnx,count-width`, `xlnx,one-timer-only`. Required keys across the schema are `#pwm-cells`, `clock-names`, `clocks`, `compatible`, `interrupts`, `reg`, `xlnx,one-timer-only`. Compatible values exposed by the schema are `xlnx,xps-timer-1.00.a`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32`, and then applies conditional branches `allOf`=2, `if`=2, `then`=2, `else`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The file has 1 example block(s) and source signal 92 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/xlnx,xps-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/xlnx,xps-timer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/hardware-timestamps-common.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/hardware-timestamps-common.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/hardware-timestamps-common.yaml` is a Linux Devicetree YAML schema for hardware timestamp engine provider or consumer binding. It preserves the binding title `Hardware timestamp providers` and documents: Some devices/SoCs have hardware timestamp engines (HTE) which can use hardware means to timestamp entity in realtime. The entity could be anything from GPIOs, IRQs, Bus and so on. The hardware timestamp engine present itself as a provider with the bindings described in this document..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#timestamp-cells`, `$nodename`. Required keys across the schema are `#timestamp-cells`. Compatible values exposed by the schema are none.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `#timestamp-cells`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `#timestamp-cells`. The file has 0 example block(s) and source signal 29 lines with top-level schema blocks `properties`, `required`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=True, limits `additionalProperties=True`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timestamp/hardware-timestamps-common.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/hardware-timestamps-common.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/hte-consumer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/hte-consumer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/hte-consumer.yaml` is a Linux Devicetree YAML schema for hardware timestamp engine provider or consumer binding. It preserves the binding title `HTE Consumer`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `timestamp-names`, `timestamps`. Required keys across the schema are none. Compatible values exposed by the schema are none.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as none, follows referenced common schemas `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string-array`, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string-array`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are none. The file has 1 example block(s) and source signal 39 lines with top-level schema blocks `properties`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=True, limits `additionalProperties=True`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timestamp/hte-consumer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/hte-consumer.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/nvidia,tegra194-hte.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/nvidia,tegra194-hte.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/nvidia,tegra194-hte.yaml` is a Linux Devicetree YAML schema for hardware timestamp engine provider or consumer binding. It preserves the binding title `Tegra on chip generic hardware timestamping engine (HTE) provider` and documents: Tegra SoC has two instances of generic hardware timestamping engines (GTE) known as GTE GPIO and GTE IRQ, which can monitor subset of GPIO and on chip IRQ lines for the state change respectively, upon detection it will record timestamp (taken from system counter) in its internal hardware FIFO. It has a bitmap array arranged in 32bit slices where each bit represent signal/line to enable or disable for the hardware timestamping. The GTE GPIO monitors GPIO lines from the AON (always on) GPIO controller..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#timestamp-cells`, `compatible`, `interrupts`, `nvidia,gpio-controller`, `nvidia,int-threshold`, `nvidia,slices`, `reg`. Required keys across the schema are `#timestamp-cells`, `compatible`, `interrupts`, `nvidia,gpio-controller`, `reg`. Compatible values exposed by the schema are `nvidia,tegra194-gte-aon`, `nvidia,tegra194-gte-lic`, `nvidia,tegra234-gte-aon`, `nvidia,tegra234-gte-lic`, `nvidia,tegra264-gte-aon`, `nvidia,tegra264-gte-lic`. Provider cell contracts are `#timestamp-cells const `1``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, `#timestamp-cells`, follows referenced common schemas `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, and then applies conditional branches `allOf`=1, `if`=5, `then`=5. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`, `#timestamp-cells`. The file has 2 example block(s) and source signal 154 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`, `minimum=1`, `maximum=256`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timestamp/nvidia,tegra194-hte.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timestamp/nvidia,tegra194-hte.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/google,cr50.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/google,cr50.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/google,cr50.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `Google Security Chip H1 (running Cr50 firmware)` and documents: Google has designed a family of security chips called "Titan". One member is the H1 built into Chromebooks and running Cr50 firmware: https://www.osfc.io/2018/talks/google-secure-microcontroller-and-ccd-closed-case-debugging/ The chip provides several functions, including TPM 2.0 like functionality. It communicates over SPI or I²C using the FIFO protocol described in the TCG PC Client Platform TPM Profile Specification for TPM 2.0 (PTP), sec 6: https://trustedcomputinggroup.org/resource/pc-client-platform-tpm-profile-ptp-specification/.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`. Required keys across the schema are `compatible`, `reg`. Compatible values exposed by the schema are `google,cr50`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, follows referenced common schemas `/schemas/spi/spi-peripheral-props.yaml#`, `tcg,tpm-tis-i2c.yaml#/properties/reg`, `tpm-common.yaml#`, and then applies conditional branches `allOf`=1, `anyOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/spi/spi-peripheral-props.yaml#`, `tcg,tpm-tis-i2c.yaml#/properties/reg`, `tpm-common.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`. The file has 2 example block(s) and source signal 65 lines with top-level schema blocks `properties`, `required`, `allOf`, `anyOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/google,cr50.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/google,cr50.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/ibm,vtpm.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/ibm,vtpm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/ibm,vtpm.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `IBM Virtual Trusted Platform Module (vTPM)` and documents: Virtual TPM is used on IBM POWER7+ and POWER8 systems running POWERVM. It is supported through the adjunct partition with firmware release 740 or higher. With vTPM support, each lpar is able to have its own vTPM without the physical TPM hardware. The TPM functionality is provided by communicating with the vTPM adjunct partition through Hypervisor calls (Hcalls) and Command/Response Queue (CRQ) commands..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `device_type`, `ibm,#dma-address-cells`, `ibm,#dma-size-cells`, `ibm,loc-code`, `ibm,my-dma-window`, `ibm,my-drc-index`, `reg`. Required keys across the schema are `compatible`, `device_type`, `ibm,#dma-address-cells`, `ibm,#dma-size-cells`, `ibm,loc-code`, `ibm,my-dma-window`, `ibm,my-drc-index`, `interrupts`, `linux,sml-base`, `linux,sml-size`, `reg`. Compatible values exposed by the schema are `IBM,vtpm`, `IBM,vtpm20`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `tpm-common.yaml#`, and then applies conditional branches `allOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `tpm-common.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 1 example block(s) and source signal 104 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maxItems=1`, `minItems=5`, `maxItems=5`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/ibm,vtpm.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/ibm,vtpm.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `Microsoft firmware-based Trusted Platform Module (fTPM)` and documents: Commodity CPU architectures, such as ARM and Intel CPUs, have started to offer trusted computing features in their CPUs aimed at displacing dedicated trusted hardware. Unfortunately, these CPU architectures raise serious challenges to building trusted systems because they omit providing secure resources outside the CPU perimeter. Microsoft's firmware-based TPM 2.0 (fTPM) leverages ARM TrustZone to overcome these challenges and provide software with security guarantees similar to those of dedicated trusted hardware. https://www.microsoft.com/en-us/research/publication/ftpm-software-implement....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`. Required keys across the schema are `compatible`, `linux,sml-base`, `linux,sml-size`. Compatible values exposed by the schema are `microsoft,ftpm`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, follows referenced common schemas `tpm-common.yaml#`, and then applies conditional branches `allOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `tpm-common.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`. The file has 1 example block(s) and source signal 47 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm-tis-i2c.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm-tis-i2c.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm-tis-i2c.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `I²C-attached Trusted Platform Module conforming to TCG TIS specification` and documents: The Trusted Computing Group (TCG) has defined a multi-vendor standard for accessing a TPM chip. It can be transported over various buses, one of them being I²C. The standard is named: TCG PC Client Specific TPM Interface Specification (TIS) https://trustedcomputinggroup.org/resource/pc-client-work-group-pc-client-specific-tpm-interface-specification-tis/ The I²C interface was not originally part of the standard, but added in 2017 with a separate document: TCG PC Client Platform TPM Profile Specification for TPM 2.0 (PTP) https://trustedcomputinggroup.org/resource/pc-client-platform-tpm-prof....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `reg`. Required keys across the schema are `compatible`, `reg`. Compatible values exposed by the schema are `infineon,slb9673`, `nuvoton,npct75x`, `st,st33ktpm2xi2c`, `st,st33tphf2ei2c`, `tcg,tpm-tis-i2c`, `atmel,at97sc3204t`, `infineon,slb9635tt`, `infineon,slb9645tt`, `infineon,tpm_i2c_infineon`, `nuvoton,npct501`, `nuvoton,npct601`, `st,st33zp24-i2c`, `winbond,wpct301`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas `tpm-common.yaml#`, and then applies conditional branches `allOf`=1, `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `tpm-common.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 2 example block(s) and source signal 92 lines with top-level schema blocks `properties`, `required`, `allOf`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/tcg,tpm-tis-i2c.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm-tis-i2c.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm-tis-mmio.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm-tis-mmio.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm-tis-mmio.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `MMIO-accessed Trusted Platform Module conforming to TCG TIS specification` and documents: The Trusted Computing Group (TCG) has defined a multi-vendor standard for accessing a TPM chip. It can be transported over various buses, one of them being LPC (via MMIO). The standard is named: TCG PC Client Specific TPM Interface Specification (TIS) https://trustedcomputinggroup.org/resource/pc-client-work-group-pc-client-specific-tpm-interface-specification-tis/.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `reg`. Required keys across the schema are `compatible`, `reg`. Compatible values exposed by the schema are `at97sc3201`, `atmel,at97sc3204`, `socionext,synquacer-tpm-mmio`, `tcg,tpm-tis-mmio`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas `tpm-common.yaml#`, and then applies conditional branches `allOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `tpm-common.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 1 example block(s) and source signal 49 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/tcg,tpm-tis-mmio.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm-tis-mmio.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `SPI-attached Trusted Platform Module conforming to TCG TIS specification` and documents: The Trusted Computing Group (TCG) has defined a multi-vendor standard for accessing a TPM chip. It can be transported over various buses, one of them being SPI. The standard is named: TCG PC Client Specific TPM Interface Specification (TIS) https://trustedcomputinggroup.org/resource/pc-client-work-group-pc-client-specific-tpm-interface-specification-tis/.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`. Required keys across the schema are `compatible`, `reg`. Compatible values exposed by the schema are `atmel,attpm20p`, `infineon,slb9670`, `st,st33htpm-spi`, `st,st33zp24-spi`, `tcg,tpm_tis-spi`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, follows referenced common schemas `/schemas/spi/spi-peripheral-props.yaml#`, `tpm-common.yaml#`, and then applies conditional branches `allOf`=1, `if`=1, `then`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/spi/spi-peripheral-props.yaml#`, `tpm-common.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`. The file has 2 example block(s) and source signal 76 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maximum=10000000`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tpm-common.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tpm-common.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tpm-common.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `Trusted Platform Module common properties`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `$nodename`, `interrupts`, `label`, `linux,sml-base`, `linux,sml-size`, `memory-region`, `powered-while-suspended`, `reset-gpios`, `resets`. Required keys across the schema are none. Compatible values exposed by the schema are none.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `interrupts`, `resets`, `label`, follows referenced common schemas `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint64`, and then applies conditional branches `allOf`=1, `if`=1, `then`=1, `dependentRequired`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint64`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `interrupts`, `resets`, `label`. The file has 0 example block(s) and source signal 87 lines with top-level schema blocks `properties`, `allOf`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=True, limits `additionalProperties=True`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/tpm-common.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tpm-common.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/adi,util-sigma-delta-spi.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/adi,util-sigma-delta-spi.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/adi,util-sigma-delta-spi.yaml` is a Linux Devicetree YAML schema for IIO trigger source provider binding. It preserves the binding title `Analog Devices Util Sigma-Delta SPI IP Core` and documents: The Util Sigma-Delta SPI is an FPGA IP core from Analog Devices that provides a SPI offload trigger from the RDY signal of the combined DOUT/RDY pin of the sigma-delta family of ADCs. https://analogdevicesinc.github.io/hdl/library/util_sigma_delta_spi/index.html.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#trigger-source-cells`, `clocks`, `compatible`, `reg`. Required keys across the schema are `#trigger-source-cells`, `clocks`, `compatible`, `reg`. Compatible values exposed by the schema are `adi,util-sigma-delta-spi`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `clocks`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `clocks`. The file has 1 example block(s) and source signal 49 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/trigger-source/adi,util-sigma-delta-spi.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/adi,util-sigma-delta-spi.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/gpio-trigger.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/gpio-trigger.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/gpio-trigger.yaml` is a Linux Devicetree YAML schema for IIO trigger source provider binding. It preserves the binding title `Generic trigger source using GPIO` and documents: A GPIO used as a trigger source..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#trigger-source-cells`, `compatible`, `gpios`. Required keys across the schema are `#trigger-source-cells`, `compatible`, `gpios`. Compatible values exposed by the schema are `gpio-trigger`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`. The file has 1 example block(s) and source signal 40 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/trigger-source/gpio-trigger.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/gpio-trigger.yaml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/pwm-trigger.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/pwm-trigger.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/pwm-trigger.yaml` is a Linux Devicetree YAML schema for IIO trigger source provider binding. It preserves the binding title `Generic trigger source using PWM` and documents: Remaps a PWM channel as a trigger source..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#trigger-source-cells`, `compatible`, `pwms`. Required keys across the schema are `#trigger-source-cells`, `compatible`, `pwms`. Compatible values exposed by the schema are `pwm-trigger`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`. The file has 1 example block(s) and source signal 37 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/trigger-source/pwm-trigger.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/trigger-source/pwm-trigger.yaml -->
