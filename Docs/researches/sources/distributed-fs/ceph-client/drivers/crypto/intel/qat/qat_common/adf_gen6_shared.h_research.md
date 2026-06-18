# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_shared.h

Purpose: declares the Gen6 shared helper entry points used by Gen6 device drivers to initialize common operations by reusing Gen4 implementations.

Important API: forward-declares `struct adf_hw_csr_ops`, `struct qat_migdev_ops`, `struct adf_accel_dev`, and `struct adf_pfvf_ops`; declares `adf_gen6_init_pf_pfvf_ops`, `adf_gen6_init_hw_csr_ops`, `adf_gen6_comp_dev_config`, `adf_gen6_no_dev_config`, and `adf_gen6_init_vf_mig_ops`.

Control flow and state: header-only declarations; no state or behavior. It sets the compile-time interface boundary between Gen6 hardware files and common/Gen4 helpers.

Dependencies and integration: included by Gen6 hardware-data sources and implemented by `adf_gen6_shared.c`. It indirectly connects Gen6 devices to PF/VF communication, CSR operations, compression configuration, and VF live migration.

Risks and test signals: declaration/implementation mismatch would fail build or link. Functional risk follows from callers assuming Gen4-compatible behavior. Test via build coverage for Gen6 configs and runtime smoke tests for PF/VF, CSR, config, and migration init hooks.
