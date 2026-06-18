# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-ipc.c

Purpose: AMD ACP IPC transport implementation between host and SOF firmware through scratch mailbox memory and DSP software interrupts.

Important APIs/types/functions: `acp_mailbox_write()`/`acp_mailbox_read()` wrap scratch memory access. `acp_sof_ipc_send_msg()` acquires the ACP hardware semaphore, writes host mailbox data, marks host message pending, triggers host-to-DSP interrupt, and releases the semaphore. `acp_sof_ipc_irq_thread()` handles DSP messages, replies, boot-time panic, runtime panic, and probe position interrupts. `acp_sof_ipc_msg_data()` reads stream or DSP mailbox data. `acp_set_stream_data_offset()` validates and stores per-stream position offsets.

Control flow: send path busy-waits on hardware semaphore, copies IPC payload into `host_box`, sets the host flag in scratch, triggers `DSP_SW_INTR_TRIG`, and unlocks. IRQ thread handles first boot specially, then checks `sof_dsp_msg_write` for incoming messages and `sof_dsp_ack_write` for replies. Replies are read from host mailbox except PM context-save/gate replies, where windows may be powered off and a synthetic success reply is used.

State and persistence: uses scratch IPC flags in `scratch_ipc_conf`, `sdev->msg`, `sdev->ipc_lock`, and per-stream `posn_offset`. Probe position state is stored in `adata->probe_stream->cstream_posn`.

Dependencies and integration points: SOF IPC core (`snd_sof_ipc_msgs_rx`, `snd_sof_ipc_reply`, panic handling), ACP scratch helpers from `acp.c`, compressed probe streams, and firmware-defined scratch mailbox layout.

Risks: semaphore acquisition is a spin/busy wait with fixed retry count. Reply size checks exempt probe commands, which need separate coverage. Position offsets must remain aligned and inside `stream_box`; bad firmware offsets are rejected. Boot-time mailbox windows differ before `FW_READY`.

Test signals: IPC round trips, PM IPC special cases, firmware panic IRQs, probe capture position updates, and timeout dump output.
