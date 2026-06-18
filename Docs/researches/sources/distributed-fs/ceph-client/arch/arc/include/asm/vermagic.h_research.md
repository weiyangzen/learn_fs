# sources/distributed-fs/ceph-client/arch/arc/include/asm/vermagic.h

Module architecture vermagic definition for ARC. It sets MODULE_ARCH_VERMAGIC to `ARC700`, which becomes part of module compatibility strings. Control flow is module build/load comparing vermagic to the running kernel. State is compile-time metadata. Dependencies are Linux module loader and arch Kconfig naming. Risk is that a fixed ARC700 string may be too coarse for ARCv2/HS distinctions if other ABI checks are insufficient. Test signals are insmod/modprobe vermagic rejection/acceptance across ARC ISA configurations.
