# sources/distributed-fs/ceph-client/sound/pci/emu10k1/Makefile

## Purpose

This Makefile defines the ALSA EMU10K1-related kernel objects built from the `sound/pci/emu10k1` directory.

## Important APIs, Types, and Functions

`snd-emu10k1-y` links the main EMU10K1/Audigy driver from PCI binding, hardware init, IRQ, memory, voice, MPU-401 MIDI, PCM, I/O, mixer, FX8010, timer, and P16V files. `snd-emu10k1-$(CONFIG_SND_PROC_FS)` optionally adds procfs diagnostics. `snd-emu10k1-synth-y` builds the wavetable synth companion from synth, callback, and patch files. `snd-emu10k1x-y` builds the separate EMU10K1X driver. `obj-$(CONFIG_SND_EMU10K1)`, `obj-$(CONFIG_SND_EMU10K1_SEQ)`, and `obj-$(CONFIG_SND_EMU10K1X)` connect those objects to Kconfig.

## Control Flow

Kbuild evaluates the selected config symbols and links the corresponding composite modules. The synth module is separate from the main PCI module and depends on sequencer configuration.

## State and Persistence Behavior

The file has no runtime state; its persistent effect is build composition and feature-dependent object inclusion.

## Dependencies and Integration Points

It integrates the driver with kernel Kbuild and config symbols. Source-level dependencies are reflected by object grouping: the main driver exports services used by PCM/mixer/synth components, and the synth module includes callback and patch loading code.

## Risks and Test Signals

Risks include missing an object from a composite module, causing unresolved symbols or disabled functionality. Test signals are successful builds with `CONFIG_SND_EMU10K1`, `CONFIG_SND_EMU10K1_SEQ`, `CONFIG_SND_PROC_FS`, and `CONFIG_SND_EMU10K1X` combinations.
