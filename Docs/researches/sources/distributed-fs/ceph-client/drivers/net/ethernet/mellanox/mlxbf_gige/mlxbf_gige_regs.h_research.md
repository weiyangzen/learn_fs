# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_regs.h

## Purpose
`mlxbf_gige_regs.h` is the BlueField GigE register map for MAC control, interrupts, RX/TX ring programming, filters, counters, RX DMA, BF3 PLU SGMII speed programming, and BF2/BF3 LLU pause counters.

## Important APIs, Types, and Functions
It defines offsets and bit masks for version/status, interrupt status/enable/mask, port control, RX WQ/CQ base and size, TX WQ/CI/PI, MAC filters, filter pass/discard counters, RX DMA, TX status, register dump size, PLU TX/RX SGMII fields, IPG sizes, pause counter offsets, and LLU counter-enable bits. Version-specific macros select BF2 or BF3 pause counter offsets through `priv->hw_version`.

## Control Flow and State
The header has no runtime flow, but its constants drive every MMIO state transition in the driver: open/stop clean-port, interrupt enable/clear, RX/TX ring setup, MAC filtering/promiscuous mode, stats reads, pause stats, and BF3 link-speed updates.

## Dependencies and Integration Points
It includes bitfield helpers and is included by all BlueField GigE implementation files. It also defines `MLXBF_GIGE_MMIO_REG_SZ` for ethtool register dumps.

## Risks and Test Signals
Risks include stale offsets for BF2/BF3 revisions, macro expressions depending on a local variable named `priv`, incorrect register dump sizing, and missed masks for error/status bits. Test signals are successful open/close, interrupt clearing, RX/TX traffic, ethtool register dumps, BF3 speed change programming, pause counter reads on both hardware versions, and hardware documentation cross-checks.
