# sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_tzmem.h

## Purpose
This header defines a Qualcomm TrustZone memory pool API. It provides controlled allocation of memory intended for secure firmware interactions and optional shared-memory bridge registration.

## APIs, types, and control flow
`enum qcom_tzmem_policy` selects static, multiplier growth, or on-demand growth. `struct qcom_tzmem_pool_config` supplies initial size, increment, maximum size, and growth policy. Callers create pools with `qcom_tzmem_pool_new()` or `devm_qcom_tzmem_pool_new()`, allocate with `qcom_tzmem_alloc(pool, size, gfp)`, free with `qcom_tzmem_free()`, and translate virtual allocation addresses with `qcom_tzmem_to_phys()`. `DEFINE_FREE(qcom_tzmem, ...)` enables cleanup-based release. With `CONFIG_QCOM_TZMEM_MODE_SHMBRIDGE`, bridge create/delete calls register physical ranges with secure firmware; otherwise they are harmless no-ops.

## State and dependencies
Pool state is opaque and implementation-owned. Allocation lifetime is tied to explicit free or devres for devm pools. Dependencies include cleanup helpers, GFP allocation context, physical addresses, and SCM shared-memory bridge support.

## Integration, risks, and tests
QSEECOM, QTEE, PAS, and secure-memory callers can use this to avoid ad hoc DMA buffer handling. Risks are freeing memory while firmware still owns it, using the no-op bridge stubs as proof of secure isolation, exceeding max growth, and calling physical translation on invalid pointers. Tests should cover policy growth boundaries, devm cleanup, phys conversion, allocation failure under GFP constraints, and bridge enabled/disabled behavior.
