<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_init.c -->
# sources/distributed-fs/ceph-client/security/lsm_init.c

## Purpose

`lsm_init.c` implements the generic LSM framework initialization pipeline: parsing boot ordering, enabling/disabling modules, assigning per-object blob offsets, registering static-call hook slots, initializing early and normal LSMs, creating blob caches, running staged initcalls, and notifying when all LSMs have started.

## Important APIs, Types, and Functions

- `lsm_choose_security()`, `lsm_choose_lsm()`, and `lsm_debug_enable()` parse `security=`, `lsm=`, and `lsm.debug`.
- `lsm_order_append()` and `lsm_order_parse()` build the enabled LSM order from built-in config, command line, legacy major selection, and first/last ordering classes.
- `lsm_prepare()` assigns blob offsets by accumulating `struct lsm_blob_sizes`.
- `lsm_init_single()` calls each enabled LSM's `init`.
- `lsm_static_call_init()` assigns a hook to an available static-call slot.
- `security_add_hooks()` records hook ownership and enables the static call branch for each hook.
- `early_security_init()` initializes early LSMs before normal security init.
- `security_init()` performs normal ordering, blob cache creation, initial cred/task blob allocation, and LSM init.
- `security_initcall_*()` run per-LSM staged initcall hooks from pure through late.

## Control Flow

Early LSMs are discovered from linker sections, force-enabled, appended to order, prepared, and initialized before normal command-line parsing. Normal initialization logs debug details when requested, chooses command-line `lsm=` over legacy `security=`, parses the selected list, appends `LSM_ORDER_FIRST` modules, then mutable listed modules, then a legacy major if specified, and finally `LSM_ORDER_LAST` modules. Nonselected modules are disabled.

For each enabled LSM, blob requests are aligned and converted into offsets while global blob sizes grow. Caches are created for file, backing-file, and inode blobs when needed. The current task's initial credentials and task blobs are allocated before non-early LSM init functions run. Hook registration does not append linked lists here; it installs static-call targets and activates branch keys, panicking if a hook exhausts the fixed per-hook LSM slot count.

After main initialization, separate kernel initcall levels invoke optional LSM initcall callbacks in the enabled order. The core level also initializes securityfs. The late level broadcasts `LSM_STARTED_ALL`.

## State and Persistence Behavior

Persistent state includes `lsm_active_cnt`, `lsm_idlist[]`, enabled flags in `struct lsm_info`, `lsm_order[]`, exclusive LSM selection, global blob sizes, and blob caches. Boot parameters are `__initdata` and discarded after init. Blob offsets assigned during init become stable contracts for all object allocations.

## Dependencies and Integration Points

The file depends on linker-provided LSM info sections, static call infrastructure, slab caches, the LSM blob allocator implementations, securityfs, and the LSM notifier chain. It is the central integration point for all built-in LSMs that use `DEFINE_LSM` or `DEFINE_EARLY_LSM`.

## Risks and Edge Cases

Ordering bugs can silently change security semantics when multiple LSMs stack. Exclusive LSM conflict handling must disable later incompatible modules. `security=` legacy behavior intentionally disables other legacy majors and is overridden by `lsm=`. Static-call slot exhaustion panics during boot. Blob offset alignment must be stable because every object allocation uses those offsets.

## Test Signals

Boot tests should cover default `CONFIG_LSM`, `lsm=` ordering, `security=` legacy selection, duplicate names, disabled modules, exclusive conflicts, first/last ordering, `lsm.debug` output, max LSM count handling, blob size/offset sanity, hook slot exhaustion under debug configs, staged initcall ordering, and `LSM_STARTED_ALL` notifier delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_init.c -->
