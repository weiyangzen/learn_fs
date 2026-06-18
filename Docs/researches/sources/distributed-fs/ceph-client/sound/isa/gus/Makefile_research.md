<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/gus/Makefile

Purpose: Kbuild manifest for the Gravis UltraSound family. It builds a shared `snd-gus-lib` from core GF1 helpers and links it with board modules for Classic, Extreme, MAX, InterWave, and InterWave STB.

Important APIs/types/functions: no C API, but the object lists define module composition. `snd-gus-lib-y` includes `gus_main.o`, I/O, IRQ, timer, memory, DRAM, DMA, volume, PCM, mixer, UART, and reset helpers. Board objects are `gusclassic.o`, `gusextreme.o`, `gusmax.o`, `interwave.o`, and `interwave-stb.o`.

Control flow: Kbuild includes the board object plus `snd-gus-lib.o` when a board Kconfig symbol is enabled. This makes exported GF1 helper symbols available to the board-specific module.

State and persistence: no runtime state. Build-time linkage determines which helper code is present in each module.

Dependencies and integration: ties the GUS subtree to ALSA ISA Kconfig symbols. The STB object is a wrapper that includes `interwave.c` with `SNDRV_STB`. Risks are missing helper objects or mismatched exported symbols causing link failures. Test signals are all five module configurations building alone and in combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/Makefile -->
