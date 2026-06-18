## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_config.h

Purpose: Publishes Gen4 configuration entry points and the service-specific config builders.

Important APIs/types: Declares `adf_gen4_dev_config()`, `adf_gen4_cfg_dev_init()`, `adf_crypto_dev_config()`, `adf_comp_dev_config()`, and `adf_no_dev_config()`.

Control flow/state: The header owns no state; functions update the per-device config database and status bits in the implementation.

Dependencies/integration: Included by Gen4 product-specific drivers and any code that needs to reuse the standard Gen4 crypto/compression/no-service config builders.

Risks and test signals: Because service-specific helpers are exported through the header, ABI/API drift should be caught by build coverage across all Gen4 product drivers.
