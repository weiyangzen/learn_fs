# sources/distributed-fs/ceph-client/arch/mips/boot/dts/qca/Makefile

Purpose: device-tree build manifest for the `qca` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_ATH79)			+= ar9132_tl_wr1043nd_v1.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_dpt_module.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_dragino_ms14.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_omega.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_openembed_som9331_board.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_tl_mr3020.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include ar9132_tl_wr1043nd_v1.dtb, ar9331_dpt_module.dtb, ar9331_dragino_ms14.dtb, ar9331_omega.dtb, ar9331_openembed_som9331_board.dtb, ar9331_tl_mr3020.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
