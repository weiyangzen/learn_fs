# sources/distributed-fs/ceph-client/include/linux/mmc/slot-gpio.h

## Purpose
`mmc/slot-gpio.h` declares generic GPIO-backed MMC slot helpers for card-detect and write-protect signals. It lets host drivers reuse common GPIO descriptor, IRQ, debounce, polarity, wake, and capability logic.

## Important APIs, Types, And Functions
The API surface is `mmc_gpio_get_ro()`, `mmc_gpio_get_cd()`, `mmc_gpio_set_cd_irq()`, `mmc_gpiod_request_cd()`, `mmc_gpiod_request_ro()`, `mmc_gpiod_set_cd_config()`, `mmc_gpio_set_cd_wake()`, `mmc_gpiod_request_cd_irq()`, `mmc_host_can_gpio_cd()`, and `mmc_host_can_gpio_ro()`.

## Control Flow And State
Host drivers request CD/RO GPIOs during probe, then use get helpers from host callbacks or let the helper request a CD IRQ that drives detect work. `mmc_gpio_set_cd_irq()` records the IRQ in `mmc_host::slot`, and wake control toggles whether card-detect can wake the system. Persistent state lives in host slot fields and helper-private GPIO context.

## Dependencies And Integration Points
Dependencies include interrupt and type headers plus `struct mmc_host`. Integration points include host `get_cd()`/`get_ro()` callbacks, device tree or platform GPIO descriptors, debounce configuration, card-detect IRQ handling, PM wake, and the host slot state in `host.h`.

## Risks And Test Signals
Risks include active-level polarity mistakes, debounce omissions, wake IRQ misconfiguration, IRQ leaks on remove, and hosts mixing native and GPIO CD/RO sources inconsistently. Test signals include card insertion/removal, write-protect readback, active-high/active-low DT configurations, debounce behavior, suspend wake on CD IRQ, and probe/remove resource cleanup.
