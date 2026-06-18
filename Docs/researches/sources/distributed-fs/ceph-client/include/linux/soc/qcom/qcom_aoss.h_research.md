# sources/distributed-fs/ceph-client/include/linux/soc/qcom/qcom_aoss.h

Purpose: This header defines the Qualcomm Always-On Subsystem QMP interface used for low-power mode and always-on resource messages.

Important APIs/types/functions: It declares opaque `struct qmp` and helpers to get/put a QMP channel and send AOSS/QMP messages, with disabled stubs in non-enabled builds.

Control flow: Consumers obtain a QMP handle from a device or phandle, send command strings/messages to AOSS, and release the handle when done.

State and persistence: The QMP core owns mailbox/transport state. AOSS keeps resource votes or low-power configuration until updated.

Dependencies and integration: Integrates with Qualcomm mailbox/QMP, power domains, regulators, remoteproc, and system suspend code.

Risks and test signals: Message strings are firmware contracts; typos can silently fail or leave stale votes. Test missing provider, timeout/error returns, suspend/resume messaging, and multiple consumers sharing QMP.
