# sources/distributed-fs/ceph-client/net/netfilter/x_tables.c

Purpose: core x_tables backend for legacy iptables/ip6tables/arptables/ebtables: match/target registration, table validation/replacement, compat translation, proc exposure, per-net lifetime, and exported helper APIs.

Important APIs/types/functions: `xt_register_match(es)`, `xt_register_target(s)`, `xt_find_match()`, `xt_request_find_target()`, `xt_check_match()`, `xt_check_target()`, `xt_check_entry_offsets()`, `xt_alloc_table_info()`, `xt_replace_table()`, `xt_register_table()`, `xt_unregister_table_pre_exit()`, `xt_unregister_table_exit()`, `xt_hook_ops_alloc()`, `xt_register_template()`, `xt_proto_init()`, and compat/counter helpers.

Control flow: extensions register in per-family lists. Rule load resolves modules, checks sizes/table/proto/hooks/offsets/verdicts, invokes extension checkentry, and installs table info. Replacement allocates jumpstacks, swaps `table->private` with barriers under bottom-half exclusion, waits for per-cpu readers via `xt_recseq`, and returns old info. Namespace teardown moves tables to dead lists, unregisters hooks, then finalizes cleanup.

State and persistence: global family registries, per-net live/dead tables, proc files, templates, compat offset tables, per-cpu recursion counters, and exported `xt_tee_enabled`. Dependencies include module autoload, procfs, audit, net namespaces, user-copy, netfilter hooks, RCU, and compat ABI. Risks: malformed user offsets/sizes, memory ordering, module refs, compat overflow, teardown ordering, and large allocations. Test signals: autoload, invalid entries, compat 32-bit paths, concurrent replacement, namespace exit, proc reads, and template lazy init.
