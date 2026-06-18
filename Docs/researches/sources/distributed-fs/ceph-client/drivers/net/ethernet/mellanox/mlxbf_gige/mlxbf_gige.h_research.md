# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige.h

## Purpose
`mlxbf_gige.h` is the internal contract for the BlueField GigE management-port driver. It defines queue sizes, DMA alignment constants, MAC filter indexes, interrupt indexes, register parameter descriptors, MDIO gateway abstraction, link configuration callbacks, private device state, WQE/CQE bit layouts, ACPI resource indexes, and cross-file prototypes.

## Important APIs, Types, and Functions
Key structures are `struct mlxbf_gige_stats`, `struct mlxbf_gige_reg_param`, `struct mlxbf_gige_mdio_gw`, `struct mlxbf_gige_link_cfg`, and `struct mlxbf_gige`. The private state holds MMIO bases, DMA rings, SKB arrays, indexes, IRQ numbers, PHY/MDIO objects, NAPI, stats, hardware version, MDIO gateway layout, and link speed cache. Prototypes connect main, RX, TX, IRQ, MDIO, and ethtool source files.

## Control Flow and State
The header has no direct runtime flow, but it defines the state machines used elsewhere. RX and TX rings use fixed maximum SKB arrays, coherent descriptor memory, producer/consumer indexes, and hardware CQE polarity. The driver assumes 2 KB packet buffers and a 4 KB DMA-page limitation, expressed through `MLXBF_GIGE_DEFAULT_BUF_SZ` and DMA page constants.

## Dependencies and Integration Points
It includes Linux netdevice, IRQ, PHY, and non-atomic 64-bit I/O headers. It integrates with the register map in `mlxbf_gige_regs.h`, version-specific MDIO headers, and all driver translation units.

## Risks and Test Signals
Risks include mismatched queue limits versus hardware programming, stale bit masks for WQE/CQE layouts, fixed-size SKB arrays not matching runtime queue sizes, and accidental changes to private state shared across files. Test signals are full driver build, ring open/close cycles, RX/TX wraparound, ethtool stats correctness, MDIO read/write on BF2 and BF3, and sparse/build warnings for prototype drift.
