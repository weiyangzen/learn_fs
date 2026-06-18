# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/Kconfig

## Purpose

This Kconfig file defines the Bluetooth device-driver configuration menu under `depends on BT`. It controls which transport drivers, vendor helper modules, firmware loaders, and protocol submodules are built into the kernel or as modules. For this subset it provides the build-time contract for `ath3k.c`, `bcm203x.c`, `bfusb.c`, `bluecard_cs.c`, `bpa10x.c`, `bt3c_cs.c`, and `btbcm.c`.

## Important Config Symbols

Vendor helper symbols include `BT_INTEL`, `BT_BCM`, `BT_RTL`, `BT_QCA`, and `BT_MTK`; most are tristate helper libraries and select `FW_LOADER` or `REGMAP` as needed. USB HCI support is controlled by `BT_HCIBTUSB` plus protocol booleans such as `BT_HCIBTUSB_BCM`, `BT_HCIBTUSB_MTK`, and `BT_HCIBTUSB_RTL`. UART HCI support is controlled by `BT_HCIUART` and protocol booleans such as `BT_HCIUART_H4`, `BT_HCIUART_BCSP`, `BT_HCIUART_ATH3K`, `BT_HCIUART_BCM`, `BT_HCIUART_QCA`, and others.

The subset-specific symbols are `BT_HCIBCM203X` for the Broadcom Blutonium firmware loader, `BT_HCIBPA10X` for Digianswer BPA 100/105 USB devices, `BT_HCIBFUSB` for AVM BlueFRITZ! USB, `BT_HCIBT3C` for 3Com PC Card devices, `BT_HCIBLUECARD` for Anycom BlueCard PC Card devices, `BT_ATH3K` for Atheros firmware download, and `BT_BCM` for the Broadcom support helper. PCMCIA drivers require `PCMCIA && HAS_IOPORT`; firmware loaders select `FW_LOADER`; HCI transport dependencies select lower protocol support when needed.

## Control Flow

Kconfig selection determines object inclusion through the Bluetooth Makefile. Enabling a user-facing transport pulls in lower-level helpers via `select`, for example `BT_HCIBTUSB_BCM` selects `BT_BCM`, `BT_HCIBPA10X` depends on `BT_HCIUART` and selects `BT_HCIUART_H4`, and `BT_ATH3K` depends on `BT_HCIBTUSB`. This keeps transport drivers from compiling without their protocol or firmware infrastructure.

## State And Persistence

There is no runtime state. The persistent effect is the kernel configuration: built-in, module, or disabled choices determine which driver probes can happen at boot or module load time and which firmware names can be requested by those drivers.

## Dependencies And Integration Points

The file integrates with USB, MMC, TTY, SERIAL_DEV_BUS, GPIOLIB, ACPI, PCMCIA, HAS_IOPORT, PCI, RPMSG, VIRTIO, firmware loading, and vendor helper libraries. The symbols here must remain aligned with object names in `drivers/bluetooth/Makefile` and with source-level `IS_ENABLED(CONFIG_...)` guards such as those in `btbcm.h`.

## Risks

Incorrect `depends on` or `select` relationships can create build failures in unusual configurations, especially for optional subsystems such as PCMCIA, serial device bus, ACPI, NVMEM, and firmware loading. Because several protocol options are booleans under a tristate parent, build combinations should be checked for built-in versus module linkage. User-facing help text and module names must stay in sync with Makefile targets to avoid confusing configuration.

## Test Signals

Strong signals are `allyesconfig`, `allmodconfig`, targeted minimal configs for each subset driver, and configs with USB disabled, PCMCIA disabled, or FW_LOADER modular. Runtime probe tests should confirm each enabled symbol creates the expected module object and that disabled helper symbols yield the expected inline stubs or absent objects.
