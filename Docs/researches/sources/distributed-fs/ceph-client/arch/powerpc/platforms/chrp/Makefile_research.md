# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/Makefile

Purpose: selects object files for the CHRP platform directory.

Important build behavior: unconditional objects are `setup.o`, `time.o`, `pegasos_eth.o`, and `pci.o`; `smp.o` is included under `CONFIG_SMP`; `nvram.o` is included when `CONFIG_NVRAM` is built-in or module-compatible through `obj-$(CONFIG_NVRAM:m=y)`.

Integration points: the files listed here provide platform setup, clock/RTC/NVRAM hooks, Pegasos ethernet platform quirks, PCI bridge setup, and SMP startup. The Kconfig `PPC_CHRP` option is the higher-level selector that causes this Makefile to matter.

Risks and test signals: the compact file hides platform coupling, especially the special NVRAM conditional syntax. Build risks include missing object coverage for selected features or module/built-in mismatches. Test signals are CHRP defconfig builds with SMP on/off and NVRAM built-in/module/disabled combinations.
