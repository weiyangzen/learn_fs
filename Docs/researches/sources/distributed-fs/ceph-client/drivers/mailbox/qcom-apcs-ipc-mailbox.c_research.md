# sources/distributed-fs/ceph-client/drivers/mailbox/qcom-apcs-ipc-mailbox.c

Purpose: implements Qualcomm APCS IPC doorbell mailboxes for many Qualcomm SoCs. It exposes 32 bit-indexed channels that send a single bit to an APCS/global register and optionally registers a related APCS clock-controller child device.

Important APIs/types/functions: `struct qcom_apcs_ipc` stores the mailbox controller, 32 channels, regmap, IPC offset, and optional clock platform device. `struct qcom_apcs_ipc_data` supplies SoC-specific offset and clock-controller name. `qcom_apcs_ipc_send_data` is the only mailbox op.

Control flow: probe maps MMIO, wraps it in a regmap, reads match data, assigns each channel's `con_priv` to its bit index, registers the mailbox controller, and optionally creates a clock-controller platform device using either a child `clock-controller` node or the APCS node fwnode. Sending writes `BIT(index)` to the configured offset. Remove unregisters the optional clock child.

State and persistence: no RX or txdone state is tracked. The only persistent runtime object beyond the controller is the optional clock platform device.

Dependencies and integration: depends on numerous Qualcomm DT compatibles, regmap-mmio, mailbox framework default index xlate, and platform clock-controller drivers that bind to the created child.

Risks: the controller has no completion or RX path; clients must treat sends as fire-and-forget. Match-data offsets are SoC-specific and wrong reuse can ring the wrong doorbell; the source contains an explicit warning not to add more entries using existing data blindly.

Test signals: compatible-specific offset tests, child clock-controller registration, one-shot bit writes for all channel indices, and probe/remove with and without clock child nodes.
