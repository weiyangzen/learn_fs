# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl_admin.h

Purpose: declares the rate-limiting admin firmware bridge.

Important API: `adf_rl_send_admin_init_msg`, `adf_rl_send_admin_add_update_msg`, and `adf_rl_send_admin_delete_msg`.

Control flow and state: no header behavior. Admin bridge state is transient DMA request memory in the implementation.

Dependencies and integration: includes `adf_rl.h` for `struct rl_slice_cnt` and `struct rl_sla`. Used by `adf_rl.c`.

Risks and test signals: signature changes affect RL core build. Functional tests should verify RL core handles each admin function's failure return without corrupting SLA state.
