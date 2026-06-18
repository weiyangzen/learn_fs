# sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-cpu.c

Purpose: Provides exported convenience wrappers for the i.MX SCMI CPU protocol.

Important APIs/types/functions: Exports `scmi_imx_cpu_reset_vector_set()`, `scmi_imx_cpu_start()`, and `scmi_imx_cpu_started()`. Probe obtains `scmi_imx_cpu_proto_ops` and a protocol handle for `SCMI_PROTOCOL_IMX_CPU`.

Control flow: The SCMI driver binds to the protocol device named `imx-cpu`. Probe rejects duplicate initialization, retrieves protocol ops via `devm_protocol_get()`, and stores globals. Exported functions return `-EPROBE_DEFER` until probe succeeds, validate pointer arguments where needed, and call protocol ops.

State and persistence behavior: Global `imx_cpu_ops` and `ph` are process-wide module state. Firmware CPU reset vector/start state is changed through SCMI.

Dependencies and integration points: Depends on SCMI core, NXP SCMI protocol definitions, and `linux/firmware/imx/sm.h` consumers.

Risks and test signals: Global singleton design assumes one i.MX CPU SCMI provider. There is no explicit remove cleanup, relying on module/SCMI lifecycle. Test probe deferral, duplicate provider rejection, invalid `started` pointer, CPU start/stop, and reset vector programming.
