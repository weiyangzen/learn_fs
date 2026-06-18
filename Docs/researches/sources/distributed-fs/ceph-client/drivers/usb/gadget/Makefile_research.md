# sources/distributed-fs/ceph-client/drivers/usb/gadget/Makefile

## Purpose
`drivers/usb/gadget/Makefile` builds the USB gadget framework top-level objects and descends into the UDC, function, and legacy gadget subdirectories. It is the build-system counterpart to the gadget Kconfig menu.

## Important APIs, Types, and Functions
The Makefile sets `subdir-ccflags-$(CONFIG_USB_GADGET_DEBUG) := -DDEBUG` and appends `-DVERBOSE_DEBUG` when `CONFIG_USB_GADGET_VERBOSE` is enabled. It builds `libcomposite.o` when `CONFIG_USB_LIBCOMPOSITE` is enabled, with component objects `usbstring.o`, `config.o`, `epautoconf.o`, `composite.o`, `functions.o`, `configfs.o`, and `u_f.o`. It descends into `udc/`, `function/`, and `legacy/` when `CONFIG_USB_GADGET` is enabled.

## Control Flow
Kbuild evaluates the conditional object lists from `.config`. If libcomposite is selected, the listed `libcomposite-y` members are linked into `libcomposite.o`. If gadget support is enabled, Kbuild recurses into the hardware-controller, reusable-function, and legacy-driver subdirectories, where lower-level Makefiles choose specific UDC and gadget function objects.

## State and Persistence Behavior
The Makefile has no runtime state. Its persistent effect is build output: which objects are compiled and how debug preprocessor symbols are applied. The debug flags affect all descendant compilation units through `subdir-ccflags`.

## Dependencies and Integration Points
The Makefile integrates with Kbuild, the top-level gadget Kconfig symbols, and subdirectory Makefiles. It is the path by which UDC drivers such as FOTG210 gadget mode and composite/configfs gadget code enter the kernel build.

## Risks
Changing `subdir-ccflags` affects every gadget subdirectory and can alter timing or log volume. Omitting a `libcomposite-y` member can break configfs or composite gadget linking. Removing `udc/`, `function/`, or `legacy/` from `obj-$(CONFIG_USB_GADGET)` can silently drop large families of gadget support.

## Test Signals
Build with `CONFIG_USB_GADGET`, `CONFIG_USB_LIBCOMPOSITE`, debug, verbose debug, selected UDC drivers, selected function drivers, and legacy gadgets as built-in and modules. Link failures in `libcomposite.o`, missing UDC modules, or absent configfs gadget functionality are direct signals of Makefile regressions.
