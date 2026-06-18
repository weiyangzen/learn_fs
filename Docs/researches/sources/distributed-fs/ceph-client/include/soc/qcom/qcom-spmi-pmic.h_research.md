# sources/distributed-fs/ceph-client/include/soc/qcom/qcom-spmi-pmic.h

Purpose: provides Qualcomm SPMI PMIC subtype/fabric constants and the PMIC identity structure used by child drivers to tailor behavior to exact PMIC revisions.

Important APIs/types/functions: defines many `*_SUBTYPE` constants, PMIC fabric IDs such as `PMI8998_FAB_ID_*` and `PM660_FAB_ID_*`, `struct qcom_spmi_pmic` with type, subtype, revision, fab ID, and name, and `qcom_pmic_get(struct device *dev)`.

Control flow: PMIC MFD code identifies the device, stores identity data, and consumers call `qcom_pmic_get()` from child devices to branch on subtype or revision.

State and persistence: the header owns no state. PMIC identity persists in the provider device data after SPMI probe.

Dependencies and integration: depends on `linux/device.h`. Used by `drivers/mfd/qcom-spmi-pmic.c` and consumers such as RRADC and other PMIC subdevice drivers.

Risks: subtype values are hardware ABI. Wrong constants or failed lookup can select invalid calibration, scaling, or quirks. Test signals include SPMI PMIC probe logs, child-device lookup, subtype-specific ADC/regulator behavior, and builds across PMIC families.
