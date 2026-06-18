# sources/distributed-fs/ceph-client/drivers/mmc/core/slot-gpio.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/slot-gpio.c

### Purpose
`slot-gpio.c` provides generic GPIO descriptor helpers for MMC slot card-detect and write-protect pins. It lets host drivers request CD/RO GPIOs, read them through MMC host ops, wire card-detect IRQs, configure wake, and fall back to polling.

### Important APIs, Types, And Functions
The private `struct mmc_gpio` stores CD/RO descriptors, labels, debounce, ISR, and IRQ number. Exported APIs are `mmc_gpio_alloc()`, `mmc_gpio_set_cd_irq()`, `mmc_gpio_get_ro()`, `mmc_gpio_get_cd()`, `mmc_gpiod_request_cd_irq()`, `mmc_gpio_set_cd_wake()`, `mmc_gpiod_request_cd()`, `mmc_gpiod_set_cd_config()`, `mmc_host_can_gpio_cd()`, `mmc_gpiod_request_ro()`, and `mmc_host_can_gpio_ro()`. The default IRQ handler is `mmc_gpio_cd_irqt()`.

### Control Flow
Host setup calls `mmc_gpio_alloc()` to allocate devm-managed context and labels. CD/RO request helpers acquire input descriptors, set debounce, adjust active-low polarity based on override and host caps, and store descriptors. `mmc_gpiod_request_cd_irq()` uses an explicit IRQ or `gpiod_to_irq()` unless polling is requested, installs a threaded edge IRQ, stores the result in `host->slot.cd_irq`, and sets `MMC_CAP_NEEDS_POLL` on failure. The default IRQ handler marks `host->trigger_card_event` and schedules debounced `mmc_detect_change()`. Read helpers use sleeping or non-sleeping GPIO access depending on descriptor capability. Wake toggles `enable_irq_wake()`/`disable_irq_wake()` when `MMC_CAP_CD_WAKE` is set.

### State, Persistence, And Dependencies
State is in `host->slot.handler_priv`, `host->slot.cd_irq`, `host->slot.cd_wake_enabled`, host caps, and devm-managed GPIO/IRQ resources. Dependencies include GPIO consumer descriptors, IRQ APIs, jiffies, MMC host structures, module exports, and pinconf-style GPIO config.

### Integration Points
Host drivers use this file to implement `get_cd`/`get_ro` host ops and to request card-detect IRQs before or after `mmc_add_host()`. The detection work feeds the MMC rescan path that eventually reaches SD/SDIO attach code.

### Risks
Calling request helpers without `mmc_gpio_alloc()` leaves `ctx` null; most read paths handle that, but config helpers assume a valid descriptor. Debounce fallback converts microseconds to milliseconds and can become zero for sub-millisecond values. Polarity toggling can be confusing when both `override_active_level` and `MMC_CAP2_CD_ACTIVE_HIGH` are used. IRQ failure silently forces polling, which changes detection latency and power behavior.

### Test Signals
Test CD/RO GPIO request success/failure, active-high and active-low polarity, debounce hardware support and fallback, card insert/remove IRQ scheduling, explicit platform IRQ, polling fallback, wake enable/disable, pin config, and hosts without CD/RO GPIOs.
