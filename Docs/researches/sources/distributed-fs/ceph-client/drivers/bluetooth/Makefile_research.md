# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/Makefile

## Purpose

This Makefile maps Bluetooth driver Kconfig symbols to kernel objects and defines composite object membership for shared transports. It is the build-system integration point for all Bluetooth source files in this subset.

## Important APIs, Types, And Functions

The key Makefile API is the kernel build `obj-$(CONFIG_...) += object.o` convention. Subset mappings include `CONFIG_BT_HCIBCM203X += bcm203x.o`, `CONFIG_BT_HCIBPA10X += bpa10x.o`, `CONFIG_BT_HCIBFUSB += bfusb.o`, `CONFIG_BT_HCIBT3C += bt3c_cs.o`, `CONFIG_BT_HCIBLUECARD += bluecard_cs.o`, `CONFIG_BT_ATH3K += ath3k.o`, and `CONFIG_BT_BCM += btbcm.o`. The file also maps the main USB, SDIO, UART, vendor, PCIe, virtio, and NXP Bluetooth transports.

For the composite UART driver, `hci_uart-y` starts with `hci_ldisc.o` and conditionally appends protocol objects based on `CONFIG_BT_HCIUART_*`, then assigns `hci_uart-objs := $(hci_uart-y)`. The Marvell driver similarly adds debugfs support conditionally.

## Control Flow

There is no runtime control flow. At build time, Kconfig values expand the `obj-*` variables and determine which `.o` files become built-in, modular, or omitted. Composite object lists control which protocol implementations are linked into `hci_uart.o`.

## State And Persistence

The persistent state is the compiled kernel or module set. There is no generated runtime state in this file, but mistakes here directly affect module availability and symbol resolution.

## Dependencies And Integration Points

The Makefile must stay synchronized with `Kconfig` symbols, module names mentioned in help text, and source files. It integrates with kbuild and with exported symbols between helper modules and transports, for example transports that call Broadcom helper APIs need `btbcm.o` when `CONFIG_BT_BCM` is selected.

## Risks

The main risks are symbol-object drift and composite linkage mistakes. A Kconfig symbol with no matching `obj-*` line silently produces a nonfunctional option, while an object referenced without proper dependency can fail builds. For helper libraries like `btbcm.o`, built-in/module combinations should be checked so consumers do not reference unavailable exported symbols.

## Test Signals

Build tests should cover the subset symbols as modules and built-ins. `make M=drivers/bluetooth` style builds, `allmodconfig`, and targeted tiny configs are good signals. Module packaging should confirm expected module names: `ath3k`, `bcm203x`, `bfusb`, `bluecard_cs`, `bpa10x`, `bt3c_cs`, and `btbcm`.
