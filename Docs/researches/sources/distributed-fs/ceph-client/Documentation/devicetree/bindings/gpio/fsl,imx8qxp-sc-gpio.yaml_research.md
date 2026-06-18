<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,imx8qxp-sc-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,imx8qxp-sc-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO driver over IMX SCU firmware API. This module provides the standard interface to control the resource pins in SCU domain on i.MX8 platforms.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/fsl,imx8qxp-sc-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO driver over IMX SCU firmware API`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,imx8qxp-sc-gpio`.
- Top-level required properties: `compatible`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `fsl,imx8qxp-sc-gpio`.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.

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
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/fsl,imx8qxp-sc-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,imx8qxp-sc-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,imx8qxp-sc-gpio.yaml -->
