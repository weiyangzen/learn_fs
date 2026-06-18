<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,sgpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,sgpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Aspeed SGPIO controller. This SGPIO controller is for ASPEED AST2400, AST2500, AST2600 and AST2700 SoC, AST2700 have two sgpio master both with 256 pins, AST2600 have two sgpio master one with 128 pins another one with 80 pins, AST2500/AST2400 have one sgpio master with 80 pins. Each of the Serial GPIO pins can be programmed to support the following options - Support interrupt option for each input port and various interrupt sensitivity option (level-high, level-low, edge-high, edge-low) - Support reset tolerance option for each output.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/aspeed,sgpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Aspeed SGPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `aspeed,ast2400-sgpio`, `aspeed,ast2500-sgpio`, `aspeed,ast2600-sgpiom`, `aspeed,ast2700-sgpiom`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `ngpios`, `clocks`, `bus-frequency`.
- `compatible`: enum `aspeed,ast2400-sgpio`, `aspeed,ast2500-sgpio`, `aspeed,ast2600-sgpiom`, `aspeed,ast2700-sgpiom`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 256; minItems 160.
- `#gpio-cells`: const `2`.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `ngpios` is accepted as a flag/property marker.
- `bus-frequency` is accepted as a flag/property marker.

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
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/aspeed,sgpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `aspeed,ast2400-sgpio`, `aspeed,ast2500-sgpio`, `aspeed,ast2600-sgpiom`, `aspeed,ast2700-sgpiom`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,sgpio.yaml -->
