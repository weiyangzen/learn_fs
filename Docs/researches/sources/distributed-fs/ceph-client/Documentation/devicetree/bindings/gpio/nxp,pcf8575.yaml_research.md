<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,pcf8575.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,pcf8575.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for PCF857x-compatible I/O expanders. The PCF857x-compatible chips have "quasi-bidirectional" I/O lines that can be driven high by a pull-up current source or driven low to ground. This combines the direction and output level into a single bit per line, which can't be read back. We can't actually know at initialization time whether a line is configured (a) as output and driving the signal low/high, or (b) as input and reporting a low/high value, without knowing the last value written since the chip came out of reset (if any). The only reliable.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nxp,pcf8575.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `PCF857x-compatible I/O expanders`.
- Compatible strings or compatible constants enumerated by the schema include `maxim,max7328`, `maxim,max7329`, `nxp,pca8574`, `nxp,pca8575`, `nxp,pca9670`, `nxp,pca9671`, `nxp,pca9672`, `nxp,pca9673`, `nxp,pca9674`, `nxp,pca9675`, `nxp,pcf8574`, `nxp,pcf8574a`, ....
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `maxim,max7328`, `maxim,max7329`, `nxp,pca8574`, `nxp,pca8575`, `nxp,pca9670`, `nxp,pca9671`, `nxp,pca9672`, `nxp,pca9673`, ....
- `reg`: maxItems 1.
- `gpio-line-names`: maxItems 16; minItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: The first cell is the GPIO number and the second cell specifies GPIO flags, as defined in...; const `2`.
- `lines-initial-states`: Bitmask that specifies the initial state of each line. When a bit is set to zero, the corresponding line will be...; ref `/schemas/types.yaml#/definitions/uint32`.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `wakeup-source` is accepted as a flag/property marker.
- `reset-gpios`: GPIO controlling the (reset active LOW) RESET# pin. The active polarity of the GPIO must translate to the low...; maxItems 1.
- Pattern child/property schemas: `^(.+-hog(-[0-9]+)?)$`.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `reset-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nxp,pcf8575.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `maxim,max7328`, `maxim,max7329`, `nxp,pca8574`, `nxp,pca8575`, `nxp,pca9670`, `nxp,pca9671`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,pcf8575.yaml -->
