<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max7360-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max7360-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Maxim MAX7360 GPIO controller. Maxim MAX7360 GPIO controller, in MAX7360 chipset https://www.analog.com/en/products/max7360.html The device provides two series of GPIOs, referred here as GPIOs and GPOs. PORT0 to PORT7 pins can be used as GPIOs, with support for interrupts and constant-current mode. These pins will also be used by the rotary encoder and PWM functionalities. COL2 to COL7 pins can be used as GPOs, there is no input capability. COL pins will be partitioned, with the first pins being affected to the keypad functionality and the last.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/maxim,max7360-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Maxim MAX7360 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `maxim,max7360-gpio`, `maxim,max7360-gpo`.
- Top-level required properties: `compatible`, `gpio-controller`.
- `compatible`: enum `maxim,max7360-gpio`, `maxim,max7360-gpo`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `maxim,constant-current-disable`: Bit field, each bit disables constant-current output of the associated GPIO, starting from the least significant...; ref `/schemas/types.yaml#/definitions/uint32`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/maxim,max7360-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `maxim,max7360-gpio`, `maxim,max7360-gpo`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max7360-gpio.yaml -->
