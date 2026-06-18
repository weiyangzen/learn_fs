# Group Research: group_1736_spdk_sources_virtualization_spdk_lib_blob_blobstore_h_sources_virtu_9ceabfdd4a86

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/blob/blobstore.h -->
# File Research: sources/virtualization/spdk/lib/blob/blobstore.h

Private blobstore implementation header. It defines the in-memory shape of blob metadata, blobstore state, per-channel request queues, open blob trees, snapshot clone lists, external snapshot tracking, and the request operation types used by blob I/O.

Key in-memory structures:
- `spdk_blob_mut_data` stores mutable persistent blob layout: cluster LBA array, metadata page chain, extent-page table, and allocation counts.
- `spdk_blob` keeps clean/active copies of mutable data, xattrs, flags, parent/snapshot state, lock/freeze state, extent-table parsing state, and pending persist queues.
- `spdk_blob_store` tracks metadata region geometry, backing device, allocation bitmaps, open blobs, snapshots, super blob id, blobstore type, unload state, and external snapshot unload coordination.
- `spdk_bs_channel` owns request-set memory, queued I/O, cluster allocation/free queues, temporary metadata pages, and external snapshot channels.

The on-disk portion defines blobstore metadata page, superblock, mask, xattr, flag, extent RLE, extent table, and extent page descriptor formats. It also defines blob feature/compatibility flag masks, descriptor type constants, metadata page size assertions, and extent-page sizing.

Inline helpers convert between bytes, LBAs, metadata pages, clusters, I/O units, blob ids, and extent-table slots. Blob ids deliberately set a high bit above the low 32-bit metadata page index to catch code that confuses page indices with blob ids. `bs_blob_io_unit_to_lba()` maps blob-relative I/O units through the active cluster table and returns zero for unallocated thin-provisioned clusters.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/blob/blobstore.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/blob/request.c -->
# File Research: sources/virtualization/spdk/lib/blob/request.c

Implements blobstore request-set execution. A single `spdk_bs_request_set` object is reused as a serial sequence, parallel batch, or deferred user operation, then returned to the channel free list after completion.

Major paths:
- `bs_call_cpl()` dispatches typed blobstore/blob completions, converting errors to `NULL` handles or invalid blob ids as appropriate.
- Sequence helpers allocate a request set from the channel, install callback trampoline state, optionally switch to an external snapshot backing channel, and issue reads, writes, vectored I/O, zero writes, or copy operations to either the main device or a supplied `spdk_bs_dev`.
- Batch helpers submit multiple device operations with a shared completion counter. Completion is deferred until outstanding operations reach zero and the batch has been closed.
- `bs_sequence_to_batch()` converts an active sequence into a batch for sub-operations that complete back into a sequence continuation.
- User-op helpers allocate deferred blob read/write/unmap/write-zero/readv/writev operations and later execute or abort them, returning the request set to the channel.

The code threads `ext_io_opts` into extended readv/writev paths when present, records blob request trace events, stores the first nonzero error in `set->bserrno`, and uses the same callback trampoline for both sequence and batch completion.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/blob/request.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/blob/request.h -->
# File Research: sources/virtualization/spdk/lib/blob/request.h

Private request API for blobstore asynchronous work. It defines completion variants for blobstore operations, blob operations, blob-id returns, blob-handle returns, and nested sequences.

`struct spdk_bs_request_set` is the central reusable state object. It contains the user completion, accumulated error, owning blobstore channel, optional backing device channel for external snapshot clones, low-level `spdk_bs_dev_cb_args`, a union for sequence/batch/user-op state, optional extended I/O options, and a queue link.

The header declares:
- sequence lifecycle and device I/O helpers,
- batch open/read/write/unmap/write-zero/close helpers,
- sequence-to-batch conversion,
- deferred user-op allocation/execution/abort helpers,
- the shared completion dispatcher `bs_call_cpl()`.

It is the internal contract between blob metadata/data paths and the channel request-pool implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/blob/request.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/blob/zeroes.c -->
# File Research: sources/virtualization/spdk/lib/blob/zeroes.c

Implements a singleton read-only `spdk_bs_dev` that represents an infinite zero-filled backing device. Reads and readv fill the supplied buffer/iovecs with zeroes and complete successfully. Extended readv can use `spdk_memory_domain_memzero()` when a memory domain is supplied, falling back to local `memset()` otherwise.

All mutating operations, including write, writev, writev_ext, write_zeroes, and unmap, complete with `-EPERM` and assert false. The device reports every range as valid and zero-filled, has `UINT64_MAX` 512-byte blocks, and cannot translate LBAs to a physical base.

`bs_create_zeroes_dev()` returns the global device instance, and `blob_backed_with_zeroes_dev()` checks whether a blob’s backing device is that singleton.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/blob/zeroes.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/conf/Makefile -->
# File Research: sources/virtualization/spdk/lib/conf/Makefile

Builds the SPDK `conf` shared/static library from `conf.c`. It sets the library ABI version to `8.0`, points at `spdk_conf.map`, includes common SPDK make rules, and delegates actual library build mechanics to `mk/spdk.lib.mk`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/conf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/conf/conf.c -->
# File Research: sources/virtualization/spdk/lib/conf/conf.c

Implements SPDK’s legacy INI-style configuration parser. A config is a linked list of sections; each section owns a linked list of items; each item owns a linked list of string values. `spdk_conf_allocate()` creates a config with section merging enabled by default, and `spdk_conf_free()` recursively releases sections, items, values, and the stored filename.

Lookup APIs provide default-config fallback, section iteration, case-insensitive section/key matching, section-prefix matching, section numeric suffix extraction, string value retrieval by key/value index, integer conversion via `spdk_strtol()`, and boolean parsing for Yes/Y/True and No/N/False.

Parsing behavior:
- `[section]` lines create or merge sections and derive `sp->num` from the first digit in the section name.
- parameter lines require a current section, split the key on whitespace or `=`, then split values on whitespace with quote-aware `spdk_strsepq()`.
- `#` comments and blank lines are skipped after leading whitespace.
- lines ending in backslash-newline are concatenated with the next physical line.
- `fgets_line()` grows dynamically for lines longer than the temporary 1024-byte buffer.

The parser logs allocation, syntax, and open errors but continues reading after per-line parse errors. `spdk_conf_set_as_default()` installs the process-wide default config, and `spdk_conf_disable_sections_merge()` preserves duplicate section instances.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/conf/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/dma/Makefile -->
# File Research: sources/virtualization/spdk/lib/dma/Makefile

Builds the SPDK `dma` library from `dma.c`. It sets ABI version `7.0`, uses `spdk_dma.map`, includes common SPDK make rules, and delegates library generation to `mk/spdk.lib.mk`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/dma/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/dma/dma.c -->
# File Research: sources/virtualization/spdk/lib/dma/dma.c

Implements SPDK memory-domain registration and data-transfer dispatch. A global tail queue of `spdk_memory_domain` objects is protected by `g_dma_mutex`; a constructor registers the built-in `"system"` DMA domain.

`spdk_memory_domain_create()` validates optional context sizing, allocates the domain plus optional user-context tail storage, duplicates the id string, copies the public context prefix, copies user context bytes, assigns the device type, and inserts the domain in the global list. Destroy removes non-system domains and frees context/id memory.

Setter APIs install callbacks for translation, invalidation, pull, push, transfer, and memzero. Accessors expose context, user context, DMA device type, and DMA device id. Data movement APIs validate required arguments and return `-ENOTSUP` when the corresponding callback is absent.

Iteration helpers find the first or next domain, optionally filtered by id. `spdk_dma_device_type_get_name()` maps built-in RDMA, DMA, ACCEL, vendor-specific, and unknown type values to strings.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/dma/dma.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_bus.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_bus.h

Vendored DPDK 22.07 bus interface header used by SPDK compatibility code. It exposes the full bus object layout and bus driver callback typedefs in the public header.

It defines IOVA modes, scan/probe/find/plug/unplug/parse/devargs parsing callbacks, bus-level DMA map/unmap callbacks, hot-unplug and SIGBUS handlers, scan policies, bus configuration, and `rte_bus_get_iommu_class_t`.

`struct rte_bus` contains the registered-bus list link, name, scan/probe/find/plug/unplug/parse/devargs methods, DMA map/unmap methods, configuration, IOMMU class method, device iterator, and hot-unplug/SIGBUS handlers. The header also declares bus registration, unregistration, scan/probe/dump/find APIs and the `RTE_REGISTER_BUS` constructor macro.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_bus.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_bus_pci.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_bus_pci.h

Vendored DPDK 22.07 PCI bus header. It exposes PCI device and driver internals, PCI bus lists, registration helpers, resource mapping APIs, config-space access, and I/O port access.

Important definitions:
- `struct rte_pci_device` embeds `struct rte_device`, PCI address/id, BAR resources, interrupt handles, driver pointer, SR-IOV VF count, kernel driver type, PCI name, and VFIO request interrupt handle.
- `struct rte_pci_driver` embeds `struct rte_driver`, carries a PCI bus pointer, probe/remove callbacks, optional DMA map/unmap callbacks, id table, and driver flags.
- `struct rte_pci_bus` embeds the generic bus and owns device/driver lists.
- driver flags describe BAR mapping, write combining, reprobe support, link/removal interrupts, keeping mapped resources, and requiring IOVA-as-VA.

The header declares PCI map/unmap/dump, extended capability lookup, bus-master toggling, driver register/unregister, config read/write, and PCI I/O port map/read/write/unmap APIs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_bus_pci.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_dev.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_dev.h

Vendored DPDK 22.07 device/driver public header. It exposes generic driver and device layouts, device events, hotplug/probe/remove APIs, device iteration, PMD metadata export macros, and device-level DMA map/unmap prototypes.

`struct rte_driver` contains the driver list link, name, and alias. `struct rte_device` contains the device list link, name, assigned driver, bus pointer, NUMA node, and latest devargs. `struct rte_mem_resource` stores physical address, length, and mapped virtual address.

The header also defines event callback registration/unregistration/processing, event monitor start/stop, hotplug handling enable/disable, device iterator initialization/next APIs, `RTE_DEV_FOREACH`, PMD export macros for names, PCI tables, parameter strings, and kernel-module dependencies. DMA map/unmap are marked experimental and require memory pre-registration through DPDK external memory APIs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_dev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/bus_driver.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/bus_driver.h

Vendored DPDK 22.11 internal bus-driver header. In 22.11, bus driver internals moved out of the public `rte_bus.h`, so this file carries the callback typedefs, full `struct rte_bus`, bus list type, scan policy/config definitions, and registration macros needed by SPDK compatibility code.

Compared with the 22.07 public header, this internal header adds `rte_bus_cleanup_t` and a `cleanup` method in `struct rte_bus`, includes newer internal annotation via `__rte_internal` on register/unregister APIs, and depends on the public `rte_bus.h`, `rte_dev.h`, EAL, and tailq headers.

It keeps the same core model: buses scan devices, probe drivers, find/plug/unplug devices, parse names/devargs, map/unmap DMA, expose IOMMU class, iterate devices, and handle hot-unplug/SIGBUS events.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/bus_driver.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/bus_pci_driver.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/bus_pci_driver.h

Vendored DPDK 22.11 internal PCI bus-driver header. It supplies PCI device and PCI driver internals that are no longer present in the public `rte_bus_pci.h`.

It defines PCI kernel-driver kinds, `struct rte_pci_device`, PCI conversion macros, `RTE_PCI_DEVICE`, PCI probe/remove and DMA map/unmap callback types, `struct rte_pci_driver`, driver flags, internal PCI driver register/unregister APIs, and the private `rte_pci_ioport` representation.

Differences from 22.07 include an added `bus_info` string on `struct rte_pci_device`, removal of the explicit `struct rte_pci_bus *bus` member from `struct rte_pci_driver`, and internal annotations for sysfs-path and registration functions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/bus_pci_driver.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/dev_driver.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/dev_driver.h

Vendored DPDK 22.11 internal device-driver header. It defines the concrete `struct rte_driver` and `struct rte_device` layouts that the 22.11 public `rte_dev.h` only forward-declares.

`struct rte_driver` retains the driver list link, name, and alias. `struct rte_device` retains the device list link, name, assigned driver, bus pointer, NUMA node, and latest devargs, and adds a `bus_info` string for bus-specific device description.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/dev_driver.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_bus.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_bus.h

Vendored DPDK 22.11 public bus API header. It forward-declares `struct rte_bus` and `struct rte_device` instead of exposing bus internals.

The public API provides bus-name retrieval, global bus scan/probe/dump, bus comparison type, bus find-by-callback/name/device, and common IOMMU class retrieval. Driver-facing struct definitions and registration helpers are intentionally split into `bus_driver.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_bus.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_bus_pci.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_bus_pci.h

Vendored DPDK 22.11 public PCI bus API header. It forward-declares PCI device, driver, and I/O port types, then exposes only public PCI operations.

Declared APIs cover PCI BAR resource map/unmap, PCI bus dump, extended capability lookup, bus-master enable/disable, config-space read/write, and I/O port map/unmap/read/write. PCI device/driver structs, driver registration, flags, and helper macros live in the internal `bus_pci_driver.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_bus_pci.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_dev.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_dev.h

Vendored DPDK 22.11 public device API header. It forward-declares bus, devargs, device, and driver structs, adds accessor functions for driver name, device bus, bus info, devargs, driver, device name, and NUMA node, and keeps public device management APIs.

It defines device event types/callbacks, deprecated function-pointer guard macros, device policy enum, memory resource representation, device name length, probed-state query, hotplug add/remove, device probe/remove, comparison callback type, PMD export metadata macros, device iterator APIs, event callback APIs, event monitor start/stop, hotplug handling enable/disable, and experimental device DMA map/unmap.

The concrete driver/device struct definitions are intentionally moved to `dev_driver.h`, matching DPDK’s 22.11 public/internal header split.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_dev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/Makefile -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/Makefile

Builds the SPDK `env_dpdk` library with ABI version `17.0`. It compiles core environment, memory, PCI, initialization, threading, DPDK PCI compatibility, PCI event, SIGBUS, and device-specific PCI helper sources, including both DPDK 22.07 and 22.11 compatibility translation units.

The makefile also generates `spdk_dpdklibs` pkg-config files from the deduplicated DPDK library list, rewrites the env_dpdk pkg-config `Requires:` line to depend on `spdk_dpdklibs`, and provides install/uninstall targets for the generated DPDK dependency pkg-config file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/env.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/env.c

Implements SPDK environment wrappers over DPDK allocation, memzone, mempool, timing, affinity, ring, and memory-stat APIs.

Allocation wrappers use DPDK malloc/zmalloc/realloc/free with cache-line minimum alignment and optional NUMA fallback unless `mem_enforce_numa()` has been enabled. DMA allocation is the same allocator with SPDK DMA/share flags. Memzone reservation translates SPDK flags to DPDK memzone flags, zeroes successful reservations, and supports aligned or cache-line-aligned variants.

Mempool wrappers create DPDK mempools with capped per-lcore cache size, optional object constructors, optional NUMA fallback, and wrappers for get/put bulk, count, object iteration, memory-region iteration, lookup, and free. Ring wrappers create exact-size DPDK rings with SP/SC, MP/SC, or MP/MC flags and auto-generated names.

Other responsibilities include process-primary detection, tick/timer wrappers, microsecond delay, pause, thread unaffinitization and scoped unaffinitized callback execution, DPDK memory-stat dump/get APIs, thread id retrieval, and NUMA-enforcement enablement.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/env.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/env.mk -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/env.mk

Makefile fragment that computes DPDK include flags, library lists, and linker arguments for SPDK’s DPDK environment.

It locates DPDK include/library directories from config, builds a base DPDK library list, conditionally adds power, crypto, compressdev, vhost, FC/hash, QAT, mlx5, UADK, and optional DPDK power-driver libraries, then sorts/deduplicates them for static or shared linking.

The fragment sets `ENV_CFLAGS`/`ENV_CXXFLAGS` with the DPDK include path and `ALLOW_EXPERIMENTAL_API`, builds shared-library linker args with rpath and no-as-needed handling, builds static linker args with whole-archive handling plus private dependencies, and adds platform/private libraries such as IPSec_MB, bsd, archive, mlx5/ibverbs, numa, dl, or execinfo when required.

It also carries compiler workarounds for newer GCC warnings and `-fcommon` issues in DPDK-related code.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/env.mk -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/env_internal.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/env_internal.h

Internal env_dpdk header shared by environment initialization, PCI, and memory code. It requires DPDK 21.11 or newer and defines address-space constants for the two-level/three-level memory maps: 256 TB virtual range, 1 GB chunks, and masks.

It declares initialization/finalization hooks for PCI environment, memory registration map, and vtophys map, plus IOMMU DMA BAR map/unmap helpers, PCI-device add/remove notifications for vtophys, and option-driven toggles for hugepage use, vtophys use, and NUMA enforcement.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/env_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/init.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/init.c

Builds and runs DPDK EAL initialization for SPDK. `spdk_env_opts_init()` fills defaults for name, core mask, shared memory id, memory size, main core, memory channels, base virtual address, and newer option fields guarded by `opts_size`.

`build_eal_cmdline()` constructs DPDK argv from SPDK env options. It handles program name, single-process `--no-shconf`, mutually exclusive core mask vs lcore map, core-mask-to-core-list conversion, memory channels/size, no-huge validation, NUMA enforcement, main lcore, no-pci/vtophys disable, hugepage unlink/single-file/hugedir options, PCI allow/block lists, default telemetry/log-level suppression, IOVA-mode selection, base virtual address, match-allocation, file prefix/proc type, VF token, and user-supplied `env_context` tokenization.

Linux/x86 helpers inspect `/proc/cpuinfo` and Intel IOMMU capability sysfs files to decide whether VA IOVA is safe; otherwise SPDK forces PA mode. PowerPC Linux also forces PA mode. No-huge mode forces legacy memory and VA IOVA and requires a configured memory size.

`spdk_env_init()` initializes OpenSSL config handling, prints the SPDK/DPDK versions and EAL arguments, calls `rte_eal_init()` with a copied argv because DPDK mutates it, determines legacy memory mode, then runs post-init hooks for PCI, memory maps, and vtophys. Reinitialization after SPDK-owned init only refreshes PCI state. Finalization tears down vtophys, memory map, PCI state, and generated EAL arguments; a high-priority destructor calls `rte_eal_cleanup()` only when SPDK initialized DPDK itself.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/init.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/memory.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/memory.c

Implements SPDK’s DPDK-backed memory registration, memory maps, NUMA lookup, virtual-to-physical translation, and VFIO/IOMMU DMA mapping.

The generic `spdk_mem_map` is a sparse 256 TB virtual-address map. It stores 2 MB translations in second-level 1 GB tables and can fall back to 4 KB third-level maps for unaligned edges or finer-grained regions. Registration state uses a dedicated map with `REG_MAP_REGISTERED` and `REG_MAP_NOTIFY_START` flags so exact registration regions can be walked and unregistered in the same chunks they were registered.

Public memory registration APIs:
- `spdk_mem_map_alloc/free()` create maps and replay current registrations to notify callbacks.
- `spdk_mem_register()` validates 4 KB alignment, rejects overlapping registered ranges, marks pages registered, and notifies maps.
- `spdk_mem_unregister()` requires unregistering whole registered regions, handles 4 KB submaps inside 2 MB regions, clears registration state, and sends unregister notifications in reverse map order.
- `spdk_mem_reserve()` allocates map space with default translations without marking memory registered.
- `spdk_mem_map_set_translation()`, `clear_translation()`, and `translate()` manage and query translations, coalescing contiguous translated ranges through an optional callback.

`mem_map_init()` creates the registration map, registers a DPDK memory hotplug callback outside legacy-memory mode, and walks existing DPDK memsegs to register them. The hotplug callback registers/free-unregisters DPDK memory and, for external DPDK initialization without guaranteed `--match-allocations`, marks segments as `DO_NOT_FREE`.

Vtophys translation first uses DPDK memsegs, then PCI BAR resources, then DPDK/pagemap IOVA translation for non-DPDK memory. It supports IOVA-as-VA with VFIO/IOMMU by mapping virtual addresses as IOVAs, and IOVA-as-PA by mapping physical addresses, rejecting unsupported 4 KB PA-mode pages. PCI BAR translations account for IOMMU VA mode where the virtual address is already the DMA address.

VFIO support discovers DPDK’s `/dev/vfio/vfio` container fd, tracks whether normal or noiommu VFIO is active, stores requested DMA mappings, defers mapping until the first SPDK-managed PCI device is added, reference-counts physical mappings, unmaps on final device removal, and provides BAR-specific map/unmap helpers.

`vtophys_init()` creates the physical-refcount map, optional NUMA map, and optional vtophys map with notify callbacks. `spdk_vtophys()` returns translated DMA/physical addresses plus page offset, `spdk_mem_get_numa_id()` returns mapped socket id or `SPDK_ENV_NUMA_ID_ANY`, and `spdk_mem_get_fd_and_offset()` exposes DPDK memseg fd/offset for shared-memory consumers. `mem_disable_huge_pages()` and `mem_disable_vtophys()` disable optional maps based on env options.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/memory.c -->