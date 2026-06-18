# sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/Makefile

Purpose: this Kbuild fragment enumerates 32-bit Rockchip DTBs.

Important API surface: `dtb-$(CONFIG_ARCH_ROCKCHIP)` lists 45 targets covering RV1103/RV1108/RV1109/RV1126 boards, RK3036, RK3066a, RK3128, RK3188, RK3228/RK3229, and many RK3288 boards including Firefly, MiQi, Popmetal, Rock2, Rock Pi N8, Tinker, and Veyron Chromebook variants.

Control flow: Kbuild includes the list when `CONFIG_ARCH_ROCKCHIP` is enabled. No composite targets are defined.

State and persistence: no runtime state. The persistent artifact is the build graph for Rockchip board DTBs.

Dependencies and integration: depends on matching DTS files, shared Rockchip DTSI files, pinctrl/GPIO bindings, and parent ARM DTS Makefile recursion.

Risks and test signals: high board count means stale target risk and incomplete board coverage. Test `make ARCH=arm dtbs` for Rockchip, and validate that Veyron and RK3288 variants remain separately built because they often differ in regulators, panels, and peripherals.
