# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_aux.c

Purpose: Registers an auxiliary RDMA child device for RDMA-capable Ionic LIFs and exports an RDMA-triggered LIF reset command.

Important APIs and flow: `ionic_auxbus_register()` checks `IONIC_LIF_CAP_RDMA`, allocates `struct ionic_aux_dev`, assigns an ID from a global IDA, initializes an auxiliary device named `rdma`, parents it to the PCI device, and adds it to the auxiliary bus. `ionic_auxbus_unregister()` serializes with `lif->adev_lock`, deletes and uninitializes the child, and clears `lif->ionic_adev`. `ionic_auxbus_release()` frees the ID and wrapper memory. `ionic_request_rdma_reset()` sends `IONIC_CMD_RDMA_RESET_LIF` under `dev_cmd_lock` and is exported in namespace `NET_IONIC`.

State and persistence: The auxiliary device persists while the LIF is registered and RDMA capability is present. IDA state persists globally across devices until release callbacks run.

Dependencies and integration: Depends on the auxiliary bus, LIF state from `ionic_lif.h`, device command helpers from `ionic_dev.c`, and external RDMA drivers binding to the auxiliary device.

Risks and test signals: Lifetime depends on `auxiliary_device_uninit()` eventually invoking release; use-after-free risks center on RDMA clients during reset/remove. Test RDMA-capable probe/remove, repeated register/unregister, auxiliary add failure, ID reuse, reset requests while firmware is down, and lock ordering with `adev_lock` and `dev_cmd_lock`.
