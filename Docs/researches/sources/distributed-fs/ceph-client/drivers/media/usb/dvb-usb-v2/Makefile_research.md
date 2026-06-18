# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/Makefile

## Purpose

This Makefile maps DVB USB v2 Kconfig symbols to kernel objects. It builds the shared `dvb_usb_v2` core and each selected device-specific module, and it adds include paths for DVB frontend, tuner, and common media headers.

## Important APIs, Types, and Targets

`dvb_usb_v2-objs` is composed of `dvb_usb_core.o`, `dvb_usb_urb.o`, and `usb_urb.o`; `obj-$(CONFIG_DVB_USB_V2)` emits the shared module or built-in object. Each device driver has an object list such as `dvb-usb-af9015-objs := af9015.o` and an `obj-$(CONFIG_DVB_USB_AF9015)` assignment. MxL111SF is split into multiple objects and also builds `mxl111sf-demod.o` and `mxl111sf-tuner.o` as separate targets under the same config.

The `ccflags-y` entries add include directories for `drivers/media/dvb-frontends`, `drivers/media/tuners`, and `drivers/media/common`, allowing device drivers such as `af9015.c` to include frontend/tuner headers directly.

## Control Flow

The build flow is controlled entirely by Kconfig-expanded `obj-*` variables. When a config symbol is `m`, the corresponding module object is built as a module; when `y`, it is linked into the kernel image. The source-to-object mapping is one-to-one for most device drivers, while shared core objects are grouped into the `dvb_usb_v2` composite.

## State and Persistence Behavior

There is no runtime state. Build state is persisted in generated object files and modules according to the active kernel configuration. The Makefile also encodes the stable module names, such as `dvb-usb-af9015`.

## Dependencies and Integration Points

This file integrates with the Kbuild system and the `Kconfig` file in the same directory. It also indirectly enforces source layout expectations: `af9015.c` becomes the only object in `dvb-usb-af9015`, while shared code remains in `dvb_usb_v2`. Include path choices couple this directory to frontend and tuner header locations.

## Risks

Misaligned object names and Kconfig symbols can result in drivers never being built. Missing include paths can break compile coverage for tuners/frontends. Composite module changes must preserve expected module names because userspace, documentation, initramfs module lists, and alias handling may refer to existing names.

## Test Signals

Build tests should verify module and built-in configurations for `DVB_USB_V2` and each child driver. `modinfo dvb-usb-af9015` should show USB aliases emitted from `af9015.c`, and dependency generation should include selected tuner/frontend modules when autoselection is active.
