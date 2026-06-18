# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox.h

Purpose: declares the public AMD XDNA mailbox transport interface and resource descriptors used by AIE2 firmware message code.

Important APIs/types: opaque `struct mailbox` and `struct mailbox_channel` hide implementation details. `struct xdna_mailbox_msg` carries opcode, callback handle, response callback, send data, and send size. `struct xdna_mailbox_res` describes global ring-buffer and mailbox register mappings. `struct xdna_mailbox_chann_res` describes one channel direction's ring start/size and head/tail mailbox register offsets. Public functions create the mailbox, allocate/start/stop/free channels, and send messages.

Control flow: device bring-up obtains management channel descriptors from firmware SRAM, fills channel resources, starts the channel, then higher-level message helpers submit `xdna_mailbox_msg` requests and wait for callbacks.

State and persistence: the header defines handles and descriptors; runtime state lives in `amdxdna_mailbox.c`. Mailbox resources are MMIO/SRAM mappings supplied by the device.

Dependencies: DRM device for mailbox creation and Linux `void __iomem` conventions through users.

Risks: comments say oversized data may be split transparently, but implementation rejects packages larger than the ring and does not split, so API users must keep messages within ring size. `send_data` must be 4-byte aligned in size and first word cannot equal tombstone.

Test signals: compile coverage for all users, channel resource translation from firmware descriptors, send callback behavior for success, timeout, and stop paths, and validation of message-size assumptions.
