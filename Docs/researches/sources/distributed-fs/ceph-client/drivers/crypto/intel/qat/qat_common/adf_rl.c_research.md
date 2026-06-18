# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl.c

Purpose: implements QAT rate-limiting SLA management. It maintains an in-memory hierarchy of root, cluster, and leaf nodes, validates user SLA requests, maps ring pairs to leaves, writes hierarchy mappings to hardware CSRs, sends admin firmware add/update/delete/init messages, and exposes lifecycle hooks used by device startup.

Important APIs: `adf_rl_init`, `adf_rl_start`, `adf_rl_stop`, `adf_rl_exit`, `adf_rl_add_sla`, `adf_rl_update_sla`, `adf_rl_get_sla`, `adf_rl_remove_sla`, `adf_rl_remove_sla_all`, `adf_rl_get_capability_remaining`, `adf_rl_get_sla_arr_of_type`, and token calculators for PCIe bandwidth, AE cycles, and slice tokens.

Control flow and state: `struct adf_rl` owns SLA pointer arrays, root/cluster/leaf arrays, RP usage flags, user-input state, and `rl_lock`. Start validates firmware capability, initializes token bucket registers, sends RL init, creates default root/cluster nodes for enabled services, and adds sysfs. Add/update validates input, finds parent, checks budget, writes node mappings, sends admin message, then updates budget and arrays. Removal clears mappings, sends delete, frees nodes.

Dependencies and integration: uses hardware RL offsets/scales, service mapping, PMISC CSRs, admin firmware, and `adf_sysfs_rl`.

Risks and test signals: budget arithmetic and cleanup ordering are critical; failures after CSR writes but before array insertion can leave hardware state. Test add/update/remove under each service, parent budget constraints, RP reuse rejection, default-node initialization, FW capability absence, and repeated start/stop.
