# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/vf/Makefile

Purpose: this Kbuild fragment lists Vybrid VF500/VF610 board DTBs.

Important API surface: `dtb-$(CONFIG_SOC_VF610)` appends 14 outputs, including Colibri VF500/VF610 variants, `vf610-bk4`, `vf610-cosmic` and `vf610m4-cosmic`, `vf610-twr`, and multiple ZII boards such as `vf610-zii-dev-rev-b`, `vf610-zii-dev-rev-c`, `vf610-zii-scu4-aib`, `vf610-zii-spb4`, and SSMB variants.

Control flow: Kbuild conditionally emits the list for `CONFIG_SOC_VF610`. There are no composite overlay rules.

State and persistence: no runtime state. It persists the board DTB inventory for the VF610 SoC family.

Dependencies and integration: depends on matching `.dts` files and shared VF610 DTSI/pin binding data such as `vf610-pinfunc.h`. Parent ARM DTS Kbuild includes this fragment.

Risks and test signals: stale entries fail `make dtbs`; missing entries break board packaging. Test with a VF610-enabled config and ensure all listed DTBs build cleanly.
