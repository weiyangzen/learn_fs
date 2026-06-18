<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,bcm63xx-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,bcm63xx-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Broadcom BCM63xx GPIO controller. Bindings for Broadcom's BCM63xx memory-mapped GPIO controllers. These bindings can be used on any BCM63xx SoC. However, BCM6338 and BCM6345 are the only ones which don't need a pinctrl driver. BCM6338 have 8-bit data and dirout registers, where GPIO state can be read and/or written, and the direction changed from input to output. BCM6318, BCM6328, BCM6358, BCM6362, BCM6368 and BCM63268 have 32-bit data and dirout registers, where GPIO state can be read and/or written, and the direction changed from input to output.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/brcm,bcm63xx-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom BCM63xx GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm6318-gpio`, `brcm,bcm6328-gpio`, `brcm,bcm6358-gpio`, `brcm,bcm6362-gpio`, `brcm,bcm6368-gpio`, `brcm,bcm63268-gpio`.
- Top-level required properties: `compatible`, `reg`, `reg-names`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `brcm,bcm6318-gpio`, `brcm,bcm6328-gpio`, `brcm,bcm6358-gpio`, `brcm,bcm6362-gpio`, `brcm,bcm6368-gpio`, `brcm,bcm63268-gpio`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-ranges`: maxItems 1.
- `native-endian` is accepted as a flag/property marker.
- `reg`: maxItems 2.
- `reg-names`: 2 ordered items.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/brcm,bcm63xx-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm6318-gpio`, `brcm,bcm6328-gpio`, `brcm,bcm6358-gpio`, `brcm,bcm6362-gpio`, `brcm,bcm6368-gpio`, `brcm,bcm63268-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,bcm63xx-gpio.yaml -->
