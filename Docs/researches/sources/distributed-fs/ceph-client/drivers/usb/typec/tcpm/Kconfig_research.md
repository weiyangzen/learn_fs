# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/Kconfig

## Purpose

`tcpm/Kconfig` declares build-time options for the USB Type-C Port Controller Manager and its TCPCI/FUSB302/WCOVE/Qualcomm PMIC controller drivers.

## Important APIs, Types, and Functions

The key symbols are `TYPEC_TCPM`, `TYPEC_TCPCI`, `TYPEC_RT1711H`, `TYPEC_MT6360`, `TYPEC_TCPCI_MT6370`, `TYPEC_TCPCI_MAXIM`, `TYPEC_FUSB302`, `TYPEC_WCOVE`, and `TYPEC_QCOM_PMIC`. Dependencies and selects wire in USB, I2C, regmap-I2C, power-supply, USB role-switch, ACPI, MFD support, DRM HPD bridge support, and Qualcomm architecture/compile-test coverage.

## Control Flow

There is no runtime control flow. Kconfig gates which modules are available, nests vendor TCPCI drivers under `TYPEC_TCPCI`, and restricts all controller options to the `TYPEC_TCPM` block.

## State and Persistence Behavior

Configuration state is persisted in the kernel `.config`, affecting which object files are built in or modular. It does not create runtime state directly.

## Dependencies and Integration Points

It integrates TCPM drivers with the kernel build system and dependency graph. `TYPEC_FUSB302` and `TYPEC_QCOM_PMIC` select `DRM_AUX_HPD_BRIDGE` when the DRM bridge and OF dependencies are available, matching their runtime HPD bridge allocation.

## Risks and Test Signals

Risks include missing dependency/select updates when drivers gain new subsystems, vendor drivers hidden by parent symbols, and compile-test gaps for platform-specific options. Test signals include `allyesconfig`, `allmodconfig`, `COMPILE_TEST` for Qualcomm PMIC, and building each module combination with parent symbols enabled/disabled.
