# sources/distributed-fs/ceph-client/drivers/usb/c67x00/Makefile

## Purpose
`drivers/usb/c67x00/Makefile` builds the Cypress C67X00 USB controller driver as one composite object when `CONFIG_USB_C67X00_HCD` is enabled.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_USB_C67X00_HCD) += c67x00.o` declares the module or built-in object.
- `c67x00-y := c67x00-drv.o c67x00-ll-hpi.o c67x00-hcd.o c67x00-sched.o` links common platform glue, low-level HPI access, HCD/root-hub code, and scheduler code into that object.

## Control Flow
Kbuild descends into this directory from the top-level USB Makefile and links the listed constituent objects into `c67x00.o`. This file has no runtime control flow.

## State And Persistence Behavior
It affects build state only. Runtime state is in the compiled C files.

## Dependencies And Integration Points
The Makefile must stay synchronized with C file boundaries and Kconfig symbol `USB_C67X00_HCD`. The files researched here cover three of the four linked units; `c67x00-sched.o` supplies transfer scheduling referenced by `c67x00-hcd.h`.

## Risks And Edge Cases
Removing one constituent object can create unresolved symbols because the driver is tightly split between platform, HPI, HCD, and scheduler layers. The composite object name must match module alias and user expectations.

## Test Signals
Build `CONFIG_USB_C67X00_HCD=m` and verify one `c67x00.ko` module containing symbols from all four objects. Build as built-in and confirm no duplicate object linkage.
