<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.h

## Purpose
Shared Renesas USBHS register map, bit definitions, private state, and cross-module declarations.

## Important APIs, Types, And Functions
Defines offsets for system, FIFO, interrupt, setup, DCP/PIPE, transaction, DEVADD, Gen2 DFIFO, and RZ/A SUSPMODE registers. Defines bit masks for module enable, host/function mode, pull-up/down, FIFO status, interrupts, device/control state, transfer types, PID, DATA toggle, and device address config. `struct usbhs_priv` aggregates driver state. Declares common sysconfig, request, bus, frame, device config, interrupt, and data helpers.

## Control Flow
No executable flow, but `usbhs_lock()`/`usbhs_unlock()` and `usbhs_get_dparam()` shape all modules' locking and parameter access.

## State And Persistence
`usbhs_priv` is the persistent driver state. Register definitions describe hardware state persisted until cleared/reset.

## Dependencies And Integration Points
Includes clk, extcon, platform_device, reset, `linux/usb/renesas_usbhs.h`, `mod.h`, and `pipe.h`; consumed by all USBHS modules.

## Risks
Wrong shared masks break multiple modules. `usbhs_get_dparam()` returns an lvalue, allowing runtime mutation of copied platform parameters. The intentional include cycle is fragile.

## Test Signals
Build all modules, verify interrupt clear behavior, device-state decoding, pipe PID transitions, FIFO length reads, and DEVADD programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.h -->
