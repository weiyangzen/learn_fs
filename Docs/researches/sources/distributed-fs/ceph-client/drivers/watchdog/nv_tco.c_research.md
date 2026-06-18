# sources/distributed-fs/ceph-client/drivers/watchdog/nv_tco.c

## Purpose
`nv_tco.c` is a legacy miscdevice watchdog driver for NVIDIA nForce TCO timers. It discovers supported SMBus PCI functions, derives the TCO I/O base, disables TCO SMI delivery, enables reboot capability, and exposes `/dev/watchdog`.

## Important APIs, types, and functions
Global state includes `tcobase`, `timer_alive`, `tco_expect_close`, `tco_pci`, and a platform device. Hardware helpers are `tco_timer_start`, `tco_timer_stop`, `tco_timer_keepalive`, and `tco_timer_set_heartbeat`. Userspace handlers are `nv_tco_open`, `nv_tco_release`, `nv_tco_write`, and `nv_tco_ioctl`. Discovery and lifecycle are `nv_tco_getdevice`, `nv_tco_init`, `nv_tco_cleanup`, shutdown/remove, and module init/exit.

## Control flow
Module init registers a platform driver and synthetic platform device. Probe scans PCI devices against the TCO table, reads BAR/config registers to compute `tcobase`, reserves the TCO I/O region, sets a safe heartbeat, stops the timer, disables TCO SMI bits, sets the chipset reboot-enable bit, reports watchdog reset status, clears status, validates heartbeat, and registers `/dev/watchdog`. Open keepalives and starts; writes scan for magic `V` and reload; release stops only after magic close, otherwise keepalives. Cleanup stops unless nowayout and attempts to unset reboot capability.

## State and persistence
Hardware status bits survive warm boot and are cleared in probe. Software singleton state tracks single open and magic-close state. PCI config `MCP51_SMBUS_SETUP_B_TCO_REBOOT` is modified during probe, cleanup, and shutdown.

## Dependencies and integration points
It integrates PCI ID matching without binding a PCI driver, platform driver plumbing, I/O port region management, `nv_tco.h` register macros, miscdevice `WATCHDOG_MINOR`, and classic watchdog ioctls.

## Risks and test signals
Risks include global singleton assumptions, direct PCI config manipulation, confusing cleanup that disables future reboot ability, failure to handle shared SMBus ownership beyond not binding PCI driver, and legacy miscdevice behavior outside watchdog core policy. Test signals include supported PCI discovery, region conflicts, SMI disable failure, NO_REBOOT bit verification, heartbeat conversion boundaries, magic close, shutdown cleanup, and warm-boot status clearing.
