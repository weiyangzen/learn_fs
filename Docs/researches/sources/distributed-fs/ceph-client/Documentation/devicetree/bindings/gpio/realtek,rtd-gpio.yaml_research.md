<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,rtd-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,rtd-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Realtek DHC GPIO controller. The GPIO controller is designed for the Realtek DHC (Digital Home Center) RTD series SoC family, which are high-definition media processor SoCs.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/realtek,rtd-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Realtek DHC GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `realtek,rtd1295-misc-gpio`, `realtek,rtd1295-iso-gpio`, `realtek,rtd1315e-iso-gpio`, `realtek,rtd1319-iso-gpio`, `realtek,rtd1319d-iso-gpio`, `realtek,rtd1395-iso-gpio`, `realtek,rtd1619-iso-gpio`, `realtek,rtd1619b-iso-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `gpio-ranges`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `realtek,rtd1295-misc-gpio`, `realtek,rtd1295-iso-gpio`, `realtek,rtd1315e-iso-gpio`, `realtek,rtd1319-iso-gpio`, `realtek,rtd1319d-iso-gpio`, `realtek,rtd1395-iso-gpio`, `realtek,rtd1619-iso-gpio`, `realtek,rtd1619b-iso-gpio`.
- `reg`: 2 ordered items.
- `interrupts`: 2 ordered items.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.

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
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/realtek,rtd-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `realtek,rtd1295-misc-gpio`, `realtek,rtd1295-iso-gpio`, `realtek,rtd1315e-iso-gpio`, `realtek,rtd1319-iso-gpio`, `realtek,rtd1319d-iso-gpio`, `realtek,rtd1395-iso-gpio`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,rtd-gpio.yaml -->
