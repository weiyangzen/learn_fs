<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_proc.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_proc.c

## Purpose
`tls_proc.c` exports per-network-namespace kTLS statistics through `/proc/net/tls_stat` when `CONFIG_PROC_FS` is enabled. It is a small observability companion to `tls_main.c`.

## Important APIs, Types, and Functions
- `tls_mib_list[]` maps printed counter names to `LINUX_MIB_TLS*` indices.
- `tls_statistics_seq_show()` aggregates percpu TLS counters with `snmp_get_cpu_field_batch_cnt()` and prints a stable text table.
- `tls_proc_init()` creates `tls_stat` under a namespace's `proc_net`.
- `tls_proc_fini()` removes the proc entry during namespace teardown.

## Control Flow
`tls_main.c` allocates `net->mib.tls_statistics` and calls `tls_proc_init()` from pernet init. Reading the proc file invokes the seq callback, which batches all configured MIB counters and emits one line per counter. Namespace exit calls `tls_proc_fini()` before freeing the percpu MIB area.

## State and Persistence
The file owns no persistent state beyond the proc entry. The actual counters live in `net->mib.tls_statistics`; output is generated on demand and scoped to the active net namespace.

## Dependencies and Integration Points
It depends on procfs, seq_file, SNMP/MIB helpers, and `net/tls.h` counter definitions. It is compiled even without procfs, but the create/show logic is guarded by `CONFIG_PROC_FS`.

## Risks and Edge Cases
Counter list drift is the main maintenance risk: new TLS counters need a matching `SNMP_MIB_ITEM` to become visible. `tls_proc_fini()` calls `remove_proc_entry()` unconditionally; kernel proc removal tolerates absent entries, but init failure paths rely on this being safe.

## Test Signals
Attach kTLS sockets in TX/RX software and device modes, trigger decrypt/rekey/no-pad errors, then read `/proc/net/tls_stat` in the namespace and verify expected counters change. Namespace creation/destruction tests should show no proc entry leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_proc.c -->
