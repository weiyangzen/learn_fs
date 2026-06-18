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
