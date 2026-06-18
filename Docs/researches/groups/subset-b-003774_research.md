# subset-b-003774 research

Grouped source research for Xe DRM device, submission, forcewake, GGTT, dma-buf, RAS, fdinfo, EU stall, and scheduler files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.h

## Purpose
`xe_device.h` is the public convenience and lifecycle header for the Xe DRM device object. It provides casts from DRM, PCI, kernel device, and TTM handles to `struct xe_device`, declares device create/probe/remove/shutdown entry points, and centralizes helpers for GT/tile lookup, memory access, address canonicalization, flushing, wedged state, and per-file references.

## Important APIs, types, and functions
The most used helpers are `to_xe_device()`, `kdev_to_xe_device()`, `pdev_to_xe_device()`, `ttm_to_xe_device()`, `to_xe_file()`, `xe_device_get_root_tile()`, `xe_device_get_gt()`, `xe_root_mmio_gt()`, and `xe_root_tile_mmio()`. Iteration macros cover tiles, remote tiles, all GTs, typed GTs, and GTs on a tile. Capability helpers expose UC submission, flat CCS, SR-IOV, MSI-X, memory IRQ, LMTT, and MERT. Declared operations include memory barriers, memory-access assertion, CCS byte sizing, device snapshot printing, canonical/uncanonical address conversion, TD/L2 flushing, wedged-state control, file refcounting, fault-injection status, file identity, and ASID-to-VM lookup.

## Control flow and integration points
Most control flow is inline dispatch around `xe->info.tile_count` and `xe->info.max_gt_per_tile`. `xe_device_get_gt()` maps a global GT id to tile primary/media GT, validates initialized GT identity, and returns NULL for out-of-range or missing GTs. These helpers are used throughout submission, memory management, sysfs, fdinfo, and PM code.

## State and persistence behavior
The header does not allocate state, but it exposes persistent device state in `struct xe_device`: tile arrays, capability flags, IRQ mode, wedged atomics, and per-file objects. `LNL_FLUSH_WORKQUEUE()` and `LNL_FLUSH_WORK()` intentionally map to workqueue flushes as a platform latency workaround.

## Dependencies, risks, and test signals
Dependencies are DRM core, TTM, Xe device types, GT types, and SR-IOV helpers. Risks are incorrect GT id mapping on multi-tile/media platforms, stale capability helpers, or wedged-state misuse. Test signals include probe/remove, multi-tile GT enumeration, SR-IOV PF/VF paths, memory IRQ enablement, ASID lookup, runtime suspend/resume, wedged uevents, and build coverage for all inline consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.c

## Purpose
`xe_device_sysfs.c` creates PCI-device sysfs attributes for device-level Xe knobs and read-only platform status. It exposes runtime D3cold VRAM threshold control, late-binding fan and voltage-regulator version reporting, and Battlemage PCIe Gen5 auto-link-downgrade capability/status.

## Important APIs, types, and functions
`vram_d3cold_threshold_show()` and `_store()` read and update `xe->d3cold.vram_threshold` through `xe_pm_set_vram_threshold()` under runtime PM. `lb_fan_control_version_show()` and `lb_voltage_regulator_version_show()` query PCODE late-binding capability and version mailboxes and format major.minor.hotfix.build. `late_bind_attr_is_visible()` hides version files unless PCODE reports support. `auto_link_downgrade_capable_show()` reads `BMG_PCIE_CAP`, while `auto_link_downgrade_status_show()` reads DGFX init status through PCODE. `xe_device_sysfs_init()` installs managed attribute groups conditionally.

## Control flow and integration points
Initialization adds the VRAM group only when `xe->d3cold.capable` is true. Battlemage non-VF devices get auto-link-downgrade and late-bind groups. All hardware reads run under `guard(xe_pm_runtime)(xe)` so sysfs access wakes the device safely. The attributes integrate with PM policy, PCODE mailbox definitions, MMIO register definitions, and PCI device kobjects.

## State and persistence behavior
Only the D3cold threshold is mutable persistent driver state; it is protected inside `xe_pm_set_vram_threshold()`. Version and link files are live hardware/firmware views. The groups are devm-managed and are removed with the device.

## Dependencies, risks, and test signals
Dependencies include PCI sysfs, runtime PM, PCODE mailbox APIs, root-tile MMIO, SR-IOV mode, and Battlemage register fields. Risks include exposing attributes on unsupported hardware, failing PCODE reads while sysfs visibility is evaluated, incorrect runtime-PM nesting, and user-visible D3cold policy regressions. Test signals are sysfs presence/absence by platform/VF mode, read/write threshold behavior, PCODE error propagation, link downgrade field decoding, and suspend/resume with sysfs polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.h

## Purpose
`xe_device_sysfs.h` is the small declaration header for device-level sysfs setup. It lets the probe path initialize the sysfs attribute groups without exposing implementation details.

## Important APIs, types, and functions
The file forward-declares `struct xe_device` and declares `int xe_device_sysfs_init(struct xe_device *xe);`.

## Control flow and integration points
There is no executable control flow. The implementation installs devm-managed groups for D3cold threshold, late-binding version, and PCIe auto-link-downgrade attributes. Probe or device initialization code includes this header to invoke the setup once the `xe_device` and capability flags are available.

## State and persistence behavior
The header owns no state. It describes a setup entry point that creates sysfs files whose lifetime follows the underlying PCI device through managed resource cleanup.

## Dependencies, risks, and test signals
The dependency surface is intentionally minimal. Risks are mostly build/API drift if the implementation signature changes or if callers invoke it before runtime PM, PCODE, or capability state is initialized. Test signals are successful driver build, probe-time sysfs registration, and correct cleanup on probe failure and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_types.h

## Purpose
`xe_device_types.h` defines the central top-level Xe driver state containers: `struct xe_device` for the DRM device and `struct xe_file` for per-open-file state. It is the shared type contract used by almost every Xe subsystem.

## Important APIs, types, and functions
`enum xe_wedged_mode` defines recovery policy. `struct xe_device` embeds `struct drm_device`, optional display pointer, device coredump, `info` platform/IP/capability flags, active workaround bitmap, survivability, IRQ/MSI-X state, TTM device, global MMIO mapping, memory managers, SR-IOV PF/VF state, USM ASID/page-fault queues, pinned BO lists, workqueues, tile array, memory-access tracking, PAT tables, D3cold policy, PM notifiers, telemetry/remapper state, HECI/GSC, late bind, OA, PXP, wedged state, async BO free state, PMU, RAS, I2C, SVM timeslices, validation domain, and KUnit hooks. `struct xe_file` stores the owning device, DRM file, VM and exec-queue xarrays plus locks, per-engine-class run ticks, client accounting object, process identity, and kref.

## Control flow and integration points
This header has no functions, but its layout governs initialization, teardown, fdinfo, VM binding, exec queue lookup, PM, SR-IOV, memory management, RAS, and display compatibility. Many helpers in `xe_device.h` and subsystem modules directly dereference these fields.

## State and persistence behavior
Most persistent driver state for a live PCI function is anchored here. Device capability flags remain fixed after probe. xarrays, workqueues, lists, locks, atomics, notifiers, and counters persist until remove. `xe_file` state persists until the DRM file is closed and asynchronous queue destruction has drained.

## Dependencies, risks, and test signals
Dependencies include DRM core/file, TTM, platform/step types, tile, page fault, PMU, SR-IOV, survivability, RAS, OA, validation, and display compatibility shims. Risks are layout coupling, lock-order mistakes, missing initialization of nested locks/lists, stale capability flags, and UAF around per-file xarrays. Test signals include full probe/remove, open/close stress, VM and exec queue creation/destruction, SR-IOV PF/VF tests, fdinfo accounting, runtime PM, suspend/resume, error recovery, and KUnit/debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_wa_oob.rules -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_wa_oob.rules

## Purpose
`xe_device_wa_oob.rules` is a data input file for generated out-of-band Xe device workarounds. Each rule maps a workaround identifier to platform, subplatform, display, or stepping predicates consumed by the workaround code generator.

## Important APIs, types, and functions
The file is not C code. Entries include `22010954014 PLATFORM(DG2)`, `15015404425 PLATFORM(LUNARLAKE) PLATFORM(PANTHERLAKE)`, `22019338487_display PLATFORM(LUNARLAKE)`, `14022085890 SUBPLATFORM(BATTLEMAGE, G21)`, and `14026539277 PLATFORM(NOVALAKE_P), PLATFORM_STEP(A0, B0)`. Continuation lines extend the previous rule, which is part of the parser contract in `xe_gen_wa_oob.c`.

## Control flow and integration points
Build tooling reads this file and emits generated C/header tables such as `generated/xe_wa_oob.h`. Driver code later queries the generated identifiers through `XE_DEVICE_WA()` or related helpers when deciding platform-specific behavior.

## State and persistence behavior
The rules persist as source data only. At build time they become enum identifiers and rule arrays; at runtime active workaround state is tracked under `xe->wa_active.oob`.

## Dependencies, risks, and test signals
Dependencies are the rule parser syntax, platform/subplatform/step vocabulary, and generated workaround consumers. Risks include malformed continuation lines, predicates that are too broad or too narrow, identifier collisions, or deleting rules still used by runtime code. Test signals are successful code generation, generated enum/table diffs, platform matrix validation, and runtime workaround activation logs on DG2, Lunar Lake, Battlemage G21, Panther Lake, and Nova Lake P steppings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_wa_oob.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.c

## Purpose
`xe_dma_buf.c` implements Xe PRIME dma-buf export/import, attachment policy, mapping, CPU-access migration, and move notifications. It bridges Xe BO/TTM placement rules with the Linux dma-buf and DRM PRIME interfaces.

## Important APIs, types, and functions
Export-side ops include `xe_dma_buf_attach()`, `detach()`, `pin()`, `unpin()`, `map_dma_buf()`, `unmap_dma_buf()`, `begin_cpu_access()`, and `release()` through `xe_dmabuf_ops`. `xe_gem_prime_export()` rejects VM-private, purgeable, or purged BOs, marks them willneed, prepares TTM export, and installs Xe dma-buf ops. Import uses `xe_gem_prime_import()`, `xe_dma_buf_create_obj()`, dynamic attach ops, and `xe_dma_buf_move_notify()`.

## Control flow and integration points
Attachment disables peer-to-peer if PCI P2P distance is invalid, otherwise requires migration to TT memory when not P2P. Pin scans all attachments to decide if VRAM is allowed; if not, it migrates to TT and pins externally. Mapping builds an SG table from TT pages or VRAM manager ranges. Import of a self-exported dma-buf returns the GEM object directly unless KUnit forces different-device behavior; external imports create an SG BO bound to the dma-buf reservation before dynamic attach.

## State and persistence behavior
Runtime PM refs are held per attachment. Exported BOs hold willneed state until dma-buf release. Imported objects store `obj->import_attach`; move notifications evict importer BO mappings. Placement may change between VRAM and TT depending on attachment mix.

## Dependencies, risks, and test signals
Dependencies include dma-buf, PCI P2PDMA, DRM PRIME, TTM TT, Xe BO migration/pinning, VRAM manager SG allocation, validation, and runtime PM. Risks include pinned VRAM with non-P2P importers, SG table lifetime mismatches, CPU access in current placement after migration failure, purgeable export races, and global attachment-list policy. Test signals include PRIME export/import, self-import, P2P and non-P2P attachments, CPU read access, purge/madvise rejection, move-notify eviction, KUnit live dma-buf tests, and runtime PM leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.h

## Purpose
`xe_dma_buf.h` declares the Xe PRIME dma-buf entry points used by DRM GEM callbacks.

## Important APIs, types, and functions
The header includes `drm_gem.h` and declares `struct dma_buf *xe_gem_prime_export(struct drm_gem_object *obj, int flags);` and `struct drm_gem_object *xe_gem_prime_import(struct drm_device *dev, struct dma_buf *dma_buf);`.

## Control flow and integration points
There is no control flow in the header. DRM driver ops wire these functions into PRIME export/import paths. The implementation handles BO placement, dma-buf attachment, mapping, CPU access, and imported object construction.

## State and persistence behavior
The header owns no state. The declared functions manipulate GEM/BO references, dma-buf attachments, runtime PM references, and imported-object attachment state in the implementation.

## Dependencies, risks, and test signals
Dependencies are DRM GEM and dma-buf type visibility. Risks are signature drift with DRM PRIME callbacks or missing include coverage for users. Test signals are successful build of driver ops, PRIME ioctl export/import tests, and KUnit dma-buf scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.c

## Purpose
`xe_drm_client.c` implements per-DRM-client memory and engine runtime reporting for `/proc/<pid>/fdinfo`, plus client object lifetime and private BO tracking.

## Important APIs, types, and functions
`xe_drm_client_alloc()` initializes a kref and, with procfs, `bos_lock` and `bos_list`. `__xe_drm_client_free()` releases the client. `xe_drm_client_add_bo()` and `xe_drm_client_remove_bo()` attach internal BOs to client accounting. `bo_meminfo()` classifies BO memory as private/shared, resident, active, and purgeable. `show_meminfo()` aggregates public GEM objects and internal client BOs. `show_run_ticks()` samples queue runtime and total GPU timestamp. `xe_drm_client_fdinfo()` prints memory and run-tick sections.

## Control flow and integration points
Memory reporting walks the DRM file object IDR under `file->table_lock`; if a BO reservation cannot be trylocked it temporarily refs the BO, drops the table lock, locks the BO, samples it, and reacquires. Internal BOs are walked under `client->bos_lock` with deferred put batching. Runtime reporting waits for pending queue removal to complete, takes runtime PM and forcewake on any engine, updates all file exec queues, reads a hardware timestamp, then prints class-specific cycle keys and capacities.

## State and persistence behavior
Client state persists for the DRM file lifetime and owns refs from BO client links. `xef->run_ticks[]` accumulates queue runtime deltas; pending queue removal uses an atomic wait variable to avoid fdinfo racing context-switch-out accounting.

## Dependencies, risks, and test signals
Dependencies include DRM fdinfo/memory stats, Xe BO/ref helpers, exec queue runtime updates, forcewake, runtime PM, hardware engine timestamp reads, and procfs configuration. Risks include lock-order regressions, BO UAF during list walks, inaccurate parallel-queue accounting, VF omission of total cycles, and stalled fdinfo waits. Test signals are fdinfo memory totals by region, shared/imported object accounting, queue create/destroy while reading fdinfo, SR-IOV VF output, and runtime PM/forcewake leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.h

## Purpose
`xe_drm_client.h` defines the lightweight client accounting object and inline refcount helpers used by BO tracking and fdinfo reporting.

## Important APIs, types, and functions
`struct xe_drm_client` contains a kref, numeric id, and, under `CONFIG_PROC_FS`, a spinlock-protected `bos_list`. Inline `xe_drm_client_get()` and `xe_drm_client_put()` manage references through `__xe_drm_client_free()`. Public declarations cover allocation, fdinfo output, and BO add/remove hooks, with no-op BO hooks when procfs is disabled.

## Control flow and integration points
The header has only inline refcount control. BO creation paths call add/remove when internal objects need client accounting. DRM driver fdinfo callbacks call `xe_drm_client_fdinfo()` under procfs.

## State and persistence behavior
The client object persists while held by an open `xe_file` and by any internal BOs linked for accounting. The list is protected by `bos_lock`; when procfs is disabled no list state exists.

## Dependencies, risks, and test signals
Dependencies include Linux kref/list/spinlock and DRM file/printer declarations. Risks include double add/remove of BO client links, refcount imbalance, and conditional-build drift between procfs and non-procfs configurations. Test signals are open/close refcount stress, internal BO lifetime tests, procfs fdinfo reads, and allmodconfig/no-procfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.c

## Purpose
`xe_drm_ras.c` registers Xe error counters with the DRM RAS core. It creates per-device nodes for correctable and uncorrectable error severities and exposes counters by hardware error component.

## Important APIs, types, and functions
`hw_query_error_counter()` validates a counter table entry and returns its name and atomic count. Severity-specific query callbacks select `xe->ras.info[DRM_XE_RAS_ERR_SEV_*]`. `allocate_and_copy_counters()` allocates component counters from `DRM_XE_RAS_ERROR_COMPONENT_NAMES`. `assign_node_params()` formats the PCI device name, fills `drm_ras_node`, allocates severity counters, and selects query callback. `register_nodes()` registers each severity. `xe_drm_ras_init()` allocates node storage with drmm, registers nodes, and installs cleanup action.

## Control flow and integration points
Initialization loops over `for_each_error_severity()`, assigns node metadata, registers with `drm_ras_node_register()`, then registers `xe_drm_ras_unregister_nodes()` as a managed cleanup action. Query flow comes from DRM RAS into the severity callback and then into the severity/component counter table.

## State and persistence behavior
`xe->ras.node` is drmm-managed. Per-severity `ras->info[]` arrays and node device-name strings are manually allocated and freed on cleanup. Counters are atomic and currently initialized to zero; hardware error reporters can increment them through the stored arrays.

## Dependencies, risks, and test signals
Dependencies are DRM RAS, UAPI component/severity name arrays, PCI identity, and managed DRM cleanup. Risks include leaks if `assign_node_params()` fails after `device_name` allocation, incomplete cleanup on partial register failure, name-array/index mismatch, and unconnected hardware increment paths. Test signals are RAS node creation/removal, sysfs/debugfs RAS counter reads, injected correctable/uncorrectable increments, probe-failure cleanup, and PCI BDF formatting checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.h

## Purpose
`xe_drm_ras.h` is the public Xe RAS declaration header. It provides the severity iteration macro and the initialization entry point.

## Important APIs, types, and functions
The header forward-declares `struct xe_device`, defines `for_each_error_severity(i)` as a loop over `DRM_XE_RAS_ERR_SEV_MAX`, and declares `int xe_drm_ras_init(struct xe_device *xe);`.

## Control flow and integration points
There is no executable control flow. Device probe code includes this header to register DRM RAS nodes; implementation code uses the macro to initialize and unregister severity nodes consistently.

## State and persistence behavior
The header owns no state. Initialization populates `xe->ras` as defined in `xe_drm_ras_types.h`.

## Dependencies, risks, and test signals
It relies on DRM Xe UAPI severity constants being visible through included implementation contexts. Risks are macro drift if severity enumeration changes. Test signals are build coverage and successful RAS init/unregister paths for every defined severity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras_types.h

## Purpose
`xe_drm_ras_types.h` defines Xe RAS state structures and a small hardware-error category enum.

## Important APIs, types, and functions
`enum hardware_error` distinguishes correctable, nonfatal, fatal, and max categories. `struct xe_drm_ras_counter` pairs a component name with an atomic counter. `struct xe_drm_ras` stores the allocated DRM RAS node array and per-severity arrays of `xe_drm_ras_counter`.

## Control flow and integration points
The header has no control flow. `xe_device_types.h` embeds `struct xe_drm_ras ras` in `struct xe_device`, while `xe_drm_ras.c` allocates nodes and counter arrays and registers them with DRM RAS.

## State and persistence behavior
Counter arrays persist for the device lifetime after RAS initialization. Counter increments are atomic so hardware error paths can update them concurrently with RAS queries.

## Dependencies, risks, and test signals
Dependencies include Linux atomics and `drm/xe_drm.h` severity/component constants. Risks include unused or mismatched `enum hardware_error`, counter-array sizing tied to UAPI values, and missing synchronization for future non-atomic fields. Test signals include counter query correctness, concurrent increment/read tests, and build checks when UAPI RAS enums change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drv.h

## Purpose
`xe_drv.h` provides the Xe DRM driver identity and version macros used by driver registration and userspace-visible metadata.

## Important APIs, types, and functions
It defines `DRIVER_NAME` as `xe`, `DRIVER_DESC` as `Intel Xe2 Graphics`, and interface version macros `DRIVER_MAJOR`, `DRIVER_MINOR`, and `DRIVER_PATCHLEVEL`, currently 1.1.0. The comment records interface history with 1.1 as original.

## Control flow and integration points
There is no control flow. DRM driver setup includes these macros when registering the driver and reporting version information through DRM APIs.

## State and persistence behavior
No runtime state is owned here. The values are compile-time constants that persist as the driver identity for a built kernel/module.

## Dependencies, risks, and test signals
The only direct dependency is `drm/drm_drv.h`. Risks are user-visible identity/version drift and mismatch between UAPI changes and version history. Test signals include module/driver registration, DRM version queries, modinfo output, and userspace feature-detection sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.c

## Purpose
`xe_eu_stall.c` implements EU stall observation streams. It lets privileged userspace open an anonymous fd, enable hardware sampling, poll/read per-XeCore stall records, and disable/close the stream.

## Important APIs, types, and functions
Data structures include per-XeCore circular-buffer pointers, `xe_eu_stall_data_stream`, GT-level `xe_eu_stall_gt`, open properties, and packed PVC/Xe2/Xe3p record formats. Public helpers report supported sampling rates, per-XeCore buffer size, record size, initialize GT state, and open a stream. Internal paths parse user extensions, allocate GGTT-mapped system BO buffers, program MCR EU stall registers, poll write pointers, copy records to userspace, report drop bits, and handle enable/disable ioctls.

## Control flow and integration points
`xe_eu_stall_stream_open()` validates platform support and perf permissions, parses properties, requires a GT id, serializes on `stream_lock`, allocates one stream, initializes buffers, and returns an anon inode fd. Enable takes runtime PM and render forcewake, applies WA `22016596838` if needed, initializes read/write pointers, programs MOCS/sample rate/base registers, and starts delayed polling. Polling checks all DSS steering instances every 5 ms and wakes readers once enough rows are present. Read aligns user count to record size, blocks unless `O_NONBLOCK`, copies circular data across wrap boundaries, advances hardware read pointers, and reports drops as `-EIO` once.

## State and persistence behavior
One stream can exist per GT. The stream owns a pinned GGTT BO, per-XeCore buffer metadata, waitqueue, delayed work, forcewake ref, runtime PM ref while enabled, and data-drop bitmap. Close disables sampling, frees the BO, clears `gt->eu_stall->stream`, and drops the DRM device ref.

## Dependencies, risks, and test signals
Dependencies include observation ioctls, anon inodes, MCR register access, forcewake, runtime PM, GT topology, GGTT BO allocation, MOCS, platform workarounds, and generated WA identifiers. Risks include pointer wrap math, buffer overflow/drop reporting, single-stream locking, enable failure leaving `enabled` true, small read buffer behavior, forcewake leaks, and unsupported platform exposure. Test signals include open/enable/poll/read/disable/close, blocking and nonblocking reads, drop-bit injection, PVC/Xe2/Xe3p record-size checks, GT id validation, perf permission checks, runtime PM, and suspend/removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.h

## Purpose
`xe_eu_stall.h` declares the EU stall observation API and the platform support predicate.

## Important APIs, types, and functions
The header declares `xe_eu_stall_get_per_xecore_buf_size()`, `xe_eu_stall_data_record_size()`, `xe_eu_stall_get_sampling_rates()`, `xe_eu_stall_init()`, and `xe_eu_stall_stream_open()`. Inline `xe_eu_stall_supported_on_platform()` returns true for non-SRIOV-VF PVC or graphics version 20 and newer.

## Control flow and integration points
Callers use the support predicate before initializing GT state or exposing observation stream open behavior. The open function is invoked from the observation ioctl path and returns an anonymous fd for stream operations.

## State and persistence behavior
The header owns no state. The implementation allocates `gt->eu_stall`, stream objects, pinned BOs, workqueues, runtime PM references, and forcewake references.

## Dependencies, risks, and test signals
Dependencies are GT/device types and SR-IOV mode helpers. Risks are platform predicate drift, missing declarations for observation integration, and exposing the feature on VF where registers are unavailable. Test signals are platform capability queries, build coverage with observation code, SR-IOV VF rejection, and stream open tests on PVC/Xe2+ hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.c

## Purpose
`xe_exec.c` implements the user exec ioctl for GPU command submission. It is the high-level path that validates a user exec request, parses sync objects, locks and validates the VM, creates a scheduler job, wires dependencies and output fences, then submits to the exec queue backend.

## Important APIs, types, and functions
`xe_exec_fn()` injects VM validation/rebind into the `drm_gpuvm_exec` locking loop. `xe_exec_ioctl()` handles `DRM_XE_EXEC`: queue lookup, argument validation, sync parsing, batch address copy for parallel queues, hardware-engine-group mode selection, VM locking, userptr pin/recheck, validation, protected VM checks, job creation, dependency setup, user fence setup, last-fence update, job push, and cleanup.

## Control flow and integration points
The ioctl rejects extensions/padding/reserved fields, queue VM-bind misuse, mismatched batch count and queue width, reset queues, and too many queued jobs. For empty submissions, it only converts in-fences to out-fences and updates the last fence. For real execs it blocks on suspend, runs validation for non-LR VMs, checks closed/banned VM state, validates PXP, creates a job, adds VM rebind and sync dependencies, locks SVM notifier state for userptr repin checks, arms the job as the point of no return, installs dma-resv bookkeeping and sync outputs, pushes the job, and resumes faulting LR jobs when needed.

## State and persistence behavior
The path mutates queue job counts through job lifetime, VM validation state, dma-resv fence slots, syncobj/user-fence outputs, queue last-fence state, VM rebind activity, LRU bulk-move placement, and hardware-engine-group execution mode references.

## Dependencies, risks, and test signals
Dependencies include DRM exec/GPUVM, Xe VM/userptr/SVM, exec queues, hw engine groups, scheduler jobs, sync parsing, PM suspend blocking, PXP, and tracepoints. Risks include lock ordering around VM and dma-resv, repin retry loops, mode get/put imbalance, point-of-no-return error semantics, user fence limits, and LR/non-LR divergence. Test signals include exec ioctl validation, parallel submissions, empty exec/fence conversion, userptr invalidation races, VM ban/close, PXP protected queues, suspend freezer interruption, LR fault resume, syncobj/user-fence behavior, and max-job backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.h

## Purpose
`xe_exec.h` is the declaration header for user GPU command submission.

## Important APIs, types, and functions
It forward-declares `struct drm_device` and `struct drm_file`, and declares `int xe_exec_ioctl(struct drm_device *dev, void *data, struct drm_file *file);`.

## Control flow and integration points
There is no header-local control flow. DRM ioctl dispatch includes this function to handle user exec submissions. The implementation coordinates VM locking, sync parsing, job creation, and backend scheduling.

## State and persistence behavior
The header owns no state. The declared ioctl mutates VM fences, queue last fences, scheduler jobs, and user synchronization objects.

## Dependencies, risks, and test signals
Dependencies are DRM ioctl wiring and type declarations. Risks are signature mismatch with the ioctl table. Test signals are driver build and exec ioctl smoke/stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.c

## Purpose
`xe_exec_queue.c` implements execution queue allocation, initialization, ioctl creation/destruction/property handling, multi-queue grouping, LRC management, runtime accounting, kill/fini ordering, and last-fence tracking.

## Important APIs, types, and functions
Core APIs include `xe_exec_queue_create()`, `xe_exec_queue_create_class()`, `xe_exec_queue_create_bind()`, `xe_exec_queue_destroy()`, `xe_exec_queue_fini()`, `xe_exec_queue_lookup()`, `xe_exec_queue_create_ioctl()`, property get/set ioctls, `xe_exec_queue_is_lr()`, `xe_exec_queue_is_idle()`, `xe_exec_queue_update_run_ticks()`, `xe_exec_queue_kill()`, and last-fence/TLB-invalidation fence helpers. Internal helpers allocate dependency schedulers, parse user extensions, validate logical engine masks, initialize multi-queue groups, and add secondary queues.

## Control flow and integration points
Creation allocates a flex-array queue, initializes defaults from the hardware engine class, optionally parses user extensions before LRC creation, initializes backend ops, then creates LRCs while coordinating with SR-IOV VF GGTT migration fixups. User create ioctl validates placements, handles VM-bind queues per tile, validates regular engine masks and multi-LRC constraints, creates queues, attaches multi-queue state, registers LR compute queues and hardware-engine-group membership, then allocates the user xarray id last to avoid UAF. Destroy ioctl erases the xarray id, increments pending-removal for fdinfo synchronization, removes engine-group membership, kills backend execution, traces close, and drops the reference.

## State and persistence behavior
Queues hold VM/file refs, LRC refs, backend state, DRM sched entity, PXP linkage, multi-GT child queues, multi-queue group BO/LRC refs, last fences, TLB invalidation fences, dependency schedulers, run-tick accounting, and optional replay state. Locking contracts vary by queue type: migrate job lock, VM lock, or hardware-engine-group mode semaphore protect last-fence access.

## Dependencies, risks, and test signals
Dependencies include Xe VM, LRC, GuC/execlist backend ops, hw engine groups, migration, dep scheduler, syncobj, PXP, SR-IOV PF/VF, xarrays, and UAPI properties. Risks include multi-queue reference leaks, id allocation ordering, stale LRC GGTT addresses after VF migration, property permission mistakes, lockdep contract violations for fences, and partial creation cleanup. Test signals include queue create/destroy ioctl stress, VM-bind multi-tile queues, multi-LRC validation, multi-queue group add/delete, property limits and CAP_SYS_NICE behavior, LR compute queues, PXP queue lists, fdinfo pending-removal waits, and error-injection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.h

## Purpose
`xe_exec_queue.h` declares the execution queue API and inline helpers used by submission, VM bind, scheduler, fdinfo, and backend code.

## Important APIs, types, and functions
The header exports creation helpers, fini/destroy/name assignment, refcount helpers, lookup, parallel and PXP predicates, multi-queue predicates and primary lookup, LR/idle/kill queries, create/destroy/property ioctls, max priority query, last-fence helpers, TLB invalidation fence helpers, run-tick update, HWSP rebase, and LRC accessors. `for_each_tlb_inval()` iterates primary/media TLB invalidation slots.

## Control flow and integration points
Inline control flow covers kref get/put, width-based parallel detection, PXP type detection, and multi-queue primary/secondary classification. The API is consumed by exec ioctl, VM bind, backend schedulers, fdinfo, suspend/resume, and SR-IOV migration fixups.

## State and persistence behavior
No state is owned by the header. It exposes operations over persistent `struct xe_exec_queue` state: refs, LRCs, VM/file ownership, last fences, TLB invalidation fences, and backend entities.

## Dependencies, risks, and test signals
Dependencies include exec queue and VM types plus DRM file/device declarations. Risks are stale inline predicates relative to `xe_exec_queue_types.h`, improper refcount use, and callers using unlocked last-fence functions outside destroy paths. Test signals include build coverage, kref lifetime stress, queue ioctl tests, VM bind fence tests, and suspend/resume rebase paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue_types.h

## Purpose
`xe_exec_queue_types.h` defines the execution queue data model, priority enums, multi-queue group state, queue flags, scheduling properties, long-running state, TLB invalidation tracking, PXP metadata, and backend operation contract.

## Important APIs, types, and functions
It defines `enum xe_exec_queue_priority`, `enum xe_multi_queue_priority`, `struct xe_exec_queue_group`, `struct xe_exec_queue`, flag bits such as `EXEC_QUEUE_FLAG_KERNEL`, `VM`, `MIGRATE`, and `LOW_LATENCY`, TLB invalidation slot constants, `XE_MAX_JOB_COUNT_PER_EXEC_QUEUE`, and `struct xe_exec_queue_ops`. Backend ops cover init/kill/fini/destroy, scheduling property updates, multi-queue priority, suspend/wait/resume, reset status, and active state.

## Control flow and integration points
There is no executable control flow, but the structure layout defines the runtime contract for GuC and execlist backends, exec ioctl, VM bind, LR compute mode, PXP termination, fdinfo accounting, and SR-IOV migration fixups.

## State and persistence behavior
`struct xe_exec_queue` is persistent for the queue lifetime. It stores VM/file refs, engine class/logical mask/name/width, backend union state, multi-queue membership, scheduler properties, LR preemption fence state, dependency schedulers and TLB fences, VM/hw-engine-group links, user fence syncobj, replay state, DRM sched entity, job count, LRC lookup lock, and an LRC flex array.

## Dependencies, risks, and test signals
Dependencies include DRM scheduler, kref, hardware engine, LRC, fence, and Xe GPU scheduler types. Risks include backend union misuse, missing initialization of links/locks, flex-array width bugs, property state not propagated to backend, and queue flags with incompatible semantics. Test signals include backend init/fini, multi-queue group stress, LR preemption, TLB invalidation ordering, PXP queue handling, job-count throttling, and KASAN/lockdep during queue destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.c

## Purpose
`xe_execlist.c` implements the legacy execlist submission backend used when GuC submission is disabled. It provides port scheduling, LRC start/idle programming, interrupt/timer progress handling, DRM scheduler backend ops, and `xe_exec_queue_ops` for execlist queues.

## Important APIs, types, and functions
Key functions include `__start_lrc()`, `__xe_execlist_port_start()`, `_idle()`, `_start_next_active()`, `read_execlist_status()`, IRQ handler functions, `xe_execlist_make_active()`, fail timer, `xe_execlist_port_create()`, `xe_execlist_port_destroy()`, `execlist_run_job()`, `execlist_job_free()`, backend queue init/fini/destroy, and `xe_execlist_init()`.

## Control flow and integration points
Port creation allocates a kernel idle LRC, initializes priority lists and lock, installs the hardware engine IRQ handler, and starts a fallback timer. Job run emits ring commands, marks the queue active, and returns the job fence. The active selection scans priority lists high-to-low, drops idle queues, and starts the next non-idle LRC or submits the port idle LRC. Starting an LRC writes context tail, flushes memory, writes HWSP, configures ring mode/MSI-X, writes descriptor low/high, and loads execlist control. Destroy is asynchronous on `system_dfl_wq` and removes active links before common queue fini.

## State and persistence behavior
Port state persists per hardware engine with active lists, last software context id, current running queue, fail timer, and idle LRC. Queue backend state stores the DRM scheduler, entity, port pointer, active priority, active link, and destroy work.

## Dependencies, risks, and test signals
Dependencies include DRM scheduler, MMIO registers, LRC layout, ring ops, HWSP BOs, engine IRQ locking, MSI-X capability, and exec queue common code. Risks include NIY kill/suspend/reset/active ops, interrupt race noted by TODO, timer fallback behavior, context-id wrap, async destroy ordering, and missing GuC feature parity. Test signals include force-execlist boot, job submission/completion, priority ordering, timer fallback, queue destroy under load, MSI-X/non-MSI-X interrupts, compute RCU mode programming, and lockdep on port lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.h

## Purpose
`xe_execlist.h` declares the legacy execlist backend interface and a lock assertion helper.

## Important APIs, types, and functions
The header includes execlist types, declares `xe_execlist_init()`, `xe_execlist_port_create()`, and `xe_execlist_port_destroy()`, and defines `xe_execlist_port_assert_held(port)` as a lockdep assertion on the port spinlock.

## Control flow and integration points
There is no control flow beyond the lock assertion macro. GT initialization uses `xe_execlist_init()` when GuC submission is disabled; hardware engine setup/teardown uses port create/destroy.

## State and persistence behavior
The header owns no state. The implementation allocates per-engine ports and per-queue execlist backend state.

## Dependencies, risks, and test signals
Dependencies are execlist type definitions, GT/device declarations, and lockdep. Risks are callers invoking port internals without holding the lock or failing to skip execlist init when GuC is enabled. Test signals are force-execlist builds, backend init on GuC-disabled platforms, and lockdep coverage for active-list manipulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist_types.h

## Purpose
`xe_execlist_types.h` defines the data structures for the execlist submission backend.

## Important APIs, types, and functions
`struct xe_execlist_port` stores the associated hardware engine, spinlock, per-priority active lists, last software context id, currently running execlist queue, fallback IRQ timer, and idle LRC. `struct xe_execlist_exec_queue` stores the owning common exec queue, DRM GPU scheduler, scheduler entity, port pointer, first-run flag, asynchronous destroy work, active priority, and active-list link.

## Control flow and integration points
There is no executable code. The structures are manipulated by `xe_execlist.c` and referenced through `q->execlist` and `hwe->exl_port`.

## State and persistence behavior
Port state persists while the hardware engine exists. Backend queue state persists from queue init until asynchronous destroy/fini. Active-list links and priorities are protected by the port spinlock.

## Dependencies, risks, and test signals
Dependencies include Linux list/spinlock/workqueue, DRM scheduler types via exec queue types, and hardware engine declarations. Risks include active-link lifetime races, timer firing during destroy, and scheduler entity cleanup ordering. Test signals include queue lifecycle stress, active priority changes, interrupt/fallback timer behavior, and KASAN/lockdep under destroy races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.c

## Purpose
`xe_force_wake.c` manages GT forcewake domains. It initializes domain register mappings, reference-counts wake requests, programs wake/sleep controls, waits for acknowledgments, tracks awake domains, and provides domain names for diagnostics.

## Important APIs, types, and functions
Initialization functions are `xe_force_wake_init_gt()` and `xe_force_wake_init_engines()`. Core operations are `xe_force_wake_get()` and `xe_force_wake_put()`. Helpers include domain initialization, MMIO control/wait paths, wake/sleep wrappers, and `xe_force_wake_domain_to_str()`.

## Control flow and integration points
GT initialization always creates a GT domain, selecting MTL ack registers for graphics version 12.70+. Engine initialization adds render, VDBOX, VEBOX, and GSC domains based on GT type and engine mask. Get asserts a single domain bit or all-domains request, increments refs under spinlock, sends wake for domains transitioning from zero, waits for ack, records awake domains, and rolls back failed acks. Put decrements refs, sends sleep for domains reaching zero, waits for ack, and clears awake bits. SR-IOV VFs skip MMIO programming and waits.

## State and persistence behavior
`struct xe_force_wake` persists per GT. It stores initialized and awake masks plus per-domain refcounts/register fields. References returned by get must be put exactly once; scope classes in the header automate this for common flows.

## Dependencies, risks, and test signals
Dependencies include GT registers, MMIO wait/write helpers, SR-IOV mode, GT logging, and forcewake type masks. Risks include refcount imbalance, wake ack timeouts, `0xffffffff` MMIO unreliability, misuse of `XE_FORCEWAKE_ALL`, and skipped VF behavior hiding register access bugs. Test signals include forcewake get/put nesting, timeout/error injection, render/media/GSC domain coverage, SR-IOV VF paths, runtime PM interactions, and lockdep/irq-safe usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.h

## Purpose
`xe_force_wake.h` declares forcewake initialization and reference APIs, iteration helpers, assertions, and scoped cleanup classes.

## Important APIs, types, and functions
Exports include `xe_force_wake_init_gt()`, `xe_force_wake_init_engines()`, `xe_force_wake_get()`, `xe_force_wake_put()`, and `xe_force_wake_domain_to_str()`. Macros iterate initialized domains, query a domain refcount, assert a domain is awake, check whether an opaque forcewake reference includes a domain, and create scope-bound forcewake acquisition/release classes.

## Control flow and integration points
Inline control flow implements domain iteration by bitmask, `xe_force_wake_assert_held()`, and cleanup-on-scope-exit through `DEFINE_CLASS`. Callers use `CLASS(xe_force_wake, ...)`, `xe_with_force_wake()`, or `xe_force_wake_release_only` around MMIO sections that require powered domains.

## State and persistence behavior
The header owns no state but controls forcewake reference lifetime. The opaque `struct xe_force_wake_ref` carries the `fw` pointer and acquired domain mask so cleanup can put only acquired domains.

## Dependencies, risks, and test signals
Dependencies include Xe assertions and forcewake types. Risks include using assertions with multiple domains, losing the returned domain mask after partial wake failure, and cleanup class misuse with mismatched lifetimes. Test signals are build coverage for scoped guards, lockdep assertions on MMIO callers, and forcewake leak/timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake_types.h

## Purpose
`xe_force_wake_types.h` defines forcewake domain identifiers, bitmasks, and persistent state structures for GT power-domain wake management.

## Important APIs, types, and functions
`enum xe_force_wake_domain_id` enumerates GT, render, generic media, VDBOX0-7, VEBOX0-3, GSC, and count. `enum xe_force_wake_domains` maps these IDs to bitmasks and defines `XE_FORCEWAKE_ALL` as a sentinel bit. `struct xe_force_wake_domain` stores domain id, control and ack registers, wake value, mask, and refcount. `struct xe_force_wake` stores the owning GT, spinlock, awake mask, initialized mask, and domain array.

## Control flow and integration points
The header has no executable code. `xe_force_wake.c` fills domains during GT/engine init and mutates refs/awake masks during get/put. Other subsystems rely on these masks to keep render/media/GSC registers accessible.

## State and persistence behavior
Per-domain register metadata is immutable after initialization. Refcounts and awake masks are mutable under `fw->lock` and persist across nested callers until all references are released.

## Dependencies, risks, and test signals
Dependencies include Linux types, register definitions, and GT ownership. Risks include enum order mismatches with bitmask macros, adding domains without increasing arrays, and using `XE_FORCEWAKE_ALL` as a real domain id. Test signals include domain initialization on GT/media/GSC engine masks, nested forcewake reference tests, and compile-time coverage of domain-to-string mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gen_wa_oob.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gen_wa_oob.c

## Purpose
`xe_gen_wa_oob.c` is a build-time generator for Xe workaround out-of-band rule files. It converts a textual rules file into generated C source and header fragments containing rule tables and enum identifiers.

## Important APIs, types, and functions
Important helpers are `print_usage()`, `print_parse_error()`, `strip()`, `parse()`, `xbasename()`, `fn_to_prefix()`, and `main()`. The generator emits a standard SPDX/header guard, enum values prefixed from the output header basename, and C table entries using `XE_RTP_NAME()` and `XE_RTP_RULES()`.

## Control flow and integration points
`main()` expects input rules, generated C source, and generated header paths, derives the enum prefix from the header filename, opens all files, writes the header prologue, invokes `parse()`, then writes the footer on success. The parser skips comments/blank lines, rejects max-length lines, treats leading whitespace as continuation of the previous rule, splits new rules into name and rule expression, emits enum indices for new names, and appends continuation rules with `OR`.

## State and persistence behavior
No runtime driver state exists. Persistent outputs are generated source/header files produced during the build. Parser state is limited to current line number, index, and previous rule name.

## Dependencies, risks, and test signals
Dependencies include GNU/POSIX C library I/O, ctype/string APIs, errno values, and the rule macro vocabulary understood by generated C consumers. Risks include `argc < 3` while accessing `argv[3]` in the initializer, `strip()` underflow for unusual empty lines, malformed continuation handling, and generated syntax errors from unchecked rule expressions. Test signals are build generator execution, malformed-rule tests, continuation-rule tests, line-length tests, generated enum/table compilation, and round-trip changes to `xe_device_wa_oob.rules`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gen_wa_oob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.c

## Purpose
`xe_ggtt.c` implements Xe Global Graphics Translation Table management. It allocates usable GGTT ranges, maps BOs and transformed display layouts, clears mappings to scratch, invalidates GT TLBs, supports SR-IOV VF assignment/save/load, and exposes debug hole/dump helpers.

## Important APIs, types, and functions
Internal types include `xe_ggtt_node`, platform `xe_ggtt_pt_ops`, and `xe_ggtt`. Public operations include `xe_ggtt_alloc()`, `xe_ggtt_init_early()`, `xe_ggtt_init()`, `xe_ggtt_insert_node()`, `xe_ggtt_insert_node_transform()`, `xe_ggtt_node_remove()`, `xe_ggtt_insert_bo_at()`, `xe_ggtt_insert_bo()`, `xe_ggtt_remove_bo()`, `xe_ggtt_largest_hole()`, SR-IOV `assign/save/load`, dump/print helpers, PTE flag encoding, PTE read, and node address/size helpers.

## Control flow and integration points
Early init computes usable GGTT from WOPCM and GSM size, or VF-provisioned base/size, clamps to `GUC_GGTT_TOP`, maps GSM, selects PTE ops including WA `22019338487`, allocates a removal workqueue, initializes `drm_mm`, and marks online. Regular init creates a scratch BO and clears all holes. BO insertion validates placement, takes runtime PM, allocates a node, translates requested ranges relative to `ggtt->start`, inserts into `drm_mm`, writes PTEs from TT SG pages or VRAM resources, and invalidates if requested. Removal clears to scratch if online, removes the node, optionally invalidates, and may defer through a workqueue if runtime PM is inactive.

## State and persistence behavior
Each tile has a persistent GGTT with start/size, online flag, scratch BO, GSM pointer, `drm_mm`, access counter, and removal workqueue. BOs store per-tile `ggtt_node` pointers. VF recovery can shift the base with `WRITE_ONCE` while node offsets remain stable. SR-IOV assignment persists VFID bits in PTEs.

## Dependencies, risks, and test signals
Dependencies include DRM MM, MMIO/GSM mapping, PAT/MOCS cache indices, TTM resources, BO validation, runtime PM, TLB invalidation, WOPCM, SR-IOV VF provisioning, display transform callbacks, and generated workarounds. Risks include off-by-one loops using `end = start + size - 1`, scratch clearing before scratch allocation, access-counter WA thresholds, deferred removal after device offline, 64K VRAM alignment, VF base shifts, and PTE VFID validation. Test signals include KUnit GGTT init, GuC boot allocations, display inherited framebuffer mapping, BO insert/remove stress, suspend/resume remap, GGTT TLB invalidation, SR-IOV save/load/assign, hole reporting, and error-injection on init/insert paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.h

## Purpose
`xe_ggtt.h` declares the public Global Graphics Translation Table API used by BO, display, GuC, migration, debug, and SR-IOV code.

## Important APIs, types, and functions
The header declares allocation, early and regular init, KUnit init, node shift, start/size queries, node insertion and transform insertion, node removal and PTE-size query, BO map/insert/remove helpers, largest-hole query, dump/print helpers, SR-IOV assignment/save/load under `CONFIG_PCI_IOV`, lockdep helper, PTE flag encoding/read, and node address/size accessors.

## Control flow and integration points
There is no executable control flow except a no-op inline `xe_ggtt_might_lock()` when lockdep is disabled. The API integrates tile initialization, BO placement, display GGTT transforms, VF migration, and debugfs-like reporting.

## State and persistence behavior
The header owns no state. The implementation manages per-tile GGTTs, nodes, BO node pointers, scratch mappings, and PTE contents.

## Dependencies, risks, and test signals
Dependencies include GGTT types, DRM printer/exec declarations, Xe BO/tile types, and optional PCI IOV. Risks include callers failing to remove nodes, using node addresses after VF shifts without `xe_ggtt_node_addr()`, and SR-IOV APIs missing in non-IOV builds. Test signals are build coverage across CONFIG_PCI_IOV/LOCKDEP, BO GGTT mapping tests, display transform users, and VF migration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt_types.h

## Purpose
`xe_ggtt_types.h` provides forward declarations and callback typedefs for GGTT users without exposing the private `struct xe_ggtt` layout.

## Important APIs, types, and functions
It forward-declares `struct xe_ggtt` and `struct xe_ggtt_node`. `xe_ggtt_set_pte_fn` is the function signature for writing one GGTT PTE. `xe_ggtt_transform_cb` is a display/custom mapping callback receiving the GGTT, node, PTE flags, PTE writer, and caller argument.

## Control flow and integration points
There is no control flow. Transform callbacks are passed to `xe_ggtt_insert_node_transform()` to populate non-linear mappings such as display rotations or layout-specific views.

## State and persistence behavior
No state is owned here. Callback users mutate PTEs inside an allocated GGTT node owned by the implementation.

## Dependencies, risks, and test signals
Dependencies are Linux integer types and DRM MM type visibility. Risks include transform callbacks writing outside node bounds or using wrong PTE flags. Test signals include display transform mapping tests, GGTT PTE readback, and compile coverage of callback users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.c

## Purpose
`xe_gpu_scheduler.c` wraps the DRM GPU scheduler with Xe-specific in-band message processing. It lets backends queue messages onto the scheduler submit workqueue while respecting scheduler stopped state.

## Important APIs, types, and functions
`xe_sched_init()` initializes the embedded DRM scheduler, Xe backend ops, message lock/list, and message work item. `xe_sched_fini()` stops submission and finalizes DRM scheduler state. `xe_sched_submission_start()`, `_stop()`, and `_resume_tdr()` control scheduler execution. `xe_sched_add_msg()`, `_locked()`, and `_head()` enqueue backend messages. Internal helpers process queued messages one at a time on `base.submit_wq`.

## Control flow and integration points
Adding a message takes `msg_lock`, appends or prepends the message, and queues processing if the scheduler is not stopped. Work exits immediately if stopped, otherwise removes the first message, calls `sched->ops->process_msg(msg)`, then schedules itself again if more messages remain. Start begins the DRM scheduler workqueue and queues message work; stop stops the scheduler queue and cancels message work synchronously.

## State and persistence behavior
`struct xe_gpu_scheduler` owns the DRM scheduler base, message list, spinlock, backend ops pointer, and work item. Message ownership is backend-defined; `process_msg` is responsible for freeing dynamically allocated messages.

## Dependencies, risks, and test signals
Dependencies include DRM GPU scheduler semantics, backend ops, workqueues, and Xe scheduler types. Risks include lost messages during stop/start, process_msg blocking submit work too long, callers using locked add without holding `msg_lock`, and message lifetime leaks. Test signals include GuC/backend message ordering, start/stop/resume TDR, stopped scheduler no-processing behavior, lockdep for locked add paths, and teardown with pending messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.h

## Purpose
`xe_gpu_scheduler.h` declares Xe scheduler wrapper operations and inline helpers around DRM scheduler behavior.

## Important APIs, types, and functions
It declares init/fini, submission start/stop, TDR resume, and message add APIs. Inline helpers lock/unlock the message list, stop scheduler execution, queue immediate TDR, resubmit pending jobs, invalidate a job, find the first unsignaled pending job, initialize a scheduler entity, and alias entity fini to DRM scheduler fini.

## Control flow and integration points
Inline `xe_sched_resubmit_jobs()` walks DRM pending jobs, preserving replay restore behavior: once any pending job requires replay restore or an unsignaled job is found, it calls the backend `run_job()` on jobs in order. `xe_sched_first_pending_job()` returns the first pending job whose scheduler fence is not signaled. Backends use these helpers during reset, timeout, and recovery paths.

## State and persistence behavior
The header owns no state. It operates on `struct xe_gpu_scheduler`, DRM scheduler pending-job lists, and `struct xe_sched_job` flags such as `restore_replay`.

## Dependencies, risks, and test signals
Dependencies are Xe scheduler types, scheduler job conversion, and DRM scheduler APIs. Risks include resubmitting already-signaled jobs incorrectly, backend `run_job()` side effects during replay, and entity casting assumptions. Test signals include timeout recovery, job replay/restore, pending job iteration, scheduler entity lifecycle, and lockdep around message helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler_types.h

## Purpose
`xe_gpu_scheduler_types.h` defines the Xe scheduler extension types layered on top of DRM GPU scheduler.

## Important APIs, types, and functions
`struct xe_sched_msg` is an in-band backend-defined message with list link, opaque private data, and opcode. `struct xe_sched_backend_ops` currently provides `process_msg()`, which may block and owns message cleanup policy. `struct xe_gpu_scheduler` embeds `struct drm_gpu_scheduler`, backend ops, message list, message spinlock, and work item. It aliases `xe_sched_entity` and `xe_sched_policy` to DRM scheduler types.

## Control flow and integration points
There is no executable code. `xe_gpu_scheduler.c` uses these structures to initialize scheduler state and process queued backend messages on the submit workqueue. GuC or other submission backends can embed or extend messages through private data/opcodes.

## State and persistence behavior
Scheduler objects persist for backend scheduler lifetime. Message nodes persist until `process_msg()` handles and frees or otherwise consumes them.

## Dependencies, risks, and test signals
Dependencies include DRM GPU scheduler and Linux list/work types via that include. Risks include backend-private message lifetime ambiguity, opcode namespace conflicts, and blocking `process_msg()` delaying GPU submission work. Test signals include backend message queue tests, scheduler init/fini under pending messages, and timeout/recovery paths using the embedded DRM scheduler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler_types.h -->
