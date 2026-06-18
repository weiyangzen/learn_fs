
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-dln2.c

Purpose: supports Diolan DLN-2 USB GPIO adapters using DLN-2 MFD command transfers and asynchronous event callbacks for GPIO IRQs.

Important APIs/types/functions: `struct dln2_gpio` stores the platform device, gpiochip, output-direction bitmap, unmasked/enabled IRQ bitmaps, IRQ type array, and IRQ mutex. Core functions are `dln2_gpio_request()`, `dln2_gpio_set_direction()`, `dln2_gpio_get()`, `dln2_gpio_set_config()`, `dln2_irq_set_type()`, `dln2_irq_bus_unlock()`, `dln2_gpio_event()`, `dln2_gpio_probe()`, and `dln2_gpio_remove()`.

Control flow: probe queries pin count, clamps to 32, initializes gpiochip callbacks and a child IRQ domain without parent handler, registers the gpiochip, then registers a DLN-2 event callback. GPIO request enables the hardware pin and caches its current direction; free disables it. IRQ mask/unmask only changes software bitmaps, while bus-sync-unlock sends event configuration commands to hardware when enabled state changes. Events validate message length/pin, filter synthetic rising/falling edge variants, and dispatch through the GPIO IRQ domain.

State and persistence behavior: direction is cached to avoid USB transfers when deciding whether `get()` should read input or output value. IRQ state is split into requested/unmasked and hardware-enabled bitmaps. Debounce is programmed globally through `DLN2_GPIO_SET_DEBOUNCE`, not per pin.

Dependencies and integration points: depends on DLN-2 MFD transfer APIs, gpiolib, irqdomain, platform child devices, and asynchronous USB-originated events.

Risks: USB/firmware transfer errors surface directly. The debounce API ignores the offset in the command payload. Cached direction can become stale if firmware or another client changes pin direction. IRQ event filtering relies on stored `irq_type` and event value semantics.

Test signals: pin-count query and clamp, request/free enable/disable commands, input/output get behavior based on cached direction, event configuration on mask/unmask, rising/falling event filtering, short/out-of-range event rejection, and callback unregister on remove.
