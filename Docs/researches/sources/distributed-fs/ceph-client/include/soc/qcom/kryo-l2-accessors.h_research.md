# sources/distributed-fs/ceph-client/include/soc/qcom/kryo-l2-accessors.h

Purpose: declares low-level accessors for Qualcomm Kryo L2 indirect registers.

Important APIs/types/functions: exports `kryo_l2_set_indirect_reg(u64 reg, u64 val)` and `kryo_l2_get_indirect_reg(u64 reg)`.

Control flow: consumers pass an indirect register selector and either write a value or read the current value. The implementation serializes the platform-specific indirect access sequence.

State and persistence: the accessors read and write CPU/L2 PMU and cache-control registers. Persistent effects depend on the selected register, including counter enables, event types, filters, overflow status, and CPU clock configuration fields.

Dependencies and integration: implemented in `drivers/soc/qcom/kryo-l2-accessors.c`. Consumers include `drivers/perf/qcom_l2_pmu.c` and Qualcomm CPU clock code.

Risks: these are privileged CPU-register accesses. Wrong register IDs or concurrency mistakes can corrupt PMU state or CPU clock behavior. Test signals include qcom L2 PMU perf event tests, counter overflow handling, CPU clock changes, and SMP stress.
