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
