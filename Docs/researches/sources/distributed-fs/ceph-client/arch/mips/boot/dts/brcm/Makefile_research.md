# sources/distributed-fs/ceph-client/arch/mips/boot/dts/brcm/Makefile

Purpose: device-tree build manifest for the `brcm` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_DT_BCM93384WVG)		+= bcm93384wvg.dtb; dtb-$(CONFIG_DT_BCM93384WVG_VIPER)	+= bcm93384wvg_viper.dtb; dtb-$(CONFIG_DT_BCM96368MVWG)		+= bcm96368mvwg.dtb; dtb-$(CONFIG_DT_BCM9EJTAGPRB)		+= bcm9ejtagprb.dtb; dtb-$(CONFIG_DT_BCM97125CBMB)		+= bcm97125cbmb.dtb; dtb-$(CONFIG_DT_BCM97346DBSMB)		+= bcm97346dbsmb.dtb; dtb-$(CONFIG_DT_BCM97358SVMB)		+= bcm97358svmb.dtb; dtb-$(CONFIG_DT_BCM97360SVMB)		+= bcm97360svmb.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include bcm93384wvg.dtb, bcm93384wvg_viper.dtb, bcm96368mvwg.dtb, bcm9ejtagprb.dtb, bcm97125cbmb.dtb, bcm97346dbsmb.dtb, bcm97358svmb.dtb, bcm97360svmb.dtb, bcm97362svmb.dtb, bcm97420c.dtb, bcm97425svmb.dtb, bcm97435svmb.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
