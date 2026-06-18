# sources/distributed-fs/ceph-client/drivers/reset/reset-qcom-aoss.c

Purpose: Qualcomm SDM845 AOSS reset provider for subsystem restart lines.

Important APIs/types/functions: `struct qcom_aoss_reset_map`, `struct qcom_aoss_desc`, `struct qcom_aoss_reset_data`, `sdm845_aoss_resets[]`, `qcom_aoss_control_assert()`, `qcom_aoss_control_deassert()`, `qcom_aoss_control_reset()`, and `qcom_aoss_reset_probe()`.

Control flow: OF match supplies a descriptor of restart register offsets. Probe maps MMIO and registers reset lines. Assert writes 1 to the mapped register and waits 200-300 us; deassert writes 0 and waits the same; reset is assert followed by deassert.

State and persistence: AOSS restart registers hold state during operation; no software cache.

Dependencies and integration: platform driver, OF, MMIO, dt-bindings for SDM845 AOSS resets, reset framework.

Risks and test signals: sleep duration encodes six 32 kHz cycles and must fit hardware requirements. Test all subsystem IDs, register offsets, reset pulse timing, and client subsystem restart behavior.
