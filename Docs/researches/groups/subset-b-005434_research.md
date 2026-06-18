# Research: subset-b-005434

Grouped research for AMD-TEE, OP-TEE, and Qualcomm TEE driver files under `sources/distributed-fs/ceph-client/drivers/tee`. Each source section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/amdtee_private.h -->
# sources/distributed-fs/ceph-client/drivers/tee/amdtee/amdtee_private.h

## Purpose
`amdtee_private.h` is the private contract for the AMD-TEE Linux driver. It defines driver identity, selected GlobalPlatform return codes, session limits, firmware TA path conventions, per-device/per-context state containers, shared-memory bookkeeping, TA reference bookkeeping, session-id packing helpers, and internal function prototypes shared by AMD-TEE core, PSP command, and shared-memory pool code.

## Important APIs, Types, And Functions
The main service type is `struct amdtee`, which binds a client `tee_device` to a `tee_shm_pool`. `struct amdtee_context_data` is attached to each `tee_context` and persists two lists: `sess_list` for TA sessions and `shm_list` for mapped buffers, with `shm_mutex` protecting shared-memory entries. `struct amdtee_session` tracks a loaded TA handle, kref lifetime, up to `TEE_NUM_SESSIONS` per-TA `session_info` values, and a bitmap protected by a spinlock. `struct amdtee_shm_data` maps a kernel virtual address to the PSP/TEE buffer id returned by `TEE_CMD_ID_MAP_SHARED_MEM`. `struct amdtee_ta_data` is used by the command layer to maintain global TA load reference counts.

`set_session_id()`, `get_ta_handle()`, and `get_session_index()` encode a synthetic Linux session id: lower 16 bits carry the TA handle and upper 16 bits carry the per-TA session slot. Prototypes expose TEE core callbacks (`amdtee_open_session()`, `amdtee_close_session()`, `amdtee_invoke_func()`, `amdtee_cancel_req()`), shared-memory hooks (`amdtee_map_shmem()`, `amdtee_unmap_shmem()`, `amdtee_config_shm()`, `get_buffer_id()`), and lower-level PSP command wrappers (`handle_load_ta()`, `handle_open_session()`, `handle_invoke_cmd()`, etc.).

## Control Flow And State
The header’s key state model is two-tiered. Per Linux TEE context, `amdtee_context_data` owns the active session list and mapped shared-memory list. Separately, the command layer keeps a global `amdtee_ta_data` list keyed by TA handle to avoid unloading a TA while multiple sessions still reference it. Session ids are not opaque PSP ids; they are driver-packed values that must remain consistent with bitmap slot allocation in `core.c`.

## Dependencies And Integration Points
The file depends on Linux TEE core types, list/mutex/spinlock/kref primitives, bitmaps, and AMD PSP command structure definitions from `amdtee_if.h`. Its prototypes are implemented in `core.c`, `call.c`, and `shm_pool.c`, and its exported semantics must match the generic `/dev/tee*` core callbacks.

## Risks
The 16-bit TA handle encoding (`LOWER_TWO_BYTE_MASK`) assumes TA handles fit the lower two bytes; if firmware returns wider meaningful handles, session lookup can alias. Shared-memory lookup by `kaddr` also assumes unique live mappings per context. The session limit is hard-coded to 32 per TA instance, so overflow paths must reliably close the just-opened firmware session and unload the TA reference.

## Test Signals
Useful signals include opening more than 32 sessions to one TA, opening sessions to multiple TAs in one context, releasing a context with live sessions and mapped buffers, mapping/unmapping shared memory repeatedly, and injecting PSP command failures to ensure session and TA reference cleanup stays balanced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/amdtee_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/call.c -->
# sources/distributed-fs/ceph-client/drivers/tee/amdtee/call.c

## Purpose
`call.c` translates Linux TEE core operations into AMD PSP TEE command packets. It handles parameter marshaling, TA load/unload reference tracking, shared-memory map/unmap requests, open/close session commands, and invoke-command calls.

## Important APIs, Types, And Functions
`tee_params_to_amd_params()` converts `struct tee_param` arrays into `struct tee_operation`, packs parameter types four bits at a time, rejects meta parameters and invalid attributes, maps memrefs through `get_buffer_id()`, and only preserves value fields `a` and `b` because AMD TEE does not support value `c`. `amd_params_to_tee_params()` copies output/inout values back to Linux TEE params, updating output memref offsets/sizes and zeroing unsupported value `c`.

`handle_load_ta()` validates a page-aligned TA blob, sends `TEE_CMD_ID_LOAD_TA`, updates `arg->ret`/`arg->ret_origin`, and stores a driver-packed session id if a TA handle was allocated. `handle_unload_ta()` decrements the global TA reference list and sends `TEE_CMD_ID_UNLOAD_TA` only when the count reaches zero. `handle_open_session()`, `handle_close_session()`, and `handle_invoke_cmd()` wrap `TEE_CMD_ID_OPEN_SESSION`, `TEE_CMD_ID_CLOSE_SESSION`, and `TEE_CMD_ID_INVOKE_CMD`. `handle_map_shmem()` constructs a PSP scatter/gather list from page-aligned kernel virtual addresses and returns the firmware buffer id; `handle_unmap_shmem()` retires that id.

## Control Flow And State
Open-session flow starts with a loaded TA handle already placed in `arg->session` by `handle_load_ta()`. `handle_open_session()` marshals parameters, calls firmware, records returned `session_info`, and copies output params back. Invocation follows the same marshal, PSP command, unmarshal flow using the Linux session’s TA handle and the `session_info` slot value stored in `core.c`.

TA persistence is managed by a static `ta_list` protected by `ta_refcount_mutex`. Each successful TA load increments or creates an `amdtee_ta_data` entry; unload decrements and only sends the PSP unload command on the last reference. Shared-memory state itself is held in `core.c`; this file only sends firmware map/unmap commands and returns buffer ids.

## Dependencies And Integration Points
This file integrates with `linux/psp-tee.h` through `psp_tee_process_cmd()` and physical address conversion via `__psp_pa()`. It relies on `amdtee_if.h` command structures and the generic Linux TEE parameter representation. It is called by `core.c` session and shared-memory callbacks and by `shm_pool.c` indirectly through `amdtee_map_shmem()`.

## Risks
Parameter conversion assumes values fit in 32 bits and silently discards value `c`, which can break TAs expecting full GP value semantics. `handle_load_ta()` returns 0 even when firmware reports a GP error in `arg->ret`, so callers must always inspect `arg->ret`. `handle_unload_ta()` returns `-EBUSY` for non-final references, which is expected internally but can look like a command failure if reused carelessly. `handle_map_shmem()` allocates one command structure and writes `count` scatter entries without local visible bounds checking against the command’s array capacity.

## Test Signals
Exercise all GP parameter types accepted by the driver, including output memrefs and inout values; verify value `c` behavior is documented for callers. Fault-inject PSP transport failures and nonzero firmware statuses. Stress concurrent TA opens/closes to validate `ta_refcount_mutex` and ensure final unload happens exactly once. Validate map rejection for unaligned addresses and non-page-aligned sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/core.c -->
# sources/distributed-fs/ceph-client/drivers/tee/amdtee/core.c

## Purpose
`core.c` registers the AMD-TEE device with the Linux TEE subsystem and implements context lifecycle, TA firmware loading, session management, shared-memory bookkeeping, and TEE driver callbacks.

## Important APIs, Types, And Functions
`amdtee_get_version()` reports `TEE_IMPL_ID_AMDTEE` with GP generic capability. `amdtee_open()` allocates `amdtee_context_data`, initializes session and shared-memory lists, and stores it on `ctx->data`. `amdtee_release()` closes all tracked sessions by calling `release_session()`, destroys the shared-memory mutex, and frees context data.

`copy_ta_binary()` derives the firmware path `/amdtee/<uuid>.bin` from the requested TA UUID, serializes firmware loading with `drv_mutex`, rounds size to a page, allocates page memory, and copies the TA binary. `amdtee_open_session()` enforces public login, loads the TA, allocates or references an `amdtee_session`, opens a PSP session, assigns the first free bitmap slot, and rewrites `arg->session` to the driver-packed id. `amdtee_close_session()` removes a session slot, closes the firmware session, unloads the TA reference, and drops the kref. `amdtee_invoke_func()` validates the packed session id and invokes the command with the stored `session_info`.

`amdtee_map_shmem()` and `amdtee_unmap_shmem()` call firmware map/unmap helpers and maintain the context `shm_list`. `get_buffer_id()` looks up a firmware buffer id by the `tee_shm` kernel address. `amdtee_driver_init()` checks PSP TEE availability, allocates driver state, creates a shared-memory pool, allocates/registers a TEE device, and stores global `drv_data`. `amdtee_driver_exit()` unregisters the device and frees the pool.

## Control Flow And State
Every opened Linux context owns its own session list. Multiple sessions for the same TA share one `amdtee_session` object in that context, with a kref incremented by `alloc_session()` and decremented on close. `session_list_mutex` serializes context session-list lookup/mutation, while each session’s spinlock protects the bitmap and slot arrays. Shared-memory entries persist until `amdtee_unmap_shmem()` removes them from `ctxdata->shm_list`.

Driver initialization persists global `drv_data` and the registered `tee_device` until module exit. Session release on context close iterates every session object and closes every set bitmap slot, then unloads the TA for each slot.

## Dependencies And Integration Points
The file is the Linux TEE core integration point through `tee_driver_ops`, `tee_desc`, `tee_device_alloc()`, and `tee_device_register()`. It depends on firmware loading (`request_firmware()`), AMD PSP availability (`psp_check_tee_status()`), PSP command helpers from `call.c`, and the shared-memory pool from `shm_pool.c`.

## Risks
`copy_ta_binary()` uses `roundup(fw->size, PAGE_SIZE)` and page allocation but does not zero the padding after the firmware size; firmware consumers must tolerate padded content. `destroy_session()` unlocks `session_list_mutex` via `kref_put_mutex()` semantics, so callers must not alter the locking pattern casually. `amdtee_driver_exit()` unregisters and frees the pool but does not free the allocated `amdtee` or `drv_data`, which is a teardown leak in this source. Shared-memory context entries are not explicitly drained in `amdtee_release()`, so normal TEE core ordering must ensure SHM objects are freed before context teardown.

## Test Signals
Boot/probe with PSP TEE absent and present. Open/close sessions under concurrency and force error paths after TA load, after session allocation, and after PSP open-session. Release a context with live sessions to validate cleanup. Run kmemleak/module unload checks for `amdtee` and `drv_data`. Allocate and free shared memory across multiple contexts and ensure `get_buffer_id()` never crosses contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/shm_pool.c -->
# sources/distributed-fs/ceph-client/drivers/tee/amdtee/shm_pool.c

## Purpose
`shm_pool.c` implements AMD-TEE’s page-backed `tee_shm_pool`. It allocates zeroed kernel pages, translates their physical address for the PSP, maps them into AMD TEE firmware, and unmaps/frees them when the TEE core releases shared memory.

## Important APIs, Types, And Functions
`pool_op_alloc()` computes an allocation order from the requested size, allocates zeroed pages with `__get_free_pages()`, fills `tee_shm.kaddr`, `paddr`, and page-rounded `size`, then calls `amdtee_map_shmem()`. If mapping fails, it frees the pages and clears `kaddr`. `pool_op_free()` calls `amdtee_unmap_shmem()` and frees the pages using the stored size. `pool_op_destroy_pool()` frees the pool object. `amdtee_config_shm()` allocates a `tee_shm_pool` and assigns the AMD pool ops.

## Control Flow And State
The pool itself has no independent allocation list. State is stored in each `tee_shm` plus the per-context mapping list maintained by `core.c`. Allocation order determines the final shared-memory size, which may be larger than requested. The firmware buffer id is acquired as part of allocation and retired before physical pages are returned.

## Dependencies And Integration Points
This file depends on Linux TEE core pool callbacks, page allocator APIs, AMD PSP physical address translation (`__psp_pa()`), and `amdtee_map_shmem()`/`amdtee_unmap_shmem()` from `core.c` and `call.c`. It is consumed by `amdtee_driver_init()`.

## Risks
The `align` argument is intentionally ignored because page allocation is assumed sufficient; future callers requiring larger alignment would not get it. `get_order(size)` rounds up, so callers must respect `shm->size` rather than the requested size. Unmap failure is not represented because `amdtee_unmap_shmem()` returns void.

## Test Signals
Allocate sizes below, equal to, and above one page and verify `shm->size` and PSP map size. Inject map failure and ensure pages are freed. Confirm unmap is called exactly once on free and that repeated allocations do not leave stale `shm_list` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/shm_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/Kconfig

## Purpose
`Kconfig` defines OP-TEE driver build options: the main OP-TEE TEE driver, an optional insecure firmware image loading mode, and a static protected-memory pool helper option.

## Important APIs, Types, And Functions
`config OPTEE` is a tristate depending on `HAVE_ARM_SMCCC`, `MMU`, and a satisfiable `RPMB || !RPMB` expression. It enables the OP-TEE Trusted Execution Environment driver. `config OPTEE_INSECURE_LOAD_IMAGE` is an ARM64-only boolean behind `OPTEE` that loads `optee/tee.bin` as firmware during probe. `config OPTEE_STATIC_PROTMEM_POOL` is an internal bool defaulting to yes when `HAS_IOMEM` and `TEE_DMABUF_HEAPS` are enabled.

## Control Flow And State
These symbols control compile-time inclusion and code paths. `OPTEE_INSECURE_LOAD_IMAGE` activates firmware loading support in `smc_abi.c`. `OPTEE_STATIC_PROTMEM_POOL` enables static protected-memory pool setup in the same backend. `OPTEE` controls the module/object build through the Makefile.

## Dependencies And Integration Points
The options integrate with ARM SMCCC, MMU, RPMB availability, arm64 firmware loading, I/O memory mapping, and TEE DMA-BUF heap support. The warning text points readers to OP-TEE and Trusted Firmware-A threat documentation because image loading from the kernel materially changes the trust model.

## Risks
The insecure image loading option is explicitly dangerous: loading BL32 from filesystem firmware makes kernel/rootfs integrity part of the secure-world boot path. Build coverage for protected memory depends on a default-y internal symbol, so platforms without `HAS_IOMEM` or `TEE_DMABUF_HEAPS` silently lose that path.

## Test Signals
Validate builds with OP-TEE as built-in, module, and disabled. Build ARM64 with and without `OPTEE_INSECURE_LOAD_IMAGE`. Confirm protected-memory code is compiled only when expected and that RPMB-disabled configurations still allow OP-TEE to build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/Makefile

## Purpose
The OP-TEE Makefile defines the module object composition and a compile include path needed by trace generation.

## Important APIs, Types, And Functions
`obj-$(CONFIG_OPTEE) += optee.o` builds the composite OP-TEE object. `optee-objs` includes common core/session code (`core.o`, `call.o`), notification/RPC/supplicant/device support (`notif.o`, `rpc.o`, `supp.o`, `device.o`), protected memory (`protmem.o`), and both transport backends (`smc_abi.o`, `ffa_abi.o`). `CFLAGS_smc_abi.o := -I$(src)` lets the tracing framework find `optee_trace.h` when compiling `smc_abi.o`.

## Control Flow And State
There is no runtime state in this file. It guarantees both SMC and FF-A backend code are linked into the same OP-TEE driver object, with runtime probing deciding which ABI registers successfully.

## Dependencies And Integration Points
The file integrates with Kbuild composite object rules and the Linux trace event header-generation convention used by `CREATE_TRACE_POINTS` in `smc_abi.c`.

## Risks
Backend files are always part of `optee.o`; compile-time dependencies must therefore be guarded internally where optional subsystems are not reachable. Removing the trace include flag can break trace header discovery.

## Test Signals
Run kernel build targets with `CONFIG_OPTEE=m` and `CONFIG_OPTEE=y`, and include a build with tracing enabled to confirm `optee_trace.h` remains discoverable for `smc_abi.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/call.c -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/call.c

## Purpose
`call.c` implements OP-TEE generic TEE operations above the transport-specific ABI. It manages secure-world thread admission, cached shared-memory argument buffers, session open/close/invoke/cancel, system-session thread reservation, memory-type validation, and simple internal OP-TEE commands.

## Important APIs, Types, And Functions
`optee_cq_init()`, `optee_cq_wait_init()`, `optee_cq_wait_for_completion()`, and `optee_cq_wait_final()` implement a fairness queue for calls into OP-TEE. They optionally track secure thread counts and prioritize system-thread sessions when one secure thread should be reserved. `optee_cq_incr_sys_thread_count()` and `_decr_...()` adjust the number of sessions needing system-thread priority.

`optee_shm_arg_cache_init()`, `optee_get_msg_arg()`, `optee_free_msg_arg()`, and `optee_shm_arg_cache_uninit()` manage reusable shared-memory pages that hold `struct optee_msg_arg` plus optional RPC argument space. Cache behavior is controlled by `OPTEE_SHM_ARG_ALLOC_PRIV` and `OPTEE_SHM_ARG_SHARED`.

`optee_open_session()` constructs an `OPTEE_MSG_CMD_OPEN_SESSION` message with two meta parameters, converts client params through the selected backend ops, calls secure world, records successful sessions in `optee_context_data`, and copies output params back. `optee_close_session_helper()` sends close to secure world; `optee_close_session()` removes and frees the local session first. `optee_invoke_func()` and `optee_cancel_req()` validate the session and issue command/cancel messages. `optee_system_session()` marks a session as using a reserved system thread when possible.

`optee_check_mem_type()` rejects user memory mappings that are not normal cacheable memory before registering them with OP-TEE. `optee_do_bottom_half()` and `optee_stop_async_notif()` send simple internal commands via `simple_call_with_arg()`.

## Control Flow And State
Session state is per context in `ctxdata->sess_list`, protected by `ctxdata->mutex`. Every secure-world call obtains an argument buffer from the cache, fills an OP-TEE message, calls `optee->ops->do_call_with_arg()`, then returns the cache slot. The selected ABI backend supplies transport-specific parameter conversion and call mechanics.

The call queue persists at `optee->call_queue`. If a finite thread count is known, entering a call decrements `free_thread_count` or waits; exiting increments it and wakes another waiter. System sessions cause normal sessions to leave a thread available when needed.

## Dependencies And Integration Points
This file depends on `optee_private.h`, `optee_msg.h`, Linux TEE core helpers, UUID/client-login helpers, VMA iteration, architecture page attribute definitions, and backend ops from `smc_abi.c` or `ffa_abi.c`. It is used by both client and supplicant devices registered by each ABI backend.

## Risks
`optee_open_session()` calls `optee_close_session()` if output parameter conversion fails after a secure session was created; any bug in session-list insertion or conversion can leak or double-close. The argument cache logs but continues if freeing a non-free entry or clearing an already-free bit, so memory corruption symptoms may be delayed. Memory-type checking is architecture-specific and compile errors on unsupported architectures. `system_thread` is only initialized if a session lookup succeeds; the current flow returns on failed lookup before use, so that invariant must be preserved.

## Test Signals
Stress concurrent open/invoke/close with finite thread counts and system-session reservation. Validate cached argument reuse with `rpc_param_count` zero and nonzero. Fault-inject backend conversion failures after successful secure calls. Register user memory from normal and device mappings to test `optee_check_mem_type()`. Exercise cancellation and bottom-half commands through both SMC and FF-A backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/core.c -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/core.c

## Purpose
`core.c` provides OP-TEE module initialization, common context lifecycle, device enumeration, RPMB integration, sysfs attributes, revision reporting, and shared removal logic used by both SMC and FF-A transports.

## Important APIs, Types, And Functions
`optee_get_revision()` formats the OP-TEE OS revision stored in `optee->revision`. `optee_open()` allocates per-context session state and has special handling for the privileged supplicant TEE device: only one supplicant context may be active, and first open schedules device enumeration. `optee_release()` and `optee_release_supp()` close all sessions through `optee_release_helper()`, with the supplicant release also aborting pending supplicant RPCs.

`optee_enumerate_devices()` opens a client context, opens the device-enumeration PTA, queries device UUIDs with `PTA_CMD_GET_DEVICES*`, allocates a kernel buffer for the returned UUID list, and registers `tee_client_device` instances on `tee_bus_type`. `optee_unregister_devices()` removes registered `optee-ta-*` devices. `optee_bus_scan_rpmb()` and `optee_rpmb_intf_rdev()` rescan RPMB-dependent devices when RPMB devices appear. `optee_set_dev_group()` attaches sysfs groups showing RPMB routing model.

`optee_remove_common()` performs transport-independent teardown: unregister RPMB notifier, cancel work, unregister TEE client devices, uninitialize notifications and SHM arg cache, close internal context, unregister both TEE devices, free pool, uninit supplicant, destroy call queue/RPMB mutex, and drop the current RPMB device.

`optee_core_init()` avoids kdump kernels, registers an RPMB class interface when reachable, registers SMC and FF-A ABI backends, and keeps the module only if at least one backend succeeds. `optee_core_exit()` unregisters successful backends and RPMB interface.

## Control Flow And State
Global module state records SMC and FF-A registration results and whether the RPMB interface is registered. Per OP-TEE instance, context/session state is initialized by the backend probe and then managed by common open/release paths. Device enumeration is lazy for supplicant-dependent TAs and can also be triggered by RPMB notifier work for RPMB-dependent TAs.

## Dependencies And Integration Points
This file integrates with Linux module init/exit, TEE core devices, TEE client bus, RPMB class interfaces, notifier chains, sysfs device groups, workqueues, and both ABI registration functions. It calls common operations implemented in `call.c`, `notif.c`, `supp.c`, and backend files.

## Risks
`optee_remove_common()` assumes backends initialized fields in the expected order; partial-probe error paths must avoid calling it too early. Device enumeration treats missing PTA as success but propagates registration errors, so one failing client device can abort backend probe. Supplicant singleton enforcement means leaked `optee->supp.ctx` blocks future supplicant opens. RPMB routing model is visible to userspace and must match actual in-kernel versus supplicant routing behavior.

## Test Signals
Probe on systems with only SMC, only FF-A, both, and neither backends. Test kdump-kernel refusal. Verify supplicant open exclusivity and release aborts pending RPCs. Exercise device enumeration PTAs with zero devices, short-buffer retry, storage-not-available, and registration failure. Hot-add RPMB devices and confirm RPMB-dependent device scan work runs once successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/device.c -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/device.c

## Purpose
`device.c` discovers Trusted Application client devices exposed by OP-TEE pseudo TAs and registers them on the Linux TEE bus so normal kernel drivers can bind to TA UUIDs.

## Important APIs, Types, And Functions
`optee_ctx_match()` selects TEE contexts with `TEE_IMPL_ID_OPTEE`. `get_devices()` invokes a PTA command using one output memref and updates the caller’s buffer size, accepting `TEEC_ERROR_SHORT_BUFFER` as part of sizing. `optee_register_device()` allocates a `tee_client_device`, names it `optee-ta-<uuid>`, copies the UUID, registers it, and adds a `need_supplicant` sysfs file for supplicant-dependent devices. `__optee_enumerate_devices()` opens a context, opens the device-enumeration PTA UUID, queries required buffer size, allocates a kernel SHM buffer, reads UUIDs, and registers each device. `optee_unregister_devices()` unregisters all `tee_bus_type` devices whose names start with `optee-ta`.

## Control Flow And State
Enumeration is a two-pass PTA call: first with no buffer to learn the required size, then with a kernel SHM buffer to receive UUIDs. Registered devices persist on the TEE bus until common teardown calls `optee_unregister_devices()`. Device objects are heap allocated and freed by their `.release` callback.

## Dependencies And Integration Points
The file uses Linux TEE client APIs (`tee_client_open_context()`, `tee_client_open_session()`, `tee_client_invoke_func()`), TEE shared-memory allocation, UUID helpers, `tee_bus_type`, and PTA command ids from `optee_private.h`. It is called from backend probe and deferred scans in `core.c`.

## Risks
`need_supplicant_show()` returns 0 without emitting content, so its presence rather than value is the signal. `optee_unregister_devices()` matches by device name prefix, which is simple but broad within `tee_bus_type`. If registering one UUID fails, earlier registered devices remain until caller cleanup unregisters them.

## Test Signals
Mock PTA responses with short-buffer sizing, empty device lists, invalid memref sizes, and multiple UUIDs. Verify devices bind on `tee_bus_type` and are removed on teardown. Confirm supplicant-dependent enumeration adds the `need_supplicant` attribute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/ffa_abi.c -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/ffa_abi.c

## Purpose
`ffa_abi.c` implements the OP-TEE FF-A transport. It registers the FF-A driver, probes OP-TEE secure partitions, exchanges capabilities, registers shared memory through FF-A memory-share/lend handles, translates FF-A message parameters, performs yielding direct-message calls with RPC handling, manages FF-A notifications, and wires client/supplicant TEE devices to common OP-TEE code.

## Important APIs, Types, And Functions
The FF-A shared-memory handle map uses `struct shm_rhash`, `optee_shm_add_ffa_handle()`, `optee_shm_rem_ffa_handle()`, and `optee_shm_from_ffa_handle()` to translate FF-A global ids back to `tee_shm`. `optee_ffa_to_msg_param()` and `optee_ffa_from_msg_param()` convert between `struct tee_param` and `OPTEE_MSG_ATTR_TYPE_FMEM_*` parameters, using `shm->sec_world_id` as the FF-A global id and `OPTEE_MSG_FMEM_INVALID_GLOBAL_ID` for NULL memrefs.

`optee_ffa_shm_register()` validates memory type, builds an SG table, calls FF-A `memory_share()`, inserts the global handle, and stores it on `shm->sec_world_id`. `optee_ffa_shm_unregister()` tells OP-TEE to unregister, reclaims the FF-A memory object, and removes the handle. The supplicant unregister path skips the OP-TEE unregister call because the free originated from OP-TEE RPC.

`optee_ffa_yielding_call()` sends direct FF-A messages, handles busy returns through `optee_call_queue`, services RPC command or interrupt returns, and resumes with `OPTEE_FFA_YIELDING_CALL_RESUME`. `optee_ffa_do_call_with_arg()` prepares the direct call using the SHM global id and an offset to the message arg. `handle_ffa_rpc_func_cmd_shm_alloc()` and `_free()` service secure-world SHM allocation RPCs using either supplicant application SHM or kernel private SHM.

Protected memory is handled by `optee_ffa_lend_protmem()`, which lends memory via FF-A, assigns the use case with `OPTEE_MSG_CMD_ASSIGN_PROTMEM`, maps the global id, and reclaims on errors; `optee_ffa_reclaim_protmem()` releases and reclaims it. Probe helpers read FF-A API version, OP-TEE OS revision, capabilities, async notification support, RPMB probe capability, and protected memory support.

## Control Flow And State
Probe starts with API compatibility and capability exchange, allocates `struct optee`, creates a page-based SHM pool, allocates/registers client and privileged supplicant TEE devices, initializes the FF-A global-id rhashtable, call queue, supplicant, argument cache, RPMB mutex, internal context, notifications, optional protected memory, and device enumeration. Runtime calls use common OP-TEE message construction but enter secure world through FF-A direct request/response.

Persistent state includes `optee->ffa.global_ids`, `optee->ffa.bottom_half_value`, FF-A notification workqueue/work item, shared-memory pool, internal context, and per-instance common OP-TEE state. Removal relinquishes notification ids, destroys the workqueue, calls common removal, destroys the rhashtable/mutex, and frees `optee`.

## Dependencies And Integration Points
This file depends on the ARM FF-A bus and memory/message/notifier ops, Linux scatterlist APIs, TEE dynamic SHM helpers, common OP-TEE core/session/RPC/protected-memory code, RPMB reachability, and `optee_ffa.h` ABI constants. It registers with `ffa_register()` only when `CONFIG_ARM_FFA_TRANSPORT` is reachable.

## Risks
`optee_ffa_lend_protmem()` allocates `mem_attr` with `kzalloc_objs()` but does not visibly check for NULL before filling it, making low-memory behavior a risk if that helper does not encode allocation failure safely. FF-A SHM unregister removes the local handle before both OP-TEE unregister and memory reclaim, so failed unregister/reclaim leaves local state already gone. `optee_ffa_do_call_with_arg()` rejects nonzero `shm->offset` for argument SHM, so pool behavior must continue to satisfy page-start arguments. Async notification setup treats failures as nonfatal in probe, which means notification-dependent behavior must still work through synchronous RPC fallback.

## Test Signals
Probe with incompatible FF-A API versions, missing capability bits, and failures at each registration step. Register/unregister normal and supplicant SHM and verify global id mapping is removed exactly once. Exercise yielding calls with busy, RPC command, RPC interrupt, and done returns. Test protected memory lend assignment failure and ensure FF-A memory is reclaimed. Trigger notification ids including bottom-half value and normal keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/ffa_abi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/notif.c -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/notif.c

## Purpose
`notif.c` implements OP-TEE notification wait/send synchronization for values posted by secure world or by OP-TEE RPC notification commands.

## Important APIs, Types, And Functions
`struct notif_entry` stores a waiting key and completion on a list. `optee_notif_wait()` validates the key, allocates an entry, checks whether the key was already posted in the bitmap, rejects duplicate waiters, optionally waits with a timeout, removes the entry, and returns 0, `-ETIMEDOUT`, `-EBUSY`, `-ENOMEM`, or `-EINVAL`. `optee_notif_send()` either completes a waiting entry for the key or records the key in the bitmap for a future waiter. `optee_notif_init()` initializes the spinlock/list and allocates the bitmap. `optee_notif_uninit()` frees the bitmap.

## Control Flow And State
Notification state is per `struct optee` in `optee->notif`. A spinlock protects both the active wait-list and posted-key bitmap. If send happens before wait, the bit is set and consumed by the next waiter without sleeping. If wait happens first, the waiter sleeps on a completion until send or timeout.

## Dependencies And Integration Points
This code is used by RPC notification handling in `rpc.c` and async interrupt/FF-A notification paths in backend files. It depends on Linux completions, bitmaps, spinlocks, and the OP-TEE max notification key negotiated during probe.

## Risks
The bitmap is allocated with `bitmap_zalloc(max_key, ...)` while valid keys are checked as `key > max_key`, which makes `key == max_key` appear valid but may be outside the allocated bitmap bit range depending on bitmap API expectations. Duplicate waiters return `-EBUSY`, treated by RPC code as bad parameters. Timeout removes the entry while a concurrent send is serialized by the spinlock, so lost completion should be avoided.

## Test Signals
Wait after pre-posted send, send after wait, timeout wait, duplicate wait on the same key, invalid key above max, and boundary key equal to max. Exercise from both interrupt-triggered async notifications and RPC notification wait/send commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/notif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_ffa.h -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_ffa.h

## Purpose
`optee_ffa.h` defines the OP-TEE FF-A ABI constants shared between normal-world Linux and secure-world OP-TEE for FF-A direct messaging, capability exchange, shared-memory operations, async notifications, protected memory, and yielding calls.

## Important APIs, Types, And Functions
The file declares OP-TEE FF-A API version 1.0 and separates blocking and yielding service ids with `OPTEE_FFA_BLOCKING_CALL()` and `OPTEE_FFA_YIELDING_CALL()`. Blocking calls include API version, OS version, capability exchange, unregister shared memory, enable async notification, and release protected memory. Capability bits describe argument offsets, async notification, RPMB probing, and protected memory support.

Yielding call constants define `OPTEE_FFA_YIELDING_CALL_WITH_ARG`, `OPTEE_FFA_YIELDING_CALL_RESUME`, and return reasons: done, RPC command, and interrupt. Register comments document how `w3-w7` carry service ids, shared-memory handles, offsets, resume info, and return status.

## Control Flow And State
This header has no runtime state. It constrains how `ffa_abi.c` fills `struct ffa_send_direct_data` and interprets secure-world responses.

## Dependencies And Integration Points
It depends on `linux/arm_ffa.h` for FF-A definitions and is included by `ffa_abi.c`. The comments state it is exported by OP-TEE and kept in sync with secure-world code, so mismatches are ABI breakage rather than local implementation bugs.

## Risks
The ABI assumes FF-A 1.0 and AArch32 SMC register conventions for direct messages. If secure world advertises capabilities inconsistently, Linux may pass nonzero argument offsets or notification ids incorrectly. Protected-memory release and shared-memory unregister use global handles split into low/high 32-bit registers, so truncation or endian mistakes would be severe.

## Test Signals
Compatibility tests should validate major/minor negotiation, capability-bit handling, yielding call return reason handling, and shared/protected memory handle split/recombine behavior across 32-bit register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_ffa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_msg.h -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_msg.h

## Purpose
`optee_msg.h` defines the OP-TEE message protocol carried by both SMC and FF-A transports. It describes parameter encodings, message argument layout, API identity/revision values, normal-world commands, shared-memory registration commands, async notification commands, and protected-memory commands.

## Important APIs, Types, And Functions
Parameter attribute constants distinguish none, value, registered memory, FF-A memory, and temporary memory inputs/outputs/inouts. Flags include `OPTEE_MSG_ATTR_META`, `OPTEE_MSG_ATTR_NONCONTIG`, and cache attribute fields. `struct optee_msg_param_tmem`, `_rmem`, `_fmem`, and `_value` define the union arms inside `struct optee_msg_param`. `struct optee_msg_arg` is the command envelope with command id, function id, session, cancel id, return code/origin, parameter count, and a flexible parameter array. `OPTEE_MSG_GET_ARG_SIZE()` computes the allocation size.

Command constants include session open/invoke/close/cancel, SHM register/unregister, bottom-half execution, async notification stop, protected memory lend/reclaim/config/assign, and `OPTEE_MSG_FUNCID_CALL_WITH_ARG`. The header also defines UID/revision constants for API probing and protected-memory use-case values.

## Control Flow And State
There is no state in the header, but its structures are the persistent ABI stored in shared memory during every OP-TEE call. Common call code fills `optee_msg_arg`, backends translate Linux params into transport-specific memory parameter forms, secure world updates the same shared memory, and common code copies results back.

## Dependencies And Integration Points
The file is included by `optee_private.h`, SMC/FF-A backend code, and common call/RPC code. It is dual-licensed because it is an ABI contract shared with OP-TEE secure-world sources.

## Risks
Any layout change breaks the shared-memory ABI. Noncontiguous temporary memory uses 4 KiB page-list assumptions even on larger Linux pages, so helper code must preserve the documented chaining format. FF-A and SMC use different memory union arms for conceptually similar memrefs; using the wrong attr family will make secure world reject or misinterpret buffers.

## Test Signals
Compile-time layout/size checks, open-session meta-parameter tests, registered and temporary SHM registration tests, NULL memref tests, noncontiguous user buffer registration, and protected-memory command round trips are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_private.h -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_private.h

## Purpose
`optee_private.h` is the internal OP-TEE driver contract. It defines common driver state, synchronization structures, transport-specific substructures, ops abstraction, session/context types, GP error constants, helper conversion functions, and prototypes shared by OP-TEE core, call, RPC, notification, protected-memory, and ABI backend code.

## Important APIs, Types, And Functions
`struct optee` is the central per-instance object. It owns client and supplicant `tee_device`s, selected `optee_ops`, internal context, an SMC or FF-A union, argument cache, call queue, notification database, supplicant queue, SHM pool, RPMB state, device-enumeration work, RPC parameter count, routing flags, and OS revision.

`struct optee_ops` abstracts transport differences: `do_call_with_arg()`, `to_msg_param()`, `from_msg_param()`, `lend_protmem()`, and `reclaim_protmem()`. `struct optee_call_queue`, `optee_call_waiter`, `optee_notif`, `optee_shm_arg_cache`, and `optee_supp` define persistent synchronization state. `struct optee_smc` carries SMCCC function pointer, reserved SHM mapping, capabilities, notification IRQ state, per-CPU notification work, and CPU hotplug state. `struct optee_ffa` carries FF-A device pointer, bottom-half notification id, global-id rhashtable, and notification workqueue.

Inline helpers convert value params and register pairs. Prototypes expose all common functions across files, including session operations, supplicant RPC, device enumeration, notifications, protected memory, RPC command helpers, ABI registration, and simple internal commands.

## Control Flow And State
The header expresses the main layering: backend probe creates and initializes `struct optee`; common TEE operations use `optee->ops`; client contexts use `optee_context_data` session lists; secure-world calls coordinate through `optee_call_queue`; RPC to userspace flows through `optee_supp`; async and synchronous notification state lives in `optee_notif`.

## Dependencies And Integration Points
It depends on ARM SMCCC, notifier chains, rhashtable, RPMB, semaphores, Linux TEE core, FF-A types via forward usage, and the OP-TEE message ABI. It is included by nearly every OP-TEE driver source in this subset.

## Risks
Because this file is a shared internal ABI, field lifetime assumptions must match all backends and common teardown. The union of `smc` and `ffa` means code must only touch the active transport fields. `optee_supp` supports both synchronous and asynchronous request modes; mixing them incorrectly is guarded in `supp.c` but can break userspace supplicant behavior.

## Test Signals
Build both SMC and FF-A backends, run probe/remove cycles, exercise supplicant connect/disconnect, run concurrent session calls, and test RPMB/notification/protected-memory optional capabilities to cover most shared state fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_rpc_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_rpc_cmd.h

## Purpose
`optee_rpc_cmd.h` defines RPC command ids and parameter contracts for services secure-world OP-TEE asks normal world to perform in kernel or through tee-supplicant.

## Important APIs, Types, And Functions
The header defines kernel-handled RPCs for time (`OPTEE_RPC_CMD_GET_TIME`), notification wait/send, suspend/sleep, shared-memory allocate/free, I2C transfer, RPMB probing, and RPMB frame routing. It also defines shared-memory types (`OPTEE_RPC_SHM_TYPE_APPL`, `OPTEE_RPC_SHM_TYPE_KERNEL`), I2C operation and flag values, and RPMB type values for eMMC, UFS, and NVMe.

## Control Flow And State
There is no state in the header. `rpc.c` and backend-specific RPC handlers inspect these command ids in `optee_msg_arg.cmd`, validate the documented parameter layouts, and either satisfy the request in kernel or forward it to tee-supplicant.

## Dependencies And Integration Points
The definitions are consumed by `rpc.c`, `smc_abi.c`, and `ffa_abi.c`. The documented parameter contracts must match OP-TEE secure-world RPC generation and tee-supplicant behavior.

## Risks
The command contracts include raw I2C and RPMB access from secure world through normal world; parameter validation and routing policy are security-sensitive. RPMB routing model must match `optee->in_kernel_rpmb_routing` to avoid user/kernel split-brain. SHM allocation/free semantics differ between application and kernel memory.

## Test Signals
Test each command id with correct and malformed parameter counts/types. Exercise I2C with unsupported 10-bit adapters and invalid transfer modes. Run RPMB probe/reset/next/frame flows with each supported RPMB type and with no device present. Verify SHM allocation/free for both APPL and KERNEL types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_rpc_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_smc.h -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_smc.h

## Purpose
`optee_smc.h` defines the SMC/HVC ABI constants, register contracts, return codes, capability bits, and helper result structures used by the OP-TEE SMC backend.

## Important APIs, Types, And Functions
Macros build SMCCC fast and standard call ids. API probe calls include call count, UID, API revision, OS UUID, OS revision, optional image loading, call-with-arg variants, shared-memory config, capability exchange, SHM cache enable/disable, thread count, async notification enable/get value, protected-memory config, and return-from-RPC.

Capability bits describe reserved SHM, unregistered SHM, dynamic SHM, virtualization, NULL memref, async notification, RPC arg support, RPMB probe, protected memory, and dynamic protected memory. RPC return values encode allocate, free, foreign interrupt, and command requests. `OPTEE_SMC_RETURN_IS_RPC()` identifies RPC returns by prefix while excluding unknown-function.

## Control Flow And State
There is no local state. The SMC backend fills registers according to this header, loops on RPC returns and thread-limit returns, and interprets fast-call capability data during probe.

## Dependencies And Integration Points
The header depends on ARM SMCCC and bitops and mirrors constants from `optee_msg.h`. It is included by `smc_abi.c`, which uses the structures as overlays on `arm_smccc_res`.

## Risks
Register field ordering is the ABI. A high/low register mixup can corrupt pointers or memory handles. SHM cache disable returns stale `tee_shm` pointers from secure world, so `smc_abi.c` must ignore them when they may not be mapped by the current kernel. Optional firmware image loading is security-sensitive and separately gated by Kconfig.

## Test Signals
SMCCC ABI probing against known OP-TEE versions, capability exchange matrix tests, dynamic versus reserved SHM probe, RPC prefix decoding, async notification value retrieval, and SHM cache enable/disable behavior during boot and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_trace.h -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_trace.h

## Purpose
`optee_trace.h` defines tracepoints for the raw OP-TEE SMC invocation boundary, allowing developers to observe register arguments before and return registers after calls into secure world.

## Important APIs, Types, And Functions
`TRACE_EVENT(optee_invoke_fn_begin)` records the `optee_rpc_param` pointer and eight 32-bit argument registers. `TRACE_EVENT(optee_invoke_fn_end)` records the same parameter pointer and four return registers from `struct arm_smccc_res`. The trace include path/file footer lets Linux tracepoint generation include this header correctly from `smc_abi.c`.

## Control Flow And State
Tracepoints are passive instrumentation. `smc_abi.c` emits begin/end events around `optee->smc.invoke_fn()` in `optee_smc_do_call_with_arg()`.

## Dependencies And Integration Points
The header depends on Linux tracepoint infrastructure, ARM SMCCC result types, and `optee_private.h` for `struct optee_rpc_param`. The Makefile adds `-I$(src)` for `smc_abi.o` so the trace generator can resolve it.

## Risks
The tracepoint copies raw register values and a kernel pointer into trace buffers; enabling it can expose sensitive call metadata to privileged tracing users. The `BUILD_BUG_ON` checks depend on source structures remaining at least as large as the copied arrays.

## Test Signals
Build with tracing enabled, enable both trace events, run TEE open/invoke calls, and confirm begin/end events pair around secure calls without breaking normal execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/optee_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/protmem.c -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/protmem.c

## Purpose
`protmem.c` implements dynamic OP-TEE protected-memory pools used for secure data path DMA heaps. It queries secure-world protected-memory requirements, allocates physical memory, lends it to OP-TEE, suballocates it through a gen_pool, and reclaims it when no allocations remain.

## Important APIs, Types, And Functions
`struct optee_protmem_dyn_pool` wraps `tee_protmem_pool` with an OP-TEE pointer, backing `tee_shm`, gen_pool, page count, memory attributes, use case, refcount, and mutex. `init_dyn_protmem()` allocates DMA memory via `tee_shm_alloc_dma_mem()`, lends it with `optee->ops->lend_protmem()`, marks it dynamic, creates a gen_pool, and adds the protected physical range. `get_dyn_protmem()` lazily initializes or refcounts the pool; `put_dyn_protmem()` releases it when the last allocation returns.

Pool ops allocate by page-aligning requested size, taking a physical subrange from gen_pool, creating a one-entry SG table, and returning an offset relative to the backing protected SHM. Free returns SG entries to the gen_pool and drops the dynamic pool reference. `protmem_pool_op_dyn_update_shm()` reports the parent protected SHM to the TEE core.

`get_protmem_config()` sends `OPTEE_MSG_CMD_GET_PROTMEM_CONFIG` to secure world, optionally using a private SHM output buffer for memory attributes. `optee_protmem_alloc_dyn_pool()` queries size/attributes, sets DMA mask from returned PA width, initializes the pool object, and returns the generic `tee_protmem_pool`.

## Control Flow And State
Dynamic protected memory is lazily lent on the first allocation and reclaimed after the last allocation. `refcount` guards active users; `mutex` serializes init and teardown. The gen_pool tracks suballocations inside the protected physical range. Memory attributes and use case persist for the pool lifetime.

## Dependencies And Integration Points
This file depends on Linux genalloc, TEE protected-memory pool APIs, TEE DMA memory allocation, common OP-TEE message calls from `call.c`, and backend-specific `lend_protmem()`/`reclaim_protmem()` ops from SMC or FF-A. It is called by backend protected-memory initialization.

## Risks
`protmem_pool_op_dyn_alloc()` aligns allocation size to pages but calls `gen_pool_free()` with `size` instead of the aligned `sz` in the SG allocation failure path, which can leave part of the allocation unreleased. The TODO notes memory should be unmapped before lending because it becomes inaccessible; relying on EL2 to handle this is platform-dependent. `get_protmem_config()` computes `*ma_count = params[1].u.memref.size / sizeof(*mem_attrs)` even when `mem_attrs` is NULL; this relies on `sizeof(*mem_attrs)` being valid on the pointed-to type and is syntactically okay but easy to misread.

## Test Signals
Query configs with no attributes, short-buffer attributes, and invalid returns. Allocate/free multiple protected buffers and ensure the dynamic pool initializes once and reclaims on last free. Fault-inject gen_pool add/alloc, lend, and reclaim failures. Use memory-debugging to catch the aligned-size free mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/protmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/rpc.c -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/rpc.c

## Purpose
`rpc.c` handles OP-TEE RPC commands requested by secure world. It services time, notification, sleep, I2C, shared-memory allocation/free through supplicant helpers, RPMB probe/frame routing either in kernel or via tee-supplicant, and generic forwarding to the supplicant.

## Important APIs, Types, And Functions
`handle_rpc_func_cmd_get_time()` returns real time in one value output param. `handle_rpc_func_cmd_i2c_transfer()` converts OP-TEE params to Linux TEE params, validates the exact attr layout, acquires an I2C adapter, performs one read or write transfer, and returns transferred length. `handle_rpc_func_cmd_wq()` implements notification wait/send using `optee_notif_wait()` and `optee_notif_send()`. `handle_rpc_func_cmd_wait()` sleeps interruptibly for a requested number of milliseconds.

`handle_rpc_supp_cmd()` converts params, calls `optee_supp_thrd_req()`, then converts output params back. `optee_rpc_cmd_alloc_suppl()` and `optee_rpc_cmd_free_suppl()` request application SHM allocation/free through tee-supplicant, using the returned SHM id to get a kernel reference. RPMB helpers probe/reset devices, iterate matching RPMB devices, copy device ids to output memrefs, and route RPMB frames through `rpmb_route_frames()` when in-kernel routing is enabled.

`optee_rpc_cmd()` dispatches command ids and chooses in-kernel or supplicant RPMB routing based on `optee->in_kernel_rpmb_routing`.

## Control Flow And State
RPC handling happens synchronously while a secure-world call is suspended. Results are written back into the same `optee_msg_arg`. For supplicant commands, a kernel thread queues a request and blocks until userspace receives and sends a response. RPMB probe state is persisted in `optee->rpmb_dev` under `rpmb_dev_mutex` so probe-next can iterate devices across calls.

## Dependencies And Integration Points
The file integrates with Linux timekeeping, I2C, RPMB, TEE parameter conversion backend ops, supplicant request queues in `supp.c`, notification state in `notif.c`, and RPC command definitions in `optee_rpc_cmd.h`.

## Risks
I2C RPC exposes normal-world I2C transfers to secure world; strict attr validation helps but bus/address policy is delegated to secure world and kernel adapter availability. In `handle_rpc_func_rpmb_frames()`, `tee_shm_get_va()` results are not checked with `IS_ERR()` before `rpmb_route_frames()`, unlike other paths. `optee_rpc_cmd_alloc_suppl()` maps supplicant return failures to `-ENOMEM`, losing error specificity. RPMB routing state must be reset on probe-reset to avoid stale device references.

## Test Signals
Malformed RPC parameter counts/types for every command. I2C transfers with missing adapter, unsupported 10-bit mode, invalid operation, and transfer errors. Notification wait timeout and send. Supplicant absent with blocking and nonblocking callers. RPMB probe with multiple device types, no devices, short output buffer, and frame routing errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/smc_abi.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/smc_abi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/supp.c -->
# sources/distributed-fs/ceph-client/drivers/tee/optee/supp.c

## Purpose
`supp.c` implements the kernel side of the OP-TEE supplicant RPC queue. Secure-world calls can request userspace services; kernel requesters enqueue work, tee-supplicant receives it through privileged TEE ioctls, and sends results back.

## Important APIs, Types, And Functions
`struct optee_supp_req` stores one request, including queue/id state, function id, return code, params, and completion. `optee_supp_init()` initializes mutex, completion, IDR, request list, and synchronous request id. `optee_supp_release()` aborts all requests in the IDR and queue, completes their waiters with communication errors, clears `supp->ctx`, and resets synchronous state.

`optee_supp_thrd_req()` enqueues a request, wakes supplicant waiters, and blocks killably until completion; if interrupted while still queued it removes the request and returns communication error. `optee_supp_recv()` validates the user-provided receive parameter slots, waits for a queued request, assigns an IDR id, supports asynchronous mode when a meta parameter is provided, copies request params to userspace, and returns the requested function id. `optee_supp_send()` finds the outstanding request by async meta id or synchronous `req_id`, copies output values and memref sizes back to the original params, stores the supplicant return code, and completes the blocked requester.

## Control Flow And State
The supplicant state is protected by `supp->mutex`. Requests start in `supp->reqs`, move into `supp->idr` after userspace receives them, and complete when userspace sends a response. `supp->req_id` enforces legacy synchronous mode; async mode uses a meta value parameter carrying the IDR id and requires `supp->req_id == -1`.

## Dependencies And Integration Points
The file integrates with privileged OP-TEE supplicant TEE device ops, TEE parameter/memref helpers, Linux completions, IDR, and common RPC dispatch in `rpc.c`. `core.c` manages supplicant context singleton and calls release cleanup.

## Risks
`supp_check_recv_params()` drops references for memrefs present in receive buffers before validating attrs, relying on ioctl-layer reference behavior. Supplicant must not mix synchronous and asynchronous request modes; violations return errors that force restart-like behavior. If no supplicant is present and caller is blocking, requests can wait until interrupted. Output copying only updates value outputs/inouts and memref sizes, not memref object pointers or contents, which is intentional but must match caller expectations.

## Test Signals
Supplicant recv/send in synchronous and asynchronous meta modes, mixed-mode rejection, too few receive params, malformed attrs, interrupted requester waits, supplicant release with queued and in-flight requests, and output propagation for value and memref params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/optee/supp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/Kconfig

## Purpose
`qcomtee/Kconfig` defines the Qualcomm Trusted Execution Environment driver configuration.

## Important APIs, Types, And Functions
`config QCOMTEE` is a tristate labeled "Qualcomm TEE Support". It depends on Qualcomm architecture or compile testing, excludes big-endian CPUs, selects `QCOM_SCM`, and selects `QCOM_TZMEM_MODE_SHMBRIDGE`. The help text describes access to QTEE services, loaded Trusted Applications, and userspace supplicant services exported to QTEE.

## Control Flow And State
The Kconfig symbol controls whether the QCOMTEE composite object is built. Its selected dependencies configure the Qualcomm SCM and TZ memory bridge modes needed by the driver.

## Dependencies And Integration Points
The symbol integrates QCOMTEE with Qualcomm firmware call infrastructure (`QCOM_SCM`) and trusted-zone memory mode selection. It is consumed by the qcomtee Makefile.

## Risks
The driver is unavailable on big-endian builds. Selecting specific Qualcomm TZ memory mode may affect other Qualcomm secure memory users and should be validated in multi-driver configurations.

## Test Signals
Build with `ARCH_QCOM`, with `COMPILE_TEST`, and with big-endian disabled/enabled configurations to confirm dependency gating. Verify selected symbols appear in final configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/Makefile

## Purpose
The qcomtee Makefile defines the composite Qualcomm TEE driver object and its source components.

## Important APIs, Types, And Functions
`obj-$(CONFIG_QCOMTEE) += qcomtee.o` builds the driver when selected. `qcomtee-objs` includes async messaging, call handling, core driver registration, memory object support, primordial object support, shared memory, and user object handling.

## Control Flow And State
There is no runtime state. The object list shows that `async.c` is only one component of a larger object model with call, core, memory, primordial, SHM, and user-object modules.

## Dependencies And Integration Points
The file integrates with Kbuild composite object rules and the `CONFIG_QCOMTEE` symbol from Kconfig.

## Risks
All listed object files must compile together whenever QCOMTEE is selected; missing optional guards in any one file can break compile-test builds.

## Test Signals
Kernel builds with `CONFIG_QCOMTEE=m` and `CONFIG_QCOMTEE=y`, including `COMPILE_TEST`, are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/async.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/async.c

## Purpose
`async.c` parses asynchronous QCOMTEE messages appended to outbound invocation buffers and currently handles secure-world object release requests. It prevents async requests from being replayed by clearing the async buffer after processing.

## Important APIs, Types, And Functions
The file defines async protocol versions 1.0, 1.1, 1.2 and treats 1.2 as current. `struct qcomtee_async_msg_hdr` carries version and operation. `struct qcomtee_async_release_msg` carries a counted array of object ids to release.

`qcomtee_get_async_buffer()` computes the available async-message region in a `qcomtee_object_invoke_ctx`: if the invocation context is not busy, the full outbound buffer is available; if a callback request already occupies the buffer, it skips callback header, input buffers, and output buffers using `qcomtee_msg_*` helpers and alignment. `async_release()` erases each object id from the object invocation context with `qcomtee_idx_erase()` and drops the object with `qcomtee_object_put()`. `qcomtee_fetch_async_reqs()` loops through aligned async messages until unused zeroed space, major-version mismatch, unsupported op, parse failure, or insufficient remaining space, then zeroes the entire async buffer with `memzero_explicit()`.

## Control Flow And State
Async state is encoded in the outbound message buffer associated with one invocation context. The driver consumes messages sequentially, advances by aligned consumed size, and resets the buffer so QTEE does not see the same async requests again. Release messages mutate object-index state in the invocation context and object refcounts.

## Dependencies And Integration Points
This file depends on `qcomtee.h` for object invocation context, buffer, callback-message layout, argument iteration macros, object index erase, object put, and QCOMTEE message operation ids. It integrates with the QCOMTEE call path that owns outbound buffers and invokes `qcomtee_fetch_async_reqs()` after QTEE has had a chance to write async messages.

## Risks
`async_release()` trusts `msg->counts` enough to iterate and compute `struct_size()`; the `size` argument is currently unused, so a malformed count could overread the async buffer unless upstream message bounds are guaranteed elsewhere. `qcomtee_fetch_async_reqs()` checks only major version, so newer minor versions are accepted even if they add incompatible operation formats under the same major. Offset computation for busy callback buffers must stay aligned with the callback message format or async parsing can overlap normal callback payloads.

## Test Signals
Feed empty zeroed async buffers, valid release messages with one and many ids, unsupported op codes, major-version mismatch, truncated release messages, and busy callback buffers with input/output payloads. Verify released objects are removed and refcounts drop once, and that the async buffer is zeroed after every exit path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/async.c -->
