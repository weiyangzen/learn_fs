<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/delta,tn48m-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/delta,tn48m-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Delta Networks TN48M CPLD GPIO controller. This module is part of the Delta TN48M multi-function device. For more details see ../mfd/delta,tn48m-cpld.yaml. Delta TN48M has an onboard Lattice CPLD that is used as an GPIO expander. It provides 12 pins in total, they are input-only or ouput-only type.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/delta,tn48m-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Delta Networks TN48M CPLD GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `delta,tn48m-gpo`, `delta,tn48m-gpi`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `delta,tn48m-gpo`, `delta,tn48m-gpi`.
- `reg`: maxItems 1.
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
- Integrates with provider/consumer property `reg`.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/delta,tn48m-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `delta,tn48m-gpo`, `delta,tn48m-gpi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/delta,tn48m-gpio.yaml -->
