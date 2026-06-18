# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/raspberrypi,rp1-gpio.yaml

## Purpose
This schema covers the Raspberry Pi RP1 GPIO, pinconf, pinmux, and interrupt-controller submodule. It validates three register banks, GPIO and interrupt provider cells, and nested pin state nodes. Source title: RaspberryPi RP1 GPIO/Pinconf/Pinmux Controller submodule. Description signal from the file: The RP1 chipset is a Multi Function Device containing, among other sub-peripherals, a gpio/pinconf/mux controller whose 54 pins are grouped into 3 banks. It works also as an interrupt controller for those gpios.

## Important APIs, Types, and Schema Surface
- Lines read: 231.
- Compatible contract: raspberrypi,rp1-gpio. Top-level required properties: reg, compatible, #gpio-cells, gpio-controller, interrupts, #interrupt-cells, interrupt-controller. Important top-level properties found in the schema: reg, interrupts, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-ranges, gpio-line-names. Child-node patterns: -state$, -pins$. Function enum sample: alt0, alt1, alt2, alt3, alt4, gpio, alt6, alt7, alt8, none, aaud, dcd0, dpi, dsi0_te_ext, dsi1_te_ext, dsr0 plus 46 more. Referenced schemas: #/$defs/raspberrypi-rp1-state, pincfg-node.yaml#, pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation requires three register bank ranges, GPIO and interrupt-controller provider declarations, interrupt lines, and `gpio-ranges`. State nodes use `$defs/raspberrypi-rp1-state` to combine generic pinmux/pinconf properties with RP1 pin numbering and function constraints.

## State and Persistence Behavior
Persistent state is the RP1 MFD submodule topology: bank registers, GPIO numbering across 54 pins, interrupt provider cells, and named pinctrl states used by RP1 clients.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Bank count, interrupt count, and GPIO range mismatches are the main hazards. Because RP1 is an MFD submodule, integration tests should validate the parent bus representation and child pin state references together.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/raspberrypi,rp1-gpio.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
