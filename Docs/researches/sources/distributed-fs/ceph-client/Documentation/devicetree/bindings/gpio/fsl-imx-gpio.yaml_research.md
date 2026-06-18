<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl-imx-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl-imx-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Freescale i.MX/MXC GPIO controller. Freescale i.MX/MXC GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/fsl-imx-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Freescale i.MX/MXC GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,imx1-gpio`, `fsl,imx21-gpio`, `fsl,imx31-gpio`, `fsl,imx35-gpio`, `fsl,imx7d-gpio`, `fsl,imx27-gpio`, `fsl,imx25-gpio`, `fsl,imx50-gpio`, `fsl,imx51-gpio`, `fsl,imx53-gpio`, `fsl,imx6q-gpio`, `fsl,imx6sl-gpio`, ....
- Top-level required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `#gpio-cells`, `gpio-controller`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: Should be the port interrupt shared by all 32 pins, if one number. If two numbers, the first one is the interrupt...; maxItems 2; minItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `power-domains`: maxItems 1.
- Pattern child/property schemas: `^(hog-[0-9]+|.+-hog(-[0-9]+)?)$`.

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
- Integrates with provider/consumer property `power-domains`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/fsl-imx-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,imx1-gpio`, `fsl,imx21-gpio`, `fsl,imx31-gpio`, `fsl,imx35-gpio`, `fsl,imx7d-gpio`, `fsl,imx27-gpio`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl-imx-gpio.yaml -->
