## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinctrl-single.yaml

### Purpose
`pinctrl-single.yaml` describes generic pin controllers where one register controls one or more pins, including `pinctrl-single` and several TI padconf variants. It provides the binding for register-width, mask, function-mask, optional interrupt controller behavior, and child state nodes that program packed register values.

### Important Schema APIs
The controller accepts `pinctrl-single` plus TI padconf compatibles such as `ti,am437-padconf`, `ti,am62l-padconf`, `ti,am654-padconf`, `ti,dra7-padconf`, and OMAP padconf variants. Important properties include `reg`, `#pinctrl-cells`, `pinctrl-single,register-width`, `pinctrl-single,function-mask`, `pinctrl-single,bit-per-mux`, `pinctrl-single,drive-strength`, optional interrupt properties, and child nodes carrying `pinctrl-single,pins`, `pinctrl-single,bits`, `pinctrl-single,bias-pullup`, `pinctrl-single,bias-pulldown`, drive-strength arrays, slew-rate arrays, power-source arrays, low-power-mode arrays, and wakeup-enable arrays.

### Validation Flow
The top-level schema applies `pinctrl.yaml`, validates the compatible choice, register sizing, and provider cell count, then evaluates child nodes under `patternProperties`. Child node validation closes unknown keys with `additionalProperties: false`, so misspelled `pinctrl-single,*` properties should fail early. The schema uses typed arrays to validate the register offset/value/mask tuples consumed by the generic pinctrl-single driver.

### State And Persistence
The schema itself is static. DTS data persists register offsets and values that the Linux `pinctrl-single` driver writes into controller registers for each selected state. Optional interrupt-controller properties persist GPIO/pin interrupt mapping for controllers that multiplex interrupt status into the same register block.

### Dependencies And Integration Points
It depends on `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, and `/schemas/types.yaml`. Integration is with the generic Linux pinctrl-single driver and TI SoC pad configuration bindings that use the same register programming model.

### Risks
Packed offset/value arrays are hard for schema to validate semantically: a tuple can be well typed but target a reserved register or set illegal bits. `#pinctrl-cells` and function mask mismatches can break client references. Interrupt-related properties must stay consistent with the hardware and the generic IRQ domain setup.

### Test Signals
Run `dt_binding_check` for this file and compile DTS examples using both `pinctrl-single,pins` and `pinctrl-single,bits`. Runtime signals are successful state selection through the pinctrl core, correct register writes, and interrupt mapping tests on controllers advertising interrupt support.
