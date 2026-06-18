# sources/distributed-fs/ceph-client/samples/bpf/sockex3_kern.c

Purpose: advanced socket filter flow dissector using tail calls and per-CPU scratch state.

Important APIs/types/functions: parser stage constants, `struct flow_key_record`, `struct globals`, per-CPU array for scratch state, program array for tail calls, flow stats map, `this_cpu_globals`, `update_stats`, parser helpers for IP/TCP/UDP/MPLS/VLAN, and multiple `SEC("socket...")` programs.

Control flow: main socket program initializes per-CPU globals and dispatches parsing stages through tail calls. Stages parse Ethernet, VLAN/MPLS, IPv4/IPv6, and transport headers, then update flow packet/byte counters.

State and persistence: per-CPU scratch map holds parser state during packet processing; hash map stores persistent flow counters; program array stores tail-call targets.

Dependencies and integration: loaded by `sockex3_user.c`, which must populate/locate program array and maps. Requires tail-call support and packet socket attachment.

Risks: tail-call setup is fragile; missing program array entries truncate parsing. Per-CPU scratch assumes one packet context per CPU program execution. Parser complexity increases verifier sensitivity.

Test signals: attach successfully, verify tail-call programs loaded, send mixed protocol traffic, and observe flow counters.
