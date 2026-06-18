# sources/distributed-fs/ceph-client/drivers/watchdog/gef_wdt.c

## Purpose
`gef_wdt.c` is a legacy miscdevice watchdog for GE Intelligent Platforms FPGA watchdog hardware. It provides `/dev/watchdog` access to one watchdog even though the hardware can support more.

## Important APIs, types, and functions
Global state includes MMIO base, timeout/count, bus clock, status, open flag, magic-close flag, and spinlock. Hardware helpers are `gef_wdt_toggle_wdc`, `gef_wdt_service`, `gef_wdt_handler_enable`, `gef_wdt_handler_disable`, and `gef_wdt_set_timeout`. File operations implement write, ioctl, open, and release.

## Control Flow
Probe maps the FPGA watchdog registers from device tree, gets system bus frequency through `fsl_get_sys_freq`, computes the initial counter, disables any running watchdog, and registers `/dev/watchdog`. Open enforces single-open, optionally pins the module for nowayout, and enables hardware. Writes scan for magic close and service the watchdog. Ioctls support status, set options, keepalive, and timeout get/set. Release disables only after magic close.

## State and Persistence
State is global and singleton. The hardware register combines enabled state, service/enable toggle fields, and low 24 bits of count. Status bits are software-only and partially cleared on read.

## Dependencies and Integration Points
The driver depends on OF compatible `gef,fpga-wdt`, big-endian MMIO access, Freescale system frequency helper, miscdevice watchdog ABI, and module nowayout.

## Risks and Test Signals
Risks include global singleton limitations, count scaling from bus clock, upper-24-bit truncation, lack of watchdog core integration, and no interrupt-threshold support. Tests should cover timeout clamping, big-endian register toggle sequences, unexpected close, ioctl compatibility, OF map failure, and bus frequency fallback.
