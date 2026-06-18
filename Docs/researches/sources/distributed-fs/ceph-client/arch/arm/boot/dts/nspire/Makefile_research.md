# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nspire/Makefile

Purpose: Kbuild manifest for TI-Nspire ARM device trees. It selects DTBs for the CX, Touchpad, and Clickpad variants when `CONFIG_ARCH_NSPIRE` is enabled.

Important APIs/types/functions: the single Kbuild API is `dtb-$(CONFIG_ARCH_NSPIRE) +=`, listing `nspire-cx.dtb`, `nspire-tp.dtb`, and `nspire-clp.dtb`.

Control flow: no code flow beyond conditional Make expansion during `make dtbs`.

State and persistence: no runtime state. Generated DTB files are the build artifacts that persist board descriptions.

Dependencies and integration: depends on `CONFIG_ARCH_NSPIRE`, the matching DTS files, and the ARM DTS parent Makefile. It integrates board files into the normal kernel DTB build.

Risks: board coverage is small, so omissions are easy to detect but high impact for users of a specific calculator variant. Test with an NSPIRE-enabled `make ARCH=arm dtbs` and targeted builds for all three DTBs.
