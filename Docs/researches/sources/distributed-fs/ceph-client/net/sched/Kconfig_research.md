# sources/distributed-fs/ceph-client/net/sched/Kconfig

Purpose: defines Linux traffic-control scheduler, classifier, ematch, action, and related feature configuration symbols. It controls which qdisc, classifier, action, and metadata modules are built into or as modules for `net/sched`.

Important symbols: top-level `NET_SCHED` enables QoS/fair queueing and selects FIFO support. Scheduler symbols include HTB, HFSC, PRIO, MULTIQ, RED/GRED/SFB/SFQ, TEQL, TBF, CBS, ETF, TAPRIO, NETEM, DRR, MQPRIO, SKBPRIO, CHOKE, QFQ, CODEL/FQ_CODEL, CAKE, FQ, HHF, PIE/FQ_PIE, INGRESS, PLUG, ETS, BPF qdisc, and DUALPI2. Classifier symbols include BASIC, ROUTE4, FW, U32 with optional perf/mark, FLOW, CGROUP, BPF, FLOWER, MATCHALL, and EMATCH variants. Action symbols include POLICE, GACT with optional probability, MIRRED, SAMPLE, NAT, PEDIT, SIMP, SKBEDIT, CSUM, MPLS, VLAN, BPF, CONNMARK, CTINFO, SKBMOD, IFE with metadata plugins, TUNNEL_KEY, CT, GATE, and `NET_TC_SKB_EXT`.

Control flow: Kconfig dependency logic exposes options only under `if NET_SCHED`. Many action configs depend on `NET_CLS_ACT`; netfilter-backed actions add `NETFILTER`, `NF_CONNTRACK`, mark, NAT, and flow-table dependencies. Defaults for queue discipline are selected through `NET_SCH_DEFAULT` choice and materialized in `DEFAULT_NET_SCH`.

State and persistence: selected symbols persist in the kernel `.config` and drive compilation, module names, and runtime feature availability. No runtime state is directly managed.

Dependencies and integration: consumed by the build system and C preprocessor. It aligns with `net/sched/Makefile`, user-facing `tc`/iproute2 features, and optional subsystems such as BPF, netfilter, CAN, textsearch, cgroups, and skb extensions.

Risks: dependency mistakes can allow uncompilable combinations or hide needed modules. Help text advertises module names and should remain synchronized with Makefile objects. Some options select helper libraries, so missing `select` lines can cause link errors.

Test signals: `allmodconfig`, `allyesconfig`, randconfig, module build coverage for each symbol, and iproute2 `tc` feature tests matching enabled symbols.
