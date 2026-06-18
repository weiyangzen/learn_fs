<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-pca95xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-pca95xx.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for NXP PCA95xx I2C GPIO multiplexer. Bindings for the family of I2C GPIO multiplexers/expanders: NXP PCA95xx, Maxim MAX73xx

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-pca95xx.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NXP PCA95xx I2C GPIO multiplexer`.
- Compatible strings or compatible constants enumerated by the schema include `toradex,ecgpiol16`, `nxp,pcal6416`, `diodes,pi4ioe5v6534q`, `nxp,pcal6534`, `exar,xra1202`, `maxim,max7310`, `maxim,max7312`, `maxim,max7313`, `maxim,max7315`, `maxim,max7319`, `maxim,max7320`, `maxim,max7321`, ....
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-line-names`: maxItems 40; minItems 1.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `reset-gpios`: GPIO specification for the RESET input. This is an active low signal to the PCA953x. Not valid for Maxim MAX732x...; maxItems 1.
- `vcc-supply`: Optional power supply. Not valid for Maxim MAX732x devices..
- `wakeup-source`: ref `/schemas/types.yaml#/definitions/flag`.
- Pattern child/property schemas: `^(hog-[0-9]+|.+-hog(-[0-9]+)?)$`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
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
- References shared schemas: `/schemas/types.yaml#/definitions/flag`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `reset-gpios`.
- Integrates with provider/consumer property `vcc-supply`.
- Includes 4 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-pca95xx.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `toradex,ecgpiol16`, `nxp,pcal6416`, `diodes,pi4ioe5v6534q`, `nxp,pcal6534`, `exar,xra1202`, `maxim,max7310`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-pca95xx.yaml -->
