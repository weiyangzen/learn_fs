<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,rcar-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,rcar-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Renesas R-Car General-Purpose Input/Output Ports (GPIO). Renesas R-Car General-Purpose Input/Output Ports (GPIO)

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/renesas,rcar-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Renesas R-Car General-Purpose Input/Output Ports (GPIO)`.
- Compatible strings or compatible constants enumerated by the schema include `renesas,gpio-r8a7778`, `renesas,gpio-r8a7779`, `renesas,rcar-gen1-gpio`, `renesas,gpio-r8a7742`, `renesas,gpio-r8a7743`, `renesas,gpio-r8a7744`, `renesas,gpio-r8a7745`, `renesas,gpio-r8a77470`, `renesas,gpio-r8a7790`, `renesas,gpio-r8a7791`, `renesas,gpio-r8a7792`, `renesas,gpio-r8a7793`, ....
- Top-level required properties: `compatible`, `reg`, `interrupts`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `interrupt-controller`, `#interrupt-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `power-domains`: maxItems 1.
- `resets`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `gpio-ranges`: maxItems 1.
- `gpio-reserved-ranges`: maxItems 8; minItems 1.
- Pattern child/property schemas: `^.*$`.
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
- Integrates with provider/consumer property `resets`.
- Integrates with provider/consumer property `power-domains`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/renesas,rcar-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `renesas,gpio-r8a7778`, `renesas,gpio-r8a7779`, `renesas,rcar-gen1-gpio`, `renesas,gpio-r8a7742`, `renesas,gpio-r8a7743`, `renesas,gpio-r8a7744`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,rcar-gpio.yaml -->
