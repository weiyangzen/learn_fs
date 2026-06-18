# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/resources.c

Purpose: shared mlx5 vDPA hardware resource and command utility layer. It allocates protection/doorbell resources, wraps create/destroy commands for TIS/RQT/TIR/TD/mkeys, initializes the control VQ IOTLB, and batches async commands.

Important APIs/types/functions: `mlx5_vdpa_alloc_resources()` allocates UAR, optional user context, PD, null mkey, maps the kick BAR page, and initializes CVQ `vringh` IOTLB. `mlx5_vdpa_free_resources()` releases those in reverse. Command wrappers create/destroy TIS, RQT, TIR, transport domains, and mkeys with the vDPA UID. `mlx5_vdpa_exec_async_cmds()` issues arrays of mlx5 commands using async callbacks with fallback when throttled.

Control flow: allocation validates `res->valid`, obtains resources stepwise, and unwinds on each failure. Async command execution initializes completions, issues until all submitted or error, waits for outstanding completions, and records per-command completion errors.

State and persistence: `mlx5_vdpa_resources` stores PD number, UAR, kick MMIO mapping/physical address, UID, null mkey, and valid flag. CVQ owns a vhost IOTLB and lock. Async command structs carry input/output buffers, completion, and result.

Dependencies and integration: consumed by mlx5 vnet and MR code. Uses mlx5 core command API, HCA capabilities, UAR pages, ioremap, vhost IOTLB, vringh, and async command context.

Risks: resource allocation order is strict; missing unwind can leak UAR/PD/uctx mappings. `create_uctx()` returns success without setting UID when `umem_uid_0` is supported, relying on UID 0 semantics. Async throttling falls back to synchronous command execution only in the external-throttle case.

Test signals: allocation/free under all failure injection points, devices with/without `umem_uid_0`, kick BAR mapping, CVQ IOTLB allocation, async batches larger than firmware command capacity, and destroy after partial initialization.
