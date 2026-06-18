<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.h

Purpose: declares the firmware interrupt/message work entry points used by mailbox and core initialization.

Important APIs: `vpu_isr()` receives a firmware IRQ word for a core. `vpu_inst_run_work()`, `vpu_msg_run_work()`, and `vpu_msg_delayed_work()` are workqueue callbacks for instance and core message draining.

Control/state behavior: header has no state; the implementation operates on core/instance FIFOs and workqueue structs embedded in `vpu_core` and `vpu_inst`.

Dependencies and integration: implemented in `vpu_msgs.c`; called by `vpu_mbox.c` RX callback and assigned during core/instance workqueue initialization.

Risks and test signals: build-contract risk only. Runtime signals are correct IRQ-to-workqueue routing and message delivery to active instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.h -->
