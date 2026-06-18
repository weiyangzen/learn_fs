# sources/distributed-fs/ceph-client/include/linux/sched/sd_flags.h

Purpose: X-macro list of scheduler-domain balancing/topology flags and their meta-properties.

Important APIs and types: `SDF_SHARED_CHILD`, `SDF_SHARED_PARENT`, `SDF_NEEDS_GROUPS`, and `SD_FLAG(...)` entries such as `SD_BALANCE_NEWIDLE`, `SD_BALANCE_EXEC`, `SD_BALANCE_FORK`, `SD_BALANCE_WAKE`, `SD_WAKE_AFFINE`, `SD_ASYM_CPUCAPACITY`, `SD_SHARE_CPUCAPACITY`, `SD_CLUSTER`, `SD_SHARE_LLC`, `SD_SERIALIZE`, `SD_ASYM_PACKING`, `SD_PREFER_SIBLING`, and `SD_NUMA` are the declarations.

Control flow: `sched/topology.h` includes this file with different `SD_FLAG` definitions to generate indexes, bit values, and debug metadata; topology construction applies meta-flags to propagate behavior through domain hierarchy.

State and persistence: no runtime state is stored here, but generated flag bits configure scheduler-domain runtime behavior.

Dependencies and integration points: depends on being included only with `SD_FLAG` defined. Integrates topology description with load balancing, wake affinity, NUMA, SMT/cache sharing, and asymmetric CPU capacity.

Risks and test signals: risks include incorrect import without `SD_FLAG`, wrong meta-flag propagation, bit-count overflow, and balancing regressions from flag semantics changes. Test sched-domain debug output, topology rebuilds, NUMA/SMT/asym-capacity machines, cpuset relax levels, and compile generation.
