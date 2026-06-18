# sources/distributed-fs/ceph-client/net/sched/act_bpf.c

Purpose: implements the `bpf` traffic-control action, allowing a classic BPF instruction array or an eBPF `BPF_PROG_TYPE_SCHED_ACT` program to decide packet action results.

Important APIs/functions: `tcf_bpf_act()` runs the program; `tcf_bpf_init()` parses and installs/replaces programs; `tcf_bpf_dump()` reports program parameters, ID/tag/name or classic instructions; `tcf_bpf_cleanup()` releases program resources. `tcf_bpf_init_from_ops()` creates classic BPF with `bpf_prog_create()`, while `tcf_bpf_init_from_efd()` gets an eBPF program by fd.

Control flow: init validates `TCA_ACT_BPF_PARMS`, allocates or finds an action index, checks the configured control action, requires exactly one of classic ops or eBPF fd, installs new config under the action lock, assigns the filter with RCU, and synchronizes before freeing replaced programs. Runtime updates stats, adjusts skb data pointers at ingress by pushing/pulling MAC header, runs the program, normalizes the returned opcode, drops prefetched sockets for non-OK results, and counts drops on `TC_ACT_SHOT`.

State and persistence: action state stores the RCU `bpf_prog *filter`, optional copied classic instructions, optional eBPF name, instruction count, action opcode, stats, and IDR-managed action lifetime. eBPF program refs are held with `bpf_prog_get_type()`/`bpf_prog_put()`.

Dependencies and integration: integrates TC action API, Linux BPF verifier/program subsystem, rtnetlink attributes, module/pernet registration, and ingress skb data-pointer conventions.

Risks: replacing programs requires RCU synchronization to avoid freeing code still executing. Classic and eBPF encodings are mutually exclusive; accepting both would make lifetime ambiguous. Ingress MAC push/pull must remain balanced. Unknown BPF return codes intentionally become `TC_ACT_UNSPEC`.

Test signals: classic BPF and eBPF install/dump/delete, invalid fd/type rejection, replacement while packets run, ingress versus egress program execution, return-code mapping, drop statistics, and module autoload via `act_bpf`.
