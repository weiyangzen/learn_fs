<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/brcm,bcm4751.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/brcm,bcm4751.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for Broadcom BCM4751 family GNSS Receiver. Broadcom GPS chips can be used over the UART or I2C bus. The UART bus requires CTS/RTS support. The number of the capsule is more elaborate than the compatibles BCM4751 may be printed BCM4751IFBG for example.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/brcm,bcm4751.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom BCM4751 family GNSS Receiver`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm4751`, `brcm,bcm4752`, `brcm,bcm4753`.
- Top-level required properties: `compatible`, `enable-gpios`.
- `compatible`: enum `brcm,bcm4751`, `brcm,bcm4752`, `brcm,bcm4753`.
- `reg`: The I2C Address, not required on UART buses..
- `vdd-auxin-supply`: Main voltage supply, pin name VDD_AUXIN, typically connected directly to a battery such as LiIon 3.8V battery or a....
- `vddio-supply`: IO voltage supply, pin name VDDIO, typically 1.8V.
- `reset-gpios`: An optional active low reset line, should be flagged with GPIO_ACTIVE_LOW.; maxItems 1.
- `enable-gpios`: Enable GPIO line, connected to pins named REGPU or NSTANDBY. If the line is active low such as NSTANDBY, it should....
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
- Integrates with provider/consumer property `enable-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/brcm,bcm4751.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm4751`, `brcm,bcm4752`, `brcm,bcm4753`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/brcm,bcm4751.yaml -->
