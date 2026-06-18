<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pl061-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pl061-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for ARM PL061 GPIO controller. ARM PL061 GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/pl061-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `ARM PL061 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `arm,pl061`, `arm,primecell`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `#gpio-cells`, `gpio-controller`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: 2 ordered items.
- `reg`: maxItems 1.
- `interrupts`: constraints via oneOf.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `clock-names` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.
- `gpio-ranges`: maxItems 8; minItems 1.

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
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/pl061-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `arm,pl061`, `arm,primecell`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pl061-gpio.yaml -->
