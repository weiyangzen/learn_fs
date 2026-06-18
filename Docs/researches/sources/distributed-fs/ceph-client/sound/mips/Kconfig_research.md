# sources/distributed-fs/ceph-client/sound/mips/Kconfig

Purpose: Defines the ALSA MIPS sound-device configuration menu and three platform driver symbols: SGI O2 Audio, SGI HAL2 Audio, and Nintendo 64 Audio.

Important APIs/types/functions: Kconfig symbols are `SND_MIPS`, `SND_SGI_O2`, `SND_SGI_HAL2`, and `SND_N64`. `SND_SGI_O2` depends on `SGI_IP32` and selects `SND_PCM`; `SND_SGI_HAL2` depends on `SGI_HAS_HAL2` and selects `SND_PCM`; `SND_N64` is built-in only, depends on `MACH_NINTENDO64 && SND=y`, and selects `SND_PCM`.

Control flow: `menuconfig SND_MIPS` appears under MIPS and defaults to `y`. If enabled, the nested config entries become visible and govern whether the corresponding objects in `sound/mips/Makefile` are built.

State and persistence: No runtime state exists here. Persistent effects are build configuration choices that decide driver availability and whether modules or built-ins are produced.

Dependencies/integration: Integrates architecture platform symbols with ALSA PCM support. Risks are build-coverage gaps if platform dependencies are wrong, especially `SND_N64` requiring built-in ALSA due its `bool` and `SND=y` dependency. Test signals are Kconfig visibility on the intended MIPS platforms, expected object selection in generated `.config`, and successful builds for enabled SGI/N64 targets.
