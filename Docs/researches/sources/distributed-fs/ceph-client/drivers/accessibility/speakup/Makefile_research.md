# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/Makefile Research

## Purpose
The Speakup Makefile maps Kconfig symbols to synthesizer driver objects, assembles the core `speakup.o` composite object, and defines host-tool generation steps for keymap headers.

## Important Build Rules And Control Flow
Each `CONFIG_SPEAKUP_SYNTH_*` option adds a matching `speakup_*.o`. `obj-$(CONFIG_SPEAKUP) += speakup.o` builds the core. `speakup-y` includes buffers, device synth, i18n, fake key, main, key help, kobjects, selection, tty I/O, synth, thread, and variable handlers; `serialio.o` is added with `CONFIG_SPEAKUP_SERIALIO`. Host tools generate `mapdata.h` and `speakupmap.h`, and `main.o` depends on `speakupmap.h`.

## State And Persistence
Generated state exists under the object directory as `mapdata.h` and `speakupmap.h`; it is build-local and cleaned by kbuild. Runtime state is in the linked Speakup objects.

## Dependencies And Integration Points
The file depends on kbuild host program support, `makemapdata.c`, `genmap.c`, `speakupmap.map`, headers consumed by `makemapdata`, and all Speakup implementation objects.

## Risks
Generated-header ordering is fragile: `main.o` requires `speakupmap.h`, and `genmap.o` requires `mapdata.h`. Missing dependencies can create parallel-build races. Renaming synthesizer symbols or objects without synchronized changes breaks builds.

## Test Signals
Use parallel builds such as `make -jN drivers/accessibility/speakup/` to catch dependency races. Test `CONFIG_SPEAKUP=y/m`, individual synthesizer modules, clean rebuilds, and `make clean` behavior for generated headers.
