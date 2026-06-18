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
