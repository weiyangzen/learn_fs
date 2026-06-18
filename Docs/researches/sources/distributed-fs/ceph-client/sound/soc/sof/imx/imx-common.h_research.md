# sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx-common.h

Purpose: common i.MX SOF declarations, chip abstraction types, descriptor/DAI helper macros, and inline chip-op dispatchers.

Important APIs/types/functions: `IMX_SOF_DEV_DESC()` builds a `sof_dev_desc` with IPC3 defaults and firmware/topology paths. `IMX_SOF_DAI_DRV_ENTRY*` macros define DAI capabilities. Types include `imx_ipc_info`, `imx_chip_ops`, `imx_memory_info`, `imx_chip_info`, and `imx_common_data`. Inline helpers call optional chip `probe`, `core_kick`, `core_shutdown`, and `core_reset`.

Control flow: header macros and inline dispatchers let platform files describe SoCs declaratively while common code invokes optional operations safely.

State and persistence: `imx_common_data` stores runtime platform state; `imx_chip_info` and `imx_memory_info` are static per-chip descriptors.

Dependencies and integration points: SOF OF device descriptors, SOF ops, Linux clocks/OF platform, and Xtensa panic interfaces.

Risks: macro-generated descriptors assume IPC3 and default path/name conventions. Platforms needing different IPC or paths must not use the simple macro blindly. `get_chip_info()` and `get_chip_pdata()` depend on correctly initialized `pdata`.

Test signals: compile-time descriptor generation for i.MX8/i.MX9, OF probe using generated descriptors, and DAI macro expansion in registered components.
