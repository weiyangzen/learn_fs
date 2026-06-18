<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-delay.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-delay.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO delay controller. This binding describes an electrical setup where setting an GPIO output is delayed by some external setup, e.g. RC circuit. +----------+ +-----------+ | | VCC_B | | | | | | | | | VCC_A _ | | | GPIO | | | R | Consumer | |controller| ___ |_| | | | | | | | | | | [IOx|-------| |--+-----|-----+ | | | |___| | | input | | | | | | +----------+ --- C +-----------+ --- | - GND If the input on the consumer is controlled by an open-drain signal attached to an RC circuit the ramp-up delay is not under control of the GPIO.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-delay.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO delay controller`.
- Top-level required properties: `compatible`, `#gpio-cells`, `gpio-controller`, `gpios`.
- `compatible`: const `gpio-delay`.
- `#gpio-cells`: Specifies the pin, ramp-up and ramp-down delays. The delays are specified in microseconds.; const `3`.
- `gpios`: Array of GPIOs which output signal change is delayed; maxItems 32; minItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 32; minItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-delay.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-delay.yaml -->
