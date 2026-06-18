<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sock_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sock_diag.h

Purpose: defines generic socket diagnostics netlink commands, memory-info indexes, multicast groups, and BPF socket-storage diagnostic attributes.

Important APIs, types, and functions: command IDs include `SOCK_DIAG_BY_FAMILY` and `SOCK_DESTROY`. `struct sock_diag_req` selects family and protocol. `SK_MEMINFO_*` indexes describe receive/send buffer allocation, queued memory, optmem, backlog, and drops. `sknetlink_groups` defines destroy notification groups. BPF storage request/reply/map-value attribute enums define how socket-local BPF storage is requested and returned.

Control flow: diagnostic tools send sock_diag netlink requests by family/protocol, optionally request memory or BPF storage data, and receive family-specific dumps. Destroy commands can request socket termination where supported.

State and persistence behavior: responses are snapshots of live socket memory and optional BPF storage state. Destroy commands mutate socket state. The header stores no state.

Dependencies and integration points: depends on Linux types and integrates with inet/unix/packet/smc diagnostics, netlink multicast destroy notifications, BPF maps, and tools such as `ss`.

Risks and edge cases: the macro typo `SK_DIAB_BPF_STORAGE_REP_MAX` is exported ABI and cannot simply be renamed without compatibility care. BPF storage values are variable length and must be policy-checked. Socket destruction requires permission and race handling.

Test signals: sock_diag dumps for multiple families, memory-info indexes, destroy notification groups, BPF storage map fd requests and replies, malformed attribute rejection, and namespace/permission tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sock_diag.h -->
