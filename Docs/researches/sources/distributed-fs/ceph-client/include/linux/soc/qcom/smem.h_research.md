# sources/distributed-fs/ceph-client/include/linux/soc/qcom/smem.h

Purpose: This header exposes Qualcomm Shared Memory APIs for allocating and retrieving SMEM items shared with remote processors.

Important APIs/types/functions: It defines `QCOM_SMEM_HOST_ANY` and declares `qcom_smem_is_available`, `qcom_smem_alloc`, `qcom_smem_get`, `qcom_smem_get_free_space`, `qcom_smem_get_soc_id`, `qcom_smem_get_feature_code`, and `qcom_smem_bust_hwspin_lock_by_host`.

Control flow: Consumers check availability, allocate or retrieve host/item entries, read sizes, query SoC/feature IDs, and optionally recover a stuck hardware spinlock for a remote host.

State and persistence: SMEM allocations live in shared memory and may persist across subsystem restarts. Hardware spinlocks protect shared metadata.

Dependencies and integration: Integrates with Qualcomm SMEM core, hwspinlock, socinfo, remoteproc, modem/adsp/wcnss clients, and boot firmware.

Risks and test signals: Wrong host/item IDs can corrupt shared protocol data. Spinlock busting is dangerous and should be exceptional. Test availability before probe, allocation races, size validation, socinfo queries, and remote restart behavior.
