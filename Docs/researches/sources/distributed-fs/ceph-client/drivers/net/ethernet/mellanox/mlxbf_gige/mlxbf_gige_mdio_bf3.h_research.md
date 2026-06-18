# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio_bf3.h

## Purpose
`mlxbf_gige_mdio_bf3.h` defines the BlueField-3 MDIO gateway, separate read-data register, and split configuration registers used by the shared MDIO code.

## Important APIs, Types, and Functions
It provides gateway/data/config offsets, masks and shifts for start, opcode, partad, devad, write data, busy, read data, mode, full drive, MDC period, input sample, and output sample. Unlike BF2, BF3 reads data from `MLXBF3_GIGE_MDIO_DATA_READ`.

## Control Flow and State
The header has no direct runtime control flow. `mlxbf_gige_mdio.c` uses these constants to build BF3 gateway commands and to write `CFG_REG0`, `CFG_REG1`, and `CFG_REG2` during MDIO setup.

## Dependencies and Integration Points
It depends on bitfield helpers and integrates with the BF3 hardware-version branch in the MDIO driver.

## Risks and Test Signals
Risks include confusing write-data and read-data fields, using BF2 timing layout on BF3, or wrong sampling constants. Test signals are BF3 PHY discovery, MII read/write loops, link negotiation at 10/100/1000, and register dumps confirming expected MDIO config programming.
