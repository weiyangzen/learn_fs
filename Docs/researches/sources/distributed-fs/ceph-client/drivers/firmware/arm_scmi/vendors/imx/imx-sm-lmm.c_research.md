# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-lmm.c

Purpose: This file implements the NXP i.MX SCMI Logical Machine Manager vendor protocol for logical machine information, boot/power-on, reset vector setup, and shutdown.

Important APIs/types/functions: `struct scmi_imx_lmm_priv` stores logical-machine count. Ops are `lmm_power_boot`, `lmm_info`, `lmm_reset_vector_set`, and `lmm_shutdown`. `scmi_imx_lmm_protocol_attributes_get()` reads and caps the number of logical machines at `SCMI_IMX_LMM_NR_MAX`. `scmi_imx_lmm_attributes()` reads per-LM state, error status, and name.

Control flow: Init reads the protocol version and LM count, rejects counts above 16, and stores private state. `lmm_power_boot()` validates LM ID and chooses boot or power-on command. `lmm_shutdown()` validates LM ID and sends a graceful flag only when requested. `lmm_reset_vector_set()` builds LM ID, CPU ID, reserved flags as zero, and 64-bit reset vector before sending. Attribute reads are on demand through the ops table.

State and persistence: The driver caches only LM count. LM state, error status, and reset vectors are controlled by firmware/hardware. No persistent kernel storage exists.

Dependencies and integration points: It depends on SCMI core xfer ops, public i.MX protocol definitions, and vendor protocol registration with `SCMI_PROTOCOL_IMX_LMM`.

Risks and edge cases: `scmi_imx_lmm_reset_vector_set()` does not validate `lmid` even though other operations do; invalid LM IDs may be passed to firmware. The `flags` argument to reset-vector set is ignored and transmitted as zero. Attribute xfer uses rx size 0 while reading a response structure, similar to the CPU file and worth validating. Count validation protects only against above-max values, not zero behavior.

Test signals: Test LM count limits, boot vs power-on, graceful and non-graceful shutdown, invalid LM IDs for every op including reset-vector set, attribute response sizing, and reset vector low/high encoding.
