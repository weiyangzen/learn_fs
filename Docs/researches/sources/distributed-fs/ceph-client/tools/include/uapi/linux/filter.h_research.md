# sources/distributed-fs/ceph-client/tools/include/uapi/linux/filter.h

Purpose: defines classic Linux socket filter program structures and helper macros used with `SO_ATTACH_FILTER` and TUN/TAP filtering. It extends the common BPF instruction constants with socket-filter-specific return, misc, scratch-memory, and ancillary-data definitions.

Important APIs/types: `struct sock_filter` is one BPF instruction (`code`, true/false jumps, `k`). `struct sock_fprog` carries a program length and pointer to the instruction array. Macros include `BPF_STMT`, `BPF_JUMP`, `BPF_RVAL`, `BPF_A`, `BPF_MISCOP`, `BPF_TAX`, `BPF_TXA`, `BPF_MEMWORDS`, and `SKF_AD_*` negative-offset ancillary fields such as protocol, ifindex, mark, queue, CPU, VLAN tag, and random.

Control flow, state, and persistence: userspace builds an instruction array, passes it to the kernel, and the kernel validates and attaches it to a socket or TAP filter. The filter then runs per packet. Attached program state persists with the socket/device until detached or closed; scratch memory is per execution.

Dependencies and integration points: depends on `<linux/types.h>` and `bpf_common.h`. It integrates sockets, seccomp-like classic BPF infrastructure, packet capture, TUN/TAP, and network filtering tools.

Risks and test signals: risks are invalid jump offsets, negative ancillary offset misuse, program length limits, and pointer lifetime during attach. Tests should attach valid/invalid filters, validate ancillary loads, verify packet accept/drop behavior, and compile macros into known instruction arrays.
