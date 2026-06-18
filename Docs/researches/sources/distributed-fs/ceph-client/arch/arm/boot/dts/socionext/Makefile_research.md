# sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/Makefile

Purpose: this Makefile lists Socionext Milbeaut and UniPhier ARM DTBs.

Important API surface: `dtb-$(CONFIG_ARCH_MILBEAUT)` adds `milbeaut-m10v-evb.dtb`. `dtb-$(CONFIG_ARCH_UNIPHIER)` adds 10 UniPhier boards: LD4, LD6b, Pro4, Pro5, PXs2, and SLD8 reference/evaluation variants.

Control flow: Kbuild appends targets based on the two architecture config symbols. There are no overlay composition rules.

State and persistence: no mutable state. The persistent behavior is build inclusion of the listed DTBs.

Dependencies and integration: depends on same-directory DTS files and shared Socionext DTSI includes. Parent ARM DTS Kbuild consumes the fragment.

Risks and test signals: risk is limited to missing or stale target names and incorrect config gating. Test `make dtbs` for Milbeaut and UniPhier configs and ensure all listed sources exist.
