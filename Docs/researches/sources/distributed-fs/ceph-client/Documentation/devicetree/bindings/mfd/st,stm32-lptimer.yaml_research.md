# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stm32-lptimer.yaml

Purpose: Schema for STM32 low-power timer blocks, an MFD-style timer node that can expose PWM, counter, trigger/timer, and encoder-related child functions.

Important schema surface and control flow: the node requires `compatible`, `reg`, `clocks`, and `clock-names = "mux"`. Optional properties include one interrupt, DMA-style address/size cells, `wakeup-source`, access controllers, power domains, and child nodes `pwm`, `counter`, and `timer`. Child nodes reference PWM, counter, and timer-trigger semantics with required compatibles and cell counts. Pattern properties cover encoder child nodes with unit addresses.

State, dependencies, and integration: DT state configures a low-power timer MMIO block, clock input, optional wake IRQ, and child-function registration for STM32 timer drivers. Dependencies include clock, interrupt, power-domain, access-controller, PWM, counter, and timer-trigger bindings. Risks include missing child address cells when timer subnodes use `reg`, exposing unsupported child functions on a given SoC instance, and wakeup-source without a valid interrupt. Test signals are `dt_binding_check`, child schema validation, and runtime probe of PWM/counter/timer-trigger devices under the LPTIM parent.
