# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/Makefile

## Purpose

`tcpm/qcom/Makefile` builds the Qualcomm PMIC TCPM adapter as one composite module.

## Important APIs, Types, and Functions

`obj-$(CONFIG_TYPEC_QCOM_PMIC) += qcom_pmic_tcpm.o` selects the module. `qcom_pmic_tcpm-y` links `qcom_pmic_typec.o`, `qcom_pmic_typec_port.o`, `qcom_pmic_typec_pdphy.o`, and `qcom_pmic_typec_pdphy_stub.o`.

## Control Flow

There is no runtime control flow. Kbuild uses the composite object list to link the platform driver and both real/stub PD PHY providers into the same module.

## State and Persistence Behavior

The file controls build artifacts only. It has no runtime state.

## Dependencies and Integration Points

It integrates the Qualcomm PMIC platform driver, Type-C port block, PD PHY block, and no-PD-PHY stub under the `TYPEC_QCOM_PMIC` symbol.

## Risks and Test Signals

Risks include missing object updates when the driver split changes and ensuring the stub is always linked for PMI632-like devices without a PD PHY. Test signals are module link checks for `CONFIG_TYPEC_QCOM_PMIC=m/y` and compatible probing for both PM8150B and PMI632 resource sets.
