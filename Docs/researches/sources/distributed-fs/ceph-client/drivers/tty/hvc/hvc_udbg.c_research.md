# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_udbg.c

## Purpose
`hvc_udbg.c` bridges PowerPC `udbg` early debug callbacks into the HVC tty/console framework. It is a minimal backend used when `udbg_putc` and optionally `udbg_getc_poll` are available.

## Important APIs, Types, and Functions
`hvc_udbg_put()` writes bytes via `udbg_putc`. `hvc_udbg_get()` polls bytes via `udbg_getc_poll` and stops when it returns `-1`. `hvc_udbg_ops` is the HVC ops table. `hvc_udbg_console_init()` performs early console instantiation and preferred console selection; `hvc_udbg_init()` allocates the runtime HVC device.

## Control Flow
If no `udbg_putc` callback exists, both init paths return `-ENODEV`. Otherwise console init registers vterm 0/index 0 and adds preferred `hvc0`. Device init allocates one HVC device with a 16-byte output buffer and saves it in `hvc_udbg_dev`.

## State and Persistence Behavior
The only private state is the single `hvc_udbg_dev` pointer. Operational behavior depends entirely on globally installed udbg callbacks.

## Dependencies and Integration Points
It depends on PowerPC `asm/udbg.h` and HVC core APIs. Other platform code such as OPAL and VIO may install udbg callbacks that this backend then exposes through tty/HVC.

## Risks and Edge Cases
Input is unavailable if `udbg_getc_poll` is null, but output can still work. Only one device is supported. Because udbg callbacks are low-level debug hooks, they may have platform-specific polling or blocking behavior.

## Test Signals
Signals include `udbg_putc` availability, preferred `hvc0` registration, output through debug console, optional input polling, and absence of registration when no udbg output callback is installed.
