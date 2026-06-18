# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_provider.c

Purpose: binds the mthca low-level HCA implementation to the Linux RDMA core verbs interface, including device/port queries, ucontext/PD/CQ/QP/SRQ/AH/MR verbs, sysfs attributes, and device registration.

Important APIs/functions: implements RDMA device ops such as `mthca_query_device`, `mthca_query_port`, `mthca_modify_device`, `mthca_modify_port`, `mthca_query_pkey`, `mthca_query_gid`, `mthca_alloc_ucontext`, `mthca_mmap_uar`, `mthca_alloc_pd`, `mthca_create_qp`, `mthca_create_cq`, `mthca_resize_cq`, `mthca_reg_user_mr`, `mthca_dereg_mr`, `mthca_register_device`, and `mthca_unregister_device`.

Control flow: query paths allocate SMP MAD mailboxes and call `mthca_MAD_IFC`. User context allocation creates a UAR, optional mem-free user DB table, and returns ABI data. Object creation validates udata/create flags, maps user doorbell pages when applicable, delegates allocation to lower-level CQ/QP/SRQ/MR/AH code, and copies object ids back to userspace. Registration initializes node data, composes base, SRQ, and Tavor/Arbel-specific `ib_device_ops`, registers with RDMA core, and starts catastrophic error polling.

State and persistence: manages RDMA core object lifetime and runtime mappings: UAR PFNs, user DB pages, CQ resize buffers, MRs with `ib_umem`, and sysfs-visible board/revision strings. No disk persistence exists.

Dependencies and integration: depends on RDMA core/uverbs ABI, MAD/SMP helpers, mthca command interface, mem-free doorbell mapping, lower-level CQ/QP/SRQ/MR/AH modules, and PCI device data.

Risks: userspace ABI validation and cleanup ordering are critical; partial failures after mapping doorbells must unmap both SQ/RQ or CQ DBs. CQ resize has concurrent poll/resize states. `mthca_reg_user_mr` supports old libmthca inputs with warnings. Device ops vary by mem-free versus Tavor and SRQ support, so missing ops would break verbs behavior.

Test signals: rdma-core verbs tests for query/create/modify/destroy, user MR registration and deregistration, CQ resize, mmap UAR, SRQ creation on supported hardware, sysfs attribute reads, and unload after active object churn.
