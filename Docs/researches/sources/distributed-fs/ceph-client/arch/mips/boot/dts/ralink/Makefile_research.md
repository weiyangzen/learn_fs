# sources/distributed-fs/ceph-client/arch/mips/boot/dts/ralink/Makefile

Purpose: device-tree build manifest for the `ralink` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_DTB_RT2880_EVAL)	+= rt2880_eval.dtb; dtb-$(CONFIG_DTB_RT305X_EVAL)	+= rt3052_eval.dtb; dtb-$(CONFIG_DTB_RT3883_EVAL)	+= rt3883_eval.dtb; dtb-$(CONFIG_DTB_MT7620A_EVAL)	+= mt7620a_eval.dtb; dtb-$(CONFIG_DTB_OMEGA2P)	+= omega2p.dtb; dtb-$(CONFIG_DTB_VOCORE2)	+= vocore2.dtb; dtb-$(CONFIG_SOC_MT7621) += \; mt7621-gnubee-gb-pc1.dtb \`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include rt2880_eval.dtb, rt3052_eval.dtb, rt3883_eval.dtb, mt7620a_eval.dtb, omega2p.dtb, vocore2.dtb, mt7621-gnubee-gb-pc1.dtb, mt7621-gnubee-gb-pc2.dtb, mt7621-tplink-hc220-g5-v1.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
