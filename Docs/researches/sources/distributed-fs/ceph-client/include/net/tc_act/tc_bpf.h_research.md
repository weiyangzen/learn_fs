<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_bpf.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_bpf.h

Purpose: Declares the traffic-control BPF action private state.

Important APIs/types/functions: `struct tcf_bpf` embeds `struct tc_action`, an RCU-protected `struct bpf_prog *filter`, either a BPF fd or classic BPF instruction count, raw `sock_filter` operations, and an optional BPF action name. `to_bpf()` casts a generic `tc_action`.

Control flow: TC action creation loads or references a BPF program and stores it in `filter`; packet action execution dereferences the program and runs it to decide the TC action result. Replacement is RCU-based.

State and persistence behavior: Action state is per TC action instance. The BPF program pointer is RCU-protected; classic BPF ops and name are owned by action lifetime.

Dependencies/integration points: Depends on Linux filter/BPF infrastructure and `net/act_api.h`. Integrated with `tc_wrapper.h` as `tcf_bpf_act`.

Risks: Program lifetime, RCU dereference, verifier assumptions, and fd/program replacement are safety-critical.

Test signals: TC BPF selftests for direct-action and legacy modes, action replace/delete under traffic, verifier rejection, and RCU/KASAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_bpf.h -->
