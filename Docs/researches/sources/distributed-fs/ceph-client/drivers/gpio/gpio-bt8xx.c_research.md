
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bt8xx.c

Purpose: exposes the 24 GPIO pins of Brooktree/Conexant BT848/849/878/879 PCI framegrabber chips as a generic GPIO controller.

Important APIs/types/functions: `struct bt8xxgpio` stores the spinlock, MMIO base, PCI device, gpiochip, and suspend snapshots of `BT848_GPIO_OUT_EN` and `BT848_GPIO_DATA`. Core GPIO operations are `bt8xxgpio_gpio_direction_input()`, `bt8xxgpio_gpio_direction_output()`, `bt8xxgpio_gpio_get()`, and `bt8xxgpio_gpio_set()`. Driver lifecycle is handled by `bt8xxgpio_probe()`, `bt8xxgpio_remove()`, `bt8xxgpio_suspend()`, and `bt8xxgpio_resume()`.

Control flow: PCI probe enables the device, requests BAR0, maps 0x1000 bytes, disables BT848 interrupts and GPIO DMA/input-register modes, sets all GPIOs input, then registers a 24-line gpiochip. GPIO reads and writes use `BT848_GPIO_DATA`; direction is controlled through `BT848_GPIO_OUT_EN`. Suspend snapshots output-enable/data registers and disables outputs; resume reinitializes interrupt/DMA state and restores only saved output data bits that are still output-enabled.

State and persistence behavior: no software cache is maintained during normal operation; hardware registers are read under `spinlock_irqsave`. Only suspend state persists in `saved_outen` and `saved_data`. `gpiobase` is a module parameter and may force a static GPIO base, otherwise dynamic allocation is used.

Dependencies and integration points: depends on PCI core, legacy BT848 register definitions from the media driver, gpiolib, and PM ops. There is no IRQ support in this GPIO driver; it explicitly disables the device interrupt mask.

Risks: the driver intentionally "abuses" media hardware, so sharing with a real bttv/media function would conflict over BAR registers. Static `gpiobase` can collide with other GPIO controllers. The GPIO input path clears the data bit before disabling output, which matches hardware assumptions but is unusual compared with pure direction registers.

Test signals: compile with BT8xx PCI IDs, probe on matching hardware, GPIO direction/value smoke tests through libgpiod, suspend/resume preserving output pins, and removal disabling outputs/interrupts without leaking the PCI enable.
