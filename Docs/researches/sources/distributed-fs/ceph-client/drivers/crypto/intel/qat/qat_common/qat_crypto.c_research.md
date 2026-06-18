# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_crypto.c

Purpose: implements QAT crypto service instance management for symmetric and asymmetric crypto rings. It registers the `qat_crypto` ADF service, builds ring pairs from config, and provides a NUMA/load-aware instance picker for crypto algorithms.

Important APIs and functions: `qat_crypto_register()`/`qat_crypto_unregister()` register the service. `qat_crypto_event_handler()` maps init/shutdown events to `qat_crypto_create_instances()` and `qat_crypto_free_instances()`. `qat_crypto_get_instance_node()` scans ADF devices for a started accelerator on the requested NUMA node, falls back to any started device, then chooses the least-used instance. `qat_crypto_vf_dev_config()` validates VF ring/service mapping before invoking hardware `dev_config()`.

Control flow: service initialization reads `ADF_NUM_CY`, then each instance reads sym/asym bank numbers and ring sizes. It halves configured message counts for TX/RX pairing, creates symmetric TX, asymmetric/PKE TX, symmetric RX, and asymmetric/PKE RX rings, and attaches callbacks `qat_alg_callback` and `qat_alg_asym_callback`. Shutdown drains references by repeatedly putting held instances, removes all rings, deletes the list node, and frees instance memory.

State and persistence: per-device state is `accel_dev->crypto_list`; per-instance state includes ring pointers, `refctr`, ID, owning device, and backlog. Device references are acquired in `qat_crypto_get_instance_node()` and released by `qat_crypto_put_instance()`.

Dependencies and integration points: depends on ADF config strings, transport ring creation/removal, gen2 default ring/service mapping for VFs, and QAT firmware request/response sizes. It integrates with all QAT symmetric/asymmetric algorithm implementations through `struct qat_crypto_instance`.

Risks: create-instance error handling consistently jumps to cleanup, but the free path decrements references by reading the current refcount while changing it in the loop; concurrent users must be quiesced before shutdown. `qat_crypto_init()` maps all create errors to `-EFAULT`, losing diagnostic precision. Tests should cover partial ring creation failures, VF config mismatch, NUMA fallback, async callback completion, and refcount balance under request churn.
