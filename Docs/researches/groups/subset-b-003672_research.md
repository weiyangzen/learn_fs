# Research: subset-b-003672

Grouped research for Nouveau DRM files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau`. Each section preserves the original source path for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dmem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dmem.c

## Purpose
Implements Nouveau's HMM device-private memory support for SVM-enabled GPUs. The file allocates GPU VRAM-backed `MEMORY_DEVICE_PRIVATE` pages, migrates CPU pages into VRAM, migrates them back on CPU faults or device teardown, and uses the GPU copy engine to move or clear page contents. It is enabled only for Pascal and newer devices with a supported DMA copy class.

## Important APIs, Types, and Functions
Key internal types are `struct nouveau_dmem`, `struct nouveau_dmem_chunk`, `struct nouveau_dmem_migrate`, and `struct nouveau_dmem_dma_info`. `nouveau_dmem_init()`, `nouveau_dmem_fini()`, `nouveau_dmem_suspend()`, and `nouveau_dmem_resume()` are the lifecycle hooks called from the DRM device lifecycle. `nouveau_dmem_migrate_vma()` is the SVM-facing entry for migrating a VMA range from system memory to GPU private memory. `nouveau_dmem_migrate_to_ram()` is registered through `dev_pagemap_ops` and is invoked by the mm subsystem when the CPU faults on a device-private page. `nouveau_dmem_page_addr()` converts a device-private `struct page` back to the VRAM offset inside its pinned BO.

The Pascal+ copy-engine implementation is in `nvc0b5_migrate_copy()` and `nvc0b5_migrate_clear()`, selected by `nouveau_dmem_migrate_init()` based on `drm->ttm.copy.oclass`.

## Control Flow
Initialization allocates `drm->dmem`, initializes locks and chunk lists, and binds migration callbacks to the existing TTM copy channel. GPU-private allocation is chunk based: `nouveau_dmem_page_alloc_locked()` first consumes a free page or THP-sized folio, otherwise calls `nouveau_dmem_chunk_alloc()`, which reserves a fake physical address range, allocates a pinned VRAM BO, registers device-private pages with `memremap_pages()`, and pushes all pages onto free lists.

System-to-device migration uses `migrate_vma_setup()`, allocates destination device pages, DMA-maps source pages when present, emits copy or clear commands into the copy channel, calls `migrate_vma_pages()`, waits on a Nouveau fence, maps resulting PFNs into the SVM page tables, unmaps DMA addresses, and finalizes migration. Device-to-system migration on fault allocates a CPU page or folio, invalidates the SVM range under `svmm->mutex`, copies VRAM to host memory, calls `migrate_vma_pages()`, waits for the copy fence, unmaps DMA, and finalizes.

## State and Persistence
State is in-memory only: chunk list, free page/folio lists, per-chunk allocation counts, pinned BOs, dev_pagemap ranges, and migration channel callbacks. Device-private pages store either free-list links or `svmm` pointers in `zone_device_data`. Suspend unpins chunks; resume re-pins them. Finalization evicts all device-private pages back to system memory before unmapping pages and freeing BOs.

## Dependencies and Integration Points
This file depends on Linux HMM/migration APIs, `memremap_pages()`, TTM BO allocation, DMA mapping, Nouveau fences, copy-channel push macros, and SVM PFN mapping helpers. It integrates with `nouveau_drm.c` lifecycle hooks and with SVM code through `nouveau_dmem_migrate_vma()` and `nouveau_pfns_map()`.

## Risks and Test Signals
Risk is high around lifetime and migration error handling. The source contains FIXME notes for TTM-based VRAM page allocation, missing chunk reclaim, and no explicit channel-idle wait when no fence exists. Fault paths have early returns after `migrate_vma_setup()` that bypass shared cleanup in some branches. Large folio handling, DMA map/unmap sizes, suspend pin failures, and teardown eviction need stress coverage. Test signals include SVM migration tests, CPU fault-back after GPU migration, transparent huge page migration, suspend/resume with active device-private mappings, module unload with migrated pages, copy-engine failure injection, and lockdep around `svmm->mutex`, dmem spinlock, and migration callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dmem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dmem.h

## Purpose
Declares the public interface for Nouveau device-private memory support. It hides the HMM/DMEM implementation behind lifecycle, migration, and address helpers, and compiles to no-op stubs when `CONFIG_DRM_NOUVEAU_SVM` is disabled.

## Important APIs, Types, and Functions
The header forward-declares DRM and Nouveau structures and declares `nouveau_dmem_init()`, `nouveau_dmem_fini()`, `nouveau_dmem_suspend()`, `nouveau_dmem_resume()`, `nouveau_dmem_migrate_vma()`, and `nouveau_dmem_page_addr()`. `nouveau_dmem_migrate_vma()` accepts a `struct nouveau_drm`, `struct nouveau_svmm`, `struct vm_area_struct`, and address range for migration into GPU private memory.

## Control Flow
Consumers call lifecycle hooks from device init, suspend, resume, and fini without needing local `#ifdef` blocks. When SVM is disabled, the init/fini/suspend/resume hooks become empty inline functions; migration/address helpers are not exposed because no caller should perform DMEM migration without SVM.

## State and Persistence
The header owns no state. It defines the contract for the opaque `drm->dmem` pointer managed by `nouveau_dmem.c`.

## Dependencies and Integration Points
The header includes `nvif/os.h` for kernel/NVIF environment definitions and is included by `nouveau_drm.c`, SVM-related code, and the DMEM implementation. It forms the compile-time boundary between optional SVM memory migration support and the always-built DRM lifecycle.

## Risks and Test Signals
The main risk is feature gating: callers must not invoke migration helpers when SVM support is absent. Build coverage should include both `CONFIG_DRM_NOUVEAU_SVM=y/m` and disabled configurations. Runtime signals are that device init/fini and PM paths remain harmless on unsupported configurations and older GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dp.c

## Purpose
Implements DisplayPort probing, capability discovery, link training, HPD IRQ service, and mode validation for Nouveau encoders. It supports SST, optional MST, LTTPR probing, eDP fixed-rate tables, sink count handling, and downstream bandwidth limits.

## Important APIs, Types, and Functions
The external functions are `nouveau_dp_detect()`, `nouveau_dp_train()`, `nouveau_dp_power_down()`, `nouveau_dp_link_check()`, `nouveau_dp_irq()`, and `nv50_dp_mode_valid()`. Internal helpers include `nouveau_dp_probe_dpcd()`, `nouveau_dp_probe_lttpr()`, `nouveau_dp_has_sink_count()`, `nouveau_dp_train_link()`, and `nouveau_dp_link_check_locked()`. Module parameter `mst` controls whether MST capability is used.

## Control Flow
Detection powers the AUX path, serializes on `outp->dp.hpd_irq_lock`, handles eDP cached status, asks NVIF for physical detect status, reads DPCD and LTTPR capabilities, clamps lanes and rates by DCB and repeater limits, programs supported rates through `nvif_outp_dp_rates()`, reads DP descriptor/downstream info, and decides between disconnected, SST, or MST. If MST is active, detection delegates topology setup to `nv50_mstm_detect()`.

Training computes a minimum link rate from MST maximum link capacity or SST mode clock/bpc, then tries decreasing lane counts and advertised rates until `nvif_outp_dp_train()` succeeds. Certain sinks require post-link-training adjustment loops using DPCD link status and `nvif_outp_dp_drive()`. IRQ handling services MST topology or CEC/sink-count changes and then reports HPD events through `nouveau_connector_hpd()`. Mode validation compares mode bandwidth against cached link capacity and DP downstream dotclock.

## State and Persistence
Persistent per-encoder DP state lives in `struct nouveau_encoder`: DPCD bytes, LTTPR caps/count, sorted link rates, lane count, max bandwidth, sink descriptor, downstream ports, sink count, and current training settings. This state is protected for IRQ-sensitive paths by `hpd_irq_lock`.

## Dependencies and Integration Points
The file integrates with DRM DP helpers, DRM MST helpers through `nv50_mstm_*`, NVIF output methods (`nvif_outp_detect`, AUX power, rates, train, drive), connector HPD handling, and encoder/connector state from Nouveau display code.

## Risks and Test Signals
Risks include incorrect AUX power state on GSP-managed disconnected ports, MST state races during suspend, malformed DPCD/rate arrays, LTTPR corner cases, and retraining loops that hide persistent link failures. Test signals include DP/eDP hotplug, MST hub plug/unplug, sink-count dongles, LTTPR repeaters, high-bpc HDR mode lists, suspend/resume with MST active, link loss IRQ retraining, and mode validation against low-bandwidth adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_drm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_drm.c

## Purpose
Provides the main DRM driver entry point for Nouveau. It owns module parameters, PCI/platform device creation, NVIF client/device/MMU setup, global DRM driver callbacks, ioctl dispatch, client lifetime, acceleration channel initialization, suspend/resume/runtime PM, and module registration.

## Important APIs, Types, and Functions
Important externally visible functions include `nouveau_pmops_suspend()`, `nouveau_pmops_resume()`, `nouveau_pmops_runtime()`, `nouveau_drm_ioctl()`, `nouveau_platform_device_create()`, and `nouveau_drm_device_remove()`. Internal lifecycle functions include `nouveau_drm_device_new()`, `nouveau_drm_device_init()`, `nouveau_drm_device_fini()`, `nouveau_drm_device_del()`, `nouveau_drm_probe()`, and `nouveau_drm_remove()`. Client helpers are `nouveau_cli_init()`, `nouveau_cli_fini()`, and `nouveau_cli_work_queue()`. Acceleration setup is split across `nouveau_accel_init()`, `nouveau_accel_fini()`, `nouveau_accel_gr_init()`, and `nouveau_accel_ce_init()`.

## Control Flow
Module init clones a common `driver_stub` into PCI and platform drivers, evaluates `modeset`, initializes debugfs/backlight/DSM hooks, registers optional platform support, then registers the PCI driver. PCI probe verifies switcheroo readiness, creates an NVKM PCI device, removes conflicting framebuffers, allocates the DRM/NVIF device stack, enables PCI, initializes the device stack, and starts DRM client setup. Device initialization creates the shared scheduler workqueue, initializes the root client and client list, sets up VGA, TTM, BIOS, acceleration/fences/channels, display, debugfs, hwmon, SVM, DMEM, LED support, runtime PM, and finally calls `drm_dev_register()`.

Open creates a per-file `nouveau_cli`, initializes NVIF client/device/MMU/VMM and scheduler state, and links it into `drm->clients`. Postclose tears down ABI16, removes the client, and releases VMM/MMU/device/client state. Ioctl dispatch runtime-resumes the device, routes the legacy NVIF ioctl specially, otherwise calls DRM core ioctl handling, then autosuspends. PM suspend stops SVM/DMEM/LED, suspends display, evicts VRAM resources, idles kernel channels, suspends fences and the NVIF object tree, and powers PCI down. Resume reverses the NVIF, fence, VBIOS/display, LED, DMEM, and SVM steps.

## State and Persistence
Driver state is held in `struct nouveau_drm`: NVKM/NVIF objects, root and per-file clients, TTM and GEM accounting, fence backend, channel/runlist metadata, kernel channels, display state, debugfs/hwmon/LED/SVM/DMEM pointers, and audio component state. Module parameters persist for module lifetime and control debug, acceleration, modeset, atomic exposure, and runtime PM policy.

## Dependencies and Integration Points
This file connects Linux DRM core, PCI/platform buses, PM runtime, VGA switcheroo, aperture removal, NVKM/NVIF, TTM, GEM, display, hwmon, LED, SVM/DMEM, debugfs, ABI16, VM_BIND, and EXEC. The DRM ioctl table exposes legacy GEM/pushbuf/SVM ioctls plus VM_BIND and EXEC.

## Risks and Test Signals
Risk is concentrated in init/fini unwinding, runtime PM ordering, hot-unplug behavior, client cleanup while file descriptors remain open, fence/channel backend selection by class, and the D3hot/D3cold bridge quirk. Test signals include probe failure injection at every stage, module unload after open files, runtime autosuspend/resume under ioctl load, system suspend/resume, hibernation freeze/thaw, kexec shutdown, Optimus switcheroo, noaccel/headless modes, and ioctl access through render nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_drm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_drv.h

## Purpose
Defines the central Nouveau DRM data structures, driver identity, logging helpers, client abstraction, global device object, PM prototypes, platform creation prototype, and legacy NVKM accessors used across the driver.

## Important APIs, Types, and Functions
Key types are `struct nouveau_cli`, `struct nouveau_cli_work`, `struct nouveau_drm`, `struct nouveau_drm_tile`, `enum nouveau_drm_object_route`, and `enum nouveau_drm_handle`. Inline helpers include `nouveau_cli()`, `nouveau_cli_uvmm()`, `nouveau_cli_uvmm_locked()`, `nouveau_cli_vmm()`, `nouveau_cli_disable_uvmm_noinit()`, `u_memcpya()`, `u_free()`, `nouveau_drm()`, `nouveau_drm_use_coherent_gpu_mapping()`, and `nvxx_device()` plus NVKM subdevice macros. Prototypes include PM hooks, platform device creation, device removal, and client deferred work queueing.

## Control Flow
This header does not execute control flow directly, but it shapes cross-file control flow by determining how callers resolve per-file clients, select classic VMM versus SVM versus UVMM, copy arrays from userspace safely with overflow checking, and log through the correct DRM/client context. `nouveau_cli_disable_uvmm_noinit()` is part of the UAPI separation flow that prevents mixing legacy GEM pushbuf and VM_BIND/EXEC APIs.

## State and Persistence
`struct nouveau_drm` is the persistent per-device state root. It contains NVIF root objects, the root client, per-file client list, TTM/GEM accounting, synchronization backend, channel/runlist metadata, scheduler workqueue, kernel acceleration channels, tiling state, display/HPD state, PM helpers, hwmon/debugfs/LED/SVM/DMEM pointers, and audio component registration state. `struct nouveau_cli` is persistent per DRM file or root client and owns VMM/MMU/device objects, optional UVMM/SVM contexts, scheduler, ABI16 object list, deferred work, and naming.

## Dependencies and Integration Points
Includes Linux notifier and DRM/TTM headers, NVIF client/device/ioctl/MMU/VMM headers, UAPI Nouveau DRM definitions, and local fence/BIOS/scheduler/VMM/UVMM headers. Nearly every Nouveau DRM file depends on this header for the device and client model.

## Risks and Test Signals
Risks are ABI and locking related: changes to these structures affect many subsystems. The direct NVKM accessor macros are explicitly discouraged for new code, especially with GSP-RM paths where NVKM subdevices can be stubbed. Test signals include allmodconfig builds, GSP and non-GSP devices, legacy and UVMM UAPI separation tests, lockdep around `client_mutex`/`clients_lock`/client locks, and compile coverage for optional subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_encoder.h

## Purpose
Defines Nouveau's encoder wrapper and DisplayPort/MST state shared by the display implementation. It bridges DRM encoder objects, NVIF output objects, BIOS DCB data, connector association, DP training state, audio flags, and display-specific callbacks.

## Important APIs, Types, and Functions
Primary types are `struct nouveau_encoder` and `struct nv50_mstm`. Helpers include `nouveau_encoder()`, `to_drm_encoder()`, and the external `find_encoder()`. The header declares DP functions from `nouveau_dp.c`: `nouveau_dp_detect()`, `nouveau_dp_train()`, `nouveau_dp_power_down()`, `nouveau_dp_link_check()`, `nouveau_dp_irq()`, and `nv50_dp_mode_valid()`. It also declares connector lookup helpers and MST functions `nv50_mstm_detect()`, `nv50_mstm_remove()`, and `nv50_mstm_service()`.

## Control Flow
Display code stores hardware programming callbacks in each encoder and uses the inline wrappers to move between DRM and Nouveau encoder types. DP detection/training/control paths update and consume the nested `dp` state. MST state is managed through `struct nv50_mstm`, whose flags are protected by the encoder's `dp.hpd_irq_lock`.

## State and Persistence
`struct nouveau_encoder` persists per output. It holds DCB output data, NVIF output handle, output resource index, bound connector, optional I2C adapter, currently programmed CRTC and mode, audio enable flag, HDMI enable flag, DP caps/DPCD/rates/lane/bandwidth/training state/downstream descriptor/sink count, interlace capability, and save/restore/update callbacks. `struct nv50_mstm` persists MST topology state, including topology manager, `can_mst`, `is_mst`, `suspended`, `modified`, `disabled`, and link count.

## Dependencies and Integration Points
The header depends on NVIF output definitions, BIOS DCB definitions, DRM DP and MST helpers, and legacy display encoder wrappers. It is consumed by DP, connector, and NV50 display code.

## Risks and Test Signals
Risks include stale cached DP state, lock ordering around HPD IRQ service, MST suspend/resume transitions, and callback assumptions about programmed CRTC versus DRM's proposed state. Test signals include encoder enumeration, DP hotplug, MST topology changes, display suspend/resume, audio enable transitions, and link training/state cache resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_exec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_exec.c

## Purpose
Implements the `DRM_NOUVEAU_EXEC` ioctl for the new VM_BIND/EXEC UAPI. It schedules asynchronous push-buffer execution jobs on an ABI16 channel while coordinating GPUVM reservations, syncobjs, scheduler credits, and a Nouveau hardware fence.

## Important APIs, Types, and Functions
External entry points are `nouveau_exec_job_init()` and `nouveau_exec_ioctl_exec()`. The job operation callbacks are `nouveau_exec_job_submit()`, `nouveau_exec_job_armed_submit()`, `nouveau_exec_job_run()`, `nouveau_exec_job_free()`, and `nouveau_exec_job_timeout()`, collected in `nouveau_exec_job_ops`. Helpers `nouveau_exec_ucopy()` and `nouveau_exec_ufree()` copy/free userspace arrays for waits, signals, and push descriptors.

## Control Flow
The ioctl obtains ABI16 state, requires an initialized UVMM, finds the requested channel by CHID, rejects killed or pre-NV50 channels, bounds push count by half the GPFIFO ring minus one fence slot, copies userspace push and sync arrays, and submits a job. Job init validates per-push length against `NV50_DMA_PUSH_MAX_LENGTH`, duplicates push descriptors, attaches scheduler/sync metadata, and initializes the generic Nouveau job. Submit creates a fence but delays emission, locks GPUVM execution state, and validates backing reservations. Armed submit attaches the scheduler done fence to reservations. Run waits for GPFIFO space, pushes each indirect buffer, posts the channel, emits the hardware fence, and returns its `dma_fence`. Timeout kills the channel and asks the scheduler for reset handling.

## State and Persistence
Per-job state is transient in `struct nouveau_exec_job`: generic job base, channel, copied push descriptors, and a hardware fence pointer. Persistent state comes from the per-file `nouveau_cli`, UVMM, ABI16 channel list, channel scheduler, and channel kill flag.

## Dependencies and Integration Points
The file integrates with DRM GPU scheduler through `nouveau_sched`, DRM GPUVM exec validation, syncobjs through the generic job layer, ABI16 channel lookup, Nouveau fences, NVIF GPFIFO submission, UVMM state, and the ioctl table in `nouveau_drm.c`.

## Risks and Test Signals
Risks include mismatched legacy ABI16 channel ownership with new UVMM requirements, malformed userspace arrays, scheduler/fence lifetime errors, GPFIFO credit miscalculation, and timeout channel-kill behavior. Test signals include EXEC with zero and many push buffers, invalid channel IDs, killed channels, pre-NV50 channels, syncobj wait/signal chains, VM_BIND dependency ordering, timeout injection, and userspace pointer fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_exec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_exec.h

## Purpose
Declares data structures and APIs for Nouveau EXEC jobs. It is the local contract between the DRM ioctl layer, scheduler job implementation, and command submission code.

## Important APIs, Types, and Functions
`struct nouveau_exec_job_args` carries file private data, scheduler, channel, input sync array, output sync array, and push descriptor array. `struct nouveau_exec_job` embeds `struct nouveau_job`, stores the pending Nouveau fence, selected channel, and copied push descriptors. `to_nouveau_exec_job()` converts a generic job to an EXEC job. Declared functions are `nouveau_exec_job_init()` and `nouveau_exec_ioctl_exec()`. The inline `nouveau_exec_push_max_from_ib_max()` computes a conservative push descriptor limit from GPFIFO depth.

## Control Flow
The header's inline push limit reserves half the indirect-buffer ring and leaves one additional slot for the hardware fence, preventing jobs from starving the channel ring between submissions.

## State and Persistence
The types define transient per-ioctl/per-job state only. Persistent state remains in the scheduler, channel, client, and UVMM objects referenced by pointers.

## Dependencies and Integration Points
Includes `nouveau_drv.h` and `nouveau_sched.h`, and relies on UAPI structures such as `drm_nouveau_exec_push` and `drm_nouveau_sync`. It is included by `nouveau_exec.c` and registered through `nouveau_drm.c`.

## Risks and Test Signals
Risks are mostly ABI boundary and ring-capacity related. Tests should cover push count limits for small and large `ib_max`, structure lifetime after userspace array copy, and build coverage when scheduler and VM_BIND support are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_fence.c

## Purpose
Implements Nouveau's common `dma_fence` wrapper and channel fence tracking. It provides fence creation, emission, signaling, waiting, synchronization against BO reservations, uevent-assisted callbacks, context teardown, and killed-channel cleanup for multiple hardware-specific fence backends.

## Important APIs, Types, and Functions
External functions include `nouveau_fence_create()`, `nouveau_fence_new()`, `nouveau_fence_emit()`, `nouveau_fence_done()`, `nouveau_fence_wait()`, `nouveau_fence_sync()`, `nouveau_fence_unref()`, `nouveau_fence_context_new()`, `nouveau_fence_context_del()`, `nouveau_fence_context_free()`, and `nouveau_fence_context_kill()`. Internal helpers include `nouveau_fence_signal()`, `nouveau_fence_update()`, `nouveau_fence_wait_legacy()`, `nouveau_fence_wait_busy()`, `nouveau_fence_is_signaled()`, and uevent callback/work handlers. The file defines legacy and uevent `dma_fence_ops`.

## Control Flow
Each channel owns a `nouveau_fence_chan` with a pending list, sequence counter, backend callbacks, lock, and optional NVIF non-stall interrupt event. `nouveau_fence_emit()` initializes the dma_fence, increments the context sequence, calls the backend emit method, then under lock updates already-completed fences and appends the new fence to pending. Signaling walks pending fences in sequence order based on the backend `read()` callback. Uevent mode allows NVIF events to schedule work that updates pending fences; legacy mode relies on polling/wait hooks. `nouveau_fence_sync()` iterates reservation fences, tries local GPU-side sync via backend `sync()`, and falls back to CPU waits when needed.

## State and Persistence
Per-channel state persists in `struct nouveau_fence_chan`: pending/flip lists, lock, kref, backend callbacks, sequence/context IDs, name, event, notify count, dead flag, and killed flag. Per-fence state includes the embedded `dma_fence`, pending-list node, RCU channel pointer, and timeout.

## Dependencies and Integration Points
The file depends on Linux dma-fence/dma-resv APIs, NVIF channel events, trace/fence infrastructure, Nouveau channel objects, and hardware-specific fence backend constructors declared in the header. GEM validation, EXEC, DMEM migration, display flips, and BO lifetime management all consume these fences.

## Risks and Test Signals
Risks include list lifetime under `dma_fence` callbacks, RCU channel pointer use after channel teardown, missed uevent blocking/unblocking, sequence wrap comparisons, and deadlock/performance regressions in `nouveau_fence_sync()`. Test signals include cross-channel BO sharing, external reservation fences, interrupt-driven and polling fence completion, channel kill with error propagation, fence callbacks after channel free, timeout waits, and lockdep with reservation locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_fence.h

## Purpose
Declares Nouveau's fence objects, per-channel fence context, fence backend operations, common fence APIs, and hardware-generation fence constructor prototypes.

## Important APIs, Types, and Functions
`struct nouveau_fence` embeds a `dma_fence`, pending-list node, RCU channel pointer, and timeout. `struct nouveau_fence_chan` stores pending/flip lists, backend callbacks (`emit`, `sync`, `read`, `emit32`, `sync32`), sequence/context IDs, event work, NVIF event, and lifetime flags. `struct nouveau_fence_priv` describes the per-device fence backend with destructor, suspend/resume, context creation/destruction, and uevent capability. The header declares common fence operations and backend constructors for NV04, NV10, NV17, NV50, NV84, NVC0, and GV100 paths.

## Control Flow
Callers create or emit fences through the common APIs without knowing the backend generation. Channel initialization installs a `nouveau_fence_chan`, and acceleration setup selects the right backend based on channel class. Backend callbacks supply the hardware-specific sequence write/read/sync behavior.

## State and Persistence
The header defines persistent channel fence context and per-device fence backend state. NV84-specific extensions add a BO, suspend buffer, and mutex for fence storage.

## Dependencies and Integration Points
Depends on Linux `dma-fence` and NVIF events. It is included by the core driver header and therefore by GEM, EXEC, DMEM, channel, display, and BO code.

## Risks and Test Signals
Any structure layout or callback contract changes affect multiple GPU generations. Tests should cover backend selection, suspend/resume per fence generation, channel context allocation/free, fence wait/signal under interrupt and polling modes, and build coverage across old and new hardware support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_gem.c

## Purpose
Implements Nouveau GEM object lifetime, mmap fault handling, legacy GEM creation/info/CPU sync ioctls, legacy ABI16 pushbuf validation/relocation/submission, and per-client VMA open/close handling.

## Important APIs, Types, and Functions
Externally used functions include `nouveau_gem_new()`, `nouveau_gem_object_del()`, `nouveau_gem_object_open()`, `nouveau_gem_object_close()`, `nouveau_gem_ioctl_new()`, `nouveau_gem_ioctl_pushbuf()`, `nouveau_gem_ioctl_cpu_prep()`, `nouveau_gem_ioctl_cpu_fini()`, and `nouveau_gem_ioctl_info()`. Internal validation helpers include `validate_init()`, `validate_list()`, `validate_fini()`, `nouveau_gem_pushbuf_validate()`, and `nouveau_gem_pushbuf_reloc_apply()`. `nouveau_ttm_fault()` customizes TTM mmap faults.

## Control Flow
GEM creation disables UVMM if it has not been initialized, allocates a Nouveau BO, initializes the embedded GEM object, initializes TTM backing, applies valid-domain restrictions on Tesla+, creates a handle, and reports GEM info. Object open creates per-client VMAs for legacy VMM users; UVMM users bind explicitly and no eager VMA is created. Object close drops the VMA reference and either deletes it immediately or queues deletion after the VMA fence signals.

Legacy pushbuf ioctl rejects UVMM clients, finds an ABI16 channel, checks limits, copies push/BO/reloc arrays, validates every push buffer is in the BO list, reserves BOs with ww-acquire deadlock handling, chooses placement domains, validates/moves BOs, syncs against reservation fences, applies relocations if presumed offsets changed, emits push calls through GPFIFO/CALL/JUMP paths depending on hardware class, creates a Nouveau fence, optionally waits synchronously, attaches fences to BOs/VMAs, returns updated presumed offsets and next suffix values, and releases all reservations/references.

## State and Persistence
Persistent state lives in `struct nouveau_bo` and GEM object fields: valid domains, no-share flag, per-client VMA list, TTM resource, reservation object, tile/kind/compression metadata, relocation kmap state, and fence pointers on VMAs. Pushbuf validation uses transient `struct validate_op` state and per-BO indices while reserved.

## Dependencies and Integration Points
The file integrates DRM GEM, TTM BO/resource/mmap helpers, dma-resv, Nouveau BO/VMM/fence/channel/ABI16 helpers, NVIF GPFIFO push interfaces, and PRIME hooks through the GEM object function table.

## Risks and Test Signals
Risks are high in userspace ABI validation, reservation deadlock retry, relocation bounds, VMA lifetime after GPU use, UVMM versus legacy UAPI separation, and CPU/GPU synchronization. Test signals include legacy Mesa pushbuf workloads, invalid handles/counts/reloc offsets, no-share export/open denial, mmap page faults, CPU_PREP nowait/write behavior, BO eviction during validation, GPFIFO and pre-NV50 submission paths, and lockdep on reservation locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_gem.h

## Purpose
Declares Nouveau GEM APIs and PRIME hooks, and provides the conversion helper from `drm_gem_object` to the containing `nouveau_bo`.

## Important APIs, Types, and Functions
`nouveau_gem_object()` is the key inline container conversion. The header exposes `nouveau_gem_object_funcs`, object lifecycle functions, GEM ioctls, `nouveau_gem_new()`, and PRIME functions `nouveau_gem_prime_pin()`, `nouveau_gem_prime_unpin()`, `nouveau_gem_prime_get_sg_table()`, `nouveau_gem_prime_import_sg_table()`, and `nouveau_gem_prime_export()`.

## Control Flow
This header routes DRM GEM callbacks and ioctls to Nouveau implementations. The function table declared here is installed by GEM/PRIME allocation paths and later called by DRM core.

## State and Persistence
No state is stored in the header. It defines the interface to persistent BO/GEM state owned by `struct nouveau_bo`.

## Dependencies and Integration Points
Includes `nouveau_drv.h` and `nouveau_bo.h`, so it is part of the common object/memory interface consumed by DRM device setup, GEM implementation, PRIME import/export, and callers that need BO conversion.

## Risks and Test Signals
Risk is interface drift between GEM, BO, and PRIME implementations. Build and runtime tests should cover GEM object open/close/free callbacks, PRIME import/export, and ioctl registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_hwmon.c

## Purpose
Registers Nouveau with the Linux hwmon subsystem and exposes GPU temperature, fan, PWM, voltage, and power readings/controls when the corresponding NVKM subdevices support them.

## Important APIs, Types, and Functions
External lifecycle functions are `nouveau_hwmon_init()` and `nouveau_hwmon_fini()`. Visibility callbacks include `nouveau_chip_is_visible()`, `nouveau_temp_is_visible()`, `nouveau_fan_is_visible()`, `nouveau_input_is_visible()`, `nouveau_pwm_is_visible()`, and `nouveau_power_is_visible()`. Read/write callbacks include `nouveau_read()`, `nouveau_write()`, channel-specific read/write helpers, and `nouveau_read_string()`. Extra sysfs attributes cover fan PWM min/max and automatic fan boost threshold/hysteresis.

## Control Flow
Initialization checks for thermal, voltage, or iccsense subdevices. If none exist, it skips registration. If thermal attributes and fan control exist, it attaches additional legacy-style sysfs groups. It then registers `hwmon_device_register_with_info()` with `nouveau_chip_info`. The hwmon core calls visibility callbacks to expose only supported attributes, then read/write callbacks translate hwmon requests into NVKM therm/volt/iccsense operations. Runtime power-off state causes live sensor reads to return `-EINVAL` rather than waking or touching an off device.

## State and Persistence
Persistent state is a small `struct nouveau_hwmon` allocated on init and stored in `drm->hwmon`, containing the DRM device and registered hwmon device. Sensor values and thresholds persist in hardware/NVKM subdevices, not in this file.

## Dependencies and Integration Points
Depends on Linux hwmon, hwmon-sysfs, power supply includes, and NVKM `therm`, `volt`, and `iccsense` subdevices accessed through `nvxx_*` helpers. It is called from `nouveau_drm_device_init()` and `nouveau_drm_device_fini()`.

## Risks and Test Signals
Risks include exposing writable thresholds on hardware that cannot safely handle them, reading sensors while runtime suspended, unit conversions between degrees/millivolts/microwatts, and missing capability checks for partially implemented NVKM callbacks. Test signals include sysfs attribute presence by hardware capability, read/write threshold behavior, runtime-suspended reads, fan PWM mode/input writes, iccsense power limits, hwmon unregister on module unload, and builds without `CONFIG_HWMON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_hwmon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_hwmon.h

## Purpose
Declares the Nouveau hwmon wrapper object and lifecycle functions.

## Important APIs, Types, and Functions
`struct nouveau_hwmon` stores the owning DRM device and the registered hwmon device. `nouveau_hwmon()` returns `nouveau_drm(dev)->hwmon`. The header declares `nouveau_hwmon_init()` and `nouveau_hwmon_fini()`.

## Control Flow
The header provides a simple accessor used by teardown and any code needing the registered hwmon wrapper. Lifecycle control is implemented in `nouveau_hwmon.c` and invoked by the DRM device init/fini sequence.

## State and Persistence
The only defined state is the heap-allocated wrapper stored on the persistent `struct nouveau_drm`. It exists from successful hwmon registration until device teardown.

## Dependencies and Integration Points
Relies on `nouveau_drm()` from the main driver header and on Linux device types. It is included by `nouveau_drm.c` and `nouveau_hwmon.c`.

## Risks and Test Signals
Risks are low and mostly around null handling when hwmon support is disabled or registration skipped. Test signals include init/fini on devices without therm/volt/iccsense and builds with hwmon compiled in, modular, and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ioc32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ioc32.c

## Purpose
Provides 32-bit compatibility ioctl handling for Nouveau on 64-bit kernels. Current Nouveau-specific compat translation is effectively disabled, so most driver ioctls are delegated to the normal Nouveau ioctl path.

## Important APIs, Types, and Functions
The single external function is `nouveau_compat_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)`. It uses `DRM_IOCTL_NR()`, `drm_compat_ioctl()`, and `nouveau_drm_ioctl()`.

## Control Flow
If the ioctl number is below `DRM_COMMAND_BASE`, the call is handled by generic DRM compat ioctl support. For driver-private ioctls, the placeholder table lookup is compiled out with `#if 0`; since `fn` remains `NULL`, the handler calls `nouveau_drm_ioctl()` directly. This means compatibility depends on the normal ioctl handlers accepting the same pointer-sized layout or using DRM core-compatible structures.

## State and Persistence
The file owns no persistent state.

## Dependencies and Integration Points
It depends on Linux compat support, DRM ioctl helpers, and the declarations in `nouveau_ioctl.h`. `nouveau_drm.c` installs it as `.compat_ioctl` when `CONFIG_COMPAT` is enabled.

## Risks and Test Signals
The comment still references MGA, indicating copied legacy scaffolding. The practical risk is 32-bit userspace ABI mismatch for private ioctl structures that contain pointers or differently sized fields. Test signals include 32-bit userspace exercising GEM, ABI16, SVM, VM_BIND, and EXEC ioctls on a 64-bit kernel, plus generic DRM ioctls through the compat path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ioc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ioctl.h

## Purpose
Declares Nouveau's normal and compat file ioctl entry points.

## Important APIs, Types, and Functions
The header declares `nouveau_compat_ioctl()` and `nouveau_drm_ioctl()`.

## Control Flow
No runtime control flow is implemented. `nouveau_drm.c` uses these declarations for file operations, and `nouveau_ioc32.c` calls back into the normal handler when no compat-specific translator is present.

## State and Persistence
No state is defined.

## Dependencies and Integration Points
It provides the small interface between file operations in `nouveau_drm.c` and compat ioctl handling in `nouveau_ioc32.c`.

## Risks and Test Signals
Risk is low, but prototype changes must stay synchronized with DRM file operation signatures. Test signals are compile coverage with and without `CONFIG_COMPAT` and basic ioctl dispatch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_led.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_led.c

## Purpose
Registers and controls the NVIDIA logo LED through the Linux LED class when a matching BIOS GPIO function exists. Brightness is implemented by programming a display SOR PWM divider and duty register.

## Important APIs, Types, and Functions
External lifecycle functions are `nouveau_led_init()`, `nouveau_led_suspend()`, `nouveau_led_resume()`, and `nouveau_led_fini()`. LED callbacks are `nouveau_led_get_brightness()` and `nouveau_led_set_brightness()`.

## Control Flow
Initialization checks for an NVKM GPIO subdevice, searches for `DCB_GPIO_LOGO_LED_PWM`, allocates `drm->led`, fills a `led_classdev` named `nvidia-logo`, and registers it. Brightness reads register `0x61c880` as divider and `0x61c884` as duty, scaling to `LED_FULL`. Brightness writes use a 27 MHz input clock and 100 Hz PWM frequency, compute divider/duty, and write the SOR PWM registers. Suspend/resume forward to LED class helpers; fini unregisters and frees the wrapper.

## State and Persistence
Persistent state is `struct nouveau_led` stored in `drm->led`, containing the DRM device and LED class device. Actual brightness state is in hardware PWM registers.

## Dependencies and Integration Points
Depends on Linux LED class support, NVKM GPIO discovery, and NVIF register access. Called from the DRM device init/fini and PM paths. The code assumes the logo LED is controlled by `PDISPLAY.SOR[1].PWM` and that Nouveau does not otherwise manage those registers.

## Risks and Test Signals
Risk comes from direct magic register access, hardware assumptions about the PWM controller, runtime PM interactions during sysfs brightness access, and absence of locking around register updates. Test signals include devices with and without logo LED GPIO, LED sysfs brightness read/write, suspend/resume preserving sane state, module unload, and GSP/non-GSP register access behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_led.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_led.h

## Purpose
Declares Nouveau LED support and provides no-op stubs when the LED class is not reachable.

## Important APIs, Types, and Functions
`struct nouveau_led` stores the owning DRM device and `struct led_classdev`. `nouveau_led()` returns the per-device LED pointer. The header exposes `nouveau_led_init()`, `nouveau_led_suspend()`, `nouveau_led_resume()`, and `nouveau_led_fini()` when `CONFIG_LEDS_CLASS` is reachable, otherwise inline stubs return success or do nothing.

## Control Flow
The conditional declarations let `nouveau_drm.c` call LED lifecycle hooks unconditionally. Compile-time configuration determines whether those calls perform real LED registration/control or no-op.

## State and Persistence
The header defines the wrapper state that persists in `drm->led` only when LED support is active and hardware registration succeeds.

## Dependencies and Integration Points
Includes the main Nouveau driver header and Linux LED class definitions. Integrated from DRM device init/fini and PM suspend/resume.

## Risks and Test Signals
Risks are low but include configuration-dependent build coverage and accidental dereference of `drm->led` when stubs are active. Test signals include builds with LED class built-in, modular, and disabled; device init/fini on hardware without a logo LED; and PM paths with no registered LED.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_mem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_mem.c

## Purpose
Implements Nouveau's wrapper around TTM resource allocations and NVIF memory objects. It constructs VRAM or host memory objects, maps them into NVIF VMMs with generation-specific arguments, and provides TTM placement range compatibility helpers.

## Important APIs, Types, and Functions
External functions are `nouveau_mem_new()`, `nouveau_mem_del()`, `nouveau_mem_fini()`, `nouveau_mem_vram()`, `nouveau_mem_host()`, `nouveau_mem_map()`, `nouveau_mem_intersects()`, and `nouveau_mem_compatible()`. The implementation uses `struct nouveau_mem`, which embeds `struct ttm_resource` and owns an `nvif_mem` plus two `nvif_vma` slots.

## Control Flow
`nouveau_mem_new()` allocates and initializes the wrapper. `nouveau_mem_vram()` creates an NVIF VRAM memory object using GF100 or NV50 argument formats, respecting contiguity, page size, bankswizzle, and `drm->ttm.type_vram`, then stores the resource start from the NVIF memory address. `nouveau_mem_host()` chooses coherent or non-coherent host memory type based on MMU capabilities and `nouveau_drm_use_coherent_gpu_mapping()`, drops kind/compression if unsupported, and constructs an NVIF RAM object from an sg list or DMA address array. `nouveau_mem_map()` selects VMM map argument formats for NV50 and GF100+ VMM classes and maps the NVIF memory into a VMA. `nouveau_mem_del()` tears the NVIF state down, finalizes the TTM resource, and frees the wrapper.

## State and Persistence
Persistent state is one `struct nouveau_mem` per TTM resource. It stores kind/compression metadata, NVIF memory object, VMA slots used by the BO/VMM code, and a pointer back to the DRM device. The underlying memory is owned by NVIF/NVKM and TTM.

## Dependencies and Integration Points
Depends on DRM TTM resources/TTM TT, NVIF MMU/MEM/VMM classes, and Nouveau BO/DRM helpers. It is used by BO allocation, TTM memory managers, and VMM mapping paths.

## Risks and Test Signals
Risks include wrong memory type selection for coherent versus non-coherent mappings, unsupported compression/kind handling, page-size alignment errors, VMM class argument mismatch, and resource-range eviction checks. Test signals include VRAM and GART BO allocation, imported sg-table BOs, compressed/tiled formats, coherent mapping behavior on affected platforms, eviction placement constraints, and suspend/unload teardown of mapped resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_mem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_mem.h

## Purpose
Declares the Nouveau TTM resource/NVIF memory wrapper and memory management helpers.

## Important APIs, Types, and Functions
`struct nouveau_mem` embeds `struct ttm_resource`, stores a `nouveau_drm` pointer, kind/compression bytes, `struct nvif_mem`, and two `struct nvif_vma` slots. `nouveau_mem()` converts a TTM resource to the wrapper. The header declares allocation, deletion, placement range, VRAM/host construction, fini, and map functions, plus `nouveau_mem_map_fixed()`.

## Control Flow
The header provides the common interface used by BO and TTM managers to allocate a resource wrapper first, then initialize it as VRAM or host memory, map it into a VMM, and finally tear it down.

## State and Persistence
The defined wrapper persists for the lifetime of a TTM resource. VMA slots are used by mapping code and must be released by `nouveau_mem_fini()`.

## Dependencies and Integration Points
Depends on TTM BO/resource headers and NVIF memory/VMM headers. It is included by BO, GEM, DMEM, and memory-manager implementation code.

## Risks and Test Signals
Risks include callers forgetting to finalize NVIF VMAs/memory, stale declarations such as `nouveau_mem_map_fixed()` needing implementation elsewhere, and incorrect container conversions. Test signals include build/link coverage, BO allocation/free under memory pressure, and VMM map/unmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_nvif.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_nvif.c

## Purpose
Provides the NVIF driver backend that directly links the DRM driver to NVKM in-kernel services. It adapts NVIF client operations to NVKM client, object, event, ioctl, and BAR mapping functions.

## Important APIs, Types, and Functions
The exported object is `const struct nvif_driver nvif_driver_nvkm`. Its callbacks are implemented by `nvkm_client_driver_init()`, `nvkm_client_suspend()`, `nvkm_client_resume()`, `nvkm_client_ioctl()`, `nvkm_client_map()`, and `nvkm_client_unmap()`. `nvkm_client_event()` bridges NVKM event delivery into `struct nvif_event` callbacks.

## Control Flow
NVIF initialization calls `nvkm_client_driver_init()`, which creates an NVKM client and installs the event bridge. NVIF ioctls call `nvkm_ioctl()`. NVIF map/unmap operations use `ioremap()` and `iounmap()`. Suspend/resume finish or initialize the root NVKM object with runtime versus system suspend state. Events reinterpret the token as an NVIF object, recover the containing event, call its function, and translate keep/drop return values.

## State and Persistence
State is mostly owned by NVKM clients and NVIF objects. This file stores no mutable global state beyond the constant driver descriptor.

## Dependencies and Integration Points
Depends on NVKM core client/ioctl/object APIs and NVIF client/driver/event/ioctl definitions. `nouveau_drm.c` initializes the DRM NVIF client through this backend.

## Risks and Test Signals
Risks include pointer-token assumptions in event delivery, direct kernel virtual mapping lifetime, and suspend state mismatch between runtime and system PM. Test signals include NVIF ioctl coverage, event delivery and drop/keep behavior, runtime PM suspend/resume, module unload with active events, and error paths during client creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_nvif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_platform.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_platform.c

## Purpose
Implements Nouveau platform-driver support for Tegra GPUs such as GK20A, GM20B, and GP10B. It binds device-tree compatible strings to Tegra NVKM device configuration and delegates DRM device creation/removal to the core driver.

## Important APIs, Types, and Functions
The platform driver object is `nouveau_platform_driver`. Internal functions are `nouveau_platform_probe()`, `nouveau_platform_remove()`, and PM sleep callbacks `nouveau_platform_suspend()`/`nouveau_platform_resume()` when enabled. Static platform data describes IOMMU address width and power/clock requirements for GK20A, GM20B, and GP10B.

## Control Flow
Probe obtains `nvkm_device_tegra_func` match data from OF, calls `nouveau_platform_device_create()`, and returns `PTR_ERR_OR_ZERO()`. Remove retrieves the stored `nouveau_drm` pointer and calls `nouveau_drm_device_remove()`. PM sleep callbacks delegate to GK20A devfreq suspend/resume. The OF match table registers compatible strings and data.

## State and Persistence
Persistent platform state is stored in the DRM/NVKM device created by the core path and in static match-data structs. The file itself owns no dynamic allocations beyond what the core creation path performs.

## Dependencies and Integration Points
Depends on platform bus/OF matching, NVKM Tegra device functions, GK20A devfreq helpers, and the core platform device creation/removal APIs declared in `nouveau_drv.h`. Registered from module init when `CONFIG_NOUVEAU_PLATFORM_DRIVER` is enabled.

## Risks and Test Signals
Risks include missing or incorrect OF match data, PM domain/regulator/clock requirement mismatches, removal assumptions about driver data, and devfreq-only PM handling diverging from PCI PM. Test signals include boot/probe on supported Tegra compatibles, deferred probe for resources, suspend/resume with devfreq, remove/unbind, and builds with OF or platform driver disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_platform.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_platform.h

## Purpose
Declares the Nouveau platform driver for optional Tegra platform-device registration.

## Important APIs, Types, and Functions
The only declaration is `extern struct platform_driver nouveau_platform_driver`.

## Control Flow
No runtime logic is implemented. `nouveau_drm.c` registers and unregisters this driver during module init/exit when platform support is configured.

## State and Persistence
No state is owned by the header.

## Dependencies and Integration Points
Includes `nouveau_drv.h` so the platform driver declaration shares the common Nouveau device definitions. It is included by platform implementation and core DRM module code.

## Risks and Test Signals
Risk is limited to build configuration and symbol visibility. Test signals include compile coverage with `CONFIG_NOUVEAU_PLATFORM_DRIVER` enabled/disabled and platform probe registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_prime.c

## Purpose
Implements PRIME/dma-buf import and export helpers for Nouveau GEM objects, allowing buffer sharing with other DRM devices while enforcing Nouveau placement and no-share policy.

## Important APIs, Types, and Functions
External functions are `nouveau_gem_prime_get_sg_table()`, `nouveau_gem_prime_import_sg_table()`, `nouveau_gem_prime_pin()`, `nouveau_gem_prime_unpin()`, and `nouveau_gem_prime_export()`.

## Control Flow
Export sg-table creation converts the TTM page array to an sg table with `drm_prime_pages_to_sg()`. Import locks the dma-buf reservation object, allocates a Nouveau BO in GART domain using the supplied sg table and shared reservation object, initializes the embedded GEM object, initializes BO/TTM state, and returns the GEM object. PRIME pin pins the BO in GART; unpin releases it. Export rejects `nvbo->no_share`, prepares the BO for export with a non-blocking TTM operation context, then delegates to `drm_gem_prime_export()`.

## State and Persistence
Imported objects persist as Nouveau BO/GEM objects backed by the dma-buf reservation object and sg table. Export does not create new persistent Nouveau state beyond dma-buf bookkeeping in DRM/TTM core.

## Dependencies and Integration Points
Depends on Linux dma-buf, DRM PRIME helpers, TTM TT pages, Nouveau BO/GEM allocation, and the GEM object function table installed in `nouveau_gem.c`. Registered through the DRM driver and GEM object funcs.

## Risks and Test Signals
Risks include exporting private no-share BOs, pinning failures mapped to `-EINVAL`, reservation locking/lifetime with imported dma-bufs, and assumptions that TTM pages exist for sg export. Test signals include PRIME import/export with another DRM driver, no-share export denial, GART pin/unpin under eviction pressure, mmap/rendering of imported BOs, and dma-buf lifetime after file close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_prime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_reg.h

## Purpose
Defines legacy Nouveau hardware register offsets, bit masks, object classes, FIFO commands, display registers, AUX channel registers, framebuffer registers, graph registers, timer registers, and NV50-era register-block descriptions used by low-level display, FIFO, memory, and legacy acceleration code.

## Important APIs, Types, and Functions
This header is entirely preprocessor definitions. Major groups include NV04/NV10/NV40 framebuffer boot/tile/Z compression registers, RAMHT context fields, DMA object class IDs, USER channel register layouts, PMC interrupt/enable registers, PBUS/PCI/ROM fields, PTIMER registers, PGRAPH interrupt/context/clip/format registers, FIFO DMA command encodings, NV50 PMC/PCONNECTOR/AUX/PBUS/PFB/PDISPLAY blocks, CRTC/DAC/SOR/display-user register definitions, SOR PWM definitions, DP control bits, and cursor user registers.

## Control Flow
The header implements no control flow. It provides symbolic constants that low-level code uses for direct `nvif_rd32()`/`nvif_wr32()`/MMIO programming and bitfield interpretation.

## State and Persistence
No software state is stored. The definitions correspond to persistent hardware register state and command encodings in NVIDIA GPUs.

## Dependencies and Integration Points
It is a low-level integration point for legacy register programming paths throughout the Nouveau driver, especially display, FIFO/channel, memory/tile, graph, timer, AUX, backlight, and LED/PWM code. Some definitions overlap with rules-ng imports and are documented as partial and potentially duplicated.

## Risks and Test Signals
Risks include stale or duplicated register definitions, incorrect bit masks across GPU generations, direct register access that bypasses NVIF/GSP abstractions, and accidental use of legacy definitions on unsupported hardware. Test signals are hardware-generation smoke tests, display hotplug/AUX/backlight/PWM behavior, legacy FIFO and graph init, suspend/resume register restore, and static checks for duplicate/conflicting defines when importing newer rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_reg.h -->
