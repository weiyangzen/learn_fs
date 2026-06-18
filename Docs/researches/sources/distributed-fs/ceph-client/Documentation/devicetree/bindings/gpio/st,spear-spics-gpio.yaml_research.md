<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,spear-spics-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,spear-spics-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for ST Microelectronics SPEAr SPI CS GPIO Controller. SPEAr platform provides a provision to control chipselects of ARM PL022 Prime Cell spi controller through its system registers, which otherwise remains under PL022 control. If chipselect remain under PL022 control then they would be released as soon as transfer is over and TxFIFO becomes empty. This is not desired by some of the device protocols above spi which expect (multiple) transfers without releasing their chipselects. Chipselects can be controlled by software by turning them as GPIOs. SPEAr provides another.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/st,spear-spics-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `ST Microelectronics SPEAr SPI CS GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `st,spear-spics-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `st-spics,peripcfg-reg`, `st-spics,sw-enable-bit`, `st-spics,cs-value-bit`, `st-spics,cs-enable-mask`, `st-spics,cs-enable-shift`.
- `compatible`: const `st,spear-spics-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `st-spics,peripcfg-reg`: Offset of the peripcfg register.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st-spics,sw-enable-bit`: Bit offset to enable software chipselect control.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st-spics,cs-value-bit`: Bit offset to drive chipselect low or high.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st-spics,cs-enable-mask`: Bitmask selecting which chipselects to enable.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st-spics,cs-enable-shift`: Bit shift for programming chipselect number.; ref `/schemas/types.yaml#/definitions/uint32`.

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
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/st,spear-spics-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `st,spear-spics-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,spear-spics-gpio.yaml -->
