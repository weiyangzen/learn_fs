# sources/distributed-fs/ceph-client/include/net/proto_memory.h

Purpose: provides inline helpers for protocol/socket memory pressure and per-CPU fast-path accounting.

Important APIs and types: `SK_MEMORY_PCPU_RESERVE` defines the default per-CPU reserve in pages. Helpers test whether protocols have pressure accounting, read global and cgroup socket memory pressure, read allocated memory, drain per-CPU forward allocation to `proto->memory_allocated`, and add/subtract socket memory usage through per-CPU counters.

Control flow: socket allocation/free paths update per-CPU `per_cpu_fw_alloc`; when thresholds exceed `net_hotdata.sysctl_mem_pcpu_rsv`, the value is drained into the protocol atomic counter. Pressure checks combine memcg, protocol pressure, and socket bypass flag.

State and persistence: updates runtime protocol memory counters and per-CPU accounting only.

Dependencies and integration points: depends on socket/proto internals, memcg socket pressure, per-CPU counters, atomics, and net hotdata sysctls.

Risks and test signals: risks include per-CPU drift if drains are missed, bypass flag misuse, negative accounting, and pressure read races. Test TCP/UDP memory pressure, memcg pressure, per-CPU reserve sysctl changes, allocation/free balance, and protocols without pressure pointers.
