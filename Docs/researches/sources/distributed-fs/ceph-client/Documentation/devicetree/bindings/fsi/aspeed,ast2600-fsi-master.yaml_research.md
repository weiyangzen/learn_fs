<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2600-fsi-master.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2600-fsi-master.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for Aspeed FSI master. The AST2600 and later contain two identical FSI masters. They share a clock and have a separate interrupt line and output pins.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/aspeed,ast2600-fsi-master.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Aspeed FSI master`.
- Compatible strings or compatible constants enumerated by the schema include `aspeed,ast2600-fsi-master`, `aspeed,ast2700-fsi-master`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `interrupts`.
- `compatible`: enum `aspeed,ast2600-fsi-master`, `aspeed,ast2700-fsi-master`.
- `clocks`: maxItems 1.
- `cfam-reset-gpios`: Output GPIO pin for CFAM reset; maxItems 1.
- `fsi-routing-gpios`: Output GPIO pin for setting the FSI mux (internal or cabled); maxItems 1.
- `fsi-mux-gpios`: Input GPIO pin for detecting the desired FSI mux state; maxItems 1.
- `interrupts`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fsi-controller.yaml#`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/aspeed,ast2600-fsi-master.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `aspeed,ast2600-fsi-master`, `aspeed,ast2700-fsi-master`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2600-fsi-master.yaml -->
