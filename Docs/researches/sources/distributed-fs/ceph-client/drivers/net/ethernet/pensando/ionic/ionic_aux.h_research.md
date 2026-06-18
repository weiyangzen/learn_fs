# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_aux.h

Purpose: Declares auxiliary bus lifecycle hooks for Ionic LIFs.

Important APIs/types/functions: Exposes `ionic_auxbus_register(struct ionic_lif *lif)` and `ionic_auxbus_unregister(struct ionic_lif *lif)`.

Control flow: PCI/LIF setup calls register after netdev/devlink setup, and remove/reset paths call unregister before tearing down queues and LIF state.

State and dependencies: The header intentionally hides `struct ionic_aux_dev`; callers only pass the parent LIF. It depends on the LIF definition being available to C files including it.

Risks and test signals: Build coverage should verify callers compile with RDMA auxiliary support selected by Kconfig. Runtime tests should confirm unregister is idempotent when no RDMA capability created an auxiliary device.
