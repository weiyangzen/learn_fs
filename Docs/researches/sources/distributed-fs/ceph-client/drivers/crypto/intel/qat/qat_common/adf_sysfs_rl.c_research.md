# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_rl.c

Purpose: implements the `qat_rl` sysfs frontend for rate-limiting SLA operations. It stages input fields and executes add/update/remove/get/capability operations against the RL core.

Important APIs: `adf_sysfs_rl_add` and `adf_sysfs_rl_rm`. Attributes include `rp`, `id`, `cir`, `pir`, `srv`, `cap_rem`, and write-only `sla_op`.

Control flow and state: each parameter attribute reads/writes `rate_limiting->user_input` under an rwsem. `srv` and `cap_rem` parse service names and validate enabled service for SLA service. `sla_op_store` matches operation strings, then under write lock calls RL core functions. Add defaults parent to `RL_PARENT_DEFAULT_ID`, type to `RL_LEAF`, and updates `input.sla_id` with the new ID. Add initializes staged service fields to `SVC_BASE_COUNT`.

Dependencies and integration: depends on `adf_rl` APIs and device sysfs group management. Added by `adf_rl_start`, removed by `adf_rl_stop`.

Risks and test signals: staged input persists across operations; users must set fields in the right order. Test each operation, invalid service names, disabled services, concurrent sysfs writes, capability remaining defaults, and removal of all non-default SLAs.
