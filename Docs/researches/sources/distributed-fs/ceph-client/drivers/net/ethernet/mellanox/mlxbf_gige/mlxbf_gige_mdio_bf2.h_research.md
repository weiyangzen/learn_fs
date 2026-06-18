# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio_bf2.h

## Purpose
`mlxbf_gige_mdio_bf2.h` defines the BlueField-2 MDIO gateway and configuration register layout used by `mlxbf_gige_mdio.c`.

## Important APIs, Types, and Functions
It provides offsets `MLXBF2_GIGE_MDIO_GW_OFFSET` and `MLXBF2_GIGE_MDIO_CFG_OFFSET`, gateway masks/shifts for data/address, devad, partad, opcode, start bit, and busy bit, plus config masks for mode, 3.3 V, full drive, MDC period, input sample, and output sample. `MLXBF2_GIGE_MDIO_CFG_VAL` builds the static portion of the config value with `FIELD_PREP()`.

## Control Flow and State
The header has no runtime control flow. Its constants are consumed by the BF2 entry in `mlxbf_gige_mdio_gw_t[]` and by `mlxbf_gige_mdio_cfg()` when programming MDIO mode and timing.

## Dependencies and Integration Points
It depends on Linux bitfield helpers and integrates only with the BlueField GigE MDIO implementation.

## Risks and Test Signals
Risks are incorrect bit positions or default config values, which would break PHY access on BF2. Test signals are BF2 MDIO read/write success, PHY discovery, scope/register verification of MDC timing, and build coverage for the included header.
