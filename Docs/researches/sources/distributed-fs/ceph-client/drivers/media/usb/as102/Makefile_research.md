# sources/distributed-fs/ceph-client/drivers/media/usb/as102/Makefile

## Purpose
Builds the AS102 USB DVB receiver module from the driver, firmware, USB transport, and AS10x command source files.

## Important APIs, types, and functions
Defines `dvb-as102-objs` as `as102_drv.o`, `as102_fw.o`, `as10x_cmd.o`, `as10x_cmd_stream.o`, `as102_usb_drv.o`, and `as10x_cmd_cfg.o`. Adds the resulting module with `obj-$(CONFIG_DVB_AS102) += dvb-as102.o`.

## Control flow and state
No runtime control flow exists. The object list determines link composition: `as102_drv.c` provides module registration and DVB glue, `as102_usb_drv.c` exports the `as102_usb_driver`, firmware upload lives in `as102_fw.c`, and protocol operations are split across command files.

## Dependencies and integration points
Adds a compiler include path to `drivers/media/dvb-frontends`, needed for AS102 frontend headers such as `as102_fe.h` and `as102_fe_types.h`. Integrates with kbuild's media module build flow.

## Risks and test signals
Risks are missing object files or include paths when command APIs are moved. Test signals are a clean module link for `CONFIG_DVB_AS102=m`, no undefined references to `as102_usb_driver` or AS10x command helpers, and correct module name `dvb-as102`.
