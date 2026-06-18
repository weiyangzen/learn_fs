# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_shared.c

Purpose: provides a thin Gen6 compatibility layer that reuses Gen4 implementations for common QAT mechanisms. It avoids duplicating CSR, PF/VF, VF migration, and device configuration logic when Gen6 register layout or behavior matches Gen4.

Important APIs: `adf_gen6_init_pf_pfvf_ops()` delegates to `adf_gen4_init_pf_pfvf_ops`; `adf_gen6_init_hw_csr_ops()` delegates to Gen4 CSR operations; `adf_gen6_comp_dev_config()` and `adf_gen6_no_dev_config()` call shared Gen4 configuration helpers; `adf_gen6_init_vf_mig_ops()` delegates to Gen4 VF migration operations. All are exported GPL symbols.

Control flow and state: no local state. Each function directly initializes an ops table or returns another helper's result. The state changed is owned by caller-provided ops structures or `accel_dev` configuration.

Dependencies and integration: depends on Gen4 config, CSR, PF/VF, and migration headers plus the Gen6 public header. Device-specific Gen6 drivers use these symbols during hardware data initialization.

Risks and test signals: risk is semantic drift if Gen6 hardware diverges from Gen4. Test by probing Gen6 PF/VF messaging, CSR ring control, compression/no-device config, and migration paths under the device-specific driver.
