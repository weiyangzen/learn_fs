<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/gpio-nomadik.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/gpio-nomadik.h

Purpose: This is the shared private/public interface between Nomadik GPIO and pinctrl drivers. It defines bank geometry, register offsets, sleep/pull/alternate-function encodings, per-bank runtime state, and SoC pinctrl description tables.

Important APIs/types/functions: Register macros cover data, set/clear, pull disable, direction, sleep, alternate-function, low-EMI, interrupt masks/status/clear, wake masks/status, and later edge/level registers. `struct nmk_gpio_chip` embeds `gpio_chip` and stores MMIO base, clock, bank id, `set_ioforce`, lock, sleep mode, Mobileye flag, interrupt edge masks, wake masks, cached mask registers, pull-up, and low-EMI state. Pinctrl data uses `struct prcm_gpiocr_altcx`, `struct prcm_gpiocr_altcx_pin_desc`, `struct nmk_function`, `struct nmk_pingroup`, and `struct nmk_pinctrl_soc_data`. SoC init hooks exist for STN8815, DB8500, and DB8540.

Control flow, state, and persistence: GPIO and pinctrl share bank arrays and sleep-mode locking when `CONFIG_PINCTRL_NOMADIK` is enabled. Driver implementation uses cached fields to preserve interrupt, wake, pull, and low-EMI configuration across transitions. Alternate-C selection may require PRCM GPIOCR register control rather than only the GPIO block.

Dependencies/integration: It depends on gpiolib, pinctrl pin descriptors/groups, platform devices, clocks, debugfs, and SoC-specific Kconfig. Debug support exposes `nmk_gpio_dbg_show_one()` only under `CONFIG_DEBUG_FS`; otherwise it is a no-op inline.

Risks and test signals: Pin numbering must match GPIO numbering for GPIO-backed pins. Cached IRQ and sleep masks can drift from hardware if locking is bypassed. Tests should cover SoC init data selection, alternate function C/C1-C4 encoding, GPIO direction/output transitions, sleep persistence, IRQ edge/wake masks, debugfs formatting, and builds with each SoC CONFIG off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/gpio-nomadik.h -->
