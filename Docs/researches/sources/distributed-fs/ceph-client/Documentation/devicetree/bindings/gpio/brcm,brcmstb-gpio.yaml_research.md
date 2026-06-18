<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,brcmstb-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,brcmstb-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Broadcom STB "UPG GIO" GPIO controller. The controller's registers are organized as sets of eight 32-bit registers with each set controlling a bank of up to 32 pins. A single interrupt is shared for all of the banks handled by the controller.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/brcm,brcmstb-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom STB "UPG GIO" GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm7445-gpio`, `brcm,brcmstb-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `brcm,gpio-bank-widths`.
- `compatible`: 2 ordered items.
- `reg`: Define the base and range of the I/O address space containing the brcmstb GPIO controller registers; maxItems 1.
- `#gpio-cells`: The first cell is the pin number (within the controller's pin space), and the second is used for the following:...; const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `brcm,gpio-bank-widths`: Number of GPIO lines for each bank. Number of elements must correspond to number of banks suggested by the 'reg'...; ref `/schemas/types.yaml#/definitions/uint32-array`.
- `interrupts`: The interrupt shared by all GPIO lines for this controller.; maxItems 1.
- `#interrupt-cells`: The first cell is the GPIO number, the second should specify flags. The following subset of flags is supported: -...; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 128; minItems 1.
- `wakeup-source`: GPIOs for this controller can be used as a wakeup source.

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
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/brcm,brcmstb-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm7445-gpio`, `brcm,brcmstb-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,brcmstb-gpio.yaml -->
