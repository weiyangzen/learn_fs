# sources/distributed-fs/ceph-client/sound/pci/riptide/Makefile

## Purpose

This Makefile builds the ALSA Riptide PCI driver as the composite `snd-riptide` module when enabled in kernel configuration.

## Important APIs, Types, And Functions

- `snd-riptide-y := riptide.o` declares the single object that forms the composite module.
- `obj-$(CONFIG_SND_RIPTIDE) += snd-riptide.o` integrates the module with Kbuild and the `CONFIG_SND_RIPTIDE` option.

## Control Flow

Kbuild compiles `riptide.o` and links it into `snd-riptide.o` only when the config symbol is enabled. Runtime control flow is in `riptide.c`, not in this file.

## State And Persistence

The file has no runtime state. Its persistent effect is build inclusion of the Riptide driver.

## Dependencies And Integration Points

It depends on Linux Kbuild syntax and the surrounding ALSA PCI sound Makefile hierarchy. The SPDX line marks the build metadata as GPL-2.0-only.

## Risks

Because there is only one object, any future split of the Riptide driver must update `snd-riptide-y`; otherwise new code will not link. A mismatched config symbol would silently omit or incorrectly include the module.

## Test Signals

Build with `CONFIG_SND_RIPTIDE=m` and verify `snd-riptide.ko` links. Build with the option disabled and verify no Riptide module is produced.
