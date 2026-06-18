# subset-b-003687 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gsp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gsp.c

Purpose: this is the R535 GSP-RM bring-up, runtime messaging, suspend/resume, debug logging, and teardown implementation for Nouveau's `nvkm_gsp` path. It bridges Nouveau's internal subdevice model to NVIDIA's GSP firmware ABI by allocating DMA-coherent shared memory, describing firmware images to the booter, issuing boot-time RPCs, receiving asynchronous GSP events, and publishing the R535 `nvkm_rm_api_gsp` callbacks.

Important APIs and types: exported helpers include `nvkm_gsp_mem_ctor()`, `nvkm_gsp_mem_dtor()`, `nvkm_gsp_sg()`, `nvkm_gsp_sg_free()`, `r535_gsp_oneinit()`, `r535_gsp_init()`, `r535_gsp_fini()`, and `r535_gsp_dtor()`. The local registry machinery uses `registry_list_entry` to build `PACKED_REGISTRY_TABLE` payloads for `NV_VGPU_MSG_FUNCTION_SET_REGISTRY`. Boot and logging use `LibosMemoryRegionInitArgument`, `GSP_ARGUMENTS_CACHED`, `GspFwWprMeta`, `GspFwSRMeta`, and RM_RISCV firmware descriptors from `nvrm/gsp.h`. The file also registers the public `r535_gsp` API table with `.set_rmargs`, `.set_system_info`, `.get_static_info`, `.xlat_mc_engine_idx`, `.drop_send_user_shared_data`, and `.sr_data_size`.

Control flow: `r535_gsp_oneinit()` is the first major setup stage. It initializes command and message queue mutexes, extracts `.fwimage` and the chip-specific signature section from the RM ELF, constructs a DMA-backed firmware object, copies the signature, builds a radix3 page table over the firmware scatter-gather image, registers message notification handlers, constructs booter firmware state, releases original firmware blobs, initializes libos logging/RM argument regions, sends system information, sends registry key/value data, and initializes the client IDR. `r535_gsp_init()` then writes the firmware app version into the falcon mailbox, verifies the RISC-V falcon is active, waits for `GSP_INIT_DONE`, marks `gsp->running`, and either resumes from saved SR state or completes post-init. Post-init fetches static info, creates the message work item, reads the RM interrupt table, translates RM engine indexes into Nouveau subdevice types, binds the GSP interrupt handler, enables interrupt delivery, and frees boot-only buffers.

Message and interrupt behavior: `r535_gsp_intr()` reads falcon interrupt and mask registers, handles bit `0x40` by acknowledging and scheduling `r535_gsp_msgq_work()`, reports unknown interrupt bits, and retriggers the falcon interrupt source. The work item serializes on `gsp->cmdq.mutex` and drains messages through `r535_gsp_msg_recv()`. Registered callbacks handle OS error logs, MMU fault queued notifications, client event fanout, CPU sequencer commands, FIFO RC events, libos print messages, and intentionally dropped notifications. `r535_gsp_msg_run_cpu_sequencer()` is a sensitive firmware-command interpreter: it performs MMIO writes, masks, polls, delays, register saves, falcon reset/start/wait, and a core resume path that resets GSP, reloads libos address mailboxes, starts SEC2, validates SEC2 mailbox status, writes the app version, and checks RISC-V activity.

State and persistence: the file manages many long-lived DMA allocations on `nvkm_gsp`: `boot.fw`, `libos`, `loginit`, `logintr`, `logrm`, `rmargs`, `shm.mem`, firmware signature, WPR metadata, radix3 tables, suspend/resume metadata, and scatter-gather backing stores. `nvkm_gsp_mem_ctor()` takes a device reference because some buffers may outlive normal device remove ordering; `nvkm_gsp_mem_dtor()` poisons buffers before freeing coherent memory. The registry list is transient and either consumed by `build_registry()` or cleared by `clean_registry()`. Static RM data persists into `gsp->internal` handles, BAR PDE bases, framebuffer regions, reserved FB size, and GR GPC/TPC counts. Suspend allocates system memory for SR data, builds SR radix3 metadata, calls the FBSR API, sends `UNLOADING_GUEST_DRIVER`, waits for the firmware mailbox shutdown value, and marks the GSP stopped.

Dependencies and integration points: this file depends on `rm/rpc.h` for generic RM RPC allocation/control calls, R535 protocol headers for payload shape and function IDs, falcon and SEC2 helpers for boot/resume, PCI/device resource helpers for system info, ACPI DSM helpers for display/mux capability reporting, debugfs for log exposure, and `nvkm_inth` for interrupt registration. It is tightly coupled to `rpc.c` for command/message queue transport, `rm.c` for API table selection, `fbsr` for suspend/resume memory preservation, and engine-specific API implementations through notification callbacks.

Risks: most failures are firmware ABI or lifetime bugs. The GSP-provided sequencer can touch arbitrary MMIO offsets from firmware data, so malformed payloads or ABI drift can cause device hangs. Registry parsing accepts module-supplied keys and converts non-numeric values to strings, so key length, allocation sizing, and GSP expectations are important. The radix3 builder assumes firmware size/page counts fit the designed table shape. Debugfs log retention deliberately copies buffers across object teardown and must avoid stale pointers. Interrupt-table translation silently skips unknown RM engine indexes, which is safer than failing but may leave engine interrupts unmanaged after ABI changes. Several error paths allocate staged resources and rely on the destructor to clean later allocations.

Test signals: useful validation includes booting R535-supported GPUs through `r535_gsp_oneinit()`/`r535_gsp_init()`, checking `GSP_INIT_DONE`, verifying `/sys/kernel/debug/nouveau/<dev>/loginit`, `logintr`, `logrm`, and `logpmu` exposure when debugfs is enabled, exercising hotplug/client events, provoking RC/MMU fault logs, suspending/resuming both runtime and system paths, and checking that FB region discovery produces sane usable/reserved sizes. Kernel logs should be watched for `seq`, `event`, `Xid`, `intr`, and `libos print` messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvdec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvdec.c

Purpose: provides the R535 RM engine allocator for NVDEC/BSP video decode engine objects. It adapts Nouveau's generic `nvkm_rm_api_engine.alloc` signature to the R535 `NV_BSP_ALLOCATION_PARAMETERS` ABI.

Important API: `r535_nvdec_alloc()` calls `nvkm_gsp_rm_alloc_get()` against the parent channel object, using the requested RM handle and class. It fills `args->size` with `sizeof(*args)` and `args->engineInstance` with Nouveau's selected instance, then commits with `nvkm_gsp_rm_alloc_wr()`. The exported `r535_nvdec` table contains this function as `.alloc`.

Control flow and state: the function is stateless beyond initializing the RM allocation payload and the output `nvkm_gsp_object`. The object lifetime is then owned by the generic RM allocation/free path. Errors are returned directly from allocation preparation or writeback; `WARN_ON(IS_ERR(args))` highlights unexpected RM allocation setup failures.

Dependencies and integration: depends on `rm/engine.h` for the API contract and `nvrm/nvdec.h` for the R535 payload layout. It is selected from `r535_api` in `rm.c` and used by FIFO/channel object creation paths when binding decode engines.

Risks and tests: the only ABI-sensitive fields are `size` and `engineInstance`; wrong instance numbering would bind the wrong physical decoder or fail allocation. Test signals are successful creation/destruction of NVDEC objects for each discovered instance, decode workload submission, and absence of RM allocation errors for multi-NVDEC GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvenc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvenc.c

Purpose: provides the R535 RM engine allocator for NVENC/MSENC video encode engine objects. It is a small adapter from Nouveau's engine allocation API to `NV_MSENC_ALLOCATION_PARAMETERS`.

Important API: `r535_nvenc_alloc()` obtains an RM alloc RPC buffer using the parent channel, requested object handle, class, payload size, and destination object. It sets `size` and `engineInstance`, then sends the allocation. The exported `r535_nvenc` table installs this allocator.

Control flow and state: the allocator has no persistent local state. Success initializes the supplied `nvkm_gsp_object` through the shared RM allocation helper; failure leaves the caller responsible for unwinding any broader channel setup. The `prohibitMultipleInstances` field in the ABI payload is left at zero from the zeroed allocation buffer, meaning this implementation does not request single-instance enforcement.

Dependencies and integration: selected through `r535_api.nvenc` and consumed by higher-level Nouveau engine/channel setup. It depends on the R535 header definition matching the firmware's expected MSENC allocation structure.

Risks and tests: ABI drift in `NV_MSENC_ALLOCATION_PARAMETERS` or incorrect instance mapping can break encode object creation. Validation should allocate NVENC objects across advertised instances and run encode workloads while checking for GSP RM allocation failures and RC events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvenc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvjpg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvjpg.c

Purpose: implements the R535 RM allocation adapter for NVJPG/NVJPEG engines.

Important API: `r535_nvjpg_alloc()` allocates a `NV_NVJPG_ALLOCATION_PARAMETERS` payload under a channel object, sets `size` and `engineInstance`, and writes the allocation. The `r535_nvjpg` `nvkm_rm_api_engine` table exposes it to the rest of RM integration.

Control flow and state: no persistent local state is kept. The output object is populated by `nvkm_gsp_rm_alloc_get()` and finalized by `nvkm_gsp_rm_alloc_wr()`. Error propagation is direct, with a warning for allocation-buffer setup failure.

Dependencies and integration: depends on `rm/engine.h` and `nvrm/nvjpg.h`, and is referenced by the R535 API table. Its instance value must align with RM engine discovery and FIFO engine translation.

Risks and tests: the principal risks are stale ABI layout or wrong instance numbering, especially on GPUs with multiple NVJPEG engines. Test signals include successful NVJPG object allocation for every discovered instance and exercising JPEG decode paths without RM RC-triggered failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvjpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/alloc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/alloc.h

Purpose: defines the R535 RM allocation and free RPC payload headers used by Nouveau's generic GSP RM object helpers. The file is an ABI excerpt from NVIDIA's open GPU kernel modules and must match firmware expectations.

Important types: `rpc_gsp_rm_alloc_v03_00` carries `hClient`, `hParent`, `hObject`, `hClass`, status, payload size, flags, reserved bytes, and a flexible `params[]` area. `NVOS00_PARAMETERS_v03_00` describes free parameters with root, parent, old object handle, and status. `rpc_free_v03_00` wraps the free parameters.

Control flow and state: this header has no executable logic. Runtime state lives in RM objects and the flexible parameter payload that callers allocate, fill, and send through `NV_VGPU_MSG_FUNCTION_GSP_RM_ALLOC` or free paths.

Dependencies and integration: included by RM allocation helpers that build object creation RPCs for clients, devices, channels, engines, and memory objects. It depends on `nvrm/nvtypes.h` for fixed-width RM types and alignment macros.

Risks and tests: because the status and flexible-array layout is protocol-owned, padding or field order changes would corrupt every RM allocation. Test signals are broad: all GSP object creation paths, free paths, and error-status translation should work across root, device, subdevice, engine, and memory allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/bar.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/bar.h

Purpose: defines the R535 RPC payload for updating RM-managed BAR page directory entries.

Important types: `NV_RPC_UPDATE_PDE_BAR_TYPE` selects BAR1, BAR2, or invalid. `UpdateBarPde_v15_00` carries the target BAR type, a 64-bit entry value, and entry level shift. `rpc_update_bar_pde_v15_00` wraps that structure for the `UPDATE_BAR_PDE` RPC function.

Control flow and state: no code is present. State represented by this ABI is the current RM view of BAR page directory entries, usually synchronized with Nouveau's BAR/MMU setup.

Dependencies and integration: consumed by BAR update code outside this work item and tied to `NV_VGPU_MSG_FUNCTION_UPDATE_BAR_PDE` from `rpcfn.h`. It depends on `nvrm/nvtypes.h` for aligned 64-bit fields.

Risks and tests: incorrect BAR type or alignment can break BAR1/BAR2 access and therefore instance memory, VRAM mappings, and resume restoration. Test signals include BAR1/BAR2 mapping operations, page table updates, and suspend/resume paths that depend on BAR accessibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/bar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ce.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ce.h

Purpose: declares the R535 copy-engine allocation payload.

Important type: `NVC0B5_ALLOCATION_PARAMETERS` contains a structure version and `engineType`. Nouveau CE allocation code uses this ABI to select the RM/NV2080 engine type for a copy engine object.

Control flow and state: the header is declarative only. The payload captures allocation-time engine selection; persistent state lives in the allocated RM object.

Dependencies and integration: included by R535 CE allocation code, selected via `r535_api.ce`, and linked to FIFO engine discovery/translation. It depends on fixed RM scalar types from `nvrm/nvtypes.h`.

Risks and tests: wrong engine type assignment can allocate an object on the wrong CE or fail channel binding. Tests should cover CE object allocation, memory copy submissions, and GPUs with multiple CEs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/client.h

Purpose: defines the R535 RM root client class and allocation payload.

Important definitions: `NV01_ROOT` is the RM class for a root client. `NV_PROC_NAME_MAX_LENGTH` bounds process-name storage. `NV0000_ALLOC_PARAMETERS` begins with `hClient`, then carries `processID` and `processName`.

Control flow and state: no code is present. The root client allocation initializes the top-level RM namespace for all later device, subdevice, event, VAS, channel, and engine objects.

Dependencies and integration: consumed by client constructors in the RM API, and indirectly by `nvkm_gsp_client_device_ctor()` used in VMM, display, and engine paths. The R570 client implementation in this work item uses the analogous R570 header and shows the pattern.

Risks and tests: `hClient` must remain the first member per the source comment; changing that would break RM allocation parsing. Test signals are basic GSP client creation, object handle allocation, and cleanup without leaked IDR entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ctrl.h

Purpose: defines the generic R535 GSP RM control RPC header.

Important type: `rpc_gsp_rm_control_v03_00` carries `hClient`, `hObject`, control command ID, status, parameter size, flags, and a flexible `params[]` payload. Control helpers place command-specific structures behind this header.

Control flow and state: declarative only. The runtime control flow is in `nvkm_gsp_rm_ctrl_get()`, `_push()`, `_wr()`, `_rd()`, and `_done()` users; this header defines the common envelope those helpers transmit.

Dependencies and integration: every R535/R570 control call in this group ultimately relies on this shape: interrupt-table reads, VAS page-directory controls, display queries, FBSR setup, FIFO queries, and GR context/ZCULL controls.

Risks and tests: status, parameter sizing, and flexible-array alignment are global ABI risks. Bad layout can manifest as nearly any RM control failure. Tests should include representative read, write-only, and push/readback controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/device.h

Purpose: defines R535 RM device and subdevice allocation classes and payloads.

Important definitions: `NV01_DEVICE_0` is the device class. `NV0080_ALLOC_PARAMETERS` carries device ID, sharing/target handles, flags, internal VA size/start/limit, and VA mode. `NV20_SUBDEVICE_0` is the subdevice class, with `NV2080_ALLOC_PARAMETERS.subDeviceId`.

Control flow and state: the header declares allocation-time parameters for the RM device tree. Once allocated, these handles become parents for controls such as display static info, FBSR, FIFO, GR, VMM, and internal GSP controls.

Dependencies and integration: consumed by RM device constructors and by `gsp->internal.device` static handles populated from `GET_GSP_STATIC_INFO` in `gsp.c`.

Risks and tests: VA sizing and subdevice ID fields must align with RM's expectations, particularly for multi-subdevice or SR-IOV paths. Test signals are successful client-device-subdevice construction and follow-on internal controls through the subdevice object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/disp.h

Purpose: this is the large R535 display RM control ABI excerpt. It describes internal display initialization controls, common display-object controls, connector/OR/DFP/DP queries, hotplug and DP IRQ notifications, backlight, ELD/audio, EDID, HDMI sink caps, infoframe/OD packets, AUX, indexed link rates, DP link control, MST/SST stream configuration, display channel pushbuffers, and PIO/DMA display channel allocation parameters.

Important APIs/types: internal controls include `NV2080_CTRL_INTERNAL_DISPLAY_WRITE_INST_MEM_PARAMS`, `NV2080_CTRL_INTERNAL_DISPLAY_GET_STATIC_INFO_PARAMS`, `NV2080_CTRL_INTERNAL_INIT_BRIGHTC_STATE_LOAD_PARAMS`, and `NV2080_CTRL_INTERNAL_DISPLAY_CHANNEL_PUSHBUFFER_PARAMS`. Display common controls include `NV0073_CTRL_SYSTEM_GET_NUM_HEADS`, `GET_SUPPORTED`, `GET_CONNECT_STATE`, `GET_ACTIVE`, connector data, OR info, DP caps, DFP info, SOR assignment, backlight get/set, ELD/audio, EDID, HDMI enable/caps, OD packet, AUX, indexed link rates, DP control, lane data, topology display ID allocation/free, stream config, and audio enable/mute. `NV50VAIO_CHANNELPIO_ALLOCATION_PARAMETERS` and `NV50VAIO_CHANNELDMA_ALLOCATION_PARAMETERS` support RM display channel allocation.

Control flow and state: the header contains no executable flow, but fields are used across display setup. Static info populates `nvkm_disp` window masks. Supported/connect/active queries drive output detection. DP caps and link controls drive link training policy. Backlight and ELD/audio controls reflect mutable display state. Channel pushbuffer and DMA allocation fields bind Nouveau display channel memory to RM.

Dependencies and integration: included by R535 display code and by R570 display code when the ABI is overridden with a newer R570 header. It depends on `nvrm/nvtypes.h` and Nouveau bitfield macros at call sites. It connects GSP-RM to DRM/KMS output probing, connector routing, DP AUX/link training, HDMI/DP audio, backlight, and pushbuffer channel setup.

Risks: display ABI drift is high-impact because many controls have dense bitfields, fixed array sizes, and firmware-defined masks. Duplicate command defines in the header are harmless at compile time if identical, but make maintenance error-prone. Wrong display IDs are expressed as bitmasks and can target the wrong connector. `NV0073_CTRL_DP_AUXCH_MAX_DATA_SIZE` and EDID buffer sizes must be respected by callers.

Test signals: KMS probing should return correct supported and connected masks, hotplug and DP IRQ events should arrive with correct notification payloads, DP caps/link rates should match hardware, EDID/AUX operations should succeed, backlight get/set should round-trip, HDMI/DP audio programming should work, and display channel pushbuffers should be accepted by RM without modeset hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/engine.h

Purpose: defines R535 engine identity constants used to translate RM/GSP engine descriptions into Nouveau subdevice and NV2080 engine types.

Important definitions: `MC_ENGINE_IDX_*` enumerates master-control interrupt engine indexes, including GSP, DISP, CE0-CE9, GR, NVDEC0-7, NVENC/MSENC0-2, NVJPEG0-7, and OFA0. `RM_ENGINE_TYPE` enumerates RM engine types for GR, copy, video, display-adjacent engines, NVJPEG, OFA, and support engines. `NV2080_ENGINE_TYPE_*` defines control/channel-facing engine types and helper macros for ranges and indexes.

Control flow and state: declarative only. In this work item, `r535_gsp_xlat_mc_engine_idx()` consumes `MC_ENGINE_IDX_*` to register interrupt vectors, and FIFO/channel code consumes `RM_ENGINE_TYPE`/`NV2080_ENGINE_TYPE` to translate RM engine discovery into Nouveau engine instances.

Dependencies and integration: included by `nvrm/gsp.h`, FIFO headers, and GSP code. It is a central contract between firmware tables and Nouveau engine enumeration.

Risks and tests: enum order and numeric values are ABI-sensitive. Unknown or shifted values can drop interrupts, bind channels to wrong engines, or skip discovered engines. Validation should compare RM engine info tables against Nouveau runlists and verify interrupt vectors, channel binding, and engine object allocation across all engine classes present on a GPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/event.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/event.h

Purpose: defines R535 RM event allocation and notification-control payloads plus the asynchronous post-event message format.

Important types: `NV0005_ALLOC_PARAMETERS` creates `NV01_EVENT_KERNEL_CALLBACK_EX` event objects, carrying parent client, source resource, event class, notify index, and callback data pointer. `NV2080_CTRL_EVENT_SET_NOTIFICATION_PARAMS` configures event actions such as repeat notification. `rpc_post_event_v17_00` is the message payload sent by GSP for posted events, including client handle, event handle, notify index, status, optional data, and notify-list flag.

Control flow and state: `gsp.c` registers `r535_gsp_msg_post_event()` for `POST_EVENT`. It looks up the low 16 bits of `hClient` in `gsp->client_id.idr`, scans the client's event list by `hEvent`, and invokes the event callback with `eventData`.

Dependencies and integration: used by RM event helpers and display/hotplug or other notification consumers. It connects firmware event delivery to Nouveau callback lists.

Risks and tests: message length validation is critical because `eventData[]` is flexible. Client/event handle mismatches produce dropped events. Tests should cover event allocation, notification enabling, hotplug/DP IRQ callbacks, and removal while events may be in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/fbsr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/fbsr.h

Purpose: defines the R535 framebuffer suspend/resume memory-list and control payloads. These structures let Nouveau describe system/FB memory regions that RM should preserve across suspend or runtime power transitions.

Important types: `rpc_alloc_memory_v13_01` allocates memory-list objects with client/device/memory handles, class, flags, length, page count, and embedded `pte_desc` entries. `NV2080_CTRL_INTERNAL_FBSR_INIT_PARAMS` initializes FBSR with type, region count, client/sysmem handles, GSP FB allocation offset, and GC-off state. `NV2080_CTRL_INTERNAL_FBSR_SEND_REGION_INFO_PARAMS` sends per-region vidmem/sysmem offsets and size. Constants define `NV01_MEMORY_LIST_FBMEM`, `NV01_MEMORY_LIST_SYSTEM`, `FBSR_TYPE_DMA`, and `NVOS02` memory flags.

Control flow and state: R535 and R570 FBSR code build memory list objects over scatter-gather system memory, initialize RM FBSR, and send region mappings. Persistent state includes the allocated system memory backing suspend data and RM memory object handles until resume cleanup.

Dependencies and integration: included by FBSR implementations and tied to `r535_gsp_fini()` suspend handling. It also intersects BAR/instmem state because resume must restore page tables before normal BAR2 use.

Risks and tests: size and page-count mismatches can corrupt preserved VRAM or fail resume. The flexible `pte_desc` layout is sensitive to allocation sizing and alignment. Tests should cover system suspend/resume, runtime suspend/resume, high VRAM allocation pressure, and verification that channels survive resume without forced reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/fbsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/fifo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/fifo.h

Purpose: defines R535 FIFO, channel, engine-info, constructed-falcon, context-promotion, scheduling, and RC-event ABI structures.

Important APIs/types: `NV2080_CTRL_FIFO_GET_DEVICE_INFO_TABLE_PARAMS` returns engine table entries with engine data, PBDMA IDs, fault IDs, and names. `ENGINE_INFO_TYPE` defines indexes into the `engineData` array. `NV2080_CTRL_CE_GET_FAULT_METHOD_BUFFER_SIZE_PARAMS` and `NV2080_CTRL_INTERNAL_GET_CONSTRUCTED_FALCON_INFO_PARAMS` support context/falcon buffer sizing. `NV_CHANNELGPFIFO_ALLOCATION_PARAMETERS` is the large channel allocation payload, carrying GP FIFO location, flags, VAS handle, UserD memory, engine type, channel ID, subdevice mask, instance/UserD/RAMFC/method-buffer memory descriptors, error notifiers, and security fields. `NVA06F_CTRL_BIND_PARAMS`, `NVA06F_CTRL_GPFIFO_SCHEDULE_PARAMS`, and `NV2080_CTRL_GPU_PROMOTE_CTX_PARAMS` support channel binding, scheduling, and GPU context promotion. `rpc_rc_triggered_v17_02` reports recovery/RC events in R535 form.

Control flow and state: the header is declarative, but its payloads are central to FIFO initialization. Device info table results populate Nouveau runlist/engine metadata. Channel allocation creates persistent RM channel objects over Nouveau-allocated instance, UserD, RAMFC, and method-buffer memory. Promote context controls attach context buffers to a channel.

Dependencies and integration: used by R535/R570 FIFO and GR code, with R570 overriding several definitions in its own header. It depends on engine enumerations and RM memory descriptor types.

Risks: `ENGINE_INFO_TYPE` ordering is explicitly compatibility-sensitive. Channel flags are dense bitfields; incorrect USERD page/index, privilege, or skip-map settings can break submissions. Memory descriptor address-space/cache attributes must match actual backing memory. RC payload layout differs in R570, so versioned headers must be paired with matching callbacks.

Test signals: engine discovery should produce correct runlists and instance counts, channel allocation should submit GP FIFO work, context promotion should succeed for GR/CE/video engines, RC events should map CHIDs back to Nouveau channels, and fault method buffer sizing should match RM expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/gr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/gr.h

Purpose: defines R535 graphics context-buffer and ZCULL-related control payloads used by GSP-backed GR initialization and context promotion.

Important definitions: `NV2080_CTRL_INTERNAL_STATIC_KGR_GET_CONTEXT_BUFFERS_INFO` returns `NV2080_CTRL_INTERNAL_STATIC_GR_GET_CONTEXT_BUFFERS_INFO_PARAMS`, an array of `NV2080_CTRL_INTERNAL_ENGINE_CONTEXT_BUFFER_INFO` entries per GR engine. Engine-context property IDs identify main, preemption, spill, pagepool, betacb, RTV, GFXP, FECS, privilege maps, and related buffer categories. `NV2080_CTRL_GPU_PROMOTE_CTX_BUFFER_ID_*` maps those categories into promote-context buffer IDs. The header includes `fifo.h` for `NV2080_CTRL_GPU_PROMOTE_CTX_PARAMS`.

Control flow and state: GR code reads this information to size/align context buffers, then allocates memory and promotes them into RM channel contexts. ZCULL context buffer size/alignment is also derived from this data.

Dependencies and integration: consumed by R535/R570 GR implementations, FIFO context promotion, and MMU/VMM helpers for mapping context buffers.

Risks and tests: stale buffer IDs or size/alignment fields can produce invalid contexts, GR channel failures, or RC events during rendering. Tests should include GR initialization, context creation/destruction, workloads that require preemption/context switching, and ZCULL-dependent rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/gr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/gsp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/gsp.h

Purpose: this is the main R535 GSP firmware/RM ABI header. It covers static GPU information, FB region metadata, system information, ACPI payloads, error/sequencer messages, firmware boot handoff metadata, shared message queue layout, suspend/resume metadata, RISCV firmware descriptors, interrupt-table controls, and WPR heap sizing constants.

Important APIs/types: `GspStaticConfigInfo` is returned by `GET_GSP_STATIC_INFO` and contains GR caps, GID, GPC/TPC/ZCULL masks, SKU, FB region info, SR-IOV caps, engine caps, SM info, FB topology, GFX preemption buffer sizing, names/branding flags, BAR PDE bases, VBIOS IDs, displayless limits, and internal RM handles. `GspSystemInfo` is sent by Nouveau and contains BAR physical addresses, BDF, user VA limit, PCI config mirror, ACPI method data, passthrough/hypervisor fields, and VF information. `PACKED_REGISTRY_TABLE` and `PACKED_REGISTRY_ENTRY` define registry RPC content. `rpc_run_cpu_sequencer_v17_00` and `GSP_SEQUENCER_BUFFER_CMD` define firmware-requested CPU-side register operations. `GspFwWprMeta`, `GspFwSRMeta`, `GSP_ARGUMENTS_CACHED`, `LibosMemoryRegionInitArgument`, `RM_RISCV_UCODE_DESC`, `msgqTxHeader`, and `msgqRxHeader` define boot, queue, and resume handoff state.

Control flow and state: `gsp.c` consumes this header heavily. Static info seeds Nouveau's internal client/device/subdevice handles, BAR PDBs, usable FB regions, reserved FB size, and GR counts. System info sends host PCI/BAR/ACPI context before RM initialization completes. Shared queue headers are initialized in coherent memory and then referenced through RM arguments. WPR and SR metadata describe firmware and resume buffers to the booter and GSP.

Dependencies and integration: includes `engine.h` and depends on `nvrm/nvtypes.h`. It integrates with RPC function IDs in `rpcfn.h`, message IDs in `msgfn.h`, falcon/SEC2 boot paths, ACPI display/mux probing, FBSR, BAR/MMU setup, and interrupt routing.

Risks: this header is packed with firmware-owned layouts. Field order, alignment, and exact constants are critical. The sequencer opcode sizing macro must match the union payloads or `gsp.c` will walk command buffers incorrectly. Queue header offsets and page counts must match the shared memory layout. WPR/SR metadata is exactly 256 bytes by design; size drift can break boot or resume authentication.

Test signals: static info should decode sane FB and GR topology, system info RPC should succeed on PCI devices with and without ACPI, queue traffic should work for small and split RPCs, CPU sequencer events should complete, GSP boot should validate WPR metadata, and suspend/resume should verify SR metadata handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/gsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/msgfn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/msgfn.h

Purpose: enumerates R535 GSP asynchronous message/event function IDs starting at `0x1000`.

Important definitions: events include `GSP_INIT_DONE`, `GSP_RUN_CPU_SEQUENCER`, `POST_EVENT`, `RC_TRIGGERED`, `MMU_FAULT_QUEUED`, `OS_ERROR_LOG`, `UCODE_LIBOS_PRINT`, `PERF_BRIDGELESS_INFO_UPDATE`, `GSP_SEND_USER_SHARED_DATA`, and others. The macro-based `E()` pattern lets includers either build the enum or reuse the list with a custom macro.

Control flow and state: `gsp.c` registers notification handlers for several of these IDs and polls for `GSP_INIT_DONE` during initialization. Message queue transport in `rpc.c` compares incoming RPC function IDs to these values.

Dependencies and integration: paired with `rpcfn.h` and the message queue ABI in `gsp.h`/`rpc.c`. Event payload layouts are defined in headers such as `event.h`, `fifo.h`, and `gsp.h`.

Risks and tests: numeric drift would route messages to the wrong handler or cause init polling to time out. Tests should verify boot completion, event fanout, RC/MMU fault logging, PMU libos print capture, and ignored/drop events not causing queue stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/msgfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvdec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvdec.h

Purpose: declares the R535 NVDEC/BSP allocation payload used by `nvdec.c`.

Important type: `NV_BSP_ALLOCATION_PARAMETERS` contains `size`, `prohibitMultipleInstances`, and `engineInstance`. The allocator sets `size` and `engineInstance`, leaving the multiple-instance prohibition defaulted.

Control flow and state: the structure is only used at RM object allocation time. The chosen `engineInstance` selects the physical decoder instance.

Dependencies and integration: included by `r535/nvdec.c` and indirectly used by the R535 API table's `.nvdec` engine allocator.

Risks and tests: incorrect structure size or instance value can break allocation. Test signals are successful object creation and decode workloads across all discovered NVDEC instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvdec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvenc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvenc.h

Purpose: declares the R535 NVENC/MSENC allocation payload used by `nvenc.c`.

Important type: `NV_MSENC_ALLOCATION_PARAMETERS` contains `size`, `prohibitMultipleInstances`, and `engineInstance`. `engineInstance` selects NVENC0, NVENC1, or NVENC2 in the R535 ABI.

Control flow and state: no executable code. The payload is populated immediately before RM allocation and then owned by firmware as part of object construction.

Dependencies and integration: consumed by the R535 NVENC engine allocator and tied to engine translation constants from `engine.h`.

Risks and tests: the layout is small but ABI-sensitive. Tests should allocate NVENC objects and run encode submissions on GPUs with one or more encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvenc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvjpg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvjpg.h

Purpose: declares the R535 NVJPG/NVJPEG allocation payload.

Important type: `NV_NVJPG_ALLOCATION_PARAMETERS` contains `size`, `prohibitMultipleInstances`, and `engineInstance`. The R535 allocator fills the size and instance fields.

Control flow and state: used only during RM object allocation. Persistent state after success is the RM object handle, not the stack/flexible payload.

Dependencies and integration: included by `r535/nvjpg.c` and aligned with NVJPEG engine indexes in `engine.h`.

Risks and tests: multiple-instance hardware needs correct `engineInstance` selection. Test signals include allocation and JPEG engine workload success for each advertised instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvjpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ofa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ofa.h

Purpose: declares the R535 optical-flow accelerator allocation payload.

Important type: `NV_OFA_ALLOCATION_PARAMETERS` contains `size` and `prohibitMultipleInstances`. Unlike NVDEC/NVENC/NVJPG, the R535 OFA payload has no explicit `engineInstance` field, and `ofa.c` only sets the size.

Control flow and state: allocation-time only. RM selects/constructs the OFA object according to class and payload.

Dependencies and integration: included by `r535/ofa.c` and selected through the R535 RM API table.

Risks and tests: if newer GPUs expose multiple OFA instances, this R535 shape cannot select an instance; R570 adds OFA1 engine identity elsewhere. Test signals are successful OFA object allocation and workload execution where OFA is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ofa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/rpcfn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/rpcfn.h

Purpose: enumerates the R535 GSP/RM RPC function numbers used on the command queue. The list spans legacy RM calls, GSP-specific static/system info calls, allocation/control/free calls, channel and GR controls, UVM-related functions, and newer maintenance controls.

Important definitions: key entries used in this work item include `NV_VGPU_MSG_FUNCTION_GET_GSP_STATIC_INFO`, `UNLOADING_GUEST_DRIVER`, `UPDATE_BAR_PDE`, `CONTINUATION_RECORD`, `GSP_SET_SYSTEM_INFO`, `SET_REGISTRY`, `GSP_RM_CONTROL`, `GSP_RM_ALLOC`, `CTRL_GPU_PROMOTE_CTX`, `CTRL_VASPACE_COPY_SERVER_RESERVED_PDES`, `CTRL_MC_SERVICE_INTERRUPTS`, and `NUM_FUNCTIONS`. The macro-based `X(UNIT, RPC)` list can either define an enum or be reused by custom macro expansion.

Control flow and state: `rpc.c` writes these values into `nvfw_gsp_rpc.function`, detects continuation records for split messages, and matches replies by function. `gsp.c` and RM helper layers select function IDs for boot-time and runtime operations.

Dependencies and integration: paired with payload headers such as `alloc.h`, `ctrl.h`, `gsp.h`, `bar.h`, `fifo.h`, and `vmm.h`. The transport layer's split-RPC logic depends on `CONTINUATION_RECORD` being correct.

Risks and tests: function-number drift is catastrophic because payloads would be interpreted by the wrong firmware handler. Split RPCs specifically require correct continuation function IDs. Test signals are successful boot RPCs, RM alloc/control/free sequences, large payload transfers, and correct errno mapping for RPC status failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/rpcfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/vmm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/vmm.h

Purpose: defines R535 virtual-address-space allocation and page-directory control ABI structures.

Important definitions: `FERMI_VASPACE_A` is the VAS class. `NV_VASPACE_ALLOCATION_PARAMETERS` carries index, flags, VA size/range, big page size, and base. `NV_VASPACE_ALLOCATION_FLAGS_IS_EXTERNALLY_OWNED` marks a Nouveau-owned/external VAS. `SPLIT_VAS_SERVER_RM_MANAGED_VA_START` and `_SIZE` define the 4 GiB plus 512 MiB reserved server-RM window. `NV90F1_CTRL_VASPACE_COPY_SERVER_RESERVED_PDES_PARAMS` describes page levels to copy for RM-reserved VA space. `NV0080_CTRL_DMA_SET_PAGE_DIRECTORY_PARAMS` and `UNSET_PAGE_DIRECTORY_PARAMS` bind or unbind external page directories to a VAS.

Control flow and state: `vmm.c` allocates RM VAS objects with this payload, either sets an external page directory for Nouveau-owned VMMs or reserves/copies RM-managed PDEs for internally owned ones. State persists in `vmm->rm.object`, `vmm->rm.device/client`, `vmm->rm.rsvd`, and `vmm->rm.external`.

Dependencies and integration: included by R535 VMM code and tied to MMU promotion, BAR/VMM page table data, and RM control helpers. Uses bitfield macros at call sites for page-directory aperture flags.

Risks and tests: page-level descriptions must reflect Nouveau's actual page table hierarchy and physical addresses. The reserved VA range is asserted in code, so mismatch breaks VAS creation. Tests should create/destroy external and internal VAS objects, bind channels to VAS, and exercise mappings around the reserved range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/vmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ofa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ofa.c

Purpose: provides the R535 RM engine allocator for OFA objects.

Important API: `r535_ofa_alloc()` allocates an `NV_OFA_ALLOCATION_PARAMETERS` payload using the parent channel, handle, class, and destination object. It sets only `args->size` and commits with `nvkm_gsp_rm_alloc_wr()`. The `r535_ofa` API table exposes this as `.alloc`.

Control flow and state: the function is stateless and ignores its `inst` parameter because the R535 OFA ABI payload has no instance field. The allocated `nvkm_gsp_object` becomes the persistent handle on success.

Dependencies and integration: depends on `rm/engine.h` and `nvrm/ofa.h`, and is selected through `r535_api.ofa`. It integrates with FIFO/engine discovery that decides whether an OFA object should be allocated.

Risks and tests: the unused instance argument is notable. It matches R535 payload shape, but multi-OFA support requires newer ABI handling. Test signals are successful OFA allocation on supported GPUs and no invalid-instance assumptions when RM reports OFA engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ofa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/rm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/rm.c

Purpose: assembles the R535 RM implementation descriptor and API table for Turing/Ampere-style GSP-RM operation.

Important definitions: `r535_wpr_libos2` and `r535_wpr_libos3` define WPR heap sizing policy from `GSP_FW_HEAP_*` constants. `r535_api` wires together the R535 module implementations: GSP, RPC, control, allocation, client, device, FBSR, display, FIFO, CE, GR, NVDEC, NVENC, NVJPG, and OFA. `r535_rm_tu102` uses the libos2 WPR sizing; `r535_rm_ga102` uses the libos3 sizing.

Control flow and state: no runtime flow is implemented here. The table determines which callbacks downstream Nouveau code invokes for the selected GPU/RM firmware generation. WPR sizing feeds firmware carveout allocation and boot metadata construction.

Dependencies and integration: includes `rm/rm.h` for API/implementation structures and `nvrm/gsp.h` for heap constants. It is a central integration point across all R535 implementation files.

Risks and tests: an incorrect API pointer mixes incompatible payload versions and can break boot, display, FIFO, or resume. Wrong WPR sizing can prevent firmware heap setup or under-allocate resume state. Test signals are successful RM implementation selection for TU102/GA102-family devices and coverage of each callback family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/rm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/rpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/rpc.c

Purpose: implements the R535 GSP command/message queue transport used by all RM RPC calls. It builds queue elements, computes message checksums, handles queue wraparound, splits oversized requests into continuation records, reassembles oversized replies, routes unsolicited event messages to registered callbacks, and exposes the `r535_rpc` API table.

Important APIs and types: local transport headers are `r535_gsp_msg` and `nvfw_gsp_rpc`. Public entry points are `r535_rpc_status_to_errno()`, `r535_gsp_msg_recv()`, `r535_gsp_msg_ntfy_add()`, `r535_gsp_rpc_poll()`, and the `r535_rpc` table with `.get`, `.push`, and `.done`. Helpers include `r535_gsp_msgq_wait()`, `r535_gsp_msgq_peek()`, `r535_gsp_msgq_recv_one_elem()`, `r535_gsp_msgq_recv()`, `r535_gsp_cmdq_get()`, `r535_gsp_cmdq_push()`, `r535_gsp_rpc_get()`, `r535_gsp_rpc_send()`, `r535_gsp_rpc_handle_reply()`, and `r535_gsp_rpc_push()`.

Control flow: callers allocate a payload with `.get`, which reserves a zeroed command queue message element and initializes the RPC header with version `0x03000000`, signature `CPRV`, function ID, result sentinels, and payload length. `.push` serializes on `gsp->cmdq.mutex`. If the payload exceeds one queue element's max payload, it sends the first chunk under the original function, then sends remaining chunks as `NV_VGPU_MSG_FUNCTION_CONTINUATION_RECORD`, then waits for the original reply according to the requested reply policy. Otherwise it sends one message. `r535_gsp_cmdq_push()` computes an XOR checksum over the aligned element, copies pages into the circular command queue, updates the write pointer with barriers, rings the falcon doorbell, and frees the allocated command buffer.

Receive behavior: `r535_gsp_msg_recv()` peeks the message queue, copies one or more queue elements, validates `rpc_result`, optionally matches a requested reply function, dispatches unsolicited messages through `gsp->msgq.ntfy[]`, and drains additional queued messages when called without a target function. `r535_gsp_msgq_recv()` allocates enough memory for the full RPC, handles queue wraparound, validates continuation records, strips repeated RPC headers from continuation payloads, and fixes the assembled length.

State and persistence: command and message queue read/write pointers point into shared memory initialized by `gsp.c`. `gsp->cmdq.seq` and `gsp->rpc_seq` are monotonically incremented in memory only. Notification registrations persist in `gsp->msgq.ntfy` for the life of the GSP object. RPC reply buffers returned to callers must be released with `.done`.

Dependencies and integration: depends on `rm/rpc.h`, R535 function IDs from `rpcfn.h`, shared queue layout from `gsp.h`, and falcon doorbells. All allocation, control, boot, registry, system-info, display, FIFO, GR, VMM, and FBSR paths depend on this transport.

Risks: queue length calculations, wraparound copies, barriers, and split-message size accounting are critical. A mismatch between requested `gsp_rpc_len` and firmware reply length can over-wait, under-copy, or reject valid messages. Large RPC send failure paths need to avoid leaking the original message buffer. Notification callbacks run while receiving under command-queue serialization, so long callbacks can delay replies.

Test signals: boot-time RPCs should complete, large RPC payloads should split and reassemble, unsolicited event storms should drain without starving expected replies, trace dumps should show correct lengths/function IDs, and failure injection should report `-ETIMEDOUT`, `-ENOMEM`, or status-derived errors cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/vmm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/vmm.c

Purpose: wraps a hardware `nvkm_mmu_func` with R535 GSP-RM virtual address space promotion support. It creates and destroys RM VASpace objects for Nouveau VMMs and teaches RM about either Nouveau-owned page directories or RM-reserved server PDE ranges.

Important APIs: `r535_mmu_vaspace_new()` constructs a GSP client/device pair, allocates a `FERMI_VASPACE_A` object, and either sets external ownership or reserves/copies server RM PDEs. `r535_mmu_vaspace_del()` unsets external page directories when needed, frees the RM VAS object, destroys device/client wrappers, and releases reserved VMM space. `r535_mmu_promote_vmm()` promotes an existing VMM as external using handle `NVKM_RM_VASPACE`. `r535_mmu_new()` clones the hardware MMU function table and overrides `.promote_vmm`.

Control flow: VAS creation first calls `nvkm_gsp_client_device_ctor()`. It prepares `NV_VASPACE_ALLOCATION_PARAMETERS`, sets `index = GPU_NEW`, and sets `IS_EXTERNALLY_OWNED` for external VMMs. For internal RM-managed VAS, it reserves the fixed 512 MiB server range at 4 GiB with 512 MiB page coverage, walks the Nouveau page descriptor hierarchy, fills `NV90F1_CTRL_VASPACE_COPY_SERVER_RESERVED_PDES_PARAMS` with physical addresses/sizes/apertures/page shifts for each page-table level, and writes the control. For external VAS, it sends `NV0080_CTRL_DMA_SET_PAGE_DIRECTORY` with the root page-table address, entry count, aperture VIDMEM flag, and VAS handle.

State and persistence: `vmm->rm.client`, `vmm->rm.device`, and `vmm->rm.object` persist while the VMM is promoted. `vmm->rm.rsvd` persists only for internally owned VAS and is released on delete. `vmm->rm.external` tracks whether an unset-page-directory control is required before free.

Dependencies and integration: depends on Nouveau MMU/VMM internals, `nvhw/drf.h` bitfield helpers, `nvrm/vmm.h`, GSP RM client/device helpers, and RM alloc/control functions. Channel allocation later consumes `vmm->rm.object.handle` as `hVASpace`.

Risks: failures after client/device construction or VAS allocation can leave partial RM objects unless higher-level destructors run. The server-reserved VA address and size are asserted; any firmware policy change requires header/code update. Page table walking assumes a compatible descriptor chain and uses `pd->pt[0]->addr` at each level. External unbind failure is warned but deletion proceeds.

Test signals: create/destroy promoted VMMs, allocate channels against promoted VAS handles, test mappings around the 4 GiB reserved range, validate external VMM teardown sends unset-page-directory, and run workloads after VMM promotion without MMU faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/vmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/Kbuild

Purpose: adds R570 GSP-RM implementation objects to the Nouveau `nvkm-y` build.

Important entries: it builds `rm.o`, `gsp.o`, `client.o`, `fbsr.o`, `disp.o`, `fifo.o`, `gr.o`, and `ofa.o` from `nvkm/subdev/gsp/rm/r570/`.

Control flow and state: no runtime logic. Build inclusion makes the R570 API implementation available to RM selection code.

Dependencies and integration: relies on the kernel Kbuild aggregation for `nvkm-y`. The listed files use R570 protocol headers and reuse many R535 helpers where compatible.

Risks and tests: missing an object here would produce unresolved symbols or silently omit a callback implementation from the final driver. Test signals are successful kernel/module build with R570 enabled and symbol presence for `r570_*` API tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/client.c

Purpose: implements the R570 root-client constructor for GSP-RM.

Important API: `r570_gsp_client_ctor()` allocates an `NV01_ROOT` object using `NV0000_ALLOC_PARAMETERS`, sets `hClient` to the object's handle and `processID` to `~0`, then commits the allocation. `r570_client` exposes this as `.ctor`.

Control flow and state: the constructor operates on `client->object` as both parent and destination, which is normal for a root object. On success, the client handle becomes the root for later RM allocations under this client. No process name is set in the zeroed payload.

Dependencies and integration: includes `rm/rm.h` and R570 `nvrm/client.h`. It is selected by the R570 API table and used wherever Nouveau creates a GSP client/device pair.

Risks and tests: the R570 root-client ABI may differ from R535, so using the matching header is important. Test signals are successful root client creation, follow-on device/subdevice allocations, and cleanup without leaked client handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/disp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/disp.c

Purpose: implements R570 display RM API callbacks. It adapts display channel allocation, pushbuffer registration, output probing, DP capability/link-rate setup, backlight control, and static display info to R570 protocol payloads.

Important APIs: `r570_dmac_alloc()` allocates display DMA channels with `NV50VAIO_CHANNELDMA_ALLOCATION_PARAMETERS`, setting channel instance, initial put offset, and `subDeviceId`. `r570_disp_chan_set_pushbuf()` sends `NV2080_CTRL_INTERNAL_DISPLAY_CHANNEL_PUSHBUFFER`, mapping Nouveau memory targets to RM `addressSpace`, `cacheSnoop`, and `pbTargetAperture`. `r570_dp_set_indexed_link_rates()` sends `DP_CONFIG_INDEXED_LINK_RATES`. `r570_dp_get_caps()` reads DP caps and translates RM max-link-rate enums to DPCD link bandwidth codes while returning MST and watermark support. `r570_bl_ctrl()` gets or sets percent backlight brightness. `r570_disp_get_active()`, `r570_disp_get_connect_state()`, `r570_disp_get_supported()`, and `r570_disp_get_static_info()` wrap common display controls. The exported `r570_disp` table wires these callbacks under `.get_static_info`, `.get_supported`, `.get_connect_state`, `.get_active`, `.bl_ctrl`, `.dp`, and `.chan`.

Control flow and state: most functions allocate a control buffer, populate display IDs as `BIT(index)` masks or subdevice instance 0, push/read the control, copy output fields into Nouveau state, and call `_done()` for readback controls. Static info updates `disp->wndw.mask` and `disp->wndw.nr`. Pushbuffer registration can also invalidate a channel for class low byte `0x7a`.

Dependencies and integration: depends on `rm/rm.h`, display engine/output structures, `nvhw/drf.h`, and R570 `nvrm/disp.h`. It integrates with DRM/KMS output probing, DP training, backlight, audio/ELD paths, and display channel setup.

Risks: `r570_dp_set_indexed_link_rates()` indexes `linkRateTbl` by `outp->dp.rate[i].dpcd` while only checking `outp->dp.rates` against array size; malformed DPCD indexes would be dangerous if not constrained earlier. Memory target to aperture translation must match RM's R570 fields (`pbTargetAperture` is R570-specific). Backlight uses `brightnessType`, also R570-specific. Missing `_done()` on some error paths after `ctrl_push()` failure can leak control buffers depending on helper semantics.

Test signals: modeset and hotplug probing should work, window masks should match hardware, DP caps should report correct link rates/MST/watermark support, indexed link-rate programming should succeed for UHBR-capable links, backlight get/set should round-trip, and display DMA channels should allocate with working pushbuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/disp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/fbsr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/fbsr.c

Purpose: implements R570 framebuffer suspend/resume callbacks. It preserves BAR/instance-memory state around GSP suspend, disables active channel scheduling through a new internal FIFO control, allocates system backing for RM's VRAM state, and delegates common cleanup to R535 helpers where compatible.

Important APIs: `r570_fbsr_suspend_channels()` writes `NV2080_CTRL_INTERNAL_FIFO_TOGGLE_ACTIVE_CHANNEL_SCHEDULING`. `r570_fbsr_init()` creates a host memory-list object with `r535_fbsr_memlist()`, sends `NV2080_CTRL_INTERNAL_FBSR_INIT`, and passes `gsp->sr.meta.addr` as `sysmemAddrOfSuspendResumeData`. `r570_fbsr_suspend()` stops scheduling, saves preserved and boot instmem objects, disables BAR2, sizes and allocates `gsp->sr.fbsr`, and initializes RM FBSR. `r570_fbsr_resume()` restores boot BAR2 page tables via BAR0, re-enables BAR2, flushes BAR2 VMM, restores remaining instmem objects, flushes BAR1 VMM, resumes scheduling, and calls `r535_fbsr_resume()`.

Control flow and state: suspend saves state from `device->imem->list` and `imem->boot`, marks `device->bar->bar2 = false`, and allocates `gsp->sr.fbsr` sized from `gsp->fb.heap.size`, `gsp->fb.rsvd_size`, and VGA workspace size. Resume reverses BAR accessibility in stages so page tables are available before normal BAR2-backed restore.

Dependencies and integration: depends on instmem private APIs, BAR helpers, GSP, VMM, R570 FBSR/FIFO headers, and R535 FBSR memory-list/resume helpers. It is invoked from `r535_gsp_fini()`/`r535_gsp_init()` through the selected RM API's `.fbsr` callbacks.

Risks: errors after scheduling is disabled or BAR2 is disabled must be unwound by higher-level failure handling; this file does not re-enable scheduling on all suspend failure paths. FBSR size calculation must include all RM VRAM allocations or resume may lose state. Resume order is critical because BAR2 page tables themselves need restoring before BAR2 can be used.

Test signals: runtime and system suspend/resume should preserve channels and instmem allocations, BAR1/BAR2 VMM flushes should occur without faults, active channel scheduling should stop and resume, and post-resume workloads should not see unexpected channel resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/fbsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/fifo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/fifo.c

Purpose: implements R570 FIFO RM API callbacks for channel allocation, RC event handling, constructed-falcon context sizing, and RM engine-type translation.

Important APIs: `r570_chan_alloc()` fills `NV_CHANNELGPFIFO_ALLOCATION_PARAMETERS` for a physical GPFIFO channel, including GP FIFO offset/entries, dense `NVOS04_FLAGS`, fixed USERD page/index based on `CHID_PER_USERD`, VAS handle, engine type, instance/UserD/RAMFC/method-buffer descriptors, privilege, and notifier types. `r570_fifo_rc_triggered()` logs R570 RC payload fields including GFID, exception level, MMU fault address/type, and calls `r535_fifo_rc_chid()` to mark the affected channel. `r570_fifo_ectx_size()` reads `NV2080_CTRL_CMD_GPU_GET_CONSTRUCTED_FALCON_INFO` and updates matching `engn->rm.size` by `engDesc`. `r570_fifo_xlat_rm_engine_type()` maps R570 `RM_ENGINE_TYPE_*` values to Nouveau subdevice type and NV2080 engine type, extending copy engines through COPY19, NVENC3, and OFA1. `r570_fifo` exports these callbacks and sets `.rsvd_chids = 1`.

Control flow and state: channel allocation constructs persistent RM channel objects using Nouveau-allocated memory addresses. Engine context sizing iterates the returned constructed-falcon table and then all runlists/engines to update per-engine RM context buffer sizes. Engine translation returns the Nouveau instance as the function return value and writes type/NV2080 type through output pointers.

Dependencies and integration: includes RM, MMU, FIFO private channel/runlist headers, `nvhw/drf.h`, R570 FIFO and engine headers, and reuses R535 RC CHID handling. It feeds GR and other engine channel setup through `rm->api->fifo->chan.alloc`.

Risks: channel flag construction is bitfield-heavy; a wrong flag can affect privilege, USERD placement, scheduling, or method-buffer setup. Address-space/cache attributes are hard-coded (`2/1` for instance/UserD/RAMFC and `1/0` for method buffer), so they must match actual memory placement. Engine translation must stay aligned with R570 headers or engines will be missing/misclassified. The RC handler assumes the R570 payload size and field names, which differ from R535.

Test signals: create user and privileged channels on GR/CE/video engines, verify USERD placement by CHID, submit workloads, provoke or simulate RC events, check constructed falcon sizes populate matching engines, and validate discovery of COPY10-19, NVENC3, and OFA1 where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/gr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/gr.c

Purpose: implements R570 GR RM API callbacks for topology queries, context buffer/ZCULL information, and a TU10x-specific graphics scrubber workaround channel.

Important APIs: `r570_gr_tpc_mask()` and `r570_gr_gpc_mask()` query GPC/TPC masks through R570/RM controls. `r570_gr_get_ctxbufs_and_zcull_info()` reads static GR context-buffer info, passes entries to `r535_gr_get_ctxbuf_info()`, extracts ZCULL context size/alignment, then reads `NV2080_CTRL_CMD_GR_GET_ZCULL_INFO` and populates `gr->base.zcull_info`. `r570_gr_scrubber_init()` conditionally creates a scrubber channel on TU10x chipsets `0x162`, `0x164`, and `0x166`: it obtains a CHID, allocates instance memory, creates a VMM, creates an RM VAS with `r535_mmu_vaspace_new()`, allocates a FIFO channel, promotes GR context buffers, allocates a 3D object, and enables RM's bug-4208224 workaround. `r570_gr_scrubber_fini()` tears that state down and sends teardown control if enabled. `r570_gr` exports `.get_ctxbufs_and_zcull_info` and scrubber init/fini callbacks.

Control flow and state: scrubber state persists in `gr->scrubber`: CHID, instance memory, VMM, context buffers/VMAs, channel object, 3D object, and enabled flag. Initialization is all-or-nothing; any failure calls `r570_gr_scrubber_fini()`. Context buffer info persists in `r535_gr`/base GR structures and informs later context promotion.

Dependencies and integration: depends on RM GR helpers, MMU, FIFO/CHID, GR private structures, R570 GR/engine headers, and R535 helpers for VAS creation, context promotion, and context buffer interpretation. It integrates with FIFO channel allocation and RM API callbacks.

Risks: the scrubber path is chipset-gated and allocates several interdependent resources; teardown must tolerate partially initialized state. Context buffer and ZCULL control IDs differ between RM generations, so pairing with R570 headers matters. CHID allocation for the scrubber consumes a FIFO channel ID and must not conflict with user channels.

Test signals: query GPC/TPC masks and compare against static info, initialize GR contexts, verify ZCULL info is populated, boot TU10x devices through scrubber init/fini, run graphics workloads that require context switching, and inspect error logs for bug-4208224 or RC-triggered failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/gr.c -->
