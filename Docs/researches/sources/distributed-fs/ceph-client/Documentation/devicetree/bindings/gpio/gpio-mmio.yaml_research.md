<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mmio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mmio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Generic MMIO GPIO. Some simple GPIO controllers may consist of a single data register or a pair of set/clear-bit registers. Such controllers are common for glue logic in FPGAs or ASICs. Commonly, these controllers are accessed over memory-mapped NAND-style parallel busses.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-mmio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Generic MMIO GPIO`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm6345-gpio`, `intel,ixp4xx-expansion-bus-mmio-gpio`, `ni,169445-nand-gpio`, `opencores,gpio`, `wd,mbl-gpio`.
- Top-level required properties: `compatible`, `reg`, `reg-names`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `brcm,bcm6345-gpio`, `intel,ixp4xx-expansion-bus-mmio-gpio`, `ni,169445-nand-gpio`, `opencores,gpio`, `wd,mbl-gpio`.
- `big-endian` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `little-endian` is accepted as a flag/property marker.
- `reg`: A list of registers in the controller. The width of each register is determined by its size. All registers must...; minItems 1; 5 ordered items.
- `reg-names`: maxItems 5; minItems 1.
- `native-endian` is accepted as a flag/property marker.
- `ngpios`: If this property is present the number of usable GPIO lines are restricted to the first 0 .. ngpios lines. This is....
- `no-output`: If this property is present, the controller cannot drive the GPIO lines.; ref `/schemas/types.yaml#/definitions/flag`.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.
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
- References shared schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-mmio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm6345-gpio`, `intel,ixp4xx-expansion-bus-mmio-gpio`, `ni,169445-nand-gpio`, `opencores,gpio`, `wd,mbl-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mmio.yaml -->
