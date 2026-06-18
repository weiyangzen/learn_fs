<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nuvoton,sgpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nuvoton,sgpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Nuvoton SGPIO controller. This SGPIO controller is for NUVOTON NPCM7xx and NPCM8xx SoC and detailed information is in the NPCM7XX/8XX SERIAL I/O EXPANSION INTERFACE section. Nuvoton NPCM7xx SGPIO module is combines a serial to parallel IC (HC595) and a parallel to serial IC (HC165). Clock is a division of the APB3 clock. This interface has 4 pins (D_out , D_in, S_CLK, LDSH). NPCM7xx/NPCM8xx have two sgpio modules. Each module can support up to 64 output pins, and up to 64 input pins, the pin is only for GPI or GPO. GPIO pins can be.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nuvoton,sgpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Nuvoton SGPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `nuvoton,npcm750-sgpio`, `nuvoton,npcm845-sgpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `nuvoton,input-ngpios`, `nuvoton,output-ngpios`, `clocks`.
- `compatible`: enum `nuvoton,npcm750-sgpio`, `nuvoton,npcm845-sgpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `nuvoton,input-ngpios`: The numbers of GPIO's exposed. GPIO lines are only for GPI.; ref `/schemas/types.yaml#/definitions/uint32`.
- `nuvoton,output-ngpios`: The numbers of GPIO's exposed. GPIO lines are only for GPO.; ref `/schemas/types.yaml#/definitions/uint32`.

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
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nuvoton,sgpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nuvoton,npcm750-sgpio`, `nuvoton,npcm845-sgpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nuvoton,sgpio.yaml -->
