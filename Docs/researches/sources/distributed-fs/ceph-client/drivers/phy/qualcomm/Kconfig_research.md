# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/Kconfig

This Kconfig file defines build-time feature symbols for Qualcomm and Atheros PHY drivers. It covers small legacy drivers (`PHY_ATH79_USB`, APQ8064/IPQ SATA, IPQ USB), display/eDP (`PHY_QCOM_EDP`), QMP subdrivers under `menuconfig PHY_QCOM_QMP`, USB HS/SS/HSIC/QUSB2/M31/eUSB2 drivers, and Ethernet SGMII.

Control flow is Kconfig dependency resolution: symbols constrain architecture, OF, IOMEM, COMMON_CLK, USB, EXTCON, NVMEM, PCI, TYPEC, and DRM availability, and select `GENERIC_PHY` or other helper subsystems where required. The nested QMP menu uses `default PHY_QCOM_QMP` so enabling the parent can expose specific QMP families. Some entries default on for ATH79 if platform EHCI/OHCI is enabled.

State is persisted in kernel `.config`, not runtime code. Integration points are the top-level PHY build, Makefile object selection, module availability, and DT binding compatibility. Risks include dependency mismatches causing unavailable drivers for compile-test, built-in/module conflicts noted around EXTCON, and legacy QMP USB compatibility choices. Test signals are `allyesconfig`, `allmodconfig`, architecture defconfigs, and object inclusion matching `Makefile`.
