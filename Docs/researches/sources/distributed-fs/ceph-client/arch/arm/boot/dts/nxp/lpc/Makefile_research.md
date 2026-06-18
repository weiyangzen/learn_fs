# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/lpc/Makefile

Purpose: this Kbuild fragment selects NXP LPC ARM device-tree blobs for the kernel DTB build. It maps six DTBs to two architecture configuration symbols.

Important API surface: `dtb-$(CONFIG_ARCH_LPC18XX)` adds `lpc4337-ciaa.dtb`, `lpc4350-hitex-eval.dtb`, `lpc4357-ea4357-devkit.dtb`, and `lpc4357-myd-lpc4357.dtb`. `dtb-$(CONFIG_ARCH_LPC32XX)` adds `lpc3250-ea3250.dtb` and `lpc3250-phy3250.dtb`. The Kbuild variable names are consumed by the ARM `dtbs` target.

Control flow: Kbuild evaluates the `CONFIG_ARCH_*` symbols and appends matching DTB targets. There is no shell logic or custom rule.

State and persistence: no runtime state is held. The persistent effect is the build manifest: enabled configs determine which DTBs are generated and shipped.

Dependencies and integration: depends on matching `.dts` files in the same directory and on the parent ARM DTS Makefile descending into `nxp/lpc`. It integrates with kernel configuration and packaging flows that collect generated DTBs.

Risks and test signals: stale names break `make dtbs`; missing entries leave boards without installable DTBs. Test with configs enabling LPC18xx and LPC32xx, and verify every listed `.dts` target exists.
