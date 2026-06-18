# sources/distributed-fs/ceph-client/include/linux/usb/xhci-dbgp.h

## Purpose
This header declares early xHCI debug capability console setup hooks used for early boot USB debugging.

## Important APIs, types, and functions
When `CONFIG_EARLY_PRINTK_USB_XDBC` is enabled it exports `early_xdbc_parse_parameter()`, `early_xdbc_setup_hardware()`, and `early_xdbc_register_console()`. Disabled stubs make setup return `-ENODEV` and console registration a no-op.

## Control flow, state, and persistence
Early boot parses parameters, initializes xDBC hardware, then registers an early console. State is early-console and controller hardware state only; no persistence is defined.

## Dependencies and integration points
It integrates with architecture early printk, xHCI debug capability support, and boot parameter parsing.

## Risks and test signals
Risks include using unavailable early MMIO resources, enabled/disabled config divergence, and failing gracefully before the normal USB stack exists. Tests should cover boot parameters, no-device fallback, early console output, and disabled stubs.
