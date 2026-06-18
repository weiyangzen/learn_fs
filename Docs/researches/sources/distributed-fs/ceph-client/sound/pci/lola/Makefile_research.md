# sources/distributed-fs/ceph-client/sound/pci/lola/Makefile

## Purpose
This Makefile builds the Digigram Lola ALSA PCI driver as the `snd-lola` module when `CONFIG_SND_LOLA` is enabled.

## Important APIs, Types, and Functions
It declares `snd-lola-y := lola.o lola_pcm.o lola_clock.o lola_mixer.o`, so the base module always includes PCI probe/CORB/RIRB handling, PCM stream handling, clock control, and mixer control. It conditionally appends `lola_proc.o` via `snd-lola-$(CONFIG_SND_DEBUG)` to include proc debugging only in debug builds.

## Control Flow
Kbuild compiles the listed objects into one composite module. `obj-$(CONFIG_SND_LOLA) += snd-lola.o` connects the module to the kernel config option.

## State and Persistence
The Makefile has no runtime state. Its important persistence behavior is build-contract persistence: adding or removing Lola source files requires updating this object list.

## Dependencies and Integration Points
It depends on Kbuild composite-object conventions and the kernel configuration symbol `CONFIG_SND_LOLA`. It also encodes that `lola_proc.c` must not be linked unless debug support is configured.

## Risks
Forgetting to update `snd-lola-y` when adding a required implementation file will cause unresolved symbols or missing runtime features. Accidentally linking debug proc support unconditionally could expose direct codec register access outside debug builds.

## Test Signals
`make M=sound/pci/lola` or a full kernel build with `CONFIG_SND_LOLA=m/y` should produce `snd-lola`. A debug build should include proc entries from `lola_proc.c`; a non-debug build should not reference `lola_proc_debug_new()` beyond the stub macro in `lola.h`.
