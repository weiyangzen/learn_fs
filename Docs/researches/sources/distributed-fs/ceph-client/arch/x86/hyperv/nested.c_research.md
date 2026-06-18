## `sources/distributed-fs/ceph-client/arch/x86/hyperv/nested.c`

Purpose: provides Hyper-V nested virtualization helpers to flush guest physical mappings by address space or ranges.

Important APIs and functions: exported functions are `hyperv_flush_guest_mapping()`, `hyperv_fill_flush_guest_mapping_list()`, and `hyperv_flush_guest_mapping_range()`. The range helper accepts a callback of type `hyperv_fill_flush_list_func`.

Control flow: whole-address-space flush validates the hypercall page and per-CPU input buffer, fills `address_space`, and issues `HVCALL_FLUSH_GUEST_PHYSICAL_ADDRESS_SPACE`. Range flush invokes the caller-provided fill callback, then issues `HVCALL_FLUSH_GUEST_PHYSICAL_ADDRESS_LIST` as a rep hypercall. The list filler compresses contiguous GFNs into Hyper-V entries with `additional_pages`, bounded by `HV_MAX_FLUSH_REP_COUNT` and `HV_MAX_FLUSH_PAGES`.

State and persistence: no private persistent state. Uses per-CPU hypercall input pages with interrupts disabled. Traces return status.

Dependencies and integration points: exported for nested Hyper-V/KVM integration, Hyper-V hypercall helpers, TLB flushing definitions, and tracepoints.

Risks: missing hypercall page returns `-ENOTSUPP`; callers need fallback. Range list overflow returns `-ENOSPC`, and callers should switch to broader flushes. Input buffers are per-CPU and require interrupts disabled.

Test signals: nested virtualization workloads with guest mapping invalidations, large range flushes forcing fallback, hypercall failure tracepoints, and module users resolving GPL exports.
