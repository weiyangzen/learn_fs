# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/Kconfig

Purpose: defines the Loongson DRM driver configuration symbol.

Important APIs/types/functions: `config DRM_LOONGSON` is tristate, depends on DRM/PCI and LoongArch, MIPS, or `COMPILE_TEST`, and selects DRM client selection, KMS helper, TTM, TTM helper, I2C, and bit-banged I2C.

Control flow: no runtime flow; controls whether the `loongson` module is built.

State and persistence: persisted in kernel config and affects linked objects through the Makefile.

Dependencies and integration points: mirrors source dependencies on PCI probing, DRM atomic/KMS, TTM memory management, and GPIO-emulated DDC I2C.

Risks and test signals: missing dependencies cause compile/link failures. Test LoongArch/MIPS builds, `COMPILE_TEST`, module and built-in configurations.
