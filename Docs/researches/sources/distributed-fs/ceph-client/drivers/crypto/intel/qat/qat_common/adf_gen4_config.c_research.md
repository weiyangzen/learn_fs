## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_config.c

Purpose: Builds default service instance configuration for Gen4 QAT devices and initializes the default service selection.

Important APIs/functions: `adf_gen4_dev_config()` creates common sections, chooses service-specific configuration through `adf_get_service_enabled()`, and marks the device configured. `adf_crypto_dev_config()` configures crypto instances using paired banks (`asym` on even bank, `sym` on odd bank) and writes `ADF_NUM_CY` plus zero `ADF_NUM_DC`. `adf_comp_dev_config()` configures compression instances with one bank per instance and writes `ADF_NUM_DC` plus zero `ADF_NUM_CY`. `adf_no_dev_config()` explicitly sets both counts to zero. `adf_gen4_cfg_dev_init()` creates the general section, defaults even accelerator ids to crypto and odd ids to compression, and saves a minimum heartbeat timer.

Control flow and state: Configuration is persisted in the QAT config table. Gen4 service mode controls which instance keys are present. `ADF_STATUS_CONFIGURED` is set only after successful instance configuration.

Dependencies/integration: Depends on config-service parsing, crypto/compression capability helpers, ring config strings, heartbeat setup, and transport macros. It is called before service instance creation.

Risks and test signals: The paired-bank crypto layout differs from Gen2 and must match Gen4 two-rings-per-bank behavior. Tests should validate each service mode (`SVC_SYM_ASYM`, `SVC_DC`, `SVC_DCC`, default/none), odd/even default service assignment, failure rollback behavior, and instance counts with CPU count versus bank count.
