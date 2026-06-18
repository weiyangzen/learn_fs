# sources/distributed-fs/ceph-client/sound/pci/cs46xx/Makefile

## Purpose

This Makefile defines how the ALSA CS46xx PCI driver module is built. It composes the `snd-cs46xx` object from the core wrapper and implementation library, and conditionally includes new-DSP support objects when `CONFIG_SND_CS46XX_NEW_DSP` is enabled.

## Important Build Rules

- `snd-cs46xx-y := cs46xx.o cs46xx_lib.o` always includes the PCI module entry/probe wrapper and the core implementation library.
- `snd-cs46xx-$(CONFIG_SND_CS46XX_NEW_DSP) += dsp_spos.o dsp_spos_scb_lib.o` adds DSP SPOS support when the Kconfig option is enabled.
- `obj-$(CONFIG_SND_CS46XX) += snd-cs46xx.o` connects the composite object to the kernel build when the CS46xx driver is selected.

## Control Flow and Integration

There is no runtime control flow in this file. Build-time control flow is driven by Kbuild variable expansion. When `CONFIG_SND_CS46XX=m`, the composite object becomes a module; when built in, it becomes part of the kernel image. The optional DSP files affect which functions and structure fields in `cs46xx.h` are active.

## State and Persistence Behavior

The file has no runtime state. Its build decisions persist only in generated build artifacts and are controlled by kernel configuration.

## Dependencies and Integration Points

The rule depends on Kbuild conventions and on adjacent sources: `cs46xx.c`, `cs46xx_lib.c`, and optional `dsp_spos.c` and `dsp_spos_scb_lib.c`. It integrates with the top-level ALSA PCI sound Kconfig through `CONFIG_SND_CS46XX` and `CONFIG_SND_CS46XX_NEW_DSP`.

## Risks and Edge Cases

- If `CONFIG_SND_CS46XX_NEW_DSP` is enabled without the DSP source files present or compiling, the whole module build fails.
- The Makefile does not list headers directly; dependency discovery relies on Kbuild's compiler-generated dependency tracking.
- Runtime feature availability changes substantially with `CONFIG_SND_CS46XX_NEW_DSP`, so tests must cover both build variants where supported.

## Test Signals

Build validation should compile `CONFIG_SND_CS46XX` both with and without `CONFIG_SND_CS46XX_NEW_DSP`. The resulting module should contain `cs46xx.o` and `cs46xx_lib.o` always, and DSP symbols only in the new-DSP configuration.
