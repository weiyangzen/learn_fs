# subset-b-003996 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/irq_remapping.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/irq_remapping.c

Purpose: Intel VT-d interrupt-remapping support for x86 IO-APIC, HPET, PCI MSI/MSI-X, posted MSI, kdump table reuse, and DRHD hotplug. It owns IR table allocation, ACPI DMAR scope parsing, IRTE programming, MSI parent irq-domain integration, and global enable/disable of interrupt remapping.

Important APIs/types/functions: `struct ioapic_scope`, `struct hpet_scope`, `struct irq_2_iommu`, and `struct intel_ir_data` track source devices, IRTE allocation, sub-handles, and cached MSI/IRTE state. Key paths are `intel_prepare_irq_remapping()`, `intel_enable_irq_remapping()`, `intel_setup_irq_remapping()`, `modify_irte()`, `clear_entries()`, `intel_irq_remapping_alloc()`, `intel_irq_remapping_activate()`, `intel_ir_set_affinity()`, `intel_ir_set_vcpu_affinity()`, `intel_irq_remap_add_device()`, and `dmar_ir_hotplug()`.

Control flow: early boot parses DMAR IOAPIC/HPET scopes, verifies every remapping unit supports IR/EIM, allocates a 1 MiB IR table plus bitmap, creates an MSI parent irqdomain, enables queued invalidation, loads kdump IRTEs when applicable, writes IRTA, then enables IRE and blocks compatibility-format interrupts. IRQ allocation delegates vector allocation to the parent domain, allocates one or more contiguous IRTEs, fills source-ID validation according to IOAPIC/HPET/PCI aliasing, composes DMAR-format MSI messages, and writes IRTEs on activation or affinity changes. Free/deactivate paths clear IRTEs, release bitmap regions, and invalidate IEC entries.

State and persistence: persistent state is in `iommu->ir_table`, `iommu->ir_domain`, global `ir_ioapic[]`/`ir_hpet[]`, `eim_mode`, irq-domain chip data, and per-IOMMU `VTD_FLAG_IRQ_REMAP_PRE_ENABLED`. Kdump can copy a firmware/previous-kernel IR table and preserve used entries in the bitmap.

Dependencies and integration: integrates ACPI DMAR parsing, x86 APIC/vector domains, MSI parent domains, PCI DMA aliases, queued invalidation, posted interrupt descriptors, HPET/IOAPIC routing, and Intel IOMMU register locking.

Risks: IRTE updates require correct 128-bit atomic handling for posted formats and strict lock ordering. Source-ID validation is topology-sensitive, especially HPET quirks and PCI aliases. Removing a hotplugged DRHD while bitmap entries remain returns `-EBUSY`. This local source contains duplicate lines/declarations around `map_dev_to_ir()` and IOAPIC scope parsing, which is a compile/review signal for this snapshot.

Test signals: boot with xAPIC/x2APIC, DMAR x2APIC opt-out, kdump with pre-enabled IR, IOAPIC and HPET interrupt delivery, PCI MSI/MSI-X including multi-MSI, posted MSI/vCPU affinity transitions, IRQ affinity migration, DRHD hotplug add/remove, and fault-injection for IRTE allocation and queued invalidation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/irq_remapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/nested.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/nested.c

Purpose: Intel VT-d nested-domain support for iommufd/user-managed stage-1 page tables nested on a stage-2 DMA domain. It allocates nested domains, attaches devices or PASIDs, installs nested PASID entries, and exposes user invalidation for guest stage-1 changes.

Important APIs/types/functions: `intel_iommu_domain_alloc_nested()` consumes `IOMMU_HWPT_DATA_VTD_S1`; `intel_nested_attach_dev()` attaches a RID to a nested domain; `intel_nested_set_dev_pasid()` attaches a PASID; `intel_nested_cache_invalidate_user()` handles `IOMMU_HWPT_INVALIDATE_DATA_VTD_S1`; `intel_nested_domain_free()` removes the nested domain from its parent stage-2 list.

Control flow: allocation validates `nested_supported()`, requested flags, user data type, parent stage-2 paging compatibility, and `nested_parent`. It copies the user VT-d stage-1 config, initializes domain lists/locks/xarray, and links into `s2_domain->s1_domains`. Attach blocks translation, verifies parent stage-2 compatibility, attaches the domain to the IOMMU, assigns cache tags, enables IOPF routing, programs PASID `IOMMU_NO_PASID`, then records the device on the domain list. PASID attach performs similar compatibility checks, registers `dev_pasid_info`, replaces IOPF routing, programs the PASID entry, and removes the old PASID association.

State and persistence: nested domains persist `s1_cfg`, `s2_domain`, cache tags, `dev_pasids`, and parent `s1_domains` links. Device attachment updates `device_domain_info` and PASID tables; user invalidations do not persist, they flush cache-tag ranges.

Dependencies and integration: depends on Intel scalable-mode PASID programming in `pasid.c`, core IOMMU domain/PASID attach handles, PCI ATS/PRI compatibility, iommufd user data copy helpers, and cache-tag invalidation helpers.

Risks: nested attach is only valid when the stage-2 domain is compatible with the current IOMMU and marked nested-parent. PASID replacement must unwind IOPF and dev-pasid bookkeeping in the right order. User invalidation accepts only aligned ranges and supported flags; incorrect processed counts can affect userspace retry logic.

Test signals: iommufd nested HWPT allocation, invalid parent rejection, PASID attach/replace/unwind, device attach with IOPF, userspace cache invalidation arrays with partial failures, and teardown while parent tracks child stage-1 domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/nested.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.c

Purpose: Intel scalable-mode PASID directory/table management and PASID entry programming. It allocates per-device PASID tables, programs first-level, second-level, pass-through, dirty-tracking, and nested translation entries, tears entries down with required invalidations, and installs PASID directory pointers in context entries.

Important APIs/types/functions: exported functions include `intel_pasid_alloc_table()`, `intel_pasid_free_table()`, `intel_pasid_get_table()`, `intel_pasid_setup_first_level()`, `intel_pasid_setup_second_level()`, `intel_pasid_setup_dirty_tracking()`, `intel_pasid_setup_pass_through()`, `intel_pasid_setup_nested()`, `intel_pasid_tear_down_entry()`, `intel_pasid_setup_page_snoop_control()`, `intel_pasid_setup_sm_context()`, `intel_pasid_teardown_sm_context()`, and `intel_context_flush_no_pasid()`.

Control flow: allocation sizes the PASID directory from PCI PASID capability and `intel_pasid_max_id`, allocates IOMMU-accounted pages, and lazily allocates 4 KiB PASID entry tables with `try_cmpxchg64()` on PDEs. Setup paths validate hardware capability, lock `iommu->lock`, reject already-present entries, encode page-table pointers/domain IDs/address widths/PGTT/snoop/fault bits, release the lock, then flush caches using PASID-cache, PIOTLB/IOTLB, device-TLB, or write-buffer invalidations. Teardown clears present first, flushes PASID and TLB state based on PGTT, clears the entry or leaves FPD for fault-ignore SVA release, and drains PRQ when needed. Scalable-mode context setup installs the PASID directory into all matching PCI DMA aliases and handles copied kdump contexts with global invalidations.

State and persistence: `struct pasid_table` hangs from `device_domain_info`; PDE/PTE pages remain until table free. PASID entries persist hardware translation state. Context entries persist PASID-table base, RID2PASID, DTE/PASIDE/PRE bits, and present/fault-enable state.

Dependencies and integration: integrates VT-d queued invalidation, Intel domain ID allocation, second-stage page-table metadata, PCI ATS/devTLB invalidations, SVA/nested code, kdump copied contexts, and `iommu-pages` allocation.

Risks: invalidation ordering is spec-critical, especially present-bit clearing, A/D dirty tracking toggles, and context replacement after copied tables. Lazy PDE population must remain race-safe. Device-TLB flushes are skipped for absent PCI devices to avoid hangs. PASID zero has special RID2PASID invalidation semantics.

Test signals: PASID table allocation/free with different PCI PASID widths, concurrent PASID entry creation, first/second/nested/pass-through setup rejection paths, dirty tracking enable/disable, SVA teardown with PRQ drain, scalable context setup for PCI aliases, and kdump copied-context cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.h

Purpose: internal Intel PASID data layout and bitfield helper header. It defines PASID directory/table structures, translation-type constants, setup flags, inline PTE/PDE accessors, and prototypes consumed by Intel SVA, nested, DMA-domain, and context setup code.

Important APIs/types/functions: `struct pasid_dir_entry`, `struct pasid_entry`, and `struct pasid_table` represent hardware PASID structures. Inline helpers include `pasid_pde_is_present()`, `get_pasid_table_from_pde()`, `pasid_pte_is_present()`, `pasid_pte_get_pgtt()`, `pasid_clear_entry()`, `pasid_clear_entry_with_fpd()`, `pasid_set_domain_id()`, `pasid_set_slptr()`, `pasid_set_flptr()`, `pasid_set_translation_type()`, `pasid_set_present()`, `pasid_clear_present()`, `pasid_set_ssade()`, `pasid_set_page_snoop()`, `pasid_set_pgsnp()`, and nested/SRE/WPE/EAFE setters.

Control flow: implementation code composes entries by clearing all eight qwords, setting page-table pointers and translation fields, applying capability-driven flags, and finally calling `pasid_set_present()` with a DMA write barrier. Teardown clears present with a barrier before invalidation.

State and persistence: helpers directly encode persistent hardware-visible qwords. `PASID_PTE_FPD` supports non-present entries that suppress fault processing during fault-ignore teardown.

Dependencies and integration: depends on Linux bit macros, VT-d page masks, device and Intel IOMMU forward declarations, and the exported implementation in `pasid.c`.

Risks: bit positions must match VT-d scalable-mode PASID entry layout. `PASID_FLAG_NESTED` and `PASID_FLAG_FL5LP` both use `BIT(1)`, which is safe only because they are used in separate contexts. Barrier placement around present-bit changes is correctness-critical.

Test signals: compile coverage across all Intel IOMMU build options, unit-style validation of encoded qwords against VT-d spec tables, 4-level/5-level first-level setup, and teardown cases preserving or clearing FPD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.c

Purpose: lightweight Intel DMAR latency histogram support for invalidation and PRQ-related operations when `CONFIG_DMAR_PERF` is enabled.

Important APIs/types/functions: `dmar_latency_enable()`, `dmar_latency_disable()`, `dmar_latency_enabled()`, `dmar_latency_update()`, and `dmar_latency_snapshot()` operate on `struct latency_statistic` arrays indexed by `enum latency_type`.

Control flow: enabling lazily allocates `iommu->perf_statistic`, marks a latency bucket enabled, and initializes minimum to `UINT_MAX`. Updates bucket nanosecond latency into fixed ranges, maintains min/max/sum/sample count, and snapshots a formatted table with min/max/average converted to microseconds.

State and persistence: per-IOMMU statistics persist in `iommu->perf_statistic` until disabled or the IOMMU is freed. A single global spinlock serializes all stat updates and snapshots.

Dependencies and integration: included by Intel IOMMU invalidation/PRQ code and debugfs/reporting paths that request latency snapshots. It depends on `perf.h` enum ordering matching the snapshot name arrays.

Risks: `dmar_latency_disable()` clears `sizeof(*lstat) * DMAR_LATENCY_NUM` from `&lstat[type]`, which can overrun for nonzero `type` in this snapshot. Snapshot name arrays include `svm_prq` while `DMAR_LATENCY_NUM` currently covers three enum entries, another drift signal.

Test signals: enable/disable each latency type, update boundary values around each bucket, snapshot formatting with empty and populated samples, lockdep coverage under IRQ context, and KASAN/UBSAN for disable bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.h

Purpose: header for Intel DMAR latency statistics, providing enums, the statistic structure, and real or stub implementations depending on `CONFIG_DMAR_PERF`.

Important APIs/types/functions: `enum latency_type` names IOTLB, devTLB, and IEC invalidation latency classes; `enum latency_count` defines histogram buckets plus min/max/sum; `struct latency_statistic` holds enable state, counters, and sample count. Public helpers are declared or stubbed.

Control flow: callers can unconditionally call latency helpers; when disabled, enable returns `-EINVAL`, enabled returns false, and update/snapshot become no-ops.

State and persistence: no state in the header itself; it defines the shape allocated per IOMMU by `perf.c`.

Dependencies and integration: included by Intel IOMMU code that wants optional latency accounting without ifdefs at call sites.

Risks: enum/list drift with `perf.c` can produce mislabeled output or out-of-bounds clears. Stubs must match signatures to preserve compile behavior across configs.

Test signals: builds with and without `CONFIG_DMAR_PERF`, callers using every helper, and snapshot consumers tolerating empty strings when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.c

Purpose: Intel IOMMU hardware performance-monitoring PMU driver. It discovers VT-d PMU capabilities, exposes perf events and filters via sysfs, assigns events to IOMMU counters, handles freeze/unfreeze and counter overflow interrupts, and registers/unregisters a system-wide perf PMU per IOMMU.

Important APIs/types/functions: public entry points are `alloc_iommu_pmu()`, `free_iommu_pmu()`, `iommu_pmu_register()`, and `iommu_pmu_unregister()`. Internal perf callbacks include `iommu_pmu_event_init()`, `iommu_pmu_add()`, `iommu_pmu_del()`, `iommu_pmu_start()`, `iommu_pmu_stop()`, `iommu_pmu_event_update()`, `iommu_pmu_enable()`, and `iommu_pmu_disable()`.

Control flow: allocation checks ECAP PMS, ECMD support, `DMAR_PERFCAP`, counter/event-group counts, overflow interrupt support, and essential ECMD capability. It reads event-group capabilities, builds per-counter capability matrices, maps config/counter/overflow MMIO windows from offset registers, and stores `iommu->pmu`. Registration fills `struct pmu`, calls `perf_pmu_register()`, then allocates/request a DMAR perf IRQ. Event add selects a compatible free counter, writes event config, programs supported filters from `config1/config2`, and starts if requested. Overflow IRQ reads status, updates assigned events, clears overflow bits, and clears DMAR perf interrupt status.

State and persistence: state lives in `struct iommu_pmu`: capability arrays, used counter bitmap, event pointers, MMIO register bases, IRQ name, and backpointer to `intel_iommu`. Active events persist in hardware counters until stopped/deleted.

Dependencies and integration: depends on Intel VT-d PMU capability macros, enhanced command submission, perf core PMU callbacks, DMAR hardware IRQ allocation, and sysfs PMU attribute machinery.

Risks: capability parsing is hardware-specific; inconsistent per-counter capabilities reduce usable counter count. Filter bit encodings must match the PMU sysfs format. Runtime ECMD errors are intentionally ignored in start/stop, so users may see stale/no counts. `free_iommu_pmu()` assumes `cntr_evcap` is present when `evcap` is present.

Test signals: perf list/sysfs event visibility, perf stat with each event group, filter programming for requester/domain/PASID/ATS/page-table, grouped event scheduling beyond counter count, overflow IRQ delivery, register/unregister on probe/remove, and hardware without PMS/ECMD/PERFCAP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.h

Purpose: register offsets, filter bits, event encoding helpers, and optional prototypes for Intel IOMMU PMU support.

Important APIs/types/functions: macros define PMU offset-register layout, filter enable bits, config/counter capability offsets, counter capability extractors, and `iommu_event_select()`/`iommu_event_group()` decoders. Prototypes cover allocation, free, register, and unregister, with no-op stubs when `CONFIG_INTEL_IOMMU_PERF_EVENTS` is disabled.

Control flow: `perfmon.c` uses these helpers to parse hardware capabilities, format perf event config, locate per-counter filter registers, and conditionally compile PMU entry points.

State and persistence: no runtime state; it codifies the hardware ABI used to populate `struct iommu_pmu`.

Dependencies and integration: included by Intel IOMMU probe/remove and PMU code; relies on kernel bit helpers and Intel VT-d register definitions from `iommu.h`.

Risks: incorrect offsets or shifts would silently program wrong MMIO registers. Stubs returning success for allocation/register in disabled builds mean callers must not assume a PMU exists afterward.

Test signals: build with PMU enabled/disabled, static validation of event encodings, sysfs format strings matching macros, and hardware counter capability parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/prq.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/prq.c

Purpose: Intel VT-d Page Request Queue support for PRI/IOPF. It allocates and programs PRQ rings, handles page-request interrupts, validates and reports PRQ descriptors to the generic IOPF layer, drains PRQ state during PASID teardown, and sends page-group responses.

Important APIs/types/functions: `struct page_req_dsc` models hardware descriptors. Public functions are `intel_iommu_enable_prq()`, `intel_iommu_finish_prq()`, `intel_iommu_drain_pasid_prq()`, and `intel_iommu_page_response()`. Core helpers include `prq_event_thread()`, `intel_prq_report()`, `handle_bad_prq_event()`, and `prq_to_iommu_prot()`.

Control flow: enabling allocates a PRQ page ring, DMAR IRQ vector, generic `iopf_queue`, threaded IRQ, initializes head/tail/PQA registers, and completion. The IRQ thread clears pending status, walks descriptors from head to tail, rejects non-canonical/unsupported request combinations, drops stop markers, finds the requesting device by RID under `iopf_lock`, reports valid faults to `iommu_report_device_fault()`, traces descriptors, advances PQH, handles overflow by discarding partial IOPF groups when drained, and completes waiters. Draining waits for matching descriptors to leave software and hardware queues, flushes the generic IOPF workqueue, then submits wait/IOTLB/devTLB descriptors with drain semantics until hardware reports no PRQ overflow.

State and persistence: `iommu->prq`, `pr_irq`, `iopf_queue`, names, sequence counter, `prq_complete`, and hardware PRQ registers persist while PRQ is enabled. Device `iopf_refcount` determines whether drain is needed.

Dependencies and integration: integrates Intel queued invalidation, device RID lookup, generic `io-pgfault.c`, PCI ATS/PRI, PASID teardown, tracepoints, and DMAR hwirq allocation.

Risks: PRQ drain assumes the device driver has stopped DMA and no new requests arrive. Bad descriptor response uses RID as DID in response fields per hardware format. Overflow recovery can discard partial groups. Device lookup and IOPF queue removal must be synchronized to avoid reporting to freed domains.

Test signals: PRI-capable device SVA faults, invalid descriptor injection, stop-marker handling, overflow and partial discard, PASID teardown drain, page response success/failure, IRQ allocation unwind, and tracepoint decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/prq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/svm.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/svm.c

Purpose: Intel Shared Virtual Memory domain support. It verifies SVM capability, creates SVA domains bound to process `mm_struct`s, installs first-level PASID entries, invalidates secondary IOMMU TLBs on mmu notifier callbacks, and tears PASIDs down when an address space exits.

Important APIs/types/functions: `intel_svm_check()` marks IOMMUs SVM-capable. `intel_svm_domain_alloc()` allocates an `IOMMU_DOMAIN_SVA` domain and registers mmu notifiers. `intel_svm_set_dev_pasid()` attaches a device PASID to an mm. `intel_mm_release()`, `intel_arch_invalidate_secondary_tlbs()`, and `intel_mm_free_notifier()` implement notifier behavior.

Control flow: SVM capability requires PASID support and compatibility with CPU 1GiB pages and LA57. Domain allocation first checks device SVA support, initializes lists/locks/cache tags, and registers `intel_mmuops`. PASID attach validates PASID/ATS/PRI state, adds dev-pasid info, optionally replaces IOPF routing for PRI devices, programs a first-level PASID entry using `mm->pgd` with FL5LP/PWSNP flags, and removes the old domain association. MMU invalidation flushes all or range cache tags. MM release tears down every dev PASID with fault-ignore to prevent hardware walks after mm notifier removal.

State and persistence: SVA domain state includes `domain->mm`, `dev_pasids`, cache tags, notifier, lock, and `qi_batch`. Device PASID table entries persist until detach or mm release.

Dependencies and integration: relies on generic SVA core, Intel PASID programming, mmu_notifier, PCI ATS/PRI, cache-tag flushes, IOPF routing, and x86 CPU feature checks.

Risks: mm release occurs before page tables are cleared and after invalidate callbacks are removed, so PASID teardown ordering is safety-critical. Non-PRI devices are allowed only if their driver handles IOPF itself. The default first-level DID and page-table physical pointer must match VT-d expectations for the process address space.

Test signals: SVA bind/unbind through generic API, mm exit with active PASIDs, LA57 and 1GiB-page capability mismatch, PRI and non-PRI device behavior, mmu notifier range invalidation, and PASID replacement unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/svm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.c

Purpose: tracepoint instantiation unit for Intel IOMMU tracing.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS` and includes `trace.h`, causing the trace events declared there to be emitted exactly once.

Control flow: compile-time only; no runtime functions are implemented here. Including this translation unit links tracepoint definitions for queued invalidation, PRQ reporting, and cache-tag assignment/flush events.

State and persistence: tracepoint state is owned by the kernel tracing subsystem; this file has no persistent private data.

Dependencies and integration: depends on `trace.h`, Linux tracepoint infrastructure, and any helpers referenced by trace print functions such as PRQ descriptor decoding.

Risks: this file must remain the only `CREATE_TRACE_POINTS` inclusion for the Intel IOMMU trace system. Missing it causes unresolved trace symbols; duplicating it causes duplicate definitions.

Test signals: kernel build/link, tracefs event presence under `intel_iommu`, and enabling each Intel IOMMU tracepoint during invalidation/PRQ/cache-tag activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.h

Purpose: Intel IOMMU tracepoint declarations for queued invalidation descriptors, PRQ reports, and cache-tag assignment/flush activity.

Important APIs/types/functions: `TRACE_EVENT(qi_submit)`, `TRACE_EVENT(prq_report)`, `DECLARE_EVENT_CLASS(cache_tag_log)`, `cache_tag_assign`, `cache_tag_unassign`, `DECLARE_EVENT_CLASS(cache_tag_flush)`, `cache_tag_flush_range`, and `cache_tag_flush_range_np`.

Control flow: callers invoke generated trace helpers around queued invalidation submission, PRQ reporting, and cache-tag operations. Print functions decode descriptor type bits and cache-tag types into human-readable strings; PRQ output delegates descriptor formatting to `decode_prq_descriptor()`.

State and persistence: no driver state; trace records snapshot IOMMU name, device name, descriptor qwords, domain IDs, PASIDs, ranges, masks, and sequence numbers into tracing buffers.

Dependencies and integration: includes `iommu.h`, Linux tracepoint macros, and `trace/define_trace.h` with explicit include path/file settings for out-of-tree trace generation.

Risks: tracepoint field layouts are ABI-like for tracing users. `MSG_MAX` limits decoded PRQ text. Cache-tag enum names must stay in sync with actual cache-tag values.

Test signals: build with tracing, tracefs format files, enabled `qi_submit` while invalidating, `prq_report` during PRI faults, and cache-tag tracepoints during SVA/nested attach and invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgfault.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgfault.c

Purpose: generic I/O page-fault framework used by IOMMU drivers. It groups PRI page-request faults, routes them to the correct domain IOPF handler, manages per-device fault queues, sends failure responses on errors/removal, and flushes outstanding fault work.

Important APIs/types/functions: exported functions include `iommu_report_device_fault()`, `iopf_queue_alloc()`, `iopf_queue_free()`, `iopf_queue_add_device()`, `iopf_queue_remove_device()`, `iopf_queue_flush_dev()`, `iopf_group_response()`, `iopf_free_group()`, and `iopf_queue_discard_partial()`. Internal helpers manage `iommu_fault_param` references, partial faults, group allocation, and attach-handle lookup.

Control flow: drivers report low-level faults through `iommu_report_device_fault()`. Non-last group faults are copied to a per-device partial list. The last fault creates a group, moves matching partial faults before the last fault, registers it pending, finds the domain/PASID attach handle, and calls the domain `iopf_handler`. Handlers must later call `iopf_group_response()` and `iopf_free_group()`. Error paths respond invalid/failure and free groups. Queue add installs a refcounted fault parameter under RCU; removal invalidates partial and pending groups, sends invalid responses, unlinks the device, and drops the RCU reference.

State and persistence: per-device `fault_param` stores partial/pending lists, queue pointer, lock, refcount, and device pointer. Queue state stores a workqueue, device list, and lock. Fault groups persist until handlers respond/free them.

Dependencies and integration: used by Intel PRQ and generic SVA. It depends on core IOMMU attach handles, per-domain `iopf_handler`, device `iommu_ops->page_response`, RCU, mutexes, and workqueues.

Risks: callers must stop new hardware faults before flushing/removing queues. Partial group matching uses `grpid` only within a device fault parameter. Missing page-response ops rejects queue add. User-managed PASID tables route PASID faults through the nested RID domain when direct PASID handle lookup fails.

Test signals: multi-fault group assembly, non-last fault postponement, handler success/failure, queue flush on PASID teardown, queue remove with pending groups, overflow partial discard, and RCU/refcount stress with concurrent reports/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgfault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-selftests.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-selftests.c

Purpose: KUnit tests for ARM LPAE IOMMU page-table operations.

Important APIs/types/functions: `arm_lpae_do_selftests()` is the KUnit case; `arm_lpae_run_tests()` exercises `alloc_io_pgtable_ops()`, `map_pages`, `unmap_pages`, and `iova_to_phys` for `ARM_64_LPAE_S1` and `ARM_64_LPAE_S2`. Dummy TLB callbacks validate cookie and page-size arguments.

Control flow: the test registers a KUnit device, constructs coherent-walk configs with `IO_PGTABLE_QUIRK_NO_WARN`, iterates 4K/16K/64K granule page-size sets and IAS/OAS combinations, allocates both S1 and S2 page tables, verifies empty translations, maps distinct granularities, rejects overlapping maps, verifies translation offsets, unmaps/remaps, and tests the last largest supported page of the IAS.

State and persistence: state is per-test `io_pgtable_cfg`, dummy cookie, temporary page tables, and pass/fail counters. Page tables are freed after each format pass.

Dependencies and integration: depends on KUnit, `io-pgtable-arm.h`, generic io-pgtable allocation, and ARM LPAE backend availability.

Risks: early return on failure may skip `free_io_pgtable_ops()` for the failing case. The test covers core map/unmap/translate behavior but not dirty tracking, custom allocators, noncoherent walks, or all quirks.

Test signals: KUnit suite `io-pgtable-arm-test`, pass/fail summary, overlap rejection, boundary mapping near `1 << ias`, and KASAN/KMEMLEAK for allocation/free balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-selftests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-v7s.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-v7s.c

Purpose: ARMv7 short-descriptor IOMMU page-table backend supporting 32-bit and MediaTek-extended formats, two-level table allocation, mapping/unmapping, translation lookup, cache synchronization, and optional built-in selftests.

Important APIs/types/functions: `struct arm_v7s_io_pgtable`, `arm_v7s_alloc_pgtable()`, `arm_v7s_map_pages()`, `arm_v7s_unmap_pages()`, `arm_v7s_iova_to_phys()`, `arm_v7s_free_pgtable()`, and exported `io_pgtable_arm_v7s_init_fns`. Helpers cover PTE encoding, contiguous section/page handling, MediaTek high PA bits, and table install.

Control flow: allocation validates IAS/OAS and quirks, creates an L2 table slab, restricts page sizes, prepares PRRR/NMRR/TCR/TTBR config, allocates an L1 table, and returns ops. Mapping descends from L1 to L2 as needed, allocating synchronized tables, then installs one or more leaf PTEs. Unmapping rejects partial unmap of contiguous large entries, clears PTEs, frees child tables for table entries, and records TLB gather pages. Translation walks levels until a leaf or invalid PTE.

State and persistence: persistent backend state is the L1 `pgd`, L2 slab cache, and encoded register values in `io_pgtable_cfg`. PTEs persist hardware-visible mappings and may encode contiguous large entries or MediaTek high-address bits.

Dependencies and integration: used by IOMMU drivers selecting `ARM_V7S`; depends on DMA mapping for noncoherent walkers, kmem caches, generic io-pgtable callbacks, and optional `CONFIG_IOMMU_IO_PGTABLE_ARMV7S_SELFTEST`.

Risks: contiguous entries cannot be partially unmapped. Table physical addresses must fit PTE format unless MediaTek TTBR extension is enabled. Noncoherent sync ordering is critical. Permission handling can be disabled by quirk, so callers must understand hardware protection. Selftest-only overlap warnings differ from normal runtime behavior.

Test signals: built-in selftest with 4K/64K/1M/16M sizes, MediaTek quirk configurations, noncoherent table walks, overlap map rejection, contiguous entry full unmap, and translation after map/unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-v7s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.c

Purpose: ARM LPAE IOMMU page-table backend for 32/64-bit stage-1, stage-2, and Mali LPAE formats. It allocates page tables, encodes register configuration, maps/unmaps page ranges, translates IOVAs, walks page tables, and supports dirty-bit harvesting for ARM64 S1.

Important APIs/types/functions: `struct arm_lpae_io_pgtable`, `arm_lpae_alloc_pgtable()`, `arm_64_lpae_alloc_pgtable_s1()`, `arm_64_lpae_alloc_pgtable_s2()`, `arm_32_lpae_alloc_pgtable_s1()`, `arm_32_lpae_alloc_pgtable_s2()`, `arm_mali_lpae_alloc_pgtable()`, `arm_lpae_map_pages()`, `arm_lpae_unmap_pages()`, `arm_lpae_iova_to_phys()`, `arm_lpae_pgtable_walk()`, `arm_lpae_read_and_clear_dirty()`, and the five `io_pgtable_*_init_fns`.

Control flow: allocation restricts page sizes to supported granules, computes levels/start-level/PGD bits, validates quirks, fills TCR/VTCR/MAIR/Mali config, optionally adjusts concatenated stage-2 PGDs, allocates the root table, and publishes TTBR/VTTBR. Mapping validates IOVA/PA/prot, encodes permissions/memory attributes/shareability/XN/NS/AF/DBM, recursively allocates child tables, atomically installs table PTEs, and writes leaf entries. Unmap recursively clears leaves or table entries, flushes partial walks, frees child tables, and records gather pages. Walk helpers visit PTEs for translation, debug walking, or dirty bitmap collection.

State and persistence: backend state includes computed table geometry and root `pgd`; config stores hardware register values. Hardware-visible PTEs persist mappings, table links, dirty/DBM state, and software sync bits for noncoherent walkers.

Dependencies and integration: selected through `io-pgtable.c`; uses `iommu-pages`, DMA mapping for noncoherent page-table sync, generic TLB flush callbacks, dirty bitmap helpers, and ARM LPAE register definitions in `io-pgtable-arm.h`.

Risks: this local source snapshot has duplicate function parameter text and duplicate `return 0;` in places, suggesting a merge/copy issue that may break compilation. Correctness depends on barrier and cache-sync ordering around table install and leaf writes. Partial large-page unmap is rejected. Dirty tracking is limited to ARM64 S1 and writeable-dirty PTE interpretation.

Test signals: KUnit LPAE selftests, map/unmap/translate across 4K/16K/64K granules, stage-1/stage-2 register config validation, noncoherent walk DMA sync, dirty bitmap read-and-clear, custom allocator use, and overlap/partial-unmap rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.h

Purpose: shared ARM LPAE register field constants for io-pgtable ARM backends and tests.

Important APIs/types/functions: defines TCR granule encodings for TTBR0/TTBR1, shareability values, inner/outer cacheability values, and physical address size encodings from 32 to 52 bits.

Control flow: allocation code in `io-pgtable-arm.c` selects these constants while constructing `arm_lpae_s1_cfg.tcr` and `arm_lpae_s2_cfg.vtcr` based on page granule, coherency, output address size, and TTBR1 quirk.

State and persistence: no runtime state; constants become persistent hardware register configuration stored in `io_pgtable_cfg`.

Dependencies and integration: included by ARM LPAE implementation and KUnit tests.

Risks: constants are hardware ABI values; any mismatch changes page-table walk behavior. Header intentionally contains no guards around feature availability, so callers must validate formats elsewhere.

Test signals: compile use in implementation/tests, register field comparisons on ARM SMMU drivers, and KUnit coverage across address sizes/granules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-dart.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-dart.c

Purpose: Apple DART/DART2 IOMMU page-table backend. It allocates top-level TTBR tables, creates intermediate tables, maps/unmaps fixed-size pages, translates IOVAs, and encodes DART1/DART2 protection and physical-address formats.

Important APIs/types/functions: `struct dart_io_pgtable`, `apple_dart_alloc_pgtable()`, `apple_dart_free_pgtable()`, `dart_map_pages()`, `dart_unmap_pages()`, `dart_iova_to_phys()`, `dart_alloc_pgtable()`, and exported `io_pgtable_apple_dart_init_fns`.

Control flow: allocation requires coherent walks, OAS 36 or 42, IAS <= OAS, and page size exactly 4K or 16K. It computes level count, top-table count, and bits per level, allocates each TTBR root table, and fills `apple_dart_cfg`. Mapping validates fixed page size, PA range, and read/write permission, walks/allocates intermediate tables with atomic install, then installs leaf PTEs for as many entries as fit in the last table. Unmap finds the last-level table, clears valid PTEs, and records TLB pages. Translation walks to the last-level PTE and adds page offset.

State and persistence: state is `pgd[]`, level geometry, and DART PTEs. PTEs include valid bit, DART1/DART2 no-read/no-write/no-cache bits, DART1 subpage allow range, and encoded physical address.

Dependencies and integration: selected through `io-pgtable.c` for `APPLE_DART` and `APPLE_DART2`; uses `iommu-pages`, atomic cmpxchg, generic TLB gather, and Apple DART driver config.

Risks: only coherent page-table walks are supported. `pgsize_bitmap` is treated as a single fixed page size, not a bitmap of alternatives. Intermediate tables are not freed on individual unmaps, only full free. Address encoding differs between DART generations and must match hardware.

Test signals: DART1 and DART2 map/unmap/translate, 4K and 16K roots, multi-TTBR DART1 coverage, invalid IAS/OAS/page-size rejection, overlap map rejection, and teardown freeing all allocated levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-dart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable.c

Purpose: generic dispatch layer for IOMMU page-table backends. It maps `enum io_pgtable_fmt` values to backend init functions, validates custom allocator support, allocates page-table ops, stores common config, and frees page tables after flushing.

Important APIs/types/functions: `io_pgtable_init_table[]`, `check_custom_allocator()`, exported `alloc_io_pgtable_ops()`, and exported `free_io_pgtable_ops()`.

Control flow: allocation rejects out-of-range formats, invalid custom allocator pairs, missing backend functions, or backend allocation failure. On success it stamps the format, cookie, and copied config into the returned `io_pgtable` and returns the ops table. Free converts ops back to `io_pgtable`, flushes all TLBs through generic callbacks, and invokes the backend free function.

State and persistence: global static init table reflects build-time enabled backends. Allocated backends own their private state; this file only initializes shared metadata.

Dependencies and integration: depends on Linux `io-pgtable.h` and backend symbols from ARM LPAE, DART, and ARMv7S under Kconfig guards. IOMMU drivers use it instead of directly constructing backend state.

Risks: `check_custom_allocator()` dereferences `io_pgtable_init_table[fmt]` before `alloc_io_pgtable_ops()` checks that the backend exists, so a custom allocator with a disabled format could fault in this snapshot. Free assumes the page table walker is already inaccessible apart from the final TLB flush.

Test signals: allocation for each enabled/disabled format, custom allocator accepted only for supporting formats, free after map/unmap, and negative tests for invalid enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-debug-pagealloc.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-debug-pagealloc.c

Purpose: optional IOMMU API debug page-allocation sanitizer. It tracks physical pages mapped through IOMMU domains using `page_ext` metadata and warns when pages are freed while still IOMMU-mapped or when map/unmap accounting underflows.

Important APIs/types/functions: `page_iommu_debug_ops`, static key `iommu_debug_initialized`, `__iommu_debug_check_unmapped()`, `__iommu_debug_map()`, `__iommu_debug_unmap_begin()`, `__iommu_debug_unmap_end()`, `iommu_debug_init()`, and early parameter `iommu.debug_pagealloc`.

Control flow: early parameter sets `needed`; page-ext allocates `struct iommu_debug_metadata` when needed. Init enables the static key. Map increments per-minimum-IOMMU-page refcounts for the physical range. Unmap begin decrements by translating IOVA to PA first; unmap end re-increments the failed tail if unmap was partial. Free checks warn and dump page owner for any page with nonzero IOMMU refcount.

State and persistence: per-page `page_ext` atomic refcounts persist while debug mode is active. Static key gates low-overhead wrappers in `iommu-priv.h`.

Dependencies and integration: integrates with the core IOMMU map/unmap wrappers, page owner, page_ext operations, and domain `pgsize_bitmap`.

Risks: debug accounting relies on `iommu_iova_to_phys()` during unmap begin and on the smallest domain page size for symmetric accounting. It adds overhead and can miss pages without page_ext metadata. Partial unmap handling must mirror core unmap return values.

Test signals: boot with `iommu.debug_pagealloc=1`, map/unmap balanced ranges, forced partial unmap, freeing still-mapped pages to trigger warnings/page-owner dumps, and static-key disabled overhead checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-debug-pagealloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-debugfs.c

Purpose: top-level debugfs infrastructure for IOMMU drivers.

Important APIs/types/functions: exports `struct dentry *iommu_debugfs_dir` and implements `iommu_debugfs_setup()`.

Control flow: setup lazily creates `/sys/kernel/debug/iommu` and prints a prominent boot warning that IOMMU internals are exposed. Vendor drivers can create subdirectories under `iommu_debugfs_dir` after core setup.

State and persistence: `iommu_debugfs_dir` persists for the lifetime of the kernel debugfs tree. No teardown is implemented here.

Dependencies and integration: depends on debugfs, IOMMU core init, and vendor IOMMU debugfs users.

Risks: debugfs can expose sensitive IOMMU state, which the warning explicitly calls out. Repeated setup is idempotent only through the global pointer check.

Test signals: kernel built with IOMMU debugfs, boot warning presence, `/sys/kernel/debug/iommu` creation, vendor subdirectory creation, and disabled-debugfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.c

Purpose: IOMMU page-table/configuration page allocator with memory accounting and optional incoherent-walk DMA/cache management. It backs page-table allocations used by several IOMMU backends.

Important APIs/types/functions: `iommu_alloc_pages_node_sz()`, `iommu_free_pages()`, `iommu_put_pages_list()`, `iommu_pages_start_incoherent()`, `iommu_pages_start_incoherent_list()`, `iommu_pages_stop_incoherent_list()`, and `iommu_pages_free_incoherent()`. Static assertions ensure `struct ioptdesc` overlays `struct page` fields safely.

Control flow: allocation rejects highmem, rounds size to a power-of-two order, handles `NUMA_NO_NODE`, allocates a zeroed folio, marks incoherent false, and charges `NR_IOMMU_PAGES` and `NR_SECONDARY_PAGETABLE`. Free/list free reverse accounting and put the folio. Incoherent start either flushes cache directly on x86 or maps the allocation through the DMA API and verifies DMA address equals physical address; stop/free undo DMA mappings on non-x86.

State and persistence: metadata is stored in the page-overlaid `ioptdesc`, including list node and `incoherent` flag. VM/node accounting persists until pages are freed.

Dependencies and integration: used by Intel IR/PASID/PRQ and io-pgtable backends. Depends on folios, node/lruvec stats, DMA mapping, cacheflush on x86, and `iommu-pages.h`.

Risks: overlay assumptions are guarded by static asserts but fragile across `struct page` changes. Incoherent mode assumes direct DMA mappings and rejects translated/truncated DMA addresses. Lists become invalid after `iommu_put_pages_list()` unless reinitialized.

Test signals: allocation/free accounting in `/proc/vmstat`, NUMA allocation, list splice/free, highmem rejection, incoherent start/stop on x86 and non-x86, and DMA mapping error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.h

Purpose: public internal header for IOMMU page-table page allocation, list management, and incoherent page-table cache/DMA synchronization helpers.

Important APIs/types/functions: `struct ioptdesc` overlays `struct page`; converters include `folio_ioptdesc()`, `ioptdesc_folio()`, and `virt_to_ioptdesc()`. Allocation/list helpers include `iommu_alloc_pages_node_sz()`, `iommu_alloc_pages_sz()`, `iommu_free_pages()`, `iommu_pages_list_add()`, `iommu_pages_list_splice()`, `iommu_pages_list_empty()`, and incoherent start/stop/free/flush helpers.

Control flow: callers allocate pages, optionally add them to an `iommu_pages_list`, optionally start incoherent operation for noncoherent page-table walkers, flush updates through `iommu_pages_flush_incoherent()`, and free individually or as a list.

State and persistence: `ioptdesc` stores list linkage and an `incoherent` flag or page index overlay. On x86, incoherent stop is intentionally a no-op for performance and free ignores the flag; on other architectures the DMA API mapping state matters.

Dependencies and integration: included by Intel IOMMU and io-pgtable code. It depends on core IOMMU list type definitions, folios, DMA mapping, and architecture cacheflush support.

Risks: because `ioptdesc` overlays `struct page`, field layout drift is hazardous and must remain paired with `iommu-pages.c` static asserts. Callers must not use highmem allocations and must not reuse lists after splice/free without reinitialization.

Test signals: compile on x86 and non-x86, list helper behavior, incoherent flush semantics, and static assertions after memory-management changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-priv.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-priv.h

Purpose: private IOMMU core header shared inside `drivers/iommu`. It exposes internal helpers for device ops, fwspec, bus registration, mock devices, attach handles, iommufd MSI helpers, device PASID replacement, and debug pagealloc wrappers.

Important APIs/types/functions: `dev_iommu_ops()`, `dev_iommu_free()`, `iommu_ops_from_fwnode()`, `iommu_fwspec_ops()`, `iommu_fwspec_free()`, `iommu_device_register_bus()`, `iommu_device_unregister_bus()`, `iommu_mock_device_add()`, attach-handle helpers, `iommufd_sw_msi()`, `iommu_replace_device_pasid()`, and `iommu_debug_map/unmap_begin/unmap_end/init()` wrappers.

Control flow: internal code includes this header to access device-owned IOMMU ops after probe, manage firmware specs and attach handles, or call debug hooks without sprinkling config ifdefs. Debug wrappers branch on the static key only when `CONFIG_IOMMU_DEBUG_PAGEALLOC` is enabled; otherwise they compile away.

State and persistence: no state here except references to external static key/debug functions. It defines internal contracts for persistent core objects such as `dev_iommu`, `iommu_fwspec`, groups, domains, and attach handles.

Dependencies and integration: used by generic IOPF, SVA, debug pagealloc, and IOMMU core code. Depends on public `linux/iommu.h`, MSI types, and optional iommufd/IRQ MSI support.

Risks: `dev_iommu_ops()` trusts that probe installed valid ops, so misuse before probe would dereference invalid state. This is private API; external drivers should not depend on it. Conditional stubs must preserve semantics across config combinations.

Test signals: all IOMMU core build configs, attach-handle PASID routing, iommufd MSI enabled/disabled builds, debug pagealloc enabled/disabled runtime, and mock device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-sva.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-sva.c

Purpose: generic Shared Virtual Addressing helpers. It binds process address spaces to devices with global PASIDs, reuses or allocates SVA domains, manages bind references, handles SVA I/O page faults by faulting CPU page tables, and broadcasts kernel VA invalidations to active SVA mms.

Important APIs/types/functions: exported `iommu_sva_bind_device()`, `iommu_sva_unbind_device()`, `iommu_sva_get_pasid()`, `mm_pasid_drop()`, and `iommu_sva_invalidate_kva_range()`. Internal helpers include `iommu_alloc_mm_data()`, `iommu_sva_domain_alloc()`, `iommu_sva_iopf_handler()`, `iommu_sva_handle_iopf()`, and `iommu_sva_handle_mm()`.

Control flow: bind requires an IOMMU group, locks global SVA state, allocates/reuses `mm->iommu_mm` and PASID, reuses an existing attach handle if present, otherwise tries existing SVA domains for the mm or allocates a driver SVA domain through `ops->domain_alloc_sva`, attaches the device PASID, updates domain/mm lists, and returns a refcounted handle. Unbind decrements handle refs, detaches PASID when last, frees domains with no users, and updates the global active-mm list. Fault handling queues work per IOPF group, checks PASID-valid faults, pins the mm, validates VMA permissions, calls `handle_mm_fault()`, then responds success or invalid/failure.

State and persistence: global `iommu_sva_lock`, `iommu_sva_present`, and `iommu_sva_mms` track active SVA address spaces. Each `iommu_mm_data` stores PASID, mm, domain list, and list node. Domains hold mm references and IOPF handler pointers; handles hold device and refcount.

Dependencies and integration: integrates architecture PASID helpers, global PASID allocator, IOMMU PASID attach/detach, driver `domain_alloc_sva`, mm fault handling, IOPF groups, and mmu notifier secondary TLB invalidation.

Risks: `arch_pgtable_dma_compat()` may reject mms incompatible with device DMA. PASID range is checked against each device `max_pasids`. Fault handling must not outlive mm teardown; domain allocation `mmgrab()` and driver free paths must pair. Access checks must correctly translate IOMMU permissions to VMA/fault flags.

Test signals: repeated bind/unbind reference counting, reuse of domains across devices for one mm, PASID exhaustion/range errors, IOPF read/write/exec/priv faults, mm exit `mm_pasid_drop()`, and `iommu_sva_invalidate_kva_range()` with active and inactive lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-sva.c -->
