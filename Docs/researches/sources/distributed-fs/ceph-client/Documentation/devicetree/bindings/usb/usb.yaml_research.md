# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml`, a YAML devicetree binding titled "Generic USB Controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `$nodename`: declared schema property.
- `phys`: List of all the USB PHYs on this HCD
- `phy-names`: Name specifier for the USB PHY
- `usb-phy`: refers to `/schemas/types.yaml#/definitions/phandle-array`; deprecated; List of all the USB PHYs on this HCD to be accepted by the legacy USB Physical Layer subsystem.
- `phy_type`: refers to `/schemas/types.yaml#/definitions/string`; enum `utmi`, `utmi_wide`, `ulpi`, `serial`, `hsic`; Tells USB controllers that we want to configure the core to support a UTMI+ PHY with an 8- or 16-bit interface if UTMI+ is sele...
- `maximum-speed`: refers to `/schemas/types.yaml#/definitions/string`; enum `low-speed`, `full-speed`, `high-speed`, `super-speed`, `super-speed-plus`, `super-speed-plus-gen2x1`, `super-speed-plus-gen1x2`, `super-speed-plus-gen2x2`; Tells USB controllers we want to work up to a certain speed. In case this isn't passed via DT, USB controllers should default t...

External schema dependencies: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.

## Test Signals
No inline DTS example is present; validation depends on in-tree DTS users and dt_binding_check schema compilation.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 0 required field(s), 2 external reference(s), and 0 conditional branch(es).
