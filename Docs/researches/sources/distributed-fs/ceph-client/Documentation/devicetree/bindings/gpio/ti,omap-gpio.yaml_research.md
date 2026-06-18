<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,omap-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,omap-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for OMAP GPIO controller. The general-purpose interface combines general-purpose input/output (GPIO) banks. Each GPIO banks provides up to 32 dedicated general-purpose pins with input and output capabilities; interrupt generation in active mode and wake-up request generation in idle mode upon the detection of external events.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/ti,omap-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `OMAP GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `ti,omap2-gpio`, `ti,omap3-gpio`, `ti,omap4-gpio`, `ti,am4372-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: maxItems 1.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 32; minItems 1.
- `ti,gpio-always-on`: Indicates if a GPIO bank is always powered and will never lose its logic state.; ref `/schemas/types.yaml#/definitions/flag`.
- `ti,hwmods`: Name of the hwmod associated with the GPIO. Needed on some legacy OMAP SoCs which have not been converted to the...; ref `/schemas/types.yaml#/definitions/string`.
- `ti,no-reset-on-init`: Do not reset on init. Used with ti,hwmods on some legacy OMAP SoCs which have not been converted to the ti,sysc...; ref `/schemas/types.yaml#/definitions/flag`.
- Pattern child/property schemas: `^(.+-hog(-[0-9]+)?)$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/ti,omap-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ti,omap2-gpio`, `ti,omap3-gpio`, `ti,omap4-gpio`, `ti,am4372-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,omap-gpio.yaml -->
