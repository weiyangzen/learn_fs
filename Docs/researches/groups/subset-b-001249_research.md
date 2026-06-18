# subset-b-001249 research

This grouped report covers DIBS class/loopback support, legacy DIO bus plumbing, and the Linux dma-buf core, fence, reservation, heap, and selftest sources under the assigned Ceph-client source mirror. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dibs/Kconfig

Purpose: defines the build-time feature switches for Direct Internal Buffer Sharing. `DIBS` enables the core abstraction layer used by DIBS devices and clients such as SMC, while `DIBS_LO` adds a software loopback device for same-OS testing without hardware fabric support.

Important APIs/types/functions: this is Kconfig-only. `config DIBS` is a tristate with module name `dibs`; `config DIBS_LO` is a bool depending on `DIBS`, so loopback code is compiled into the DIBS object only when the core is enabled.

Control flow: no runtime control flow. The selections drive `drivers/dibs/Makefile`, where `dibs_main.o` is always part of the DIBS object and `dibs_loopback.o` is added when `CONFIG_DIBS_LO` is enabled.

State and persistence behavior: no runtime state. Configuration state persists in the kernel `.config` and determines whether the DIBS class and optional loopback provider are present.

Dependencies and integration points: integrates with Linux Kconfig and the DIBS client-facing headers in `include/linux/dibs.h`. `DIBS_LO` is a test/convenience provider, not a hardware transport.

Risks and test signals: enabling `DIBS_LO` creates an in-kernel emulated sharing device, so test kernels may expose behavior not representative of hardware. Build signals are `CONFIG_DIBS=m/y` producing the DIBS class, and `CONFIG_DIBS_LO=y` adding the `lo` DIBS device during DIBS init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dibs/Makefile

Purpose: builds the DIBS class object and conditionally includes the loopback implementation.

Important APIs/types/functions: declares `dibs-y += dibs_main.o`, `obj-$(CONFIG_DIBS) += dibs.o`, and `dibs-$(CONFIG_DIBS_LO) += dibs_loopback.o`.

Control flow: no runtime flow. Kbuild links `dibs_main.o` into `dibs.o` whenever `CONFIG_DIBS` is enabled, and links `dibs_loopback.o` into the same module/built-in object only when `CONFIG_DIBS_LO` is enabled.

State and persistence behavior: none beyond build artifacts.

Dependencies and integration points: follows the Kconfig dependency from `drivers/dibs/Kconfig`; the resulting object exports DIBS device/client APIs for other kernel users.

Risks and test signals: a mismatch between Kconfig and Makefile would either omit loopback symbols or build unused code. Test signal is successful allmodconfig/module builds in both loopback-enabled and disabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/dibs_loopback.c -->
# sources/distributed-fs/ceph-client/drivers/dibs/dibs_loopback.c

Purpose: implements the software DIBS loopback device named `lo`, providing direct-memory-buffer registration, token lookup, attach/detach, memory copy, and optional synthetic interrupt forwarding for same-OS DIBS client testing.

Important APIs/types/functions: implements `dibs_loopback_init()`/`dibs_loopback_exit()` around `dibs_lo_dev_probe()` and `dibs_lo_dev_remove()`. The `dibs_lo_ops` table supplies DIBS device callbacks: `get_fabric_id`, `query_remote_gid`, `max_dmbs`, `register_dmb`, `unregister_dmb`, `move_data`, `support_mmapped_rdmb`, `attach_dmb`, and `detach_dmb`. DMBs are represented by `struct dibs_lo_dmb_node` from the header, stored in a hash table by random token and indexed by an `sba_idx` bitmap.

Control flow: probe allocates `struct dibs_lo_dev` and a core `struct dibs_dev`, initializes hash/table/waitqueue state, generates a UUID, installs loopback ops, names the device `lo`, and calls `dibs_dev_add()`. Registering a DMB reserves a free SBA bit, allocates a node and zeroed folio, generates a collision-free random token under the hash write lock, inserts it, increments `dmb_cnt`, fills the caller's `struct dibs_dmb`, and records the owning client id in the core device array. Attach finds a token under the hash read lock, increments the node refcount if nonzero, and returns the same CPU/DMA/length metadata. Unregister/detach drop the refcount and free the node when the last reference leaves. `move_data()` finds the remote memory token, copies the supplied bytes into `cpu_addr + offset`, and, when `sf` is set, computes a signal mask and calls the registered client's `handle_irq()`.

State and persistence behavior: global `lo_dev` tracks the singleton loopback provider. Per-DMB state includes token, length, SBA index, CPU address, invalid DMA address, and refcount. State is memory-resident only. Removal calls `dibs_dev_del()` and waits until `dmb_cnt` reaches zero before freeing the loopback device.

Dependencies and integration points: depends on core DIBS allocation/registration from `dibs_main.c`, `include/linux/dibs.h` device and client contracts, folio allocation, Linux hashtable/rwlock/refcount primitives, and DIBS client interrupt callbacks. It advertises `DIBS_LOOPBACK_FABRIC` and validates remote GID by equality with local GID.

Risks and test signals: `move_data()` does not bounds-check `offset + size` against the DMB length in this file, so callers must validate ranges. Token lookup drops the hash read lock before `refcount_inc_not_zero()` in attach, creating a narrow lifetime-sensitive path mitigated only by refcount semantics and removal ordering. Exit can wait indefinitely if users keep DMB refs. Test signals include loopback device creation, DMB register/attach/detach/unregister cycles, collision-free token lookup, fallback on allocation failure, synthetic IRQ delivery when `sf` is true, and teardown waiting until all DMBs are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/dibs_loopback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/dibs_loopback.h -->
# sources/distributed-fs/ceph-client/drivers/dibs/dibs_loopback.h

Purpose: declares the loopback DIBS provider's private state and init/exit hooks, with no-op stubs when loopback support is disabled.

Important APIs/types/functions: defines `DIBS_LO_DMBS_HASH_BITS`, `DIBS_LO_MAX_DMBS`, `struct dibs_lo_dmb_node`, and `struct dibs_lo_dev`. The node tracks token, buffer length, SBA index, CPU/DMA addresses, and refcount. The device tracks the public `struct dibs_dev`, atomic DMB count, hash lock/table, SBA bitmap, and release waitqueue.

Control flow: no direct runtime flow beyond conditional declarations. With `CONFIG_DIBS_LO`, real `dibs_loopback_init()` and `dibs_loopback_exit()` are provided by `dibs_loopback.c`; otherwise inline stubs return success/do nothing so `dibs_main.c` can call them unconditionally.

State and persistence behavior: describes in-memory loopback state only. The hash table and bitmap persist for the lifetime of the singleton loopback device.

Dependencies and integration points: includes DIBS public definitions, hashtable, spinlock, waitqueue, and Linux type headers. It forms the private interface between `dibs_main.c` and the loopback provider.

Risks and test signals: the hard-coded `DIBS_LO_MAX_DMBS` limit defines memory and bitmap sizing; raising it affects allocation and lookup behavior. Test signals are clean builds with and without `CONFIG_DIBS_LO`, and correct no-op behavior in non-loopback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/dibs_loopback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/dibs_main.c -->
# sources/distributed-fs/ceph-client/drivers/dibs/dibs_main.c

Purpose: implements the DIBS class module: client registration, device allocation/add/remove, sysfs attributes, and forwarding of DIBS device events to registered clients.

Important APIs/types/functions: exports `dibs_register_client()`, `dibs_unregister_client()`, `dibs_dev_alloc()`, `dibs_dev_add()`, and `dibs_dev_del()`. It owns the `dibs` class, `clients[MAX_DIBS_CLIENTS]`, `max_client`, `clients_lock`, and a mutex-protected global DIBS device list. Sysfs exposes `gid` and `fabric_id`.

Control flow: init registers the class and then initializes optional loopback. Client registration reserves the first free client id under `clients_lock`, then while the device list mutex is held calls the client's `add_dev()` for every existing device and installs the client into each device's `subs[]` forwarding slot. Unregistration refuses to remove a client with registered DMBs by scanning each device's `dmb_clientid_arr`, clears forwarding slots, calls `del_dev()`, and clears client private state. Device add initializes the device lock and DMB owner array, adds the device, creates sysfs attributes, calls all existing client `add_dev()` callbacks, then adds the device to the global list. Device delete removes sysfs, clears subscribers, calls client `del_dev()`, removes the list node, deletes the device, and frees the DMB owner array.

State and persistence behavior: DIBS device and client state is kernel-resident. `struct dibs_dev` lifetime is tied to `device_initialize()`/`put_device()` and `dibs_dev_release()`. The client array is a fast id-to-client map and persists until module exit. Sysfs attributes reflect the current UUID and fabric id callback.

Dependencies and integration points: depends on Linux device/class/sysfs APIs and public DIBS structures from `include/linux/dibs.h`. Loopback is integrated through `dibs_loopback_init/exit()`. DIBS clients must implement `add_dev`, `del_dev`, and interrupt/event handlers expected by the device subscriber table.

Risks and test signals: client `add_dev()` return values are ignored, so partial client-device setup failures must be handled internally by clients. `max_client` is only decremented by one on last-id removal and may stay above the actual highest occupied id after sparse removals. Unregister scans DMB ownership under each device lock and fails with `-EBUSY` if any DMB remains. Test signals include sysfs `gid`/`fabric_id`, correct client id allocation/reuse, rejection of unregister with active DMBs, balanced add/del callbacks across existing and future devices, and clean class/loopback teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dibs/dibs_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dio/Makefile

Purpose: builds the legacy DIO bus support objects into the kernel.

Important APIs/types/functions: declares `obj-y := dio.o dio-driver.o dio-sysfs.o`.

Control flow: no runtime flow. The three objects are always linked when this directory participates in the architecture build.

State and persistence behavior: none beyond build output.

Dependencies and integration points: integrates bus enumeration (`dio.o`), driver-core registration (`dio-driver.o`), and sysfs attributes (`dio-sysfs.o`) into one built-in subsystem for HP300/m68k DIO support.

Risks and test signals: because this is `obj-y`, architecture Makefiles/Kconfig must gate directory inclusion. Test signal is successful HP300/m68k builds with all three object files present and no missing DIO symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dio/dio-driver.c -->
# sources/distributed-fs/ceph-client/drivers/dio/dio-driver.c

Purpose: connects DIO devices to the Linux driver core by registering the `dio` bus, matching DIO ids, and exposing registration helpers for DIO drivers.

Important APIs/types/functions: exports `dio_register_driver()`, `dio_unregister_driver()`, and `dio_bus_type`. Internal helpers are `dio_match_device()`, `dio_device_probe()`, and `dio_bus_match()`.

Control flow: `postcore_initcall(dio_driver_init)` registers `dio_bus_type`. Driver registration fills common `struct device_driver` fields and calls `driver_register()`. Bus matching checks a driver's id table against a DIO device. Matching treats `DIO_WILDCARD` as universal, compares full encoded ids when the primary id needs a secondary id, and otherwise compares only the primary byte. Probe re-runs the match, calls the driver's `probe()` callback, and records the driver on success.

State and persistence behavior: bus type registration persists for the kernel lifetime. Each successful probe stores the owning `struct dio_driver *` in the `struct dio_dev`; unregister relies on the driver core to unwind device bindings.

Dependencies and integration points: depends on `linux/dio.h` conversion macros and driver/device types. It is used by DIO bus enumeration in `dio.c` and any DIO device drivers.

Risks and test signals: probe treats any nonnegative driver `probe()` result as success and normalizes it to zero, so drivers must return negative values on failure. Matching depends on correct secondary-id encoding. Test signals include bus registration before DIO device enumeration, wildcard and secondary-id match behavior, driver bind/unbind callbacks, and exported symbol availability to DIO drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dio/dio-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dio/dio-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/dio/dio-sysfs.c

Purpose: publishes read-only sysfs attributes for each enumerated DIO device.

Important APIs/types/functions: defines device attributes `id`, `ipl`, `secid`, `name`, and `resource`, and exports the local helper `dio_create_sysfs_dev_files()` to create them for a `struct dio_dev`.

Control flow: each show function converts the generic device to `struct dio_dev` and formats one field. `resource` prints start, end, and flags via DIO resource helpers. `dio_create_sysfs_dev_files()` creates attributes sequentially and stops on the first error.

State and persistence behavior: no independent state. Sysfs files reflect fields stored in the `struct dio_dev` populated by bus scan.

Dependencies and integration points: depends on Linux device attributes and DIO helper macros. Called from `dio_init()` after `device_register()` succeeds.

Risks and test signals: uses `sprintf()` instead of `sysfs_emit()`, though fixed-size simple fields make overflow unlikely. There is no rollback for earlier files if a later `device_create_file()` fails. Test signals are presence and content of `/sys/bus/dio/devices/*/{id,ipl,secid,name,resource}` after enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dio/dio-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dio/dio.c -->
# sources/distributed-fs/ceph-client/drivers/dio/dio.c

Purpose: scans HP300 DIO/DIO-II address spaces, identifies installed boards, registers them as DIO devices, and provides early select-code lookup helpers.

Important APIs/types/functions: defines global `struct dio_bus dio_bus`, `dio_find()`, `dio_scodetophysaddr()`, and `dio_init()`. It includes a built-in id-to-name table under local `CONFIG_DIO_CONSTANTS`.

Control flow: `dio_find()` is an early console helper that scans select codes, skips holes, maps DIO-II pages when needed, reads primary and optional secondary ids with fault-safe access, and returns the matching select code or `-1`. `dio_init()` runs as `subsys_initcall`, exits unless `MACH_IS_HP300`, registers the DIO bus device, requests DIO memory resource ranges, then scans all select codes. For each present board it allocates `struct dio_dev`, fills bus/device/resource/id/interrupt/name fields, unmaps DIO-II temporary mappings, registers the device, and creates sysfs files.

State and persistence behavior: `dio_bus` holds resource ranges and the bus device. Each discovered `struct dio_dev` persists as a registered device until driver core cleanup; `dio_dev_release()` frees it. There is no dynamic rescan/removal path in this file.

Dependencies and integration points: depends on HP300/m68k machine macros, DIO address/id macros, `copy_from_kernel_nofault()`, `ioremap()`/`iounmap()`, iomem resources, and `dio_bus_type` from `dio-driver.c`. The sysfs helper from `dio-sysfs.c` is called for each device.

Risks and test signals: device allocation failure aborts scanning with `-ENOMEM`, potentially after some devices/resources are registered. Resource requests are not checked for failure. The name table is retained rather than init-discarded. Test signals include boot-time scan logs on HP300, correct select-code physical addresses, sysfs resource ranges, early console `dio_find()` returning known hardware, and graceful no-op on non-HP300 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dio/dio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/Kconfig

Purpose: defines the dma-buf subsystem feature switches for explicit sync files, software sync validation, userspace dma-buf creation, debug checks, selftests, and userland memory heaps.

Important APIs/types/functions: Kconfig symbols include `SYNC_FILE`, `SW_SYNC`, `UDMABUF`, `DMABUF_DEBUG`, `DMABUF_SELFTESTS`, and menuconfig `DMABUF_HEAPS`. `SYNC_FILE` and `DMABUF_HEAPS` select `DMA_SHARED_BUFFER`; heap configuration is delegated to `drivers/dma-buf/heaps/Kconfig`.

Control flow: no runtime control flow. The symbols determine which objects in `drivers/dma-buf/Makefile` are compiled and which code paths are enabled, including sync-file ioctls, sw_sync debugfs test driver, dma-buf importer debug wrapping, and heap char devices.

State and persistence behavior: build-time configuration only. `DMABUF_DEBUG` defaults to y for debug kernels and changes runtime validation behavior in `dma-buf.c`.

Dependencies and integration points: integrates with the Linux dma-buf core, sync_file framework, debugfs, memfd creation, MMU support, and heap drivers.

Risks and test signals: enabling `SW_SYNC` is explicitly test/debug oriented and can deadlock kernel drivers if misused from userspace. Test signals are correct object inclusion under each symbol combination, `/dev/dma_heap/*` nodes when heaps are enabled, sync-file ioctls only when `SYNC_FILE` is enabled, and selftest module availability under `DMABUF_SELFTESTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/Makefile

Purpose: wires the dma-buf core, optional heap/sync/misc drivers, and selftest objects into Kbuild.

Important APIs/types/functions: always builds `dma-buf.o`, `dma-fence.o`, `dma-fence-array.o`, `dma-fence-chain.o`, `dma-fence-unwrap.o`, `dma-resv.o`, and `dma-buf-mapping.o`. Optional objects include `dma-heap.o`, `heaps/`, `sync_file.o`, `sw_sync.o`, `sync_debug.o`, `udmabuf.o`, and the composite `dmabuf_selftests.o`.

Control flow: no runtime control flow. Kconfig symbols select which translation units are linked. The selftest object aggregates `selftest.o`, `st-dma-fence.o`, `st-dma-fence-chain.o`, `st-dma-fence-unwrap.o`, and `st-dma-resv.o`.

State and persistence behavior: none beyond build products.

Dependencies and integration points: connects core dma-buf primitives to optional heap and synchronization facilities. The always-built core objects provide exported symbols consumed by graphics, media, accelerator, and memory-sharing drivers.

Risks and test signals: core object ordering matters only through link inclusion, not initialization order, which is handled by initcalls in the source files. Test signals are symbol availability for namespace exports and successful builds across heap/sync/selftest combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-buf-mapping.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-buf-mapping.c

Purpose: provides exporter helpers for creating and freeing dma-buf scatter-gather tables from physical MMIO ranges, including PCI P2PDMA and IOVA-backed mappings.

Important APIs/types/functions: exports `dma_buf_phys_vec_to_sgt()` and `dma_buf_free_sgt()` in the `DMA_BUF` namespace. Internal helpers `fill_sg_entry()` and `calc_sg_nents()` split large DMA spans into scatterlist entries compatible with `sg_dma_len`.

Control flow: `dma_buf_phys_vec_to_sgt()` asserts the dma-buf reservation lock, validates attachment and P2P provider, allocates a private `struct dma_buf_dma`, chooses mapping mode via `pci_p2pdma_map_type()`, optionally allocates `dma_iova_state`, allocates an sg table, maps each physical vector either to P2P bus addresses, DMA API physical mappings, or IOVA links, and fills only DMA address/length fields in the returned scatterlist. For IOVA mappings it syncs the whole IOVA range and emits one logical DMA address span. On errors it unmaps any partial work and frees state. `dma_buf_free_sgt()` performs the corresponding IOVA destroy or `dma_unmap_phys()` loop, frees the sg table, and releases wrapper state.

State and persistence behavior: mapping state persists in the private object containing the returned `sg_table`; callers must release it through `dma_buf_free_sgt()`. `orig_nents` is set to zero to signal that there is no CPU page list.

Dependencies and integration points: depends on dma-resv locking, PCI P2PDMA routing, DMA IOVA helpers, DMA mapping APIs, `struct phys_vec`, and dma-buf attachment semantics. Intended for exporters of MMIO/P2P memory, not normal page-backed buffers.

Risks and test signals: callers must hold the reservation lock and must not treat returned scatterlist entries as page-backed. Alignment is documented as page-sized; misuse by importers can break because `sg_page` is deliberately NULL. Error cleanup has separate paths for IOVA and non-IOVA mappings. Test signals include P2P bus-address mapping, host-bridge IOVA mapping, non-IOVA `dma_map_phys()` fallback, correct splitting above `UINT_MAX`, and balanced unmap/free under injected mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-buf-mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-buf.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-buf.c

Purpose: implements the central dma-buf framework for exporting buffers as file descriptors, attaching devices, mapping/unmapping DMA access, mmap/vmap CPU access, implicit fence polling, sync-file import/export, debugfs visibility, and global dma-buf iteration.

Important APIs/types/functions: exports `dma_buf_export()`, `dma_buf_fd()`, `dma_buf_get()`, `dma_buf_put()`, `dma_buf_dynamic_attach()`, `dma_buf_attach()`, `dma_buf_detach()`, `dma_buf_pin()`, `dma_buf_unpin()`, `dma_buf_map_attachment()`, unlocked map/unmap/vmap variants, `dma_buf_invalidate_mappings()`, `dma_buf_attach_revocable()`, `dma_buf_begin_cpu_access()`, `dma_buf_end_cpu_access()`, `dma_buf_mmap()`, `dma_buf_vmap()`, `dma_buf_vunmap()`, and global `dma_buf_iter_begin()/next()`. It owns `dma_buf_fops`, the pseudo `dmabuf` filesystem, global `dmabuf_list`, and optional debugfs `dma_buf/bufinfo`.

Control flow: init mounts the pseudo filesystem and creates debugfs. Export validates mandatory ops, pins the exporter module, creates an anonymous pseudo file/inode, allocates `struct dma_buf` plus an internal `dma_resv` when the exporter did not provide one, initializes poll/vmap/attachment state, binds the file/dentry to the dma-buf, and adds it to the global list. FD creation installs the file with requested flags; get/put wrap `fget()`/`fput()`. Attach creates an attachment, optionally calls exporter `attach`, then inserts it into the attachment list under the reservation lock. Mapping requires the reservation lock, optionally pins static attachments, calls exporter `map_dma_buf`, waits for kernel-usage fences for static importers, optionally wraps the sg table for debug, and returns it; unmap unwraps, calls exporter unmap, and unpins. CPU begin calls exporter coherency hook, then waits on implicit fences; CPU end calls exporter end hook. Poll installs fence callbacks for read/write readiness and holds a file reference until callbacks fire. Sync-file ioctls export a singleton reservation fence or import/unwrap fences into the reservation object.

State and persistence behavior: each dma-buf persists through file references and releases through dentry `d_release`, which calls exporter `release`, finalizes an internal reservation object, warns on live attachments, drops the owner module, and frees name/object memory. Vmap state is cached in `vmap_ptr` with `vmapping_counter` under the reservation lock. Poll callback state is kept in `cb_in/cb_out`. The global list supports debugfs and iteration with careful file ref acquisition because the list mutex does not protect file refcounts.

Dependencies and integration points: depends on file/inode/pseudo-fs APIs, dma-resv/fence/unwrap, optional sync_file, debugfs, tracepoints, Linux DMA and VM APIs, and exporter-provided `struct dma_buf_ops`. It is the integration point for DRM, media, accelerator, heap, and userspace memory-sharing drivers.

Risks and test signals: the reservation-lock convention is strict: several importer APIs require the lock, while attach/detach/export/get/put and unlocked wrappers must not be called with it held. Poll callback file-reference balancing is guarded by release-time BUGs. Debug sg wrapping catches importers that peek at pages, but only under `DMABUF_DEBUG`. Static importers block in map waiting on fences; dynamic importers must handle synchronization and invalidation correctly. Test signals include fd export/import, mmap bounds checks, vmap reference counting, poll readiness for read/write fences, sync-file export/import, attachment invalidation callbacks, debugfs object/attachment listing, and clean release with no live vmap or callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-array.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-array.c

Purpose: implements a dma-fence container that represents a set of fences and signals either when all member fences signal or, optionally, when any member signals.

Important APIs/types/functions: exports `dma_fence_array_ops`, `dma_fence_array_alloc()`, `dma_fence_array_init()`, `dma_fence_array_create()`, `dma_fence_match_context()`, `dma_fence_array_first()`, and `dma_fence_array_next()`. Internal callbacks track pending fence count and error propagation.

Control flow: init initializes the base fence with array ops, an irq_work item, the pending counter, and the supplied fence array. `enable_signaling()` registers a callback on each contained fence and takes extra references on the array so callbacks cannot outlive the container. Each member callback records the first nonzero error, decrements `num_pending`, and queues irq_work when the array is complete. The irq_work clears the pending-error sentinel, signals the base fence, and drops the held reference. The signaled op either checks `num_pending` after software signaling is enabled or scans member signaled state before callbacks are armed.

State and persistence behavior: the array owns the supplied `struct dma_fence **fences` array and drops each member fence plus the array allocation in release. `base.error` temporarily carries `PENDING_ERROR` until real error propagation or completion.

Dependencies and integration points: depends on dma-fence core, irq_work, lockdep class separation, and fence-array public helpers used by reservation singleton export, fence unwrap/merge, and sync-file composition.

Risks and test signals: array containers must not contain other containers; the code warns and expects callers to flatten first to avoid recursion and stack overflow. Callback registration races are handled, but error propagation depends on members setting `f->error` before signaling. Test signals include all-vs-any completion semantics, first-error propagation, no premature free with outstanding callbacks, deadline forwarding to all members, and correct iteration through `first/next`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-chain.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-chain.c

Purpose: implements dma-fence chains, a timeline-like container where each node wraps a current fence and links to a previous fence/chain, allowing ordered waiting and sequence-number lookup without large arrays.

Important APIs/types/functions: exports `dma_fence_chain_walk()`, `dma_fence_chain_find_seqno()`, `dma_fence_chain_ops`, and `dma_fence_chain_init()`. Internal helpers include RCU-safe previous-node lookup, chain callback rearming through irq_work, and release-time recursive unlink avoidance.

Control flow: `dma_fence_chain_init()` stores references to previous and current fences, chooses a context/sequence number, initializes the base fence with 64-bit seqno support, and assigns a separate lockdep class. `enable_signaling()` walks the chain and arms a callback on the first unsignaled contained fence; the callback queues irq_work, which tries to rearm on the next unsignaled fence or signals the chain base when all are complete. `dma_fence_chain_walk()` advances to the previous link and opportunistically garbage-collects already signaled chain nodes by replacing `prev`. `find_seqno()` advances from a chain head to the node covering a requested seqno.

State and persistence behavior: each chain node owns references to `prev` and `fence`. Release manually unlinks single-referenced chain nodes to avoid recursive put/free paths, then drops the contained fence and frees the base object. Garbage collection can shorten chains as signaled prefixes are traversed.

Dependencies and integration points: depends on dma-fence core, RCU-safe fence gets, irq_work, and public chain iteration macros. Used by sync/fence users that need timeline composition and by fence unwrap utilities.

Risks and test signals: contained fences must not themselves be chain containers; chain nesting is allowed only through `prev`. Sequence-number lookup semantics for gaps and out-of-order completion are subtle. Test signals include forward/backward/random signaling, wait on long chains, sequence lookup for exact/gap/future values, concurrent lookup/signaling races, deadline propagation, and release without recursive stack overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-chain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-unwrap.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-unwrap.c

Purpose: provides utilities to flatten dma-fence array/chain containers and merge multiple fence inputs into a minimal fence or fence array.

Important APIs/types/functions: exports `dma_fence_unwrap_first()`, `dma_fence_unwrap_next()`, `dma_fence_dedup_array()`, and `__dma_fence_unwrap_merge()`. Internal `fence_cmp()` sorts by context and newest sequence number.

Control flow: unwrap starts by taking a reference to the head, treating the current chain-contained fence as a possible array, and returning its first member. Next advances within the current array, then walks the chain when the array is exhausted. Merge first counts unsignaled unwrapped fences and tracks the latest signaled timestamp. If none are pending it returns a private signaled stub with that timestamp; if one is pending it returns that fence directly; otherwise it collects unsignaled fences, deduplicates by context keeping the latest, and returns either the remaining single fence or a new `dma_fence_array`.

State and persistence behavior: no global state. Merge owns temporary arrays and carefully transfers fence references to either returned objects or releases duplicates.

Dependencies and integration points: depends on dma-fence, array, chain, sorting, and allocation helpers. Used by sync-file import and reservation singleton/merge paths where container fences must be decomposed before adding to reservation objects.

Risks and test signals: callers must understand reference ownership for returned fences and iterated members. Signaled fences are collapsed into timestamped private stubs, which preserves completion time but not original identity. Test signals include flattening arrays, chains, and chain-of-array shapes; deduplicating duplicate contexts by latest seqno; preserving deterministic order after sort; filtering signaled fences; and returning NULL only on allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-unwrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence.c

Purpose: implements the dma-fence synchronization primitive used by dma-buf, graphics, media, and accelerator drivers to represent asynchronous DMA work completion.

Important APIs/types/functions: exports fence context allocation, signaled stub fences, signaling functions, wait/default-wait functions, callback add/remove, status/error queries, deadline hints, descriptions, initialization, and driver/timeline name access. Major APIs include `dma_fence_context_alloc()`, `dma_fence_get_stub()`, `dma_fence_allocate_private_stub()`, `dma_fence_signal*()`, `dma_fence_wait_timeout()`, `dma_fence_wait_any_timeout()`, `dma_fence_add_callback()`, `dma_fence_remove_callback()`, `dma_fence_enable_sw_signaling()`, `dma_fence_set_deadline()`, `dma_fence_init()`, and `dma_fence_init64()`.

Control flow: boot initializes a permanently signaled stub fence. Fence init sets refcount, ops under RCU, callback list, context/seqno, lock choice, flags, and error state. Signaling sets the signaled flag once, optionally clears ops for fences with no release/wait callbacks, replaces the callback list, records timestamp, emits tracepoints, and invokes callbacks. Waiting enables software signaling and either calls a custom wait op or the default callback/schedule loop. `wait_any` installs callbacks on all fences and wakes on the first signaled. Release warns and force-signals with `-EDEADLK` if a fence is destroyed with pending callbacks, then calls custom release or RCU frees.

State and persistence behavior: global `dma_fence_context_counter` allocates unique ordered contexts. Each fence carries refcount, ops pointer, callback list/timestamp overlay, context, seqno, flags, lock, and error. After signal, driver/timeline names must be accessed under RCU and may return detached placeholder names because driver-owned backing data can be freed after a grace period.

Dependencies and integration points: depends on atomic/refcounting, spinlocks, RCU, scheduler waits, tracepoints, lockdep, seq_file, and dma-fence public macros. Reservation objects, dma-buf poll/sync-file code, fence arrays/chains, and many drivers build on this contract.

Risks and test signals: the cross-driver contract is strict: fences must complete in reasonable time, signaling paths must not deadlock with waiters holding reservation locks, and signaling-critical sections should be annotated with `dma_fence_begin_signalling()/end`. Callback functions can run in atomic/IRQ context. Custom wait ops are deprecated. Test signals include signaling idempotence, callback races, timeout behavior, status/error propagation, stub fence behavior, lockdep coverage of wait-vs-signal paths, deadline callback invocation, and RCU-safe name access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-heap.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-heap.c

Purpose: implements the userspace DMA-BUF heap framework, creating `/dev/dma_heap/<heap>` character devices that allocate dma-buf file descriptors through heap-specific backends.

Important APIs/types/functions: exports `dma_heap_add()`, `dma_heap_get_drvdata()`, and `dma_heap_get_name()` in the `DMA_BUF_HEAP` namespace. Internal file operations include `dma_heap_open()` and `dma_heap_ioctl()` with `DMA_HEAP_IOCTL_ALLOC`. `struct dma_heap` stores heap name, ops, private data, char device, minor, and list node. Module parameter `mem_accounting` influences heap allocation GFP flags in heap backends.

Control flow: init allocates a char-device major range and creates class `dma_heap` with devnode path `dma_heap/<name>`. Heap registration validates name and allocate op, allocates a minor from an xarray, adds a cdev, creates the device node, enforces unique heap names under `heap_list_lock`, and links the heap into the global list. Opening a heap resolves the minor through the xarray and stores the heap in `file->private_data`. The ioctl path validates command number and structure sizes, copies userspace data into stack or heap scratch space, dispatches allocation, and copies results back. Allocation page-aligns length, rejects zero, calls the heap's `allocate()` op, and converts the returned dma-buf to an fd.

State and persistence behavior: registered heaps persist in the global list and xarray for the lifetime of the heap provider. Minors are limited to 128. Allocated buffers persist through dma-buf file references and are owned by heap-specific dma-buf ops.

Dependencies and integration points: depends on Linux cdev/class/device, xarray minor allocation, dma-buf fd export, uapi `linux/dma-heap.h`, and backend heap drivers such as `system_heap.c` and `cma_heap.c`.

Risks and test signals: duplicate heap names are detected after device creation, so error cleanup must destroy device/cdev/minor correctly. The ioctl compatibility logic is size-flexible but must zero unknown fields to keep ABI extension safe. Test signals include `/dev/dma_heap/system` and CMA node creation, allocation fd returned with valid flags, rejection of invalid heap/fd flags and zero size, unique name enforcement, and correct cleanup on registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-resv.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-resv.c

Purpose: implements reservation objects, the dma-buf synchronization container that stores fences tagged by usage and protected by a ww_mutex plus RCU for lockless readers.

Important APIs/types/functions: exports `reservation_ww_class`, `dma_resv_init()`, `dma_resv_fini()`, `dma_resv_reserve_fences()`, `dma_resv_add_fence()`, `dma_resv_replace_fences()`, locked/unlocked iterators, `dma_resv_copy_fences()`, `dma_resv_get_fences()`, `dma_resv_get_singleton()`, `dma_resv_wait_timeout()`, `dma_resv_set_deadline()`, `dma_resv_test_signaled()`, and `dma_resv_describe()`. Internal `struct dma_resv_list` packs fence pointer plus usage bits in the low pointer bits.

Control flow: init creates the ww_mutex and clears the RCU fence-list pointer. Reserving fences allocates or grows the list, compacts out already signaled fences, publishes the new list via RCU, and drops references to signaled fences. Adding a fence requires the lock and prior reservation, takes a reference, replaces older/signed fences where possible, or appends a new entry with a write barrier before raising `num_fences`. Iterators either run under the lock or use RCU and restart if the list changes. `get_singleton()` returns NULL, a single fence, or a newly created fence array. Wait/test/deadline operations iterate matching usage fences without requiring callers to hold the lock.

State and persistence behavior: each reservation object owns its fence list references until replaced or finalized. Signaled fences are lazily pruned during reservation/growth. Usage tags determine which fences block read/write/kernel/bookkeeping operations.

Dependencies and integration points: depends on dma-fence core, fence arrays for singleton aggregation, ww_mutex wound/wait locking, RCU, mm and mmu-notifier lockdep priming, and seq_file debug descriptions. Used by dma-buf core, DRM GEM objects, sync-file import/export, and shared buffer exporters/importers.

Risks and test signals: callers must reserve slots before adding fences and hold the reservation lock for mutations. Pointer low-bit packing assumes fence pointer alignment. Unlocked iteration can restart, so accumulation code must handle `dma_resv_iter_is_restarted()`. Test signals include all usage levels, slot reservation compaction, replacing fences by context, RCU iteration under concurrent updates, singleton array creation, wait timeout semantics, deadline forwarding, and lockdep init coverage for reclaim/mmu-notifier interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/dma-resv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/Kconfig

Purpose: defines selectable dma-buf heap backends.

Important APIs/types/functions: `DMABUF_HEAPS_SYSTEM` enables the buddy-allocator-backed system heap and depends on `DMABUF_HEAPS`; `DMABUF_HEAPS_CMA` enables the CMA-backed heap and depends on `DMABUF_HEAPS && DMA_CMA`.

Control flow: no runtime control flow. These symbols select heap object files in `heaps/Makefile`, whose init functions register heap devices with `dma_heap_add()`.

State and persistence behavior: build configuration only.

Dependencies and integration points: integrates heap backend selection with the generic dma-heap framework. System heap uses normal pages; CMA heap uses contiguous memory allocator areas.

Risks and test signals: enabling CMA heap without usable CMA areas may produce no useful allocation node except where CMA regions exist. Test signals are `/dev/dma_heap/system`, optional `/dev/dma_heap/system_cc_shared`, and CMA heap device nodes matching configured CMA areas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/Makefile

Purpose: builds optional dma-buf heap backend implementations.

Important APIs/types/functions: maps `CONFIG_DMABUF_HEAPS_SYSTEM` to `system_heap.o` and `CONFIG_DMABUF_HEAPS_CMA` to `cma_heap.o`.

Control flow: no runtime flow. Module/built-in init functions in the selected objects register heap providers with the common dma-heap framework.

State and persistence behavior: none beyond build artifacts.

Dependencies and integration points: driven by `heaps/Kconfig` and consumed by parent `drivers/dma-buf/Makefile`.

Risks and test signals: missing backend object selection results in no heap device despite the generic heap framework being enabled. Test signal is successful Kbuild inclusion for each selected heap symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/cma_heap.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/cma_heap.c

Purpose: implements a dma-buf heap exporter backed by CMA contiguous memory regions, exposing one heap for the default CMA region and one per named CMA area.

Important APIs/types/functions: defines `struct cma_heap`, `struct cma_heap_buffer`, attachment state, `cma_heap_buf_ops`, and heap op `cma_heap_allocate()`. Init path `add_cma_heaps()` calls `__add_cma_heap()` for default and enumerated CMA regions.

Control flow: allocation page-aligns length, allocates buffer state, chooses CMA alignment up to `CONFIG_CMA_ALIGNMENT`, allocates contiguous pages through `cma_alloc()`, zeroes them, builds a page pointer array, fills dma-buf export info, and calls `dma_buf_export()`. Attach builds an sg table from the page array and stores per-device attachment state. Map/unmap uses `dma_map_sgtable()` and `dma_unmap_sgtable()`. CPU begin/end invalidates/flushes vmap ranges and syncs mapped attachment sg tables. mmap installs PFN fault operations; faults insert PFNs from the page array. vmap/vunmap reference-count a `vmap()` of all pages. Release warns on leaked kernel mappings, frees the page array, releases CMA pages, and frees buffer state.

State and persistence behavior: each buffer owns contiguous CMA pages, page array, attachment list, mutex, vmap address/count, and length until dma-buf release. Each attachment owns a separate sg table and mapped flag. Registered heaps persist after module init.

Dependencies and integration points: depends on CMA APIs, dma-buf/dma-heap framework, DMA mapping APIs, VM fault/mmap APIs, scatterlist helpers, and optional device CMA areas discovered by CMA enumeration.

Risks and test signals: allocation can be expensive and may fail under fragmentation or fatal signals during highmem zeroing. mmap uses PFN insertion with IO/PFNMAP flags, so page fault behavior differs from normal page-backed mmap. `map_dma_buf()` maps the attachment's table in place and tracks a single mapped flag. Test signals include allocation from default/named CMA heaps, zero-filled buffers, DMA map/unmap, mmap page faults over full length with SIGBUS past end, CPU sync over mapped attachments, vmap refcounting, and release returning pages to CMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/cma_heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/system_heap.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/system_heap.c

Purpose: implements the default page-backed dma-buf system heap, plus an optional confidential-computing shared heap that decrypts pages before sharing.

Important APIs/types/functions: defines `struct system_heap_priv`, `struct system_heap_buffer`, attachment state, `system_heap_buf_ops`, and heap op `system_heap_allocate()`. Helpers allocate high-order pages, duplicate sg tables for attachments, map/unmap DMA, mmap/vmap buffers, and set pages decrypted/encrypted for `system_cc_shared`.

Control flow: allocation loops over high-order preferences 8, 4, and 0 to satisfy the requested length with zeroed pages, optionally using `__GFP_ACCOUNT` when dma-heap `mem_accounting` is enabled. It builds the master sg table from collected pages, decrypts pages for the shared confidential-computing heap, exports a dma-buf, and unwinds by re-encrypting/freeing pages on failure. Attach duplicates the master sg table for the device. Map uses `dma_map_sgtable()` with `DMA_ATTR_CC_SHARED` when appropriate; unmap calls `dma_unmap_sgtable()`. CPU begin/end invalidates or flushes vmap ranges and syncs all mapped attachments. mmap remaps pages from the sg table, using decrypted pgprot for cc-shared buffers. vmap builds a temporary page array from the sg table and caches a vmap under the buffer mutex. Release frees or re-encrypts pages, intentionally leaking pages that cannot be re-encrypted.

State and persistence behavior: each buffer owns the master sg table, attachments list, mutex, length, vmap pointer/count, heap pointer, and cc-shared flag. Attachments own duplicated sg tables and mapped flags. Static heap private structs distinguish normal and cc-shared registration.

Dependencies and integration points: depends on dma-buf/dma-heap, buddy page allocator, DMA mapping, mem encryption/set_memory APIs, scatterlist/vmalloc/mmap APIs, and `cc_platform_has(CC_ATTR_MEM_ENCRYPT)`. Registers `system` always and `system_cc_shared` only when not HIGHMEM and memory encryption is available.

Risks and test signals: high-order allocation policy trades IOMMU efficiency for fragmentation sensitivity. Confidential-computing paths intentionally leak pages if re-encryption fails to avoid reusing shared memory unsafely. `system_heap_unmap_dma_buf()` does not pass the cc-shared attr on unmap, which should be checked against DMA API expectations. Test signals include allocation sizes spanning multiple orders, memcg accounting behavior, DMA map/unmap with and without cc-shared attrs, mmap/vmap coherency sync, cleanup under fatal signal/allocation failure, and no cc-shared heap on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/system_heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/selftest.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/selftest.c

Purpose: provides the module harness for dma-buf selftests, including test selection, subtest filtering, ordering, and init-time execution.

Important APIs/types/functions: builds the `selftests[]` table from `selftests.h`, declares per-test module parameters, exposes `__sanitycheck__()`, `__subtests()`, and module parameter `st_filter`.

Control flow: module init calls `run_selftests()`. If no individual test parameter is enabled, all tests default to enabled. Tests run in declaration order. `__subtests()` applies optional comma-separated filters with optional `!` negation and `caller/subtest` syntax, prints each subtest, checks for pending signals, runs the function, and stops on non-`-EINTR` errors. `run_selftests()` warns if a test returns positive or `-ENOTTY`, because those conflict with selftest sentinel semantics.

State and persistence behavior: enabled flags are module parameters. `__st_filter` is module parameter string state. There is no persistent result storage beyond kernel logs and module load return code.

Dependencies and integration points: depends on `selftest.h`/`selftests.h`, module parameters, scheduler signal checks, and individual selftest source files. The module is built as `dmabuf_selftests` under `CONFIG_DMABUF_SELFTESTS`.

Risks and test signals: filter parsing assumes `kstrdup(__st_filter)` succeeds and that `__st_filter` is meaningful; null filter behavior should be validated in module-parameter handling. Long-running subtests can be interrupted by signals. Test signals are module load success/failure, per-test parameter selection, `st_filter` include/exclude behavior, and kernel log lines for each executed test/subtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/selftest.h -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/selftest.h

Purpose: shared declarations and helpers for dma-buf selftest modules.

Important APIs/types/functions: includes generated prototypes for every `selftest(name, func)` entry in `selftests.h`, defines `struct subtest`, declares `__subtests()`, and provides the `subtests()` and `SUBTEST()` helper macros.

Control flow: no direct runtime flow. Test files define static subtest arrays with `SUBTEST(fn)` and invoke `subtests(tests, data)`, which passes the caller function name for filtering/logging.

State and persistence behavior: none. It is compile-time glue.

Dependencies and integration points: included by `selftest.c` and all `st-*` dma-buf selftest files. It centralizes subtest invocation against the harness.

Risks and test signals: macro-generated prototypes must match the actual selftest function signatures. Test signals are clean builds when adding/removing entries in `selftests.h` and correct caller names in `st_filter`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/selftests.h -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/selftests.h

Purpose: central list of dma-buf selftest suites consumed multiple times by macro expansion.

Important APIs/types/functions: lists `selftest(sanitycheck, __sanitycheck__)`, `selftest(dma_fence, dma_fence)`, `selftest(dma_fence_chain, dma_fence_chain)`, `selftest(dma_fence_unwrap, dma_fence_unwrap)`, and `selftest(dma_resv, dma_resv)`.

Control flow: no standalone runtime flow. `selftest.c` expands this file to build enum indexes, the table of names/functions, and module parameters; `selftest.h` expands it to declare prototypes.

State and persistence behavior: none directly. The order in this file persists as execution order at module init.

Dependencies and integration points: tightly coupled to `selftest.c` and `selftest.h`. New selftest suites must be added here to be runnable by the harness.

Risks and test signals: names must be unique legal C identifiers and functions must have `int func(void)` signature. Test signal is that `sanitycheck` remains first for harness self-checking and all listed functions link into `dmabuf_selftests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/selftests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence-chain.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence-chain.c

Purpose: selftests dma-fence-chain behavior, including sequence lookup, signaling order, waiting, garbage collection, and concurrent lookup/signaling races.

Important APIs/types/functions: defines mock fences backed by a `KMEM_CACHE` with RCU-safe slab flags, helper `mock_chain()`, `struct fence_chains`, chain construction/destruction helpers, and top-level `dma_fence_chain()`.

Control flow: `fence_chains_init()` builds an array of mock fences and a chain tail of requested length, enabling software signaling on each chain node. Subtests validate `dma_fence_chain_find_seqno()` for exact, zero, future, previous, gap, signaled, and out-of-order cases. Race tests spawn per-CPU kthreads that randomly find seqnos and signal fences in a long chain. Signaling tests complete fences forward/backward and verify chain nodes only signal when predecessors are complete. Wait tests run a waiter on the tail and signal contained fences in forward, backward, or randomized order.

State and persistence behavior: temporary chain/fence arrays are allocated with `kvmalloc`; each test releases fences/chains through `fence_chains_fini()`. The slab cache exists for the duration of `dma_fence_chain()` and is destroyed after subtests.

Dependencies and integration points: depends on dma-fence core, dma-fence-chain APIs, kthreads, random number helpers, RCU-safe slab allocation, and the selftest harness.

Risks and test signals: race test timing is bounded and may be sensitive to CPU count/scheduling. The tests exercise long chains (`CHAIN_SZ` is 4096), which is important for stack-safety and garbage collection. Passing signals include no incorrect seqno lookup, no premature chain signaling, waiter completion under varied signal orders, and no race errors under concurrent find/signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence-chain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence-unwrap.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence-unwrap.c

Purpose: selftests fence unwrap and merge helpers across arrays, chains, duplicate fences, sequence-number deduplication, signaled filtering, and mixed container shapes.

Important APIs/types/functions: defines `struct mock_fence`, `__mock_fence()`, `mock_fence()`, `mock_array()`, `mock_chain()`, and top-level `dma_fence_unwrap()`. Subtests cover unwrap and merge variants.

Control flow: mock helpers create fences, arrays, and chains with explicit contexts/seqnos. `unwrap_array`, `unwrap_chain`, and `unwrap_chain_array` verify every original fence appears exactly once during unwrap iteration. Merge tests combine fences and containers, then iterate the result and validate deduplication/order: duplicate same fence collapses, later seqno per context wins, reversed arrays/chains merge deterministically, signaled stub fences are filtered, and complex context/seqno mixtures return only latest unsignaled fences.

State and persistence behavior: all state is temporary per subtest. Ownership transfer is a key part of the tests: arrays/chains take references, merge returns a fence/container, and tests drop references after validation.

Dependencies and integration points: depends on dma-fence, fence-array, fence-chain, fence-unwrap APIs, variadic test helpers, and the selftest harness.

Risks and test signals: tests are sensitive to reference ownership; failure paths must put all allocated fences to avoid leaks during module load. Passing signals include complete iteration coverage, no unexpected fences, correct context/seqno ordering, duplicate release behavior, and allocation-failure paths returning `-ENOMEM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence-unwrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence.c

Purpose: selftests core dma-fence behavior: signaling, callbacks, status/error reporting, waits/timeouts, stub fences, and callback races.

Important APIs/types/functions: defines a simple mock fence ops table, `mock_fence()`, `struct simple_cb`, timer-backed wait helper, race-thread structures, and top-level `dma_fence()`.

Control flow: subtests create unsignaled mock fences, enable software signaling, and check one behavior at a time. Signaling verifies initial unsignaled state, idempotent signal, signaled flags, and ops clearing after signal. Callback tests cover add-before-signal, add-after-signal failure, removal before signal, and removal after callback execution. Status/error tests ensure errors are visible only after signal. Wait tests validate zero-timeout results and timer-driven completion. Stub tests check many references to the global signaled stub. Race tests run two kthreads exchanging RCU-published fences while signaling before or after callback attachment to stress `dma_fence_get_rcu_safe()` and callback completion ordering.

State and persistence behavior: all fences are temporary per subtest. Race test uses RCU pointer array state only for the duration of the subtest. The global stub fence state is owned by `dma-fence.c`.

Dependencies and integration points: depends on dma-fence core, kthreads, timers, RCU, scheduler waits, spinlocks, and the selftest harness.

Risks and test signals: race test duration is short and probabilistic, so it is a smoke test rather than exhaustive proof. Passing signals include callback visibility under memory barriers, no late callback invocation after failed add/removal, correct wait return values, no unsignaled stub fences, and no race-thread errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-resv.c -->
# sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-resv.c

Purpose: selftests dma-resv reservation objects across all usage classes for locking, signaling visibility, locked/unlocked iteration, and fence extraction.

Important APIs/types/functions: defines a shared `fence_lock`, mock fence allocation, subtests `sanitycheck`, `test_signaling`, `test_for_each`, `test_for_each_unlocked`, `test_get_fences`, and top-level `dma_resv()`.

Control flow: `dma_resv()` initializes the fence lock and runs the same subtest set for `DMA_RESV_USAGE_KERNEL` through `DMA_RESV_USAGE_BOOKKEEP`. Each subtest allocates a mock fence, enables signaling, initializes a reservation object, reserves one slot under lock, adds the fence with the current usage, then validates the API under test. Unlocked iteration intentionally corrupts the cursor list pointer mid-test to force a restart path. Cleanup signals the fence, finalizes the reservation, drops fence refs, and frees extracted arrays.

State and persistence behavior: reservation and fence state are temporary per subtest. The shared spinlock is initialized once at suite entry and used as external fence lock for allocated fences.

Dependencies and integration points: depends on dma-resv and dma-fence APIs plus the selftest harness. It validates the same reservation semantics used by dma-buf, DRM, and sync-file integration.

Risks and test signals: tests use one fence per usage and do not cover multi-fence compaction or replacement, but they exercise the essential API contracts. Passing signals include successful ww_mutex lock/unlock, unsignaled then signaled reservation status, locked iteration returning the expected usage/fence, unlocked iterator restart detection, and `dma_resv_get_fences()` returning one referenced fence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-resv.c -->
