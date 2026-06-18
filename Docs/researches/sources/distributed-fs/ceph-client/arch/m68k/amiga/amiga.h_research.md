# sources/distributed-fs/ceph-client/arch/m68k/amiga/amiga.h

Purpose: local Amiga prototypes shared across platform files.

The header declares `amiga_init_sound()` and `amiga_mksound(unsigned int hz, unsigned int ticks)` from `amisound.c`. These are consumed by `config.c` when initializing built-in audio and wiring `mach_beep`.

State/persistence: none in the header. The declared functions manipulate Chip RAM allocations, Paula audio DMA, and timers in their implementation.

Dependencies and integration: used inside the `arch/m68k/amiga` directory. It keeps sound prototypes out of broader architecture headers.

Risks and test signals: prototype drift would be compile-time visible. Runtime validation is Amiga boot with audio present and `CONFIG_INPUT_M68K_BEEP` enabled, confirming `mach_beep` can call `amiga_mksound()`.
