<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cdns,gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cdns,gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Cadence GPIO Controller. Cadence GPIO Controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/cdns,gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Cadence GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `cdns,gpio-r1p02`, `axiado,ax3000-gpio`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `gpio-controller`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `ngpios`: constraints via minimum, maximum.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: - First cell is the GPIO line number. - Second cell is flags as defined in <dt-bindings/gpio/gpio.h>, only...; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: - First cell is the GPIO line number used as IRQ. - Second cell is the trigger type, as defined in...; const `2`.
- `interrupts`: maxItems 1.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/cdns,gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `cdns,gpio-r1p02`, `axiado,ax3000-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cdns,gpio.yaml -->
