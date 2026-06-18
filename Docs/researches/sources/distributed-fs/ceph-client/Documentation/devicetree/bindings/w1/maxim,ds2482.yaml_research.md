# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml`, a YAML devicetree binding titled "Maxim One wire bus master controller". It is a 1-Wire bus binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `maxim,ds2482.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Stefan Wahren <stefan.wahren@chargebyte.com>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `maxim,ds2482`, `maxim,ds2484`.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `compatible`: enum `maxim,ds2482`, `maxim,ds2484`
- `reg`: items ?..1
- `vcc-supply`: boolean/standard property admitted by this schema.

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
Contains 1 inline example block(s), including node(s) `onewire@18`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/w1/maxim,ds2482.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 2 required field(s), 0 external reference(s), and 0 conditional branch(es).
