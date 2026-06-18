# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/hwif.h

Purpose: Declares the callback interfaces and wrapper macros that isolate the common stmmac driver from hardware-family-specific implementations.

Important APIs and types: Defines `stmmac_desc_ops`, `stmmac_dma_ops`, `stmmac_ops`, `stmmac_hwtimestamp`, `stmmac_mode_ops`, `stmmac_tc_ops`, `stmmac_mmc_ops`, `stmmac_est_ops`, `stmmac_vlan_ops`, and `stmmac_regs_off`. It also declares exported operation tables for descriptor, PTP, ring/chain, MAC, DMA, TC, MMC, and EST implementations plus `stmmac_reset()` and `stmmac_hwif_init()`.

Control flow and state: The `stmmac_do_callback` and `stmmac_do_void_callback` macros centralize null-checking and return `-EINVAL` when a callback is absent. All runtime hardware operations are dispatched through these wrappers from `priv->hw`, so the selected vtables become persistent driver state after probe.

Dependencies and integration: Pulls in netdevice, Linux stmmac platform definitions, packet classifier types, and many forward declarations to avoid large include coupling. It is included by implementation files and common driver code.

Risks and test signals: Macro signatures hide type checking and can silently return `-EINVAL` for missing callbacks. Build coverage should exercise all callback users, and runtime tests should verify optional operations degrade correctly: absent TC, absent EST, absent VLAN, absent PTP, and missing safety/FPE hooks.
