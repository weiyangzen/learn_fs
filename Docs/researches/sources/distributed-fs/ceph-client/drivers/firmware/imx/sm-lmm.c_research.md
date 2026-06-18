# sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-lmm.c

Purpose: Provides exported wrappers for i.MX SCMI Logical Machine Management operations.

Important APIs/types/functions: Exports `scmi_imx_lmm_info()`, `scmi_imx_lmm_reset_vector_set()`, and `scmi_imx_lmm_operation()`. Probe obtains `scmi_imx_lmm_proto_ops` for `SCMI_PROTOCOL_IMX_LMM`.

Control flow: The SCMI driver binds to `imx-lmm`, prevents duplicate initialization, and stores protocol ops/handle. Callers can query LMM info, program a reset vector, or request boot, power-on, or shutdown; unsupported operation enum values return `-EINVAL`.

State and persistence behavior: Global ops/handle state. Firmware logical-machine state is changed by SCMI calls and persists according to firmware semantics.

Dependencies and integration points: Depends on SCMI protocol framework and NXP LMM protocol definitions. Exported symbols are consumed by other i.MX platform drivers managing auxiliary machines/cores.

Risks and test signals: Singleton globals and no remove reset mirror other SCMI wrappers. Test probe deferral, invalid info pointer, each operation enum, shutdown flags, and duplicate SCMI device handling.
