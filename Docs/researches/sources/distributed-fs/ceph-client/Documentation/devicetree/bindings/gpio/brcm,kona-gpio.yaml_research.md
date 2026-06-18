<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,kona-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,kona-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Broadcom Kona family GPIO controller. The Broadcom GPIO Controller IP can be configured prior to synthesis to support up to 8 banks of 32 GPIOs where each bank has its own IRQ. The GPIO controller only supports edge, not level, triggering of interrupts.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/brcm,kona-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom Kona family GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm11351-gpio`, `brcm,bcm21664-gpio`, `brcm,bcm23550-gpio`, `brcm,kona-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `#gpio-cells`, `#interrupt-cells`, `gpio-controller`, `interrupt-controller`.
- `compatible`: 2 ordered items.
- `reg`: maxItems 1.
- `interrupts`: The interrupt outputs from the controller. There is one GPIO interrupt per GPIO bank. The number of interrupts...; maxItems 6; minItems 4.
- `#gpio-cells`: const `2`.
- `#interrupt-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.
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
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/brcm,kona-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm11351-gpio`, `brcm,bcm21664-gpio`, `brcm,bcm23550-gpio`, `brcm,kona-gpio`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,kona-gpio.yaml -->
