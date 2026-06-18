# sources/distributed-fs/ceph-client/include/soc/rockchip/rockchip_sip.h

Purpose: defines Rockchip secure monitor call IDs and subcommands for suspend and DRAM frequency management.

Important APIs/types/functions: provides `ROCKCHIP_SIP_SUSPEND_MODE`, `ROCKCHIP_SLEEP_PD_CONFIG`, `ROCKCHIP_SIP_DRAM_FREQ`, and `ROCKCHIP_SIP_CONFIG_DRAM_*` subcommands for init, set/round/get rate, set at self-refresh, get bandwidth, clear IRQ, set params, and ODT power-down.

Control flow: callers pass these constants to ARM SMCCC/SIP calls handled by secure firmware. Kernel code uses them to request DRAM clock operations or suspend power-domain configuration.

State and persistence: effects are secure-firmware controlled DRAM frequency and suspend configuration. The header owns no state.

Dependencies and integration: consumed by Rockchip clock DDR code, PM-domain code, and RK3399 DMC/devfreq code.

Risks: SIP IDs are firmware ABI. Wrong command IDs can fail calls or invoke the wrong secure service. Test signals include DRAM frequency scaling, suspend/resume, secure monitor return-code handling, and bandwidth query validation.
