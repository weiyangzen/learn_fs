# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl.h

Purpose: defines the rate-limiting data model, user input format, hardware data, driver state, SLA node structure, constants, and public API.

Important types: `enum rl_node_type` defines root/cluster/leaf hierarchy. `struct adf_rl_sla_input_data` represents sysfs/user operations. `struct rl_slice_cnt` stores firmware slice counts. `struct adf_rl_interface_data` protects sysfs staging state. `struct adf_rl_hw_data` holds device-specific offsets/scales/throughput/slice data. `struct adf_rl` stores all live state. `struct rl_sla` represents one hierarchy node.

Control flow and state: state is per device through `accel_dev->rate_limiting`. The model caps roots, clusters, leaves, ring-pairs per leaf, and total SLA IDs with fixed arrays.

Dependencies and integration: includes service enums from `adf_cfg_services.h`; implemented by `adf_rl.c`, admin bridge, and sysfs frontend.

Risks and test signals: fixed limits must match hardware and sysfs expectations. Test maximum node counts, RP masks beyond device banks, service enablement, and public API behavior for default parent and empty IDs.
