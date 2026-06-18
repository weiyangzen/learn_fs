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
