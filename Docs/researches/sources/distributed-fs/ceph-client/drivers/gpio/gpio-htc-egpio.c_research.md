<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-htc-egpio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-htc-egpio.c

## Purpose
`gpio-htc-egpio.c` supports legacy HTC phone CPLD GPIO/IRQ expanders described by platform data. It can register several gpiochips over one MMIO region, manage fixed input/output line capabilities, cache output values, and demultiplex a shared parent IRQ.

## Important APIs, types, and functions
`struct egpio_info` holds the shared spinlock, MMIO layout, IRQ bookkeeping, and flexible array of `struct egpio_chip`. `egpio_get()`, `egpio_set()`, direction helpers, `egpio_get_direction()`, and `egpio_write_cache()` implement GPIO behavior. IRQ flow uses `egpio_handler()`, `ack_irqs()`, `egpio_mask()`, and `egpio_unmask()`. PM hooks are `egpio_suspend()` and `egpio_resume()`.

## Control flow
The early `subsys_initcall` registers a platform driver with `platform_driver_probe()`. Probe consumes `struct htc_egpio_platform_data`, maps the memory resource, computes bus/register shifts from platform widths, creates one gpiochip per declared chip, writes cached initial output values, then optionally maps a contiguous legacy IRQ range to a chained parent IRQ. Resume rewrites cached output values after possible CPLD power loss.

## State and persistence behavior
Output state is shadowed in each `egpio_chip.cached_values`; `is_out` marks output-capable lines. IRQ enable state is software-only in `irqs_enabled` because the CPLD cannot proactively mask individual child IRQs. Runtime state persists across suspend in RAM and is reapplied to hardware on resume.

## Dependencies and integration points
This driver depends on board platform data from `linux/platform_data/gpio-htc-egpio.h`, legacy fixed IRQ bases, raw MMIO `readw()`/`writew()`, and chained IRQ APIs. It predates DT/ACPI and managed gpiochip removal patterns.

## Risks and edge cases
The probe path calls `gpiochip_add_data()` without checking its return value inside the loop, so partial registration failures can be hard to detect. Child IRQ masking only filters in software after interrupts arrive. The driver assumes valid platform data; missing `dev_get_platdata()` would dereference null.

## Test signals
Test with HTC board platform data, verify output cache writes on probe and resume, fixed input/output direction errors, chained IRQ demux and software mask filtering, wake enable/disable during suspend, and cleanup behavior under gpiochip registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-htc-egpio.c -->
