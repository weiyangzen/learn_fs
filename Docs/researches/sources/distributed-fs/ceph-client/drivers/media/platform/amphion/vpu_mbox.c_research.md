<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.c

Purpose: wraps Linux mailbox channels used to signal firmware command types/data and receive firmware IRQ codes.

Important APIs/functions: `vpu_mbox_init()` names `tx0`, `tx1`, and `rx`; `vpu_mbox_request()` opens all channels; `vpu_mbox_free()` releases them; `vpu_mbox_send_type()` and `vpu_mbox_send_msg()` transmit firmware notifications. `vpu_mbox_rx_callback()` forwards incoming mailbox words to `vpu_isr()`.

Control flow: runtime resume in `vpu_core.c` requests channels. Command submission writes data to shared memory then calls `vpu_mbox_send_type(COMMAND)`. Boot sync response sends PRC buffer offset, boot address, and INIT_DONE through `vpu_mbox_send_msg()`. Runtime suspend frees channels.

State and persistence: each `struct vpu_mbox` stores channel name, client, channel pointer, and blocking mode. No durable persistence.

Dependencies and integration: depends on Linux mailbox framework and `vpu_msgs.c` ISR path. Channel names must match device-tree mailbox names.

Risks: send helpers do not check `mbox_send_message()` return values or NULL channel pointers. RX callback assumes `msg` points to a `u32`. Failure to request any channel frees all channels and aborts runtime resume.

Test signals: mailbox DT binding validation, request/free across runtime suspend/resume, command interrupt delivery, boot sync sequence, RX callback with boot/snapshot/message codes, and failure injection for missing channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.c -->
