<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,stmpe-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,stmpe-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for STMicroelectonics Port Expander (STMPE) GPIO Block. STMicroelectronics Port Expander (STMPE) is a series of slow bus controllers for various expanded peripherals such as GPIO, keypad, touchscreen, ADC, PWM or rotator. It can contain one or several different peripherals connected to SPI or I2C. These bindings pertain to the GPIO portions of these expanders.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/st,stmpe-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `STMicroelectonics Port Expander (STMPE) GPIO Block`.
- Compatible strings or compatible constants enumerated by the schema include `st,stmpe-gpio`.
- Top-level required properties: `compatible`, `#gpio-cells`, `#interrupt-cells`, `gpio-controller`, `interrupt-controller`.
- `compatible`: const `st,stmpe-gpio`.
- `#gpio-cells`: const `2`.
- `#interrupt-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 24; minItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `st,norequest-mask`: A bitmask of GPIO lines that cannot be requested because for for example not being connected to anything on the...; ref `/schemas/types.yaml#/definitions/uint32`.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.

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

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/st,stmpe-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `st,stmpe-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,stmpe-gpio.yaml -->
