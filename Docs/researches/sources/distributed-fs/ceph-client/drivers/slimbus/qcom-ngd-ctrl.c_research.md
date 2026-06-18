# sources/distributed-fs/ceph-client/drivers/slimbus/qcom-ngd-ctrl.c

## Purpose
This is the Qualcomm SLIMbus NGD controller driver. It bridges the generic SLIMbus core to Qualcomm Non-ported Generic Device hardware, using DMA message queues for SLIMbus packets, QMI to coordinate with the remote audio subsystem, runtime PM for power collapse, and SSR/PDR notifiers for remote processor restart handling.

## Important APIs, Types, And Functions
Important private state lives in `struct qcom_slim_ngd_ctrl`, which embeds `struct slim_controller`, a `struct slim_framer`, QMI state, DMA channels, descriptor rings, work items, runtime state, and restart locks. `struct qcom_slim_ngd` represents a child NGD platform device. The QMI request/response structs and `qmi_elem_info` tables encode select-instance and power messages.

Key functions include `qcom_slim_ngd_xfer_msg()`, `qcom_slim_ngd_xfer_msg_sync()`, `qcom_slim_ngd_enable_stream()`, `qcom_slim_ngd_get_laddr()`, `qcom_slim_ngd_power_up()`, `qcom_slim_ngd_runtime_resume()`, `qcom_slim_ngd_runtime_suspend()`, `qcom_slim_ngd_ssr_pdr_notify()`, and the parent/child probes `qcom_slim_ngd_ctrl_probe()` and `qcom_slim_ngd_probe()`.

## Control Flow
The parent controller probe maps NGD registers, requests the IRQ, registers SSR/PDR hooks, initializes SLIMbus controller callbacks, and creates a child platform device for the concrete NGD instance. The child probe enables runtime PM, starts QMI service lookup, and allocates the master worker queue.

When QMI service appears, `qcom_slim_ngd_up_worker()` enables the controller. Enable selects the SLIMbus hardware instance over QMI, resumes runtime PM, powers up the remote service, initializes DMA queues, enables RX/TX message queues, waits for capability exchange, then registers with the SLIMbus core. Transfers allocate a TX descriptor, optionally translate core connect/disconnect messages into Qualcomm user messages, write the packed message to the DMA buffer, submit TX DMA, and wait for completion. RX DMA callbacks parse replies and forward responses to `slim_msg_response()`.

## State, Persistence, And Dependencies
State is in memory and hardware registers only. DMA buffers are coherent allocations for RX and TX queues. TX ring indexes are protected by `tx_buf_lock`, serialized message submission uses `tx_lock`, and subsystem restart teardown uses `ssr_lock`. Runtime PM state transitions update `enum qcom_slim_ngd_state`. Dependencies include SLIMbus core, DMAengine, PM runtime, QMI, QRTR sockets, PDR, Qualcomm SSR notifier APIs, device tree, and platform IRQ/resources.

## Integration Points
The driver registers a `slim_controller` and supplies `xfer_msg`, `get_laddr`, `enable_stream`, and framer timing. It also consumes child DT nodes for SLIMbus devices, notifies `of_slim_get_device()` children after restart, maps two NGD compatibles, and exposes power state through runtime PM rather than userspace.

## Risks
Several paths mutate transaction fields or stream/channel state before final transfer success, so error unwinding can leave software state ahead of hardware. `qcom_slim_qmi_send_power_request()` does not check `qmi_txn_init()` before sending. DMA init failure after RX setup does not immediately unwind RX in `qcom_slim_ngd_init_dma()`. Error paths in TX allocation and user-message conversion can return without freeing an allocated descriptor or TID in all cases. SSR and runtime PM share controller state, making lock ordering and wakeup timing important.

## Test Signals
Useful signals include probe and QMI service discovery, runtime suspend/resume, SLIMbus device enumeration after SSR, DMA TX/RX completion, `slim_msg_response()` delivery for value and address replies, stream enable success on audio playback/capture, timeout logs for capability exchange or TX, and fault injection around missing DMA channels, QMI timeout, and remote processor restart.
