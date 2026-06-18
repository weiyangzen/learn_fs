<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mxs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mxs.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Freescale MXS GPIO controller. The Freescale MXS GPIO controller is part of MXS PIN controller. The GPIOs are organized in port/bank, each port consists of 32 GPIOs. As the GPIO controller is embedded in the PIN controller and all the GPIO ports share the same IO space with PIN controller, the GPIO node will be represented as sub-nodes of MXS pinctrl node.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-mxs.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Freescale MXS GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,imx23-pinctrl`, `fsl,imx28-pinctrl`.
- Top-level required properties: `compatible`, `reg`, `#address-cells`, `#size-cells`.
- `compatible`: 2 ordered items.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `reg`: maxItems 1.
- Pattern child/property schemas: `^(?!gpio@)[^@]+@[0-9]+$`, `^gpio@[0-9]+$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-mxs.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,imx23-pinctrl`, `fsl,imx28-pinctrl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mxs.yaml -->
