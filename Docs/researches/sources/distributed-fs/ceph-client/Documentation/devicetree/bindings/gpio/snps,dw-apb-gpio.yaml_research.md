<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/snps,dw-apb-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/snps,dw-apb-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Synopsys DesignWare APB GPIO controller. Synopsys DesignWare GPIO controllers have a configurable number of ports, each of which are intended to be represented as child nodes with the generic GPIO-controller properties as described in this bindings file.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/snps,dw-apb-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Synopsys DesignWare APB GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `snps,dw-apb-gpio`.
- Top-level required properties: `compatible`, `reg`, `#address-cells`, `#size-cells`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: const `snps,dw-apb-gpio`.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `reg`: maxItems 1.
- `clocks`: minItems 1; 2 ordered items.
- `clock-names`: minItems 1; 2 ordered items.
- `resets`: maxItems 1.
- Pattern child/property schemas: `^gpio-(port|controller)@[0-9a-f]+$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/snps,dw-apb-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `snps,dw-apb-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/snps,dw-apb-gpio.yaml -->
