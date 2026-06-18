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
