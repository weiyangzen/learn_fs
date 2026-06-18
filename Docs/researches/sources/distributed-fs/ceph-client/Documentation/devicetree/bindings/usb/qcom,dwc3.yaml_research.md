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
