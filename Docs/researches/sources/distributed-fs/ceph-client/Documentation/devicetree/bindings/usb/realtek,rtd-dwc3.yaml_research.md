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
