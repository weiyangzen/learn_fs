# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/Makefile

## Purpose

The ath5k Makefile declares the object composition of the `ath5k.o` composite driver module. It lists core objects, conditionally includes debug and bus backends, adds a local include path for `base.o`, and binds the module to `CONFIG_ATH5K`.

## Important Rules

- `ath5k-y` always includes core objects such as `caps.o`, `initvals.o`, `eeprom.o`, `gpio.o`, `desc.o`, `dma.o`, `qcu.o`, `pcu.o`, `phy.o`, `reset.o`, `attach.o`, `base.o`, `led.o`, `rfkill.o`, `ani.o`, `sysfs.o`, and `mac80211-ops.o`.
- `CFLAGS_base.o += -I$(src)` adds the ath5k source directory for `base.o`.
- `ath5k-$(CONFIG_ATH5K_DEBUG) += debug.o`.
- `ath5k-$(CONFIG_ATH5K_AHB) += ahb.o`.
- `ath5k-$(CONFIG_ATH5K_PCI) += pci.o`.
- `obj-$(CONFIG_ATH5K) += ath5k.o`.

## Control Flow

Kbuild expands the unconditional and conditional object lists into the final composite `ath5k.o`. Runtime bus probe behavior depends on whether `ahb.o` or `pci.o` was included. ANI is always compiled when ath5k is built because `ani.o` is unconditional.

## State And Persistence Behavior

There is no runtime state. The persistent result is the compiled object graph and therefore the available probe/debug/sysfs features.

## Dependencies And Integration Points

The Makefile mirrors Kconfig symbols: debug, AHB, and PCI symbols control object inclusion. It uses standard Kbuild composite-object syntax.

## Risks

New source files must be added here or they will not build. Conditional bus objects must stay aligned with Kconfig or supported platforms can lose probe support. Local include path assumptions should not spread accidentally without matching `CFLAGS_*.o` changes.

## Test Signals

Build ath5k with debug on/off and AHB/PCI configurations. Confirm `ani.o` is always included with ath5k, `debug.o` only with `CONFIG_ATH5K_DEBUG`, and the expected bus backend for the target platform.
