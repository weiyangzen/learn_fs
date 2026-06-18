# sources/distributed-fs/ceph-client/net/sched/sch_mqprio_lib.h

Purpose: declares the shared mqprio helper API for validation, qopt reconstruction, and frame-preemption offload conversion.

Important APIs, types, and functions: forward-declares `struct net_device`, `struct netlink_ext_ack`, and `struct tc_mqprio_qopt`; includes `<linux/types.h>` for `u32`; and declares `mqprio_validate_qopt`, `mqprio_qopt_reconstruct`, and `mqprio_fp_to_offload`. The `mqprio_fp_to_offload` prototype references `struct tc_mqprio_qopt_offload` through scheduler headers included by users.

Control flow: no executable control flow exists in the header. It provides compile-time linkage between qdisc implementations and `sch_mqprio_lib.c`.

State and persistence behavior: no state is owned here. The header constrains callers to pass explicit input/output structures.

Dependencies and integration points: the include guard `__SCH_MQPRIO_LIB_H` prevents duplicate declarations. Consumers must include the appropriate packet scheduler definitions for mqprio constants and offload struct layout. The file is intentionally local to `net/sched`, not a broad userspace ABI header.

Risks: signature drift between this header and implementation would break mqprio/taprio builds. Because one prototype uses `TC_QOPT_MAX_QUEUE` and `struct tc_mqprio_qopt_offload`, include ordering matters for consumers.

Test signals: build coverage is the main signal: compile all mqprio-lib consumers, verify no missing declarations or incompatible prototypes, and ensure symbol exports in the C file match the header.
