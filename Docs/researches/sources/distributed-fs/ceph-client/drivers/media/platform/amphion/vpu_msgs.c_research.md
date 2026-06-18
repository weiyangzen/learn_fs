<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.c

Purpose: handles firmware interrupt codes and RPC messages, routes instance messages through workqueues/FIFOs, invokes codec callbacks, and completes pending commands.

Important APIs/functions: exported `vpu_isr()`, `vpu_inst_run_work()`, `vpu_msg_run_work()`, and `vpu_msg_delayed_work()`. Internal handlers cover start/stop, memory request, sequence header, resolution change, encode done, frame request/release, input done, picture decoded/displayed, EOS, unsupported stream, firmware exception, skipped picture, and debug string messages.

Control flow: mailbox RX calls `vpu_isr()`, which completes core boot/snapshot completions for special IRQs, enqueues the IRQ code in the core FIFO, and schedules core work. Core work handles boot sync mailbox replies or drains RPC messages from firmware. Each message is converted to a common ID, matched to a live instance, used to advance command response state with `handled=0`, recorded in flow history, queued into the instance FIFO, and later processed in instance work. Instance handlers unpack payloads through iface ops, call codec `vpu_inst_ops`, and finally call `vpu_response_cmd(..., handled=1)`.

State and persistence: uses core and instance kfifo buffers plus workqueues. It can set `core->hang_mask` and V4L2 queue error state on firmware exceptions. No durable persistence.

Dependencies and integration: depends on `vpu_rpc.c` iface conversion/unpack hooks, `vpu_cmds.c` response tracking, `vpu_mbox.c` boot-sync sends, codec ops in `vdec.c`/`venc.c`, and V4L2 error helpers.

Risks: FIFO overflow drops messages and only logs. String termination reduces `hdr.num` when full but assumes data is word-addressable as a string. Message payload validity largely depends on firmware-specific unpackers. The two-phase command response model requires handler completion to run; if instance workqueue is unavailable, sync commands can time out.

Test signals: boot IRQ, snapshot IRQ, high-volume message FIFO pressure, every handler type, unsupported stream and firmware exception, instance close while messages are queued, delayed-work recovery for nonempty FIFOs, and command completion timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.c -->
