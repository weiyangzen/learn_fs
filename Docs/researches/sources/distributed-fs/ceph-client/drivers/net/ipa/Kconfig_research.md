# sources/distributed-fs/ceph-client/drivers/net/ipa/Kconfig

## Purpose
`ipa/Kconfig` defines the build-time configuration symbol for the Qualcomm IPA network driver. It presents `CONFIG_QCOM_IPA` as a tristate option and records the platform, subsystem, and helper dependencies required to build the driver.

## Important APIs, types, and functions
There are no C APIs or functions. The important interface is the `config QCOM_IPA` symbol. It depends on networking, Qualcomm SMEM, Qualcomm architecture or compile-test, interconnect support, compatible remoteproc/common and AOSS QMP settings, and selects the MDT loader, SCM, and QMI helper libraries.

## Control flow
Kconfig resolution determines whether `drivers/net/ipa/Makefile` contributes `ipa.o` to the build. The help text constrains expected use to Qualcomm IPA hardware and notes that the selection type must match `QCOM_Q6V5_COMMON`.

## State and persistence
Kconfig state persists only in the kernel build configuration. It determines compilation and module/built-in linkage, not runtime driver data.

## Dependencies and integration points
The symbol gates all IPA source under the folder and ties the network driver to Qualcomm firmware loading, secure monitor calls, QMI messaging, remoteproc, AOSS QMP, and interconnect infrastructure.

## Risks and test signals
Risks include dependency mismatches where IPA is built without compatible remoteproc/Q6 support, unmet selected helpers in unusual compile-test configurations, and user confusion around built-in vs module linkage matching `QCOM_Q6V5_COMMON`. Test signals include `olddefconfig` dependency resolution, `COMPILE_TEST` builds on non-QCOM architectures, module and built-in build combinations, and runtime probe on supported Qualcomm SoCs.
