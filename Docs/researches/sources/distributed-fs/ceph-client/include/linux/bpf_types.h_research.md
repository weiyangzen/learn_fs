# sources/distributed-fs/ceph-client/include/linux/bpf_types.h

Purpose: Central macro inventory of BPF program types, map types, and link types. It is intentionally not directly included by ordinary users; instead other headers define `BPF_PROG_TYPE`, `BPF_MAP_TYPE`, and `BPF_LINK_TYPE` macros to generate declarations, tables, or switch cases from one authoritative list.

Important APIs/types/functions: Program entries map UAPI program types to internal operation names and context types, gated by configs such as `CONFIG_NET`, `CONFIG_CGROUP_BPF`, `CONFIG_BPF_EVENTS`, `CONFIG_BPF_LIRC_MODE2`, `CONFIG_INET`, `CONFIG_BPF_JIT`, `CONFIG_BPF_LSM`, and `CONFIG_NETFILTER_BPF_LINK`. Map entries enumerate array/hash/prog/perf/cgroup/local-storage/dev/cpu/xsk/sock/ringbuf/bloom/user-ringbuf/arena/insn-array and other map ops. Link entries enumerate raw tracepoint, tracing, cgroup, iterator, netns, XDP, netfilter, TCX, netkit, sockmap, perf event, kprobe/uprobe multi, and struct_ops links.

Control flow: This file is compile-time data. Consumers include it after defining macros to emit extern declarations in `bpf.h`, operation tables in BPF core, or string/metadata mappings elsewhere.

State/persistence: No runtime state. Its ordering and conditional presence influence compiled kernel capability surfaces and generated arrays.

Dependencies/integration: Integrates BPF UAPI enum values with internal ops symbols such as `sk_filter_prog_ops`, `array_map_ops`, or `raw_tracepoint` link ops. Depends heavily on Kconfig guards matching implementation availability.

Risks/test signals: Risks include forgetting to add new types to this inventory, using the wrong context type, mismatching config guards, or breaking macro consumers by changing entry shape. Test signals include allconfig/allyesconfig/randconfig builds, BPF syscall feature probes, bpftool feature output, selftests for every new prog/map/link type, and compile failures from missing ops externs.
