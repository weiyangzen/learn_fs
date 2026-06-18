<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/kontron,sl28cpld-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/kontron,sl28cpld-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO driver for the sl28cpld board management controller. This module is part of the sl28cpld multi-function device. For more details see ../embedded-controller/kontron,sl28cpld.yaml. There are three flavors of the GPIO controller, one full featured input/output with interrupt support (kontron,sl28cpld-gpio), one output-only (kontron,sl28-gpo) and one input-only (kontron,sl28-gpi). Each controller supports 8 GPIO lines.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/kontron,sl28cpld-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO driver for the sl28cpld board management controller`.
- Compatible strings or compatible constants enumerated by the schema include `kontron,sl28cpld-gpio`, `kontron,sl28cpld-gpi`, `kontron,sl28cpld-gpo`.
- Top-level required properties: `compatible`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `kontron,sl28cpld-gpio`, `kontron,sl28cpld-gpi`, `kontron,sl28cpld-gpo`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#interrupt-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 8; minItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/kontron,sl28cpld-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `kontron,sl28cpld-gpio`, `kontron,sl28cpld-gpi`, `kontron,sl28cpld-gpo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/kontron,sl28cpld-gpio.yaml -->
