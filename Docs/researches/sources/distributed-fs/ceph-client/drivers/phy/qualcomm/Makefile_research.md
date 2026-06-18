# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/Makefile

This Makefile maps Qualcomm/Atheros PHY Kconfig symbols to object files. It is the build integration layer for the directory and directly controls which C drivers are compiled into built-in objects or modules.

Each `obj-$(CONFIG_...) += ...` line ties a Kconfig symbol to one or more object files. Simple mappings include `PHY_ATH79_USB` to `phy-ath79-usb.o`, `PHY_QCOM_APQ8064_SATA` to `phy-qcom-apq8064-sata.o`, `PHY_QCOM_EDP` to `phy-qcom-edp.o`, `PHY_QCOM_EUSB2_REPEATER` to `phy-qcom-eusb2-repeater.o`, and IPQ-specific USB/SATA objects. QMP combo deliberately builds both `phy-qcom-qmp-combo.o` and `phy-qcom-qmp-usbc.o`.

State is build-system state only. Dependencies are the Linux kbuild convention and Kconfig symbols defined nearby. Integration risks are missing object entries for new Kconfig symbols, stale entries after file renames, or multi-object symbols omitting companion objects. Test signals are compile coverage from enabled configs and link failures if symbols or objects drift.
