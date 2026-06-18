<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-davinci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-davinci.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO controller for Davinci and keystone devices. GPIO controller for Davinci and keystone devices

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-davinci.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO controller for Davinci and keystone devices`.
- Compatible strings or compatible constants enumerated by the schema include `ti,k2g-gpio`, `ti,am654-gpio`, `ti,j721e-gpio`, `ti,am64-gpio`, `ti,keystone-gpio`, `ti,dm6441-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `ti,ngpio`, `ti,davinci-gpio-unbanked`, `clocks`, `clock-names`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-reserved-ranges` is accepted as a flag/property marker.
- `gpio-line-names`: strings describing the names of each gpio line.; maxItems 144; minItems 1.
- `#gpio-cells`: first cell is the pin number and second cell is used to specify optional parameters (unused).; const `2`.
- `interrupts`: The interrupts are specified as per the interrupt parent. Only banked or unbanked IRQs are supported at a time. If...; maxItems 100; minItems 1.
- `ti,ngpio`: The number of GPIO pins supported consecutively.; ref `/schemas/types.yaml#/definitions/uint32`.
- `ti,davinci-gpio-unbanked`: The number of GPIOs that have an individual interrupt line to processor.; ref `/schemas/types.yaml#/definitions/uint32`.
- `clocks`: maxItems 1.
- `clock-names`: const `gpio`.
- `interrupt-controller` is accepted as a flag/property marker.
- `power-domains`: maxItems 1.
- `#interrupt-cells`: const `2`.
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
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `power-domains`.
- Includes 3 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-davinci.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ti,k2g-gpio`, `ti,am654-gpio`, `ti,j721e-gpio`, `ti,am64-gpio`, `ti,keystone-gpio`, `ti,dm6441-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-davinci.yaml -->
