# sources/distributed-fs/ceph-client/drivers/mailbox/qcom-cpucp-mbox.c

Purpose: implements the Qualcomm APSS CPUCP mailbox for X1E80100, exposing three IPC channels between APSS and CPUCP with separate TX and RX register spaces.

Important APIs/types/functions: `struct qcom_cpucp_mbox` owns three channels, controller, TX base, and RX base. `channel_number` derives the channel index. Ops are startup, shutdown, and send; `qcom_cpucp_mbox_irq_fn` handles RX interrupts.

Control flow: probe maps RX and TX windows, clears RX enable/clear/map registers, requests a high-triggered no-suspend IRQ, enables RX command mapping, and registers the controller. Startup sets the RX enable bit for the channel; shutdown clears it. TX writes one `u32` command to the per-channel TX command register. IRQ reads the 64-bit RX status, iterates supported channel bits, reads each command value, locks the channel to synchronize with `chan->cl`, delivers data only if a client is bound, clears the RX bit, and unlocks.

State and persistence: hardware enable/map/status registers hold live state. The driver stores no per-message data and no persistent settings.

Dependencies and integration: depends on DT `qcom,x1e80100-cpucp-mbox`, two MMIO resources, one IRQ, and the mailbox controller framework.

Risks: RX status is treated as a bitset limited to three channels; wider unexpected bits are ignored. The IRQ passes a stack-local `u32` pointer synchronously. There is no txdone indication, so sends are fire-and-forget.

Test signals: channel enable/disable on request/free, IRQ delivery with and without a bound client, RX clear ordering, and register-window ordering in DT.
