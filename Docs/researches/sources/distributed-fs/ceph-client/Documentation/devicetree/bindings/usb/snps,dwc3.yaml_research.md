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
