# sources/distributed-fs/ceph-client/include/soc/qcom/cmd-db.h

Purpose: declares the Qualcomm Command DB API used to look up firmware-described resource addresses, auxiliary data, resource address matching, and hardware slave IDs for RPMh-managed resources.

Important APIs/types/functions: defines `enum cmd_db_hw_type` with ARC, VRM, BCM, and all/invalid values. When `CONFIG_QCOM_COMMAND_DB` is enabled it exports `cmd_db_read_addr`, `cmd_db_read_aux_data`, `cmd_db_match_resource_addr`, `cmd_db_read_slave_id`, and `cmd_db_ready`; otherwise it provides `-ENODEV`, `ERR_PTR(-ENODEV)`, zero, or false stubs.

Control flow: callers normally wait for `cmd_db_ready()`, look up a resource ID, then use the returned address/slave data to build RPMh/TCS commands. Disabled-config flow fails fast through inline stubs.

State and persistence: command-db state is firmware/platform data parsed by `drivers/soc/qcom/cmd-db.c`; this header does not store state. Returned auxiliary data pointers are owned by the command DB implementation.

Dependencies and integration: depends on `linux/err.h`. Consumers include RPMh regulators, clocks, power domains, interconnect BCM voter code, GMU/HFI GPU code, and RPMh RSC.

Risks: resource IDs are firmware ABI strings. Missing DB readiness or bad address matching can vote the wrong resource or fail probe. Test signals include RPMh clock/regulator/interconnect probe, command DB lookup failures, and boot on configs with and without `CONFIG_QCOM_COMMAND_DB`.
