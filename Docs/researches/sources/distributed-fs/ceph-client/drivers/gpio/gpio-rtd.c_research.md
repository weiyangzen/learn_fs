# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rtd.c

## Purpose
This platform driver supports Realtek DHC SoC GPIO controllers, including several ISO and MISC register layouts. It provides GPIO direction/value operations, pinconf debounce support, and edge interrupt handling through separate assert and deassert parent IRQs.

## Important APIs, Types, and Functions
`struct rtd_gpio_info` captures per-compatible register offset arrays, GPIO counts, debounce encodings, and a callback for locating debounce bitfields. `struct rtd_gpio` stores the gpio chip, selected info, base and IRQ-base mappings, two parent IRQs, and a raw spinlock. Important functions include `rtd_gpio_set_debounce()`, `rtd_gpio_set/get/direction_*()`, `rtd_gpio_irq_handle()`, `rtd_gpio_enable_irq()`, `rtd_gpio_disable_irq()`, and `rtd_gpio_irq_set_type()`.

## Control Flow
Probe obtains two parent IRQs, selects match data, maps control and IRQ status resources, fills gpiolib callbacks, wires a two-parent `gpio_irq_chip`, and registers the chip. GPIO get checks the direction register and reads either output data or input data. IRQ handling selects the assert or deassert status register family based on parent IRQ, iterates status registers packed as 31 GPIOs plus a write-enable bit, clears status, checks line enable, and dispatches allowed domain IRQs.

## State and Persistence
Hardware registers hold direction, values, interrupt enable, polarity, status, and debounce configuration. The driver stores no IRQ shadow state beyond the immutable layout data and parent IRQ numbers. There are no PM callbacks.

## Dependencies and Integration Points
The driver uses OF match data, platform MMIO resources, two parent interrupts, pinconf generic bias delegation, gpiolib generic request/free, and raw spinlock guard macros from cleanup helpers.

## Risks
Interrupt status packing is unusual: each status register covers 31 GPIOs because bit 0 is write-enable, making off-by-one errors likely. `rtd_gpio_irq_handle()` assumes only the two known parent IRQs call it; otherwise the register-offset function is uninitialized. For deassert IRQs, non-both-edge lines break out of the loop instead of continuing, which makes trigger-type interactions important to test. Only edge triggers are accepted.

## Test Signals
Test each compatible layout's offsets and GPIO counts, debounce values exactly matching 1/10/100/1000/10000/20000/30000 us, assert and deassert parent IRQ delivery, both-edge versus single-edge behavior, invalid trigger types, bias delegation, and boundary GPIOs around 31/32 and bank transitions.
