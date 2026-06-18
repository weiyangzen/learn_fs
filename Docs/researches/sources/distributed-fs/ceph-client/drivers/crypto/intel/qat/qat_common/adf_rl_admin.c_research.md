# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl_admin.c

Purpose: bridges rate-limiting SLA state to firmware admin commands. It prepares DMA-backed SLA configuration parameters and sends firmware init/add/update/delete messages.

Important APIs: `adf_rl_send_admin_init_msg`, `adf_rl_send_admin_add_update_msg`, and `adf_rl_send_admin_delete_msg`. Helpers fill `icp_qat_fw_init_admin_req` and `icp_qat_fw_init_admin_sla_config_params`.

Control flow and state: init sends an RL init command and stores returned slice counts, mapping UCS count to symmetric crypto slice tokens. Add/update allocates coherent DMA for firmware params, calculates PCIe in/out, slice utilization, and AE utilization token values from SLA CIR/PIR, copies RP IDs, sends the admin command, then frees DMA. Delete forwards node ID and node type.

Dependencies and integration: depends on admin firmware functions, RL calculator functions, DMA mapping, and `struct rl_sla`.

Risks and test signals: DMA allocation failure aborts add/update; token calculations must match firmware units. Test firmware init failure, add/update DMA failure, params content for each service, and delete after node removal.
