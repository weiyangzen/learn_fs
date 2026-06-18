# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml`, a YAML devicetree binding titled "UART 1-Wire Bus". It is a 1-Wire bus binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `w1-uart.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Christoph Winklhofer <cj.winklhofer@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `w1-uart`.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: constant `w1-uart`
- `reset-bps`: default `9600`; The baud rate for the 1-Wire reset and presence detect.
- `write-0-bps`: default `115200`; The baud rate for the 1-Wire write-0 cycle.
- `write-1-bps`: default `115200`; The baud rate for the 1-Wire write-1 and read cycle.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties` admits typed child/object extensions, usually for bus children or hub/device subnodes.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: No external `$ref` dependencies beyond the devicetree core metaschema..

1-Wire integration points include the w1 master subsystem, parent I2C/UART/platform/GPIO providers, optional regulators, and child 1-Wire devices represented as additional nodes where the schema allows them.

## Risks And Edge Cases
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `onewire`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/w1-uart.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 4 top-level declared propert(ies), 1 required field(s), 0 external reference(s), and 0 conditional branch(es).
