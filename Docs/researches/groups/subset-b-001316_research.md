# subset-b-001316 research

Grouped research for AMDGPU driver, GEM, fence, GART, EEPROM, FRU, fdinfo, encoder, and firmware-attestation support files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_drv.c

## Purpose
`amdgpu_drv.c` is the AMDGPU DRM PCI driver entry point. It defines the KMS UAPI version, global module parameters, supported PCI IDs, the DRM driver and file-operation tables, PCI probe/remove/shutdown handlers, power-management callbacks, AER hooks, ioctl dispatch, fd release/flush behavior, sysfs groups, and module init/exit wiring.

## Important APIs, types, and functions
Important exported or externally visible objects include `amdgpu_ioctls_kms[]`, `amdgpu_partition_driver`, `amdgpu_drm_ioctl()`, and `amdgpu_file_to_fpriv()`. Core lifecycle functions are `amdgpu_pci_probe()`, `amdgpu_pci_remove()`, `amdgpu_pci_shutdown()`, `amdgpu_init()`, and `amdgpu_exit()`. Power management is split across `amdgpu_pmops_prepare()`, `suspend()`, `resume()`, `freeze()`, `thaw()`, `poweroff()`, `restore()`, `runtime_suspend()`, `runtime_resume()`, and `runtime_idle()`. Support helpers include `amdgpu_support_enabled()`, `amdgpu_fix_asic_type()`, `amdgpu_init_debug_options()`, `amdgpu_runtime_idle_check_display()`, `amdgpu_runtime_idle_check_userq()`, `amdgpu_flush()`, and `amdgpu_drm_release()`.

## Control flow
Module load initializes sync support, registers ATPX/ACPI handling, initializes KFD if available, taints the kernel if OverDrive is enabled, and registers the PCI driver. Probe rejects unsupported or experimental devices unless enabled, resolves SI/CIK ownership against radeon, applies ASIC quirks, rejects incompatible SME/Raven combinations, allocates `struct amdgpu_device` through DRM managed allocation, enables PCI, applies debug options, calls `amdgpu_driver_load_kms()`, registers the DRM device with retry on `-EAGAIN`, registers XCP and KFD clients, starts fbdev/client setup when display connectors exist, creates debugfs entries, and enables runtime PM when supported.

Remove runs RAS EEPROM recovery checks, unplug paths, NPS preparation, DRM unplug, runtime PM shutdown, KMS unload, PCI disable, and pending-transaction wait. IOCTLs wrap `drm_ioctl()` in runtime-PM get/put. File release shuts down per-file eviction fences and user queues before `drm_release()`. Runtime suspend refuses to proceed with active displays, active user queues, or undrained rings, then chooses PX, BOCO, BACO, or BAMACO handling. Resume restores PCI state or exits BACO and resumes the device.

## State and persistence behavior
The file owns module parameter globals for memory sizing, VM behavior, scheduling, power, display, RAS, recovery, firmware loading, user queues, and debug modes. Persistent device state is not stored on disk here; state lives in `struct amdgpu_device`, DRM file private data, runtime-PM flags, PCI power state, sysfs/debugfs registrations, and per-module globals. The KMS UAPI version is a compatibility contract exposed to userspace.

## Dependencies and integration points
This file integrates DRM core, DRM GEM, syncobj timelines, fbdev/client setup, PCI, runtime PM, ACPI/ATPX, VGA switcheroo, KFD, XCP partitions, RAS, reset/AER recovery, user queues, fdinfo, GEM, CS, VM, scheduler, BO-list, and sysfs memory-manager attribute groups. It is the central registration point for the ioctl handlers implemented across the AMDGPU driver.

## Risks and edge cases
Probe has many early exits where PCI enablement, DRM registration, KFD/XCP setup, and runtime PM state must unwind correctly. SI/CIK support depends on build options and module parameter precedence with radeon. Runtime PM can race displays, user queues, ring fences, or hot-unplug. Suspend paths must distinguish S0ix, S3, S4, BOCO, PX, BACO, and passthrough. `amdgpu_drm_ioctl()` must always release runtime PM references after errors. Release ordering for user queues and eviction fences is important because user queue resume work can otherwise outlive the file.

## Test signals
Useful signals include PCI probe/remove on supported and unsupported ASICs, SI/CIK ownership parameter tests, DRM minor registration and ioctl availability, render-node ioctl runtime-PM accounting, suspend/resume across S0ix/S3/S4/runtime modes, hot-unplug, AER recovery, user-queue-open release, active-display runtime-idle refusal, active-ring drain refusal, sysfs group creation, debugfs creation, KFD/XCP registration failures, and module unload with `mmu_notifier_synchronize()` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_drv.h

## Purpose
`amdgpu_drv.h` is the small private driver header that exposes common AMDGPU DRM driver identity constants and ioctl entry points to files that need the driver-level declarations.

## Important APIs, types, and functions
It defines `DRIVER_AUTHOR`, `DRIVER_NAME`, and `DRIVER_DESC`, declares `extern const struct drm_driver amdgpu_partition_driver`, and declares `amdgpu_drm_ioctl()` plus the compat ioctl wrapper `amdgpu_kms_compat_ioctl()`.

## Control flow
The header has no executable control flow. It is consumed by `amdgpu_drv.c` and other driver files that need the canonical DRM driver name, description, or ioctl signatures.

## State and persistence behavior
No runtime state is allocated here. The macros become compile-time constants embedded in the DRM driver objects and module metadata.

## Dependencies and integration points
It includes Linux firmware/platform-device headers and `amd_shared.h`. The `amdgpu_partition_driver` declaration connects partition DRM devices with the primary driver definition in `amdgpu_drv.c`.

## Risks and edge cases
Changing driver identity strings affects module metadata and userspace-facing DRM naming. Prototype drift from `amdgpu_drv.c` or compat code would break builds. Because the partition driver is declared here, any partition-driver feature changes must stay synchronized with the definition in the C file.

## Test signals
Build coverage is the main signal. Runtime confirmation comes from DRM device names, module metadata, compat ioctl builds, and XCP partition device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eeprom.c

## Purpose
`amdgpu_eeprom.c` provides common I2C EEPROM read/write helpers for AMDGPU components such as FRU and RAS EEPROM users. It handles 19-bit EEPROM addressing, two-byte memory offsets, page-limited writes, adapter quirk limits, and read/write transfer chunking.

## Important APIs, types, and functions
Public entry points are `amdgpu_eeprom_read()` and `amdgpu_eeprom_write()`. Internal helpers are `amdgpu_eeprom_xfer()` and `__amdgpu_eeprom_xfer()`. Constants define 256-byte EEPROM write pages, two-byte offsets, and `MAKE_I2C_ADDR()` for mapping high address bits into the I2C EEPROM device address.

## Control flow
Callers pass an I2C adapter, EEPROM memory address, buffer, and byte count. `amdgpu_eeprom_xfer()` checks `i2c_adapter_quirks`; without quirks it delegates directly, otherwise it subtracts offset bytes from the adapter transfer limit and splits the operation into partial chunks. `__amdgpu_eeprom_xfer()` loops until all data is moved, fills an address-message plus data-message pair, caps writes so they do not cross a 256-byte page boundary, caps reads to `U16_MAX`, calls `i2c_transfer()`, and sleeps 10 ms after writes to allow the EEPROM self-timed write cycle.

## State and persistence behavior
The helper has no long-lived kernel state. Writes persist in the external EEPROM device. The only temporary state is stack I2C message setup and caller-provided buffers.

## Dependencies and integration points
It depends on Linux I2C adapter APIs, adapter quirk metadata, `msleep()`, AMDGPU device logging indirectly through callers, and `str_read_write()` from included AMDGPU headers. `amdgpu_fru_eeprom.c` and other EEPROM consumers rely on this file for consistent address and page handling.

## Risks and edge cases
The function returns a byte count for partial progress when `i2c_transfer()` returns a non-negative short result, so callers must check exact lengths. Adapter limits less than or equal to the two-byte offset are rejected. Write behavior depends on the fixed 10 ms delay rather than acknowledge polling. Address encoding must match 2-Mbit EEPROM wiring; wrong high address bits target the wrong chip or region. Page-boundary handling is critical because EEPROM page writes can wrap within the page.

## Test signals
Test signals include full and partial reads, page-boundary writes, adapter quirk-limited transfers, exact-length checks by FRU/RAS callers, invalid quirk limits returning `-EINVAL`, I2C transfer error propagation, and persistence verification across rereads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eeprom.h

## Purpose
`amdgpu_eeprom.h` declares the common AMDGPU I2C EEPROM access API.

## Important APIs, types, and functions
It includes `<linux/i2c.h>` and declares `amdgpu_eeprom_read()` and `amdgpu_eeprom_write()`, each taking an `i2c_adapter`, 32-bit EEPROM address, byte buffer, and transfer length.

## Control flow
The header has no executable control flow. Callers use the declared helpers to route EEPROM access through the common transfer implementation.

## State and persistence behavior
No state is defined here. Persistence behavior is provided by the backing EEPROM device and the implementation in `amdgpu_eeprom.c`.

## Dependencies and integration points
It is the contract between EEPROM consumers, including FRU support, and the low-level I2C transfer helper.

## Risks and edge cases
The API accepts mutable `u8 *` for writes as well as reads, so callers must pass correctly sized buffers and check exact byte counts. Address interpretation is implementation-specific and not self-describing in the prototype.

## Test signals
Build coverage plus successful FRU/RAS EEPROM reads and writes through consumers validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_encoders.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_encoders.c

## Purpose
`amdgpu_encoders.c` contains legacy/non-DC display encoder helper logic. It links connectors to compatible encoders, tracks the active connector device mask, finds related connectors and external DP bridge encoders, adjusts panel modes to native timing, and decides when digital outputs need dual-link DVI/HDMI-style behavior.

## Important APIs, types, and functions
Important functions are `amdgpu_link_encoder_connector()`, `amdgpu_encoder_set_active_device()`, `amdgpu_get_connector_for_encoder()`, `amdgpu_get_connector_for_encoder_init()`, `amdgpu_get_external_encoder()`, `amdgpu_encoder_get_dp_bridge_encoder_id()`, `amdgpu_panel_mode_fixup()`, and `amdgpu_dig_monitor_is_duallink()`.

## Control flow
Connector/encoder setup walks DRM connector and encoder lists, compares AMDGPU ATOM device bitmasks, attaches compatible encoders, and initializes LCD backlight state for LCD-capable encoders. Active-device selection scans connectors for the current encoder and stores the intersection of encoder and connector device masks. Lookup helpers either use the active device mask or the initialization-time possible device mask. External encoder discovery scans for another encoder marked `is_ext_encoder` with overlapping device masks, and bridge ID reporting only exposes known Travis/Nutmeg bridge IDs. Panel fixup copies native mode timings while preserving blanking/sync offsets. Dual-link detection switches on connector type, HDMI information, DP sink type, and pixel-clock thresholds.

## State and persistence behavior
The file updates runtime DRM mode objects and AMDGPU encoder fields such as `active_device`, `native_mode`, and `adev->mode_info.bl_encoder`. It does not persist state outside the kernel mode configuration.

## Dependencies and integration points
It depends on DRM connector/encoder iteration, AMDGPU connector and encoder private structures, ATOM device masks, ATOM bridge encoder IDs, backlight initialization, and display mode helpers. It integrates with legacy KMS display bring-up paths rather than the newer DC-specific helpers.

## Risks and edge cases
Connector lookup assumes a connector is found before dereferencing in `amdgpu_dig_monitor_is_duallink()`. Device-mask mismatches can attach wrong encoders or miss valid ones. Pixel-clock thresholds encode single-link HDMI/DVI limits and must stay aligned with connector semantics. External bridge detection is limited to known encoder IDs. Mode fixup assumes the native panel mode is valid and initialized.

## Test signals
Signals include connector-to-encoder attachments, backlight setup for LCD/eDP panels, active-device changes during modesets, DP bridge ID detection, native panel mode timing in adjusted modes, single-link versus dual-link decisions across DVI/HDMI/DP connectors, and hotplug/modeset testing on legacy display hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_encoders.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eviction_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eviction_fence.c

## Purpose
`amdgpu_eviction_fence.c` implements per-file eviction fences used to coordinate user-queue eviction and resume with BO reservation objects. When a BO is associated with an unsignaled eviction fence, consumers waiting on that BO trigger user queue suspension before memory eviction or validation proceeds.

## Important APIs, types, and functions
Public manager operations are `amdgpu_evf_mgr_init()`, `amdgpu_evf_mgr_rearm()`, `amdgpu_evf_mgr_attach_fence()`, `amdgpu_evf_mgr_detach_fence()`, `amdgpu_evf_mgr_shutdown()`, `amdgpu_evf_mgr_flush_suspend()`, and `amdgpu_evf_mgr_fini()`. Internal dma-fence operations include driver/timeline naming and `amdgpu_eviction_fence_enable_signaling()`, which schedules the suspension worker. The worker is `amdgpu_eviction_fence_suspend_worker()`.

## Control flow
Manager initialization allocates a dma-fence context, starts with a stub fence, and initializes suspension work. Rearming allocates a new `amdgpu_eviction_fence`, initializes it with a per-manager sequence number and current task name, replaces the manager's current fence, and attaches it to every already locked GEM object in the supplied `drm_exec`. Attaching a BO validates it to allowed domains and adds the current unsignaled fence to its reservation object as a bookkeeping fence. Fence signaling is enabled by scheduling suspend work. The worker locks the file's user queue manager, begins a dma-fence signaling section, gets the current eviction fence, evicts user queues, signals the fence while still holding `userq_mutex`, drops the fence, optionally schedules resume work, and unlocks.

## State and persistence behavior
State lives in `struct amdgpu_eviction_fence_mgr`: fence context, atomic sequence, RCU-protected current fence, work item, and shutdown flag. Individual eviction fences hold a dma-fence, spinlock, task-derived timeline name, and backpointer to the manager. There is no durable persistence; fences are synchronization state for one DRM file lifetime.

## Dependencies and integration points
The file depends on dma-fence, dma-resv, TTM validation, DRM exec locked-object iteration, AMDGPU BO placement, and `amdgpu_userq_evict()` / user queue resume work. It is called from GEM open/close and file release paths.

## Risks and edge cases
Ordering is delicate: signaling must occur while holding `userq_mutex` so queues are not resumed before the next fence is installed. RCU access to `ev_fence` must always take references safely. Shutdown must flush work after making the flag visible. `amdgpu_evf_mgr_attach_fence()` can validate BO placement while handling eviction synchronization, so error propagation matters. Replacement with a stub fence on detach depends on the unique fence context.

## Test signals
Signals include user-queue eviction on fence wait, automatic resume scheduling after eviction, BO reservation bookkeeping fence insertion/removal, GEM open/close interactions, file release with pending work, shutdown flush behavior, and stress tests with concurrent VM BO operations and user queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eviction_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eviction_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eviction_fence.h

## Purpose
`amdgpu_eviction_fence.h` defines the data structures and API for AMDGPU per-file eviction fence management.

## Important APIs, types, and functions
The key types are `struct amdgpu_eviction_fence`, embedding `struct dma_fence`, and `struct amdgpu_eviction_fence_mgr`, holding the current RCU-protected eviction fence, fence context/sequence, suspend work, and shutdown flag. The inline `amdgpu_evf_mgr_get_fence()` safely references the current fence under RCU. Prototypes cover attach, rearm, detach, init, shutdown, suspend flush, and fini.

## Control flow
The header encodes the lifecycle: initialize a manager for a file, rearm fences while VM BOs are locked, attach/detach BO reservation fences during GEM open/close, flush or shut down work during release, and drop the final fence reference at fini.

## State and persistence behavior
All state is runtime synchronization state scoped to a DRM file private object. The comments document the lock contract: current fence updates happen under the VM reservation lock, and signaling happens under the user queue mutex.

## Dependencies and integration points
It depends on Linux dma-fence, RCU-safe fence reference helpers, AMDGPU BO types, and DRM exec through the C implementation. It connects GEM/VM code with user-queue eviction.

## Risks and edge cases
Misusing the inline without checking for `NULL` would be unsafe, though the manager initializes with a stub fence. Lock-order violations between VM reservation locks and `userq_mutex` can create races or deadlocks. The RCU pointer must not be replaced or signaled outside the documented locking model.

## Test signals
Build coverage, lockdep under VM/user-queue stress, BO reservation fence replacement, file close/release ordering, and user queue eviction/resume tests validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eviction_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fdinfo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fdinfo.c

## Purpose
`amdgpu_fdinfo.c` implements AMDGPU's `/proc/<pid>/fdinfo` reporting. It prints PASID, DRM memory accounting by placement, legacy amdgpu memory aliases, AMD-specific requested/evicted memory counters, and per-engine runtime usage.

## Important APIs, types, and functions
The main function is `amdgpu_show_fdinfo()`. It uses the `amdgpu_ip_name[]` table to translate hardware IP indices to fdinfo engine names and relies on `amdgpu_vm_get_memory()` plus `amdgpu_ctx_mgr_usage()` for accounting.

## Control flow
When DRM core invokes the driver's `show_fdinfo` hook, the function retrieves `struct amdgpu_fpriv`, obtains the VM and context manager, fills memory stats for all AMDGPU placements, fills per-IP usage times, prints the PASID, emits generic DRM memory stats for named placements, prints legacy `drm-memory-vram/gtt/cpu` aliases, prints AMD-specific requested and evicted memory keys, and prints each nonzero engine usage counter.

## State and persistence behavior
No state is persisted or mutated here. The output is a point-in-time view of per-file VM memory accounting and context runtime usage. Values are derived from in-memory VM BO and context-manager state.

## Dependencies and integration points
It depends on DRM fdinfo printer APIs, DRM usage-stats format, AMDGPU VM accounting, AMDGPU context manager usage accounting, placement indices, and hardware IP constants. The hook is installed by the `amdgpu_kms_driver` in `amdgpu_drv.c`.

## Risks and edge cases
The output format is userspace-facing and should stay compatible with `drm-usage-stats.rst`. IP names are shared for some decode/encode variants, so aggregation interpretation matters. Placement arrays must stay synchronized with AMDGPU placement enum values. Statistics may be approximate under concurrent memory or context changes.

## Test signals
Signals include fdinfo reads for graphics and compute clients, PASID presence, correct placement names, nonzero engine counters after workload submission, memory resident/shared/private/purgeable accounting, legacy alias values matching generic counters, and format compatibility with DRM usage parsers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fdinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fdinfo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fdinfo.h

## Purpose
`amdgpu_fdinfo.h` declares AMDGPU fdinfo support and related helper prototypes.

## Important APIs, types, and functions
It declares `amdgpu_show_fdinfo()` and `amdgpu_get_ip_count()`. The includes pull in DRM file, scheduler, sync, ring, ID, IDR, kfifo, rbtree, and task memory types used by fdinfo-adjacent accounting code.

## Control flow
The header has no executable control flow. Its declarations allow the DRM driver table to point at `amdgpu_show_fdinfo()` and allow related code to query IP counts.

## State and persistence behavior
No state is defined here. Runtime state is owned by file private data, VM, context managers, and device IP metadata.

## Dependencies and integration points
It is included by `amdgpu_drv.c` and `amdgpu_fdinfo.c`, connecting DRM core fdinfo callbacks to AMDGPU accounting implementation.

## Risks and edge cases
The include guard name still says `__AMDGPU_SMI_H__`, which is harmless for builds but confusing for maintenance. Prototype drift would break fdinfo registration or IP-count callers.

## Test signals
Build coverage and successful `/proc/<pid>/fdinfo` reporting validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fdinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c

## Purpose
`amdgpu_fence.c` implements AMDGPU ring fence tracking, signaling, fallback polling, interrupt enable/disable, cleanup, debugfs reporting, and queue-reset reemit support. It bridges GPU-written fence memory with Linux `dma_fence` objects used by schedulers, BO reservations, VM updates, and userspace sync.

## Important APIs, types, and functions
Key fence APIs include `amdgpu_fence_emit()`, `amdgpu_fence_emit_polling()`, `amdgpu_fence_process()`, `amdgpu_fence_wait_empty()`, `amdgpu_fence_wait_polling()`, `amdgpu_fence_count_emitted()`, `amdgpu_fence_last_unsignaled_time_us()`, `amdgpu_fence_update_start_timestamp()`, `amdgpu_fence_driver_init_ring()`, `amdgpu_fence_driver_start_ring()`, `amdgpu_fence_driver_hw_init()`, `amdgpu_fence_driver_hw_fini()`, `amdgpu_fence_driver_sw_fini()`, `amdgpu_fence_driver_set_error()`, and `amdgpu_fence_driver_force_completion()`. Queue reset helpers are `amdgpu_ring_backup_unprocessed_commands()` and `amdgpu_ring_set_fence_errors_and_reemit()`.

## Control flow
Ring initialization allocates a power-of-two fence slot array sized to twice `num_hw_submission`, initializes locks and fallback timer, and later `amdgpu_fence_driver_start_ring()` points the fence driver at the ring's fence memory or UVD firmware-adjacent memory. Emitting a fence increments `sync_seq`, initializes a `dma_fence`, writes a hardware fence packet, takes a runtime-PM reference, waits for an old fence in the same wrapped slot if necessary, stamps start time, and publishes the fence in the slot under RCU. Interrupt handlers or fallback timers call `amdgpu_fence_process()`, which reads the GPU fence value, updates `last_seq`, signals all newly completed fences, drops references, and releases runtime-PM usage.

## State and persistence behavior
Per-ring state is in `ring->fence_drv`: CPU/GPU fence addresses, last and emitted sequence numbers, fence array, fallback timer, spinlock, interrupt source/type, and initialization flag. Fence objects carry ring pointer, start timestamp, IB write-pointer metadata, backup indices, and dma-fence state. No state is durable across driver unload or GPU reset; recovery paths can mark pending fences with errors or force completion.

## Dependencies and integration points
The file depends on dma-fence, DRM scheduler teardown, runtime PM, AMDGPU ring emission, IRQ get/put, reset domains, UVD firmware layout, debugfs, and reset recovery. BO reservations, VM updates, command submission, and scheduler entities consume the produced fences.

## Risks and edge cases
Fence sequence wrapping requires waiting for old slot occupants before reuse. Missing interrupts rely on the fallback timer. Runtime-PM gets in emit must be balanced when fences signal or are forced. Hardware teardown cannot wait forever for unavailable GPU signaling and must set errors. Queue reset reemit must preserve innocent contexts while marking the guilty fence `-ETIME` and other fences from the same context `-ECANCELED`. S0ix interrupt restore skips GFX power-domain rings, so classification must be correct.

## Test signals
Signals include fence signal latency, fallback timer warnings, runtime-PM reference balance, fence wrap stress, ring drain on suspend/remove, forced completion after unplug/reset, debugfs fence counters, manual `amdgpu_gpu_recover`, polling fences, queue reset with guilty context cancellation and innocent command reemit, and scheduler shutdown without leaked fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fru_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fru_eeprom.c

## Purpose
`amdgpu_fru_eeprom.c` detects supported server GPUs with Field Replaceable Unit EEPROM data, reads IPMI FRU Product Info Area records through the common EEPROM helper, stores product identity fields in `adev->fru_info`, and exposes those fields through read-only sysfs files.

## Important APIs, types, and functions
Public functions are `amdgpu_fru_get_product_info()`, `amdgpu_fru_sysfs_init()`, and `amdgpu_fru_sysfs_fini()`. The detection helper is `is_fru_eeprom_supported()`. Sysfs show handlers export `product_name`, `product_number`, `serial_number`, `fru_id`, and `manufacturer`.

## Control flow
Detection rejects SR-IOV VFs and APUs, then switches on MP1 IP version, ASIC type, and VBIOS part-number substrings to decide whether FRU EEPROM is available and which EEPROM memory address to use. Product-info reading allocates `adev->fru_info` when needed, seeds the serial field from `adev->unique_id`, verifies the FRU I2C adapter exists, reads and validates the IPMI common header version and checksum, locates the Product Info Area, reads and validates its header and checksum, then walks type/length fields to copy manufacturer, product name, product number, serial, and optional FRU ID into bounded strings. Sysfs init creates attributes only for supported devices with populated FRU info.

## State and persistence behavior
The persistent source of truth is the external FRU EEPROM. Runtime state is copied into `struct amdgpu_fru_info` attached to `adev`. Sysfs attributes expose that cached runtime copy; the driver does not write FRU data in this file.

## Dependencies and integration points
It depends on PCI/device data, ATOM VBIOS context, PM FRU I2C adapter initialization, SMU I2C support, `amdgpu_eeprom_read()`, AMDGPU IP-version helpers, and sysfs device attributes. It integrates with device initialization and teardown paths that call the product-info and sysfs helpers.

## Risks and edge cases
SKU detection is partly string-based and can miss new server cards or misclassify VBIOS part numbers. Some supported IP versions return `FRU_EEPROM_MADDR_INV`, meaning FRU data is supported but not directly readable. The parser assumes IPMI FRU type/length fields fit inside the validated Product Info Area; it bounds string copies but advances offsets manually. Sysfs show handlers assume `adev->fru_info` remains valid while attributes exist.

## Test signals
Signals include supported and unsupported SKU detection, VF/APU rejection, I2C adapter absence returning `-ENODEV`, common-header and Product Info Area checksum failures, exact-length EEPROM reads, populated sysfs attributes, serial fallback from unique ID, and teardown removing sysfs files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fru_eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fru_eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fru_eeprom.h

## Purpose
`amdgpu_fru_eeprom.h` declares the AMDGPU FRU product-information cache and sysfs lifecycle API.

## Important APIs, types, and functions
It defines `AMDGPU_PRODUCT_NAME_LEN`, `struct amdgpu_fru_info`, and prototypes for `amdgpu_fru_get_product_info()`, `amdgpu_fru_sysfs_init()`, and `amdgpu_fru_sysfs_fini()`.

## Control flow
The header has no executable control flow. It defines the data contract used by device initialization to fetch FRU data and by sysfs setup/teardown to expose it.

## State and persistence behavior
`struct amdgpu_fru_info` is runtime cached state containing product number, product name, serial, manufacturer name, and FRU ID. Persistent storage is the EEPROM read by the C file.

## Dependencies and integration points
It relies on `struct amdgpu_device` being visible to callers. The structure is stored as `adev->fru_info` and exported via sysfs attributes implemented in `amdgpu_fru_eeprom.c`.

## Risks and edge cases
Fixed-size string buffers require bounded copies and NUL termination in the implementation. New FRU fields or longer identifiers would require structure and sysfs contract changes.

## Test signals
Build coverage plus sysfs reads of all FRU fields on supported server GPUs validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fru_eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fw_attestation.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fw_attestation.c

## Purpose
`amdgpu_fw_attestation.c` exposes PSP firmware-attestation records through a debugfs binary read file on supported discrete GPUs. It validates an attestation database header in VRAM and streams valid fixed-size firmware records to userspace.

## Important APIs, types, and functions
The public initializer is `amdgpu_fw_attestation_debugfs_init()`. Internal data layouts are `struct FW_ATT_DB_HEADER` and `struct FW_ATT_RECORD`. Core logic is in `amdgpu_fw_attestation_debugfs_read()` and support gating is in `amdgpu_is_fw_attestation_supported()`.

## Control flow
Debugfs initialization rejects unsupported devices, then creates `amdgpu_fw_attestation` under the primary DRM minor debugfs root. Reads require a user buffer at least as large as one record, stop at the 4 KiB maximum table size, ask PSP for the attestation-records address, convert that address to a VRAM offset, and on position zero read the header and validate the cookie. Each read then fetches one record after the header plus current file position, stops on the first invalid record, copies a valid record to userspace, advances the file position by one record, and returns the record size.

## State and persistence behavior
The records are stored in VRAM by PSP/firmware and are read on demand. The driver keeps no cache. File position controls iteration through the table during a debugfs read sequence.

## Dependencies and integration points
It depends on debugfs, PSP `psp_get_fw_attestation_records_addr()`, VRAM access through `amdgpu_device_vram_access()`, AMDGPU IP-version/ASIC helpers, and DRM logging. It excludes APUs, MP0 14.0.2/14.0.3, and ASICs older than Sienna Cichlid.

## Risks and edge cases
The file exposes raw binary records, so readers must know the structure layout. Bounds checking uses the maximum table size and current position, but corrupted firmware data can still stop iteration early through invalid cookie or record-valid flags. VRAM address conversion assumes the PSP-provided address lies in VRAM. `copy_to_user()` failures return `-EINVAL` rather than `-EFAULT`.

## Test signals
Signals include debugfs file presence only on supported ASICs, valid cookie acceptance, invalid cookie rejection, record-by-record reads, EOF on invalid record or table bound, small-buffer `-EINVAL`, PSP address failure handling, and userspace decoding of firmware ID/version/source fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fw_attestation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fw_attestation.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fw_attestation.h

## Purpose
`amdgpu_fw_attestation.h` declares the debugfs initialization hook for firmware-attestation reporting.

## Important APIs, types, and functions
It includes `amdgpu.h` and declares `amdgpu_fw_attestation_debugfs_init(struct amdgpu_device *adev)`.

## Control flow
The header has no executable control flow. Device debugfs initialization calls the declared function, which performs support checks internally.

## State and persistence behavior
No state is defined here. The implementation reads PSP-populated VRAM records on demand.

## Dependencies and integration points
It connects AMDGPU device/debugfs setup code with the firmware-attestation implementation and PSP integration.

## Risks and edge cases
The single exported hook hides support gating in the C file, so callers should not assume the debugfs file exists after calling it.

## Test signals
Build coverage and debugfs file creation/absence on supported/unsupported devices validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fw_attestation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gart.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gart.c

## Purpose
`amdgpu_gart.c` implements common internal GART management. It allocates dummy pages and GART page tables in system RAM or VRAM, maps and unmaps CPU/VRAM pages into the GPU aperture, handles gfx9 MQD memory-type differences, and invalidates GPU TLBs after table changes.

## Important APIs, types, and functions
Public functions include `amdgpu_gart_init()`, `amdgpu_gart_dummy_page_fini()`, `amdgpu_gart_table_ram_alloc()`, `amdgpu_gart_table_ram_free()`, `amdgpu_gart_table_vram_alloc()`, `amdgpu_gart_table_vram_free()`, `amdgpu_gart_map()`, `amdgpu_gart_bind()`, `amdgpu_gart_unbind()`, `amdgpu_gart_map_vram_range()`, `amdgpu_gart_map_gfx9_mqd()`, and `amdgpu_gart_invalidate_tlb()`.

## Control flow
Initialization verifies `PAGE_SIZE >= AMDGPU_GPU_PAGE_SIZE`, DMA maps the global TTM dummy page, and derives CPU/GPU page counts from `adev->gmc.gart_size`. System-RAM table allocation allocates pages, assigns them to the device mapping, DMA maps them, builds an SG table, creates an SG BO, pins it in GTT, stores the CPU pointer, and allocates VMID0 GART backing. VRAM table allocation uses `amdgpu_bo_create_kernel()` and initializes entries to default PTE flags. Mapping functions write GPU PTE/PDE entries with `amdgpu_gmc_set_pte_pde()`, expanding each CPU page into 4 KiB GPU pages when needed. Unbind replaces entries with the dummy page and invalidates TLBs.

## State and persistence behavior
Runtime state lives in `adev->gart`: BO, CPU pointer, page counts, table size, and default PTE flags, plus `adev->dummy_page_addr`. There is no persistence across driver unload. The GART page table is hardware-visible memory and must be reinitialized after teardown/reset as required by ASIC code.

## Dependencies and integration points
It depends on DMA mapping, TTM dummy pages, SG BOs, AMDGPU BO creation/pinning, GMC PTE formatting, reset-domain locking, HDP flush, VM hub masks, and DRM hot-unplug guards. TTM memory management and VMID0 access depend on these mappings.

## Risks and edge cases
System table allocation has many cleanup paths involving pages, SG tables, BOs, pinning, and DMA mappings. TLB invalidation skips HDP flush if the reset-domain read lock cannot be acquired. Hot-unplug guards prevent MMIO access but can leave mapping calls as no-ops. PTE flags must distinguish system memory from VRAM; `amdgpu_gart_map_vram_range()` warns if system flags are used. gfx9 MQD mapping uses UC for the first page and NC for control stack pages, so off-by-one handling matters.

## Test signals
Signals include GART init page counts, RAM-table and VRAM-table allocation/free, dummy-page unmap, BO pin/unpin, CPU-page to GPU-page PTE expansion, unbind to dummy page, TLB flushes on all VM hubs, gfx9 MQD mapping memory types, hot-unplug no-op behavior, and allocation-failure unwind testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gart.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gart.h

## Purpose
`amdgpu_gart.h` defines the AMDGPU GART page-size constants, `struct amdgpu_gart`, and the common GART allocation, mapping, unmapping, and TLB invalidation API.

## Important APIs, types, and functions
It defines 4 KiB GPU page constants, `AMDGPU_GPU_PAGE_ALIGN()`, `AMDGPU_GPU_PAGES_IN_CPU_PAGE`, and `struct amdgpu_gart` with the table BO, CPU pointer, page counts, table size, and default PTE flags. Prototypes cover RAM/VRAM table allocation/free, initialization, dummy page finalization, map/bind/unbind, gfx9 MQD mapping, VRAM range mapping, and TLB invalidation.

## Control flow
The header has no executable flow but defines the sequence used by ASIC code: initialize the GART, allocate a table in the appropriate memory domain, bind/unbind pages as BOs move, invalidate TLBs after changes, and free resources during teardown.

## State and persistence behavior
`struct amdgpu_gart` is runtime device state attached to `struct amdgpu_device`. It describes hardware-visible page-table memory, not durable storage.

## Dependencies and integration points
It depends on Linux integer types, DMA addresses via prototypes, AMDGPU device and BO forward declarations, and GMC/PTE implementation in the C file and ASIC-specific code.

## Risks and edge cases
The macro `AMDGPU_GPU_PAGES_IN_CPU_PAGE` assumes CPU pages are an integer multiple of 4 KiB; the implementation rejects smaller CPU pages. Callers must pass offsets and sizes aligned to GPU page granularity and correct PTE flags for the memory type.

## Test signals
Build coverage, GART page-count logging, BO mapping/unmapping tests, and ASIC-specific GART bring-up validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gds.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gds.h

## Purpose
`amdgpu_gds.h` defines small structures describing Global Data Share resource sizes and register offsets for GDS, GWS, and OA resources.

## Important APIs, types, and functions
It forward declares `struct amdgpu_ring` and `struct amdgpu_bo`, defines `struct amdgpu_gds` with GDS/GWS/OA sizes and compute max wave ID, and defines `struct amdgpu_gds_reg_offset` with register offsets for memory base, memory size, GWS, and OA.

## Control flow
The header has no executable control flow. It provides shared data layouts consumed by command submission, resource allocation, and ASIC programming paths elsewhere in AMDGPU.

## State and persistence behavior
Instances are runtime configuration state. They describe hardware resource capacities or register offsets and are not persisted.

## Dependencies and integration points
It integrates AMDGPU GDS resource accounting with ring/BO-related code via forward declarations while avoiding heavy includes.

## Risks and edge cases
The structures are compact and rely on callers to interpret units consistently. ASIC-specific register offsets must match hardware definitions or GDS/GWS/OA programming will target the wrong registers.

## Test signals
Build coverage, GDS/GWS/OA command submission, resource allocation limits, and ASIC register programming tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gem.c

## Purpose
`amdgpu_gem.c` implements AMDGPU GEM object operations and user-facing GEM ioctls. It creates device and userptr BOs, maps them to userspace, tracks per-file VM BO associations, handles metadata and placement operations, updates GPU virtual-address mappings, lists process handles, creates dumb display buffers, and exposes GEM debugfs state.

## Important APIs, types, and functions
Important exported functions include `amdgpu_gem_object_create()`, `amdgpu_gem_force_release()`, `amdgpu_gem_create_ioctl()`, `amdgpu_gem_userptr_ioctl()`, `amdgpu_gem_mmap_ioctl()`, `amdgpu_gem_wait_idle_ioctl()`, `amdgpu_gem_metadata_ioctl()`, `amdgpu_gem_va_ioctl()`, `amdgpu_gem_op_ioctl()`, `amdgpu_gem_list_handles_ioctl()`, `amdgpu_mode_dumb_create()`, `amdgpu_mode_dumb_mmap()`, `amdgpu_gem_timeout()`, and `amdgpu_debugfs_gem_init()`. GEM object hooks are collected in `amdgpu_gem_object_funcs`.

## Control flow
Object creation builds `amdgpu_bo_param`, forces VRAM wipe-on-release, calls `amdgpu_bo_create_user()`, and returns the embedded GEM object. GEM open rejects foreign userptr mm ownership and invalid always-valid use, locks the BO and VM page directory with DRM exec, creates or references a `bo_va`, attaches an eviction fence, and for dynamic DMA-buf imports in compute VMs validates and fences the BO with KFD process eviction state. Close detaches eviction fences, drops `bo_va` references, clears freed VM mappings when ready, and fences the BO with resulting page-table work. Fault handling reserves the TTM BO, notifies AMDGPU before faulting pages, and falls back to a dummy page after unplug.

Ioctls validate flags and domains, create BOs with fallback from required CPU access or VRAM-only placement, create userptr BOs with HMM/MMU-notifier registration and optional upfront validation, return mmap offsets only for CPU-accessible non-userptr objects, wait on BO reservation fences, get/set metadata and tiling, mutate VM mappings through map/unmap/clear/replace operations, optionally export VM update fences to syncobj timelines, change placement, report create or mapping info, list all handles for a file, and create aligned dumb buffers in display-supported domains.

## State and persistence behavior
Runtime state lives in GEM handles, TTM BOs, AMDGPU BO flags/domains/metadata, `amdgpu_bo_va` mappings, VM page tables, HMM userptr registration, reservation fences, syncobj timeline points, and per-file object IDRs. No data is persisted by this file beyond BO memory contents while objects live. Metadata and mappings are kernel runtime state exposed through ioctls.

## Dependencies and integration points
It depends on DRM GEM/TTM helpers, DRM exec locking, syncobj timelines, dma-buf imports, HMM/userptr support, AMDGPU BO/VM/display/dma-buf/XGMI/KFD/user-queue eviction code, dma-resv, and debugfs. Its ioctl entry points are registered by `amdgpu_drv.c`.

## Risks and edge cases
User input validation is broad: flags, domains, addresses, VA holes, reserved ranges, metadata sizes, and placement changes all need strict checks. VM updates must merge page-table and BO mapping fences so userspace does not miss PDE updates. Object open/close lock ordering with BOs, VM PDs, eviction fences, and KFD process locks is sensitive. Userptr write access requires registration; foreign-mm userptr sharing is rejected. `amdgpu_gem_userptr_ioctl()` has an early `-ENOMEM` path after range allocation failure that bypasses `drm_gem_object_put()`, which is a code-review risk to verify against surrounding ownership expectations. Handle listing can race object table changes and returns `-EAGAIN` if counts change.

## Test signals
Signals include GEM create fallback paths, TMZ encrypted buffer rejection when disabled, GDS/GWS/OA no-CPU-access creation, always-valid BO behavior, mmap permission checks, userptr validation and MMU invalidation, metadata get/set, VA map/unmap/clear/replace across reserved ranges and VM holes, syncobj timeline fence export, placement changes with imported/userptr/XGMI BOs, dumb buffer allocation/pitch alignment, fd close mapping cleanup, debugfs GEM info, and handle-list retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gem.h

## Purpose
`amdgpu_gem.h` declares AMDGPU GEM object helpers, ioctl handlers, dumb-buffer helpers, and the user-settable GEM create flag mask.

## Important APIs, types, and functions
It defines `AMDGPU_GEM_DOMAIN_MAX`, `gem_to_amdgpu_bo()`, declares `amdgpu_gem_object_funcs`, and prototypes all major GEM helpers and ioctls implemented in `amdgpu_gem.c`. `AMDGPU_GEM_CREATE_SETTABLE_MASK` lists flags userspace may set during GEM creation, including CPU access controls, VM always-valid, explicit sync, wipe-on-release, encryption, DCC, discardable, and coherence/cache flags.

## Control flow
The header has no executable control flow. It defines the external contract used by the DRM ioctl table, display dumb-buffer paths, BO users, and debugfs initialization.

## State and persistence behavior
No state is allocated here. The macro `gem_to_amdgpu_bo()` maps DRM GEM objects to their containing AMDGPU BO runtime state.

## Dependencies and integration points
It depends on DRM AMDGPU UAPI definitions and DRM GEM core types. It is the bridge between driver registration in `amdgpu_drv.c` and GEM implementation in `amdgpu_gem.c`.

## Risks and edge cases
The settable-mask macro is an important UAPI validation boundary; adding a flag here permits userspace to request it through GEM create. Prototype drift breaks ioctl registration. `gem_to_amdgpu_bo()` assumes every passed GEM object is an AMDGPU BO.

## Test signals
Build coverage, ioctl flag validation, GEM create tests for every settable flag, and imported-object paths validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gem.h -->
