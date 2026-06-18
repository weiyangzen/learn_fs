<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/core.h

## Purpose
`core.h` is the central WM8350 MFD contract. It defines core register addresses and bit fields, embeds child-device state, declares regmap/register helpers, exposes platform initialization data, and provides IRQ wrapper helpers for child drivers.

## Important APIs, types, and functions
Key types are `struct wm8350_hwmon`, `struct wm8350`, and `struct wm8350_platform_data`. Important APIs include `wm8350_device_init()`, `wm8350_clear_bits()`, `wm8350_set_bits()`, `wm8350_reg_read()`, `wm8350_reg_write()`, `wm8350_reg_lock()`, `wm8350_reg_unlock()`, `wm8350_block_read()`, `wm8350_block_write()`, `wm8350_irq_init()`, `wm8350_irq_exit()`, and inline IRQ helpers `wm8350_register_irq()`, `wm8350_free_irq()`, `wm8350_mask_irq()`, and `wm8350_unmask_irq()`. It also declares `wm8350_regmap`.

## Control flow
Bus glue creates a `struct wm8350`, initializes regmap, calls `wm8350_device_init()`, and child drivers use embedded sub-structs plus register/IRQ helpers. IRQ registration offsets child IRQ numbers by `irq_base` and requests threaded one-shot handlers.

## State and persistence behavior
`struct wm8350` stores runtime state: device pointer, regmap, register-lock state, AUXADC mutex/completion, IRQ lock/base/masks, chip IRQ, and child state for codec, GPIO, hwmon, PMIC, power, RTC, and watchdog. Hardware register state includes power management, hibernate, interface, interrupt, status, and override registers.

## Dependencies and integration points
The header includes completion, interrupt, mutex, regmap, and all WM8350 child headers. It integrates with MFD child creation, regulator, GPIO, ASoC, RTC, watchdog, power-supply, hwmon, and genirq.

## Risks and test signals
Risks include using IRQ helpers with `irq_base == 0`, losing mask state over suspend, incorrect register lock/unlock sequencing, child header circularity, and regmap cache mismatches. Test signals include full MFD probe/remove, regmap read/write/block tests, IRQ mask/unmask dispatch, AUXADC completion, and child-device registration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/core.h -->
