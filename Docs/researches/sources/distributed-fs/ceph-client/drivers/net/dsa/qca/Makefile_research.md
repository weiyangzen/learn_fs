# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/Makefile

## Purpose

This Makefile maps the QCA DSA Kconfig symbols to object files. It builds AR9331 as a standalone object and QCA8K as a composite module/object.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_NET_DSA_AR9331) += ar9331.o`
- `obj-$(CONFIG_NET_DSA_QCA8K) += qca8k.o`
- `qca8k-y += qca8k-common.o qca8k-8xxx.o`
- `qca8k-y += qca8k-leds.o` when `CONFIG_NET_DSA_QCA8K_LEDS_SUPPORT` is set.

## Control Flow

There is no runtime control flow. Kbuild combines the listed objects into `qca8k.o` when QCA8K is enabled and conditionally includes the LED implementation.

## State and Persistence

The file affects build artifacts only. No runtime state is introduced.

## Dependencies and Integration Points

It integrates with Kbuild and the symbols declared in the local Kconfig. The composite object arrangement lets `qca8k-common.c`, `qca8k-8xxx.c`, and optionally `qca8k-leds.c` share internal headers and one module registration unit.

## Risks and Edge Cases

The conditional `ifdef CONFIG_NET_DSA_QCA8K_LEDS_SUPPORT` must match Kconfig exactly; otherwise `qca8k_setup_led_ctrl()` would resolve to the inline stub in `qca8k_leds.h` or fail to link if declarations diverge. Object order is conventional: common code before the device-specific driver. Build-only changes here need all tristate combinations tested.

## Test Signals

Expected build outputs are `ar9331.o` when AR9331 is enabled and `qca8k.o` containing `qca8k-common.o` plus `qca8k-8xxx.o`, with `qca8k-leds.o` present only for LED support. `modinfo qca8k` should reflect the module metadata from `qca8k-8xxx.c`.
