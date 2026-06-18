<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apm,xgene-gpio-sb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apm,xgene-gpio-sb.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for APM X-Gene Standby GPIO controller. This is a gpio controller in the standby domain. It also supports interrupt in some particular pins which are sourced to its parent interrupt controller as diagram below: +-----------------+ | X-Gene standby | | GPIO controller +------ GPIO_0 +------------+ | | ... | Parent IRQ | EXT_INT_0 | +------ GPIO_8/EXT_INT_0 | controller | (SPI40) | | ... | (GICv2) +--------------+ +------ GPIO_[N+8]/EXT_INT_N | | ... | | | | EXT_INT_N | +------ GPIO_[N+9] | | (SPI[40 + N])| | ... | +--------------+ +------ GPIO_MAX.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/apm,xgene-gpio-sb.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `APM X-Gene Standby GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `apm,xgene-gpio-sb`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `interrupts`, `#interrupt-cells`, `interrupt-controller`.
- `compatible`: const `apm,xgene-gpio-sb`.
- `reg`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `interrupts`: List of interrupt specifiers for EXT_INT_0 through EXT_INT_N. The first entry must correspond to EXT_INT_0..
- `#interrupt-cells`: First cell selects EXT_INT_N (0-N), second cell specifies flags; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `apm,nr-gpios`: Number of GPIO pins; ref `/schemas/types.yaml#/definitions/uint32`.
- `apm,nr-irqs`: Number of interrupt pins; ref `/schemas/types.yaml#/definitions/uint32`.
- `apm,irq-start`: Lowest GPIO pin supporting interrupts; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/apm,xgene-gpio-sb.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `apm,xgene-gpio-sb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apm,xgene-gpio-sb.yaml -->
