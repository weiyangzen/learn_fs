# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-if.c

## Purpose
`bttv-if.c` preserves the old exported GPIO/kernel-module interface for consumers that address bttv cards by card index instead of using the newer `bttv-sub` device model. The source comments mark it obsolete in favor of `bttv-gpio.c`.

## Important APIs, Types, And Functions
The exported symbols are `bttv_get_pcidev()`, `bttv_gpio_enable()`, `bttv_read_gpio()`, and `bttv_write_gpio()`. These functions operate on the global `bttvs[]` array and the current `bttv_num` card count, then delegate to `gpio_inout()`, `gpio_read()`, and `gpio_bits()` macros.

## Control Flow
Callers pass a card index. Each function checks the index against `bttv_num`, verifies the `struct bttv *` exists, and returns `-EINVAL` or `-ENODEV` when invalid. GPIO enable updates `BT848_GPIO_OUT_EN`, read returns `BT848_GPIO_DATA`, and write updates masked data bits. Debug tracking is emitted when `bttv_gpio` is enabled.

## State And Persistence
There is no state local to this file. It exposes global live driver state and hardware GPIO registers. `bttv_read_gpio()` additionally rejects access after `btv->shutdown` is set during remove, reducing use-after-remove risk for legacy clients.

## Dependencies And Integration Points
This interface depends on `bttv-driver.c` maintaining `bttvs[]`, `bttv_num`, and `shutdown`. It shares register access helpers and GPIO locking behavior with `bttv-gpio.c`. Legacy IR or board helper modules may still use these symbols.

## Risks
The interface is card-index based and lacks device references, so users can race hot-unplug/removal unless they handle `-ENODEV`. `bttv_gpio_enable()` and `bttv_write_gpio()` do not check `shutdown`, unlike read. Because the interface is deprecated, test coverage may be weaker than for the subdevice path.

## Test Signals
Signals are module symbol availability, successful legacy client load, correct negative returns for invalid card numbers or removed devices, and GPIO tracking logs showing expected masked updates.
