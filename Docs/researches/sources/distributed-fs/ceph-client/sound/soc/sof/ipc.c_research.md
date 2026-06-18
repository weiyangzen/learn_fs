<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc.c

## Purpose
Generic SOF IPC core that selects IPC3 or IPC4 ops, serializes outbound messages, tracks replies, exposes common IPC send helpers, and shuts IPC down safely during device removal.

## Important APIs, Types, and Functions
Exports `sof_ipc_send_msg()`, `sof_ipc_tx_message()`, `sof_ipc_set_get_data()`, `sof_ipc_tx_message_no_pm()`, `snd_sof_ipc_get_reply()`, `snd_sof_ipc_reply()`, `snd_sof_ipc_init()`, and `snd_sof_ipc_free()`. Important state lives in `struct snd_sof_ipc`, `struct snd_sof_ipc_msg`, `ipc->tx_mutex`, `sdev->ipc_lock`, `msg->waitq`, `msg->ipc_complete`, and `ipc->disable_ipc_tx`.

## Control Flow, State, and Persistence
`snd_sof_ipc_init()` allocates IPC state, initializes serialization and waitqueue state, selects `ipc3_ops` or `ipc4_ops` from `sdev->pdata->ipc_type`, validates mandatory op groups, calls optional init, then stores the ops. `sof_ipc_send_msg()` requires firmware boot complete and TX enabled, initializes the shared message object under spinlock, points `sdev->msg` at it, and invokes the platform send op. Replies are read by IPC-version-specific `get_reply()` and completed by `snd_sof_ipc_reply()`. `snd_sof_ipc_free()` disables TX under the mutex and calls optional IPC exit.

## Dependencies and Integration
Depends on `sof-priv.h`, `sof-audio.h`, SOF platform ops, and compiled IPC3/IPC4 support. It is the integration point between higher-level PCM/control/topology code and low-level HDA/Atom/other transport send/receive callbacks.

## Risks and Test Signals
Risks include single shared message state requiring strict TX serialization, unexpected replies being ignored, firmware-state checks rejecting late cleanup IPCs, and missing mandatory ops causing probe failure. Test signals are IPC flood tests, timeout handling, reply-size validation in IPC3/IPC4, removal while IPCs are in flight, and probe failure paths for unsupported IPC versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc.c -->
