# subset-b-000619 Research

Grouped research report for 78 devicetree binding source files. Each section is delimited for reconciliation into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,dwc3.yaml`, a YAML devicetree binding titled "Legacy Qualcomm SuperSpeed DWC3 USB SoC controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code. This binding is marked `deprecated: true`, so new DTS should migrate to the replacement documented in comments or companion schemas.

## Purpose
The schema documents and validates the hardware description for `qcom,dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Wesley Cheng <quic_wcheng@quicinc.com>.

## Important APIs, Types, And Schema Surface
Accepts 46 compatible string(s): `qcom,ipq4019-dwc3`, `qcom,ipq5018-dwc3`, `qcom,ipq5332-dwc3`, `qcom,ipq5424-dwc3`, `qcom,ipq6018-dwc3`, `qcom,ipq8064-dwc3`, `qcom,ipq8074-dwc3`, `qcom,ipq9574-dwc3`, `qcom,msm8953-dwc3`, `qcom,msm8994-dwc3`, plus 36 more.

Required top-level fields: `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1; Offset and length of register set for QSCRATCH wrapper
- `#address-cells`: enum `1`, `2`
- `#size-cells`: enum `1`, `2`
- `ranges`: boolean/standard property admitted by this schema.
- `power-domains`: items ?..1; specifies a phandle to PM domain provider node
- `required-opps`: items ?..1
- `clocks`: items 1..9; Several clocks are used, depending on the variant. Typical ones are:: - cfg_noc:: System Config NOC clock. - core:: Master/Core...
- `clock-names`: items 1..9
- `resets`: items ?..1
- `interconnects`: items ?..2
- `interconnect-names`: declared schema property.
- `interrupts`: items 2..18; Different types of interrupts are used based on HS PHY used on target: - pwr_event: Used for wakeup based on other power events...
- `interrupt-names`: items 2..18
- `qcom,select-utmi-as-pipe-clk`: type `boolean`; If present, disable USB3 pipe_clk requirement. Used when dwc3 operates without SSPHY and only HS/FS/LS modes are supported.
- `wakeup-source`: boolean/standard property admitted by this schema.

Pattern properties / child-node contracts: `^usb@[0-9a-f]+$`.

External schema dependencies: `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3.yaml#`.

The schema contains 17 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

Pattern child nodes are validated with `^usb@[0-9a-f]+$`, so child bus/controller nodes are part of the binding contract.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Deprecated bindings can remain required for existing DTBs, but new boards should not copy them; migration must preserve compatibility with shipped firmware.
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `soc, `usb@a6f8800, `usb@a600000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 16 top-level declared propert(ies), 9 required field(s), 1 external reference(s), and 17 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,pmic-typec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,pmic-typec.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,pmic-typec.yaml`, a YAML devicetree binding titled "Qualcomm PMIC based USB Type-C block". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `qcom,pmic-typec.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Bryan O'Donoghue <bryan.odonoghue@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 5 compatible string(s): `qcom,pmi632-typec`, `qcom,pm8150b-typec`, `qcom,pm6150-typec`, `qcom,pm7250b-typec`, `qcom,pm4125-typec`.

Required top-level fields: `compatible`, `reg`, `interrupts`, `interrupt-names`, `vdd-vbus-supply`.

Primary declared properties:
- `compatible`: declared schema property.
- `connector`: refers to `/schemas/connector/usb-connector.yaml#`; type `object`
- `reg`: items 1..2; Type-C port and pdphy SPMI register base offsets
- `interrupts`: items 8..?
- `interrupt-names`: items 8..?
- `vdd-vbus-supply`: VBUS power supply.
- `vdd-pdphy-supply`: VDD regulator supply to the PDPHY.
- `port`: refers to `/schemas/graph.yaml#/properties/port`; Contains a port which produces data-role switching messages.

External schema dependencies: `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`.

The schema contains 1 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `pmic, `typec@1500, `connector, `ports, `port@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,pmic-typec.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,pmic-typec.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,pmic-typec.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 8 top-level declared propert(ies), 5 required field(s), 2 external reference(s), and 1 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,pmic-typec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,snps-dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,snps-dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,snps-dwc3.yaml`, a YAML devicetree binding titled "Qualcomm SuperSpeed DWC3 USB SoC controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `qcom,snps-dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Wesley Cheng <quic_wcheng@quicinc.com>.

## Important APIs, Types, And Schema Surface
Accepts 51 compatible string(s): `qcom,eliza-dwc3`, `qcom,glymur-dwc3`, `qcom,glymur-dwc3-mp`, `qcom,ipq4019-dwc3`, `qcom,ipq5018-dwc3`, `qcom,ipq5332-dwc3`, `qcom,ipq5424-dwc3`, `qcom,ipq6018-dwc3`, `qcom,ipq8064-dwc3`, `qcom,ipq8074-dwc3`, plus 41 more.

Required top-level fields: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `power-domains`: items ?..1
- `required-opps`: items ?..1
- `clocks`: items 1..9; Several clocks are used, depending on the variant. Typical ones are:: - cfg_noc:: System Config NOC clock. - core:: Master/Core...
- `clock-names`: items 1..9
- `dma-coherent`: boolean/standard property admitted by this schema.
- `iommus`: items ?..1
- `resets`: items ?..1
- `interconnects`: items ?..2
- `interconnect-names`: declared schema property.
- `interrupts`: items 3..19; Different types of interrupts are used based on HS PHY used on target: - dwc_usb3: Core DWC3 interrupt - pwr_event: Used for wa...
- `interrupt-names`: items 3..19
- `qcom,select-utmi-as-pipe-clk`: type `boolean`; If present, disable USB3 pipe_clk requirement. Used when dwc3 operates without SSPHY and only HS/FS/LS modes are supported.
- `wakeup-source`: boolean/standard property admitted by this schema.

External schema dependencies: `snps,dwc3-common.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3-common.yaml#`.

The schema contains 19 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3-common.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `soc, `usb@a600000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,snps-dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,snps-dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,snps-dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 15 top-level declared propert(ies), 6 required field(s), 1 external reference(s), and 19 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,snps-dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,wcd939x-usbss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,wcd939x-usbss.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,wcd939x-usbss.yaml`, a YAML devicetree binding titled "Qualcomm WCD9380/WCD9385 USB SubSystem Altmode/Analog Audio Switch". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `qcom,wcd939x-usbss.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `qcom,wcd9390-usbss`, `qcom,wcd9395-usbss`.

Required top-level fields: `compatible`, `reg`, `ports`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `reset-gpios`: items ?..1
- `vdd-supply`: USBSS VDD power supply
- `mode-switch`: boolean/standard property admitted by this schema.
- `orientation-switch`: boolean/standard property admitted by this schema.
- `ports`: refers to `/schemas/graph.yaml#/properties/ports`

External schema dependencies: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-switch-ports.yaml#`, `usb-switch.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-switch-ports.yaml#`, `usb-switch.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-switch-ports.yaml#`, `usb-switch.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `typec-mux@42, `ports, `port@0, `endpoint, `port@1`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,wcd939x-usbss.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,wcd939x-usbss.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,wcd939x-usbss.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 7 top-level declared propert(ies), 3 required field(s), 4 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/qcom,wcd939x-usbss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-dwc3.yaml`, a YAML devicetree binding titled "Realtek DWC3 USB SoC Controller Glue". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `realtek,rtd-dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Stanley Chang <stanley_chang@realtek.com>.

## Important APIs, Types, And Schema Surface
Accepts 8 compatible string(s): `realtek,rtd1295-dwc3`, `realtek,rtd1315e-dwc3`, `realtek,rtd1319-dwc3`, `realtek,rtd1319d-dwc3`, `realtek,rtd1395-dwc3`, `realtek,rtd1619-dwc3`, `realtek,rtd1619b-dwc3`, `realtek,rtd-dwc3`.

Required top-level fields: `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: declared schema property.
- `#address-cells`: constant `1`
- `#size-cells`: constant `1`
- `ranges`: boolean/standard property admitted by this schema.

Pattern properties / child-node contracts: `^usb@[0-9a-f]+$`.

External schema dependencies: `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3.yaml#`.

Pattern child nodes are validated with `^usb@[0-9a-f]+$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@98050000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 5 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-type-c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-type-c.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-type-c.yaml`, a YAML devicetree binding titled "Realtek DHC RTD SoCs USB Type-C Connector detection". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `realtek,rtd-type-c.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Stanley Chang <stanley_chang@realtek.com>.

## Important APIs, Types, And Schema Surface
Accepts 8 compatible string(s): `realtek,rtd1295-type-c`, `realtek,rtd1312c-type-c`, `realtek,rtd1315e-type-c`, `realtek,rtd1319-type-c`, `realtek,rtd1319d-type-c`, `realtek,rtd1395-type-c`, `realtek,rtd1619-type-c`, `realtek,rtd1619b-type-c`.

Required top-level fields: `compatible`, `reg`, `interrupts`.

Primary declared properties:
- `compatible`: enum `realtek,rtd1295-type-c`, `realtek,rtd1312c-type-c`, `realtek,rtd1315e-type-c`, `realtek,rtd1319-type-c`, `realtek,rtd1319d-type-c`, `realtek,rtd1395-type-c`, `realtek,rtd1619-type-c`, `realtek,rtd1619b-type-c`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `nvmem-cell-names`: declared schema property.
- `nvmem-cells`: items ?..1; The phandle to nvmem cell that contains the trimming data. The type c parameter trimming data specified via efuse. If unspecifi...
- `realtek,rd-ctrl-gpios`: items ?..1; The gpio node to control external Rd on board.
- `connector`: refers to `/schemas/connector/usb-connector.yaml#`; type `object`; Properties for usb c connector.

External schema dependencies: `/schemas/connector/usb-connector.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/connector/usb-connector.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/connector/usb-connector.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `type-c@7220, `connector`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-type-c.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-type-c.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-type-c.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 7 top-level declared propert(ies), 3 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rtd-type-c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rts5411.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rts5411.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rts5411.yaml`, a YAML devicetree binding titled "Realtek RTS5411 USB 3.0 hub controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `realtek,rts5411.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Matthias Kaehlcke <mka@chromium.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `usbbda,5411`, `usbbda,411`.

Required top-level fields: `peer-hub`, `compatible`, `reg`.

Primary declared properties:
- `compatible`: declared schema property.
- `vdd-supply`: phandle to the regulator that provides power to the hub.
- `peer-hub`: boolean/standard property admitted by this schema.
- `ports`: refers to `/schemas/graph.yaml#/properties/ports`

External schema dependencies: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties` admits typed child/object extensions, usually for bus children or hub/device subnodes.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `hub@1, `device@2, `hub@2, `ports, `port@4`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rts5411.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rts5411.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rts5411.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 3 required field(s), 3 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/realtek,rts5411.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzg3e-xhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzg3e-xhci.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzg3e-xhci.yaml`, a YAML devicetree binding titled "Renesas USB 3.2 Gen2 Host controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `renesas,rzg3e-xhci.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Biju Das <biju.das.jz@bp.renesas.com>.

## Important APIs, Types, And Schema Surface
Accepts 3 compatible string(s): `renesas,r9a09g056-xhci`, `renesas,r9a09g057-xhci`, `renesas,r9a09g047-xhci`.

Required top-level fields: `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `power-domains`, `resets`, `phys`, `phy-names`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: declared schema property.
- `interrupt-names`: declared schema property.
- `clocks`: items ?..1
- `phys`: items ?..2
- `phy-names`: declared schema property.
- `power-domains`: items ?..1
- `resets`: items ?..1

External schema dependencies: `usb-xhci.yaml`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `usb-xhci.yaml`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `usb-xhci.yaml`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@15850000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzg3e-xhci.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzg3e-xhci.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzg3e-xhci.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 9 top-level declared propert(ies), 9 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzg3e-xhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzn1-usbf.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzn1-usbf.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzn1-usbf.yaml`, a YAML devicetree binding titled "Renesas RZ/N1 SoCs USBF (USB Function) controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `renesas,rzn1-usbf.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Herve Codina <herve.codina@bootlin.com>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `renesas,r9a06g032-usbf`, `renesas,rzn1-usbf`.

Required top-level fields: `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `interrupts`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `clocks`: declared schema property.
- `clock-names`: declared schema property.
- `power-domains`: items ?..1
- `interrupts`: declared schema property.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@4001e000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzn1-usbf.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzn1-usbf.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzn1-usbf.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 6 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzn1-usbf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzv2m-usb3drd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzv2m-usb3drd.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzv2m-usb3drd.yaml`, a YAML devicetree binding titled "Renesas RZ/V2M USB 3.1 DRD controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `renesas,rzv2m-usb3drd.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Biju Das <biju.das.jz@bp.renesas.com>.

## Important APIs, Types, And Schema Surface
Accepts 3 compatible string(s): `renesas,r9a09g011-usb3drd`, `renesas,r9a09g055-usb3drd`, `renesas,rzv2m-usb3drd`.

Required top-level fields: `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, `resets`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: declared schema property.
- `interrupt-names`: declared schema property.
- `clocks`: declared schema property.
- `clock-names`: declared schema property.
- `power-domains`: items ?..1
- `resets`: items ?..1
- `ranges`: boolean/standard property admitted by this schema.
- `#address-cells`: enum `1`, `2`
- `#size-cells`: enum `1`, `2`

Pattern properties / child-node contracts: `^usb3peri@[0-9a-f]+$`, `^usb@[0-9a-f]+$`.

External schema dependencies: `/schemas/usb/renesas,usb3-peri.yaml`, `renesas,usb-xhci.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/usb/renesas,usb3-peri.yaml`, `renesas,usb-xhci.yaml#`.

Pattern child nodes are validated with `^usb3peri@[0-9a-f]+$`, `^usb@[0-9a-f]+$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/usb/renesas,usb3-peri.yaml`, `renesas,usb-xhci.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@85070400, `usb@85060000, `usb3peri@85070000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzv2m-usb3drd.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzv2m-usb3drd.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzv2m-usb3drd.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 11 top-level declared propert(ies), 8 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,rzv2m-usb3drd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,upd720201-pci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,upd720201-pci.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,upd720201-pci.yaml`, a YAML devicetree binding titled "UPD720201/UPD720202 USB 3.0 xHCI Host Controller (PCIe)". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `renesas,upd720201-pci.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `pci1912,0014`, `pci1912,0015`.

Required top-level fields: `compatible`, `reg`, `avdd33-supply`, `vdd10-supply`, `vdd33-supply`.

Primary declared properties:
- `compatible`: enum `pci1912,0014`, `pci1912,0015`
- `reg`: items ?..1
- `avdd33-supply`: +3.3 V power supply for analog circuit
- `vdd10-supply`: +1.05 V power supply
- `vdd33-supply`: +3.3 V power supply

External schema dependencies: `usb-xhci.yaml`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `usb-xhci.yaml`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `usb-xhci.yaml`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb-controller@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,upd720201-pci.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,upd720201-pci.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,upd720201-pci.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 5 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,upd720201-pci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb-xhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb-xhci.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb-xhci.yaml`, a YAML devicetree binding titled "Renesas USB xHCI controllers". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `renesas,usb-xhci.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com>, Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, And Schema Surface
Accepts 20 compatible string(s): `renesas,xhci-r8a7742`, `renesas,xhci-r8a7743`, `renesas,xhci-r8a7744`, `renesas,xhci-r8a7790`, `renesas,xhci-r8a7791`, `renesas,xhci-r8a7793`, `renesas,rcar-gen2-xhci`, `renesas,xhci-r8a774a1`, `renesas,xhci-r8a774b1`, `renesas,xhci-r8a774c0`, plus 10 more.

Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`, `resets`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: items ?..1
- `clocks`: items 1..?
- `clock-names`: items 1..?
- `phys`: items ?..1
- `phy-names`: declared schema property.
- `power-domains`: items ?..1
- `resets`: items ?..1

External schema dependencies: `usb-xhci.yaml`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `usb-xhci.yaml`.

The schema contains 1 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `usb-xhci.yaml`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@ee000000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb-xhci.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb-xhci.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb-xhci.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 9 top-level declared propert(ies), 6 required field(s), 1 external reference(s), and 1 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb-xhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb3-peri.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb3-peri.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb3-peri.yaml`, a YAML devicetree binding titled "Renesas USB 3.0 Peripheral controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `renesas,usb3-peri.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, And Schema Surface
Accepts 13 compatible string(s): `renesas,r8a774a1-usb3-peri`, `renesas,r8a774b1-usb3-peri`, `renesas,r8a774c0-usb3-peri`, `renesas,r8a774e1-usb3-peri`, `renesas,r8a7795-usb3-peri`, `renesas,r8a7796-usb3-peri`, `renesas,r8a77961-usb3-peri`, `renesas,r8a77965-usb3-peri`, `renesas,r8a77990-usb3-peri`, `renesas,rcar-gen3-usb3-peri`, plus 3 more.

Required top-level fields: `compatible`, `interrupts`, `clocks`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: items ?..1
- `clocks`: items 1..?
- `clock-names`: items 1..?
- `phys`: items ?..1
- `phy-names`: constant `usb`
- `power-domains`: items ?..1
- `resets`: items ?..1
- `usb-role-switch`: refers to `/schemas/types.yaml#/definitions/flag`; Support role switch.
- `companion`: refers to `/schemas/types.yaml#/definitions/phandle`; phandle of a companion.
- `ports`: refers to `/schemas/graph.yaml#/properties/ports`; any connector to the data bus of this controller should be modelled using the OF graph bindings specified, if the "usb-role-swi...

External schema dependencies: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`.

The schema contains 1 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@ee020000, `ports, `port@0, `endpoint, `port@1`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb3-peri.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb3-peri.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb3-peri.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 12 top-level declared propert(ies), 3 required field(s), 4 external reference(s), and 1 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usb3-peri.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usbhs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usbhs.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usbhs.yaml`, a YAML devicetree binding titled "Renesas USBHS (HS-USB) controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `renesas,usbhs.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, And Schema Surface
Accepts 36 compatible string(s): `renesas,usbhs-r7s72100`, `renesas,rza1-usbhs`, `renesas,usbhs-r7s9210`, `renesas,rza2-usbhs`, `renesas,usbhs-r9a07g043`, `renesas,usbhs-r9a07g044`, `renesas,usbhs-r9a07g054`, `renesas,usbhs-r9a08g045`, `renesas,usbhs-r9a09g047`, `renesas,usbhs-r9a09g056`, plus 26 more.

Required top-level fields: `compatible`, `reg`, `clocks`, `interrupts`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `clocks`: items 1..?
- `interrupts`: items 1..4
- `renesas,buswait`: refers to `/schemas/types.yaml#/definitions/uint32`; Integer to use BUSWAIT register.
- `renesas,enable-gpio`: items ?..1; deprecated
- `renesas,enable-gpios`: items ?..1; gpio specifier to check GPIO determining if USB function should be enabled.
- `phys`: items ?..1
- `phy-names`: declared schema property.
- `dmas`: items 2..4
- `dma-names`: items 2..?
- `dr_mode`: boolean/standard property admitted by this schema.
- `power-domains`: items ?..1
- `resets`: items 1..?

External schema dependencies: `/schemas/types.yaml#/definitions/uint32`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint32`.

The schema contains 2 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint32`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@e6590000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usbhs.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usbhs.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usbhs.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 14 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 2 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/renesas,usbhs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1711h.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1711h.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1711h.yaml`, a YAML devicetree binding titled "Richtek RT1711H Type-C Port Switch and Power Delivery controller". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `richtek,rt1711h.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Gene Chen <gene_chen@richtek.com>.

## Important APIs, Types, And Schema Surface
Accepts 4 compatible string(s): `richtek,rt1711h`, `richtek,rt1715`, `hynetek,husb311`, `etekmicro,et7304`.

Required top-level fields: `compatible`, `reg`, `connector`, `interrupts`.

Primary declared properties:
- `compatible`: RT1711H support PD20, ET7304 and RT1715 support PD30 except Fast Role Swap. HUSB311 is a rebrand of RT1711H which is pin and re...
- `reg`: items ?..1
- `interrupts`: items ?..1
- `vbus-supply`: VBUS power supply
- `wakeup-source`: type `boolean`
- `connector`: refers to `/schemas/connector/usb-connector.yaml#`; type `object`; Properties for usb c connector.

External schema dependencies: `/schemas/connector/usb-connector.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/connector/usb-connector.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/connector/usb-connector.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `i2c, `rt1711h@4e, `connector, `ports, `port@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1711h.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1711h.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1711h.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1711h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1719.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1719.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1719.yaml`, a YAML devicetree binding titled "Richtek RT1719 sink-only Type-C PD controller". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `richtek,rt1719.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is ChiYuan Huang <cy_huang@richtek.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `richtek,rt1719`.

Required top-level fields: `compatible`, `reg`, `connector`, `interrupts`.

Primary declared properties:
- `compatible`: enum `richtek,rt1719`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `wakeup-source`: type `boolean`; enable IRQ remote wakeup, see power/wakeup-source.txt
- `connector`: refers to `../connector/usb-connector.yaml#`; type `object`; Properties for usb c connector.

External schema dependencies: `../connector/usb-connector.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `../connector/usb-connector.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `../connector/usb-connector.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `i2c, `rt1719@43, `connector, `ports, `port@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1719.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1719.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1719.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/richtek,rt1719.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,dwc3.yaml`, a YAML devicetree binding titled "Rockchip SuperSpeed DWC3 USB SoC controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `rockchip,dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Heiko Stuebner <heiko@sntech.de>.

## Important APIs, Types, And Schema Surface
Accepts 6 compatible string(s): `rockchip,rk3328-dwc3`, `rockchip,rk3562-dwc3`, `rockchip,rk3568-dwc3`, `rockchip,rk3576-dwc3`, `rockchip,rk3588-dwc3`, `snps,dwc3`.

Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: items ?..1
- `clocks`: items 3..?
- `clock-names`: items 3..?
- `power-domains`: items ?..1
- `resets`: items ?..1
- `reset-names`: constant `usb3-otg`

External schema dependencies: `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3.yaml#`.

The schema contains 4 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `bus, `usb@fe800000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 8 top-level declared propert(ies), 5 required field(s), 1 external reference(s), and 4 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,rk3399-dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,rk3399-dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,rk3399-dwc3.yaml`, a YAML devicetree binding titled "Rockchip RK3399 SuperSpeed DWC3 USB SoC controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `rockchip,rk3399-dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Heiko Stuebner <heiko@sntech.de>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `rockchip,rk3399-dwc3`.

Required top-level fields: `compatible`, `#address-cells`, `#size-cells`, `ranges`, `clocks`, `clock-names`, `resets`, `reset-names`.

Primary declared properties:
- `compatible`: constant `rockchip,rk3399-dwc3`
- `#address-cells`: constant `2`
- `#size-cells`: constant `2`
- `ranges`: boolean/standard property admitted by this schema.
- `clocks`: declared schema property.
- `clock-names`: declared schema property.
- `resets`: items ?..1
- `reset-names`: constant `usb3-otg`

Pattern properties / child-node contracts: `^usb@`.

External schema dependencies: `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3.yaml#`.

Pattern child nodes are validated with `^usb@`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `bus, `usb, `usb@fe800000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,rk3399-dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,rk3399-dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,rk3399-dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 8 top-level declared propert(ies), 8 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/rockchip,rk3399-dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-dwc3.yaml`, a YAML devicetree binding titled "Samsung Exynos SoC USB 3.0 DWC3 Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `samsung,exynos-dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Krzysztof Kozlowski <krzk@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 10 compatible string(s): `google,gs101-dwusb3`, `samsung,exynos2200-dwusb3`, `samsung,exynos5250-dwusb3`, `samsung,exynos5433-dwusb3`, `samsung,exynos7-dwusb3`, `samsung,exynos7870-dwusb3`, `samsung,exynos850-dwusb3`, `samsung,exynosautov920-dwusb3`, `samsung,exynos8890-dwusb3`, `samsung,exynos990-dwusb3`.

Required top-level fields: `compatible`, `#address-cells`, `clocks`, `clock-names`, `ranges`, `#size-cells`, `vdd33-supply`.

Primary declared properties:
- `compatible`: declared schema property.
- `#address-cells`: constant `1`
- `clocks`: items 1..4
- `clock-names`: items 1..4
- `power-domains`: items ?..1
- `ranges`: boolean/standard property admitted by this schema.
- `#size-cells`: constant `1`
- `vdd10-supply`: 1.0V power supply
- `vdd33-supply`: 3.0V/3.3V power supply

Pattern properties / child-node contracts: `^usb@[0-9a-f]+$`.

External schema dependencies: `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3.yaml#`.

The schema contains 8 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

Pattern child nodes are validated with `^usb@[0-9a-f]+$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@12000000, `usb@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 9 top-level declared propert(ies), 7 required field(s), 1 external reference(s), and 8 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-usb2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-usb2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-usb2.yaml`, a YAML devicetree binding titled "Samsung Exynos SoC USB 2.0 EHCI/OHCI Controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `samsung,exynos-usb2.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Krzysztof Kozlowski <krzk@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `samsung,exynos4210-ehci`, `samsung,exynos4210-ohci`.

Required top-level fields: `compatible`, `clocks`, `clock-names`, `interrupts`, `phys`, `phy-names`, `reg`.

Primary declared properties:
- `compatible`: enum `samsung,exynos4210-ehci`, `samsung,exynos4210-ohci`
- `clocks`: items ?..1
- `clock-names`: declared schema property.
- `interrupts`: items ?..1
- `phys`: items 1..3
- `phy-names`: items 1..3
- `reg`: items ?..1
- `samsung,vbus-gpio`: Only for controller in EHCI mode, if present, specifies the GPIO that needs to be pulled up for the bus to be powered.

External schema dependencies: `usb-hcd.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `usb-hcd.yaml#`.

The schema contains 1 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `usb-hcd.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@12110000, `hub@1, `usbether@1, `usb@12120000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-usb2.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-usb2.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-usb2.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 8 top-level declared propert(ies), 7 required field(s), 1 external reference(s), and 1 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/samsung,exynos-usb2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml`, a YAML devicetree binding titled "SMSC USB3503 High-Speed Hub Controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `smsc,usb3503.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Dongjin Kim <tobetter@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 3 compatible string(s): `smsc,usb3503`, `smsc,usb3503a`, `smsc,usb3803`.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: enum `smsc,usb3503`, `smsc,usb3503a`, `smsc,usb3803`
- `reg`: items ?..1
- `connect-gpios`: items ?..1; GPIO for connect
- `intn-gpios`: items ?..1; GPIO for interrupt
- `reset-gpios`: items ?..1; GPIO for reset
- `bypass-gpios`: items ?..1; GPIO for bypass. Control signal to select between HUB MODE and BYPASS MODE.
- `disabled-ports`: refers to `/schemas/types.yaml#/definitions/uint32-array`; items 1..3; Specifies the ports unused using their port number. Do not describe this property if all ports have to be enabled.
- `initial-mode`: refers to `/schemas/types.yaml#/definitions/uint32`; Specifies initial mode. 1 for Hub mode, 2 for standby mode and 3 for bypass mode. In bypass mode the downstream port 3 is conne...
- `clocks`: items ?..1; Clock used for driving REFCLK signal. If not provided the driver assumes that clock signal is always available, its rate is spe...
- `clock-names`: constant `refclk`
- `refclk-frequency`: refers to `/schemas/types.yaml#/definitions/uint32`; Frequency of the REFCLK signal as defined by REF_SEL pins. If not provided, driver will not set rate of the REFCLK signal and a...

External schema dependencies: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

The schema contains 2 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 3 inline example block(s), including node(s) `usb-hub@8, `i2c, `usb-hub@8, `usb-hub`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 11 top-level declared propert(ies), 1 required field(s), 2 external reference(s), and 2 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml`, a YAML devicetree binding titled "Synopsys DesignWare USB3 Controller common properties". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `snps,dwc3-common.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Felipe Balbi <balbi@kernel.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `extcon`: items ?..1; deprecated
- `usb-phy`: items 1..?
- `phys`: items 1..19
- `phy-names`: items 1..19
- `snps,usb2-lpm-disable`: type `boolean`; Indicate if we don't want to enable USB2 HW LPM for host mode.
- `snps,usb3_lpm_capable`: type `boolean`; Determines if platform is USB3 LPM capable
- `snps,usb2-gadget-lpm-disable`: type `boolean`; Indicate if we don't want to enable USB2 HW LPM for gadget mode.
- `snps,reserved-endpoints`: refers to `/schemas/types.yaml#/definitions/uint8-array`; items 1..30; Reserve endpoints for other needs, e.g, for tracing control and output. When set, the driver will avoid using them for the regu...
- `snps,dis-start-transfer-quirk`: type `boolean`; When set, disable isoc START TRANSFER command failure SW work-around for DWC_usb31 version 1.70a-ea06 and prior.
- `snps,disable_scramble_quirk`: type `boolean`; True when SW should disable data scrambling. Only really useful for FPGA builds.
- `snps,has-lpm-erratum`: type `boolean`; True when DWC3 was configured with LPM Erratum enabled
- `snps,lpm-nyet-threshold`: refers to `/schemas/types.yaml#/definitions/uint8`; LPM NYET threshold
- `snps,u2exit_lfps_quirk`: type `boolean`; Set if we want to enable u2exit lfps quirk
- `snps,u2ss_inp3_quirk`: type `boolean`; Set if we enable P3 OK for U2/SS Inactive quirk
- `snps,req_p1p2p3_quirk`: type `boolean`; When set, the core will always request for P1/P2/P3 transition sequence.
- `snps,del_p1p2p3_quirk`: type `boolean`; When set core will delay P1/P2/P3 until a certain amount of 8B10B errors occur.
- `snps,del_phy_power_chg_quirk`: type `boolean`; When set core will delay PHY power change from P0 to P1/P2/P3.
- `snps,lfps_filter_quirk`: type `boolean`; When set core will filter LFPS reception.
- Additional declared properties include `snps,rx_detect_poll_quirk`, `snps,tx_de_emphasis_quirk`, `snps,tx_de_emphasis`, `snps,dis_u3_susphy_quirk`, `snps,dis_u2_susphy_quirk`, `snps,dis_enblslpm_quirk`, `snps,dis-u1-entry-quirk`, `snps,dis-u2-entry-quirk`, `snps,dis_rxdet_inp3_quirk`, `snps,dis-u2-freeclk-exists-quirk`, `snps,dis-del-phy-power-chg-quirk`, `snps,dis-tx-ipgap-linecheck-quirk`, `snps,parkmode-disable-ss-quirk`, `snps,parkmode-disable-hs-quirk`, `snps,dis_metastability_quirk`, `snps,dis-split-quirk`, ...

External schema dependencies: `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8`, `/schemas/types.yaml#/definitions/uint8-array`, `usb-drd.yaml#`, `usb-xhci.yaml#`, `usb.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8`, and 4 more.

The schema contains 1 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8`, `/schemas/types.yaml#/definitions/uint8-array`, `usb-drd.yaml#`, `usb-xhci.yaml#`, `usb.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
No inline DTS example is present; validation depends on in-tree DTS users and dt_binding_check schema compilation.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 58 top-level declared propert(ies), 2 required field(s), 12 external reference(s), and 1 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3.yaml`, a YAML devicetree binding titled "Synopsys DesignWare USB3 Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `snps,dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Felipe Balbi <balbi@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `snps,dwc3`, `synopsys,dwc3`.

Required top-level fields: `compatible`, `reg`, `interrupts`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: items 1..4; It's either a single common DWC3 interrupt (dwc_usb3) or individual interrupts for the host, gadget and DRD modes.
- `interrupt-names`: items 1..4
- `clocks`: In general the core supports three types of clocks. bus_early is a SoC Bus Clock (AHB/AXI/Native). ref generates ITP when the U...
- `clock-names`: declared schema property.
- `dma-coherent`: boolean/standard property admitted by this schema.
- `iommus`: items ?..1
- `power-domains`: items 1..?; The DWC3 has 2 power-domains. The power management unit (PMU) and everything else. The PMU is typically always powered and may ...
- `resets`: items 1..?

External schema dependencies: `snps,dwc3-common.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3-common.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3-common.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 2 inline example block(s), including node(s) `usb@4a000000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 10 top-level declared propert(ies), 3 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/socionext,uniphier-dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/socionext,uniphier-dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/socionext,uniphier-dwc3.yaml`, a YAML devicetree binding titled "Socionext Uniphier SuperSpeed DWC3 USB SoC controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `socionext,uniphier-dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Kunihiko Hayashi <hayashi.kunihiko@socionext.com>, Masami Hiramatsu <mhiramat@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `socionext,uniphier-dwc3`, `snps,dwc3`.

Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `phys`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: items 1..?
- `interrupt-names`: items 1..?
- `clocks`: items ?..3
- `clock-names`: declared schema property.
- `phys`: items 1..6; 1 to 4 HighSpeed PHYs followed by 1 or 2 SuperSpeed PHYs
- `resets`: items ?..1

External schema dependencies: `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3.yaml#`.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@65a00000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/socionext,uniphier-dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/socionext,uniphier-dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/socionext,uniphier-dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 8 top-level declared propert(ies), 6 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/socionext,uniphier-dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/spacemit,k1-dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/spacemit,k1-dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/spacemit,k1-dwc3.yaml`, a YAML devicetree binding titled "SpacemiT K1 SuperSpeed DWC3 USB SoC Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `spacemit,k1-dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Ze Huang <huang.ze@linux.dev>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `spacemit,k1-dwc3`, `spacemit,k3-dwc3`.

Required top-level fields: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `phys`, `phy-names`, `resets`, `reset-names`.

Primary declared properties:
- `compatible`: enum `spacemit,k1-dwc3`, `spacemit,k3-dwc3`
- `reg`: items ?..1
- `clocks`: items ?..1
- `clock-names`: constant `usbdrd30`
- `interrupts`: items ?..1
- `phys`: items 1..?
- `phy-names`: items 1..?
- `resets`: declared schema property.
- `reset-names`: declared schema property.
- `reset-delay`: refers to `/schemas/types.yaml#/definitions/uint32`; default `2`; delay after reset sequence [us]
- `vbus-supply`: A phandle to the regulator supplying the VBUS voltage.

External schema dependencies: `/schemas/types.yaml#/definitions/uint32`, `snps,dwc3-common.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint32`, `snps,dwc3-common.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint32`, `snps,dwc3-common.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `hub@1, `hub@2`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/spacemit,k1-dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/spacemit,k1-dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/spacemit,k1-dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 11 top-level declared propert(ies), 9 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/spacemit,k1-dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,st-ohci-300x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,st-ohci-300x.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,st-ohci-300x.yaml`, a YAML devicetree binding titled "STMicroelectronics USB OHCI Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `st,st-ohci-300x.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Peter Griffin <peter.griffin@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `st,st-ohci-300x`.

Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `phys`, `phy-names`, `resets`, `reset-names`.

Primary declared properties:
- `compatible`: constant `st,st-ohci-300x`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `clocks`: items ?..2
- `clock-names`: declared schema property.
- `phys`: items ?..1
- `phy-names`: declared schema property.
- `resets`: items ?..2
- `reset-names`: declared schema property.

External schema dependencies: `/schemas/usb/usb-hcd.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/usb/usb-hcd.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/usb/usb-hcd.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@fe1ffc00`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,st-ohci-300x.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,st-ohci-300x.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,st-ohci-300x.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 9 top-level declared propert(ies), 9 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,st-ohci-300x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,stusb160x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,stusb160x.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,stusb160x.yaml`, a YAML devicetree binding titled "STMicroelectronics STUSB160x Type-C controller". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `st,stusb160x.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Amelie Delaunay <amelie.delaunay@foss.st.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `st,stusb1600`.

Required top-level fields: `compatible`, `reg`, `connector`.

Primary declared properties:
- `compatible`: enum `st,stusb1600`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `vdd-supply`: main power supply (4.1V-22V)
- `vsys-supply`: low power supply (3.0V-5.5V)
- `vconn-supply`: power supply (2.7V-5.5V) used to supply VConn on CC pin in source or dual power role
- `connector`: refers to `/schemas/connector/usb-connector.yaml#`; type `object`

External schema dependencies: `/schemas/connector/usb-connector.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/connector/usb-connector.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/connector/usb-connector.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `i2c, `stusb1600@28, `connector, `ports, `port@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,stusb160x.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,stusb160x.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,stusb160x.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 7 top-level declared propert(ies), 3 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,stusb160x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,typec-stm32g0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,typec-stm32g0.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,typec-stm32g0.yaml`, a YAML devicetree binding titled "STMicroelectronics STM32G0 USB Type-C PD controller". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `st,typec-stm32g0.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Fabrice Gasnier <fabrice.gasnier@foss.st.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `st,stm32g0-typec`.

Required top-level fields: `compatible`, `reg`, `interrupts`, `connector`.

Primary declared properties:
- `compatible`: constant `st,stm32g0-typec`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `connector`: refers to `/schemas/connector/usb-connector.yaml#`; type `object`
- `firmware-name`: Should contain the name of the default firmware image file located on the firmware search path
- `wakeup-source`: boolean/standard property admitted by this schema.
- `power-domains`: items ?..1

External schema dependencies: `/schemas/connector/usb-connector.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/connector/usb-connector.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/connector/usb-connector.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `i2c, `typec@53, `connector, `ports, `port@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,typec-stm32g0.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,typec-stm32g0.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,typec-stm32g0.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 7 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/st,typec-stm32g0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jh7110-usb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jh7110-usb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jh7110-usb.yaml`, a YAML devicetree binding titled "StarFive JH7110 wrapper module for the Cadence USBSS-DRD controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `starfive,jh7110-usb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Minda Chen <minda.chen@starfivetech.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `starfive,jh7110-usb`.

Required top-level fields: `compatible`, `ranges`, `starfive,stg-syscon`, `#address-cells`, `#size-cells`, `dr_mode`, `clocks`, `resets`.

Primary declared properties:
- `compatible`: constant `starfive,jh7110-usb`
- `ranges`: boolean/standard property admitted by this schema.
- `starfive,stg-syscon`: refers to `/schemas/types.yaml#/definitions/phandle-array`; The phandle to System Register Controller syscon node and the offset of STG_SYSCONSAIF__SYSCFG register for USB.
- `dr_mode`: enum `host`, `otg`, `peripheral`
- `#address-cells`: enum `1`, `2`
- `#size-cells`: enum `1`, `2`
- `clocks`: declared schema property.
- `clock-names`: declared schema property.
- `resets`: declared schema property.
- `reset-names`: declared schema property.

Pattern properties / child-node contracts: `^usb@[0-9a-f]+$`.

External schema dependencies: `/schemas/types.yaml#/definitions/phandle-array`, `cdns,usb3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle-array`, `cdns,usb3.yaml#`.

Pattern child nodes are validated with `^usb@[0-9a-f]+$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle-array`, `cdns,usb3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jh7110-usb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jh7110-usb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jh7110-usb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 10 top-level declared propert(ies), 8 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jh7110-usb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jhb100-dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jhb100-dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jhb100-dwc3.yaml`, a YAML devicetree binding titled "StarFive JHB100 DWC3 USB SoC Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `starfive,jhb100-dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Minda Chen <minda.chen@starfivetech.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `starfive,jhb100-dwc3`.

Required top-level fields: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`.

Primary declared properties:
- `compatible`: constant `starfive,jhb100-dwc3`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `clocks`: declared schema property.
- `clock-names`: declared schema property.
- `resets`: items ?..1

External schema dependencies: `snps,dwc3-common.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3-common.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3-common.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jhb100-dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jhb100-dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jhb100-dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 5 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/starfive,jhb100-dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/terminus,fe11.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/terminus,fe11.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/terminus,fe11.yaml`, a YAML devicetree binding titled "Terminus FE1.1/1.1S USB 2.0 Hub Controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `terminus,fe11.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Yixun Lan <dlan@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `usb1a40,0101`.

Required top-level fields: `compatible`, `reg`, `vdd-supply`.

Primary declared properties:
- `compatible`: enum `usb1a40,0101`
- `reg`: boolean/standard property admitted by this schema.
- `reset-gpios`: GPIO controlling the RESET#.
- `vdd-supply`: Regulator supply to the hub, one of 3.3V or 5V can be chosen.
- `ports`: refers to `/schemas/graph.yaml#/properties/ports`

External schema dependencies: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb, `hub@1`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/terminus,fe11.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/terminus,fe11.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/terminus,fe11.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 3 required field(s), 3 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/terminus,fe11.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,am62-usb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,am62-usb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,am62-usb.yaml`, a YAML devicetree binding titled "TI's AM62 wrapper module for the Synopsys USBSS-DRD controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,am62-usb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Aswath Govindraju <a-govindraju@ti.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `ti,am62-usb`.

Required top-level fields: `compatible`, `reg`, `power-domains`, `clocks`, `clock-names`, `ti,syscon-phy-pll-refclk`.

Primary declared properties:
- `compatible`: constant `ti,am62-usb`
- `reg`: items 1..?
- `ranges`: boolean/standard property admitted by this schema.
- `power-domains`: items ?..1; PM domain provider node and an args specifier containing the USB ISO device id value. See, Documentation/devicetree/bindings/so...
- `clocks`: items ?..1; Clock phandle to usb2_refclk
- `clock-names`: declared schema property.
- `ti,vbus-divider`: type `boolean`; Should be present if USB VBUS line is connected to the VBUS pin of the SoC via a 1/3 voltage divider.
- `ti,syscon-phy-pll-refclk`: refers to `/schemas/types.yaml#/definitions/phandle-array`; Specifier for conveying frequency of ref clock input, for the operation of USB2PHY.
- `#address-cells`: constant `2`
- `#size-cells`: constant `2`

Pattern properties / child-node contracts: `^usb@[0-9a-f]+$`.

External schema dependencies: `/schemas/types.yaml#/definitions/phandle-array`, `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle-array`, `snps,dwc3.yaml#`.

Pattern child nodes are validated with `^usb@[0-9a-f]+$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle-array`, `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `bus, `usb@f910000, `usb@31100000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,am62-usb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,am62-usb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,am62-usb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 10 top-level declared propert(ies), 6 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,am62-usb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,dwc3.yaml`, a YAML devicetree binding titled "Texas Instruments OMAP DWC3 USB Glue Layer". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Felipe Balbi <balbi@ti.com>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `ti,dwc3`, `ti,am437x-dwc3`.

Required top-level fields: `reg`, `compatible`, `interrupts`, `#address-cells`, `#size-cells`, `utmi-mode`, `ranges`.

Primary declared properties:
- `compatible`: enum `ti,dwc3`, `ti,am437x-dwc3`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `utmi-mode`: refers to `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`; Controls the source of UTMI/PIPE status for VBUS and OTG ID. 1 for HW mode, 2 for SW mode.
- `#address-cells`: constant `1`
- `#size-cells`: constant `1`
- `ranges`: boolean/standard property admitted by this schema.
- `extcon`: refers to `/schemas/types.yaml#/definitions/phandle`; Phandle for the extcon device used to detect connect/ disconnect events.
- `vbus-supply`: Phandle to the regulator device tree node if needed.

Pattern properties / child-node contracts: `^usb@[0-9a-f]+$`.

External schema dependencies: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `snps,dwc3.yaml#`.

Pattern child nodes are validated with `^usb@[0-9a-f]+$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `omap_dwc3_1@0, `usb@10000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 9 top-level declared propert(ies), 7 required field(s), 3 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,hd3ss3220.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,hd3ss3220.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,hd3ss3220.yaml`, a YAML devicetree binding titled "TI HD3SS3220 TypeC DRP Port Controller". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,hd3ss3220.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Biju Das <biju.das.jz@bp.renesas.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `ti,hd3ss3220`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: constant `ti,hd3ss3220`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `id-gpios`: items ?..1; An input gpio for USB ID pin. Upon detecting a UFP device, HD3SS3220 will keep ID pin high if VBUS is not at VSafe0V. Once VBUS...
- `ports`: refers to `/schemas/graph.yaml#/properties/ports`; OF graph bindings (specified in bindings/graph.txt) that model SS data bus to the SS capable connector.

External schema dependencies: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `hd3ss3220@47, `ports, `port@0, `endpoint, `port@1`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,hd3ss3220.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,hd3ss3220.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,hd3ss3220.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 2 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,hd3ss3220.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,j721e-usb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,j721e-usb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,j721e-usb.yaml`, a YAML devicetree binding titled "TI wrapper module for the Cadence USBSS-DRD controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,j721e-usb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Roger Quadros <rogerq@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `ti,j721e-usb`, `ti,am64-usb`.

Required top-level fields: `compatible`, `reg`, `power-domains`, `clocks`, `clock-names`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `ranges`: boolean/standard property admitted by this schema.
- `power-domains`: items ?..1; PM domain provider node and an args specifier containing the USB device id value. See, Documentation/devicetree/bindings/soc/ti...
- `clocks`: items 2..2; Clock phandles to usb2_refclk and lpm_clk
- `clock-names`: declared schema property.
- `ti,usb2-only`: type `boolean`; If present, it restricts the controller to USB2.0 mode of operation. Must be present if USB3 PHY is not available for USB.
- `ti,vbus-divider`: type `boolean`; Should be present if USB VBUS line is connected to the VBUS pin of the SoC via a 1/3 voltage divider.
- `#address-cells`: constant `2`
- `#size-cells`: constant `2`
- `dma-coherent`: boolean/standard property admitted by this schema.

Pattern properties / child-node contracts: `^usb@`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Pattern child nodes are validated with `^usb@`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `bus, `cdns_usb@4104000, `usb@6000000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,j721e-usb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,j721e-usb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,j721e-usb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 11 top-level declared propert(ies), 5 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,j721e-usb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,keystone-dwc3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,keystone-dwc3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,keystone-dwc3.yaml`, a YAML devicetree binding titled "TI Keystone Soc USB Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,keystone-dwc3.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Roger Quadros <rogerq@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `ti,keystone-dwc3`, `ti,am654-dwc3`.

Required top-level fields: `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`, `interrupts`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `#address-cells`: constant `1`
- `#size-cells`: constant `1`
- `ranges`: boolean/standard property admitted by this schema.
- `interrupts`: items ?..1
- `clocks`: items 1..2
- `power-domains`: items ?..1; Should contain a phandle to a PM domain provider node and an args specifier containing the USB device id value. This property i...
- `phys`: items ?..1; PHY specifier for the USB3.0 PHY. Some SoCs need the USB3.0 PHY to be turned on before the controller. Documentation/devicetree...
- `phy-names`: declared schema property.
- `dma-coherent`: boolean/standard property admitted by this schema.
- `dma-ranges`: boolean/standard property admitted by this schema.

Pattern properties / child-node contracts: `usb@[a-f0-9]+$`.

External schema dependencies: `snps,dwc3.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `snps,dwc3.yaml#`.

Pattern child nodes are validated with `usb@[a-f0-9]+$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `snps,dwc3.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `dwc3@2680000, `usb@2690000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,keystone-dwc3.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,keystone-dwc3.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,keystone-dwc3.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 12 top-level declared propert(ies), 6 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,keystone-dwc3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,omap4-musb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,omap4-musb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,omap4-musb.yaml`, a YAML devicetree binding titled "Texas Instruments OMAP MUSB USB OTG Controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,omap4-musb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Felipe Balbi <balbi@ti.com>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `ti,omap3-musb`, `ti,omap4-musb`.

Required top-level fields: `reg`, `compatible`, `interrupts`, `interrupt-names`.

Primary declared properties:
- `compatible`: enum `ti,omap3-musb`, `ti,omap4-musb`
- `reg`: items ?..1
- `interrupts`: items 1..2
- `interrupt-names`: items 1..?
- `multipoint`: refers to `/schemas/types.yaml#/definitions/uint32`; constant `1`; Indicates the MUSB controller supports multipoint. This is a MUSB configuration-specific setting.
- `num-eps`: refers to `/schemas/types.yaml#/definitions/uint32`; constant `16`; Specifies the number of endpoints. This is a MUSB configuration specific setting.
- `ram-bits`: constant `12`; Specifies the RAM address size.
- `interface-type`: refers to `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`; Describes the type of interface between the controller and the PHY. 0 for ULPI, 1 for UTMI.
- `mode`: refers to `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`, `3`; 1 for HOST, 2 for PERIPHERAL, 3 for OTG.
- `power`: refers to `/schemas/types.yaml#/definitions/uint32`; enum `50`, `150`; Indicates the maximum current the controller can supply when operating in host mode. A value of 50 corresponds to 100 mA, and a...
- `phys`: items ?..1
- `phy-names`: constant `usb2-phy`
- `usb-phy`: refers to `/schemas/types.yaml#/definitions/phandle-array`; deprecated; Phandle for the PHY device.
- `ctrl-module`: refers to `/schemas/types.yaml#/definitions/phandle`; Phandle of the control module this glue uses to write to mailbox.

External schema dependencies: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@4a0ab000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,omap4-musb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,omap4-musb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,omap4-musb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 14 top-level declared propert(ies), 4 required field(s), 3 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,omap4-musb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tps6598x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tps6598x.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tps6598x.yaml`, a YAML devicetree binding titled "Texas Instruments 6598x Type-C Port Switch and Power Delivery controller". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,tps6598x.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Bryan O'Donoghue <bryan.odonoghue@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 3 compatible string(s): `ti,tps6598x`, `apple,cd321x`, `ti,tps25750`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: enum `ti,tps6598x`, `apple,cd321x`, `ti,tps25750`
- `reg`: items 1..?
- `reg-names`: declared schema property.
- `reset-gpios`: items ?..1; GPIO used for the HRESET pin.
- `wakeup-source`: boolean/standard property admitted by this schema.
- `interrupts`: items ?..1
- `interrupt-names`: declared schema property.
- `connector`: refers to `/schemas/connector/usb-connector.yaml#`
- `firmware-name`: items ?..1; Should contain the name of the default patch binary file located on the firmware search path which is used to switch the contro...

External schema dependencies: `/schemas/connector/usb-connector.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/connector/usb-connector.yaml#`.

The schema contains 1 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/connector/usb-connector.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 2 inline example block(s), including node(s) `i2c, `tps6598x@38, `connector, `port, `endpoint`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tps6598x.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tps6598x.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tps6598x.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 9 top-level declared propert(ies), 2 required field(s), 1 external reference(s), and 1 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tps6598x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb1046.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb1046.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb1046.yaml`, a YAML devicetree binding titled "Texas Instruments TUSB1046-DCI Type-C crosspoint switch". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,tusb1046.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Romain Gantois <romain.gantois@bootlin.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `ti,tusb1046`.

Required top-level fields: `compatible`, `reg`, `port`.

Primary declared properties:
- `compatible`: constant `ti,tusb1046`
- `reg`: items ?..1

External schema dependencies: `usb-switch-ports.yaml#`, `usb-switch.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `usb-switch-ports.yaml#`, `usb-switch.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `usb-switch-ports.yaml#`, `usb-switch.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `typec-mux@44, `port, `endpoint`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb1046.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb1046.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb1046.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 2 top-level declared propert(ies), 3 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb1046.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb73x0-pci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb73x0-pci.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb73x0-pci.yaml`, a YAML devicetree binding titled "TUSB73x0 USB 3.0 xHCI Host Controller (PCIe)". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,tusb73x0-pci.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Francesco Dolcini <francesco.dolcini@toradex.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `pci104c,8241`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: constant `pci104c,8241`
- `reg`: items ?..1
- `ti,pwron-active-high`: refers to `/schemas/types.yaml#/definitions/flag`; Configure the polarity of the PWRONx# signals. When this is present, the PWRONx# pins are active high and their internal pull-d...

External schema dependencies: `/schemas/types.yaml#/definitions/flag`, `usb-xhci.yaml`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/flag`, `usb-xhci.yaml`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/flag`, `usb-xhci.yaml`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb73x0-pci.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb73x0-pci.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb73x0-pci.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 2 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,tusb73x0-pci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl4030-usb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl4030-usb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl4030-usb.yaml`, a YAML devicetree binding titled "Texas Instruments TWL4030 USB PHY and Comparator". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,twl4030-usb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Peter Ujfalusi <peter.ujfalusi@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `ti,twl4030-usb`.

Required top-level fields: `compatible`, `interrupts`, `usb1v5-supply`, `usb1v8-supply`, `usb3v1-supply`, `usb_mode`.

Primary declared properties:
- `compatible`: constant `ti,twl4030-usb`
- `interrupts`: items 1..?
- `usb1v5-supply`: Phandle to the vusb1v5 regulator.
- `usb1v8-supply`: Phandle to the vusb1v8 regulator.
- `usb3v1-supply`: Phandle to the vusb3v1 regulator.
- `usb_mode`: refers to `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`; The mode used by the PHY to connect to the controller: 1: ULPI mode 2: CEA2011_3PIN mode
- `#phy-cells`: constant `0`

External schema dependencies: `/schemas/types.yaml#/definitions/uint32`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint32`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint32`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb-phy`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl4030-usb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl4030-usb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl4030-usb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 7 top-level declared propert(ies), 6 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl4030-usb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl6030-usb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl6030-usb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl6030-usb.yaml`, a YAML devicetree binding titled "Texas Instruments TWL6030 USB Comparator". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,twl6030-usb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Peter Ujfalusi <peter.ujfalusi@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `ti,twl6030-usb`.

Required top-level fields: `compatible`, `interrupts`, `usb-supply`.

Primary declared properties:
- `compatible`: constant `ti,twl6030-usb`
- `interrupts`: declared schema property.
- `usb-supply`: Phandle to the VUSB regulator. For TWL6030, this should be the 'vusb' regulator. For TWL6032 subclass, it should be the 'ldousb...

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl6030-usb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl6030-usb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl6030-usb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 3 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,twl6030-usb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8020b.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8020b.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8020b.yaml`, a YAML devicetree binding titled "TI USB8020B USB 3.0 hub controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,usb8020b.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Macpaul Lin <macpaul.lin@mediatek.com>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `usb451,8025`, `usb451,8027`.

Required top-level fields: `compatible`, `reg`, `peer-hub`.

Primary declared properties:
- `compatible`: enum `usb451,8025`, `usb451,8027`
- `reg`: boolean/standard property admitted by this schema.
- `reset-gpios`: declared schema property.
- `vdd-supply`: VDD power supply to the hub
- `peer-hub`: refers to `/schemas/types.yaml#/definitions/phandle`; phandle to the peer hub on the controller.

External schema dependencies: `/schemas/types.yaml#/definitions/phandle`, `usb-device.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle`, `usb-device.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle`, `usb-device.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb, `hub@1, `hub@2`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8020b.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8020b.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8020b.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 3 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8020b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8041.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8041.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8041.yaml`, a YAML devicetree binding titled "TI USB8041 and USB8044 USB 3.0 hub controllers". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `ti,usb8041.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Alexander Stein <alexander.stein@ew.tq-group.com>.

## Important APIs, Types, And Schema Surface
Accepts 4 compatible string(s): `usb451,8140`, `usb451,8142`, `usb451,8440`, `usb451,8442`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: enum `usb451,8140`, `usb451,8142`, `usb451,8440`, `usb451,8442`
- `reg`: boolean/standard property admitted by this schema.
- `reset-gpios`: declared schema property.
- `vdd-supply`: VDD power supply to the hub
- `peer-hub`: boolean/standard property admitted by this schema.

Pattern properties / child-node contracts: `^.*@[1-9a-f][0-9a-f]*$`.

External schema dependencies: `/schemas/usb/usb-device.yaml`, `usb-device.yaml#`, `usb-hub.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/usb/usb-device.yaml`, `usb-device.yaml#`, `usb-hub.yaml#`.

Pattern child nodes are validated with `^.*@[1-9a-f][0-9a-f]*$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/usb/usb-device.yaml`, `usb-device.yaml#`, `usb-hub.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb, `hub@1, `hub@1, `hub@2`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8041.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8041.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8041.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 2 required field(s), 3 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/ti,usb8041.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml`, a YAML devicetree binding titled "Generic USB Device". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-device.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: `reg`.

Primary declared properties:
- `compatible`: Device nodes or combined nodes. "usbVID,PID", where VID is the vendor id and PID the product id. The textual representation of ...
- `reg`: the number of the USB hub port or the USB host-controller port to which this device is attached.
- `#address-cells`: enum `1`, `2`; should be 1 for hub nodes with device nodes, should be 2 for device nodes with interface nodes.
- `#size-cells`: constant `0`

Pattern properties / child-node contracts: `^interface@[0-9a-f]{1,2}(,[0-9a-f]{1,2})$`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Pattern child nodes are validated with `^interface@[0-9a-f]{1,2}(,[0-9a-f]{1,2})$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `hub@1, `device@2, `device@3, `interface@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 1 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml`, a YAML devicetree binding titled "Generic USB OTG Controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-drd.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `otg-rev`: refers to `/schemas/types.yaml#/definitions/uint32`; enum `256`, `288`, `304`, `512`; Tells usb driver the release number of the OTG and EH supplement with which the device and its descriptors are compliant, in bi...
- `dr_mode`: refers to `/schemas/types.yaml#/definitions/string`; enum `host`, `peripheral`, `otg`; default `otg`; Tells Dual-Role USB controllers that we want to work on a particular mode. In case this attribute isn't passed via DT, USB DRD ...
- `hnp-disable`: type `boolean`; Tells OTG controllers we want to disable OTG HNP. Normally HNP is the basic function of real OTG except you want it to be a srp...
- `srp-disable`: type `boolean`; Tells OTG controllers we want to disable OTG SRP. SRP is optional for OTG device.
- `adp-disable`: type `boolean`; Tells OTG controllers we want to disable OTG ADP. ADP is optional for OTG device.
- `usb-role-switch`: Indicates that the device is capable of assigning the USB data role (USB host or USB device) for a given USB connector, such as...
- `role-switch-default-mode`: refers to `/schemas/types.yaml#/definitions/string`; enum `host`, `peripheral`; default `peripheral`; Indicates if usb-role-switch is enabled, the device default operation mode of controller while usb role is USB_ROLE_NONE.

External schema dependencies: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 7 top-level declared propert(ies), 0 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml`, a YAML devicetree binding titled "Generic USB Host Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-hcd.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `companion`: refers to `/schemas/types.yaml#/definitions/phandle`; Phandle of a companion device
- `tpl-support`: type `boolean`; Indicates if the Targeted Peripheral List is supported for given targeted hosts (non-PC hosts).
- `#address-cells`: constant `1`
- `#size-cells`: constant `0`

Pattern properties / child-node contracts: `^.*@[0-9a-f]{1,2}$`.

External schema dependencies: `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb.yaml#`.

Pattern child nodes are validated with `^.*@[0-9a-f]{1,2}$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.

## Test Signals
Contains 1 inline example block(s), including node(s) `hub@1`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 0 required field(s), 3 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hub.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hub.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hub.yaml`, a YAML devicetree binding titled "Generic USB Hub". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-hub.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Pin-yen Lin <treapking@chromium.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `#address-cells`: constant `1`
- `peer-hub`: refers to `/schemas/types.yaml#/definitions/phandle`; phandle to the peer hub on the controller.
- `ports`: refers to `/schemas/graph.yaml#/properties/ports`; The downstream facing USB ports

Pattern properties / child-node contracts: `^.*@[1-9a-f][0-9a-f]*$`.

External schema dependencies: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb-device.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb-device.yaml#`.

Pattern child nodes are validated with `^.*@[1-9a-f][0-9a-f]*$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb-device.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `hub@1, `device@5, `hub@2, `ports, `port@3`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hub.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hub.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hub.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 2 required field(s), 5 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hub.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-nop-xceiv.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-nop-xceiv.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-nop-xceiv.yaml`, a YAML devicetree binding titled "USB NOP PHY". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-nop-xceiv.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Rob Herring <robh@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `usb-nop-xceiv`.

Required top-level fields: `compatible`, `#phy-cells`.

Primary declared properties:
- `compatible`: constant `usb-nop-xceiv`
- `clocks`: items ?..1
- `clock-names`: constant `main_clk`
- `clock-frequency`: boolean/standard property admitted by this schema.
- `#phy-cells`: constant `0`
- `vcc-supply`: phandle to the regulator that provides power to the PHY.
- `power-domains`: items ?..1
- `reset-gpios`: items ?..1
- `vbus-detect-gpio`: items ?..1; Should specify the GPIO detecting a VBus insertion
- `vbus-supply`: regulator supplying VBUS. It will be enabled and disabled dynamically in OTG mode. If the regulator is controlled by a GPIO lin...
- `wakeup-source`: Specify if the USB phy can detect the remote wakeup signal while the system sleep.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `hsusb1_phy`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-nop-xceiv.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-nop-xceiv.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-nop-xceiv.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 11 top-level declared propert(ies), 2 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-nop-xceiv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch-ports.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch-ports.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch-ports.yaml`, a YAML devicetree binding titled "USB Orientation and Mode Switches Ports Graph Properties". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-switch-ports.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `port`: refers to `/schemas/graph.yaml#/$defs/port-base`; A port node to link the device to a TypeC controller for the purpose of handling altmode muxing and orientation switching.
- `ports`: refers to `/schemas/graph.yaml#/properties/ports`

External schema dependencies: `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32-array`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32-array`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.

## Test Signals
No inline DTS example is present; validation depends on in-tree DTS users and dt_binding_check schema compilation.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch-ports.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch-ports.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch-ports.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 2 top-level declared propert(ies), 0 required field(s), 5 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch-ports.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch.yaml`, a YAML devicetree binding titled "USB Orientation and Mode Switches Common Properties". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-switch.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `mode-switch`: type `boolean`; Possible handler of altmode switching
- `orientation-switch`: type `boolean`; Possible handler of orientation switching
- `retimer-switch`: type `boolean`; Possible handler of SuperSpeed signals retiming

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- The main risk is over-permissive validation: without strict closure or enough required fields, invalid DTS nodes can pass schema checks and fail later at probe time.

## Test Signals
No inline DTS example is present; validation depends on in-tree DTS users and dt_binding_check schema compilation.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 0 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-switch.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-uhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-uhci.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-uhci.yaml`, a YAML devicetree binding titled "Generic Platform UHCI Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-uhci.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
Accepts 6 compatible string(s): `generic-uhci`, `platform-uhci`, `aspeed,ast2400-uhci`, `aspeed,ast2500-uhci`, `aspeed,ast2600-uhci`, `aspeed,ast2700-uhci`.

Required top-level fields: `compatible`, `reg`, `interrupts`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: items ?..1
- `resets`: items ?..1
- `#ports`: refers to `/schemas/types.yaml#/definitions/uint32`
- `clocks`: items ?..1

External schema dependencies: `/schemas/types.yaml#/definitions/uint32`, `usb-hcd.yaml`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint32`, `usb-hcd.yaml`.

The schema contains 2 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint32`, `usb-hcd.yaml`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 2 inline example block(s), including node(s) `usb@d8007b00, `usb@1e6b0000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-uhci.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-uhci.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-uhci.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 3 required field(s), 2 external reference(s), and 2 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-uhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-xhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-xhci.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-xhci.yaml`, a YAML devicetree binding titled "Generic USB xHCI Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-xhci.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Mathias Nyman <mathias.nyman@intel.com>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `usb2-lpm-disable`: type `boolean`; Indicates if we don't want to enable USB2 HW LPM
- `usb3-lpm-capable`: type `boolean`; Determines if platform is USB3 LPM capable
- `quirk-broken-port-ped`: type `boolean`; Set if the controller has broken port disable mechanism
- `imod-interval-ns`: default `5000`; Interrupt moderation interval
- `num-hc-interrupters`: refers to `/schemas/types.yaml#/definitions/uint16`; Maximum number of interrupters to allocate

External schema dependencies: `/schemas/types.yaml#/definitions/uint16`, `usb-hcd.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint16`, `usb-hcd.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint16`, `usb-hcd.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-xhci.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-xhci.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-xhci.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 0 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-xhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml`, a YAML devicetree binding titled "Generic USB Controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `$nodename`: declared schema property.
- `phys`: List of all the USB PHYs on this HCD
- `phy-names`: Name specifier for the USB PHY
- `usb-phy`: refers to `/schemas/types.yaml#/definitions/phandle-array`; deprecated; List of all the USB PHYs on this HCD to be accepted by the legacy USB Physical Layer subsystem.
- `phy_type`: refers to `/schemas/types.yaml#/definitions/string`; enum `utmi`, `utmi_wide`, `ulpi`, `serial`, `hsic`; Tells USB controllers that we want to configure the core to support a UTMI+ PHY with an 8- or 16-bit interface if UTMI+ is sele...
- `maximum-speed`: refers to `/schemas/types.yaml#/definitions/string`; enum `low-speed`, `full-speed`, `high-speed`, `super-speed`, `super-speed-plus`, `super-speed-plus-gen2x1`, `super-speed-plus-gen1x2`, `super-speed-plus-gen2x2`; Tells USB controllers we want to work up to a certain speed. In case this isn't passed via DT, USB controllers should default t...

External schema dependencies: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.

## Test Signals
No inline DTS example is present; validation depends on in-tree DTS users and dt_binding_check schema compilation.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 0 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml`, a YAML devicetree binding titled "Microchip USB 2.0 Hi-Speed Hub Controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb251xb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Richard Leitner <richard.leitner@skidata.com>.

## Important APIs, Types, And Schema Surface
Accepts 10 compatible string(s): `microchip,usb2422`, `microchip,usb2512b`, `microchip,usb2512bi`, `microchip,usb2513b`, `microchip,usb2513bi`, `microchip,usb2514b`, `microchip,usb2514bi`, `microchip,usb2517`, `microchip,usb2517i`, `microchip,usb251xb`.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: enum `microchip,usb2422`, `microchip,usb2512b`, `microchip,usb2512bi`, `microchip,usb2513b`, `microchip,usb2513bi`, `microchip,usb2514b`, `microchip,usb2514bi`, `microchip,usb2517`...
- `reg`: items ?..1
- `reset-gpios`: Should specify the gpio for hub reset
- `vdd-supply`: Should specify the phandle to the regulator supplying vdd
- `skip-config`: refers to `/schemas/types.yaml#/definitions/flag`; Skip Hub configuration, but only send the USB-Attach command
- `vendor-id`: refers to `/schemas/types.yaml#/definitions/uint16`; default `1060`; Set USB Vendor ID of the hub
- `product-id`: refers to `/schemas/types.yaml#/definitions/uint16`; Set USB Product ID of the hub
- `device-id`: refers to `/schemas/types.yaml#/definitions/uint16`; default `2995`; Set USB Device ID of the hub
- `language-id`: refers to `/schemas/types.yaml#/definitions/uint16`; default `0`; Set USB Language ID
- `manufacturer`: refers to `/schemas/types.yaml#/definitions/string`; Set USB Manufacturer string (max 31 characters long)
- `product`: refers to `/schemas/types.yaml#/definitions/string`; Set USB Product string (max 31 characters long)
- `serial`: refers to `/schemas/types.yaml#/definitions/string`; Set USB Serial string (max 31 characters long)
- `bus-powered`: refers to `/schemas/types.yaml#/definitions/flag`; selects between self- and bus-powered operation (boolean, default is self-powered)
- `self-powered`: refers to `/schemas/types.yaml#/definitions/flag`; selects between self- and bus-powered operation (boolean, default is self-powered)
- `disable-hi-speed`: refers to `/schemas/types.yaml#/definitions/flag`; disable USB Hi-Speed support (boolean)
- `multi-tt`: refers to `/schemas/types.yaml#/definitions/flag`; selects between multi- and single-transaction-translator (boolean, default is multi-tt)
- `single-tt`: refers to `/schemas/types.yaml#/definitions/flag`; selects between multi- and single-transaction-translator (boolean, default is multi-tt)
- `disable-eop`: refers to `/schemas/types.yaml#/definitions/flag`; disable End of Packet generation in full-speed mode (boolean)
- Additional declared properties include `ganged-sensing`, `individual-sensing`, `ganged-port-switching`, `individual-port-switching`, `dynamic-power-switching`, `oc-delay-us`, `compound-device`, `port-mapping-mode`, `led-usb-mode`, `led-speed-mode`, `string-support`, `non-removable-ports`, `sp-disabled-ports`, `bp-disabled-ports`, `sp-max-total-current-microamp`, `bp-max-total-current-microamp`, ...

External schema dependencies: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint16`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint16`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint16`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 2 inline example block(s), including node(s) `i2c, `usb-hub@2c, `usb-hub@2d, `usb-hub`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 38 top-level declared propert(ies), 1 required field(s), 5 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/vialab,vl817.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/vialab,vl817.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/vialab,vl817.yaml`, a YAML devicetree binding titled "Via labs VL817 USB 3.1 hub controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `vialab,vl817.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Anand Moon <linux.amoon@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `usb2109,2817`, `usb2109,817`.

Required top-level fields: `compatible`, `reg`, `vdd-supply`, `peer-hub`.

Primary declared properties:
- `compatible`: enum `usb2109,2817`, `usb2109,817`
- `reg`: boolean/standard property admitted by this schema.
- `reset-gpios`: items ?..1; GPIO controlling the RESET# pin.
- `vdd-supply`: phandle to the regulator that provides power to the hub.
- `peer-hub`: refers to `/schemas/types.yaml#/definitions/phandle`; phandle to the peer hub on the controller.

External schema dependencies: `/schemas/types.yaml#/definitions/phandle`, `usb-device.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle`, `usb-device.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle`, `usb-device.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb, `hub@1, `hub@2`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/vialab,vl817.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/vialab,vl817.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/vialab,vl817.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 5 top-level declared propert(ies), 4 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/vialab,vl817.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/wch,ch334.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/wch,ch334.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/wch,ch334.yaml`, a YAML devicetree binding titled "WCH CH334/CH335 USB 2.0 Hub Controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `wch,ch334.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Chaoyi Chen <kernel@airkyi.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `usb1a86,8091`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: enum `usb1a86,8091`
- `reg`: boolean/standard property admitted by this schema.
- `reset-gpios`: GPIO controlling the RESET# pin.
- `vdd33-supply`: The regulator that provides 3.3V core power to the hub.
- `v5-supply`: The regulator that provides 3.3V or 5V power to the hub.
- `ports`: refers to `/schemas/graph.yaml#/properties/ports`

External schema dependencies: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `usb-hub.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `usb, `hub@1`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/wch,ch334.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/wch,ch334.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/wch,ch334.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 2 required field(s), 3 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/wch,ch334.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/willsemi,wusb3801.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/willsemi,wusb3801.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/willsemi,wusb3801.yaml`, a YAML devicetree binding titled "WUSB3801 Type-C port controller". It is a USB Type-C, PD, orientation, mode-switch, or analog switch binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `willsemi,wusb3801.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Samuel Holland <samuel@sholland.org>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `willsemi,wusb3801`.

Required top-level fields: `compatible`, `reg`, `interrupts`, `connector`.

Primary declared properties:
- `compatible`: enum `willsemi,wusb3801`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `connector`: refers to `../connector/usb-connector.yaml#`; type `object`; The managed USB Type-C connector. Since WUSB3801 does not support Power Delivery, the node should have the "pd-disable" property.

External schema dependencies: `../connector/usb-connector.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `../connector/usb-connector.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `../connector/usb-connector.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `i2c, `tcpc@60, `connector`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/willsemi,wusb3801.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/willsemi,wusb3801.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/willsemi,wusb3801.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/willsemi,wusb3801.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/xlnx,usb2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/xlnx,usb2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/xlnx,usb2.yaml`, a YAML devicetree binding titled "Xilinx udc controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `xlnx,usb2.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Radhey Shyam Pandey <radhey.shyam.pandey@amd.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `xlnx,usb2-device-4.00.a`.

Required top-level fields: `compatible`, `reg`, `interrupts`.

Primary declared properties:
- `compatible`: constant `xlnx,usb2-device-4.00.a`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `xlnx,has-builtin-dma`: type `boolean`; If present, hardware has dma capability.
- `clocks`: items 1..?
- `clock-names`: constant `s_axi_aclk`

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/xlnx,usb2.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/xlnx,usb2.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/xlnx,usb2.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 3 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/xlnx,usb2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/vendor-prefixes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/vendor-prefixes.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/vendor-prefixes.yaml`, a YAML devicetree binding titled "Devicetree Vendor Prefix Registry". It is a global devicetree vendor prefix registry; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `vendor-prefixes.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Rob Herring <robh@kernel.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:

Pattern properties / child-node contracts: `^(at25|bm|devbus|dmacap|dsa|exynos|fsi[ab]|gpio-fan|gpio-key|gpio|gpmc|hdmi|i2c-gpio),.*`, `^(keypad|m25p|max8952|max8997|max8998|mpmc),.*`, `^(pciclass|pinctrl-single|#pinctrl-single|PowerPC),.*`, `^(pl022|pxa-mmc|rcar_sound|rotary-encoder|s5m8767|sdhci),.*`, `^(simple-audio-card|st-plgpio|st-spics|ts|vsc8531),.*`, `^pool[0-3],.*`, `^100ask,.*`, `^70mai,.*`, `^8dev,.*`, `^9tripod,.*`, `^abb,.*`, `^abilis,.*`, `^abracon,.*`, `^abt,.*`, `^acbel,.*`, `^acelink,.*`, `^acer,.*`, `^acme,.*`, `^actions,.*`, `^actiontec,.*`, `^active-semi,.*`, `^ad,.*`, `^adafruit,.*`, `^adapteva,.*`, `^adaptrum,.*`, `^adh,.*`, `^adi,.*`, `^adieng,.*`, `^admatec,.*`, `^advantech,.*`, `^aeroflexgaisler,.*`, `^aesop,.*`, `^airoha,.*`, `^al,.*`, `^alcatel,.*`, `^aldec,.*`, `^alfa-network,.*`, `^algoltek,.*`, `^allegro,.*`, `^allegromicro,.*`, `^alliedtelesis,.*`, `^alliedvision,.*`, `^allo,.*`, `^allwinner,.*`, `^alphascale,.*`, `^alps,.*`, `^alt,.*`, `^altr,.*`, `^amarula,.*`, `^amazon,.*`, `^amcc,.*`, `^amd,.*`, `^amediatech,.*`, `^amlogic,.*`, `^ampere,.*`, `^amphenol,.*`, `^ampire,.*`, `^ams,.*`, `^amstaos,.*`, `^analogix,.*`, `^anbernic,.*`, `^andestech,.*`, `^anlogic,.*`, `^anvo,.*`, `^aoly,.*`, `^aosong,.*`, `^apm,.*`, `^apple,.*`, `^aptina,.*`, `^arasan,.*`, `^archermind,.*`, `^arcom,.*`, `^arctic,.*`, `^arcx,.*`, `^arduino,.*`, `^argon40,.*`, `^ariaboard,.*`, `^aries,.*`, `^arm,.*`, `^armadeus,.*`, `^armchina,.*`, `^armsom,.*`, `^arrow,.*`, `^artesyn,.*`, `^asahi-kasei,.*`, `^asc,.*`, `^asix,.*`, `^asl-tek,.*`, `^aspeed,.*`, `^asrock,.*`, `^asteralabs,.*`, `^asus,.*`, `^atheros,.*`, `^atlas,.*`, `^atmel,.*`, `^auo,.*`, `^auvidea,.*`, `^avago,.*`, `^avia,.*`, `^avic,.*`, `^avnet,.*`, `^awinic,.*`, `^axentia,.*`, `^axiado,.*`, `^axis,.*`, `^ayaneo,.*`, `^azoteq,.*`, `^azw,.*`, `^baikal,.*`, `^bananapi,.*`, `^beacon,.*`, `^beagle,.*`, `^belling,.*`, `^bestar,.*`, `^bhf,.*`, `^bigtreetech,.*`, `^bitmain,.*`, `^blaize,.*`, `^bluegiga,.*`, `^blutek,.*`, `^boe,.*`, `^bosch,.*`, `^boundary,.*`, `^brcm,.*`, `^broadmobi,.*`, `^bsh,.*`, `^bst,.*`, `^bticino,.*`, `^buffalo,.*`, `^buglabs,.*`, `^bur,.*`, `^bytedance,.*`, `^calamp,.*`, `^calao,.*`, `^calaosystems,.*`, `^calxeda,.*`, `^cameo,.*`, `^canaan,.*`, `^caninos,.*`, `^capella,.*`, `^cascoda,.*`, `^catalyst,.*`, `^cavium,.*`, `^cct,.*`, `^cdns,.*`, `^cdtech,.*`, `^cellwise,.*`, `^ceva,.*`, `^chargebyte,.*`, `^checkpoint,.*`, `^chefree,.*`, `^chipidea,.*`, `^chipone,.*`, `^chipspark,.*`, `^chongzhou,.*`, `^chrontel,.*`, `^chrp,.*`, `^chunghwa,.*`, `^chuwi,.*`, `^ciaa,.*`, `^cirrus,.*`, `^cisco,.*`, `^cix,.*`, `^clockwork,.*`, `^cloos,.*`, `^cloudengines,.*`, `^cnm,.*`, `^cnxt,.*`, `^colorfly,.*`, `^compal,.*`, `^compulab,.*`, `^comvetia,.*`, `^congatec,.*`, `^coolpi,.*`, `^coreriver,.*`, `^corpro,.*`, `^corechips,.*`, `^cortina,.*`, `^cosmic,.*`, `^crane,.*`, `^creative,.*`, `^crystalfontz,.*`, `^csky,.*`, `^csot,.*`, `^csq,.*`, `^csr,.*`, `^ctera,.*`, `^ctu,.*`, `^cubietech,.*`, `^cudy,.*`, `^cui,.*`, `^cypress,.*`, `^cyx,.*`, `^cznic,.*`, `^dallas,.*`, `^dataimage,.*`, `^davicom,.*`, `^deepcomputing,.*`, `^dell,.*`, `^delta,.*`, `^densitron,.*`, `^denx,.*`, `^devantech,.*`, `^dfi,.*`, `^dfrobot,.*`, `^dh,.*`, `^difrnce,.*`, `^digi,.*`, `^digilent,.*`, `^dimonoff,.*`, `^diodes,.*`, `^dioo,.*`, `^djn,.*`, `^dlc,.*`, `^dlg,.*`, `^dlink,.*`, `^dmo,.*`, `^doestek,.*`, `^domintech,.*`, `^dongwoon,.*`, `^dptechnics,.*`, `^dragino,.*`, `^dream,.*`, `^ds,.*`, `^dserve,.*`, `^dynaimage,.*`, `^ea,.*`, `^ebang,.*`, `^ebbg,.*`, `^ebs-systart,.*`, `^ebv,.*`, `^eckelmann,.*`, `^econet,.*`, `^edgeble,.*`, `^edimax,.*`, `^edt,.*`, `^ees,.*`, `^eeti,.*`, `^egnite,.*`, `^einfochips,.*`, `^eink,.*`, `^elan,.*`, `^element14,.*`, `^elgin,.*`, `^elida,.*`, `^elimo,.*`, `^elpida,.*`, `^embedfire,.*`, `^embest,.*`, `^emcraft,.*`, `^emlid,.*`, `^emmicro,.*`, `^empire-electronix,.*`, `^emtrion,.*`, `^enbw,.*`, `^enclustra,.*`, `^endian,.*`, `^endless,.*`, `^ene,.*`, `^energymicro,.*`, `^engicam,.*`, `^engleder,.*`, `^epcos,.*`, `^epfl,.*`, `^epson,.*`, `^esp,.*`, `^est,.*`, `^eswin,.*`, `^etekmicro,.*`, `^ettus,.*`, `^eukrea,.*`, `^everest,.*`, `^everspin,.*`, `^evervision,.*`, `^exar,.*`, `^excito,.*`, `^exegin,.*`, `^ezchip,.*`, `^ezurio,.*`, `^facebook,.*`, `^fairchild,.*`, `^fairphone,.*`, `^faraday,.*`, `^fascontek,.*`, `^fastrax,.*`, `^fcs,.*`, `^feixin,.*`, `^feiyang,.*`, `^fii,.*`, `^firefly,.*`, `^fitipower,.*`, `^flipkart,.*`, `^focaltech,.*`, `^forlinx,.*`, `^foursemi,.*`, `^foxlink,.*`, `^freebox,.*`, `^freecom,.*`, `^frida,.*`, `^friendlyarm,.*`, `^fsl,.*`, `^fujitsu,.*`, `^fxtec,.*`, `^galaxycore,.*`, `^gameforce,.*`, `^gardena,.*`, `^gateway,.*`, `^gateworks,.*`, `^gcw,.*`, `^ge,.*`, `^geekbuying,.*`, `^gef,.*`, `^GEFanuc,.*`, `^gehc,.*`, `^gemei,.*`, `^gemtek,.*`, `^genesys,.*`, `^genexis,.*`, `^geniatech,.*`, `^giantec,.*`, `^giantplus,.*`, `^glinet,.*`, `^globalscale,.*`, `^globaltop,.*`, `^gmt,.*`, `^gocontroll,.*`, `^goldelico,.*`, `^goodix,.*`, `^google,.*`, `^goramo,.*`, `^gplus,.*`, `^grinn,.*`, `^grmn,.*`, `^gumstix,.*`, `^gw,.*`, `^hannstar,.*`, `^haochuangyi,.*`, `^haoyu,.*`, `^hardkernel,.*`, `^hce,.*`, `^headacoustics,.*`, `^hechuang,.*`, `^hideep,.*`, `^himax,.*`, `^hinlink,.*`, `^hirschmann,.*`, `^hisi,.*`, `^hisilicon,.*`, `^hit,.*`, `^hitex,.*`, `^hitron,.*`, `^holitech,.*`, `^holt,.*`, `^holtek,.*`, `^honestar,.*`, `^honeywell,.*`, `^hoperf,.*`, `^hoperun,.*`, `^hp,.*`, `^hpe,.*`, `^hsg,.*`, `^htc,.*`, `^huawei,.*`, `^hugsun,.*`, `^huiling,.*`, `^hwacom,.*`, `^hxt,.*`, `^hycon,.*`, `^hydis,.*`, `^hynetek,.*`, `^hynitron,.*`, `^hynix,.*`, `^hyundai,.*`, `^i2se,.*`, `^IBM,.*`, `^ibm,.*`, `^icplus,.*`, `^idt,.*`, `^iei,.*`, `^ifi,.*`, `^ifm,.*`, `^ilitek,.*`, `^imagis,.*`, `^img,.*`, `^imi,.*`, `^inanbo,.*`, `^incircuit,.*`, `^incostartec,.*`, `^indiedroid,.*`, `^inet-tek,.*`, `^infineon,.*`, `^inforce,.*`, `^ingenic,.*`, `^ingrasys,.*`, `^injoinic,.*`, `^innocomm,.*`, `^innolux,.*`, `^inside-secure,.*`, `^insignal,.*`, `^inspur,.*`, `^intel,.*`, `^intercontrol,.*`, `^invensense,.*`, `^inventec,.*`, `^inversepath,.*`, `^iom,.*`, `^irondevice,.*`, `^isee,.*`, `^isil,.*`, `^issi,.*`, `^ite,.*`, `^itead,.*`, `^itian,.*`, `^ivo,.*`, `^iwave,.*`, `^jadard,.*`, `^jasonic,.*`, `^jdi,.*`, `^jedec,.*`, `^jenson,.*`, `^jesurun,.*`, `^jethome,.*`, `^jianda,.*`, `^jide,.*`, `^joz,.*`, `^jty,.*`, `^jutouch,.*`, `^kam,.*`, `^karo,.*`, `^keithkoep,.*`, `^keymile,.*`, `^khadas,.*`, `^kiebackpeter,.*`, `^kinetic,.*`, `^kingdisplay,.*`, `^kingnovel,.*`, `^kionix,.*`, `^kobo,.*`, `^kobol,.*`, `^koe,.*`, `^kontron,.*`, `^kosagi,.*`, `^kvg,.*`, `^kyo,.*`, `^lacie,.*`, `^laird,.*`, `^lamobo,.*`, `^lantiq,.*`, `^lattice,.*`, `^lckfb,.*`, `^lctech,.*`, `^leadtek,.*`, `^leez,.*`, `^lego,.*`, `^lemaker,.*`, `^lenovo,.*`, `^lg,.*`, `^lgphilips,.*`, `^libretech,.*`, `^licheepi,.*`, `^linaro,.*`, `^lincolntech,.*`, `^lineartechnology,.*`, `^linkease,.*`, `^linksprite,.*`, `^linksys,.*`, `^linutronix,.*`, `^linux,.*`, `^linx,.*`, `^liontron,.*`, `^liteon,.*`, `^litex,.*`, `^lltc,.*`, `^logicpd,.*`, `^logictechno,.*`, `^longcheer,.*`, `^lontium,.*`, `^loongson,.*`, `^loongmasses,.*`, `^lsi,.*`, `^luckfox,.*`, `^lunzn,.*`, `^luxul,.*`, `^lwn,.*`, `^lxa,.*`, `^lxd,.*`, `^m5stack,.*`, `^macnica,.*`, `^mantix,.*`, `^mapleboard,.*`, `^marantec,.*`, `^marvell,.*`, `^maxbotix,.*`, `^maxim,.*`, `^maxlinear,.*`, `^maxtor,.*`, `^mayqueen,.*`, `^mbvl,.*`, `^mcube,.*`, `^meas,.*`, `^mecer,.*`, `^mediatek,.*`, `^medion,.*`, `^megachips,.*`, `^mele,.*`, `^melexis,.*`, `^melfas,.*`, `^mellanox,.*`, `^memsensing,.*`, `^memsic,.*`, `^menlo,.*`, `^mentor,.*`, `^meraki,.*`, `^merrii,.*`, `^methode,.*`, `^micrel,.*`, `^microchip,.*`, `^microcrystal,.*`, `^micron,.*`, `^microsoft,.*`, `^microsys,.*`, `^microtips,.*`, `^mikroe,.*`, `^mikrotik,.*`, `^milianke,.*`, `^milkv,.*`, `^miniand,.*`, `^minix,.*`, `^mips,.*`, `^miramems,.*`, `^mitsubishi,.*`, `^mitsumi,.*`, `^mixel,.*`, `^miyoo,.*`, `^mntre,.*`, `^mobileye,.*`, `^modtronix,.*`, `^moortec,.*`, `^mosaixtech,.*`, `^motorcomm,.*`, `^motorola,.*`, `^moxa,.*`, `^mpl,.*`, `^mps,.*`, `^mqmaker,.*`, `^mrvl,.*`, `^mscc,.*`, `^msi,.*`, `^mstar,.*`, `^mti,.*`, `^multi-inno,.*`, `^mundoreader,.*`, `^murata,.*`, `^mxic,.*`, `^mxicy,.*`, `^myir,.*`, `^national,.*`, `^neardi,.*`, `^nec,.*`, `^neofidelity,.*`, `^neonode,.*`, `^netcube,.*`, `^netgear,.*`, `^netlogic,.*`, `^netron-dy,.*`, `^netronix,.*`, `^netxeon,.*`, `^neweast,.*`, `^newhaven,.*`, `^newvision,.*`, `^nexbox,.*`, `^nextthing,.*`, `^ni,.*`, `^nicera,.*`, `^nintendo,.*`, `^nlt,.*`, `^nokia,.*`, `^nordic,.*`, `^nothing,.*`, `^novatech,.*`, `^novatek,.*`, `^novtech,.*`, `^nuclei,.*`, `^numonyx,.*`, `^nutsboard,.*`, `^nuvoton,.*`, `^nvd,.*`, `^nvidia,.*`, `^nxp,.*`, `^oceanic,.*`, `^ocs,.*`, `^oct,.*`, `^okaya,.*`, `^oki,.*`, `^olimex,.*`, `^olpc,.*`, `^oneplus,.*`, `^onething,.*`, `^onie,.*`, `^onion,.*`, `^onnn,.*`, `^ontat,.*`, `^opalkelly,.*`, `^openailab,.*`, `^opencores,.*`, `^openembed,.*`, `^openpandora,.*`, `^openrisc,.*`, `^openwrt,.*`, `^option,.*`, `^oranth,.*`, `^ORCL,.*`, `^orisetech,.*`, `^ortustech,.*`, `^osddisplays,.*`, `^osmc,.*`, `^ouya,.*`, `^overkiz,.*`, `^ovti,.*`, `^oxsemi,.*`, `^ozzmaker,.*`, `^panasonic,.*`, `^parade,.*`, `^parallax,.*`, `^particle,.*`, `^pda,.*`, `^pegatron,.*`, `^pericom,.*`, `^pervasive,.*`, `^phicomm,.*`, `^phontech,.*`, `^phytec,.*`, `^picochip,.*`, `^pine64,.*`, `^pineriver,.*`, `^pixcir,.*`, `^plantower,.*`, `^plathome,.*`, `^plda,.*`, `^plx,.*`, `^ply,.*`, `^pni,.*`, `^pocketbook,.*`, `^polaroid,.*`, `^polyhex,.*`, `^portwell,.*`, `^poslab,.*`, `^pov,.*`, `^powertip,.*`, `^powervr,.*`, `^powkiddy,.*`, `^primeview,.*`, `^primux,.*`, `^probox2,.*`, `^pri,.*`, `^prt,.*`, `^pulsedlight,.*`, `^purism,.*`, `^puya,.*`, `^qca,.*`, `^qcom,.*`, `^qemu,.*`, `^qi,.*`, `^qiaodian,.*`, `^qihua,.*`, `^qishenglong,.*`, `^qnap,.*`, `^quanta,.*`, `^radxa,.*`, `^raidsonic,.*`, `^ralink,.*`, `^ramtron,.*`, `^raspberrypi,.*`, `^raumfeld,.*`, `^raydium,.*`, `^raystar,.*`, `^rda,.*`, `^realtek,.*`, `^relfor,.*`, `^remarkable,.*`, `^renesas,.*`, `^rervision,.*`, `^retronix,.*`, `^revotics,.*`, `^rex,.*`, `^rfdigital,.*`, `^richtek,.*`, `^ricoh,.*`, `^rikomagic,.*`, `^riot,.*`, `^riscv,.*`, `^rockchip,.*`, `^rocktech,.*`, `^rohm,.*`, `^ronbo,.*`, `^ronetix,.*`, `^roofull,.*`, `^roseapplepi,.*`, `^rve,.*`, `^saef,.*`, `^sakurapi,.*`, `^samsung,.*`, `^samtec,.*`, `^sancloud,.*`, `^sandisk,.*`, `^satoz,.*`, `^sbs,.*`, `^schindler,.*`, `^schneider,.*`, `^schulercontrol,.*`, `^sciosense,.*`, `^sdmc,.*`, `^seagate,.*`, `^seeed,.*`, `^seirobotics,.*`, `^semtech,.*`, `^senseair,.*`, `^sensirion,.*`, `^sensortek,.*`, `^sercomm,.*`, `^sff,.*`, `^sgd,.*`, `^sgmicro,.*`, `^sgx,.*`, `^sharp,.*`, `^shift,.*`, `^shimafuji,.*`, `^shineworld,.*`, `^shiratech,.*`, `^si-en,.*`, `^si-linux,.*`, `^sielaff,.*`, `^siemens,.*`, `^sifive,.*`, `^siflower,.*`, `^sigma,.*`, `^sii,.*`, `^sil,.*`, `^silabs,.*`, `^silan,.*`, `^silead,.*`, `^silergy,.*`, `^silex-insight,.*`, `^siliconfile,.*`, `^siliconmitus,.*`, `^silvaco,.*`, `^simtek,.*`, `^sinlinx,.*`, `^sinovoip,.*`, `^sinowealth,.*`, `^sipeed,.*`, `^sirf,.*`, `^sis,.*`, `^sitronix,.*`, `^skov,.*`, `^skyworks,.*`, `^smartfiber,.*`, `^smartlabs,.*`, `^smartrg,.*`, `^smi,.*`, `^smsc,.*`, `^snps,.*`, `^sochip,.*`, `^socionext,.*`, `^solidrun,.*`, `^solomon,.*`, `^somfy,.*`, `^sony,.*`, `^sophgo,.*`, `^sourceparts,.*`, `^spacemit,.*`, `^spansion,.*`, `^sparkfun,.*`, `^spinalhdl,.*`, `^sprd,.*`, `^square,.*`, `^ssi,.*`, `^sst,.*`, `^sstar,.*`, `^st,.*`, `^starfive,.*`, `^starry,.*`, `^startek,.*`, `^starterkit,.*`, `^ste,.*`, `^stericsson,.*`, `^st-ericsson,.*`, `^storlink,.*`, `^storm,.*`, `^storopack,.*`, `^summit,.*`, `^sunchip,.*`, `^sundance,.*`, `^sunplus,.*`, `^SUNW,.*`, `^supermicro,.*`, `^swir,.*`, `^syna,.*`, `^synaptics,.*`, `^synology,.*`, `^synopsys,.*`, `^taiguanck,.*`, `^taos,.*`, `^tbs,.*`, `^tbs-biometrics,.*`, `^tcg,.*`, `^tcl,.*`, `^tcs,.*`, `^tcu,.*`, `^tdo,.*`, `^team-source-display,.*`, `^technexion,.*`, `^technologic,.*`, `^techstar,.*`, `^techwell,.*`, `^teejet,.*`, `^teltonika,.*`, `^tempo,.*`, `^tenda,.*`, `^tenstorrent,.*`, `^terasic,.*`, `^tesla,.*`, `^test,.*`, `^tfc,.*`, `^thead,.*`, `^thine,.*`, `^thingyjp,.*`, `^thundercomm,.*`, `^thwc,.*`, `^ti,.*`, `^tianma,.*`, `^tlm,.*`, `^tmt,.*`, `^topeet,.*`, `^topic,.*`, `^topland,.*`, `^toppoly,.*`, `^topwise,.*`, `^toradex,.*`, `^toshiba,.*`, `^toumaz,.*`, `^tpk,.*`, `^tplink,.*`, `^tpo,.*`, `^tq,.*`, `^transpeed,.*`, `^traverse,.*`, `^tronfy,.*`, `^tronsmart,.*`, `^truly,.*`, `^tsd,.*`, `^turing,.*`, `^tuxedo,.*`, `^tyan,.*`, `^tyhx,.*`, `^u-blox,.*`, `^u-boot,.*`, `^ubnt,.*`, `^ucrobotics,.*`, `^udoo,.*`, `^ufispace,.*`, `^ugoos,.*`, `^ultrapower,.*`, `^uni-t,.*`, `^uniwest,.*`, `^upisemi,.*`, `^urt,.*`, `^usi,.*`, `^usr,.*`, `^ultrarisc,.*`, `^ultratronik,.*`, `^utoo,.*`, `^v3,.*`, `^vaisala,.*`, `^valve,.*`, `^vamrs,.*`, `^variscite,.*`, `^vdl,.*`, `^verisilicon,.*`, `^vertexcom,.*`, `^via,.*`, `^vialab,.*`, `^vicor,.*`, `^videostrong,.*`, `^virtio,.*`, `^virtual,.*`, `^vishay,.*`, `^visionox,.*`, `^vitesse,.*`, `^vivante,.*`, `^vivax,.*`, `^vocore,.*`, `^voipac,.*`, `^voltafield,.*`, `^vot,.*`, `^vscom,.*`, `^vxt,.*`, `^wacom,.*`, `^wanchanglong,.*`, `^wand,.*`, `^waveshare,.*`, `^wd,.*`, `^we,.*`, `^welltech,.*`, `^wetek,.*`, `^wexler,.*`, `^whwave,.*`, `^wi2wi,.*`, `^widora,.*`, `^wiko,.*`, `^wiligear,.*`, `^willsemi,.*`, `^winbond,.*`, `^wingtech,.*`, `^winlink,.*`, `^winsen,.*`, `^winstar,.*`, `^wirelesstag,.*`, `^wits,.*`, `^wlf,.*`, `^wm,.*`, `^wobo,.*`, `^wolfvision,.*`, `^x-powers,.*`, `^xen,.*`, `^xes,.*`, `^xiaomi,.*`, `^xicor,.*`, `^xillybus,.*`, `^xingbangda,.*`, `^xinpeng,.*`, `^xiphera,.*`, `^xlnx,.*`, `^xnano,.*`, `^xunlong,.*`, `^xylon,.*`, `^yadro,.*`, `^yamaha,.*`, `^yes-optoelectronics,.*`, `^yic,.*`, `^yiming,.*`, `^ylm,.*`, `^yna,.*`, `^yones-toptech,.*`, `^ys,.*`, `^ysoft,.*`, `^yuridenki,.*`, `^yuzukihd,.*`, `^zarlink,.*`, `^zealz,.*`, `^zeitec,.*`, `^zidoo,.*`, `^zii,.*`, `^zinitix,.*`, `^zkmagic,.*`, `^zte,.*`, `^zyxel,.*`, `^[a-zA-Z0-9#_][a-zA-Z0-9#+\-._@]{0,63}$`, `^[a-zA-Z0-9+\-._]*@[0-9a-zA-Z,]*$`, `^#.*`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Pattern child nodes are validated with `^(at25|bm|devbus|dmacap|dsa|exynos|fsi[ab]|gpio-fan|gpio-key|gpio|gpmc|hdmi|i2c-gpio),.*`, `^(keypad|m25p|max8952|max8997|max8998|mpmc),.*`, `^(pciclass|pinctrl-single|#pinctrl-single|PowerPC),.*`, `^(pl022|pxa-mmc|rcar_sound|rotary-encoder|s5m8767|sdhci),.*`, `^(simple-audio-card|st-plgpio|st-spics|ts|vsc8531),.*`, `^pool[0-3],.*`, `^100ask,.*`, `^70mai,.*`, `^8dev,.*`, `^9tripod,.*`, `^abb,.*`, `^abilis,.*`, `^abracon,.*`, `^abt,.*`, `^acbel,.*`, `^acelink,.*`, `^acer,.*`, `^acme,.*`, `^actions,.*`, `^actiontec,.*`, `^active-semi,.*`, `^ad,.*`, `^adafruit,.*`, `^adapteva,.*`, `^adaptrum,.*`, `^adh,.*`, `^adi,.*`, `^adieng,.*`, `^admatec,.*`, `^advantech,.*`, `^aeroflexgaisler,.*`, `^aesop,.*`, `^airoha,.*`, `^al,.*`, `^alcatel,.*`, `^aldec,.*`, `^alfa-network,.*`, `^algoltek,.*`, `^allegro,.*`, `^allegromicro,.*`, `^alliedtelesis,.*`, `^alliedvision,.*`, `^allo,.*`, `^allwinner,.*`, `^alphascale,.*`, `^alps,.*`, `^alt,.*`, `^altr,.*`, `^amarula,.*`, `^amazon,.*`, `^amcc,.*`, `^amd,.*`, `^amediatech,.*`, `^amlogic,.*`, `^ampere,.*`, `^amphenol,.*`, `^ampire,.*`, `^ams,.*`, `^amstaos,.*`, `^analogix,.*`, `^anbernic,.*`, `^andestech,.*`, `^anlogic,.*`, `^anvo,.*`, `^aoly,.*`, `^aosong,.*`, `^apm,.*`, `^apple,.*`, `^aptina,.*`, `^arasan,.*`, `^archermind,.*`, `^arcom,.*`, `^arctic,.*`, `^arcx,.*`, `^arduino,.*`, `^argon40,.*`, `^ariaboard,.*`, `^aries,.*`, `^arm,.*`, `^armadeus,.*`, `^armchina,.*`, `^armsom,.*`, `^arrow,.*`, `^artesyn,.*`, `^asahi-kasei,.*`, `^asc,.*`, `^asix,.*`, `^asl-tek,.*`, `^aspeed,.*`, `^asrock,.*`, `^asteralabs,.*`, `^asus,.*`, `^atheros,.*`, `^atlas,.*`, `^atmel,.*`, `^auo,.*`, `^auvidea,.*`, `^avago,.*`, `^avia,.*`, `^avic,.*`, `^avnet,.*`, `^awinic,.*`, `^axentia,.*`, `^axiado,.*`, `^axis,.*`, `^ayaneo,.*`, `^azoteq,.*`, `^azw,.*`, `^baikal,.*`, `^bananapi,.*`, `^beacon,.*`, `^beagle,.*`, `^belling,.*`, `^bestar,.*`, `^bhf,.*`, `^bigtreetech,.*`, `^bitmain,.*`, `^blaize,.*`, `^bluegiga,.*`, `^blutek,.*`, `^boe,.*`, `^bosch,.*`, `^boundary,.*`, `^brcm,.*`, `^broadmobi,.*`, `^bsh,.*`, `^bst,.*`, `^bticino,.*`, `^buffalo,.*`, `^buglabs,.*`, `^bur,.*`, `^bytedance,.*`, `^calamp,.*`, `^calao,.*`, `^calaosystems,.*`, `^calxeda,.*`, `^cameo,.*`, `^canaan,.*`, `^caninos,.*`, `^capella,.*`, `^cascoda,.*`, `^catalyst,.*`, `^cavium,.*`, `^cct,.*`, `^cdns,.*`, `^cdtech,.*`, `^cellwise,.*`, `^ceva,.*`, `^chargebyte,.*`, `^checkpoint,.*`, `^chefree,.*`, `^chipidea,.*`, `^chipone,.*`, `^chipspark,.*`, `^chongzhou,.*`, `^chrontel,.*`, `^chrp,.*`, `^chunghwa,.*`, `^chuwi,.*`, `^ciaa,.*`, `^cirrus,.*`, `^cisco,.*`, `^cix,.*`, `^clockwork,.*`, `^cloos,.*`, `^cloudengines,.*`, `^cnm,.*`, `^cnxt,.*`, `^colorfly,.*`, `^compal,.*`, `^compulab,.*`, `^comvetia,.*`, `^congatec,.*`, `^coolpi,.*`, `^coreriver,.*`, `^corpro,.*`, `^corechips,.*`, `^cortina,.*`, `^cosmic,.*`, `^crane,.*`, `^creative,.*`, `^crystalfontz,.*`, `^csky,.*`, `^csot,.*`, `^csq,.*`, `^csr,.*`, `^ctera,.*`, `^ctu,.*`, `^cubietech,.*`, `^cudy,.*`, `^cui,.*`, `^cypress,.*`, `^cyx,.*`, `^cznic,.*`, `^dallas,.*`, `^dataimage,.*`, `^davicom,.*`, `^deepcomputing,.*`, `^dell,.*`, `^delta,.*`, `^densitron,.*`, `^denx,.*`, `^devantech,.*`, `^dfi,.*`, `^dfrobot,.*`, `^dh,.*`, `^difrnce,.*`, `^digi,.*`, `^digilent,.*`, `^dimonoff,.*`, `^diodes,.*`, `^dioo,.*`, `^djn,.*`, `^dlc,.*`, `^dlg,.*`, `^dlink,.*`, `^dmo,.*`, `^doestek,.*`, `^domintech,.*`, `^dongwoon,.*`, `^dptechnics,.*`, `^dragino,.*`, `^dream,.*`, `^ds,.*`, `^dserve,.*`, `^dynaimage,.*`, `^ea,.*`, `^ebang,.*`, `^ebbg,.*`, `^ebs-systart,.*`, `^ebv,.*`, `^eckelmann,.*`, `^econet,.*`, `^edgeble,.*`, `^edimax,.*`, `^edt,.*`, `^ees,.*`, `^eeti,.*`, `^egnite,.*`, `^einfochips,.*`, `^eink,.*`, `^elan,.*`, `^element14,.*`, `^elgin,.*`, `^elida,.*`, `^elimo,.*`, `^elpida,.*`, `^embedfire,.*`, `^embest,.*`, `^emcraft,.*`, `^emlid,.*`, `^emmicro,.*`, `^empire-electronix,.*`, `^emtrion,.*`, `^enbw,.*`, `^enclustra,.*`, `^endian,.*`, `^endless,.*`, `^ene,.*`, `^energymicro,.*`, `^engicam,.*`, `^engleder,.*`, `^epcos,.*`, `^epfl,.*`, `^epson,.*`, `^esp,.*`, `^est,.*`, `^eswin,.*`, `^etekmicro,.*`, `^ettus,.*`, `^eukrea,.*`, `^everest,.*`, `^everspin,.*`, `^evervision,.*`, `^exar,.*`, `^excito,.*`, `^exegin,.*`, `^ezchip,.*`, `^ezurio,.*`, `^facebook,.*`, `^fairchild,.*`, `^fairphone,.*`, `^faraday,.*`, `^fascontek,.*`, `^fastrax,.*`, `^fcs,.*`, `^feixin,.*`, `^feiyang,.*`, `^fii,.*`, `^firefly,.*`, `^fitipower,.*`, `^flipkart,.*`, `^focaltech,.*`, `^forlinx,.*`, `^foursemi,.*`, `^foxlink,.*`, `^freebox,.*`, `^freecom,.*`, `^frida,.*`, `^friendlyarm,.*`, `^fsl,.*`, `^fujitsu,.*`, `^fxtec,.*`, `^galaxycore,.*`, `^gameforce,.*`, `^gardena,.*`, `^gateway,.*`, `^gateworks,.*`, `^gcw,.*`, `^ge,.*`, `^geekbuying,.*`, `^gef,.*`, `^GEFanuc,.*`, `^gehc,.*`, `^gemei,.*`, `^gemtek,.*`, `^genesys,.*`, `^genexis,.*`, `^geniatech,.*`, `^giantec,.*`, `^giantplus,.*`, `^glinet,.*`, `^globalscale,.*`, `^globaltop,.*`, `^gmt,.*`, `^gocontroll,.*`, `^goldelico,.*`, `^goodix,.*`, `^google,.*`, `^goramo,.*`, `^gplus,.*`, `^grinn,.*`, `^grmn,.*`, `^gumstix,.*`, `^gw,.*`, `^hannstar,.*`, `^haochuangyi,.*`, `^haoyu,.*`, `^hardkernel,.*`, `^hce,.*`, `^headacoustics,.*`, `^hechuang,.*`, `^hideep,.*`, `^himax,.*`, `^hinlink,.*`, `^hirschmann,.*`, `^hisi,.*`, `^hisilicon,.*`, `^hit,.*`, `^hitex,.*`, `^hitron,.*`, `^holitech,.*`, `^holt,.*`, `^holtek,.*`, `^honestar,.*`, `^honeywell,.*`, `^hoperf,.*`, `^hoperun,.*`, `^hp,.*`, `^hpe,.*`, `^hsg,.*`, `^htc,.*`, `^huawei,.*`, `^hugsun,.*`, `^huiling,.*`, `^hwacom,.*`, `^hxt,.*`, `^hycon,.*`, `^hydis,.*`, `^hynetek,.*`, `^hynitron,.*`, `^hynix,.*`, `^hyundai,.*`, `^i2se,.*`, `^IBM,.*`, `^ibm,.*`, `^icplus,.*`, `^idt,.*`, `^iei,.*`, `^ifi,.*`, `^ifm,.*`, `^ilitek,.*`, `^imagis,.*`, `^img,.*`, `^imi,.*`, `^inanbo,.*`, `^incircuit,.*`, `^incostartec,.*`, `^indiedroid,.*`, `^inet-tek,.*`, `^infineon,.*`, `^inforce,.*`, `^ingenic,.*`, `^ingrasys,.*`, `^injoinic,.*`, `^innocomm,.*`, `^innolux,.*`, `^inside-secure,.*`, `^insignal,.*`, `^inspur,.*`, `^intel,.*`, `^intercontrol,.*`, `^invensense,.*`, `^inventec,.*`, `^inversepath,.*`, `^iom,.*`, `^irondevice,.*`, `^isee,.*`, `^isil,.*`, `^issi,.*`, `^ite,.*`, `^itead,.*`, `^itian,.*`, `^ivo,.*`, `^iwave,.*`, `^jadard,.*`, `^jasonic,.*`, `^jdi,.*`, `^jedec,.*`, `^jenson,.*`, `^jesurun,.*`, `^jethome,.*`, `^jianda,.*`, `^jide,.*`, `^joz,.*`, `^jty,.*`, `^jutouch,.*`, `^kam,.*`, `^karo,.*`, `^keithkoep,.*`, `^keymile,.*`, `^khadas,.*`, `^kiebackpeter,.*`, `^kinetic,.*`, `^kingdisplay,.*`, `^kingnovel,.*`, `^kionix,.*`, `^kobo,.*`, `^kobol,.*`, `^koe,.*`, `^kontron,.*`, `^kosagi,.*`, `^kvg,.*`, `^kyo,.*`, `^lacie,.*`, `^laird,.*`, `^lamobo,.*`, `^lantiq,.*`, `^lattice,.*`, `^lckfb,.*`, `^lctech,.*`, `^leadtek,.*`, `^leez,.*`, `^lego,.*`, `^lemaker,.*`, `^lenovo,.*`, `^lg,.*`, `^lgphilips,.*`, `^libretech,.*`, `^licheepi,.*`, `^linaro,.*`, `^lincolntech,.*`, `^lineartechnology,.*`, `^linkease,.*`, `^linksprite,.*`, `^linksys,.*`, `^linutronix,.*`, `^linux,.*`, `^linx,.*`, `^liontron,.*`, `^liteon,.*`, `^litex,.*`, `^lltc,.*`, `^logicpd,.*`, `^logictechno,.*`, `^longcheer,.*`, `^lontium,.*`, `^loongson,.*`, `^loongmasses,.*`, `^lsi,.*`, `^luckfox,.*`, `^lunzn,.*`, `^luxul,.*`, `^lwn,.*`, `^lxa,.*`, `^lxd,.*`, `^m5stack,.*`, `^macnica,.*`, `^mantix,.*`, `^mapleboard,.*`, `^marantec,.*`, `^marvell,.*`, `^maxbotix,.*`, `^maxim,.*`, `^maxlinear,.*`, `^maxtor,.*`, `^mayqueen,.*`, `^mbvl,.*`, `^mcube,.*`, `^meas,.*`, `^mecer,.*`, `^mediatek,.*`, `^medion,.*`, `^megachips,.*`, `^mele,.*`, `^melexis,.*`, `^melfas,.*`, `^mellanox,.*`, `^memsensing,.*`, `^memsic,.*`, `^menlo,.*`, `^mentor,.*`, `^meraki,.*`, `^merrii,.*`, `^methode,.*`, `^micrel,.*`, `^microchip,.*`, `^microcrystal,.*`, `^micron,.*`, `^microsoft,.*`, `^microsys,.*`, `^microtips,.*`, `^mikroe,.*`, `^mikrotik,.*`, `^milianke,.*`, `^milkv,.*`, `^miniand,.*`, `^minix,.*`, `^mips,.*`, `^miramems,.*`, `^mitsubishi,.*`, `^mitsumi,.*`, `^mixel,.*`, `^miyoo,.*`, `^mntre,.*`, `^mobileye,.*`, `^modtronix,.*`, `^moortec,.*`, `^mosaixtech,.*`, `^motorcomm,.*`, `^motorola,.*`, `^moxa,.*`, `^mpl,.*`, `^mps,.*`, `^mqmaker,.*`, `^mrvl,.*`, `^mscc,.*`, `^msi,.*`, `^mstar,.*`, `^mti,.*`, `^multi-inno,.*`, `^mundoreader,.*`, `^murata,.*`, `^mxic,.*`, `^mxicy,.*`, `^myir,.*`, `^national,.*`, `^neardi,.*`, `^nec,.*`, `^neofidelity,.*`, `^neonode,.*`, `^netcube,.*`, `^netgear,.*`, `^netlogic,.*`, `^netron-dy,.*`, `^netronix,.*`, `^netxeon,.*`, `^neweast,.*`, `^newhaven,.*`, `^newvision,.*`, `^nexbox,.*`, `^nextthing,.*`, `^ni,.*`, `^nicera,.*`, `^nintendo,.*`, `^nlt,.*`, `^nokia,.*`, `^nordic,.*`, `^nothing,.*`, `^novatech,.*`, `^novatek,.*`, `^novtech,.*`, `^nuclei,.*`, `^numonyx,.*`, `^nutsboard,.*`, `^nuvoton,.*`, `^nvd,.*`, `^nvidia,.*`, `^nxp,.*`, `^oceanic,.*`, `^ocs,.*`, `^oct,.*`, `^okaya,.*`, `^oki,.*`, `^olimex,.*`, `^olpc,.*`, `^oneplus,.*`, `^onething,.*`, `^onie,.*`, `^onion,.*`, `^onnn,.*`, `^ontat,.*`, `^opalkelly,.*`, `^openailab,.*`, `^opencores,.*`, `^openembed,.*`, `^openpandora,.*`, `^openrisc,.*`, `^openwrt,.*`, `^option,.*`, `^oranth,.*`, `^ORCL,.*`, `^orisetech,.*`, `^ortustech,.*`, `^osddisplays,.*`, `^osmc,.*`, `^ouya,.*`, `^overkiz,.*`, `^ovti,.*`, `^oxsemi,.*`, `^ozzmaker,.*`, `^panasonic,.*`, `^parade,.*`, `^parallax,.*`, `^particle,.*`, `^pda,.*`, `^pegatron,.*`, `^pericom,.*`, `^pervasive,.*`, `^phicomm,.*`, `^phontech,.*`, `^phytec,.*`, `^picochip,.*`, `^pine64,.*`, `^pineriver,.*`, `^pixcir,.*`, `^plantower,.*`, `^plathome,.*`, `^plda,.*`, `^plx,.*`, `^ply,.*`, `^pni,.*`, `^pocketbook,.*`, `^polaroid,.*`, `^polyhex,.*`, `^portwell,.*`, `^poslab,.*`, `^pov,.*`, `^powertip,.*`, `^powervr,.*`, `^powkiddy,.*`, `^primeview,.*`, `^primux,.*`, `^probox2,.*`, `^pri,.*`, `^prt,.*`, `^pulsedlight,.*`, `^purism,.*`, `^puya,.*`, `^qca,.*`, `^qcom,.*`, `^qemu,.*`, `^qi,.*`, `^qiaodian,.*`, `^qihua,.*`, `^qishenglong,.*`, `^qnap,.*`, `^quanta,.*`, `^radxa,.*`, `^raidsonic,.*`, `^ralink,.*`, `^ramtron,.*`, `^raspberrypi,.*`, `^raumfeld,.*`, `^raydium,.*`, `^raystar,.*`, `^rda,.*`, `^realtek,.*`, `^relfor,.*`, `^remarkable,.*`, `^renesas,.*`, `^rervision,.*`, `^retronix,.*`, `^revotics,.*`, `^rex,.*`, `^rfdigital,.*`, `^richtek,.*`, `^ricoh,.*`, `^rikomagic,.*`, `^riot,.*`, `^riscv,.*`, `^rockchip,.*`, `^rocktech,.*`, `^rohm,.*`, `^ronbo,.*`, `^ronetix,.*`, `^roofull,.*`, `^roseapplepi,.*`, `^rve,.*`, `^saef,.*`, `^sakurapi,.*`, `^samsung,.*`, `^samtec,.*`, `^sancloud,.*`, `^sandisk,.*`, `^satoz,.*`, `^sbs,.*`, `^schindler,.*`, `^schneider,.*`, `^schulercontrol,.*`, `^sciosense,.*`, `^sdmc,.*`, `^seagate,.*`, `^seeed,.*`, `^seirobotics,.*`, `^semtech,.*`, `^senseair,.*`, `^sensirion,.*`, `^sensortek,.*`, `^sercomm,.*`, `^sff,.*`, `^sgd,.*`, `^sgmicro,.*`, `^sgx,.*`, `^sharp,.*`, `^shift,.*`, `^shimafuji,.*`, `^shineworld,.*`, `^shiratech,.*`, `^si-en,.*`, `^si-linux,.*`, `^sielaff,.*`, `^siemens,.*`, `^sifive,.*`, `^siflower,.*`, `^sigma,.*`, `^sii,.*`, `^sil,.*`, `^silabs,.*`, `^silan,.*`, `^silead,.*`, `^silergy,.*`, `^silex-insight,.*`, `^siliconfile,.*`, `^siliconmitus,.*`, `^silvaco,.*`, `^simtek,.*`, `^sinlinx,.*`, `^sinovoip,.*`, `^sinowealth,.*`, `^sipeed,.*`, `^sirf,.*`, `^sis,.*`, `^sitronix,.*`, `^skov,.*`, `^skyworks,.*`, `^smartfiber,.*`, `^smartlabs,.*`, `^smartrg,.*`, `^smi,.*`, `^smsc,.*`, `^snps,.*`, `^sochip,.*`, `^socionext,.*`, `^solidrun,.*`, `^solomon,.*`, `^somfy,.*`, `^sony,.*`, `^sophgo,.*`, `^sourceparts,.*`, `^spacemit,.*`, `^spansion,.*`, `^sparkfun,.*`, `^spinalhdl,.*`, `^sprd,.*`, `^square,.*`, `^ssi,.*`, `^sst,.*`, `^sstar,.*`, `^st,.*`, `^starfive,.*`, `^starry,.*`, `^startek,.*`, `^starterkit,.*`, `^ste,.*`, `^stericsson,.*`, `^st-ericsson,.*`, `^storlink,.*`, `^storm,.*`, `^storopack,.*`, `^summit,.*`, `^sunchip,.*`, `^sundance,.*`, `^sunplus,.*`, `^SUNW,.*`, `^supermicro,.*`, `^swir,.*`, `^syna,.*`, `^synaptics,.*`, `^synology,.*`, `^synopsys,.*`, `^taiguanck,.*`, `^taos,.*`, `^tbs,.*`, `^tbs-biometrics,.*`, `^tcg,.*`, `^tcl,.*`, `^tcs,.*`, `^tcu,.*`, `^tdo,.*`, `^team-source-display,.*`, `^technexion,.*`, `^technologic,.*`, `^techstar,.*`, `^techwell,.*`, `^teejet,.*`, `^teltonika,.*`, `^tempo,.*`, `^tenda,.*`, `^tenstorrent,.*`, `^terasic,.*`, `^tesla,.*`, `^test,.*`, `^tfc,.*`, `^thead,.*`, `^thine,.*`, `^thingyjp,.*`, `^thundercomm,.*`, `^thwc,.*`, `^ti,.*`, `^tianma,.*`, `^tlm,.*`, `^tmt,.*`, `^topeet,.*`, `^topic,.*`, `^topland,.*`, `^toppoly,.*`, `^topwise,.*`, `^toradex,.*`, `^toshiba,.*`, `^toumaz,.*`, `^tpk,.*`, `^tplink,.*`, `^tpo,.*`, `^tq,.*`, `^transpeed,.*`, `^traverse,.*`, `^tronfy,.*`, `^tronsmart,.*`, `^truly,.*`, `^tsd,.*`, `^turing,.*`, `^tuxedo,.*`, `^tyan,.*`, `^tyhx,.*`, `^u-blox,.*`, `^u-boot,.*`, `^ubnt,.*`, `^ucrobotics,.*`, `^udoo,.*`, `^ufispace,.*`, `^ugoos,.*`, `^ultrapower,.*`, `^uni-t,.*`, `^uniwest,.*`, `^upisemi,.*`, `^urt,.*`, `^usi,.*`, `^usr,.*`, `^ultrarisc,.*`, `^ultratronik,.*`, `^utoo,.*`, `^v3,.*`, `^vaisala,.*`, `^valve,.*`, `^vamrs,.*`, `^variscite,.*`, `^vdl,.*`, `^verisilicon,.*`, `^vertexcom,.*`, `^via,.*`, `^vialab,.*`, `^vicor,.*`, `^videostrong,.*`, `^virtio,.*`, `^virtual,.*`, `^vishay,.*`, `^visionox,.*`, `^vitesse,.*`, `^vivante,.*`, `^vivax,.*`, `^vocore,.*`, `^voipac,.*`, `^voltafield,.*`, `^vot,.*`, `^vscom,.*`, `^vxt,.*`, `^wacom,.*`, `^wanchanglong,.*`, `^wand,.*`, `^waveshare,.*`, `^wd,.*`, `^we,.*`, `^welltech,.*`, `^wetek,.*`, `^wexler,.*`, `^whwave,.*`, `^wi2wi,.*`, `^widora,.*`, `^wiko,.*`, `^wiligear,.*`, `^willsemi,.*`, `^winbond,.*`, `^wingtech,.*`, `^winlink,.*`, `^winsen,.*`, `^winstar,.*`, `^wirelesstag,.*`, `^wits,.*`, `^wlf,.*`, `^wm,.*`, `^wobo,.*`, `^wolfvision,.*`, `^x-powers,.*`, `^xen,.*`, `^xes,.*`, `^xiaomi,.*`, `^xicor,.*`, `^xillybus,.*`, `^xingbangda,.*`, `^xinpeng,.*`, `^xiphera,.*`, `^xlnx,.*`, `^xnano,.*`, `^xunlong,.*`, `^xylon,.*`, `^yadro,.*`, `^yamaha,.*`, `^yes-optoelectronics,.*`, `^yic,.*`, `^yiming,.*`, `^ylm,.*`, `^yna,.*`, `^yones-toptech,.*`, `^ys,.*`, `^ysoft,.*`, `^yuridenki,.*`, `^yuzukihd,.*`, `^zarlink,.*`, `^zealz,.*`, `^zeitec,.*`, `^zidoo,.*`, `^zii,.*`, `^zinitix,.*`, `^zkmagic,.*`, `^zte,.*`, `^zyxel,.*`, `^[a-zA-Z0-9#_][a-zA-Z0-9#+\-._@]{0,63}$`, `^[a-zA-Z0-9+\-._]*@[0-9a-zA-Z,]*$`, `^#.*`, so child bus/controller nodes are part of the binding contract.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

The vendor prefix registry is global infrastructure used by all binding schemas and DTS compatible/property names. It is pulled into dt-schema checks to reject unregistered vendor prefixes and to document deprecated or non-vendor exceptions.

## Risks And Edge Cases
- The registry is intentionally broad; accidental reordering, duplicate prefixes, or unreviewed wildcard patterns can weaken validation for the whole tree.
- Deprecated aliases and non-vendor exceptions must remain for old bindings, but new entries should use real vendor prefixes and stay alphabetized.
- Because `select: true` applies globally, syntax or regex mistakes here can create repository-wide dt-schema noise.

## Test Signals
No inline DTS example is present; validation depends on in-tree DTS users and dt_binding_check schema compilation.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/vendor-prefixes.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/vendor-prefixes.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/vendor-prefixes.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 0 top-level declared propert(ies), 0 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/vendor-prefixes.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/mmio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/mmio.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/mmio.yaml`, a YAML devicetree binding titled "virtio memory mapped devices". It is a virtio transport/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `mmio.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Jean-Philippe Brucker <jean-philippe@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `virtio,mmio`.

Required top-level fields: `compatible`, `reg`, `interrupts`.

Primary declared properties:
- `compatible`: constant `virtio,mmio`
- `reg`: items ?..1
- `dma-coherent`: boolean/standard property admitted by this schema.
- `interrupts`: items ?..1
- `#iommu-cells`: constant `1`; Required when the node corresponds to a virtio-iommu device.
- `iommus`: items ?..1; Required for devices making accesses thru an IOMMU.
- `wakeup-source`: type `boolean`; Required for setting irq of a virtio_mmio device as wakeup source.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties` admits typed child/object extensions, usually for bus children or hub/device subnodes.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

Virtio integration points include the virtio transport layer, PCI or MMIO enumeration, optional IOMMU attachment, DMA coherency flags, interrupt routing, and wakeup signaling.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `iommu@3100`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/mmio.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/mmio.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/mmio.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 7 top-level declared propert(ies), 3 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/mmio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/pci-iommu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/pci-iommu.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/pci-iommu.yaml`, a YAML devicetree binding titled "virtio-iommu device using the virtio-pci transport". It is a virtio transport/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `pci-iommu.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Jean-Philippe Brucker <jean-philippe@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `virtio,pci-iommu`, `pci1af4,1057`.

Required top-level fields: `compatible`, `reg`, `#iommu-cells`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `#iommu-cells`: constant `1`

External schema dependencies: `/schemas/pci/pci-device.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/pci/pci-device.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/pci/pci-device.yaml#`.

Virtio integration points include the virtio transport layer, PCI or MMIO enumeration, optional IOMMU attachment, DMA coherency flags, interrupt routing, and wakeup signaling.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `pcie@40000000, `pcie@50000000, `ethernet`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/pci-iommu.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/pci-iommu.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/pci-iommu.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 3 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/pci-iommu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/virtio-device.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/virtio-device.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/virtio-device.yaml`, a YAML devicetree binding titled "Virtio device". It is a virtio transport/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `virtio-device.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Viresh Kumar <viresh.kumar@linaro.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: Virtio device nodes. "virtio,deviceID", where ID is the virtio device id. The textual representation of ID shall be in lower ca...

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

Virtio integration points include the virtio transport layer, PCI or MMIO enumeration, optional IOMMU attachment, DMA coherency flags, interrupt routing, and wakeup signaling.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `i2c`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/virtio-device.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/virtio-device.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/virtio-device.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 1 top-level declared propert(ies), 1 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/virtio/virtio-device.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/amd,axi-1wire-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/amd,axi-1wire-host.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/amd,axi-1wire-host.yaml`, a YAML devicetree binding titled "AMD AXI 1-wire bus host for programmable logic". It is a 1-Wire bus binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `amd,axi-1wire-host.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Kris Chaplin <kris.chaplin@amd.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `amd,axi-1wire-host`.

Required top-level fields: `compatible`, `reg`, `clocks`, `interrupts`.

Primary declared properties:
- `compatible`: constant `amd,axi-1wire-host`
- `reg`: items ?..1
- `clocks`: items ?..1
- `interrupts`: items ?..1

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

1-Wire integration points include the w1 master subsystem, parent I2C/UART/platform/GPIO providers, optional regulators, and child 1-Wire devices represented as additional nodes where the schema allows them.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `onewire@a0000000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/amd,axi-1wire-host.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/amd,axi-1wire-host.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/amd,axi-1wire-host.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 4 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/amd,axi-1wire-host.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/fsl-imx-owire.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/fsl-imx-owire.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/fsl-imx-owire.yaml`, a YAML devicetree binding titled "Freescale i.MX One wire bus master controller". It is a 1-Wire bus binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `fsl-imx-owire.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Martin Fuzzey <mfuzzey@parkeon.com>.

## Important APIs, Types, And Schema Surface
Accepts 5 compatible string(s): `fsl,imx21-owire`, `fsl,imx27-owire`, `fsl,imx50-owire`, `fsl,imx51-owire`, `fsl,imx53-owire`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `interrupts`: items ?..1
- `clocks`: items ?..1

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

1-Wire integration points include the w1 master subsystem, parent I2C/UART/platform/GPIO providers, optional regulators, and child 1-Wire devices represented as additional nodes where the schema allows them.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `owire@63fa4000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/fsl-imx-owire.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/fsl-imx-owire.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/fsl-imx-owire.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 2 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/fsl-imx-owire.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml`, a YAML devicetree binding titled "Maxim One wire bus master controller". It is a 1-Wire bus binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `maxim,ds2482.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Stefan Wahren <stefan.wahren@chargebyte.com>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `maxim,ds2482`, `maxim,ds2484`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: enum `maxim,ds2482`, `maxim,ds2484`
- `reg`: items ?..1
- `vcc-supply`: boolean/standard property admitted by this schema.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties` admits typed child/object extensions, usually for bus children or hub/device subnodes.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

1-Wire integration points include the w1 master subsystem, parent I2C/UART/platform/GPIO providers, optional regulators, and child 1-Wire devices represented as additional nodes where the schema allows them.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `onewire@18`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 2 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-gpio.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-gpio.yaml`, a YAML devicetree binding titled "Bitbanged GPIO 1-Wire Bus". It is a 1-Wire bus binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `w1-gpio.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Daniel Mack <zonque@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `w1-gpio`.

Required top-level fields: `compatible`, `gpios`.

Primary declared properties:
- `compatible`: constant `w1-gpio`
- `gpios`: items 1..?
- `linux,open-drain`: type `boolean`; If specified, the data pin is considered in open-drain mode.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties` admits typed child/object extensions, usually for bus children or hub/device subnodes.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

1-Wire integration points include the w1 master subsystem, parent I2C/UART/platform/GPIO providers, optional regulators, and child 1-Wire devices represented as additional nodes where the schema allows them.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `onewire`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-gpio.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-gpio.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-gpio.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 2 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml`, a YAML devicetree binding titled "UART 1-Wire Bus". It is a 1-Wire bus binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `w1-uart.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Christoph Winklhofer <cj.winklhofer@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `w1-uart`.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: constant `w1-uart`
- `reset-bps`: default `9600`; The baud rate for the 1-Wire reset and presence detect.
- `write-0-bps`: default `115200`; The baud rate for the 1-Wire write-0 cycle.
- `write-1-bps`: default `115200`; The baud rate for the 1-Wire write-1 and read cycle.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties` admits typed child/object extensions, usually for bus children or hub/device subnodes.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

1-Wire integration points include the w1 master subsystem, parent I2C/UART/platform/GPIO providers, optional regulators, and child 1-Wire devices represented as additional nodes where the schema allows them.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `onewire`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 1 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/airoha,en7581-wdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/airoha,en7581-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/airoha,en7581-wdt.yaml`, a YAML devicetree binding titled "Airoha EN7581 Watchdog Timer". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `airoha,en7581-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Christian Marangi <ansuelsmth@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `airoha,an7583-wdt`, `airoha,en7581-wdt`.

Required top-level fields: `compatible`, `reg`, `clocks`, `clock-names`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `clocks`: items ?..1; BUS clock (timer ticks at half the BUS clock)
- `clock-names`: constant `bus`

External schema dependencies: `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `watchdog@1fbf0100`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/airoha,en7581-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/airoha,en7581-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/airoha,en7581-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/airoha,en7581-wdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/allwinner,sun4i-a10-wdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/allwinner,sun4i-a10-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/allwinner,sun4i-a10-wdt.yaml`, a YAML devicetree binding titled "Allwinner A10 Watchdog". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `allwinner,sun4i-a10-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 12 compatible string(s): `allwinner,sun4i-a10-wdt`, `allwinner,sun6i-a31-wdt`, `allwinner,sun50i-a64-wdt`, `allwinner,sun50i-a100-wdt`, `allwinner,sun50i-h6-wdt`, `allwinner,sun50i-h616-wdt`, `allwinner,sun50i-r329-wdt`, `allwinner,sun50i-r329-wdt-reset`, `allwinner,suniv-f1c100s-wdt`, `allwinner,sun20i-d1-wdt`, plus 2 more.

Required top-level fields: `compatible`, `reg`, `clocks`, `interrupts`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `clocks`: items 1..?
- `interrupts`: items ?..1

External schema dependencies: `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `watchdog.yaml#`.

The schema contains 1 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/allwinner,sun4i-a10-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/allwinner,sun4i-a10-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/allwinner,sun4i-a10-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 1 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/allwinner,sun4i-a10-wdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/alphascale,asm9260-wdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/alphascale,asm9260-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/alphascale,asm9260-wdt.yaml`, a YAML devicetree binding titled "Alphascale asm9260 Watchdog timer". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `alphascale,asm9260-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Oleksij Rempel <linux@rempel-privat.de>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `alphascale,asm9260-wdt`.

Required top-level fields: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`.

Primary declared properties:
- `compatible`: constant `alphascale,asm9260-wdt`
- `reg`: items ?..1
- `clocks`: declared schema property.
- `clock-names`: declared schema property.
- `interrupts`: items ?..1
- `resets`: items ?..1
- `reset-names`: declared schema property.
- `alphascale,mode`: refers to `/schemas/types.yaml#/definitions/string`; enum `hw`, `sw`, `debug`; default `hw`; Specifies the reset mode of operation. If set to sw, then reset is handled via interrupt request, if set to debug, then it does...

External schema dependencies: `/schemas/types.yaml#/definitions/string`, `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/string`, `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/string`, `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `watchdog@80048000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/alphascale,asm9260-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/alphascale,asm9260-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/alphascale,asm9260-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 8 top-level declared propert(ies), 5 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/alphascale,asm9260-wdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml`, a YAML devicetree binding titled "Meson GXBB SoCs Watchdog timer". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `amlogic,meson-gxbb-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 5 compatible string(s): `amlogic,meson-gxbb-wdt`, `amlogic,t7-wdt`, `amlogic,a4-wdt`, `amlogic,c3-wdt`, `amlogic,s4-wdt`.

Required top-level fields: `compatible`, `reg`, `clocks`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `clocks`: items ?..1; A phandle to the clock of this PHY

External schema dependencies: `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 3 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson6-wdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson6-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson6-wdt.yaml`, a YAML devicetree binding titled "Amlogic Meson6 SoCs Watchdog timer". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `amlogic,meson6-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Neil Armstrong <neil.armstrong@linaro.org>, Martin Blumenstingl <martin.blumenstingl@googlemail.com>.

## Important APIs, Types, And Schema Surface
Accepts 4 compatible string(s): `amlogic,meson6-wdt`, `amlogic,meson8-wdt`, `amlogic,meson8b-wdt`, `amlogic,meson8m2-wdt`.

Required top-level fields: `compatible`, `interrupts`, `reg`.

Primary declared properties:
- `compatible`: declared schema property.
- `interrupts`: items ?..1
- `reg`: items ?..1

External schema dependencies: `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `watchdog@c1109900`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson6-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson6-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson6-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 3 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson6-wdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/apple,wdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/apple,wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/apple,wdt.yaml`, a YAML devicetree binding titled "Apple SoC Watchdog". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `apple,wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Sven Peter <sven@svenpeter.dev>.

## Important APIs, Types, And Schema Surface
Accepts 10 compatible string(s): `apple,t6020-wdt`, `apple,t8103-wdt`, `apple,s5l8960x-wdt`, `apple,t7000-wdt`, `apple,s8000-wdt`, `apple,t8010-wdt`, `apple,t8015-wdt`, `apple,t8112-wdt`, `apple,t6000-wdt`, `apple,wdt`.

Required top-level fields: `compatible`, `reg`, `clocks`, `interrupts`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `clocks`: items ?..1
- `interrupts`: items ?..1

External schema dependencies: `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `watchdog@50000000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/apple,wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/apple,wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/apple,wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/apple,wdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sbsa-gwdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sbsa-gwdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sbsa-gwdt.yaml`, a YAML devicetree binding titled "SBSA (Server Base System Architecture) Generic Watchdog". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `arm,sbsa-gwdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Fu Wei <fu.wei@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `arm,sbsa-gwdt`.

Required top-level fields: `compatible`, `reg`, `interrupts`.

Primary declared properties:
- `compatible`: constant `arm,sbsa-gwdt`
- `reg`: declared schema property.
- `interrupts`: items ?..1; The Watchdog Signal 0 (WS0) SPI (Shared Peripheral Interrupt)

External schema dependencies: `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sbsa-gwdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sbsa-gwdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sbsa-gwdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 3 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sbsa-gwdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml`, a YAML devicetree binding titled "ARM AMBA Primecell SP805 Watchdog". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `arm,sp805.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Viresh Kumar <vireshk@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `arm,sp805`, `arm,primecell`.

Required top-level fields: `compatible`, `reg`, `clocks`, `clock-names`.

Primary declared properties:
- `compatible`: declared schema property.
- `interrupts`: items ?..1
- `reg`: items ?..1
- `clocks`: items ?..2; Clocks driving the watchdog timer hardware. The first clock is used for the actual watchdog counter. The second clock drives th...
- `clock-names`: declared schema property.
- `resets`: items ?..1; WDOGRESn input reset signal for sp805 module.

External schema dependencies: `/schemas/watchdog/watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/watchdog/watchdog.yaml#`.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/watchdog/watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `watchdog@66090000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,twd-wdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,twd-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,twd-wdt.yaml`, a YAML devicetree binding titled "ARM Timer-Watchdog Watchdog". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `arm,twd-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Rob Herring <robh@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 3 compatible string(s): `arm,cortex-a9-twd-wdt`, `arm,cortex-a5-twd-wdt`, `arm,arm11mp-twd-wdt`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: enum `arm,cortex-a9-twd-wdt`, `arm,cortex-a5-twd-wdt`, `arm,arm11mp-twd-wdt`
- `reg`: items ?..1
- `interrupts`: items ?..1
- `clocks`: items ?..1

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `watchdog@2c000620`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,twd-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,twd-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,twd-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 2 required field(s), 0 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,twd-wdt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml`, a YAML devicetree binding titled "ARM Secure Monitor Call based watchdog". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `arm-smc-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Julius Werner <jwerner@chromium.org>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `arm,smc-wdt`.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: enum `arm,smc-wdt`
- `arm,smc-id`: refers to `/schemas/types.yaml#/definitions/uint32`; The ATF smc function id used by the firmware. Defaults to 0x82003D06 if unset.

External schema dependencies: `/schemas/types.yaml#/definitions/uint32`, `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint32`, `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint32`, `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 2 top-level declared propert(ies), 1 required field(s), 2 external reference(s), and 0 conditional branch(es).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml -->
