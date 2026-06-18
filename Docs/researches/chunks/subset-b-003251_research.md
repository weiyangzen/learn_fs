# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 12229-14645

## Chunk Scope

- Work item: `subset-b-003251`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, lines 12229-14645
- Parent file role: generated AMDGPU NBIO 7.7.0 register offset map used by SOC15/NBIO register access helpers.
- Chunk shape: 2,397 preprocessor definitions. Most are paired `reg*` register-offset and `reg*_BASE_IDX` macros; this slice starts with a dangling `BIFPLR1_0` base-index macro from a prior register and ends after the first three `BIFP3_0` register offsets. Every visible `*_BASE_IDX` in the chunk is `5`.

## Purpose

This chunk supplies symbolic offsets for NBIO 7.7.0 PCIe logical-root-port and PCIe direct/link-controller register spaces. It does not implement executable behavior. Its purpose is to let AMDGPU code refer to hardware registers by generated names instead of numeric MMIO offsets, then let helpers such as `SOC15_REG_OFFSET(NBIO, instance, reg...)`, `RREG32_SOC15(...)`, `WREG32_SOC15(...)`, `RREG32_PCIE_PORT(...)`, and `WREG32_PCIE_PORT(...)` resolve and access the correct address.

The chunk is split between two major hardware views. `BIFPLR*_0` blocks model PCIe configuration-space-like logical root ports with standard PCI/PCIe capability registers, AER/DPC/error-reporting registers, link-speed capability extensions, lane equalization, link margining, CCIX/ESM, and 32 GT status. `BIFP*_0` blocks model PCIe direct link/transaction registers for individual ports, including link controller state, speed/width controls, L1 PM substate save/restore, RX/TX credits, replay/NAK state, and flow-control counters.

## Major Register Families In This Chunk

- Lines 12229-12475 finish the `BIFPLR1_0` logical-root-port configuration group from the previous chunk. The visible portion covers RP PIO header/prefix logs, ESM capability/status/control registers, data-link feature registers, 16 GT PHY/link capability and equalization registers, per-lane margining control/status for lanes 0-15, CCIX and ESM capability/control/status registers, 20 GT and 25 GT ESM lane equalization tables, CCIX transaction capability/control, and 32 GT link capability/control/status.
- Lines 12478-13027 define `nbio_pcie0_bifplr2_cfgdecp` at base address `0x11102000`. This is a full logical-root-port config decode block. It starts with PCI identity and command/status aliases, bridge-window registers, capability pointers, power-management capability registers, PCIe capability/link/slot/root registers, MSI registers, vendor-specific capability registers, virtual-channel resources, device serial number, AER status/mask/severity/logging, secondary PCIe capability registers, lane equalization tables, ACS, multicast, L1 PM substates, DPC, RP PIO error reporting/logging, ESM, data-link feature, 16 GT link/equalization, margining, CCIX/ESM, 20 GT/25 GT equalization, CCIX transaction, and 32 GT link status.
- Lines 13030-13579 define `nbio_pcie0_bifplr3_cfgdecp` at base address `0x11103000`. It repeats the same logical-root-port layout as `BIFPLR2_0`, giving a separate offset namespace for another PCIe root port.
- Lines 13582-14131 define `nbio_pcie0_bifplr4_cfgdecp` at base address `0x11104000`. It repeats the same full config-space/logical-root-port register families for a fourth port namespace.
- Lines 14134-14300 define `nbio_pcie0_bifp0_pciedir_p` at base address `0x11140000`. This direct PCIe port block contains scratch/reserved registers, port control, TX requester ID, physical lane status, error control, RX controls and expected sequence number, RX allocated credits for posted/non-posted/completion traffic, physical/transaction error injection registers, NAK counter, link controller control/training/width/speed/state registers, link-controller L1 PM substate registers, BCH ECC control, clock-gating override, save/restore registers, speed-control extensions, TX sequence/replay/latency/request-number controls, TX advertised/init credit registers, credit status, and flow-control counters for VC0 and VC1.
- Lines 14302-14468 define `nbio_pcie0_bifp1_pciedir_p` at base address `0x11141000`, repeating the `BIFP0_0` PCIe direct-port layout for port 1.
- Lines 14470-14635 define `nbio_pcie0_bifp2_pciedir_p` at base address `0x11142000`, repeating the `BIFP0_0` PCIe direct-port layout for port 2.
- Lines 14638-14645 begin `nbio_pcie0_bifp3_pciedir_p` at base address `0x11143000`, but this chunk only includes `PCIEP_RESERVED`, `PCIEP_SCRATCH`, and `PCIEP_PORT_CNTL` plus base-index macros. The rest of `BIFP3_0` continues in the next chunk.

## Important APIs, Types, And Symbols

There are no C functions, structs, enums, or storage objects in this slice. The public interface is preprocessor constants:

- Register-offset macros such as `regBIFPLR2_0_VENDOR_ID`, `regBIFPLR3_0_PCIE_UNCORR_ERR_STATUS`, `regBIFPLR4_0_PCIE_DPC_STATUS`, `regBIFPLR1_0_LINK_STATUS_32GT`, `regBIFP0_0_PCIE_LC_SPEED_CNTL`, `regBIFP1_0_PCIE_LC_LINK_WIDTH_CNTL`, and `regBIFP2_0_PCIE_TX_CREDITS_STATUS`.
- Paired base-index macros such as `regBIFPLR2_0_LINK_STATUS_16GT_BASE_IDX` and `regBIFP2_0_PCIE_LC_CNTL_BASE_IDX`, all set to `5` in this chunk. SOC15 offset machinery depends on these indices to select the generated base for the NBIO register block.
- PCIe configuration-space aliases in the `BIFPLR*_0` groups. Several names intentionally share the same DWORD offset because they represent different field views of a PCI/PCIe config register, for example command/status, device control/status, link control/status, slot control/status, and capability/status pairs.
- Per-lane table symbols for equalization and margining. Four lanes are packed per equalization DWORD in several 16 GT/20 GT/25 GT tables, so lane-specific macro names can intentionally map to the same offset.
- PCIe direct-port link-controller symbols in the `BIFP*_0` groups, especially `PCIE_LC_*`, `PCIE_RX_*`, `PCIE_TX_*`, `PCIE_FC_*`, `PCIEP_STRAP_*`, and error-injection/counter symbols.

## Control Flow

The header itself has no executable control flow. Runtime flow is data-driven:

1. NBIO or PCIe-related driver code selects a generated register symbol for the ASIC generation it is compiling against.
2. `SOC15_REG_OFFSET` combines the symbol's offset, the `*_BASE_IDX` metadata, the NBIO IP block, and the instance number into an MMIO register address.
3. AMDGPU register helpers read, write, or poll that address directly or through PCIe index/data windows.
4. For bit-level operations, code combines these offsets with matching shift/mask definitions from `nbio_7_7_0_sh_mask.h` and helpers such as `REG_SET_FIELD` or `REG_GET_FIELD`.

`amdgpu/nbio_v7_7.c` is the visible NBIO 7.7.0 integration point. It includes this offset header and the matching mask header, then uses SOC15 and PCIe-port helpers for NBIO setup, HDP flush offsets, PCIe index/data offsets, doorbell ranges, interrupt control, register remapping, memory-controller access, and BIF clock-gating/light-sleep configuration. This exact chunk's root-port and direct-port symbols are primarily a generated hardware ABI surface for PCIe link/error/debug paths rather than ordinary procedural code.

## State And Persistence Behavior

The source file has no mutable software state and persists no data. The registers it names are hardware state:

- Logical-root-port identity, bridge-window, capability, MSI, VC, ACS, multicast, DPC, ESM, CCIX, and link-speed registers represent PCIe configuration-space state for multiple root-port namespaces.
- AER, DPC, RP PIO, ESM, lane-error, parity-mismatch, NAK, replay, and credit-status registers expose transient or sticky hardware error/status state. Some status bits may require write-one-to-clear or firmware/driver policy outside this header.
- Link controller, speed, width, training, FTS, CDR, equalization, margining, L1 PM substate, save/restore, and clock-gating override registers affect link training, power-management, and resume behavior until reprogrammed or reset.
- RX/TX credit and flow-control registers reflect or configure transaction-layer resource accounting. Incorrect writes can alter PCIe throughput or stability.
- Error-injection registers are test/debug controls and must not be confused with passive status registers.

Persistence risk is therefore not in the generated header text itself. The operational risk is stale or mismatched offsets causing a driver, debug tool, or firmware interface to read the wrong status or mutate the wrong hardware state.

## Dependencies And Integration Points

- Included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which binds NBIO 7.7.0 register offsets to the `amdgpu_nbio_funcs` operations for HDP flush, PCIe index/data access, doorbells, interrupts, memory access, clock gating, light sleep, and setup.
- Depends on the matching `nbio_7_7_0_sh_mask.h` for field layouts. Offset macros identify register addresses; mask/shift macros identify the meaning of bits within those registers.
- Depends on the AMDGPU SOC15 register-base infrastructure. The numeric offset plus `BASE_IDX == 5` only has meaning when paired with the generated NBIO base tables used by `SOC15_REG_OFFSET`.
- Integrates with generic AMDGPU register-access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.
- Related NBIO versions (`nbio_7_2_0_offset.h`, `nbio_7_9_0_offset.h`, `nbio_7_11_0_offset.h`, and nearby generated headers) contain similarly named symbols with generation-specific offsets. Code must include the header matching the active NBIO IP version rather than carrying offsets across ASIC generations.
- Power-management and diagnostics can consume the PCIe link-state concepts exposed here. Even when newer NBIO 7.7.0 code does not name every `BIFP*_0` or `BIFPLR*_0` symbol directly, register dump, debug, link-training, and validation tools rely on the generated map being faithful.

## Risks And Edge Cases

- The chunk starts and ends inside address blocks. It begins with `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2_BASE_IDX` after the matching offset from the prior chunk and ends after only the first three `BIFP3_0` registers. The merge lane must preserve cross-chunk continuity.
- All visible base indices are `5`. A generator drift that changes only an offset or only a base index can compile successfully but target a wrong MMIO address.
- The logical-root-port blocks are highly repetitive across `BIFPLR2_0`, `BIFPLR3_0`, and `BIFPLR4_0`. Off-by-one lane entries, missing lane 15 entries, wrong port prefixes, or incorrect offset progression would be hard to notice in review and could affect only one port.
- Aliased offsets are intentional for many PCIe config-space views and lane-packed registers. Automated de-duplication or "unique offset" validation would produce false positives unless it understands these shared DWORD layouts.
- Link-training and equalization registers are sensitive. Wrong offsets in `LINK_CNTL_*`, `LINK_STATUS_*`, 16 GT/20 GT/25 GT equalization, or margining controls can lead to link-speed negotiation failures, degraded width, intermittent PCIe errors, or misleading diagnostics.
- Error-reporting registers are policy-critical. Misaddressed AER, DPC, RP PIO, ESM, or parity/status registers can hide fatal errors, report the wrong source, or leave sticky errors uncleared.
- Direct-port `PCIE_RX_*`, `PCIE_TX_*`, credit, replay, NAK, and flow-control registers are transaction-layer sensitive. Incorrect writes can cause data-path stalls or severe performance regressions; incorrect reads can send debugging toward the wrong link layer.
- Error-injection registers in the `BIFP*_0` blocks are adjacent to passive status/counter registers. Test code should gate writes carefully and avoid exposing these symbols through broad "poke all registers" flows.

## Test And Validation Signals

- Build coverage: compile AMDGPU with NBIO 7.7.0 support and verify `nbio_v7_7.c` resolves this header and the matching mask header without symbol drift.
- Generated-header consistency: check that every `reg*` macro in this span has the expected paired `reg*_BASE_IDX`, that visible base indices are `5`, and that known alias groups are intentional.
- Cross-generation comparison: mechanically compare repeated `BIFPLR*_0` and `BIFP*_0` families against AMD's source register database and nearby NBIO headers to catch copied offsets from the wrong generation.
- Runtime probe on matching hardware: successful driver initialization, HDP flush setup, doorbell setup, interrupt delivery, memory-controller access enablement, and BIF clock-gating/light-sleep toggles indicate the surrounding NBIO map is coherent.
- PCIe link validation: exercise link speed/width negotiation, retraining, suspend/resume, L1 PM substates, 16 GT/32 GT status reads, equalization status, and margining diagnostics on every exposed port.
- Error-path validation: use controlled PCIe AER/DPC/RP PIO/ESM and parity/error-injection tests where supported, then verify status, mask, severity, source-id, header-log, prefix-log, NAK, replay, and counter registers report sane values and clear as expected.
- Diagnostic validation: register dumps should show coherent per-port namespaces for `BIFPLR1_0` through `BIFPLR4_0` and `BIFP0_0` through `BIFP3_0`; port 2 should not mirror port 1 unexpectedly, and packed lane registers should decode lanes consistently.

## Notes For Merge/Reconciliation

- This is a chunk-level report only for `subset-b-003251`; no final per-file report was produced.
- The chunk begins inside the previous `BIFPLR1_0` block and should be merged with the prior chunk for the complete `BIFPLR1_0` story.
- The chunk ends at the start of `BIFP3_0`; the next chunk should continue the direct PCIe port 3 register family.
- Keep this report under `Docs/researches/chunks/` and let the merge/reconciliation lane create the source-tree-aligned final document after all chunks for `nbio_7_7_0_offset.h` are available.
