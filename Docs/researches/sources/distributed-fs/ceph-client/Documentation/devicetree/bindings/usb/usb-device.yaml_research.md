# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml`, a YAML devicetree binding titled "Generic USB Device". It is a generic USB bus/device binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb-device.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Greg Kroah-Hartman <gregkh@linuxfoundation.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: `reg`.

Primary declared properties:
- `compatible`: Device nodes or combined nodes. "usbVID,PID", where VID is the vendor id and PID the product id. The textual representation of ...
- `reg`: the number of the USB hub port or the USB host-controller port to which this device is attached.
- `#address-cells`: enum `1`, `2`; should be 1 for hub nodes with device nodes, should be 2 for device nodes with interface nodes.
- `#size-cells`: constant `0`

Pattern properties / child-node contracts: `^interface@[0-9a-f]{1,2}(,[0-9a-f]{1,2})$`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Pattern child nodes are validated with `^interface@[0-9a-f]{1,2}(,[0-9a-f]{1,2})$`, so child bus/controller nodes are part of the binding contract.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Child-node pattern schemas mean parent and child validation must stay synchronized; a valid wrapper can still fail because the nested controller/hub/port node violates its referenced schema.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `hub@1, `device@2, `device@3, `interface@0`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb-device.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 1 required field(s), 0 external reference(s), and 0 conditional branch(es).
