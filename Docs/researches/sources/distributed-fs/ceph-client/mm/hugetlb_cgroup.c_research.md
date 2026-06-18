# `sources/distributed-fs/ceph-client/mm/hugetlb_cgroup.c`

## Purpose
`hugetlb_cgroup.c` implements the hugetlb cgroup controller. It allocates per-cgroup hugetlb accounting state, charges and uncharges hugepage fault and reservation usage, reparents charged active pages when cgroups go offline, tracks NUMA usage, exposes cgroup v1 and v2 files for each hstate, and migrates cgroup metadata during hugepage migration.

## Important APIs, Types, And Functions
- Global controller state: `root_h_cgroup`, dynamically allocated `dfl_files`, and `legacy_files`.
- Counter helpers: `hugetlb_cgroup_counter_from_cgroup()`, `hugetlb_cgroup_counter_from_cgroup_rsvd()`, `hugetlb_cgroup_from_css()`, `hugetlb_cgroup_from_task()`, `parent_hugetlb_cgroup()`, and `hugetlb_cgroup_have_usage()`.
- Lifecycle: `hugetlb_cgroup_css_alloc()`, `hugetlb_cgroup_css_offline()`, `hugetlb_cgroup_css_free()`, `hugetlb_cgroup_init()`, and `hugetlb_cgroup_free()`.
- Charging API consumed by `hugetlb.c`: `hugetlb_cgroup_charge_cgroup()`, `hugetlb_cgroup_charge_cgroup_rsvd()`, `hugetlb_cgroup_commit_charge()`, `hugetlb_cgroup_commit_charge_rsvd()`, `hugetlb_cgroup_uncharge_folio()`, `hugetlb_cgroup_uncharge_folio_rsvd()`, `hugetlb_cgroup_uncharge_cgroup()`, `hugetlb_cgroup_uncharge_cgroup_rsvd()`, `hugetlb_cgroup_uncharge_counter()`, and `hugetlb_cgroup_uncharge_file_region()`.
- Event and file interfaces: `hugetlb_event()`, `hugetlb_cgroup_read_numa_stat()`, `hugetlb_cgroup_read_u64()`, `hugetlb_cgroup_read_u64_max()`, `hugetlb_cgroup_write()`, `hugetlb_cgroup_reset()`, `hugetlb_events_show()`, and `hugetlb_events_local_show()`.
- Cgroup file templates: `hugetlb_dfl_tmpl[]` for v2 (`max`, `rsvd.max`, `current`, `rsvd.current`, `events`, `events.local`, `numa_stat`) and `hugetlb_legacy_tmpl[]` for v1 (`limit_in_bytes`, `usage_in_bytes`, `max_usage_in_bytes`, `failcnt`, reservation variants, `numa_stat`).
- Initialization: `hugetlb_cgroup_file_init()` builds per-hstate cftypes and registers them with cgroup core. `hugetlb_cgrp_subsys` declares the controller callbacks.

## Control Flow
When a cgroup is created, `hugetlb_cgroup_css_alloc()` allocates a flexible `struct hugetlb_cgroup` sized for `nr_node_ids`, allocates per-node `hugetlb_cgroup_per_node` records, initializes page counters for every hstate, and records the root cgroup. In legacy mode it enables `failcnt` tracking. Limits are initialized to rounded-down `PAGE_COUNTER_MAX` values that align with each huge page size.

Fault and reservation charging starts in `__hugetlb_cgroup_charge_cgroup()`. The current task's hugetlb css is acquired under RCU with `css_tryget()`, then the proper fault or reservation `page_counter` is charged. On failure the function increments the `HUGETLB_MAX` event and drops the css reference. Fault charges release the css reference immediately after a successful charge because the charged folio will point at the cgroup. Reservation charges keep a css reference until the reservation region or counter is removed.

Commit functions run with `hugetlb_lock` held and attach the cgroup pointer to the folio, separately for real allocation and reservation charge. Non-reservation commits also increment per-node usage in `h_cg->nodeinfo[nid]->usage[idx]`. Uncharge functions clear the folio cgroup pointer, uncharge page counters, drop css references for reservations, and decrement per-node usage for real pages.

When a cgroup goes offline, `hugetlb_cgroup_css_offline()` repeatedly scans all hstate active lists under `hugetlb_lock` and calls `hugetlb_cgroup_move_parent()` for folios charged to the dying cgroup until no usage remains. Pages are moved to the parent or root counter without failure.

Cgroup file setup is generated per hstate. `hugetlb_cgroup_cfttypes_init()` formats file names with hugepage size prefixes, encodes hstate index and attribute in `cftype.private`, adjusts event file offsets for per-hstate arrays, and registers lockdep keys. The post-init step registers the generated cftypes for v1 and v2.

## State And Persistence Behavior
Each hugetlb cgroup owns two `page_counter` arrays per hstate: `hugepage[]` for instantiated pages and `rsvd_hugepage[]` for reservations. It also owns per-hstate event counters, event cgroup files, and per-node usage arrays. Usage is not persisted outside memory; it is reflected through cgroupfs files. Reservation cgroup references persist in `resv_map` or `file_region` metadata in `hugetlb.c` until the reserved range is deleted or the private VMA closes.

## Dependencies And Integration Points
The file depends on cgroup core, `page_counter`, NUMA node iteration, hugetlb folio metadata accessors, `hugetlb_lock`, hstate iteration, and cgroup file registration. It is called from `hugetlb.c` allocation, free, reservation, reservation-delete, cgroup-offline, and migration paths. Its `hugetlb_cgrp_subsys` object is consumed by kernel cgroup initialization.

## Risks
- Reservation css references must be exactly balanced. File regions can split and share source metadata, so `copy_hugetlb_cgroup_uncharge_info()` and per-region `css_get()` behavior in `hugetlb.c` are tightly coupled to these uncharge functions.
- Per-node usage is updated under `hugetlb_lock` and read with `READ_ONCE`; readers should expect approximate but consistent-enough values, especially for hierarchical NUMA stats that traverse descendant cgroups.
- Offline reparenting scans active lists until local usage drains. If folio cgroup tags or counters become inconsistent, the loop can spin or leave usage behind.
- cgroup v1/v2 file naming and `private` encoding must stay aligned with template order and hstate count. Incorrect offsets for event files can notify the wrong cgroup file.
- Limit writes round down to hugepage multiples; tests need to verify user-visible values because byte inputs can silently align down.

## Test Signals
- Create cgroup v1 and v2 hierarchies, set `max`/`limit_in_bytes` and `rsvd.max`/`rsvd.limit_in_bytes`, and verify faults fail with `events:max` or `failcnt` increments.
- Exercise reservation-only paths with mmap, truncate, VMA close, shared/private mappings, and region splits to confirm `rsvd.current` returns to zero.
- Offline a cgroup holding active huge pages and verify usage moves to the parent/root and no charged folios keep dangling css references.
- Verify `numa_stat` totals against per-node hugepage placement and hierarchical descendants.
- Run hugepage migration and confirm both fault and reservation cgroup tags move from old folio to new folio.
