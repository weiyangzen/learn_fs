# sources/distributed-fs/ceph-client/include/linux/qed/qede_rdma.h

Purpose: defines the coupling contract between the QED Ethernet driver (`qede`) and the QED RoCE/RDMA driver (`qedr`). It lets the RDMA layer register callbacks for device add/remove and link/address/MTU events while keeping non-RDMA builds compilable through inline stubs.

Important APIs and types: `enum qede_rdma_event` classifies lifecycle and netdev events (`QEDE_UP`, `QEDE_DOWN`, `QEDE_CHANGE_ADDR`, `QEDE_CLOSE`, `QEDE_CHANGE_MTU`). `struct qede_rdma_event_work` wraps event workqueue state and payload. `struct qedr_driver` carries the RDMA driver's name and `add`, `remove`, and `notify` hooks. Public entry points are `qede_rdma_register_driver()`, `qede_rdma_unregister_driver()`, `qede_rdma_supported()`, and RDMA device/event helpers gated by `CONFIG_QED_RDMA`.

Control flow: a `qedr_driver` registers once; Ethernet device probing or recovery calls `qede_rdma_dev_add()`, which can invoke the driver's `add()` callback with QED, PCI, and netdev handles. Netdev open/close/address/MTU changes are forwarded through event helpers to RDMA notification paths, often via queued work.

State and persistence: this header owns no persistent state. Runtime state is the registered RDMA driver, per-device `qedr_dev` handles, and queued `qede_rdma_event_work`; all are kernel-lifetime or device-lifetime only.

Dependencies and integration points: depends on PCI, netdevice, workqueue, and QED/qede/qedr forward declarations. It integrates Ethernet link management, PCI function state, and RDMA upper-layer device registration.

Risks and test signals: risks include callback lifetime races during remove/recovery, event ordering across close/down/remove, and build drift between `CONFIG_QED_RDMA` and non-RDMA stubs. The disabled branch omits a stub for `qede_rdma_event_change_mtu()`, so call sites must be configuration-safe. Test by building both RDMA and non-RDMA configs and exercising netdev up/down, MAC address changes, MTU changes, PCI recovery, and module unregister with pending event work.
