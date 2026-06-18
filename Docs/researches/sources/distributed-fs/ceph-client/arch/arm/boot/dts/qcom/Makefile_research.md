# sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/Makefile

Purpose: this Kbuild fragment enumerates 32-bit Qualcomm ARM DTBs under `CONFIG_ARCH_QCOM`.

Important API surface: a single `dtb-$(CONFIG_ARCH_QCOM)` list contains 60 DTBs spanning MSM8226/MSM8926 phones, APQ8016/APQ806x/APQ8074 boards, IPQ4018/IPQ4019/IPQ8064 networking platforms, MSM8916 devices, MSM8960/MSM8974 phones/tablets, MDM9615, and SDX55/SDX65 modem platforms.

Control flow: Kbuild appends the full list when the architecture config is enabled. No custom commands or overlay composition are present.

State and persistence: the file holds build inventory only. Generated DTBs become persistent artifacts consumed by bootloaders and distro packages.

Dependencies and integration: depends on same-directory Qualcomm DTS/DTSI files and the parent ARM DTS build. It is also coupled to naming conventions used by firmware loaders and packaging scripts.

Risks and test signals: with many product DTBs, risks are misspellings, removed DTS files still listed, or new boards omitted from the build. Test with `CONFIG_ARCH_QCOM=y` and `make ARCH=arm dtbs`; verify every listed board source exists and schema warnings are reviewed.
