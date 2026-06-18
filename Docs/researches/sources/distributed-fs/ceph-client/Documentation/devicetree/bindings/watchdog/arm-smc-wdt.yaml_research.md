# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml`, a YAML devicetree binding titled "ARM Secure Monitor Call based watchdog". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `arm-smc-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Julius Werner <jwerner@chromium.org>.

## Important APIs, Types, And Schema Surface
Accepts 1 compatible string(s): `arm,smc-wdt`.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: enum `arm,smc-wdt`
- `arm,smc-id`: refers to `/schemas/types.yaml#/definitions/uint32`; The ATF smc function id used by the firmware. Defaults to 0x82003D06 if unset.

External schema dependencies: `/schemas/types.yaml#/definitions/uint32`, `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint32`, `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint32`, `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/arm-smc-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 2 top-level declared propert(ies), 1 required field(s), 2 external reference(s), and 0 conditional branch(es).
