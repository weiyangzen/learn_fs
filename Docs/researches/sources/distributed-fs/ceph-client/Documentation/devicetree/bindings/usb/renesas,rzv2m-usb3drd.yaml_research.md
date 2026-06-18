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
