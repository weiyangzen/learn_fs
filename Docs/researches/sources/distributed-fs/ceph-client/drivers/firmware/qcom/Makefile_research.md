# sources/distributed-fs/ceph-client/drivers/firmware/qcom/Makefile

## Purpose
The Makefile maps Qualcomm firmware configuration symbols to object files.

## Important Build Rules
- `obj-$(CONFIG_QCOM_SCM) += qcom-scm.o`
- `qcom-scm-objs += qcom_scm.o qcom_scm-smc.o qcom_scm-legacy.o`
- `obj-$(CONFIG_QCOM_TZMEM) += qcom_tzmem.o`
- `obj-$(CONFIG_QCOM_QSEECOM) += qcom_qseecom.o`
- `obj-$(CONFIG_QCOM_QSEECOM_UEFISECAPP) += qcom_qseecom_uefisecapp.o`

## Control Flow And Integration
The SCM composite object always links the main API/probe file with both modern SMCCC and legacy call transports, allowing runtime convention probing. TZMem, QSEECOM, and the UEFI client are independent objects governed by their Kconfig dependencies.

## State And Persistence
No runtime state is defined here; the file controls linkage and module composition.

## Risks
Dropping one of the SCM transport objects would break runtime fallback for platforms that require that convention. Enabling QSEECOM without the main SCM object being built in is prevented by Kconfig, not this Makefile.

## Test Signals
Build output should show the composite `qcom-scm` object containing the three SCM source objects. Link failures around SCM transport functions or QSEECOM exports point to mismatched config dependencies or object lists.
