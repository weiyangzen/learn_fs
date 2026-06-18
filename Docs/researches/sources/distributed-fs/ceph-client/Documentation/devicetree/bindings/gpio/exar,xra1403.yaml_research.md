<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/exar,xra1403.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/exar,xra1403.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for XRA1403 16-bit GPIO Expander with Reset Input. The XRA1403 is an 16-bit GPIO expander with an SPI interface. Features available: - Individually programmable inputs: - Internal pull-up resistors - Polarity inversion - Individual interrupt enable - Rising edge and/or Falling edge interrupt - Input filter - Individually programmable outputs: - Output Level Control - Output Three-State Control

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/exar,xra1403.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `XRA1403 16-bit GPIO Expander with Reset Input`.
- Compatible strings or compatible constants enumerated by the schema include `exar,xra1403`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: const `exar,xra1403`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `reset-gpios`: Control line for the device reset..
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `reset-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/exar,xra1403.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `exar,xra1403`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/exar,xra1403.yaml -->
