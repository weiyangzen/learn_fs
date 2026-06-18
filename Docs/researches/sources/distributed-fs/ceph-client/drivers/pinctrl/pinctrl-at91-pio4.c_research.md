# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91-pio4.c

Purpose: Implements the newer Atmel/Microchip PIO4 pinctrl plus GPIO controller for SAMA5D2 and SAMA7 variants. It models each pin as one group, supports mux functions GPIO/A-G, generic and custom pinconf, gpiochip operations, IRQ domains, wake sources, and suspend/resume restore.

Important APIs and functions: Low-level register access uses `atmel_gpio_read()`, `atmel_gpio_write()`, `atmel_pin_config_read()`, and `atmel_pin_config_write()`. GPIO paths include direction/get/set/multiple and `atmel_gpio_to_irq()`. IRQ paths include set type, mask/unmask, wake, and `atmel_gpio_irq_handler()`. DT mapping is handled by `atmel_pctl_dt_node_to_map()` and helpers. Pinconf methods are `atmel_conf_pin_config_group_get()`, `atmel_conf_pin_config_group_set()`, pin wrappers, and debug show. Probe is `atmel_pinctrl_probe()`.

Control flow: Probe selects SoC data from OF match, calculates total pins and last-bank size, maps MMIO, enables the clock, allocates pin/group/name arrays, initializes one group per pin, creates gpiochip and wake/backup/IRQ arrays, chains each bank IRQ, creates a linear IRQ domain and mappings, registers pinctrl, adds gpiochip, and links the pin range. DT parsing reads packed `pinmux` cells, extracts pin/function/ioset, records pin metadata, emits mux maps, and optionally emits group config maps. Pin config access must write `MSKR` and use a write memory barrier before reading/writing `CFGR`.

State and persistence: `struct atmel_pioctrl` stores MMIO base, clock, bank/pin metadata, pinctrl device, gpiochip, irq domain, parent IRQs, wake-source bitmaps, and per-bank suspend backups of `IMR`, `ODSR`, and each pin `CFGR`. Hardware register state persists and is explicitly saved/restored over system sleep.

Dependencies and integration points: Uses `dt-bindings/pinctrl/at91.h`, generic pinconf parsing with custom `atmel,drive-strength`, gpiolib, IRQ domains, clocks, OF match data, and platform driver binding for `atmel,sama5d2-pinctrl`, `microchip,sama7d65-pinctrl`, and `microchip,sama7g5-pinctrl`.

Risks: `atmel_conf_pin_config_set()` and get wrappers pass `grp->pin` as a group selector, which works only because group index equals pin id in the one-pin-per-group model. `atmel_gpio_set_multiple()` shifts caller-provided masks/bits in place on platforms where bank width differs from `BITS_PER_LONG`, which is surprising. Pin config reads/writes rely on correct `MSKR` sequencing and can affect the wrong pin if reordered.

Test signals: DT pinmux/config parsing, all mux functions A-G, GPIO get/set/multiple across banks and partial last bank, IRQ type/mask/wake behavior per bank, custom drive-strength and slew-rate support by SoC, suspend/resume state restoration, and invalid pin/function cells should be covered.
