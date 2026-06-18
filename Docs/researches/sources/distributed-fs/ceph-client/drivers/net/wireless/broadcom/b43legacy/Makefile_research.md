# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/Makefile

## Purpose
Builds the `b43legacy` composite kernel object from its core and optional feature modules. It maps Kconfig symbols to object inclusion and registers `b43legacy.o` under `CONFIG_B43LEGACY`.

## Important APIs, Types, and Functions
The base object list includes `main.o`, `ilt.o`, `phy.o`, `radio.o`, `sysfs.o`, `xmit.o`, and `rfkill.o`. Optional objects are `leds.o` for `CONFIG_B43LEGACY_LEDS`, `debugfs.o` for `CONFIG_B43LEGACY_DEBUG`, `dma.o` for `CONFIG_B43LEGACY_DMA`, and `pio.o` for `CONFIG_B43LEGACY_PIO`. The final line adds `b43legacy.o` to `obj-$(CONFIG_B43LEGACY)`.

## Control Flow
There is no runtime control flow. Build-time control determines which translation units are linked into the module or built-in driver. Header stubs in optional components must match these object selections so disabled features still compile cleanly.

## State and Persistence
The file influences build artifacts only. It does not create runtime state, but it determines whether runtime state for DMA rings, PIO queues, LEDs, debugfs entries, and debug logs can exist.

## Dependencies and Integration Points
Integrates with the Linux kbuild composite-object convention. The listed objects correspond to the driver subsystems consumed by `main.c`: firmware/core lifecycle, PHY/radio calibration, sysfs, transmit formatting, rfkill, LEDs, debugfs, DMA, and PIO.

## Risks
Object omissions or Kconfig mismatches can produce link failures or runtime stubs that hide missing functionality. Because `main.o` calls both DMA and PIO APIs through compile-time stubs, the Makefile and headers must remain synchronized with Kconfig.

## Test Signals
Kernel builds under each transfer-mode choice and optional feature combination are sufficient. A useful guard is checking that disabling debug or LEDs removes the object while preserving successful compilation through inline stub APIs.
