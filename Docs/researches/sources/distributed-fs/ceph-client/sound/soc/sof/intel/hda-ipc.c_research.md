# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ipc.c

Purpose: `hda-ipc.c` implements the common cAVS 1.5 HDA IPC register protocol and generic IPC4 variant used by shared HDA platforms. It handles message sending, delayed D0I3 scheduling, IRQ-thread reply/notification processing, mailbox/window offsets, stream position reads, IPC IRQ detection, dumps, and IPC4 transmit-busy checks.

Important APIs: exported functions include `hda_dsp_ipc_send_msg()`, `hda_dsp_ipc4_schedule_d0i3_work()`, `hda_dsp_ipc4_send_msg()`, `hda_dsp_ipc_get_reply()`, `hda_dsp_ipc4_irq_thread()`, `hda_dsp_ipc_irq_thread()`, `hda_dsp_check_ipc_irq()`, mailbox/window offset helpers, `hda_ipc_msg_data()`, `hda_set_stream_data_offset()`, `hda_ipc4_dsp_dump()`, `hda_check_ipc_irq()`, `hda_ipc_irq_dump()`, `hda_ipc_dump()`, `hda_ipc4_dump()`, and `hda_ipc4_tx_is_busy()`.

Control flow: IPC3 send writes the mailbox and sets HIPCI BUSY. IPC4 send checks the chip-specific request register; if busy, it stores `hdev->delayed_ipc_tx_msg`, otherwise writes payload to mailbox if present, writes extension and primary registers, and schedules D0I3 work for non-PM IPC4 messages. IRQ threads read DONE/BUSY registers, mask relevant interrupts, process replies under `ipc_lock`, route notifications through `snd_sof_ipc_msgs_rx()`, handle panic magic with boot retry awareness, acknowledge DSP or host done, and resend delayed IPC4 messages after ACK.

State and persistence behavior: mutable state includes current `sdev->msg`, reply/rx data pointers, stream mailbox position offsets, `hda->code_loading`, wait queue wakeups for CLDMA, `hdev->delayed_ipc_tx_msg`, D0I3 delayed work, and chip-specific IPC register fields.

Dependencies and integration: it depends on SOF IPC core, HDA DSP register definitions, telemetry dump code, tracepoints, and the code-loader CLDMA wait path.

Risks and test signals: risks include reply-before-FW_READY races, delayed IPC pointer lifetime, panic recoverability during boot attempts, stream private-data closure races, and interrupt masking order. Test IPC3 and IPC4 command/reply, firmware notifications, panic IRQ handling, CLDMA wakeups, D0I3 work scheduling suppression for PM messages, stream position mailbox offsets, and debug dumps after stuck IPC.
