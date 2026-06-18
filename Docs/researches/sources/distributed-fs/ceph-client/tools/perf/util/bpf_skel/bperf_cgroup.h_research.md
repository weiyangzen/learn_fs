# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.h

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.h

Purpose: this shared header defines verifier-sensitive constants for cgroup bperf BPF code and user-space sizing.

Important definitions: `BPERF_CGROUP__MAX_LEVELS` caps cgroup ancestor traversal at 10 levels. `BPERF_CGROUP__MAX_EVENTS` caps events per cgroup at 128.

Control flow and state: there is no executable logic. The constants bound BPF loops and user-space maximum test loads.

Dependencies and integration: included by `bperf_cgroup.bpf.c` and `bpf_counter_cgroup.c`; both must agree on these limits.

Risks: changing either value affects verifier code size and runtime coverage. Lowering them can silently exclude deep cgroup ancestors or too many events; raising them can make the BPF program unloadable.

Test signals: run the debug max-event load path and cgroup stat sessions near both configured limits.
