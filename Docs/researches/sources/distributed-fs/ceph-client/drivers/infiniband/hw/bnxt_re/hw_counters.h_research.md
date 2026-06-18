# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/hw_counters.h

Purpose: declares the counter index ABI and in-driver statistics containers for `bnxt_re`.

Important APIs and types: `enum bnxt_re_hw_stats` defines RDMA stats array indices from basic packet/byte counters through RoCE transport errors, responder errors, request/response CQE rollups, opcode counters, RoCE-only packet/byte counters, out-of-buffer, CNP, and ECN counters. `BNXT_RE_NUM_STD_COUNTERS` marks the older standard counter boundary and `BNXT_RE_NUM_EXT_COUNTERS` is the full enum count. `struct bnxt_re_res_cntrs` tracks atomic live resource counts and watermarks. `struct bnxt_re_rstat` caches qplib error and extended stats. `struct bnxt_re_stats` aggregates RoCE stats, resource counters, and doorbell pacing counters.

Control flow and integration: no executable control flow. Function prototypes expose RDMA-core callbacks for allocating and filling port hardware stats.

State and persistence: all structs are runtime fields, normally embedded in `struct bnxt_re_dev`. Atomic counters represent live object counts; watermarks retain high-water values for the life of the device instance and are displayed through debugfs.

Dependencies: requires qplib stat structure definitions and RDMA `struct ib_device`/`struct rdma_hw_stats` through including files. It is included by `bnxt_re.h` and implemented by `hw_counters.c`.

Risks: enum ordering must remain synchronized with `bnxt_re_stat_descs[]` and every assignment in `hw_counters.c`. Adding a counter in the middle changes all later indices. Resource counters must be incremented/decremented consistently in verbs object lifecycle paths to keep debugfs reporting meaningful.

Test signals: compile-time array designated initializer coverage, RDMA stats descriptor count validation, resource churn tests for PD/QP/CQ/SRQ/MR/MW/AH counts and watermarks, and counter-index compatibility checks with user tooling.
