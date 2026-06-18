<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max31910.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max31910.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Maxim MAX3191x GPIO serializer. Maxim MAX3191x GPIO serializer

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/maxim,max31910.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Maxim MAX3191x GPIO serializer`.
- Compatible strings or compatible constants enumerated by the schema include `maxim,max31910`, `maxim,max31911`, `maxim,max31912`, `maxim,max31913`, `maxim,max31953`, `maxim,max31963`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `maxim,max31910`, `maxim,max31911`, `maxim,max31912`, `maxim,max31913`, `maxim,max31953`, `maxim,max31963`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `#daisy-chained-devices`: Number of chips in the daisy-chain..
- `maxim,modesel-gpios`: GPIO pins to configure modesel of each chip. The number of GPIOs must equal "#daisy-chained-devices" (if each chip....
- `maxim,fault-gpios`: GPIO pins to read fault of each chip. The number of GPIOs must equal "#daisy-chained-devices" or 1..
- `maxim,db0-gpios`: GPIO pins to configure debounce of each chip. The number of GPIOs must equal "#daisy-chained-devices" or 1..
- `maxim,db1-gpios`: GPIO pins to configure debounce of each chip. The number of GPIOs must equal "maxim,db0-gpios"..
- `maxim,modesel-8bit`: Boolean whether the modesel pin of the chips is pulled high (8-bit mode). Use this if the modesel pin is hardwired....
- `maxim,ignore-undervoltage`: Boolean whether to ignore undervoltage alarms signaled by the "maxim,fault-gpios" or by the status byte (in 16-bit....
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
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/maxim,max31910.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `maxim,max31910`, `maxim,max31911`, `maxim,max31912`, `maxim,max31913`, `maxim,max31953`, `maxim,max31963`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max31910.yaml -->
