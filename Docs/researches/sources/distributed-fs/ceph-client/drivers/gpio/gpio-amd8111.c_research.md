# sources/distributed-fs/ceph-client/drivers/gpio/gpio-amd8111.c

## Purpose
This module exposes the 32 GPIO pins in AMD 8111 south bridge PM I/O space. It discovers the chipset by scanning PCI devices rather than binding a PCI driver, then registers a single global gpiochip.

## Important APIs, types, and functions
`struct amd_gpio` contains the gpiochip, PM base, mapped PM I/O region, PCI device reference, spinlock, and `orig[32]` saved per-pin modes. Callbacks are `amd_gpio_request()`, `amd_gpio_free()`, `amd_gpio_set()`, `amd_gpio_get()`, `amd_gpio_dirout()`, and `amd_gpio_dirin()`. Module lifecycle is `amd_gpio_init()` and `amd_gpio_exit()`.

## Control flow
Init scans all PCI devices for AMD 8111 SMBus ID, reads PM base from config offset `0x58`, reserves and maps PM I/O ports, initializes the global chip, and registers it. Request saves each pin's debounce/mode/output-control bits; free restores the saved bits. Direction and set callbacks rewrite the mode and output state.

## State and persistence behavior
Hardware state is PM I/O register state. Driver state includes the global PCI device reference, mapping, lock, and original per-pin configuration captured on request. Free restores the captured mode, making request/free boundaries stateful.

## Dependencies and integration points
The driver depends on PCI enumeration, I/O port resources, legacy ioport mapping, gpiolib, and spinlock protection. It deliberately avoids registering a PCI driver so other functions can own the same multifunction PCI ID.

## Risks and edge cases
Only one south bridge is assumed. Global static state prevents multiple instances. Restoring `orig[]` on free is useful but can overwrite changes by other firmware/drivers after request. `devm_request_region()` is used with the PCI device in a module-init flow, while `ioport_unmap()` and `pci_dev_put()` are handled manually.

## Test signals
Test on AMD 8111 hardware for PM base discovery, gpiochip registration, request/free restoration, input and output modes, debug messages, and clean module unload with region unmap and PCI reference release.
