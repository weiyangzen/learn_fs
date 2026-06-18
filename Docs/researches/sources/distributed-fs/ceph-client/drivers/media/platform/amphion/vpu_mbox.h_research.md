<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.h

Purpose: declares mailbox lifecycle and send helpers for core code and command/message code.

Important APIs: `vpu_mbox_init()`, `vpu_mbox_request()`, `vpu_mbox_free()`, `vpu_mbox_send_msg()`, and `vpu_mbox_send_type()`.

Control/state behavior: no state in header; functions operate on a `struct vpu_core` containing three `struct vpu_mbox` channels.

Dependencies and integration: implemented by `vpu_mbox.c`, called from core runtime PM, command send, and boot-sync message handling.

Risks and test signals: header drift is build-visible. Runtime validation is mailbox request, command signaling, and cleanup on suspend/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.h -->
