# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/sif_rtr_ctrl_4_regs.h

## Purpose

`sif_rtr_ctrl_4_regs.h` is an auto-generated Gaudi ASIC register-address header for SIF router controller instance 4, labelled in the file as `SIF_RTR_CTRL_4 (Prototype: RTR_CTRL)`. It contains no executable code, functions, structs, or field definitions. Its exported API is the set of `#define mmSIF_RTR_CTRL_4_*` macros that give absolute 32-bit MMIO offsets used by the HabanaLabs Gaudi driver when programming the system interface fabric.

The instance 4 register window starts at the `0x346...` address range. The header mirrors the same router-control prototype exposed by sibling instances 0 through 7, with this instance occupying its own address page. It is part of the low-level hardware contract between driver code and the Gaudi register map, and it should be treated as generated data rather than hand-maintained logic.

## Important APIs and Register Groups

The public surface is a macro namespace. Important exported groups are:

- `mmSIF_RTR_CTRL_4_PERM_SEL`, a permission-selection register at `0x346108`.
- `mmSIF_RTR_CTRL_4_HBM_POLY_H3_0` through `_27`, a 28-entry HBM polynomial/hash configuration table.
- `mmSIF_RTR_CTRL_4_SRAM_POLY_H3_0` through `_14`, a 15-entry SRAM polynomial/hash configuration table.
- `mmSIF_RTR_CTRL_4_SCRAM_SRAM_EN` and `mmSIF_RTR_CTRL_4_SCRAM_HBM_EN`, enable points for SRAM and HBM scramblers.
- Rate-limit registers for HBM, PCI, and SRAM traffic: `RL_*_EN`, `RL_*_SAT`, `RL_*_RST`, `RL_*_TIMEOUT`, plus `RL_SRAM_RED`.
- End-to-end credit/checking registers: `E2E_HBM_EN`, `E2E_PCI_EN`, `E2E_*_WR_SIZE`, `E2E_*_RD_SIZE`, `E2E_AW_*_CTR_*`, `E2E_AR_*_CTR_*`, and per-HBM-channel wrap/count counters.
- Non-linear address mapping controls: `NL_HBM_SEL_*`, `NON_LIN_EN`, `NL_SRAM_BANK_*`, `NL_SRAM_OFFSET_*`, `NL_HBM_OFFSET_*`, and `NL_HBM_PC_SEL_*`.
- Security and privilege range registers for both AXI write and read paths: `RANGE_SEC_BASE_*_AW_*`, `RANGE_SEC_MASK_*_AW_*`, `RANGE_PRIV_BASE_*_AW_*`, `RANGE_PRIV_MASK_*_AW_*`, and equivalent `*_AR_*` variants.
- Range-hit status registers: `RANGE_SEC_HIT_AW`, `RANGE_SEC_HIT_AR`, `RANGE_PRIV_HIT_AW`, and `RANGE_PRIV_HIT_AR`.
- RGL scheduling/latency registers: `RGL_CFG`, `RGL_SHIFT`, `RGL_EXPECTED_LAT_0..7`, `RGL_TOKEN_0..7`, `RGL_BANK_ID_0..7`, and `RGL_WDT`.

## Control Flow and State Behavior

This header has no runtime control flow. Its macros are consumed by C code that issues MMIO reads and writes through driver helpers such as `WREG32`, `RREG32`, and polling paths. State lives entirely in the hardware registers at these offsets, not in the header.

In `gaudi.c`, instance 4 participates in startup sequences that enable SIF router SRAM and HBM scrambling unless firmware security or firmware boot-status bits already own those features. The same file programs E2E size registers for instance 4 with HBM write size `176 >> 3`, HBM read size `32 >> 3`, PCI write size `19`, and PCI read size `32`, then enables HBM and PCI E2E handling. These writes are guarded by firmware-security and firmware-status checks, so the register constants are used only when the host driver is responsible for initialization.

In `gaudi_security.c`, instance 4 range registers are placed in arrays alongside DMA, SIF 0..7, and NIF 0..7 routers. Those arrays let security setup code apply the same base/mask/range-hit handling across all high-bandwidth router blocks. The header therefore supports both boot-time feature setup and security fault/isolation plumbing.

## Dependencies and Integration Points

The only direct dependency is the C preprocessor include mechanism plus the broader generated register-map naming convention. Integration depends on matching bitfield shift/mask headers, especially shared `IF_RTR_CTRL_*` field definitions used when writing enable bits. The header is compiled into the Gaudi driver through aggregate ASIC register includes and is coupled to the Gaudi hardware address map.

Instance 4 is one of a symmetrical set of SIF router controllers. The address base differentiates it from instance 5 (`0x356...`), instance 6 (`0x366...`), and instance 7 (`0x376...`). Consumers rely on that symmetry when constructing per-router arrays or when writing repetitive initialization sequences.

## Risks and Test Signals

The main risk is address drift: a single wrong macro value can redirect an MMIO write to a neighboring register or block. Because the file is generated, manual edits are high risk and should be avoided. Security range registers are especially sensitive because base/mask misaddressing can weaken or break protected memory routing; E2E and scrambler registers can affect data integrity and memory confidentiality.

Useful test signals include successful Gaudi probe/init, absence of MMIO access faults, correct scrambler/E2E initialization on systems where firmware does not pre-enable those features, and security tests that exercise protected high-bandwidth ranges and confirm expected hit reporting. Static review should compare this header against the hardware register database and sibling router headers for the expected `0x10000` stride between SIF router-control instances.
