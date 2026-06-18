# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rcar.c

## Purpose
This driver exposes Renesas R-Car GPIO banks as `gpio_chip` instances with GPIO-line IRQ support and sleep/resume restoration. It supports several R-Car hardware generations through `struct gpio_rcar_info`, which records feature differences such as `OUTDTSEL`, both-edge trigger support, always-valid input reads, and the Gen4 `INEN` input-enable register.

## Important APIs, Types, and Functions
Key state lives in `struct gpio_rcar_priv`: MMIO base, raw spinlock, gpio chip, parent IRQ, wakeup-path counter, generation info, and a `struct gpio_rcar_bank_info` register snapshot for suspend. Register helpers `gpio_rcar_read()`, `gpio_rcar_write()`, and `gpio_rcar_modify_bit()` centralize MMIO access. Gpiolib callbacks include request/free, direction, get/set, and multiple-line operations. IRQ callbacks are collected in immutable `gpio_rcar_irq_chip` and include mask/unmask, type configuration, wake control, and a shared parent IRQ handler.

## Control Flow
`gpio_rcar_probe()` allocates private state, parses DT match data and `gpio-ranges` to derive the number of pins, enables runtime PM, maps the resource, registers the GPIO chip, links the IRQ domain to the PM device, and requests the parent IRQ with `gpio_rcar_irq_handler()`. GPIO requests runtime-resume the controller and delegate pin ownership to pinctrl; free returns the line to input mode before dropping runtime PM. Interrupt type selection programs POSNEG, EDGLEVEL, optional BOTHEDGE, and IOINTSEL under the raw spinlock, clearing pending edge interrupts.

## State and Persistence
Runtime state is held in hardware registers plus `wakeup_path`. Suspend snapshots IOINTSEL, INOUTSEL, OUTDT, INTMSK, POSNEG, EDGLEVEL, and optional BOTHEDGE. Resume iterates valid lines and reconstructs either GPIO mode or interrupt mode, then restores unmasked interrupts and enables inputs on Gen4-style hardware. `wakeup_path` is an atomic count incremented by `.irq_set_wake()` and drives `device_set_wakeup_path()`.

## Dependencies and Integration Points
The driver integrates with platform resources, Open Firmware match data, pinctrl GPIO request/free, gpiolib IRQ domains, runtime PM, raw MMIO access, and Linux IRQ wake APIs. `irq_domain_set_pm_device()` binds GPIO IRQs to the device PM lifecycle.

## Risks
IRQ masking uses hardware-specific write-one/clear-style registers and must match the manual precisely. Resume replay can glitch if saved OUTDT/direction/interrupt state is stale or if valid masks exclude lines. Wakeup accounting assumes balanced set_wake calls. Both-edge support is rejected on old hardware, so DT compatibility must select the right generation data.

## Test Signals
Useful tests include GPIO direction/value reads for input and output banks, `get_multiple()` with mixed directions, all supported IRQ trigger types per generation, runtime suspend/resume with GPIOs and IRQs configured, wake-from-suspend with GPIO IRQs, invalid `gpio-ranges`, and Gen4 `INEN` behavior with valid line masks.
