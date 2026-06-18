# sources/distributed-fs/ceph-client/drivers/usb/isp1760/Makefile

## Purpose
The Makefile builds the ISP1760 composite module/object. It always includes common core and bus glue and conditionally adds host-controller and gadget-controller implementations.

## Important APIs, Types, And Functions
`isp1760-y` includes `isp1760-core.o` and `isp1760-if.o`. `isp1760-$(CONFIG_USB_ISP1760_HCD)` appends `isp1760-hcd.o`; `isp1760-$(CONFIG_USB_ISP1761_UDC)` appends `isp1760-udc.o`. `obj-$(CONFIG_USB_ISP1760) += isp1760.o` exposes the final object to kbuild.

## Control Flow
kbuild expands the role-dependent object list from Kconfig selections. The final linked object contains only the selected role implementation(s), with headers providing no-op inline stubs for disabled roles.

## State And Persistence
There is no runtime state. Build output composition persists only as generated kernel objects/modules.

## Dependencies And Integration Points
This file is coupled to `Kconfig` symbols and to the C headers' conditional declarations. It must remain synchronized with any new source files or role symbols added under this directory.

## Risks
Incorrect object gating can cause unresolved symbols or silently omit a role selected by configuration. Because `isp1760-core.o` calls HCD/UDC registration functions, the disabled-role inline stubs in headers are required for configurations where an object is not linked.

## Test Signals
Build tests for all three role selections should confirm the final object list and successful linking. `make M=drivers/usb/isp1760` or equivalent subtree builds are sufficient for this file's direct behavior.
