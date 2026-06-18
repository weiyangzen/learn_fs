# sources/distributed-fs/ceph-client/drivers/tee/optee/smc_abi.c

## Purpose
`smc_abi.c` implements the OP-TEE SMC/HVC transport backend. It probes device-tree OP-TEE nodes, selects SMC or HVC conduit, optionally loads OP-TEE firmware, exchanges ABI capabilities, configures dynamic or reserved shared memory, registers client/supplicant TEE devices, handles SMC RPC loops, manages shared-memory registration/cache, async notification IRQs, protected memory, and platform remove/shutdown.

## Important APIs, Types, And Functions
Parameter conversion uses `optee_to_msg_param()`/`optee_from_msg_param()` and helpers for temporary memory (`TMEM`) and registered memory (`RMEM`). Dynamic `tee_shm` uses RMEM; static/private buffers use physical TMEM and optional noncontiguous page lists.

Shared-memory support includes `optee_enable_shm_cache()`, `optee_disable_shm_cache()`, `optee_disable_unmapped_shm_cache()`, page-list allocation/filling helpers, `optee_shm_register()`/`optee_shm_unregister()` for dynamic user SHM, supplicant register/unregister no-op variants, and page-based pool ops. Registration uses `OPTEE_MSG_CMD_REGISTER_SHM` with `OPTEE_MSG_ATTR_NONCONTIG`.

RPC handling includes SMC register RPC allocation/free, foreign interrupt acknowledgement, command RPC dispatch through `handle_rpc_func_cmd()`, and call-context cleanup for temporary page lists. `optee_smc_do_call_with_arg()` selects `OPTEE_SMC_CALL_WITH_REGD_ARG`, `OPTEE_SMC_CALL_WITH_RPC_ARG`, or `OPTEE_SMC_CALL_WITH_ARG`, emits tracepoints, loops on thread-limit and RPC returns, and uses `optee_call_queue`.

Async notification support reads pending values with `OPTEE_SMC_GET_ASYNC_NOTIF_VALUE`, sends normal notification keys to `optee_notif_send()`, and runs bottom-half work through threaded IRQ or per-CPU IRQ workqueue. Probe support includes API UID/revision checks, OS revision fetch, capability exchange, thread count query, static SHM config mapping, conduit selection, optional insecure image loading, static/dynamic protected-memory pool setup, and backend driver registration.

## Control Flow And State
Probe flow reads the DT `method`, optionally loads firmware, validates OP-TEE API UID/revision, gets thread count and capabilities, chooses dynamic SHM if supported or reserved SHM otherwise, allocates `struct optee`, creates/registers client and supplicant TEE devices, initializes call queue, supplicant, SHM arg cache, internal context, notifications, optional IRQs/protected memory, disables stale SHM cache, enables cache when needed, enumerates devices, and registers RPMB notifier work.

Runtime secure calls enter through `optee_smc_do_call_with_arg()`. The call preserves resume registers across RPCs, services normal-world RPCs, waits when secure-world threads are exhausted, and wakes another waiter on exit. Remove/shutdown disable SHM cache when applicable, stop notifications, call common removal, unmap reserved SHM, and free `optee`.

Persistent state includes reserved SHM mapping (`memremaped_shm`), secure capability bits, notification IRQ/per-CPU structures, CPU hotplug state, call queue counts, RPC param count, SHM arg cache, and common OP-TEE state.

## Dependencies And Integration Points
This file integrates with ARM SMCCC, device tree platform driver binding `linaro,optee-tz`, IRQ domains, CPU hotplug, firmware loader, memory remapping, TEE dynamic SHM helpers, static reserved SHM pools, tracepoints, RPMB, protected-memory DMA heaps, and all common OP-TEE modules.

## Risks
SMC register contracts are fragile; pointer and physical address high/low register pairs must be preserved exactly. The SHM cache can return stale pointers after kexec, so the probe’s unmapped-cache drain is important. The optional `OPTEE_INSECURE_LOAD_IMAGE` path explicitly weakens the secure boot model and uses GFP_DMA memory due to TF-A 32-bit mapping limits. `handle_rpc_func_cmd_shm_free()` sets bad-parameter for invalid type but then unconditionally sets `TEEC_SUCCESS`, which can mask invalid SHM free type errors. Per-CPU IRQ setup uses a static `pcpu_irq_num`, assuming at most one SMC ABI firmware instance.

## Test Signals
Probe with SMC and HVC methods, missing/invalid DT method, incompatible UID/revision, dynamic SHM, reserved SHM, no SHM, and varying capability bits. Run secure calls that produce thread-limit, alloc/free RPC, command RPC, and foreign interrupt returns. Test async notifications on normal and per-CPU IRQs, CPU hotplug, shutdown/kexec cache draining, protected-memory static/dynamic setup, and malformed SHM free RPCs.
