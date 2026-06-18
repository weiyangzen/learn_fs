# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_d.h

## Purpose

`bif_4_1_d.h` is a generated-style AMD GPU register-address header for the BIF 4.1 block. It does not implement executable logic; it provides preprocessor constants that map symbolic register names to numeric offsets or indexed-register addresses used by CIK-era AMDGPU and PowerPlay code.

The file is protected by `BIF_4_1_D_H` and contains 894 register definitions: 329 `mm*` constants for memory-mapped/configuration-space style register offsets and 565 `ix*` constants for indirect/indexed register addresses. It is paired with `bif_4_1_sh_mask.h`, which defines the corresponding field masks and shifts. Consumers normally include both headers so code can read or write a register from this file and then isolate fields using masks from the companion header.

## Important APIs, Types, and Constants

This header exports no C functions, structs, enums, or storage. Its public interface is the macro namespace:

- `mmMM_INDEX`, `mmMM_INDEX_HI`, and `mmMM_DATA` define the indirect MMIO aperture registers used by register-access helpers.
- Core BIF `mm*` registers cover bus and configuration control (`mmBUS_CNTL`, `mmCONFIG_CNTL`, `mmCONFIG_MEMSIZE`, `mmCONFIG_F0_BASE`), BIF scratch/reset/debug/interrupt control (`mmBIF_SCRATCH0`, `mmBIF_SCRATCH1`, `mmBX_RESET_EN`, `mmBX_RESET_CNTL`, `mmINTERRUPT_CNTL`), coherency flush controls (`mmHDP_*_COHERENCY_FLUSH_CNTL`, `mmGPU_HDP_FLUSH_REQ`, `mmGPU_HDP_FLUSH_DONE`), doorbell and XDMA controls (`mmBIF_DOORBELL_CNTL`, `mmBIF_XDMA_LO`, `mmBIF_XDMA_HI`), peer apertures (`mmPEER*_FB_OFFSET_*`, `mmPEER_REG_RANGE*`), BACO/power state controls (`mmBACO_CNTL`, `mmBACO_CNTL_MISC`, `mmBIF_BACO_DEBUG`), and BIF reset/front-end controls near the end of the file (`mmBIF_RFE_*`, `mmBIF_PWDN_*`, `mmBIF_CLOCKS_BITS`).
- PCI configuration and extended capability `mm*` constants include vendor/device IDs, BARs, power-management capability, PCIe capability, MSI, AER, BAR enhanced capability, DPA, ACS, ATS, PASID, TPH, multicast, and LTR capability locations.
- `ixPCIE_*` constants cover the indirect PCIe core register space, including link control/status, interrupt, bus, performance counters, straps, PRBS diagnostics, DPA power allocation, transmit/receive credit state, link training, equalization, and lane controls.
- `ixPB0_*` and `ixPB1_*` constants describe two PCIe bridge/PHY instances. They include global controls, straps, PLL controls, RX/TX per-lane controls for lanes 0 through 15, and debug/test registers.
- `ixPB0_PIF_*` and `ixPB1_PIF_*` constants describe PIF control, pairing, power-down, per-lane override, and sequence-status registers.

The numeric values are hardware ABI data. `mm*` values are typically passed to direct register access helpers such as `RREG32()`/`WREG32()` or table-driven command engines. `ix*` values are typically passed to indirect PCIe helpers such as `RREG32_PCIE()`/`WREG32_PCIE()` after the driver has selected the relevant indexed aperture.

## Control Flow

There is no local control flow. The only compile-time flow is the include guard:

1. If `BIF_4_1_D_H` is already defined, the preprocessor skips the file.
2. Otherwise it defines the guard and exposes all register address macros.

Runtime control flow happens in consumers. For example, CIK ASPM programming reads and writes `ixPCIE_LC_N_FTS_CNTL`, `ixPCIE_LC_CNTL3`, `ixPCIE_P_CNTL`, `ixPCIE_LC_CNTL`, `ixPB0_PIF_PWRDOWN_*`, `ixPB1_PIF_PWRDOWN_*`, `ixPCIE_LC_LINK_WIDTH_CNTL`, and `ixPCIE_LC_CNTL2` through PCIe indirect helpers while applying masks from `bif_4_1_sh_mask.h`. BACO command tables use direct BIF addresses such as `mmBIF_FB_EN` and `mmBACO_CNTL` together with mask/shift macros to sequence low-power transitions.

## State and Persistence Behavior

The header itself is stateless and has no persistence behavior. The state it names is hardware state:

- Scratch and BIOS scratch registers can retain firmware/driver communication state across portions of device initialization or reset handling, depending on platform behavior.
- Link-control, lane, PLL, PIF, and BACO registers persist in the GPU register file until reset, power-gating, BACO transition, firmware action, or another driver write changes them.
- Flush request/done registers represent synchronization state between GPU clients, host-visible HDP paths, and memory-coherency machinery.
- PCI configuration/capability offsets expose negotiated or programmed PCIe configuration state and must be interpreted in the context of PCI config-space access rules.

Because these macros are raw addresses, they do not enforce ordering, locking, posting-read flushes, timeout handling, or reset-domain safety. Those guarantees must come from the caller and the AMDGPU register-access layer.

## Dependencies

This file has no C include dependencies beyond the preprocessor. Its practical dependencies are naming and hardware-contract dependencies:

- `bif_4_1_sh_mask.h` provides bit masks and shifts for fields in the registers named here.
- AMDGPU register access helpers (`RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SMC`, `WREG32_SMC`, and table-driven BACO helpers) consume these constants.
- CIK/SI/CI PowerPlay code depends on these names being stable for the BIF 4.1 address map.
- Other asic register headers in the same tree provide adjacent blocks, such as GMC, DCE, OSS, SMU, GCA, and later NBIO/NBIF generations.

## Integration Points

Known direct include sites under the AMD DRM tree include `amdgpu/cik.c`, `amdgpu/cik_ih.c`, `amdgpu/cik_sdma.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/gfx_v7_0.c`, `amdgpu/amdgpu_device.c`, `amdgpu/amdgpu_ttm.c`, display/atombios paths, `pm/powerplay/hwmgr/ci_baco.c`, and `pm/powerplay/smumgr/ci_smumgr.c`.

Important integration patterns:

- PCIe link and ASPM setup uses `ixPCIE_LC_*`, `ixPCIE_P_*`, and PIF power-down constants with `RREG32_PCIE()`/`WREG32_PCIE()`.
- BACO and low-power command tables use `mmBIF_FB_EN`, `mmBACO_CNTL`, `mmBIF_BACO_DEBUG`, and related direct BIF registers in scripted read/modify/write sequences.
- Interrupt, DMA, memory-manager, and display files include the header because shared device bring-up and reset paths may need BIF addresses even when most field-level logic lives elsewhere.
- The address header is versioned by hardware block (`bif_4_1`) and coexists with `bif_3_0_d.h`, `bif_5_0_d.h`, and `bif_5_1_d.h`; selecting the wrong generation can silently point a read/write at the wrong hardware register.

## Risks and Edge Cases

- Register-address drift is high impact. A one-value mistake can corrupt unrelated hardware state, break PCIe link training, disable memory/doorbell paths, or hang the GPU.
- The macro names do not encode access method strongly enough for the compiler to validate usage. Passing an `ix*` indirect address to a direct MMIO helper, or an `mm*` address to an indexed helper, can produce invalid accesses.
- Some macros share offsets because they represent different fields in the same PCI configuration DWORD, such as `mmVENDOR_ID`/`mmDEVICE_ID`, `mmCOMMAND`/`mmSTATUS`, and many capability status/control pairs. This is intentional but can confuse audits that assume one symbol per address.
- Several address spaces are represented in one header: MMIO offsets, PCI config offsets, PCIe indirect space, PB0/PB1 PHY space, and PIF space. Callers must know which aperture and base index apply.
- Hardware sequencing matters. BACO, reset, PLL, and link-training registers may require polling, delays, readback, or firmware coordination that is not visible in this header.
- Generated formatting and broad macro namespaces can hide duplicate names or cross-generation incompatibilities during manual edits. This file should be treated as hardware specification data, not hand-maintained business logic.

## Test Signals

Useful validation signals for changes involving this header are mostly integration and hardware-facing:

- Build coverage for AMDGPU CIK/SI/CI configurations should catch missing or renamed macros and companion mask mismatches.
- Static grep checks can verify that each touched address macro has a corresponding field definition in `bif_4_1_sh_mask.h` when fields are expected.
- Runtime smoke tests on matching hardware should cover driver probe, PCIe link negotiation, ASPM programming, interrupt ring bring-up, SDMA/GFX initialization, doorbell operation, suspend/resume, reset, and BACO entry/exit.
- Register read/write traces are useful around `RREG32_PCIE()`/`WREG32_PCIE()` consumers to confirm indirect addresses route through the expected aperture.
- Failure signals include PCIe link width/speed regressions, ASPM disablement, GPU reset timeouts, BACO transition timeouts, HDP/coherency flush stalls, interrupt ring inactivity, and machine-check/AER reports after register programming.
