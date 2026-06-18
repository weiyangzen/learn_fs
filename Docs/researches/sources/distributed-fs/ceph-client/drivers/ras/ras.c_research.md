# sources/distributed-fs/ceph-client/drivers/ras/ras.c

Purpose: provides core RAS initialization, tracepoint exports, ARM and non-standard CPER event logging, AMD ATL decoder indirection, and boot parameter routing for RAS features.

Important APIs and functions: when `CONFIG_AMD_ATL` is enabled, `amd_atl_register_decoder()`, `amd_atl_unregister_decoder()`, and `amd_convert_umc_mca_addr_to_sys_addr()` manage a global function pointer for AMD UMC normalized-address translation. `log_non_standard_event()` and `log_arm_hw_error()` export trace logging helpers. `ras_init()` initializes debugfs and daemon trace support. `parse_ras_param()` routes setup arguments such as CEC disable.

Control flow: AMD ATL registers a decoder callback once loaded; callers receive `-EINVAL` if no decoder is installed. Tracepoint definitions are created by defining `CREATE_TRACE_POINTS` before including `ras_event.h`. ARM CPER logging computes processor error info, context info, vendor-specific error data length, validates section length, maps MPIDR to logical CPU, and emits `trace_arm_event()`.

State and persistence: only the AMD decoder function pointer is mutable long-lived state. Debugfs state is initialized through `debugfs.c`. No persistent records are written here.

Dependencies and integration: uses Linux RAS trace events, CPER ARM structures, uuid/guid support, optional AMD ATL, optional ACPI extlog tracepoint exports, and CEC parameter parsing when configured.

Risks: the decoder pointer is not synchronized; comments assume it should never be unset except testing/debug, but unregister sets it NULL. ARM section parsing depends on firmware-provided lengths and clamps negative vendor data length after warnings. `ras_init()` returns debugfs daemon trace setup errors, so debugfs behavior can affect subsystem init status.

Test signals: ATL absent/present conversion, register/unregister behavior, ARM CPER records with short section lengths, non-standard event trace emission, `ras=cec_disable`, tracepoint symbol availability under extlog configs, and debugfs init return handling.
