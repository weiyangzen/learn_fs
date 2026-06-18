<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/Makefile

Purpose: Kbuild manifest for Turtle Beach MultiSound/MSND ISA drivers. It builds a shared `snd-msnd-lib` and two board modules.

Important APIs/types/functions: build variables are `snd-msnd-lib-y := msnd.o msnd_pinnacle_mixer.o`, `snd-msnd-pinnacle-y := msnd_pinnacle.o`, and `snd-msnd-classic-y := msnd_classic.o`. `obj-$(CONFIG_SND_MSND_PINNACLE)` and `obj-$(CONFIG_SND_MSND_CLASSIC)` link the selected board object with the shared library.

Control flow: enabling a board config compiles the board-specific file and common MSND support into the module. This file does not participate in runtime control flow.

State and persistence: no runtime state; module composition is build-time only.

Dependencies and integration: depends on adjacent MSND C files and ALSA ISA Kconfig. Risks are link failures or missing common mixer support if object lists drift. Test signals are kernel builds with Pinnacle and Classic configs independently enabled and verifying both include `snd-msnd-lib.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/Makefile -->
