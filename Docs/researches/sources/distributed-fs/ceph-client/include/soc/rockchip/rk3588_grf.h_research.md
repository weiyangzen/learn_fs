# sources/distributed-fs/ceph-client/include/soc/rockchip/rk3588_grf.h

Purpose: defines RK3588 PMU GRF OS register offsets and masks for DRAM type, channel widths, channel information, sysreg version, and LPDDR5 bank/CKR mode.

Important APIs/types/functions: provides `RK3588_PMUGRF_OS_REG2` through `OS_REG6`, masks for `DRAMTYPE_INFO`, `BW_CH0`, `BW_CH1`, `CH_INFO`, `DRAMTYPE_INFO_V3`, `SYSREG_VERSION`, `LP5_BANK_MODE`, and `LP5_CKR`.

Control flow: consumers read GRF OS registers and derive memory topology and LPDDR5 mode for DFI/devfreq accounting.

State and persistence: register contents describe boot-time DRAM configuration and remain persistent platform state unless firmware rewrites them.

Dependencies and integration: uses `BIT()`/`GENMASK()` via includers. It is included by Rockchip DFI event code together with common DDR type definitions.

Risks: RK3588 has more channels and LPDDR5 modes, so missing masks can skew bandwidth scaling and event interpretation. Test signals include RK3588 DFI/devfreq operation, LPDDR5 board validation, and memory bandwidth counters.
