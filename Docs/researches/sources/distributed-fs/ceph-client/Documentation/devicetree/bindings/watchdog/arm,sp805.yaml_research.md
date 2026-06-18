# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml`, a YAML devicetree binding titled "ARM AMBA Primecell SP805 Watchdog". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `arm,sp805.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Viresh Kumar <vireshk@kernel.org>.

## Important APIs, Types, And Schema Surface
Accepts 2 compatible string(s): `arm,sp805`, `arm,primecell`.

Required top-level fields: `compatible`, `reg`, `clocks`, `clock-names`.

Primary declared properties:
- `compatible`: declared schema property.
- `interrupts`: items ?..1
- `reg`: items ?..1
- `clocks`: items ?..2; Clocks driving the watchdog timer hardware. The first clock is used for the actual watchdog counter. The second clock drives th...
- `clock-names`: declared schema property.
- `resets`: items ?..1; WDOGRESn input reset signal for sp805 module.

External schema dependencies: `/schemas/watchdog/watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/watchdog/watchdog.yaml#`.

A custom `select` block controls when the schema applies, which is important for broad fallback compatibles that could otherwise match unrelated nodes.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/watchdog/watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s), including node(s) `watchdog@66090000`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm,sp805.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 6 top-level declared propert(ies), 4 required field(s), 1 external reference(s), and 0 conditional branch(es).
