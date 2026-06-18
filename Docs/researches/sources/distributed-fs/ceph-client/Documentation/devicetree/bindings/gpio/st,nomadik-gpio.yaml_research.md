<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,nomadik-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,nomadik-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Nomadik GPIO controller. The Nomadik GPIO driver handles Nomadik SoC GPIO blocks. This block has also been called ST STA2X11. On the Nomadik platform, this driver is intertwined with pinctrl-nomadik.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/st,nomadik-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Nomadik GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `st,nomadik-gpio`, `mobileye,eyeq5-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `#gpio-cells`, `gpio-controller`, `interrupt-controller`, `gpio-bank`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: enum `st,nomadik-gpio`, `mobileye,eyeq5-gpio`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `gpio-bank`: System-wide GPIO bank index.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st,supports-sleepmode`: Whether the controller can sleep or not.; ref `/schemas/types.yaml#/definitions/flag`.
- `clocks`: maxItems 1.
- `gpio-ranges`: maxItems 1.
- `ngpios`: constraints via minimum, maximum.
- `resets`: maxItems 1.
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
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/st,nomadik-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `st,nomadik-gpio`, `mobileye,eyeq5-gpio`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,nomadik-gpio.yaml -->
