# sources/distributed-fs/ceph-client/include/linux/soc/renesas/r9a06g032-sysctrl.h

Purpose: This Renesas header exposes a system-controller helper for configuring the R9A06G032 DMA mux.

Important APIs/types/functions: It declares `r9a06g032_sysctrl_set_dmamux(u32 mask, u32 val)` when `CONFIG_CLK_R9A06G032` is enabled; otherwise the inline stub returns `-ENODEV`.

Control flow: DMA or peripheral setup code calls the helper with a mask/value pair to update DMAMUX selection in the sysctrl block.

State and persistence: The DMAMUX selection is hardware register state and persists until reprogrammed or reset.

Dependencies and integration: Integrates with Renesas R9A06G032 clock/sysctrl and DMA/peripheral drivers.

Risks and test signals: Incorrect mask/value routes DMA requests incorrectly. Test disabled configs, DMA channel operation for each muxed peripheral, and sysctrl readback.
