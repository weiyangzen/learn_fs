<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/ipc.c

## Purpose
Mailbox IPC transport for host-to-DSP CATPT commands, immediate replies, delayed replies, firmware-ready notification, stream position/glitch notifications, and firmware coredump requests.

## APIs, Types, and Functions
Exports `catpt_ipc_init()`, `catpt_dsp_send_msg_timeout()`, `catpt_dsp_send_msg()`, `catpt_dsp_irq_handler()`, and `catpt_dsp_irq_thread()`. Important internals include `catpt_ipc_arm()`, `catpt_ipc_msg_init()`, `catpt_dsp_send_tx()`, `catpt_wait_msg_completion()`, `catpt_dsp_do_send_msg()`, `catpt_dsp_notify_stream()`, `catpt_dsp_copy_rx()`, and `catpt_dsp_process_response()`.

## Control Flow, State, and Persistence
Initialization sets default 300 ms timeout, locks, and completions but leaves IPC not ready until firmware sends a ready notification. Firmware ready provides inbox/outbox offsets and sizes, allocates the RX buffer, copies config into `ipc->config`, marks IPC ready, and completes `cdev->fw_ready`. Sends are serialized by `ipc->mutex`; the spinlock clears reply state, copies payload to outbox, and sets IPCC busy. Completion waits first for immediate done, then for delayed busy reply if the initial response status is `CATPT_REPLY_PENDING`. IRQ top half handles host-done replies through IPCC and wakes the threaded handler for DSP-busy messages through IPCD; the thread handles notifications, delayed replies, coredump requests, and interrupt unmasking.

## Dependencies and Integration
Depends on CATPT packed message formats, MMIO mailbox helpers, tracepoints, Linux completion/locking, and stream helpers from `pcm.c`. The firmware loader waits on `fw_ready`, message wrappers in `messages.c` use `catpt_dsp_send_msg()`, and stream notifications call back into ALSA position handling.

## Risks and Test Signals
Risks include IPC becoming permanently not ready on timeout with recovery left as TODO, reply payload copying only for success status, request/reply size validation tied to firmware outbox size, delayed reply timeout ambiguity, and notifications for streams already removed. Test signals are firmware-ready completion, successful command/reply traces, delayed reply handling for stream messages, position notifications driving period elapsed, timeout path disabling IPC, and coredump request path producing a dump without IRQ storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/ipc.c -->
