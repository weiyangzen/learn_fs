# File Research: sources/cow-pools/openzfs/module/zfs/fm.c

## Role

Provides Fault Management Architecture support used by ZFS: FMA nvlist allocation helpers, ereport and FMRI constructors, ENA helpers, kernel zevent queueing, event stream cursor operations, and FMA-related kstats.

## Kernel Zevent Queue

- `zfs_zevent_alloc()` and `zfs_zevent_free()` allocate/free posted event records and run the provided cleanup callback.
- `zfs_zevent_insert()` inserts newest events at the head and drains the oldest event when `zfs_zevent_len_max` is exceeded.
- `zfs_zevent_post()` stamps time and monotonically increasing EID fields into an ereport, checks native nvlist size against `ERPT_DATA_SZ`, queues the event, wakes waiters, or calls the cleanup callback on failure.
- `zfs_zevent_next()` returns the next event for a per-open stream cursor, duplicates the nvlist, reports per-stream dropped counts, and includes rate-limited drops.
- `zfs_zevent_wait()` waits interruptibly for new events or shutdown.
- `zfs_zevent_seek()` positions a stream cursor by EID, start, or end.
- `zfs_zevent_init()` and `zfs_zevent_destroy()` manage per-open zevent state.
- `zfs_zevent_drain_all()` clears all queued events during shutdown.

## FMA Nvlist Helpers

- `fm_nva_xcreate()` and `fm_nva_xdestroy()` create/destroy fixed-buffer nv allocators.
- `fm_nvlist_create()` creates an FMA nvlist with either caller-supplied allocation operations or default ZFS memory allocation wrappers.
- `fm_nvlist_destroy()` frees the nvlist and optionally its allocator handle.
- `fm_payload_set()` and `i_fm_payload_set()` add typed varargs payload members across scalar, array, string, nvlist, and boolean types while tracking failures.

## Ereport and FMRI Construction

- `fm_ereport_set()` builds an `ereport.*` class event with ENA, detector, and payload fields.
- `fm_fmri_hc_set()` creates hierarchical component FMRIs from name/id varargs.
- `fm_fmri_hc_create()` extends an existing hc-list from a base board FMRI with additional hc pairs.
- `fm_fmri_dev_set()`, `fm_fmri_cpu_set()`, `fm_fmri_mem_set()`, and `fm_fmri_zfs_set()` construct dev, cpu, mem, and zfs scheme FMRIs with version validation and optional authority/device fields.

## ENA Helpers

- `fm_ena_generate_cpu()` creates format 1 or 2 ENAs from timestamp and CPU id.
- `fm_ena_generate()` disables preemption while reading CPU id.
- `fm_ena_increment()`, `fm_ena_generation_get()`, `fm_ena_format_get()`, `fm_ena_id_get()`, and `fm_ena_time_get()` manipulate and decode ENA fields.

## Kstats and Lifecycle

- `erpt_kstat_data` tracks dropped ereports, set failures, FMRI failures, payload failures, and duplicate ereports.
- `fm_init()` creates the `zfs/fm` kstat, initializes zevent locks/lists/cv, and initializes ZFS ereport support.
- `fm_fini()` tears down ereport support, drains queued events, broadcasts shutdown, waits for blocked waiters, destroys synchronization primitives, and deletes kstats.
- `fm_erpt_dropped_increment()` records rate-limited event drops.

## Research Notes

This file is both protocol-construction utility code and the kernel event transport behind ZFS event consumers. It is careful about bounded event queue length, cursor invalidation on drain, and failure counters for observability.
