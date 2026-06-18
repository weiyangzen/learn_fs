# sources/distributed-fs/ceph-client/fs/resctrl/ctrlmondata.c

## Purpose
`ctrlmondata.c` implements the resctrl user-facing control and monitor data operations behind files such as `schemata`, `mba_MBps_event`, monitor event files, `io_alloc`, and `io_alloc_cbm`. It translates kernfs reads/writes into staged resctrl domain configuration, architecture counter reads, and optional I/O allocation cache partitioning.

## Important APIs, Types, And Functions
The local `struct rdt_parse_data` carries a CLOSID, current group mode, and value buffer into parser callbacks. `ctrlval_parser_t` abstracts schema-specific parsers. `bw_validate()` and `parse_bw()` validate memory bandwidth range controls, including MBA software-controller MBps mode. `cbm_validate()` and `parse_cbm()` validate cache bitmasks, enforce contiguous-mask rules when sparse masks are unsupported, enforce minimum bits, and reject overlap with exclusive or pseudo-locked allocations. `rdtgroup_schemata_write()` parses multiline `RESOURCE:id=value;...` updates and commits them via `resctrl_arch_update_domains()`. `rdtgroup_schemata_show()` formats current allocations, with special handling for pseudo-lock setup and pseudo-locked groups.

Monitoring entry points include `mon_event_read()`, which prepares `struct rmid_read` and dispatches `mon_event_count()` on an appropriate CPU or directly for `any_cpu` events, and `rdtgroup_mondata_show()`, which resolves `struct mon_data` from `kn->priv`, reads a domain or an SNC sum, and prints numeric, fixed-point, `Error`, `Unavailable`, or `Unassigned` output. `print_event_value()` formats fixed-point event values according to the architecture-provided binary fractional bit count.

I/O allocation support is exposed through `resctrl_io_alloc_show()`, `resctrl_io_alloc_write()`, `resctrl_io_alloc_cbm_show()`, and `resctrl_io_alloc_cbm_write()`. It reserves the highest usable CLOSID from `resctrl_io_alloc_closid()`, initializes its cache bitmask through `resctrl_io_alloc_init_cbm()`, and keeps CDP code/data peers in sync when CDP is enabled.

## Control Flow
For `schemata` writes, the function requires a trailing newline, locks the live rdtgroup, clears `last_cmd_status`, rejects pseudo-locked groups, clears staged configs, parses each resource line, and then commits staged configs for all non-MBA-SC resources. If the group is in `RDT_MODE_PSEUDO_LOCKSETUP`, a valid CBM initializes the pseudo-lock region and triggers `rdtgroup_pseudo_lock_create()`. All exits clear staged configs and unlock.

For monitor reads, `rdtgroup_mondata_show()` locks the group, gets the event metadata from kernfs private data, resolves a resource and domain, then calls `mon_event_read()`. SNC summing is expressed by a `NULL` domain header and a cacheinfo shared CPU map. `mon_event_read()` allocates architecture monitor context unless assignable MBM counters are active, chooses a housekeeping CPU for domain-scoped reads, uses `smp_call_on_cpu()` or `smp_call_function_any()` as needed, and frees the context.

For `io_alloc`, enabling validates hardware support and CLOSID availability, reserves a fixed CLOSID, initializes the CBM, and calls `resctrl_arch_io_alloc_enable()`. Disabling releases the fixed CLOSID after architecture state is changed off.

## State And Persistence
The file does not own persistent on-disk state. It mutates in-memory staged configs in `rdt_ctrl_domain::staged_config`, per-domain MBA-SC values in `mbps_val`, rdtgroup `mba_mbps_event`, pseudo-lock region fields, and architecture control registers through resctrl architecture hooks. User-visible failure text is accumulated in `last_cmd_status` through helpers from `rdtgroup.c`.

## Dependencies And Integration Points
It depends on `internal.h` definitions, global `resctrl_schema_all`, `rdtgroup_mutex`, group locking via `rdtgroup_kn_lock_live()`, CLOSID helpers, pseudo-lock helpers, and architecture APIs such as `resctrl_arch_update_domains()`, `resctrl_arch_rmid_read()`, `resctrl_arch_mon_ctx_alloc()`, CDP status helpers, and I/O allocation hooks. `rdtgroup.c` wires these callbacks into kernfs `rftype` definitions.

## Risks
Parser correctness is critical because bad validation can over-allocate cache ways, violate exclusive/pseudo-lock isolation, or leave stale staged configs. All functions assume `rdtgroup_mutex` and CPU hotplug locks are held where asserted; missing those locks would race domain lists or group deletion. Monitor reads must handle architecture-specific errors without exposing misleading counters. I/O allocation uses a fixed high CLOSID, so conflicts with existing groups and CDP-halved CLOSID ranges are important edge cases.

## Test Signals
Useful tests exercise valid and invalid `schemata` writes, duplicate domain entries, sparse and non-sparse CBMs, MBA min/max/granularity rounding, pseudo-lock setup rejection for MBA, `mba_MBps_event` selection when events are disabled, monitor reads with offline domains, SNC sum files, fixed-point formatting, and `io_alloc` enable/disable plus `io_alloc_cbm` wildcard and per-domain updates.
