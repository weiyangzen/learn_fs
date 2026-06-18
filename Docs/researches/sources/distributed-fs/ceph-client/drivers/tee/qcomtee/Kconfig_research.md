# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/Kconfig

## Purpose
`qcomtee/Kconfig` defines the Qualcomm Trusted Execution Environment driver configuration.

## Important APIs, Types, And Functions
`config QCOMTEE` is a tristate labeled "Qualcomm TEE Support". It depends on Qualcomm architecture or compile testing, excludes big-endian CPUs, selects `QCOM_SCM`, and selects `QCOM_TZMEM_MODE_SHMBRIDGE`. The help text describes access to QTEE services, loaded Trusted Applications, and userspace supplicant services exported to QTEE.

## Control Flow And State
The Kconfig symbol controls whether the QCOMTEE composite object is built. Its selected dependencies configure the Qualcomm SCM and TZ memory bridge modes needed by the driver.

## Dependencies And Integration Points
The symbol integrates QCOMTEE with Qualcomm firmware call infrastructure (`QCOM_SCM`) and trusted-zone memory mode selection. It is consumed by the qcomtee Makefile.

## Risks
The driver is unavailable on big-endian builds. Selecting specific Qualcomm TZ memory mode may affect other Qualcomm secure memory users and should be validated in multi-driver configurations.

## Test Signals
Build with `ARCH_QCOM`, with `COMPILE_TEST`, and with big-endian disabled/enabled configurations to confirm dependency gating. Verify selected symbols appear in final configs.
