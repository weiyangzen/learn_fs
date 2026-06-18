# sources/distributed-fs/ceph-client/sound/mips/Makefile

Purpose: Connects MIPS ALSA platform-driver config symbols to their objects. It also defines composite modules for SGI O2 and HAL2 audio.

Important APIs/types/functions: `snd-sgi-o2-y := sgio2audio.o ad1843.o` links the O2 platform driver with the shared AD1843 codec helper. `snd-sgi-hal2-y := hal2.o` defines the HAL2 module. `obj-$(CONFIG_SND_SGI_O2)`, `obj-$(CONFIG_SND_SGI_HAL2)`, and `obj-$(CONFIG_SND_N64)` select the final build targets.

Control flow: Kbuild evaluates each `obj-*` line from the active `.config`. SGI O2 builds as a composite module/built-in containing both `sgio2audio.o` and `ad1843.o`; N64 builds directly from `snd-n64.o`.

State and persistence: No runtime state. Build output shape matters because `sgio2audio.c` depends on functions implemented in `ad1843.c`.

Dependencies/integration: Integrates with `sound/mips/Kconfig` and top-level ALSA kbuild. Risks include link failures if `ad1843.o` is omitted from SGI O2, stale object names after source renames, or module naming mismatches. Test signals are successful `CONFIG_SND_SGI_O2`, `CONFIG_SND_SGI_HAL2`, and `CONFIG_SND_N64` builds and expected module/object names.
