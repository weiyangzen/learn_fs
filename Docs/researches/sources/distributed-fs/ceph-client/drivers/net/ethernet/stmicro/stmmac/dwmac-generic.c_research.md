# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-generic.c

## Purpose
The generic DWMAC platform driver binds common Synopsys DWMAC-compatible devices that need no SoC-specific glue beyond standard STMMAC platform data.

## Important APIs, Types, And Functions
- `dwmac_generic_probe()` gets STMMAC resources, parses DT platform data when an OF node exists, or consumes legacy platform data otherwise.
- For non-OF platform data it sets default multicast filter bins to `HASH_TABLE_SIZE` and unicast entries to 1.
- The OF match table includes many generic Synopsys and SPEAr compatible strings.

## Control Flow
Probe obtains resources, chooses OF or platform-data configuration, then calls `devm_stmmac_pltfr_probe()`.

## State And Persistence
No private state beyond STMMAC platform data.

## Dependencies And Integration Points
Uses STMMAC platform helpers and the broad compatible table. The Makefile orders this object after specific platform drivers because generic compatibles could otherwise bind too broadly.

## Risks
Generic matching can hide missing SoC glue if a DT uses only a generic compatible. Non-OF platform data must provide all required fields except the small defaults this file fills.

## Test Signals
Probe generic compatible DTs, legacy platform-data use, multicast filter behavior, and module alias ordering relative to specific glue drivers.
