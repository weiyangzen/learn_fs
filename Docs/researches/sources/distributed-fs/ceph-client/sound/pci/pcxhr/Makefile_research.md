# sources/distributed-fs/ceph-client/sound/pci/pcxhr/Makefile

## Purpose

This Makefile builds the ALSA Digigram PCXHR PCI driver object. It declares the constituent object files for `snd-pcxhr.o` and connects the composite module to `CONFIG_SND_PCXHR`.

## Important APIs, Types, And Functions

- `snd-pcxhr-y` lists `pcxhr.o`, `pcxhr_hwdep.o`, `pcxhr_mixer.o`, `pcxhr_core.o`, and `pcxhr_mix22.o`.
- `obj-$(CONFIG_SND_PCXHR) += snd-pcxhr.o` lets Kbuild include the module only when the kernel configuration enables the driver.

## Control Flow

Kbuild compiles each listed object and links them into the single `snd-pcxhr` module. Runtime entry comes from `pcxhr.o`, whose `module_pci_driver()` registers the PCI driver.

## State And Persistence

The file has no runtime state. Its only persistent effect is build-system composition.

## Dependencies And Integration Points

The Makefile depends on Kbuild composite-object conventions and the `CONFIG_SND_PCXHR` symbol defined elsewhere in ALSA/Kconfig.

## Risks

Omitting one object breaks symbols across the driver stack, because the implementation is split across PCM/probe, firmware, mixer, core mailbox/IRQ, and HR222-specific code. Adding files without updating this list leaves code unlinked.

## Test Signals

Build `CONFIG_SND_PCXHR=m` and verify `snd-pcxhr.ko` links with no unresolved symbols. Also test `CONFIG_SND_PCXHR=n` to ensure no PCXHR objects are built.
