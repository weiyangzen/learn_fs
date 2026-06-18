# sources/distributed-fs/ceph-client/drivers/gpio/gpio-reg.c

## Purpose
`gpio-reg.c` is a small exported helper for devices where up to 32 fixed-direction GPIOs share one register. It offers a `gpio_chip` around a single MMIO register with fixed input/output direction, optional names, and optional GPIO-to-IRQ mapping.

## Important APIs, Types, and Functions
`struct gpio_reg` stores the gpio chip, spinlock, fixed direction bitmask, output shadow, MMIO register, optional irq domain, and per-line IRQ mappings. Public entry points are `gpio_reg_init()` and `gpio_reg_resume()`. Gpiolib callbacks include fixed-direction checks, `gpio_reg_set()`, `gpio_reg_get()`, `gpio_reg_set_multiple()`, and `gpio_reg_to_irq()`.

## Control Flow
Callers invoke `gpio_reg_init()` with the register address, line count, direction mask, default output value, optional line names, and optional IRQ mapping. The helper allocates managed or unmanaged state depending on whether a device is supplied, fills the `gpio_chip`, and registers it. Output writes update the software `out` shadow and write the entire register under a spinlock. Input reads perform a double read because some hardware latches input state on first access.

## State and Persistence
Output state persists in `r->out`, not by reading hardware back. `gpio_reg_resume()` rewrites that shadow to hardware after resume. Inputs are read from hardware only when their direction bit is input.

## Dependencies and Integration Points
This helper is exported through `linux/gpio/gpio-reg.h` for other kernel code. It integrates with gpiolib and optionally `irq_domain` via `.to_irq`.

## Risks
The helper assumes fixed directions and cannot model runtime direction changes. Output reads return the shadow, so external hardware changes are invisible. `set_multiple()` uses the caller's first word mask directly and is intended for <=32 lines. Callers must ensure `direction`, `def_out`, and IRQ arrays match `num`.

## Test Signals
Unit-style users should test fixed direction rejection, input double-read behavior on latch-like registers, output shadow restoration via `gpio_reg_resume()`, `set_multiple()` masking, and IRQ translation with both Linux IRQ numbers and domain hardware IRQs.
