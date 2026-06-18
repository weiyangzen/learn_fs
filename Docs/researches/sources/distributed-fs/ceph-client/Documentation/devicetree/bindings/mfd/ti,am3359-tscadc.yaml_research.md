# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,am3359-tscadc.yaml

Purpose: Schema for the TI AM3359 touchscreen controller and ADC MFD, describing the shared TSCADC hardware block and its ADC, touchscreen, or magnetic reader child functions.

Important schema surface and control flow: compatible values identify the AM3359 TSCADC family; `reg`, `interrupts`, `clocks`, `clock-names = "fck"`, and child function nodes are part of the contract. Optional DMA channels are named and ordered, and `power-domains` is allowed for SoCs that gate the block. The `adc`, `tsc`, and `mag` children are referenced through their dedicated schemas.

State, dependencies, and integration: DT state describes one MMIO and IRQ resource shared by multiple MFD children plus optional DMA and power-domain wiring. Dependencies include clock, DMA, power-domain, IIO ADC, input touchscreen, and TI child bindings. Risks include enabling both child functions without matching hardware muxing, DMA name/order mismatches, and missing functional clock names. Test signals are binding validation, child schema validation, runtime probe of `ti_am335x_tscadc` and ADC/touchscreen children, and input/IIO data flow tests.
