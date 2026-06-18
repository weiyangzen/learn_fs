# sources/distributed-fs/ceph-client/drivers/firmware/imx/misc.c

Purpose: Provides exported client-side helpers for i.MX SCU MISC and PM RPC services.

Important APIs/types/functions: `imx_sc_misc_set_control()` sets a miscellaneous control for a resource. `imx_sc_misc_get_control()` reads one. `imx_sc_pm_cpu_start()` starts or stops a CPU resource at a physical address. Message structs model set/get control and CPU start requests/responses.

Control flow: Each helper fills an `imx_sc_rpc_msg` header with version, service, function, and size, populates request fields, then calls `imx_scu_call_rpc()` with response expected. Get-control casts the response overlay and returns `val` to the caller.

State and persistence behavior: Stateless locally. Firmware control values, resource state, and CPU start state are persistent/firmware-managed effects of the RPC.

Dependencies and integration points: Depends on `linux/firmware/imx/svc/misc.h`, SCU RPC core, and consumers needing resource controls or CPU boot management.

Risks and test signals: Incorrect message size or packed layout breaks SCFW ABI. Callers must pass valid IPC handles and resource/control IDs. Test with known controls, invalid resources, CPU start/stop paths, and SCU error mapping.
