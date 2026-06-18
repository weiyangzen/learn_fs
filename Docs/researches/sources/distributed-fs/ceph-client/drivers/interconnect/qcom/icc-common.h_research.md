# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-common.h

Purpose: header exposing Qualcomm extended interconnect OF translation.

Important APIs/types/functions: declares `qcom_icc_xlate_extended()`.

Control flow: Qualcomm providers include this header and set the function as their extended xlate callback before registration.

State and persistence: no state.

Dependencies/integration: `linux/interconnect-provider.h` and `icc-common.c`.

Risks and test signals: compile-test all Qualcomm provider users for prototype/export drift.
