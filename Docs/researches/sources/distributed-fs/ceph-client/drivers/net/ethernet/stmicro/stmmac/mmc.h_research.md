# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/mmc.h

Purpose: Defines MMC control bits, per-core MMC base offsets, and the persistent `stmmac_counters` structure used for hardware MAC Management Counter statistics.

Important APIs and data: `stmmac_counters` contains TX/RX frame, octet, size-bin, error, pause, VLAN, LPI, IPv4/IPv6, protocol, stream-gate, and FPE/MM counters. The header exports `dwmac_mmc_ops` and `dwxgmac_mmc_ops`.

Control flow and state: Counter fields are software accumulation state. `mmc_core.c` reads hardware counters, many of which reset on read, and adds them into this structure. The control bits select reset, freeze, preset, rollover, and reset-on-read behavior.

Dependencies and integration: Used by ethtool stats, FPE MAC Merge stats, MMC callbacks in `hwif.h`, and hardware selection in `hwif.c`. Base offsets are combined with `priv->ioaddr` to create `priv->mmcaddr`.

Risks and test signals: Field order and names are externally visible through ethtool stats. Test RMON-enabled and disabled devices, reset-on-read accumulation, XGMAC 64-bit counter saturation, FPE counter updates, and string/count alignment in ethtool.
