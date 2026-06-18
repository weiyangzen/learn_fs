# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/dvfsrc.h

Purpose: This MediaTek header exposes the DVFS Resource Collector client API for bandwidth, OPP, and voltage-level requests.

Important APIs/types/functions: `enum mtk_dvfsrc_cmd` defines request/query command IDs for bandwidth, HRT bandwidth, peak bandwidth, OPP, Vcore level, VSCP level, and max marker. When `CONFIG_MTK_DVFSRC` is enabled, `mtk_dvfsrc_send_request` and `mtk_dvfsrc_query_info` are declared. Disabled builds return `-ENODEV`.

Control flow: Device drivers send a command plus 64-bit data to request resource changes, or query command-specific info into an integer pointer. The DVFSRC provider translates these into hardware PM/resource decisions.

State and persistence: Requests affect DVFSRC-managed performance state and may persist while the consumer remains active. The header stores no client state.

Dependencies and integration: Uses `struct device`, integer types, and `CONFIG_MTK_DVFSRC`. Integrates with MediaTek interconnect, memory bandwidth, power, and multimedia drivers.

Risks and test signals: Unsupported commands, stale device pointers, or missing provider support can degrade performance or power behavior. Test disabled-config stubs, request/query return codes, bandwidth stress, and suspend/resume resource restoration.
