# sources/distributed-fs/ceph-client/arch/mips/boot/dts/loongson/Makefile

Purpose: device-tree build manifest for the `loongson` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `ifneq ($(CONFIG_BUILTIN_DTB_NAME),); dtb-y	:= $(addsuffix .dtb, $(CONFIG_BUILTIN_DTB_NAME)); else; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64_2core_2k1000.dtb; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64c_4core_ls7a.dtb; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64c_4core_rs780e.dtb; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64c_8core_rs780e.dtb; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64g_4core_ls7a.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include loongson64_2core_2k1000.dtb, loongson64c_4core_ls7a.dtb, loongson64c_4core_rs780e.dtb, loongson64c_8core_rs780e.dtb, loongson64g_4core_ls7a.dtb, loongson64v_4core_virtio.dtb, cq-t300b.dtb, ls1b-demo.dtb, lsgz_1b_dev.dtb, smartloong-1c.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
