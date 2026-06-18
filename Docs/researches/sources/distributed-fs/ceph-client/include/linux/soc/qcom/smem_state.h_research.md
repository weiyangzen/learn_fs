# sources/distributed-fs/ceph-client/include/linux/soc/qcom/smem_state.h

Purpose: This header defines Qualcomm SMEM state bit providers/consumers used for low-latency shared state flags between processors.

Important APIs/types/functions: `struct qcom_smem_state_ops` contains an `update_bits` operation. Consumer APIs include `qcom_smem_state_get`, `devm_qcom_smem_state_get`, `qcom_smem_state_put`, and `qcom_smem_state_update_bits`. Provider APIs include `qcom_smem_state_register` and `qcom_smem_state_unregister`. Disabled stubs return errors or no-op.

Control flow: Providers register a state object for a DT node. Consumers get a state plus assigned bit, update masked bits, and release the handle.

State and persistence: State bits are stored in provider-managed shared memory or registers and may be visible to remote processors through SMEM.

Dependencies and integration: Uses device tree nodes, devices, and Qualcomm SMEM state providers. Integrates with remoteproc handshakes, modem/WLAN/audio state, and power-management signaling.

Risks and test signals: Bit allocation mismatches can signal the wrong state to firmware. Test DT bit parsing, managed get cleanup, concurrent update_bits, provider unregister with consumers, and disabled-config builds.
