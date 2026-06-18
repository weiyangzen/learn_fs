# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml`, a YAML devicetree binding titled "Generic USB Host Controller". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-hcd.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: No top-level `required` list; requirements are inherited, conditional, or intentionally minimal..

Primary declared properties:
- `companion`: refers to `/schemas/types.yaml#/definitions/phandle`; Phandle of a companion device
- `tpl-support`: type `boolean`; Indicates if the Targeted Peripheral List is supported for given targeted hosts (non-PC hosts).
- `#address-cells`: constant `1`
- `#size-cells`: constant `0`

Pattern properties / child-node contracts: `^.*@[0-9a-f]{1,2}$`.

External schema dependencies: `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb.yaml#`.

Pattern child nodes are validated with `^.*@[0-9a-f]{1,2}$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-device.yaml`, `usb.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.

## Test Signals
Contains 1 inline example block(s), including node(s) `hub@1`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-hcd.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 0 required field(s), 3 external reference(s), and 0 conditional branch(es).
