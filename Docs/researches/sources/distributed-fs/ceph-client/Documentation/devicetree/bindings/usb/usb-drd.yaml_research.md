# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml`, a YAML devicetree binding titled "Generic USB OTG Controller". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-drd.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `otg-rev`: refers to `/schemas/types.yaml#/definitions/uint32`; enum `256`, `288`, `304`, `512`; Tells usb driver the release number of the OTG and EH supplement with which the device and its descriptors are compliant, in bi...
- `dr_mode`: refers to `/schemas/types.yaml#/definitions/string`; enum `host`, `peripheral`, `otg`; default `otg`; Tells Dual-Role USB controllers that we want to work on a particular mode. In case this attribute isn't passed via DT, USB DRD ...
- `hnp-disable`: type `boolean`; Tells OTG controllers we want to disable OTG HNP. Normally HNP is the basic function of real OTG except you want it to be a srp...
- `srp-disable`: type `boolean`; Tells OTG controllers we want to disable OTG SRP. SRP is optional for OTG device.
- `adp-disable`: type `boolean`; Tells OTG controllers we want to disable OTG ADP. ADP is optional for OTG device.
- `usb-role-switch`: Indicates that the device is capable of assigning the USB data role (USB host or USB device) for a given USB connector, such as...
- `role-switch-default-mode`: refers to `/schemas/types.yaml#/definitions/string`; enum `host`, `peripheral`; default `peripheral`; Indicates if usb-role-switch is enabled, the device default operation mode of controller while usb role is USB_ROLE_NONE.

External schema dependencies: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-drd.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 7 top-level declared propert(ies), 0 required field(s), 2 external reference(s), and 0 conditional branch(es).
