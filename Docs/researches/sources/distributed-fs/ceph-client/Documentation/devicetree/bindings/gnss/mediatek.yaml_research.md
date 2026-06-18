<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/mediatek.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/mediatek.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for Mediatek GNSS Receiver. Mediatek chipsets are used in GNSS-receiver modules produced by several vendors and can use a UART interface.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/mediatek.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Mediatek GNSS Receiver`.
- Compatible strings or compatible constants enumerated by the schema include `globaltop,pa6h`.
- Top-level required properties: `compatible`, `vcc-supply`.
- `compatible`: const `globaltop,pa6h`.
- `vcc-supply`: Main voltage regulator, pin name VCC..
- `reset-gpios`: An optional reset line, with names such as RESET or NRESET. If the line is active low it should be flagged with...; maxItems 1.
- `timepulse-gpios`: Comes with pin names such as PPS1 or 1PPS..
- `gnss-fix-gpios`: GPIO used to determine device position fix state, pin names FIX or 3D_FIX.; maxItems 1.
- `vbackup-supply`: Regulator providing backup voltage, pin names such as VBAT or VBACKUP..
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
- Integrates with provider/consumer property `reset-gpios`.
- Integrates with provider/consumer property `vcc-supply`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/mediatek.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `globaltop,pa6h`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/mediatek.yaml -->
