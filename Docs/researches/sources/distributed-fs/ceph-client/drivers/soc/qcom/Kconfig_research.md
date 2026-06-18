# sources/distributed-fs/ceph-client/drivers/soc/qcom/Kconfig

## Purpose
Defines build options for Qualcomm SoC support drivers, including command DB, APR/GPR, interconnect bandwidth monitor, inline crypto engine, and Kryo L2 accessors covered by this subset.

## Important APIs, Types, And Functions
Kconfig symbols relevant here are `QCOM_COMMAND_DB`, `QCOM_KRYO_L2_ACCESSORS`, `QCOM_APR`, `QCOM_ICC_BWMON`, and `QCOM_INLINE_CRYPTO_ENGINE`. The file also declares many adjacent Qualcomm subsystem options.

## Control Flow
Each symbol gates the corresponding Makefile object. Dependencies encode required frameworks: command DB needs OF reserved memory; APR needs RPMSG and NET and selects PDR helpers; BWMON selects PM OPP and REGMAP_MMIO; ICE selects QCOM SCM; Kryo accessors require ARM64.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
This file binds Qualcomm architecture or compile-test builds to mailbox/RPMSG, PM OPP, reserved memory, SCM, MTD-like platform services, and remoteproc-related helpers.

## Risks
Several entries are helper symbols without prompts or are selected by other drivers, so dependency mistakes can surface as link errors in unrelated Qualcomm subsystems. `QCOM_RPMH` explicitly allows command DB built-in/module combinations through `(QCOM_COMMAND_DB || !QCOM_COMMAND_DB)`.

## Test Signals
Kconfig tests should verify enabled symbols produce the matching objects and required selected dependencies without circular or unmet dependency warnings.
