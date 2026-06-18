# sources/distributed-fs/ceph-client/sound/pci/vx222/Makefile

Purpose: Defines the ALSA build recipe for the Digigram VX222 PCI driver module. The module object `snd-vx222.o` is composed from `vx222.o` and `vx222_ops.o`, and is built when `CONFIG_SND_VX222` is enabled.

Important APIs/types/functions: This file does not define runtime APIs; it establishes the compilation unit boundary that links the PCI probe/PM code in `vx222.c` with the low-level board operation table in `vx222_ops.c`.

Control flow: Kbuild uses `snd-vx222-y := vx222.o vx222_ops.o` to aggregate objects, then `obj-$(CONFIG_SND_VX222) += snd-vx222.o` to conditionally include the module in the sound PCI build.

State and persistence: No runtime state. Build state is controlled by Kconfig selection and Kbuild object composition.

Dependencies/integration: Integrates with the ALSA PCI build and the shared VX core library included by the C files through `<sound/vx_core.h>`.

Risks: Adding a new VX222 source file without updating this object list would silently omit code. Removing either object breaks driver registration or hardware operations.

Test signals: Kernel build with `CONFIG_SND_VX222=m` should emit `snd-vx222.ko` containing symbols from both source objects.
