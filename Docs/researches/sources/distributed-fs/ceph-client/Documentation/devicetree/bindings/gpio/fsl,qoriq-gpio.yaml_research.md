<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,qoriq-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,qoriq-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Freescale MPC512x/MPC8xxx/QorIQ/Layerscape GPIO controller. Freescale MPC512x/MPC8xxx/QorIQ/Layerscape GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/fsl,qoriq-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Freescale MPC512x/MPC8xxx/QorIQ/Layerscape GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,mpc5121-gpio`, `fsl,mpc5125-gpio`, `fsl,mpc8314-gpio`, `fsl,mpc8349-gpio`, `fsl,mpc8572-gpio`, `fsl,mpc8610-gpio`, `fsl,pq3-gpio`, `fsl,ls1021a-gpio`, `fsl,ls1028a-gpio`, `fsl,ls1043a-gpio`, `fsl,ls1046a-gpio`, `fsl,ls1088a-gpio`, ....
- Top-level required properties: `compatible`, `reg`, `interrupts`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `gpio-line-names`: maxItems 32; minItems 1.
- `little-endian`: GPIO registers are used as little endian. If not present registers are used as big endian by default.; ref `/schemas/types.yaml#/definitions/flag`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/flag`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/fsl,qoriq-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,mpc5121-gpio`, `fsl,mpc5125-gpio`, `fsl,mpc8314-gpio`, `fsl,mpc8349-gpio`, `fsl,mpc8572-gpio`, `fsl,mpc8610-gpio`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,qoriq-gpio.yaml -->
