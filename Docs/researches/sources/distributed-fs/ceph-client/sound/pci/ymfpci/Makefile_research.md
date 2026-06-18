# sources/distributed-fs/ceph-client/sound/pci/ymfpci/Makefile

Purpose: Defines the Kbuild composition for the Yamaha DS-1/YMFPCI ALSA module. `snd-ymfpci.o` is linked from `ymfpci.o` and `ymfpci_main.o`, and included when `CONFIG_SND_YMFPCI` is enabled.

Important APIs/types/functions: No runtime APIs are declared. The build contract links the PCI probe/legacy-resource wrapper in `ymfpci.c` with the hardware, PCM, mixer, timer, firmware, IRQ, and PM implementation in `ymfpci_main.c`.

Control flow: Kbuild aggregates objects through `snd-ymfpci-y := ymfpci.o ymfpci_main.o`; `obj-$(CONFIG_SND_YMFPCI)` controls conditional module inclusion.

State and persistence: No runtime state. Build output depends on Kconfig.

Dependencies/integration: Integrates into ALSA PCI build and expects both C objects to share `ymfpci.h`.

Risks: Missing either object causes unresolved symbols or an incomplete driver. Any new companion object must be added here.

Test signals: Kernel build with `CONFIG_SND_YMFPCI=m` should produce `snd-ymfpci.ko` with PCI registration and exported helper symbols resolved.
