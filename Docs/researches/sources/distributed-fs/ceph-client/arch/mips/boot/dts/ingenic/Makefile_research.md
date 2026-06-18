# sources/distributed-fs/ceph-client/arch/mips/boot/dts/ingenic/Makefile

Purpose: device-tree build manifest for the `ingenic` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_JZ4740_QI_LB60)	+= qi_lb60.dtb; dtb-$(CONFIG_JZ4740_RS90)	+= rs90.dtb; dtb-$(CONFIG_JZ4770_GCW0)	+= gcw0.dtb; dtb-$(CONFIG_JZ4780_CI20)	+= ci20.dtb; dtb-$(CONFIG_X1000_CU1000_NEO)	+= cu1000-neo.dtb; dtb-$(CONFIG_X1830_CU1830_NEO)	+= cu1830-neo.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include qi_lb60.dtb, rs90.dtb, gcw0.dtb, ci20.dtb, cu1000-neo.dtb, cu1830-neo.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
