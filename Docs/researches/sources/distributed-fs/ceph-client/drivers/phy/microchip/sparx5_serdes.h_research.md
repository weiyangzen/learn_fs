# sources/distributed-fs/ceph-client/drivers/phy/microchip/sparx5_serdes.h

Purpose: Declares shared types, constants, SoC descriptor structures, and register access helpers for the Sparx5/LAN969x SerDes driver.

Important APIs, types, and flow: Defines `SPX5_SERDES_MAX`, SerDes type enum (`6G`, `10G`, `25G`), internal mode enum (`NONE`, `2G5`, `QSGMII`, `100FX`, `1000BASEX`, `SFI`), CMU selection enum, target enum (`SPARX5`, `LAN969X`), `struct sparx5_serdes_macro`, descriptor constants/ops/match data, and private driver state. Inline helpers `sdx5_addr()`, `sdx5_inst_baseaddr()`, `sdx5_rmw()`, `sdx5_inst_rmw()`, `sdx5_rmw_addr()`, `sdx5_inst_get()`, and `sdx5_inst_addr()` convert generated register macro tuples into MMIO addresses and read-modify-write operations, with `WARN_ON()` bounds checks for target/group/register instances.

State and dependencies: The header includes `sparx5_serdes_regs.h` and depends on its generated target IDs, `NUM_TARGETS`, target-size enums, and field macros. Runtime state is owned by the C file but shaped here: per-macro current requested link state and per-device target base arrays.

Risks and test signals: All register access goes through tuple arithmetic in these helpers, so target-size and index mistakes affect broad hardware programming. `WARN_ON()` detects some out-of-range tuple instances but does not prevent writes when base pointers are wrong. Build tests should catch descriptor/type mismatches, and hardware tests should exercise representative access paths for each target class.
