# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml`, a YAML devicetree binding titled "Meson GXBB SoCs Watchdog timer". It is a watchdog timer binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `amlogic,meson-gxbb-wdt.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, And Schema Surface
Accepts 5 compatible string(s): `amlogic,meson-gxbb-wdt`, `amlogic,t7-wdt`, `amlogic,a4-wdt`, `amlogic,c3-wdt`, `amlogic,s4-wdt`.

Required top-level fields: `compatible`, `reg`, `clocks`.

Primary declared properties:
- `compatible`: declared schema property.
- `reg`: items ?..1
- `clocks`: items ?..1; A phandle to the clock of this PHY

External schema dependencies: `watchdog.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `watchdog.yaml#`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`unevaluatedProperties: false` closes the composed schema after referenced schemas are evaluated.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `watchdog.yaml#`.

Watchdog integration points include the Linux watchdog core, timeout properties inherited from `watchdog.yaml` when referenced, clock/reset providers, interrupt controllers, secure firmware calls, and SoC reset behavior.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 1 inline example block(s).

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/watchdog/amlogic,meson-gxbb-wdt.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 3 top-level declared propert(ies), 3 required field(s), 1 external reference(s), and 0 conditional branch(es).
