# sources/distributed-fs/ceph-client/drivers/usb/serial/xsens_mt.c

## Purpose

`xsens_mt.c` is a small usb-serial binding driver for Xsens MT motion trackers. It binds known Xsens VID/PID pairs but only accepts the serial interface used by the device.

## Important APIs, Types, and Functions

The `id_table` lists MTi-10, MTi-20, MTi-30, MTi-100, MTi-200, MTi-300, and MTi-G-700 product IDs under vendor ID `0x2639`. `xsens_mt_probe()` checks the current alternate setting's interface number and returns success only for interface 1. `xsens_mt_device` registers a one-port usb-serial driver using default usb-serial behavior for data transfer.

## Control Flow

On USB match, usb-serial calls the probe hook. Interface 1 is accepted and exposed as a tty; all other matched interfaces are rejected with `-ENODEV`. Runtime open, close, read, and write handling is inherited from the usb-serial core.

## State and Persistence Behavior

The driver has no private state, no cached device settings, and no persistence. Device state remains entirely in the Xsens firmware and the usb-serial core's generic per-port structures.

## Dependencies and Integration Points

It depends on usb-serial core and the Xsens devices presenting a usable serial interface at USB interface number 1. Userspace interacts with the resulting tty using the device's native protocol.

## Risks and Test Signals

Risks include hard-coding interface number 1 for all listed devices, adding new Xsens products with different interface layouts, and relying on generic usb-serial defaults for all tty behavior. Test signals include binding only interface 1 for each PID, no tty exposure on other interfaces, basic open/read/write traffic with an Xsens protocol tool, and module autoload via `MODULE_DEVICE_TABLE`.
