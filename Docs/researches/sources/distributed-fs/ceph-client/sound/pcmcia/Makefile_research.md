# sources/distributed-fs/ceph-client/sound/pcmcia/Makefile

Purpose: Adds ALSA PCMCIA driver subdirectories to the build when the ALSA core is enabled.

Important APIs/types/functions: No runtime APIs. The only build rule is `obj-$(CONFIG_SND) += vx/ pdaudiocf/`.

Control flow: If `CONFIG_SND` is enabled, Kbuild descends into both `vx` and `pdaudiocf`; each subdirectory then applies its own Kconfig-controlled object rules.

State and persistence: No runtime state. Build inclusion is determined by Kconfig.

Dependencies/integration: Integrates PCMCIA sound subdirectories with the ALSA tree. It delegates actual module selection to subdirectory Makefiles and Kconfig symbols.

Risks: The parent uses `CONFIG_SND` rather than `CONFIG_SND_PCMCIA`, so subdirectory Makefiles must correctly gate objects. Adding a new PCMCIA driver requires updating this directory list.

Test signals: Kernel build with `CONFIG_SND=y/m` should descend into both subdirectories while only configured child modules are emitted.
