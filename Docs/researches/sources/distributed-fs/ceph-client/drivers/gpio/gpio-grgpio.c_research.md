
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-grgpio.c

Purpose: supports Aeroflex/Gaisler GRGPIO cores with generic MMIO GPIO operations and optional per-line IRQ mapping to one of several underlying IRQ inputs.

Important APIs/types/functions: `struct grgpio_priv` stores generic chip, registers, device, interrupt-mask shadow, IRQ domain, underlying IRQ records, and line IRQ records. Important functions are `grgpio_to_irq()`, `grgpio_irq_set_type()`, `grgpio_irq_mask()`, `grgpio_irq_unmask()`, `grgpio_irq_handler()`, `grgpio_irq_map()`, `grgpio_irq_unmap()`, and `grgpio_probe()`.

Control flow: probe maps registers, initializes a big-endian generic GPIO chip, reads current interrupt mask, sets line count from `nbits`, and optionally parses an `irqmap` property. If `irqmap` exists, it creates a linear IRQ domain and records each line's underlying IRQ index. `gpiod_to_irq()` creates mappings only for lines with valid indices. Mapping lazily requests the underlying IRQ and increments its refcount; unmapping masks the line and frees the underlying IRQ when the last mapped line using it disappears.

State and persistence behavior: `imask` shadows the hardware mask register and is updated under generic-chip lock. `uirqs[].refcnt` tracks shared underlying IRQ requests. GPIO values/directions persist in hardware. There is no PM context.

Dependencies and integration points: depends on OF GRLIB-compatible names, `nbits`/`irqmap` properties, platform IRQ resources, gpiolib generic helpers, irqdomain, and big-endian MMIO access.

Risks: the `irqmap` size check compares bytes to `ngpio`, so malformed properties may be undervalidated or overaccepted depending on endianness/encoding. IRQ handling scans every GPIO line for each underlying IRQ. Both-edge IRQs are unsupported.

Test signals: GPIO operation with and without IRQ map, line count fallback, invalid `irqmap` handling, lazy underlying IRQ request/free refcounts, mask shadow correctness, trigger type programming, and big-endian register access.
