# Research Group: subset-b-005900

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pagemap.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pagemap.h

Purpose: `pagemap.h` is the central page-cache and filemap interface header for the Ceph client kernel tree copy. It exposes address-space invalidation, writeback waiting/error reporting, folio allocation and lookup, folio private data helpers, readahead control, folio/page locking and writeback wait APIs, and helpers for translating between file offsets, page indices, folios, and VMAs.

Important APIs/types/functions: exported declarations include `invalidate_mapping_pages()`, `invalidate_inode_pages2_range()`, `filemap_fdatawrite*()`, `filemap_write_and_wait_range()`, `filemap_check_errors()`, `__filemap_get_folio_mpol()`, `pagecache_get_page()`, `filemap_get_folios*()`, `read_cache_folio()`, `filemap_add_folio()`, `filemap_remove_folio()`, `filemap_migrate_folio()`, readahead submission functions, and writeback completion/wait functions. Inline helpers define mapping flag accessors, folio order support, page-cache get/grab wrappers, `write_begin_get_folio()`, `folio_attach_private()`/`folio_detach_private()`, locking wrappers, `filemap_range_needs_writeback()`, and readahead iteration helpers.

Control flow and state: the header encodes common control paths around `struct address_space`: invalidate or flush a mapping, sample or set writeback errors through `errseq_t`, select folio allocation order, then lookup/create locked folios using `FGP_*` flags. Readahead state lives in `struct readahead_control`; `_index`, `_nr_pages`, and `_batch_count` advance as `readahead_folio()` or `__readahead_batch()` consumes locked folios from the mapping XArray. Persistence state is in memory only but represents durable-file correctness: writeback errors are persisted in `mapping->wb_err`, superblock `s_wb_err`, and legacy `AS_EIO`/`AS_ENOSPC` bits until observed by fsync-style paths. Folio private data increments the folio reference count and must be detached before reclaim.

Dependencies and integration points: this header depends on MM/VFS types from `mm.h`, `fs.h`, XArray-backed page cache state, highmem, hugetlb, GFP flags, user access fault-in helpers, errseq, folio flags, and block/writeback infrastructure. Filesystems, including network filesystems such as Ceph, use it from read, write_begin/write_end, direct-I/O invalidation, readahead, truncate, mmap fault, and writeback paths.

Risks and test signals: risks concentrate around lock ordering, refcount leaks from folio private data, stale writeback error reporting, wrong large-folio alignment/order, and races with truncation or reclaim. Tests should exercise buffered read/write, direct-I/O invalidation, fsync error propagation, readahead over large folios, mmap faults against truncation, dirty/writeback accounting, and lockdep/KASAN/VM_BUG_ON signals under reclaim and concurrent truncate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pagemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pagewalk.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pagewalk.h

Purpose: `pagewalk.h` defines generic page-table and folio-walk callback contracts. It lets callers traverse user or kernel page-table ranges, inspect or install entries, skip VMAs, and temporarily lock page-table entries that map a folio.

Important APIs/types/functions: `enum page_walk_lock`, `struct mm_walk_ops`, `enum page_walk_action`, `struct mm_walk`, `walk_page_range()`, `walk_kernel_page_table_range()`, lockless kernel walking, `walk_page_range_vma()`, `walk_page_vma()`, `walk_page_mapping()`, `folio_walk_flags_t`, `FW_ZEROPAGE`, `enum folio_walk_level`, `struct folio_walk`, `folio_walk_start()`, and `folio_walk_end()`.

Control flow and state: a caller fills `mm_walk_ops`, chooses a lock policy, and passes private state through `struct mm_walk`. Walk callbacks run from top-level entries down to PTEs; `pud_entry` and `pmd_entry` may set `walk->action` to descend, continue, or retry. `test_walk`, `pre_vma`, and `post_vma` gate VMA-level traversal. `install_pte` changes missing-entry behavior by forcing allocation and invoking the install hook at PTE level.

Dependencies and integration points: it depends on `linux/mm.h`, page-table types, VMA locking helpers, and architecture-specific folded page-table levels. It integrates with memory introspection, migration, NUMA, soft-dirty, pagemap, idle-page tracking, and filesystem mapping walks.

Risks and test signals: risks include incorrect mmap/VMA lock mode, unsafe access after hugetlb callbacks drop locks, mishandled folded levels, failure to split or handle huge PMDs, and leaked PTE mappings if `folio_walk_end()` is skipped. Test signals include lockdep, page-table debug checks, hugepage walk coverage, VMA skip/abort behavior, and install-PTE allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pagewalk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/panic.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/panic.h

Purpose: `panic.h` exports the kernel panic/oops/taint public interface. It declares panic entry points, panic synchronization state, panic policy knobs, and taint flag definitions used across crash handling and diagnostics.

Important APIs/types/functions: core calls are `panic()`, `vpanic()`, `nmi_panic()`, `check_panic_on_warn()`, `oops_enter()`, `oops_exit()`, `oops_may_print()`, `panic_try_start()`, `panic_reset()`, `panic_in_progress()`, `panic_on_this_cpu()`, `panic_on_other_cpu()`, `set_arch_panic_timeout()`, `add_taint()`, `test_taint()`, `get_taint()`, `print_tainted()`, and `print_tainted_verbose()`. State includes `panic_cpu`, `panic_redirect_cpu`, `panic_timeout`, `panic_print`, `panic_on_oops`, `panic_on_warn`, `panic_on_taint`, and `crash_kexec_post_notifiers`.

Control flow and state: panic paths claim a global panic CPU, optionally redirect execution to a configured CPU, print diagnostics, run configured crash behavior, and never return. Taint state accumulates bit flags such as proprietary modules, warnings, bad pages, livepatch, or test taints; it persists in kernel memory for the boot lifetime and influences diagnostics and policy.

Dependencies and integration points: depends on compiler attributes, stdarg/types, atomics, pt_regs, crash-kexec, sysctl, watchdog/oops paths, stack protector failure, and architecture init code.

Risks and test signals: risks include double-panic races, unsafe NMI context behavior, incorrect taint indexing, and misconfigured timeout defaults. Tests rely on fault injection, WARN/oops paths, panic-on-warn/oops sysctls, taint reporting, crash-kexec notifier ordering, and architecture panic timeout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/panic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/panic_notifier.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/panic_notifier.h

Purpose: `panic_notifier.h` exposes the atomic panic notifier chain and the `crash_kexec_post_notifiers` policy flag to subsystems that need last-chance panic callbacks.

Important APIs/types/functions: it declares `panic_notifier_list` as an `atomic_notifier_head` and `crash_kexec_post_notifiers` as a global boolean. There are no inline helpers; registration uses the generic notifier API from `linux/notifier.h`.

Control flow and state: panic code invokes the notifier list during panic processing. Registered callbacks run in a highly constrained failure context, and the boolean controls whether crash-kexec happens after notifier execution. State is global boot-lifetime kernel state.

Dependencies and integration points: depends on notifier and type definitions. Integrates with panic core, crash dump capture, platform watchdogs, logging backends, firmware notifiers, and drivers that need emergency shutdown notification.

Risks and test signals: notifier callbacks can deadlock, sleep, recurse into broken subsystems, or delay crash capture. Tests should check notifier registration/unregistration, callback ordering, panic-time constraints, and crash-kexec behavior with the post-notifier knob enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/panic_notifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/papr_scm.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/papr_scm.h

Purpose: `papr_scm.h` defines PAPR persistent-memory/SCM health and performance constants for IBM Power platform SCM devices.

Important APIs/types/functions: the file defines health bits such as `PAPR_PMEM_UNARMED`, `PAPR_PMEM_SHUTDOWN_DIRTY`, `PAPR_PMEM_EMPTY`, critical/fatal/unhealthy/non-critical health flags, encryption and scrub state, and `PAPR_PMEM_SAVE_FAILED`. It also groups those bits into masks like `PAPR_PMEM_UNARMED_MASK`, `PAPR_PMEM_BAD_SHUTDOWN_MASK`, `PAPR_PMEM_BAD_RESTORE_MASK`, `PAPR_PMEM_SMART_EVENT_MASK`, and `PAPR_PMEM_SAVE_MASK`.

Control flow and state: there is no executable control flow. The state represented is firmware-reported persistent-memory health, shutdown persistence status, restore status, and smart-event conditions. Bit numbering uses high-order PAPR convention with `1ULL << (63 - n)`.

Dependencies and integration points: used by PAPR SCM/NVDIMM drivers and user-visible health reporting paths. `PAPR_SCM_PERF_STATS_EYECATCHER` uses `__stringify`, so including contexts must provide the usual kernel macro environment.

Risks and test signals: risks are wrong bit interpretation, endian/bit-position confusion, and incomplete health-mask handling causing unsafe use of unarmed or dirty persistent memory. Tests should validate synthetic firmware bitmaps, smart event filtering, save-failure reporting, and perf stats version/eyecatcher compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/papr_scm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/parman.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/parman.h

Purpose: `parman.h` declares a manager for linear priority array areas, used by drivers that must keep priority-ordered items packed in hardware or software tables while supporting resize and move operations.

Important APIs/types/functions: it defines `enum parman_algo_type` with `PARMAN_ALGO_TYPE_LSORT`, `struct parman_item` carrying a list node and index, `struct parman_prio` carrying priority and item list, `struct parman_ops` with `base_count`, `resize_step`, `resize()`, `move()`, and algorithm selection, plus `parman_create()`, `parman_destroy()`, priority init/fini, and item add/remove functions.

Control flow and state: callers create a `struct parman`, initialize priority buckets, then add or remove items. The implementation can resize backing storage and move contiguous index ranges through caller-provided callbacks to maintain sorted priority layout. State is in list heads, per-item indices, and the opaque manager.

Dependencies and integration points: depends on `linux/list.h` and caller-provided storage movement. It integrates with networking/switch drivers and other table-backed subsystems that need priority insertion without exposing algorithm internals.

Risks and test signals: risks include failed resize rollback, incorrect move ranges corrupting hardware tables, stale `item->index`, and priority-list lifetime mistakes. Tests should cover add/remove across priorities, resize boundaries, move callback ordering, duplicate/fini misuse, and low-memory failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/parman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/parport.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/parport.h

Purpose: `parport.h` is the public kernel interface for the parallel-port core. It models low-level port operations, high-level parport drivers, attached devices, IEEE1284 protocol state, ownership arbitration, proc/device-model integration, and architecture-specific dispatch.

Important APIs/types/functions: key types include `struct parport_operations`, `struct pardevice`, `enum ieee1284_phase`, `struct ieee1284_info`, `struct parport`, `struct parport_driver`, and `struct pardev_cb`. APIs include port register/announce/remove, driver register/unregister, port lookup, refcounting, device register/unregister, `parport_claim()`, `parport_claim_or_block()`, `parport_release()`, `parport_yield()`, `parport_yield_blocking()`, IEEE1284 read/write/negotiate helpers, daisy-chain helpers, proc registration, and generic IRQ handling.

Control flow and state: low-level drivers register a `parport` with register access callbacks, announce it, and high-level drivers attach devices. Devices arbitrate ownership through claim/release and may be preempted or woken by resource management. `parport_yield*()` releases and reclaims only when waiters exist and the device timeslice expired. State includes current active device, wait queue, locks, IEEE1284 phase, probe info, mux/daisy selection, default timeslice, and per-device saved port state.

Dependencies and integration points: depends on jiffies, procfs, spin/rw locks, wait queues, semaphores, device model, IRQ handling, architecture ptrace, UAPI parport constants, and optionally `parport_pc.h` for direct PC fast paths.

Risks and test signals: risks include ownership misuse after release, IRQ callback races under `cad_lock`, deadlocks in preempt/wakeup callbacks, incorrect mux/daisy state, and driver/device lifetime refcount bugs. Tests should cover multi-device contention, blocking and nonblocking claim, IEEE1284 phase transitions, IRQ dispatch, proc registration, hotplug detach, and PC-vs-generic dispatch builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/parport_pc.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/parport_pc.h

Purpose: `parport_pc.h` provides PC-compatible parallel-port register definitions, private driver state, and inline I/O helpers used by the parport core when PC hardware is supported.

Important APIs/types/functions: register macros compute `DATA`, `STATUS`, `CONTROL`, `EPPADDR`, `EPPDATA`, `FIFO`, `CONFIGA/B`, and `ECONTROL` offsets. `struct parport_pc_private` stores control/ECR shadow state, writable masks, FIFO geometry, DMA buffer metadata, and port linkage. Inline operations include data read/write, control frobbing, data direction changes, control read/write, status read, and IRQ enable/disable. External APIs include resource claim/release, probe, and unregister.

Control flow and state: callers write data through `outb()` and read through `inb()`. Control register writes update a software shadow (`priv->ctr`) after masking by writable bits; direction bit changes route through `parport_pc_data_reverse()` or `_forward()`. IRQ enable/disable toggles the control interrupt bit. Debug builds can dump ECR/DCR/DSR state.

Dependencies and integration points: depends on `asm/io.h`, PC I/O port semantics, parport core structs, DMA addressing, printk, and UAPI control-bit definitions. It is included directly by `parport.h` for optimized PC-only dispatch.

Risks and test signals: risks include stale control shadow state, writing non-writable bits, unsafe direct I/O on absent hardware, DMA buffer lifetime issues, and legacy callers using bit 0x20 instead of direction helpers. Tests should cover register read/write emulation, ECR presence variants, IRQ toggling, resource claim/unclaim, probe failure, and debug-state output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/parport_pc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/parser.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/parser.h

Purpose: `parser.h` declares the generic simple option parser used primarily by filesystem mount/argument parsing.

Important APIs/types/functions: `struct match_token` maps integer tokens to pattern strings, `match_table_t` is an array of those mappings, `MAX_OPT_ARGS` limits captured substrings to three, and `substring_t` records a matched range. Functions include `match_token()`, numeric converters for signed, unsigned, u64, octal, and hex, `match_wildcard()`, `match_strlcpy()`, and `match_strdup()`.

Control flow and state: callers define a match table, pass an option string to `match_token()`, and receive a token plus substring captures for later conversion. State is transient in caller-provided strings and `substring_t` arrays; `match_strdup()` allocates a copy.

Dependencies and integration points: implemented by `lib/parser.c` and used by filesystem option parsers, module options, and other kernel components needing small pattern matching without a full parser.

Risks and test signals: risks include modifying input strings unexpectedly, failing to handle missing captures, overflow or invalid numeric conversion, and wildcard overmatch. Tests should cover table fall-through, malformed numbers, max argument count, substring copy bounds, allocation failure, and representative filesystem mount option strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/part_stat.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/part_stat.h

Purpose: `part_stat.h` defines per-CPU block-device partition statistics and macros for efficient updates/readout of I/O counters.

Important APIs/types/functions: `struct disk_stats` contains per-stat-group nanoseconds, sectors, I/O counts, merges, `io_ticks`, and local in-flight counters. Macros include `part_stat_lock()`, `part_stat_unlock()`, `part_stat_get_cpu()`, `part_stat_get()`, `part_stat_read()`, `part_stat_set_all()`, `part_stat_read_accum()`, add/sub/inc/dec helpers, local in-flight helpers, and `bdev_count_inflight()`.

Control flow and state: update callers disable preemption, update the current CPU's `bd_stats`, and mirror normal counters to the whole-disk device when operating on a partition. Reads aggregate all possible CPUs. In-flight uses `local_t` for read/write directions and is read per CPU or aggregated by the external helper.

Dependencies and integration points: depends on `linux/blkdev.h`, `asm/local.h`, per-CPU APIs, block-device partition helpers, and stat group constants. It integrates with block accounting, `/proc/diskstats`, sysfs statistics, and request completion paths.

Risks and test signals: risks include missing preemption protection during updates, double-counting whole-disk stats, field type assumptions in `TYPEOF_UNQUAL`, and stale per-CPU aggregation after CPU hotplug. Tests should validate diskstats under partition and whole-disk I/O, concurrent updates, in-flight counts, reset paths, and CPU-hotplug accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/part_stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pata_arasan_cf_data.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pata_arasan_cf_data.h

Purpose: `pata_arasan_cf_data.h` provides platform data for the Arasan CompactFlash PATA host controller.

Important APIs/types/functions: `struct arasan_cf_pdata` carries `cf_if_clk` encoded by `CF_IF_CLK_*` constants from 25 MHz through 200 MHz and a `quirk` bitmask with `CF_BROKEN_PIO`, `CF_BROKEN_MWDMA`, and `CF_BROKEN_UDMA`. `set_arasan_cf_pdata()` stores the platform data pointer into `pdev->dev.platform_data`.

Control flow and state: board/platform setup initializes static platform data, calls the setter, and the PATA driver consumes clock and quirk information during probe to choose transfer modes. State persists as platform-device data for the device lifetime.

Dependencies and integration points: depends on `linux/platform_device.h` and integrates with the Arasan CF low-level ATA driver, platform board files, and libata mode selection.

Risks and test signals: risks include dangling platform-data lifetime, invalid clock encoding, and underdeclared quirks causing unsupported transfer modes. Tests should probe with each quirk combination, verify mode masks, and validate board data survives device probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pata_arasan_cf_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/patchkey.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/patchkey.h

Purpose: `patchkey.h` defines the endian-sensitive `_PATCHKEY()` macro kept for soundcard/awe compatibility and includes the UAPI patchkey definition.

Important APIs/types/functions: `_PATCHKEY(id)` expands differently on big-endian and little-endian builds after including `asm/byteorder.h` and `uapi/linux/patchkey.h`. The header explicitly tells users not to include it directly and to use soundcard headers instead.

Control flow and state: there is no runtime flow or mutable state. The macro transforms an ID into the historical patch key constant at compile time according to byte order.

Dependencies and integration points: depends on architecture byte-order definitions and UAPI sound interfaces. It integrates with OSS-compatible sound headers and any legacy userspace-visible structures expecting this encoding.

Risks and test signals: risks include wrong byte-order detection, direct inclusion outside intended wrappers, and breaking userspace ABI if the macro changes. Build tests should compile on big- and little-endian targets and compare generated constants with UAPI expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/patchkey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/path.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/path.h

Purpose: `path.h` defines the VFS `struct path` pair of mount and dentry plus reference-management helpers.

Important APIs/types/functions: `struct path` contains `struct vfsmount *mnt` and `struct dentry *dentry` with layout randomization. APIs are `path_get()`, `path_put()`, `path_equal()`, and `__free_path_put` for cleanup attributes.

Control flow and state: path users hold a counted reference with `path_get()` and release it with `path_put()`. `path_equal()` compares identity by pointer equality of both mount and dentry. State is the referenced VFS object pair; persistence is lifetime-managed by mount/dentry refcounts.

Dependencies and integration points: integrates throughout VFS, file descriptors, namespace lookup, open paths, mount handling, security hooks, and cleanup-attribute based automatic release.

Risks and test signals: risks include leaking references, using uninitialized paths with cleanup attributes, comparing dentries without mount context, and use-after-put. Tests should exercise lookup/open/close paths, mount namespace cases, cleanup-attribute paths initialized to zero, and refcount debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pch_dma.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pch_dma.h

Purpose: `pch_dma.h` declares Intel PCH DMA slave configuration used by platform drivers binding to the DMAengine subsystem.

Important APIs/types/functions: `enum pch_dma_width` defines 1, 2, and 4 byte transfer widths. `struct pch_dma_slave` carries the DMA controller device, channel ID, TX/RX register DMA addresses, and transfer width.

Control flow and state: clients provide this static configuration to DMAengine filter/probe paths so the DMA controller can select a channel and program device register endpoints. State is per-slave configuration, not managed by this header.

Dependencies and integration points: depends on `linux/dmaengine.h` and integrates with Intel PCH peripheral drivers and DMAengine channel setup.

Risks and test signals: risks include wrong register DMA addresses, mismatched width causing data corruption, and channel ID conflicts. Tests should cover DMA channel request, TX/RX register programming, width variants, transfer completion, and fallback when DMA is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pch_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-acpi.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-acpi.h

Purpose: `pci-acpi.h` bridges PCI core code with ACPI root bridges, power management, MCFG/ECAM lookup, slot and hotplug enumeration, device companions, and PCI-specific ACPI DSM functions.

Important APIs/types/functions: ACPI-enabled APIs include PM notifier add/remove helpers, `acpi_pci_root_get_mcfg_addr()`, `pci_mcfg_lookup()`, bridge-handle helpers, `struct acpi_pci_root_info`, `struct acpi_pci_root_ops`, resource probing, root bus creation, bus add/remove hooks, `pci_acpi_setup()`, slot/hotplug helpers, EDR notifier helpers, and companion lookup hook registration. `_DSM` function constants include preserve boot config, device name, power-on reset delay, and readiness durations.

Control flow and state: root bridge discovery builds `acpi_pci_root_info`, prepares resources, creates a PCI bus, and registers ACPI/PCI associations. Bus add/remove hooks manage companion and slot/hotplug state. Many functions compile to no-ops when relevant config options are disabled.

Dependencies and integration points: depends on `linux/acpi.h`, PCI root/host bridge code, ECAM ops, ACPI PM notifier infrastructure, hotplug, EDR, slot code, and DSM GUID handling.

Risks and test signals: risks include stale ACPI handles, wrong root-bus traversal, MCFG quirks not applied, no-op behavior hiding missing config, and hotplug slot leaks. Tests should cover ACPI and non-ACPI builds, root resource parsing, MCFG lookup quirks, companion setup/cleanup, hotplug enumeration/removal, and EDR notifier lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ats.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-ats.h

Purpose: `pci-ats.h` declares PCI Address Translation Service, Page Request Interface, and PASID helper APIs with config-dependent stubs.

Important APIs/types/functions: ATS functions include support query, enable, prepare, disable, queue depth, and page-alignment query. PRI functions include enable, disable, reset, PRG response PASID requirement, and support query. PASID functions include enable, disable, feature query, maximum PASIDs, and status.

Control flow and state: callers check support, configure queue/page-size parameters, enable translation or request features, and disable them during teardown. When the relevant kernel config is off, most APIs return `-ENODEV`, `-EINVAL`, false, or no-op so callers can compile while feature paths remain disabled.

Dependencies and integration points: depends on `linux/pci.h`; integrates with IOMMU/SVA, device drivers using PASID, PCI capabilities, and virtualization or accelerator drivers.

Risks and test signals: risks include enabling ATS without IOMMU support, PASID feature mismatch, queue-depth misuse, and callers ignoring stub errors. Tests should cover config-off stubs, capability discovery, enable/disable ordering, IOMMU interaction, reset behavior, and device removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-bwctrl.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-bwctrl.h

Purpose: `pci-bwctrl.h` declares PCIe bandwidth cooling-device registration for thermal control of PCIe links.

Important APIs/types/functions: `pcie_cooling_device_register(struct pci_dev *port)` returns a `struct thermal_cooling_device *` when `CONFIG_PCIE_THERMAL` is enabled, and `pcie_cooling_device_unregister()` removes it. Stubs return `NULL` or no-op when disabled.

Control flow and state: a PCIe port driver registers a cooling device, thermal core can request bandwidth throttling through the implementation, and unregister occurs during teardown. State is held in the thermal cooling device and associated PCI port.

Dependencies and integration points: depends on `linux/pci.h` and the thermal framework. It integrates PCIe link bandwidth management with thermal zones and platform cooling policies.

Risks and test signals: risks include registering non-port devices, failing to unregister, thermal callbacks racing with device removal, and silent disabled-config behavior. Tests should cover thermal-enabled and disabled builds, registration failure, link speed/width throttling behavior, and removal while cooling state is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-bwctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-doe.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-doe.h

Purpose: `pci-doe.h` exposes the PCIe Data Object Exchange mailbox API used by protocols such as discovery, CMA, secure sessions, and TSM/IDE flows.

Important APIs/types/functions: `struct pci_doe_mb` is opaque. Feature constants identify DOE discovery, CMA, and secure-session protocols. `pci_find_doe_mailbox()` locates a mailbox by vendor and type, and `pci_doe()` performs a request/response exchange with caller-provided buffers.

Control flow and state: a caller discovers an appropriate mailbox, then submits typed DOE messages. The implementation serializes mailbox access and copies responses into the caller buffer. State is in the opaque mailbox and PCI DOE capability registers.

Dependencies and integration points: depends on PCI device declarations and integrates with PCI capability scanning, SPDM/CMA, PCI TSM, IDE, and vendor-specific protocols.

Risks and test signals: risks include buffer size mismatch, mailbox busy/timeouts, protocol type confusion, and use after device removal. Tests should cover mailbox discovery, malformed response lengths, timeout/error paths, concurrent callers, and protocol-specific DOE exchanges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-doe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ecam.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-ecam.h

Purpose: `pci-ecam.h` defines Enhanced Configuration Access Mechanism address calculations, config-window data structures, generic ECAM operations, and platform quirk operation declarations.

Important APIs/types/functions: macros define ECAM bus, devfn, and register shifts/masks plus `PCIE_ECAM_OFFSET()`. `struct pci_ecam_ops` embeds `pci_ops` and optional init/enable/disable hooks. `struct pci_config_window` stores config resource, bus resource, mapping(s), ops, private data, and parent device. APIs include `pci_ecam_create()`, `pci_ecam_free()`, `pci_ecam_map_bus()`, and `pci_generic_ecam_ops`; ACPI quirk ops are declared for 32-bit access and known controllers.

Control flow and state: host bridge setup creates a config window from resources and ops, maps config-space memory, and uses `pci_ecam_map_bus()` to compute per-device config addresses. State persists as host bridge sysdata until bridge teardown.

Dependencies and integration points: depends on PCI core, kernel resources, platform devices, ACPI MCFG lookup, and architecture I/O memory mapping.

Risks and test signals: risks include incorrect bus shift, out-of-range register offsets, wrong 32-bit/per-bus mapping choice, and missing controller quirks. Tests should cover config reads/writes across bus/devfn/register ranges, ACPI MCFG quirk selection, resource teardown, and invalid bus resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ecam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ep-cfs.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-ep-cfs.h

Purpose: `pci-ep-cfs.h` declares configfs group creation/removal helpers for PCI endpoint controllers and endpoint functions.

Important APIs/types/functions: when `CONFIG_PCI_ENDPOINT_CONFIGFS` is enabled, `pci_ep_cfs_add_epc_group()`, `pci_ep_cfs_remove_epc_group()`, `pci_ep_cfs_add_epf_group()`, and `pci_ep_cfs_remove_epf_group()` manage configfs groups. Disabled stubs return `NULL` or no-op.

Control flow and state: endpoint core or drivers create configfs groups by name, expose runtime configuration, and remove groups during teardown. State lives in configfs objects and the endpoint core.

Dependencies and integration points: depends on `linux/configfs.h`, PCI endpoint core, and userspace-driven endpoint configuration.

Risks and test signals: risks include group lifetime leaks, duplicate names, missing removal on probe failure, and callers not handling disabled stubs. Tests should cover configfs mount interactions, create/remove cycles, duplicate group names, disabled-config builds, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ep-cfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ep-msi.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-ep-msi.h

Purpose: `pci-ep-msi.h` declares endpoint-function side MSI doorbell allocation helpers.

Important APIs/types/functions: `pci_epf_alloc_doorbell(struct pci_epf *epf, u16 nums)` allocates doorbell MSI messages for an endpoint function, and `pci_epf_free_doorbell()` releases them. Disabled builds return `-ENODATA` and no-op.

Control flow and state: endpoint function drivers request a number of doorbells, use allocated MSI message metadata through the EPF state, and free them during teardown. State is associated with `struct pci_epf`.

Dependencies and integration points: depends on `struct pci_epf` from endpoint function core and `CONFIG_PCI_ENDPOINT_MSI_DOORBELL`. It integrates with endpoint MSI/MSI-X emulation, host-triggered doorbells, and endpoint function drivers.

Risks and test signals: risks include leaking doorbells, requesting unsupported counts, stale MSI messages after unbind, and callers ignoring `-ENODATA`. Tests should cover enabled and disabled configs, allocation/free cycles, count bounds, EPF unbind cleanup, and interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ep-msi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-epc.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-epc.h

Purpose: `pci-epc.h` defines the PCI Endpoint Controller core interface: controller objects, operations, memory windows, BAR capabilities, feature discovery, endpoint-function attachment, BAR/MSI/MSI-X programming, address mapping, link control, and endpoint memory allocation.

Important APIs/types/functions: key types include `enum pci_epc_interface_type`, `struct pci_epc_map`, `struct pci_epc_ops`, `struct pci_epc_mem_window`, `struct pci_epc_mem`, `struct pci_epc`, `enum pci_epc_bar_type`, reserved BAR region descriptors, and `struct pci_epc_features`. APIs include `pci_epc_create()`/devm create, destroy, add/remove EPF, link notifications, init/deinit/bus-master notifications, write header, set/clear BAR, map/unmap address, set/get MSI/MSI-X, raise IRQ, map MSI IRQ, start/stop link, get features, free-BAR selection, get/put EPC by name, and EPC memory init/alloc/map/unmap helpers.

Control flow and state: an EPC driver registers an EPC with an ops table and memory windows. EPF drivers bind functions, request BAR and interrupt setup, map endpoint memory to RC PCI addresses, and start link operation. `struct pci_epc` maintains EPF lists, locks, function number bitmap, domain, configfs group, feature arrays, and initialization state. Memory allocation uses bitmap-managed windows protected by mutexes.

Dependencies and integration points: depends on `pci-epf.h`, device model, configfs, endpoint core implementation, PCI BAR constants, module ownership, and controller-specific iATU/window programming.

Risks and test signals: risks include ops called without required locking, BAR type misuse, incorrect inbound mapping alignment, memory-window bitmap leaks, MSI/MSI-X count mismatch, function/VF number conflicts, and notification ordering bugs. Tests should cover EPF bind/unbind, multi-function and VF assignment, BAR feature combinations, memory map/unmap, link up/down, interrupt raise paths, configfs lifecycle, and disabled endpoint builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-epc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-epf.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-epf.h

Purpose: `pci-epf.h` defines PCI Endpoint Function core objects and driver interfaces: endpoint function identity, config header, BARs, function driver callbacks, EPC event callbacks, virtual function support, MSI-X table metadata, and allocation/bind helpers.

Important APIs/types/functions: types include `enum pci_barno`, `struct pci_epf_header`, `struct pci_epf_ops`, `struct pci_epc_event_ops`, `struct pci_epf_driver`, `struct pci_epf_bar_submap`, `struct pci_epf_bar`, `struct pci_epf_doorbell_msg`, `struct pci_epf`, and `struct pci_epf_msix_tbl`. APIs include EPF create/destroy, driver register/unregister, BAR space allocation/free/assignment, inbound address alignment, bind/unbind, and virtual EPF add/remove.

Control flow and state: endpoint function drivers register an EPF driver, get probed for EPF devices, fill header/BAR/interrupt requirements, bind to an EPC, allocate BAR space, and react to EPC events such as init, link up/down, and bus master enable. `struct pci_epf` stores primary/secondary EPC association, BAR arrays for both, function numbers, driver/id pointers, configfs group, bound/VF state, VF bitmap/list, event ops, and doorbell messages.

Dependencies and integration points: depends on configfs, device model, module device tables, MSI, PCI core, and EPC features from `pci-epc.h`. It integrates with endpoint configfs, test functions, NTB/function drivers, and controller-specific EPC operations.

Risks and test signals: risks include BAR memory leaks, binding state races, secondary EPC inconsistencies, VF bitmap conflicts, invalid MSI-X table layout, and missing unbind cleanup. Tests should cover EPF driver probe/remove, configfs-created functions, BAR allocation alignment, subrange mappings, bind/unbind idempotence, virtual functions, and endpoint interrupt paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-epf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ide.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-ide.h

Purpose: `pci-ide.h` declares helpers for PCIe Integrity and Data Encryption key-management/stream setup, shared by low-level PCI and TSM drivers implementing IDE_KM.

Important APIs/types/functions: `enum pci_ide_partner_select` identifies endpoint, root port, and host-bridge stream pools. `struct pci_ide_partner` stores RID ranges, stream index, memory/prefetchable address associations, and setup/enable flags. `struct pci_ide_regs` holds computed RID/address association registers. `struct pci_ide` tracks endpoint device, partner settings, host bridge stream, stream ID, and sysfs name. APIs set host-bridge stream counts, resolve settings, allocate/free/register/unregister/setup/teardown/enable/disable/release streams, and provide a cleanup helper via `DEFINE_FREE`.

Control flow and state: callers allocate a stream descriptor, optionally adjust partner address ranges, register it, program setup, enable IDE, then disable/teardown/free on release. State tracks whether setup and enable occurred per partner so teardown can be conditional and ordered.

Dependencies and integration points: depends on PCI devices, host bridges, bus regions, TSM-established IDE flows, sysfs naming, and cleanup attributes. It integrates with `pci-tsm.h` link security and PCIe IDE capability programming.

Risks and test signals: risks include leaked stream IDs, mismatched RID/address association, enabling without setup, teardown omissions, and wrong default stream handling. Tests should cover allocation exhaustion, endpoint/root-port/host-bridge pairing, register conversion, setup/enable/disable ordering, cleanup helper behavior, and TSM-owned stream IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-ide.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-p2pdma.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-p2pdma.h

Purpose: `pci-p2pdma.h` defines PCI peer-to-peer DMA provider and mapping APIs so devices can use PCI BAR memory for direct device-to-device transfers when topology allows it.

Important APIs/types/functions: `struct p2pdma_provider` holds owner and bus offset. `enum pci_p2pdma_map_type` distinguishes none, unsupported, bus-address mapping, and host-bridge-allowed mapping. APIs initialize providers, add resources, compute distance, find P2P memory providers, allocate/free P2P memory and scatterlists, publish memory, parse/show sysfs enable state, query map type, update map state, compute per-page P2PDMA state, and map physical to bus addresses.

Control flow and state: a PCI device initializes P2PDMA resources, publishes BAR-backed memory, and clients choose a provider based on distance. DMA mapping paths call `pci_p2pdma_state()` for each page; if the page is P2PDMA, state is updated and a map type tells the DMA layer whether to use bus addresses, normal host-bridge mappings, or reject the transfer. Disabled builds return safe unsupported/null values.

Dependencies and integration points: depends on PCI core, device pages marked as P2PDMA, scatterlists, block devices, DMA mapping, sysfs attributes, and topology/host bridge allowlists.

Risks and test signals: risks include unsafe transfers across unsupported host bridges, wrong bus offset, published memory lifetime issues, scatterlist leaks, and callers ignoring `NOT_SUPPORTED`. Tests should cover topology distance, provider allocation/free, sysfs parsing, DMA map decisions, block/NVMe P2P paths, disabled-config stubs, and hot-remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-p2pdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-pwrctrl.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-pwrctrl.h

Purpose: `pci-pwrctrl.h` declares a framework for PCI devices that need external resources such as regulators, GPIOs, or clocks enabled before the PCI device can be discovered.

Important APIs/types/functions: `struct pci_pwrctrl` contains the power-control device, `power_on`/`power_off` callbacks, and private notifier, device link, and work fields. APIs initialize a power-control context, mark/unmark a device ready, provide a devm ready helper, and create/destroy/power on/off power-control devices under a parent when `CONFIG_PCI_PWRCTRL` is enabled.

Control flow and state: platform devices created from firmware nodes power resources, mark themselves ready, trigger PCI bus rescan, and create a device link so PCI PM/reset ordering respects the power controller. State persists in the context and device link until unset or managed cleanup.

Dependencies and integration points: depends on notifier and workqueue APIs, device links, platform/OF population, PCI bus rescans, and power resource providers.

Risks and test signals: risks include rescanning before resources are stable, failing to remove links, power-off races with PCI devices, and disabled-config stubs masking missing framework support. Tests should cover deferred probe, ready/unready cycles, device-link PM ordering, devm cleanup, parent create/destroy, and PCI remove/rescan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-pwrctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-tph.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-tph.h

Purpose: `pci-tph.h` declares PCIe TLP Processing Hint helpers for enabling TPH and managing steering tags, including different tags for volatile and persistent memory targets.

Important APIs/types/functions: `enum tph_mem_type` differentiates volatile memory and persistent memory. Enabled builds export `pcie_tph_set_st_entry()`, `pcie_tph_get_cpu_st()`, `pcie_disable_tph()`, `pcie_enable_tph()`, `pcie_tph_get_st_table_size()`, and `pcie_tph_get_st_table_loc()`. Disabled stubs return `-EINVAL` or no-op for the main operations.

Control flow and state: drivers enable TPH in a selected mode, query or program steering-tag table entries, use CPU/memory-type-specific tags, and disable TPH on teardown. State is in PCIe TPH capability registers and steering tag tables.

Dependencies and integration points: depends on PCI core and PCI Firmware Specification steering-tag semantics. It integrates with performance-sensitive PCIe devices, NUMA/cache locality policy, and persistent-memory targeting.

Risks and test signals: risks include wrong memory-type steering tag, table index overflow, enabling unsupported modes, and missing disabled-build handling. Tests should cover capability discovery, table size/location reads, tag programming, CPU tag lookup, PM vs VM tag selection, and device removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-tph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-tsm.h -->
# Research: sources/distributed-fs/ceph-client/include/linux/pci-tsm.h

Purpose: `pci-tsm.h` defines PCI TEE Security Manager abstractions for confidential PCIe links and function security, including TSM registration, SPDM/IDE/TDISP coordination, TDI binding, DOE transfer, and guest request forwarding.

Important APIs/types/functions: `struct pci_tsm_ops` contains mutually exclusive link and device-security operation groups. Link ops cover probe/remove, connect/disconnect, bind/unbind, and guest requests; devsec ops cover lock/unlock. Context types include `struct pci_tdi`, `struct pci_tsm`, and `struct pci_tsm_pf0` with DSM lock and DOE mailbox. `is_pci_tsm_pf0()` identifies eligible function 0 devices. `enum pci_tsm_req_scope` classifies guest requests as info, state change, debug read, or debug write. Enabled APIs register/unregister TSM devices, construct/destruct link/PF0 contexts, perform DOE transfer, bind/unbind TDI, construct TDI state, and process guest requests.

Control flow and state: a TSM driver registers, probes/locks PCI devices, establishes secure links through connect, optionally binds a TDI to a KVM/TVM, marshals scoped guest requests, and disconnects/unbinds during teardown. Locking context is part of the contract: operations run under `pci_tsm_rwsem` and, for link operations, a DSM mutex. State ties PCI devices to TSM devices, DSM devices, DOE mailboxes, and optional TDI/KVM contexts.

Dependencies and integration points: depends on mutexes, PCI core, socket pointers, KVM, TSM device core, DOE mailboxes, PCIe IDE/TEE capabilities, and TDISP security policy. It integrates with `pci-doe.h`, `pci-ide.h`, confidential-computing guests, and VF assignment flows.

Risks and test signals: risks include security-scope violations for guest requests, debug write authorization mistakes, lock inversions, stale TDI bindings across VM teardown, DOE transfer failure handling, and incorrect PF0 eligibility. Tests should cover registration lifecycle, PF0 detection matrix, connect/disconnect serialization, bind/unbind with KVM teardown, guest request scope enforcement, DOE errors, and disabled-config stubs returning `-ENXIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci-tsm.h -->
