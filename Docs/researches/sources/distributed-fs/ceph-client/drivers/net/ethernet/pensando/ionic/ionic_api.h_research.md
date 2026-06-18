# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_api.h

Purpose: Declares the Ionic API surface shared with auxiliary clients, especially RDMA, and describes admin-command, interrupt, and CMB allocation contracts.

Important APIs/types/functions: `struct ionic_aux_dev` embeds an `auxiliary_device` and points back to the Ethernet LIF. `struct ionic_admin_ctx` carries a completion plus 64-byte admin command and 16-byte completion storage. `struct ionic_intr_info` records IRQ name, index/vector, rearm count, DIM coalescing value, affinity mask, and affinity notifier. Exported APIs include `ionic_adminq_post_wait()`, `ionic_error_to_errno()`, `ionic_request_rdma_reset()`, `ionic_intr_alloc/free()`, and `ionic_get_cmb()/ionic_put_cmb()`.

State and persistence: This header defines ownership boundaries for objects allocated in the Ethernet driver but used by auxiliary devices. CMB page reservations persist until explicitly returned by page id and order.

Dependencies and integration: Includes Linux auxiliary bus support plus Ionic firmware/register ABIs. `ionic_aux.c`, `ionic_dev.c`, and `ionic_lif.c` implement or export these symbols under namespace `NET_IONIC`.

Risks and test signals: API users must pair interrupt and CMB allocation/free calls and must not outlive the parent LIF/auxiliary device. Tests should cover RDMA-capable and non-RDMA devices, auxiliary unbind during reset, CMB exhaustion, interrupt affinity updates, and admin command timeout/error mapping.
