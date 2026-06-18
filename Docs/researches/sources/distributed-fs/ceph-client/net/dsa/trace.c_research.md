# sources/distributed-fs/ceph-client/net/dsa/trace.c

Purpose: implements helper functions used by DSA tracepoints defined in `trace.h`, and enables tracepoint generation by defining `CREATE_TRACE_POINTS`.

Important APIs/functions: `dsa_db_print()` formats a `struct dsa_db` as port, LAG, bridge, or unknown into a fixed buffer. `dsa_port_kind()` maps DSA port types to stable strings: user, cpu, dsa, or unused.

Control flow: tracepoint fast-assign code calls these helpers to produce printable database and port-kind fields. The file includes `trace.h` after `CREATE_TRACE_POINTS`, so the kernel trace infrastructure emits the tracepoint definitions here.

State and persistence: no runtime state is owned. Trace output is transient through ftrace/perf infrastructure.

Dependencies and integration: depends on DSA database and port structures from `trace.h` includes. It integrates with FDB, MDB, LAG, and VLAN trace events in the DSA core.

Risks and test signals: formatting uses `sprintf()` into `DSA_DB_BUFSIZ`, whose size is chosen in the header. Tests should compile with tracing enabled and exercise FDB/MDB/VLAN operations to ensure trace events print correct device, bridge, LAG, and port information.
