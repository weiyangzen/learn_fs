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
