<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-stp-xway.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-stp-xway.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Lantiq SoC Serial To Parallel (STP) GPIO controller. The Serial To Parallel (STP) is found on MIPS based Lantiq socs. It is a peripheral controller used to drive external shift register cascades. At most 3 groups of 8 bits can be driven. The hardware is able to allow the DSL modem and Ethernet PHYs to drive some bytes of the cascade automatically.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-stp-xway.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Lantiq SoC Serial To Parallel (STP) GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `lantiq,gpio-stp-xway`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: const `lantiq,gpio-stp-xway`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: The first cell is the pin number and the second cell is used to specify consumer flags.; const `2`.
- `lantiq,shadow`: The default value that we shall assume as already set on the shift register cascade.; ref `/schemas/types.yaml#/definitions/uint32`.
- `lantiq,groups`: Set the 3 bit mask to select which of the 3 groups are enabled in the shift register cascade.; ref `/schemas/types.yaml#/definitions/uint32`.
- `lantiq,dsl`: The dsl core can control the 2 LSBs of the gpio cascade. This 2 bit property can enable this feature.; ref `/schemas/types.yaml#/definitions/uint32`.
- `lantiq,rising`: Use rising instead of falling edge for the shift register..
- Pattern child/property schemas: `^lantiq,phy[1-4]$`.

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
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-stp-xway.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lantiq,gpio-stp-xway`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-stp-xway.yaml -->
