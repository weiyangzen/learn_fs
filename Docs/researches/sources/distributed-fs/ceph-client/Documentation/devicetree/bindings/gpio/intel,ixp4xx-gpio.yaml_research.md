<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/intel,ixp4xx-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/intel,ixp4xx-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Intel IXP4xx XScale Networking Processors GPIO Controller. This GPIO controller is found in the Intel IXP4xx processors. It supports 16 GPIO lines. The interrupt portions of the GPIO controller is hierarchical. The synchronous edge detector is part of the GPIO block, but the actual enabling/disabling of the interrupt line is done in the main IXP4xx interrupt controller which has a 1-to-1 mapping for the first 12 GPIO lines to 12 system interrupts. The remaining 4 GPIO lines can not be used for receiving interrupts. The interrupt parent of this GPIO controller must be the.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/intel,ixp4xx-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Intel IXP4xx XScale Networking Processors GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `intel,ixp4xx-gpio`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`.
- `compatible`: const `intel,ixp4xx-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `intel,ixp4xx-gpio14-clkout`: If defined, enables clock output on GPIO 14 instead of GPIO..
- `intel,ixp4xx-gpio15-clkout`: If defined, enables clock output on GPIO 15 instead of GPIO..

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
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/intel,ixp4xx-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `intel,ixp4xx-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/intel,ixp4xx-gpio.yaml -->
