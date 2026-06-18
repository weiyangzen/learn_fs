<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/u-blox,neo-6m.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/u-blox,neo-6m.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for u-blox GNSS receiver. The u-blox GNSS receivers can use UART, DDC (I2C), SPI and USB interfaces.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/u-blox,neo-6m.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `u-blox GNSS receiver`.
- Compatible strings or compatible constants enumerated by the schema include `u-blox,neo-6m`, `u-blox,neo-8`, `u-blox,neo-m8`, `u-blox,neo-m9`.
- Top-level required properties: `compatible`, `vcc-supply`.
- `compatible`: constraints via oneOf.
- `reg`: The DDC Slave Address, SPI chip select address, the number of the USB hub port or the USB host-controller port to....
- `reset-gpios`: maxItems 1.
- `safeboot-gpios`: maxItems 1.
- `vcc-supply`: Main voltage regulator.
- `u-blox,extint-gpios`: GPIO connected to the "external interrupt" input pin; maxItems 1.
- `v-bckp-supply`: Backup voltage regulator.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates a serial or platform GNSS receiver node so the GNSS subsystem can bind transport, regulators, reset lines, and optional backup/enable controls consistently.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The DT node records hardware wiring and optional regulator/reset/enable policy; live receiver state, fix data, and protocol state are handled by GNSS/serdev drivers.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `gnss-common.yaml#`, `/schemas/serial/serial-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `reset-gpios`.
- Integrates with provider/consumer property `vcc-supply`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/u-blox,neo-6m.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `u-blox,neo-6m`, `u-blox,neo-8`, `u-blox,neo-m8`, `u-blox,neo-m9`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/u-blox,neo-6m.yaml -->
