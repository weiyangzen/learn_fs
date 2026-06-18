<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sifive,gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sifive,gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for SiFive GPIO controller. SiFive GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/sifive,gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `SiFive GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `sifive,fu540-c000-gpio`, `sifive,fu740-c000-gpio`, `canaan,k210-gpiohs`, `sifive,gpio0`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `#gpio-cells`, `gpio-controller`.
- `compatible`: 2 ordered items.
- `reg`: maxItems 1.
- `interrupts`: Interrupt mapping, one per GPIO. Maximum 32 GPIOs.; maxItems 32; minItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `#gpio-cells`: const `2`.
- `ngpios`: The number of GPIOs available on the controller implementation. It is 16 for the SiFive SoCs and 32 for the Canaan....
- `gpio-line-names`: maxItems 32; minItems 1.
- `gpio-controller` is accepted as a flag/property marker.
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
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/sifive,gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `sifive,fu540-c000-gpio`, `sifive,fu740-c000-gpio`, `canaan,k210-gpiohs`, `sifive,gpio0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sifive,gpio.yaml -->
