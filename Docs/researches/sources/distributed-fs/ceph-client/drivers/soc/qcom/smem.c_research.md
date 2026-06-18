# sources/distributed-fs/ceph-client/drivers/soc/qcom/smem.c

## Purpose

`smem.c` implements the Qualcomm Shared Memory Manager. It maps SMEM reserved memory, validates global or partitioned heap formats, exports allocation/lookup/free-space/physical-address helpers, exposes SoC id and feature code from SMEM socinfo, and registers a `qcom-socinfo` child device.

## Important APIs, Types, and Functions

Exported APIs include `qcom_smem_alloc()`, `qcom_smem_get()`, `qcom_smem_get_free_space()`, `qcom_smem_virt_to_phys()`, `qcom_smem_get_soc_id()`, `qcom_smem_get_feature_code()`, `qcom_smem_is_available()`, and `qcom_smem_bust_hwspin_lock_by_host()`. The file defines firmware layouts for global TOC entries, partition tables, partition headers, private entries, SMEM info, and regions. Runtime state is the singleton `struct qcom_smem *__smem`.

## Control Flow

Probe resolves the primary reserved memory or `memory-region`, optional RPM MSG RAM, maps the header and partition table, validates SBL initialization, acquires the hwspinlock, computes global heap size, determines SMEM version, remaps either global heap or global partition, enumerates private partitions for APPS, sets `__smem`, and registers socinfo. Allocation takes the hwspinlock, rejects bootloader-fixed items, chooses a private partition, global partition, or legacy global heap, creates an entry, orders writes with `wmb()`, and releases the lock. Lookup walks the selected heap without taking the lock, validating canaries and bounds.

## State and Persistence Behavior

SMEM items are shared-memory allocations visible to multiple processors and persist until reboot. The allocator is append-only; items are not freed. `__smem` is process-global and transitions from `-EPROBE_DEFER` to a live pointer or `-ENODEV`. Partition metadata, free offsets, and TOC entries are persistent shared-memory state and must remain consistent for remote firmware.

## Dependencies and Integration Points

Dependencies include reserved-memory/OF resources, write-combine IO mapping, hwspinlock, platform devices, Qualcomm socinfo, and public SMEM headers. Major consumers include `smp2p.c`, `qcom_stats.c`, remoteproc drivers, socinfo, and many Qualcomm subsystem drivers.

## Risks and Edge Cases

Readers do not take the hwspinlock, so allocation write ordering is critical. `qcom_smem_bust_hwspin_lock_by_host()` dereferences `__smem` without checking `IS_ERR()`. Partition mapping uses 32-bit `phys_addr` in some helpers despite `phys_addr_t` regions. Legacy/global and partition formats have many bounds checks, but malformed firmware tables can still produce invalid mappings or duplicate hosts. `qcom_smem_virt_to_phys()` assumes `__smem` is live. The allocator never reclaims memory.

## Test Signals

Test uninitialized SBL header, unsupported SMEM versions, missing hwspinlock, partition magic/version/size/host failures, duplicate partitions, global partition item count, allocation existing/full/fixed-item cases, private cached and uncached lookup, aux region lookup, free-space sanity, socinfo id/feature code, hwspinlock bust, and early consumers receiving `-EPROBE_DEFER`.
