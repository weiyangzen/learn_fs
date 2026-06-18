# subset-b-004986 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/nd_perf.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/nd_perf.c

Purpose: Implements the generic libnvdimm performance monitoring unit registration helper used by architecture or platform NVDIMM PMU providers. It exposes a fixed set of NVDIMM event encodings, PMU format metadata, and a hotplug-aware `cpumask` sysfs attribute.

Important APIs and flow: `register_nvdimm_pmu()` validates provider-supplied PMU callbacks (`event_init`, `add`, `del`, `read`, and `name`), allocates PMU attribute-group storage, installs `format`, `events`, and dynamic `cpumask` groups, initializes CPU hotplug state, and calls `perf_pmu_register()`. `unregister_nvdimm_pmu()` unregisters perf state, removes hotplug state, frees PMU attribute groups, and frees the provider object. `nvdimm_events_sysfs_show()` prints `event=0xNN`; `nvdimm_pmu_cpumask_show()` reports the current designated CPU.

State and persistence behavior: Runtime state lives in `struct nvdimm_pmu`: `dev`, `pmu.attr_groups`, `arch_cpumask`, `cpu`, `cpuhp_state`, and hotplug `node`. No persistent media state is modified. CPU offline handling removes the CPU from `arch_cpumask`, chooses another allowed CPU or NUMA-local CPU, and migrates perf context with `perf_pmu_migrate_context()`.

Dependencies and integration points: Depends on `linux/nd.h` PMU macros, perf PMU registration, CPU hotplug multi-state APIs, cpumask helpers, and platform devices. Providers supply the actual counter access callbacks.

Risks and test signals: Hotplug teardown must match registration even after partial failures. The dynamic cpumask group frees only the attrs array and group, while the `perf_pmu_events_attr` allocation is not separately retained in this file. Tests should cover invalid provider callbacks, PMU register failure cleanup, CPU online/offline migration, empty `arch_cpumask`, and NUMA node without online CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/nd_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/nd_virtio.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/nd_virtio.c

Purpose: Provides the virtio-pmem flush transport used by libnvdimm regions created by `virtio_pmem.c`. It translates NVDIMM flush requests into virtqueue commands and supports asynchronous bio chaining for block-layer flushes.

Important APIs and flow: `virtio_pmem_host_ack()` is the virtqueue callback. It drains completed request buffers, marks each request done, wakes waiters, and wakes one queued submitter waiting for descriptor space. `virtio_pmem_flush()` serializes device flushes with `flush_lock`, rejects devices needing reset, allocates a request, submits request/response scatterlists, waits for descriptor availability on `-ENOSPC`, kicks the queue, waits for host completion, and returns the host status. `async_pmem_flush()` either builds a child `REQ_PREFLUSH` bio chained to the parent or synchronously calls `virtio_pmem_flush()`.

State and persistence behavior: Per-request waitqueues and flags track completion and descriptor availability. `vpmem->req_list` holds blocked flush requests when the virtqueue is full; `pmem_lock` protects the virtqueue and wait list. Persistence is delegated to the host response for `VIRTIO_PMEM_REQ_TYPE_FLUSH`.

Dependencies and integration points: Uses `struct virtio_pmem` from `virtio_pmem.h`, virtqueue APIs, libnvdimm `nd_region->flush`, block bios, and the `virtio_pmem` platform registration path.

Risks and test signals: Flush requests use `GFP_ATOMIC` while holding a spinlock and wait outside the lock on descriptor exhaustion. Tests should cover queue-full wakeups, host error status propagation, child bio chaining, device reset status, remove/freeze while flushes are in flight, and multiple concurrent flush callers serialized by `flush_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/nd_virtio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/of_pmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/of_pmem.c

Purpose: Registers Device Tree described `pmem-region` and `pmem-region-v2` memory ranges as libnvdimm regions. It is the OF-specific discovery path for platform persistent or volatile memory without per-DIMM label emulation.

Important APIs and flow: `of_pmem_region_probe()` allocates private bus state, creates an NVDIMM bus descriptor named after the platform device, registers an `nvdimm_bus`, detects the optional `volatile` property, and creates one libnvdimm region per platform resource. Nonvolatile regions set `ND_REGION_PAGEMAP` and `ND_REGION_PERSIST_MEMCTRL`; volatile regions set `ND_REGION_PAGEMAP` and use `nvdimm_volatile_region_create()`. `of_pmem_region_remove()` unregisters the bus and frees the private allocation.

State and persistence behavior: Persistent state is only the platform-described physical resource. Runtime state is `struct of_pmem_private` with the bus descriptor and bus pointer. The driver does not maintain labels, security state, or flush metadata itself.

Dependencies and integration points: Depends on OF matching, platform resources, `nvdimm_bus_register()`, and region creation from `region_devs.c`. The created regions are later probed by the generic region and pmem namespace drivers.

Risks and test signals: Probe continues after individual region creation failures and returns success if the bus registered, which can hide partial resource registration. Tests should cover missing OF node, allocation/register failure cleanup, volatile versus nonvolatile properties, multiple resources, NUMA assignment, and both compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/of_pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/pfn.h -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/pfn.h

Purpose: Defines the on-media PFN/DAX info-block format used to describe fsdax/devdax namespace metadata, alignment, data offset, and vmemmap placement.

Important APIs and types: `PFN_SIG` and `DAX_SIG` identify PFN and DAX superblocks. `struct nd_pfn_sb` stores signature, UUID, parent namespace UUID, version fields, `dataoff`, `npfns`, mode, legacy `start_pad`, `end_trunc`, alignment, page size, struct page size, padding, and checksum.

State and persistence behavior: This structure is written to the namespace info-block area at offset `SZ_4K` by `pfn_devs.c` and later validated on probe. Fields are little-endian and constitute persistent ABI; version-minor handling in implementation supplies defaults for older records.

Dependencies and integration points: Included by PFN, DAX, and PMEM code plus testing code that needs the exact layout. It depends on kernel integer and memory zone definitions.

Risks and test signals: Layout compatibility is critical because the structure is on-media metadata. Tests should validate checksums, older minor versions, endianness, signature matching, parent UUID matching, and that `sizeof(struct nd_pfn_sb)` remains compatible with the expected info-block area.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/pfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/pfn_devs.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/pfn_devs.c

Purpose: Implements libnvdimm PFN device creation, sysfs configuration, persistent PFN/DAX info-block validation, and `dev_pagemap` setup for fsdax/devdax namespaces.

Important APIs and flow: Sysfs attributes configure `mode`, `align`, `uuid`, and claimed `namespace`, and expose resource, size, and supported alignments. `nd_pfn_create()` creates seed PFN devices for memory regions. `nd_pfn_probe()` detects existing PFN info blocks on namespaces and registers PFN devices. `nd_pfn_validate()` reads the info block, checks signature, checksum, parent UUID, mode, page/struct-page compatibility, alignment, padding, and bounds. `nvdimm_setup_pfn()` initializes or validates the info block, clears metadata badblocks, and fills `struct dev_pagemap`.

State and persistence behavior: The key persistent state is `struct nd_pfn_sb` stored at namespace offset `SZ_4K`. New initialization computes `dataoff`, `npfns`, `end_trunc`, `align`, page-size metadata, and checksum before `nvdimm_write_bytes()`. Runtime state includes `nd_pfn->mode`, `align`, `uuid`, `ndns`, `pfn_sb`, `npfns`, and the region PFN ida.

Dependencies and integration points: Depends on namespace claim helpers, libnvdimm bus locking, `nvdimm_read_bytes()`/`nvdimm_write_bytes()`, badblocks, `memremap_compat_align()`, hugepage alignment availability, devdax detection, `dev_pagemap`, vmem altmap, and KMSAN page-struct override behavior.

Risks and test signals: This file gates DAX correctness. High-risk cases include legacy `start_pad`, namespace alignment changes, struct page size mismatch, insufficient namespace capacity, badblock clearing in metadata space, and partial device allocation failure. Tests should cover PFN_MODE_RAM versus PFN_MODE_PMEM, existing valid and corrupt info blocks, read-only regions, small namespaces, DAX alignment rejection, and page-struct override configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/pfn_devs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/pmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/pmem.c

Purpose: Implements the NVDIMM persistent-memory block and DAX driver. It probes raw PMEM namespaces, PFN-backed namespaces, BTT claims, and DAX claims, then exposes a gendisk and optional DAX host for direct access.

Important APIs and flow: `pmem_submit_bio()` handles `REQ_PREFLUSH`, iterates bio segments, performs direct read/write via `copy_mc_to_kernel()` or `memcpy_flushcache()`, handles badblocks and poison clearing on writes, honors FUA with `nvdimm_flush()`, and ends the bio. DAX operations include `pmem_dax_direct_access()`, `pmem_dax_zero_page_range()`, and `pmem_recovery_write()` for poison recovery. `pmem_attach_disk()` enables the namespace, optionally parses PFN metadata, maps memory via `devm_memremap_pages()` or `devm_memremap()`, initializes badblocks, allocates DAX, adds the disk, and tracks `badblocks` sysfs. `nd_pmem_probe()` chooses BTT, PFN, DAX, or raw PMEM attach.

State and persistence behavior: Runtime `struct pmem_device` stores physical base, data offset, virtual mapping, namespace size, PFN padding, badblocks, DAX device, gendisk, and `dev_pagemap`. Persistent metadata is read through PFN/DAX info blocks and badblock/poison state from the NVDIMM subsystem. Writes use cache-flush copies and explicit region flushes when required.

Dependencies and integration points: Depends on libnvdimm namespace probing, BTT/PFN/DAX helpers, block layer, DAX core, badblocks, memory failure handling, `nvdimm_flush()`, and architecture PMEM flush/copy APIs.

Risks and test signals: Media poison paths must preserve data integrity and update badblocks only after successful recovery. DAX direct access must return accurate good ranges around badblocks. Tests should cover raw/PFN/BTT/DAX probe ordering, write-cache attribute visibility, FUA/prefetch flush failures, memory-failure notification, badblock revalidation, remove/shutdown flush, and fallback when DAX allocation is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/pmem.h -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/pmem.h

Purpose: Defines the shared persistent-memory device structure consumed by the PMEM driver and NVDIMM test overrides.

Important APIs and types: `struct pmem_device` records physical address, PFN/DAX data offset, kernel mapping, immutable namespace size, PFN padding, badblocks sysfs node, badblocks state, DAX device, gendisk, and `dev_pagemap`. It declares weak-overridable `__pmem_direct_access()` and wraps `TestClearPageHWPoison()` behind `test_and_clear_pmem_poison()` when memory failure support is enabled.

State and persistence behavior: The structure is runtime state only; it points to persistent media and persistent poison/badblock information managed elsewhere. The `data_offset` and `pfn_pad` fields reflect on-media PFN metadata decisions.

Dependencies and integration points: Depends on page flags, badblocks, memremap, fs types, DAX access mode, and memory failure configuration. `tools/testing/nvdimm` can consume this header and override direct access behavior.

Risks and test signals: Consumers must initialize `bb.dev` before helpers use it indirectly. Build tests should cover `CONFIG_MEMORY_FAILURE` enabled/disabled and NVDIMM test override linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/pmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/ramdax.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/ramdax.c

Purpose: Provides a RAM-backed libnvdimm provider for e820 type-12 memory and OF `pmem-region`, including an emulated label area at the end of each resource. It lets RAM-like persistent ranges participate in namespace label workflows.

Important APIs and flow: `ramdax_probe()` registers an NVDIMM bus with `ramdax_ctl()`, then either scans OF resources or legacy persistent-memory resources. `ramdax_register_dimm()` maps the last 128 KiB as a label area, creates an `nvdimm` with label config commands, and registers a one-mapping PMEM region through `ramdax_register_region()`. The control path handles `ND_CMD_GET_CONFIG_SIZE`, `GET_CONFIG_DATA`, and `SET_CONFIG_DATA` by bounds-checking and copying from/to the mapped label area.

State and persistence behavior: `struct ramdax_dimm` stores the created `nvdimm` and mapped label area. The label area lives in the physical resource and is treated as persistent namespace metadata; region capacity excludes `LABEL_AREA_SIZE`.

Dependencies and integration points: Uses libnvdimm bus, DIMM, region, and ndctl command plumbing; e820 resource walking; OF matching; `memremap()` with write-back mapping; and synthetic interleave-set cookies.

Risks and test signals: `ramdax_probe_of()` notes a FIXME for unregistering already-created DIMMs after a later resource fails. Tests should cover label bounds, command mask enforcement, multi-resource OF cleanup, too-small resources, e820 scanning, and persistence of label writes across namespace reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/ramdax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/region.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/region.c

Purpose: Implements the generic NVDIMM region driver that activates regions, initializes badblocks, discovers/registers namespaces, creates seed devices, and forwards region events to children.

Important APIs and flow: `nd_region_probe()` warns when online CPUs are fewer than I/O lanes, calls `nd_region_activate()`, initializes region badblocks, populates badblocks from media ranges, registers namespaces, records active/total namespace counts, and creates BTT/PFN/DAX seed devices. `nd_region_remove()` unregisters children, clears seed pointers under the bus lock, drops badblock sysfs state, and invalidates CPU caches for disabled regions when supported. `nd_region_notify()` repopulates poison badblocks on `NVDIMM_REVALIDATE_POISON` and relays events to child devices.

State and persistence behavior: Runtime state includes `struct nd_region_data` driver data, seed device pointers, namespace counts, and `bb_state`. Persistent state is not modified directly; namespace discovery and badblock population read persistent label/poison state through libnvdimm.

Dependencies and integration points: Depends on `region_devs.c` activation and region types, namespace registration, badblocks, BTT/PFN/DAX seed creation, nvdimm bus locking, and child notification APIs.

Risks and test signals: Partial namespace registration is tolerated unless all registrations fail, so userspace must inspect namespace counts. Tests should cover activation failure, badblock sysfs absence, mixed namespace success/failure, removal while attributes are read, poison revalidation, and CPU cache invalidation behavior after disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/region_devs.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/region_devs.c

Purpose: Defines NVDIMM PMEM/volatile region devices, their sysfs ABI, region creation/deletion helpers, interleave mapping metadata, flush handling, lane locking, and persistence-domain queries.

Important APIs and flow: `nvdimm_pmem_region_create()` and `nvdimm_volatile_region_create()` allocate `struct nd_region`, copy mappings, allocate per-CPU lanes, assign ids, install device attributes, and register the device. `nd_region_activate()` blocks overwrite-in-progress DIMMs, invalidates incoherent memory after security operations, allocates `nd_region_data`, maps flush hint addresses, and deduplicates identical flush pages. Sysfs exposes size, mappings, namespace type, seeds, available capacity, badblocks, read-only, alignment, resource, persistence domain, interleave set cookie, and mappingN attributes. `nvdimm_flush()` dispatches provider async flushes or `generic_nvdimm_flush()`; `nvdimm_has_flush()`, `nvdimm_has_cache()`, and `is_nvdimm_sync()` report persistence semantics.

State and persistence behavior: Runtime state includes mappings, `provider_data`, interleave set, flags, read-only state, alignment, badblocks, seed pointers, IDAs, and per-CPU lane counters. Persistent behavior centers on flush hints and platform persistence flags; the file does not write labels but exposes capacity and mapping data derived from persistent namespace metadata.

Dependencies and integration points: Integrates with libnvdimm bus locking, DIMM objects, namespace label helpers, memregion IDs, badblocks, `devm_nvdimm_ioremap()`, architecture cache invalidation, PMEM write barriers, BTT lane users, CXL region flags, and virtio async flush providers.

Risks and test signals: Flush hint mapping and duplicate suppression are hardware-facing and order-sensitive. Alignment changes affect future namespace allocation. Tests should cover no-flush/flush-hint/async-flush regions, security overwrite blocking, incoherent DIMM cache invalidation, read-only propagation to children, interleave mapping sysfs visibility, lane recursion, CXL preassigned ids, and region release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/region_devs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/security.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/security.c

Purpose: Implements the libnvdimm security sysfs command dispatcher and key-management glue for DIMM unlock, freeze, disable, update, erase, overwrite, and master-passphrase operations.

Important APIs and flow: Key helpers request encrypted keys named `nvdimm:<dimm_id>`, validate passphrase length, look up user-supplied key serials, and expose decrypted payloads under key semaphores. `__nvdimm_security_unlock()` handles pre-OS unlocked revalidation, normal unlock, security flag refresh, and incoherent-cache marking. `security_disable()`, `security_update()`, `security_erase()`, and `security_overwrite()` validate state, retrieve old/new keys, call provider security ops, refresh flags, and mark DIMMs incoherent after erase/overwrite. `nvdimm_security_overwrite_query()` polls asynchronous overwrite completion and notifies sysfs. `nvdimm_security_store()` parses textual commands and dispatches operations.

State and persistence behavior: Security state persists in DIMM hardware. Runtime flags include `nvdimm->sec.flags`, `ext_flags`, `overwrite_tmo`, `NDD_SECURITY_OVERWRITE`, `NDD_WORK_PENDING`, and `NDD_INCOHERENT`. Erase/overwrite/unlock can make CPU caches incoherent, causing region activation to invalidate caches before reuse.

Dependencies and integration points: Depends on keyrings, encrypted key payloads, provider `nvdimm_security_ops`, libnvdimm bus reconfiguration mutex, sysfs notifications, delayed work on `system_percpu_wq`, and region activation's incoherency handling.

Risks and test signals: Key serial logging assumes non-null keys even for zero-key paths, which needs careful provider behavior. Tests should cover missing provider ops, frozen state, overwrite busy polling and cancellation, active DIMM erase rejection, key length/type rejection, key revalidation disabled/enabled, master versus user passphrases, and sysfs command parsing limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/virtio_pmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/virtio_pmem.c

Purpose: Implements virtio-pmem device discovery and libnvdimm region registration. It exposes a virtio-provided persistent memory range as an asynchronous-flush PMEM region.

Important APIs and flow: `init_vq()` creates the single flush virtqueue with `virtio_pmem_host_ack()`, initializes the spinlock, and initializes the pending request list. `virtio_pmem_validate()` verifies the shared-memory feature has a valid region and clears the feature if not. `virtio_pmem_probe()` allocates `struct virtio_pmem`, initializes flush locking and virtqueue state, reads start/size from a virtio shared-memory region or config space, registers an NVDIMM bus, fills an `nd_region_desc` with NUMA nodes, async flush callback, provider data, pagemap and async flags, marks the virtio device ready, and creates a PMEM region. Remove/freeze/restore unregister or reset queues and restore virtqueue readiness.

State and persistence behavior: Runtime state is `struct virtio_pmem` plus the registered NVDIMM bus. Persistent data is the host-backed memory range; persistence is guaranteed by virtio flush requests handled in `nd_virtio.c`.

Dependencies and integration points: Depends on virtio PMEM IDs/features, shared memory regions, libnvdimm bus/region creation, NUMA helpers, and the asynchronous flush callback exported by `nd_virtio.c`.

Risks and test signals: `virtio_device_ready()` is intentionally called before region creation because libnvdimm may expose the region immediately. Tests should cover config-space and shared-memory discovery, invalid shared-memory feature fallback, region creation failure cleanup, suspend/resume restore of virtqueues, reset-needed flush rejection, and remove while requests are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/virtio_pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/virtio_pmem.h -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/virtio_pmem.h

Purpose: Defines the shared data structures for the virtio-pmem discovery driver and the NVDIMM flush transport.

Important APIs and types: `struct virtio_pmem_request` wraps a virtio request/response pair, host-ack waitqueue, descriptor-availability waitqueue, completion flags, and queue list entry. `struct virtio_pmem` stores the virtio device, flush virtqueue, flush mutex, NVDIMM bus and descriptor, deferred request list, spinlock, and memory range start/size. It declares `virtio_pmem_host_ack()` and `async_pmem_flush()`.

State and persistence behavior: This header defines runtime synchronization and request state. No media metadata is stored here; the range fields describe the persistent region exposed by the host.

Dependencies and integration points: Depends on virtio PMEM UAPI, libnvdimm, mutexes, spinlocks, and module definitions. Used by both `virtio_pmem.c` and `nd_virtio.c`.

Risks and test signals: The request object is stack-independent heap state because virtqueue completion happens asynchronously. Tests should exercise list ownership, waitqueue wakeups, and lock ordering between `flush_lock` and `pmem_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/virtio_pmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nvme/Kconfig

Purpose: Defines the top-level NVMe Kconfig menu and includes the common, host, and target NVMe configuration trees.

Important APIs and flow: The file opens `menu "NVME Support"`, sources `drivers/nvme/common/Kconfig`, `drivers/nvme/host/Kconfig`, and `drivers/nvme/target/Kconfig`, then closes the menu.

State and persistence behavior: No runtime or persistent state. It controls which NVMe subsystems can be configured into the kernel.

Dependencies and integration points: Integrates the common auth/keyring options, host drivers, and target drivers into one visible menu.

Risks and test signals: Build coverage should ensure sourced paths stay valid after tree moves and that host/target/common options appear under the expected menu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nvme/Makefile

Purpose: Adds NVMe common, host, and target subdirectories to the kernel build.

Important APIs and flow: Unconditionally appends `common/`, `host/`, and `target/` to `obj-y`; each subdirectory decides which objects are built through its own Kconfig-controlled Makefile.

State and persistence behavior: No runtime state. It is build-system wiring only.

Dependencies and integration points: Integrates with kbuild recursion and the subdirectory Makefiles for common authentication/keyring code, host transports, and target transports.

Risks and test signals: Build tests should verify empty/unselected subtrees remain harmless and selected modules get linked from the proper subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nvme/common/Kconfig

Purpose: Defines common NVMe support options for TLS PSK keyring, DH-HMAC-CHAP authentication helpers, and KUnit tests.

Important APIs and flow: `NVME_KEYRING` is a tristate selecting `KEYS`. `NVME_AUTH` is a tristate selecting crypto, DH, RFC7919 DH groups, and SHA libraries. `NVME_AUTH_KUNIT_TEST` depends on KUnit and NVMe auth, defaults with `KUNIT_ALL_TESTS`, and enables tests for common authentication code.

State and persistence behavior: No runtime state directly. These symbols determine whether authentication helpers, keyring code, and tests are compiled.

Dependencies and integration points: Selected by host auth and NVMe TCP TLS paths. The KUnit option builds `common/tests/auth_kunit.o`.

Risks and test signals: Config tests should cover built-in and module combinations, especially users that select keyring/auth indirectly from host options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nvme/common/Makefile

Purpose: Builds common NVMe authentication and keyring modules plus optional authentication KUnit tests.

Important APIs and flow: Adds `-I$(src)`, builds `nvme-auth.o` from `auth.o` under `CONFIG_NVME_AUTH`, builds `nvme-keyring.o` from `keyring.o` under `CONFIG_NVME_KEYRING`, and includes `tests/auth_kunit.o` under `CONFIG_NVME_AUTH_KUNIT_TEST`.

State and persistence behavior: Build-time only; no runtime state.

Dependencies and integration points: Ties Kconfig symbols to the common C implementations used by host and transport code.

Risks and test signals: Build matrix should cover auth without keyring, keyring without auth, built-in versus module, and KUnit test linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/auth.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/common/auth.c

Purpose: Provides common NVMe DH-HMAC-CHAP and TLS PSK cryptographic helpers shared by host authentication and tests.

Important APIs and flow: Exports sequence number generation, DH group name/KPP mapping, HMAC algorithm mapping, key allocation/free/parse/extract, HMAC init/update/final wrappers, key transformation by NQN, augmented challenge generation, DH private/public/session key generation, TLS generated PSK generation, PSK digest generation, and TLS PSK derivation. `nvme_auth_extract_key()` decodes base64 DHHC keys and verifies CRC. `nvme_auth_gen_session_key()` computes DH shared secret and hashes it. TLS helpers implement generated PSK, Base64 digest, and HKDF-Expand-Label-style derivation for SHA-256/SHA-384.

State and persistence behavior: Maintains a mutex-protected global DH-HMAC-CHAP sequence number seeded from random on first use. Key material is dynamically allocated and freed with sensitive zeroing. No persistent storage is written.

Dependencies and integration points: Uses Linux crypto KPP/DH, SHA/HMAC library helpers, base64, CRC32, NVMe auth UAPI constants, and exported symbols consumed by `host/auth.c`, target auth, and KUnit tests.

Risks and test signals: Cryptographic ABI must match NVMe specs. SHA-512 has a hash id and HMAC support but TLS digest/derive intentionally reject it. Tests should cover key CRC failures, unsupported hashes/groups, sequence wraparound, DH KPP errors, transformed keys, augmented challenge vectors, TLS PSK derivation vectors, and sensitive buffer cleanup on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/keyring.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/common/keyring.c

Purpose: Implements the NVMe global keyring and `psk` key type for NVMe/TCP TLS pre-shared keys, including generated TLS PSK refresh and default-key selection.

Important APIs and flow: `nvme_keyring_id()` exposes the global `.nvme` keyring serial. `nvme_tls_key_lookup()` validates a key id and rejects revoked/invalidated keys. A custom `psk` key type uses user payload parsing plus NVMe-specific description matching. `nvme_tls_psk_refresh()` creates or updates a generated v1 PSK identity of the form `NVMe1G<hmac> <hostnqn> <subnqn> <digest>`, sets permissions, and applies a one-hour timeout. `nvme_tls_psk_default()` searches retained/generated, v1/v0, SHA-384/SHA-256 identities in priority order.

State and persistence behavior: Runtime state is the process-global `nvme_keyring` and keys linked into it or caller-provided keyrings. Key payloads persist in kernel key retention until timeout/revoke/invalidate; generated keys receive a 3600 second timeout.

Dependencies and integration points: Depends on Linux key retention, user key payload helpers, NVMe TCP TLS cipher constants, host/subsystem NQNs, and generated PSKs from common auth or host secure concatenation.

Risks and test signals: `nvme_tls_key_lookup()` returns `-EKEYREVOKED` without putting the revoked key reference, which deserves lifetime scrutiny. Prefix-style description matching can match shorter identities. Tests should cover priority ordering, generated key refresh/update, key timeouts, revoked/invalidated keys, custom keyrings, and identity collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/keyring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/tests/auth_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/common/tests/auth_kunit.c

Purpose: Provides KUnit coverage for NVMe authentication TLS PSK derivation helper paths using fixed vectors for SHA-256, SHA-384, and SHA-512 behavior.

Important APIs and flow: `test_nvme_auth_derive_tls_psk()` builds deterministic `skey`, `c1`, and `c2`, calls `nvme_auth_generate_psk()`, validates the generated PSK, calls `nvme_auth_generate_digest()`, and then calls `nvme_auth_derive_tls_psk()` when a digest is expected. Individual test cases supply expected vectors for SHA-256 and SHA-384; SHA-512 expects digest generation to fail with `-EINVAL`.

State and persistence behavior: No persistent state. Per-test allocations for PSK, digest, and TLS PSK are registered with KUnit cleanup actions.

Dependencies and integration points: Depends on KUnit, SHA digest sizes, `linux/nvme-auth.h`, and the exported common auth helpers.

Risks and test signals: The tests primarily cover TLS PSK derivation and do not cover key parsing, DH KPP, or host handshake sequencing. They are useful regression signals for spec-vector changes, SHA-512 unsupported behavior, allocation cleanup, and digest formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/common/tests/auth_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/Kconfig

Purpose: Defines NVMe host-side configuration for core support, PCI block driver, multipath, verbose errors, hwmon, fabrics transports, TCP TLS, in-band authentication, and Apple ANS platform support.

Important APIs and flow: `NVME_CORE` is selected by host drivers. `BLK_DEV_NVME` depends on PCI and block. `NVME_MULTIPATH`, `NVME_VERBOSE_ERRORS`, and `NVME_HWMON` extend the core. `NVME_FABRICS` selects core and optionally keyring for TCP TLS. RDMA, FC, TCP, TCP TLS, and host auth select their required dependencies. `NVME_APPLE` depends on OF, block, Apple RTKit/SART, and Apple architecture or compile testing.

State and persistence behavior: Build-time only.

Dependencies and integration points: Controls object inclusion in `host/Makefile` and selects common auth/keyring symbols.

Risks and test signals: Config tests should cover host auth with fabrics transports, TCP TLS keyring selection, core as module versus built-in, and Apple compile-test builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/Makefile

Purpose: Maps NVMe host Kconfig symbols to kernel objects and modules.

Important APIs and flow: Builds `nvme-core.o`, PCI `nvme.o`, fabrics, RDMA, FC, TCP, and Apple modules as selected. `nvme-core-y` includes core/ioctl/sysfs/pr and conditionally adds verbose `constants.o`, tracing, multipath, zoned namespace support, fault injection, hwmon, and host auth. Transport modules map to their C files; `nvme-apple-y` maps to `apple.o`.

State and persistence behavior: Build-time only.

Dependencies and integration points: Integrates host core features and transport implementations with kbuild. Conditional inclusion determines whether symbols like verbose status strings and host auth lifecycle are available.

Risks and test signals: Build tests should cover modular combinations, especially `NVME_HOST_AUTH`, `NVME_VERBOSE_ERRORS`, and `NVME_APPLE`, and ensure no unresolved symbols when optional core features are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/apple.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/apple.c

Purpose: Implements the Apple ANS2 NVMe host driver for Apple SoCs. It adapts NVMe core and blk-mq to Apple firmware, RTKit coprocessor boot, SART shared-memory authorization, a single admin queue, a single I/O queue, and an Apple NVMMU tag-control-block model.

Important APIs and flow: Probe allocates platform state, attaches power domains, maps ANS/NVMe MMIO, initializes SART, reset, queues, DMA pools, mempool, tag sets, IRQ, RTKit, and `nvme_ctrl`, then schedules reset. Request flow uses `apple_nvme_queue_rq()`, `nvme_setup_cmd()`, PRP setup for simple or scatter-gather DMA, request start, and hardware-specific submit functions. Completion flow polls CQ phase bits, invalidates NVMMU TCBs, finds blk-mq requests by tag, and batches completions. Reset work boots or wakes RTKit, configures NVMMU/linear submission queues, enables the NVMe controller, creates I/O queues, updates queue counts, and starts the controller. Disable handles freeze/quiesce, queue deletion, controller disable, CQ draining, and request cancellation.

State and persistence behavior: Runtime state includes `struct apple_nvme`, queue memory, TCB arrays, tag sets, DMA pools, RTKit/SART handles, power-domain links, IRQ, and controller state. No persistent media metadata is modified beyond normal NVMe commands issued by upper layers.

Dependencies and integration points: Depends on NVMe core, blk-mq, Apple RTKit, Apple SART, reset framework, OF platform matching, power domains, DMA mapping/pools, mempools, IRQ handling, and PM sleep operations.

Risks and test signals: Hardware-specific ordering is delicate: tags are shared across queues on LSQ/NVMMU hardware, interrupts can be missed without the submission lock, abort is unsupported so timeouts reset the controller, and RTKit crashes are unrecoverable without reboot. Tests should cover probe deferral, reset/suspend/resume, request timeout polling, PRP list allocation/free, DMA mapping failures, queue disable races, power-domain cleanup, T8015 versus T8103 paths, and namespace teardown after reset failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/apple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/auth.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/auth.c

Purpose: Implements NVMe host-side in-band DH-HMAC-CHAP authentication for admin and I/O queues, including optional secure concatenation that derives/replaces NVMe/TCP TLS PSKs.

Important APIs and flow: Per-queue `struct nvme_dhchap_queue_context` tracks buffers, keys, DH transform, sequence numbers, challenges, responses, status, and auth result. `nvme_queue_auth_work()` performs the protocol: send negotiate, receive/validate challenge, parse hash/DH group, generate DH public/session key if needed, compute host response, send reply, receive success1, optionally compute/validate controller response, optionally send success2, and run secure concatenation. `nvme_auth_negotiate()` queues work; `nvme_auth_wait()` waits and clears sensitive state. `nvme_ctrl_auth_work()` authenticates admin first and reauthenticates authenticated I/O queues unless concatenation only needs admin. `nvme_auth_init_ctrl()`, `nvme_auth_stop()`, `nvme_auth_free()`, `nvme_init_auth()`, and `nvme_exit_auth()` manage controller and global workqueue/mempool lifecycle.

State and persistence behavior: Runtime state includes parsed host/controller DHCHAP keys, per-queue contexts, a global auth workqueue, and a 4 KiB slab/mempool for messages. Sensitive keys and session material are freed with zeroing. Secure concatenation can create/update a generated TLS PSK in the NVMe keyring and revoke the previous generated key.

Dependencies and integration points: Depends on NVMe fabrics auth send/receive commands, common auth crypto helpers, NVMe keyring TLS PSK helpers, controller options (`dhchap_secret`, `dhchap_ctrl_secret`, `concat`, `tls_key`), blk queues for admin/connect commands, and NVMe controller state transitions.

Risks and test signals: Failure handling sends failure2 when possible but leaves some failures as soft-state during reauth. `ctrl->transaction++` is not visibly locked here. Tests should cover invalid challenge payloads, unsupported hash/DH groups, bidirectional auth, secure concatenation with existing TLS keys, I/O queue authentication, reset/stop races, mempool exhaustion, auth command NVMe status versus errno, and sensitive cleanup after all exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/constants.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/constants.c

Purpose: Provides human-readable names for NVMe I/O opcodes, admin opcodes, fabrics opcodes, and status codes when verbose NVMe error reporting is enabled.

Important APIs and flow: Static sparse arrays map opcode/status numeric constants to strings. `nvme_get_error_status_str()` masks status with `NVME_SCT_SC_MASK` and returns a known status string or `"Unknown"`. `nvme_get_opcode_str()`, `nvme_get_admin_opcode_str()`, and `nvme_get_fabrics_opcode_str()` return known opcode names or `"Unknown"` and are exported.

State and persistence behavior: No runtime mutable state and no persistent state.

Dependencies and integration points: Depends on constants from `nvme.h` and is conditionally linked into `nvme-core` by `CONFIG_NVME_VERBOSE_ERRORS`. Callers use the exported helpers for diagnostics and trace/log output.

Risks and test signals: Tables can silently fall behind new NVMe opcodes/statuses. Tests should cover unknown values, status masking, fabrics auth opcodes, and build behavior with verbose errors disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/constants.c -->
