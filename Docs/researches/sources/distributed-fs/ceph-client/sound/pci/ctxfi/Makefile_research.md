# sources/distributed-fs/ceph-client/sound/pci/ctxfi/Makefile

Purpose: Kbuild fragment for the Creative X-Fi ctxfi ALSA module.

Important APIs and types: declares `snd-ctxfi-y` object composition: PCI front end `xfi.o`, ATC orchestration, VM, PCM, mixer, resource managers, SRC, AMIXER, DAIO, input mapper, hardware abstraction, timer, and chip-specific 20k1/20k2 backends. Exposes the module through `obj-$(CONFIG_SND_CTXFI)`.

Control flow and integration: build order groups the entire ctxfi subsystem into one module, so internal symbols are linked together rather than exported between modules.

State, risks, and test signals: no runtime state. Build-test should ensure both 20k1 and 20k2 hardware backends remain included when `CONFIG_SND_CTXFI` is enabled.
