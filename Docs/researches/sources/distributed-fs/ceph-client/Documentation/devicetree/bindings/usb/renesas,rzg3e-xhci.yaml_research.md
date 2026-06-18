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
