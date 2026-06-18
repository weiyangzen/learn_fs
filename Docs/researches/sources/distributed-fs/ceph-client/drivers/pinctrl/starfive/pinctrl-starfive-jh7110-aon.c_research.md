# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110-aon.c

## Purpose
This file supplies the JH7110 always-on pinctrl instance: its pin list, MMIO register layout, GPIO IRQ register bases, pad-config range, and platform-driver binding. It delegates common pinctrl/GPIO/IRQ/PM behavior to `pinctrl-starfive-jh7110.c`.

## Important APIs, types, and functions
Constants define four always-on GPIOs, 37 saved registers, and AON register offsets. `jh7110_aon_pins[]` lists TESTEN, RGPIO0-3, RSTN, and GMAC0 pins. `jh7110_aon_set_one_pin_mux()` only calls `jh7110_set_gpiomux()` when the pin is one of the AON GPIOs and function is GPIO. `jh7110_aon_get_padcfg_base()` exposes pad config only for pins before `PAD_GMAC0_MDC`. `jh7110_aon_irq_handler()` dispatches masked status bits across the four GPIOs. `jh7110_aon_init_hw()` masks, clears, and enables AON GPIO interrupts. `jh7110_aon_pinctrl_info` is the `jh7110_pinctrl_soc_info` consumed by the common probe.

## Control flow
The platform driver matches `starfive,jh7110-aon-pinctrl` and passes `jh7110_aon_pinctrl_info` through `of_device_get_match_data()` to the common probe. During mux operations, only GPIO-function requests for the first four pins update generic GPIO mux registers; non-GPIO functions are represented by the pinmux encoding but require no extra AON function-select register in this file. IRQ handling reads `JH7110_AON_GPIOMIS` and forwards active pins to the gpiochip IRQ domain.

## State and persistence behavior
The file itself has no mutable software state. The common driver allocates `saved_regs[37]` when sleep PM is enabled and restores the AON register prefix on resume. Hardware state includes AON DOEN/DOUT/GPI/GPIOIN, IRQ registers, and the pad config register block starting at `0x30`.

## Dependencies and integration points
It depends on JH7110 DT binding pin numbers, the common JH7110 header, and the common exported `jh7110_pinctrl_probe()`, `jh7110_set_gpiomux()`, `jh7110_from_irq_desc()`, and PM ops. It integrates as a separate platform driver from the SYS controller and provides only four gpiochip lines even though the pinctrl pin list includes more non-GPIO pads.

## Risks
`JH7110_AON_GPIORIS` and `JH7110_AON_GPIOMIS` share offset `0x28`, so assumptions about raw versus masked status should be checked against hardware documentation. AON interrupt clear uses a two-write sequence through common ack/mask_ack and init paths; missed or sticky interrupts are possible if clear polarity is wrong. Pad configuration is unavailable for GMAC0 pins by design, so pinconf get may return success with no data via common fallback behavior.

## Test signals
Probe tests should verify four GPIOs register for `starfive,jh7110-aon-pinctrl`, pinctrl lists all AON pins, and suspend/resume restores the first 37 registers. Runtime tests should cover RGPIO input/output, bias/input-enable pinconf on RGPIO pins, IRQ dispatch for all four GPIOs, and no padconf writes for GMAC0 pins.
