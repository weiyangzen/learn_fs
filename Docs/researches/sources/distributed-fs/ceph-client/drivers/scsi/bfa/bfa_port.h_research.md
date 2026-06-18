<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.h

## Purpose
`bfa_port.h` declares the physical port and CEE service-module interfaces used by the BFA driver. It defines callback types, per-module state structures, DMA memory accessor macros, and public operations for port stats, port enable/disable, D-port state, CEE attributes, CEE statistics, and CEE stats reset.

## Important APIs, Types, And Functions
Physical port callback types are `bfa_port_stats_cbfn_t` and `bfa_port_endis_cbfn_t`. `struct bfa_port_s` stores the device pointer, IOC pointer, trace module, message tag, stats busy/callback/status fields, stats reset timestamp, caller stats buffer, stats DMA memory, enable/disable pending/callback/status fields, IOC notification entry, PBC/D-port flags, and module DMA segment descriptor. Public port prototypes are `bfa_port_attach()`, `bfa_port_notify()`, `bfa_port_get_stats()`, `bfa_port_clear_stats()`, `bfa_port_enable()`, `bfa_port_disable()`, `bfa_port_meminfo()`, `bfa_port_mem_claim()`, and `bfa_port_set_dportenabled()`.

CEE callback types are `bfa_cee_get_attr_cbfn_t`, `bfa_cee_get_stats_cbfn_t`, and `bfa_cee_reset_stats_cbfn_t`. `struct bfa_cee_cbfn_s` groups callback pointers and arguments. `struct bfa_cee_s` stores device and IOC pointers, pending/status fields for each operation, callbacks, IOC notification, trace module, caller/DMA pointers for attributes and stats, mailbox commands, and module DMA segment descriptor. Public CEE prototypes are `bfa_cee_meminfo()`, `bfa_cee_mem_claim()`, `bfa_cee_attach()`, `bfa_cee_get_attr()`, `bfa_cee_get_stats()`, and `bfa_cee_reset_stats()`.

## Control Flow
The header establishes asynchronous flow. Callers attach each module to an IOC, claim DMA memory sized by the `*_meminfo()` functions, then issue one operation at a time per busy flag. Operations return immediate `bfa_status_t` values for admission failures and later invoke callbacks for firmware completions. IOC events enter `bfa_port_notify()` and the CEE notify helper in the implementation to fail pending work.

## State And Persistence
All state is runtime memory owned by `struct bfa_port_s` and `struct bfa_cee_s`. Persistent adapter effects are indirect: port enable/disable changes firmware port state, stats clear resets firmware counters, and CEE reset clears firmware-side CEE stats. The header's timestamp field records when port stats were last reset in host time.

## Dependencies And Integration Points
The header includes `bfa_defs_svc.h`, `bfa_ioc.h`, and `bfa_cs.h`. It integrates with `struct bfa_modules_s` through `BFA_MEM_PORT_DMA()` and `BFA_MEM_CEE_DMA()` macros and with the IOC through mailbox commands, notification entries, and DMA address structures. Service data types such as `union bfa_port_stats_u`, `struct bfa_cee_attr_s`, and `struct bfa_cee_stats_s` come from the service definitions header.

## Risks And Test Signals
Risks include caller lifetime mistakes for asynchronous buffers/callback arguments, assuming multiple concurrent stats or enable/disable operations are supported, stale `pbc_disabled`/`dport_enabled` policy flags blocking expected port operations, and DMA memory not being claimed before issuing firmware requests. Since the header exposes internal module structures, layout changes can affect many compile units.

Good test signals include compile coverage of all module users, attach/memclaim before operation, one-operation-at-a-time admission behavior, callback invocation on success and IOC failure, D-port/PBC gating, CEE attr/stats/reset workflows, and DMA alignment matching `bfa_port.c` and CEE implementation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.h -->
