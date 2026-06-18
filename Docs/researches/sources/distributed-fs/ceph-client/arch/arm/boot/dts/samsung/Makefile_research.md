# sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/Makefile

Purpose: this Makefile is the ARM Samsung DTB build manifest for Exynos3/4/5, S3C64xx, and S5PV210 families.

Important API surface: it declares conditional `dtb-*` lists for `CONFIG_ARCH_EXYNOS3` (3 DTBs), `CONFIG_ARCH_EXYNOS4` (18), `CONFIG_ARCH_EXYNOS5` (22), `CONFIG_ARCH_S3C64XX` (2), and `CONFIG_ARCH_S5PV210` (7), totaling 52 DTB targets. It covers phones, tablets, Chromebook boards, Odroid boards, Samsung reference boards, and legacy S3C/S5PV210 boards.

Control flow: Kbuild evaluates each architecture symbol independently, so multi-platform configs may build several Samsung families in one `dtbs` run.

State and persistence: no runtime state. The file persists which board descriptions are generated and packaged.

Dependencies and integration: depends on same-directory DTS files and Samsung pinctrl binding headers such as `exynos-pinctrl.h`, `s3c64xx-pinctrl.h`, and `s5pv210-pinctrl.h`. It integrates with the parent ARM DTS build.

Risks and test signals: risks are stale board targets and accidental movement between config groups. Test with Samsung architecture configs enabled and review schema output for Exynos pinctrl and board bindings.
