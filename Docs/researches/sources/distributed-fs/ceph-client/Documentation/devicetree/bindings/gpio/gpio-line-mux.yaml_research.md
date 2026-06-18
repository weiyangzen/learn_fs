<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-line-mux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-line-mux.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO line mux. A GPIO controller to provide virtual GPIOs for a 1-to-many input-only mapping backed by a single shared GPIO and a multiplexer. A simple illustrated example is: +----- A IN / <-----o------- B / |\ | | +----- C | | \ | | +--- D | | M1 M0 MUX CONTROL M1 M0 IN 0 0 A 0 1 B 1 0 C 1 1 D This can be used in case a real GPIO is connected to multiple inputs and controlled by a multiplexer, and another subsystem/driver does not work directly with the multiplexer subsystem.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-line-mux.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO line mux`.
- Top-level required properties: `compatible`, `gpio-controller`, `gpio-line-mux-states`, `mux-controls`, `muxed-gpios`.
- `compatible`: const `gpio-line-mux`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-line-mux-states`: Mux states corresponding to the virtual GPIOs.; ref `/schemas/types.yaml#/definitions/uint32-array`.
- `gpio-line-names` is accepted as a flag/property marker.
- `mux-controls`: Phandle to the multiplexer to control access to the GPIOs.; maxItems 1.
- `ngpios` is explicitly rejected in this schema branch.
- `muxed-gpios`: GPIO which is the '1' in 1-to-many and is shared by the virtual GPIOs and controlled via the mux.; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32-array`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-line-mux.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-line-mux.yaml -->
