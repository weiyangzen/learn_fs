# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001483`: lines 1-4613, `Docs/researches/chunks/subset-b-001483_research.md`
- `subset-b-001484`: lines 4614-8563, `Docs/researches/chunks/subset-b-001484_research.md`
- `subset-b-001485`: lines 8564-11496, `Docs/researches/chunks/subset-b-001485_research.md`

## Chunk Research

### subset-b-001483: lines 1-4613

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_sh_mask.h lines 1-4613

## Scope And Purpose

This chunk is the first portion of AMDGPU's generated-style BIF 5.0 register shift/mask header. It contains C preprocessor constants for extracting and composing bitfields in 32-bit MMIO, PCI configuration-space, BIF, GPUIOV, PCIe, soft-reset, lane-mux, and PHY/PLL registers. The file begins with the license and include guard, then defines paired `*_MASK` and `*__SHIFT` macros for each register field. The mapped chunk ends at line 4613 inside the PB0 LC PLL SCI status override group; later PB0/PB1 PHY and link-controller definitions are outside this work item.

There are no functions, structs, enums, or executable control paths in this chunk. Its purpose is to give AMDGPU C code symbolic names for hardware bit positions so driver code can avoid hard-coded masks when reading status registers, programming control registers, or constructing read-modify-write sequences.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself:

- Indirect MMIO access: `MM_INDEX`, `MM_INDEX_HI`, `MM_DATA`, and `BIF_MM_INDACCESS_CNTL` expose index/data apertures and indirect-access disable bits.
- Basic BIF and display/GPU host integration: `BUS_CNTL`, `CONFIG_CNTL`, `CONFIG_MEMSIZE`, `CONFIG_F0_BASE`, `CONFIG_APER_SIZE`, `BIF_DOORBELL_APER_EN`, `BIF_FB_EN`, `HDP_*_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_*`, `GARLIC_FLUSH_*`, and `GPU_GARLIC_FLUSH_*` describe host bus access, framebuffer access, doorbell aperture enablement, HDP flushes, and garlic-cache flush request/done signaling.
- Reset, scratch, interrupt, debug, and status: `BX_RESET_EN`, `BX_RESET_CNTL`, `BIF_RLC_INTR_CNTL`, `INTERRUPT_CNTL`, `INTERRUPT_CNTL2`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `HW_DEBUG`, `BIF_DEBUG_*`, `SLAVE_HANG_*`, `BIF_MST_TRANS_PENDING`, and `BIF_SLV_TRANS_PENDING` cover BIF reset enables, interrupt generation, debug muxing, hang detection, and pending transaction state.
- Credits, routing, arbitration, and peer apertures: `MASTER_CREDIT_CNTL`, `SLAVE_REQ_CREDIT_CNTL`, `BIF_SLVARB_MODE`, `BIF_BUSNUM_*`, `BIF_DEVFUNCNUM_*`, `HOST_BUSNUM`, `PEER_REG_RANGE*`, and `PEER*_FB_OFFSET_*` describe request/return credits and host/peer routing ranges.
- Power management and BACO: `BACO_CNTL`, `BACO_CNTL_MISC`, `BF_ANA_ISO_CNTL`, `MEM_TYPE_CNTL`, `BIF_CLK_CTRL`, `SMU_BIF_VDDGFX_PWR_STATUS`, `BIF_VDDGFX_*`, `BIF_SMU_INDEX`, and `BIF_SMU_DATA` provide bitfields for bus-active chip-off handling, clock switching, isolation, memory PHY mode, VDDGFX register ranges, and SMU-indexed access.
- Doorbells, ring buffer, mailbox, and virtualization: `BIF_DOORBELL_CNTL`, `BIF_DOORBELL_GBLAPER*`, `BIF_RB_*`, `MAILBOX_*`, `BIF_VIRT_RESET_REQ`, `VM_INIT_STATUS`, `BIF_GPUIOV_*`, and `BIF_MMIO_MAP_RANGE*` describe host notification paths, write-pointer writeback, VF/PF reset notification, framebuffer partition accounting, and MMIO window maps.
- Standard PCI/PCIe config-space fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `BASE_CLASS`, BAR registers, ROM BAR, capability pointers, PMI, MSI, MSI-X, PCIe capability, link/device control/status, virtual channel, device serial number, AER, BAR sizing, power budget, DPA, ACS, ATS, PRI/page request, PASID, TPH requester, multicast, LTR, ARI, and SR-IOV fields are represented as register-field mask/shift pairs.
- AMD GPUIOV vendor-specific capability fields: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` provide the masks for SR-IOV shadow state, command/control, reset notification, context, total framebuffer, per-VF framebuffer ranges, MMIO map ranges, scheduler words, and VM busy/init status.
- PCIe wrapper and local controller diagnostics: `PCIE_INDEX`, `PCIE_DATA`, `PCIE_HOLD_TRAINING_A`, `LNCNT_*`, `PCIE_EFUSE*`, `PCIE_WRAP_*`, `PCIE_RXDET_OVERRIDE`, `REG_ADAPT_*`, `PCIE_HW_DEBUG`, `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, `PCIE_DEBUG_CNTL`, `PCIE_INT_*`, `PCIE_CNTL2`, `PCIE_RX_CNTL2`, `PCIE_TX_*_ATTR_CNTL`, `PCIE_CI_CNTL`, `PCIE_BUS_CNTL`, `PCIE_LC_STATE6` through `PCIE_LC_STATE11`, `PCIE_LC_STATUS*`, `PCIE_WPR_CNTL`, last-TLP capture registers, I2C debug, `PCIE_P_*`, `PCIE_OBFF_CNTL`, `PCIE_TX_LTR_CNTL`, `PCIE_IDLE_STATUS`, PCIe performance counters, strap registers, PRBS test registers, and F0 DPA fields.
- Soft reset, clock/power, lane mux, and PB0 PHY/PLL setup: `SWRST_*`, `CPM_CONTROL`, `GSKT_CONTROL`, `LM_*`, and the initial `PB0_*` groups cover reconfiguration/reset domains, clock gating, gasket FIFO behavior, loopback/mux/lane enablement, lane power/equalization settings, PB0 global overrides, PB0 straps, DFT jitter injection, PB0 RO PLL controls, and the start of PB0 LC PLL controls.

The macro naming convention is consistent: the register name precedes `__`, then the field name, followed by either `_MASK` or `__SHIFT`. A typical user reads a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, and writes it by clearing the mask then OR-ing `(field_value << SHIFT) & MASK`.

## Control Flow And Data Flow

This header has no runtime control flow. The data flow it enables is compile-time substitution into AMDGPU register access code. In practice, callers combine these constants with register address headers, register access helpers such as MMIO and PCIe-port reads/writes, and local read-modify-write helpers. The constants define how bits move between a raw register value and driver-local state such as current PCIe link speed, BIF ring-buffer enablement, doorbell monitor configuration, BACO transition commands, SR-IOV VF enable/reset state, or AER error status.

Several groups imply hardware protocols even though no protocol code is present here:

- Flush request/done registers use one bit per GPU client, for example CP and SDMA engines. Driver code writes request bits and polls matching done bits.
- Ring-buffer and mailbox registers split state across control, base, read pointer, write pointer, and message buffer words.
- PCIe capability registers mirror PCI/PCIe configuration-space layouts and are interpreted by both generic PCI logic and AMD-specific setup paths.
- Soft reset registers separate command/status bits from enable/control bits for reconfigure, atomic reset, endpoint reset, warm reset, and per-block reset domains.
- PB0 PHY and PLL masks represent low-level analog and training state that must be programmed in a hardware-defined order by platform tables or power-management flows.

## State And Persistence Behavior

The header itself stores no state. The persistent state is in hardware registers, firmware-programmed straps/fuses, PCI config space, and GPU-visible MMIO apertures manipulated by code that includes this file.

Important state classes described by the chunk include:

- Sticky or latched hardware state: BIOS scratch registers, BIF scratch registers, PCIe error status, last transmitted/received TLP capture, hang errors, PRBS counters, debug status, and fuse/strap-derived fields.
- Mutable operational state: bus mastering, ROM visibility, VGA and framebuffer access, doorbell monitoring, ring-buffer enablement, mailbox valid/ack bits, interrupt enables, cache flush request bits, clock gating, and reset command bits.
- Virtualization state: SR-IOV enablement, VF count and BARs, GPUIOV framebuffer partitioning, per-VF framebuffer offset/size fields, MMIO map ranges, VM init/busy status, reset notification, and soft-PF FLR control.
- Power/link state: BACO enables and power-good bits, VDDGFX access/stall ranges, PCIe link capabilities/status, DPA/LTR/OBFF fields, PHY lane enablement, lane muxing, loopback, PRBS, and PLL power/frequency overrides.

Because these constants are tied to hardware state, incorrect masks are not benign. A wrong bit position can persist until reset, change BAR or VF exposure, drop interrupts, stall access during power transitions, disable a link lane, or misreport PCIe errors.

## Dependencies And Integration Points

This header is intended to be included together with BIF 5.0 register address headers, notably the sibling address definitions under `include/asic_reg/bif/`, and with AMDGPU code that performs MMIO, indexed MMIO, PCIe-port, SMU, and power-management register access.

Repository references show this header is included by Southern Islands/CIK/VI-era AMDGPU and power-management code, including `amdgpu/vi.c`, `amdgpu/gfx_v8_0.c`, `amdgpu/gmc_v8_0.c`, SDMA implementations, virtualization code, and several legacy PowerPlay/SMU managers. Concrete consumers use symbols from this namespace for tasks such as reading `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE`, programming PCIe speed-change bits, checking `BIF_RB_CNTL__RB_ENABLE`, and enabling/disabling `BIF_DOORBELL_CNTL__DOORBELL_MONITOR_EN` in BACO tables.

The generated constants also integrate with:

- Linux DRM/AMDGPU MMIO helpers and PCI config helpers.
- AMD power-management and BACO command tables that encode register mask/shift/write values.
- SR-IOV and GPUIOV code that needs PF/VF reset notification and VF resource layout fields.
- Generic PCIe concepts such as MSI/MSI-X, AER, ACS, ATS, PASID, PRI, ARI, LTR, DPA, SR-IOV, link status, and BAR sizing.
- Low-level board/ASIC bring-up data for straps, fuses, PHY lanes, PLLs, PRBS, loopback, and DFT diagnostics.

## Risks And Edge Cases

The primary risk is ABI drift between this generated header and the ASIC register specification. Since driver code often writes fields by mask and shift rather than by higher-level validation, a single incorrect constant can mutate unrelated hardware bits.

Specific high-risk areas in this chunk are:

- PCIe and SR-IOV config-space fields, where incorrect masks can expose the wrong capability, BAR size, VF count, or access-control behavior to the host.
- Doorbell and ring-buffer fields, where bit mistakes can break command submission, writeback, or interrupt generation.
- Flush request/done fields, where mismatched client bits can leave CPU/GPU-visible caches incoherent or cause polling timeouts.
- BACO, VDDGFX, clock gating, and reset fields, where writes can power off, isolate, reset, or stall hardware blocks.
- AER/error mask/severity fields, where incorrect interpretation can hide fatal link errors or report benign events as fatal.
- PHY/PLL, strap, PRBS, lane mux, and loopback registers, where values are analog/link-training sensitive and may be board or ASIC revision dependent.
- Duplicate-looking names with `_MASK_MASK` suffixes, such as mask fields whose field name itself ends in `MASK`; these are intentional but easy for humans or generators to mishandle.
- Chunk boundary risk: this research covers only lines 1-4613. The full header continues beyond PB0 LC PLL status masks, so later PB0/PB1 link-controller and PHY definitions must be covered by later chunk documents before making full-file conclusions.

## Test Signals

There are no unit tests for this header alone. Useful validation signals are indirect and hardware/integration oriented:

- Successful build coverage for AMDGPU objects that include `bif_5_0_sh_mask.h`; compiler failures catch renamed or missing macros but not wrong values.
- Register readback tests or debugfs traces that confirm fields decode as expected, especially PCIe link speed/status, BIF ring-buffer enablement, doorbell monitor state, BACO transition state, and reset completion.
- PCI enumeration and lspci-style checks for vendor/device IDs, BARs, MSI/MSI-X, PCIe capabilities, AER, ACS/ATS/PASID/PRI, ARI, and SR-IOV capability layout on matching BIF 5.0 hardware.
- GPU command submission and interrupt tests that exercise doorbells, BIF ring buffer, HDP/garlic flushes, and interrupt routing.
- Suspend/resume, BACO, clock-gating, and reset tests that stress `BACO_CNTL`, `CPM_CONTROL`, `SWRST_*`, VDDGFX, and PCIe power-management fields.
- Virtualization tests that enable VFs, trigger FLR/reset notification, validate per-VF framebuffer/MMIO maps, and verify GPUIOV mailbox/scheduler status.
- PCIe error-injection or link-training diagnostics that validate AER status/mask/severity, last-TLP logs, PRBS counters, lane error status, loopback, and PLL/PHY override behavior.

For source review, the most practical guard is comparison against the matching AMD register database or upstream generated header for BIF 5.0. Runtime tests should focus on the consumers that combine these masks with actual register addresses and hardware sequencing.

### subset-b-001484: lines 4614-8563

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_sh_mask.h lines 4614-8563

## Purpose

This chunk is part of the generated AMD BIF 5.0 register bitfield mask header. It does not implement executable logic; it defines C preprocessor constants that describe the bit masks and shift positions for BIF/PCIe PHY registers used by AMDGPU and power-management code on VI-era ASICs.

The assigned range covers the end of the PB0 PHY register field definitions and the beginning/middle of the PB1 PHY definitions. Most of the fields are for PCIe physical-layer control: PLL power/frequency overrides, RX adaptation and equalization tuning, per-lane RX/TX status override fields, TX coefficient/preset acceptance tables, lane grouping/skew control, debug/DFT controls, strap-derived defaults, and per-lane power/data overrides.

The header is paired with the matching register-offset header, `bif_5_0_d.h`, and with helper macros such as `REG_GET_FIELD()` and `REG_SET_FIELD()`. A driver source file includes both the offset and mask headers, reads or writes a 32-bit MMIO/indirect register, and uses these constants to isolate or set a named bitfield without hardcoding numeric bit positions at the call site.

## Important APIs, Types, And Constants

There are no functions, structs, or runtime APIs in this range. The important interface is the naming convention and the generated constants:

- `<REGISTER>__<FIELD>_MASK`: a 32-bit mask for a field inside a hardware register.
- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used to shift field values into or out of the masked position.
- `PB0_*` and `PB1_*`: two parallel PHY/BIF register namespaces. PB0 definitions begin before this chunk and finish in this chunk; PB1 starts in this chunk and continues after it.
- `PB*_RX_GLB_CTRL_REG0` through `PB*_RX_GLB_CTRL_REG8`: RX global configuration fields for Gen1/Gen2/Gen3 adaptation, CDR frequency/phase gains, DFE/FOM/LEQ/OC timing, loop gains, DLL lock/reset behavior, L0/L0s/L1 transition behavior, and frontend/auxiliary power lookup behavior.
- `PB*_RX_GLB_SCI_STAT_OVRD_REG0` and `PB*_RX_GLB_OVRD_REG0/1`: RX SCI status update masks and explicit override value/enable pairs for adaptation hold/reset/tracking, clocks, PLL selection, DLL/front-end/idledet/aux power, and FOM behavior.
- `PB*_RX_LANE[0-15]_CTRL_REG0` and `PB*_RX_LANE[0-15]_SCI_STAT_OVRD_REG0`: per-lane RX backup/debug/test/termination fields and lane status fields such as `RXPWR`, `ELECIDLEDETEN`, `REQUESTTRK`, `ENABLEFOM`, `REQUESTFOM`, `RESPONSEMODE`, and `RXEYEFOM`.
- `PB*_TX_GLB_CTRL_REG0`, `PB*_TX_GLB_LANE_SKEW_CTRL`, `PB*_TX_GLB_SCI_STAT_OVRD_REG0`, `PB*_TX_GLB_COEFF_ACCEPT_TABLE_REG[0-3]`, and `PB*_TX_GLB_OVRD_REG[0-4]`: TX global timing, lane grouping, SCI status override, Gen1/Gen2/Gen3 driver tap override, coefficient acceptance, and clock/reset/data/power override fields.
- `PB*_TX_LANE[0-15]_CTRL_REG0`, `PB*_TX_LANE[0-15]_OVRD_REG0`, and `PB*_TX_LANE[0-15]_SCI_STAT_OVRD_REG0`: per-lane TX display-clock, data inversion, swing boost, PRBS, data-clock/driver/frontend power overrides, and TX status fields such as `TXPWR`, `TXMARG`, `DEEMPH`, `COEFFICIENTID`, and `COEFFICIENT`.
- `PB1_GLB_CTRL_REG[0-5]`, `PB1_GLB_SCI_STAT_OVRD_REG[0-4]`, and `PB1_GLB_OVRD_REG[0-2]`: PB1-level debug, bypass, bandgap/reference, DLL, power-good, termination, link-speed/frequency, and SCI update override fields.
- `PB1_STRAP_*`: strap/default fields for global, TX, RX, PLL, and pin behavior. These encode reset-time hardware configuration inputs such as adaptation modes, equalization defaults, PLL controls, terminations, startup timers, and debug defaults.
- `PB1_DFT_*` and `PB1_HW_DEBUG`: design-for-test jitter injection, PHY debug enable/mode, DFT status, lane enables, and a 32-bit hardware debug bitmap.
- `PB1_PLL_RO*` and `PB1_PLL_LC*`: ring-oscillator and LC PLL control/override/status fields, including clock enables, power lookup entries, reset/debug controls, refdiv/fbdiv/core clock/divider overrides, PLL power, and PLL frequency status.

## Control Flow

This header has no control flow. It contributes compile-time constants that are consumed by C expressions in other AMDGPU and powerplay source files. The practical read/modify/write flow is:

1. Include `bif_5_0_sh_mask.h` and the matching register-address definitions.
2. Read a register with an AMDGPU MMIO helper, or prepare a literal value for a write.
3. Use a mask/shift pair, usually through helper macros, to extract or update one field.
4. Write the resulting 32-bit register value back through an MMIO or indirect-register helper.

The range itself is ordered by register block rather than by runtime use. PB0 RX global fields are followed by PB0 RX lanes, PB0 TX global fields, PB0 TX lanes, then PB1 global/strap/DFT/PLL/RX/TX definitions. Repeated lane records are intentionally expanded for each lane number rather than represented by arrays or functions.

The requested range ends at line 8563 in the middle of `PB1_TX_LANE14_OVRD_REG0`: it includes `TX_DCLK_EN_OVRD_VAL_14`, `TX_DCLK_EN_OVRD_EN_14`, and the mask for `TX_DRV_DATA_EN_OVRD_VAL_14`, while the corresponding shift and later lane-14 override/status fields continue after this chunk. That is a chunk boundary artifact, not a semantic stop in the header.

## State And Persistence Behavior

The file stores no software state and performs no persistence. The constants describe hardware register layout. State changes happen only in consumers that use these masks to write device registers.

The hardware state represented by these fields is persistent at device-register granularity until reset, power transition, firmware action, or another driver write changes it. The affected domains include PCIe PHY lane power state, equalization/adaptation parameters, TX coefficients, PLL clocks, debug/test controls, strap-derived defaults, and SCI/status override behavior.

Because these macros are compile-time definitions, a wrong mask or shift becomes baked into every consumer at build time. There is no runtime validation that a mask matches the underlying ASIC register layout.

## Dependencies

This chunk depends on AMD's generated register naming scheme and on the corresponding address header for BIF 5.0. The `_MASK` and `__SHIFT` constants are meaningful only when used with the matching register offset, such as `ixPB1_TX_GLB_COEFF_ACCEPT_TABLE_REG0` from `bif_5_0_d.h`.

Repository consumers include AMDGPU and power-management files that include `bif/bif_5_0_sh_mask.h`, such as `amdgpu/vi.c`, `amdgpu/mxgpu_vi.c`, `amdgpu/gmc_v8_0.c`, `amdgpu/gfx_v8_0.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/sdma_v3_0.c`, and several `pm/powerplay` SMU/BACO managers. Those consumers rely on AMDGPU register access helpers (`RREG32*`, `WREG32*`) and field helpers (`REG_GET_FIELD`, `REG_SET_FIELD`, plus powerplay `CGS_*` variants) to use the generated bit definitions safely.

The definitions also depend on hardware documentation for the BIF 5.0 PHY. Many names expose implementation-specific concepts such as CBI updates, SCI status overrides, RX APU/debug paths, RX FOM measurement, Gen1/2/3 tuning, LC and RO PLLs, and lane grouping. These are not self-describing enough to change by intuition; updates must come from the authoritative ASIC register generator or hardware spec.

## Integration Points

The direct integration point is compile-time inclusion by AMDGPU and powerplay code for VI-generation ASIC setup, suspend/resume, BACO, GPU reset, SDMA/GFX/GMC initialization, and SMU interactions. This header provides field-level constants; source files provide the sequencing and policy.

Key hardware integration surfaces represented by this chunk are:

- PCIe PHY RX adaptation and equalization, including CDR gains, DFE/FOM/LEQ timing, eye/FOM reporting, and lane electrical-idle/tracking status.
- PCIe PHY TX behavior, including driver taps, coefficient acceptance, de-emphasis, margining, PRBS/debug enable, data inversion, swing boost, lane grouping, and per-lane power/data overrides.
- PLL and clock management for LC and RO PLLs, including power, clock enable, reference/frequency/divider overrides, and PLL status override fields.
- Strap/default configuration used to reflect reset-time hardware options into driver-visible register fields.
- Debug and DFT paths for PHY validation, jitter injection, PRBS, analog debug selection, bypass paths, and test status.

The final merged research document should connect this chunk to adjacent ranges. The preceding chunk contains earlier PB0 global, strap, DFT, and PLL definitions; this chunk starts after PB0 PLL LC1 status definitions have already begun. The following chunk completes PB1 TX lane 14, lane 15, and later BIF/PCIe field definitions.

## Risks And Edge Cases

- Incorrect masks or shifts can cause silent hardware misprogramming. A field write can accidentally alter neighboring bits, fail to set the intended field, or read a bogus status value.
- PB0 and PB1 definitions are highly repetitive but not interchangeable. Copying a PB0 constant into PB1 code, or a lane-N constant into another lane without checking the register address, can target the wrong PHY block or lane.
- The repeated lane records invite mechanical drift. Each RX lane should expose the same set of control/status fields, and each TX lane should expose the same control/override/status fields, but line-boundary chunks can make a lane appear incomplete.
- The chunk begins and ends mid-header context. Specifically, it starts with the last field of `PB0_PLL_LC1_SCI_STAT_OVRD_REG0` and ends mid-`PB1_TX_LANE14_OVRD_REG0`; research and review should not infer complete register coverage solely from this slice.
- Many fields are override enable/value pairs. Setting an override value without its enable bit, or leaving an enable asserted during normal link training, can interfere with PHY-managed state machines.
- Strap fields often represent reset defaults. Treating them as ordinary mutable configuration can conflict with firmware, board straps, or ASIC-specific bring-up assumptions.
- Debug/DFT fields such as PRBS, jitter injection, analog select, BSCAN, bypass, and forced PLL/reset controls can disrupt normal PCIe link operation if enabled in production paths.
- TX coefficient and RX equalization fields affect link quality. Bad values can produce training failures, link downtraining, replay errors, or intermittent PCIe faults that appear outside the BIF driver code.
- Some fields are status override or "ignore CBI update" controls. Misuse can leave software reading stale or forced status rather than hardware-owned lane/PLL state.

## Test Signals

Useful validation signals are mostly build-time and hardware bring-up signals:

- A kernel or module build that includes AMDGPU should compile cleanly with no missing BIF 5.0 mask/shift symbols.
- Static generation checks should verify that every `_MASK` has the expected `__SHIFT`, that masks are contiguous where required, and that repeated lane records are symmetric across lanes and PB0/PB1 where the hardware layout expects symmetry.
- Register access tests or debugfs register dumps should confirm that `REG_GET_FIELD()` extracts plausible values for RX/TX lane status, PLL power/frequency status, and link-speed/frequency fields.
- PCIe link training should reach the expected width and generation on affected VI ASICs after driver initialization, suspend/resume, BACO entry/exit, and GPU reset.
- Stress testing should show no new PCIe AER/replay/equalization errors, link downtraining, or intermittent GPU hangs when code paths use RX/TX/PLL masks from this header.
- Power-management tests should validate that BACO/SMU paths can still force or observe the intended BIF/PHY fields without leaving debug, DFT, or override bits asserted.
- Hardware diagnostics that intentionally enable PRBS, jitter injection, or PHY debug modes should verify that the requested lane and PB block are affected, and that the fields can be restored to normal afterward.

### subset-b-001485: lines 8564-11496

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_sh_mask.h

Chunk: `subset-b-001485`
Covered source range: lines 8564-11496 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_sh_mask.h`

## Purpose

This chunk is the final portion of AMD's generated BIF 5.0 register field mask header. It contains C preprocessor constants for bit masks and shift counts used by low-level AMDGPU and PowerPlay code when composing, extracting, or polling fields in BIF, PIF, PCIe port, PCIe link-control, MSI-X, RFE reset/power, and impedance-calibration registers.

The range is not executable code. It defines 2,931 `#define` lines and closes the header with `#endif /* BIF_5_0_SH_MASK_H */`. It pairs with address definitions in `bif_5_0_d.h`, including indexed PIF/PCIE port registers such as `ixPB0_PIF_CTRL`, `ixPCIEP_PORT_CNTL`, and `ixPCIE_LC_SPEED_CNTL`, and MMIO registers such as `mmPCIEMSIX_VECT0_ADDR_LO` and `mmBIF_RFE_SNOOP_REG`.

The covered range includes:

- the tail of `PB1_TX_LANE14_*` and full `PB1_TX_LANE15_*` TX lane control/status macros;
- duplicated `PB0_PIF_*` and `PB1_PIF_*` scratch, debug, strap, PLL/power, RX/TX, lane override, command bus, and BIF command status fields;
- `PCIEP_*` port, debug, SR-IOV, strap, hot-plug, error-injection, and scratch fields;
- `PCIE_TX_*`, `PCIE_RX_*`, flow-control, credit, sequence, replay, requester-id, vendor-specific, and error-control fields;
- `PCIE_LC_*` link-controller state, training, width, speed, equalization, CDR, bandwidth-change, and previous-state fields;
- MSI-X table fields for vectors 0-3 and the pending-bit array;
- BIF RFE snoop, warm reset, soft reset, client/master reset trigger, power-down, timeout, MM config, and impedance calibration fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or normal exported symbols in this chunk. The API surface is the generated macro namespace:

- `<REGISTER>__<FIELD>_MASK` isolates or updates a field in a 32-bit hardware register.
- `<REGISTER>__<FIELD>__SHIFT` gives the corresponding right-shift count for extracting or positioning the field.

Important macro families in the range:

- `PB1_TX_LANE14_OVRD_REG0`, `PB1_TX_LANE14_SCI_STAT_OVRD_REG0`, `PB1_TX_LANE15_CTRL_REG0`, `PB1_TX_LANE15_OVRD_REG0`, and `PB1_TX_LANE15_SCI_STAT_OVRD_REG0`: per-lane TX clock/data/power/frontend override controls, PRBS/debug controls, and SCI status fields such as TX power, margin, de-emphasis, coefficient ID, and coefficient value.
- `PB0_PIF_*` and `PB1_PIF_*`: two physical-bus-interface instances with parallel field layouts. These cover PIF scratch/debug, strap interpretation, PLL power-down/status/votes, TX/RX power states for S2/speed-change/off/degraded/unused/init/PLL-off states, L1/unused gating, PHY status delays, electrical-idle detection, CDR extension, RX-detect override, lane-width overrides, command bus scheduling, lane disables, and per-lane override enables/values for lanes 0-7 in this chunk.
- `PB[01]_PIF_BIF_CMD_STATUS`: per-lane `TXPHYSTATUS`, `RXPHYSTATUS`, `BPHY_CORE_TX_RDY`, and `BPHY_CORE_RX_RDY` status bits for lanes 0-7.
- `PCIEP_PORT_CNTL`, `PCIE_TX_CNTL`, `PCIE_RX_CNTL`, and `PCIE_RX_CNTL3`: PCIe port behavior, transaction-layer transmit/receive controls, error-ignore policy, completion timeout policy, TPH disable, PASID-related unsupported-request handling, and packet/flush/flow-control behavior.
- `PCIE_TX_CREDITS_*`, `PCIE_RX_CREDITS_*`, `PCIE_FC_*`, and `PCIE_TX_CREDITS_STATUS`: advertised, initialized, allocated, current, and error credit fields for posted, non-posted, and completion traffic.
- `PCIE_ERR_CNTL`, `PCIEP_ERROR_INJECT_PHYSICAL`, and `PCIEP_ERROR_INJECT_TRANSACTION`: AER/error-reporting controls and deliberate physical/transaction-layer error injection hooks for validation.
- `PCIE_LC_CNTL` through `PCIE_LC_CNTL6`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_CDR_CNTL`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, and `PCIE_LC_STATE0`-`PCIE_LC_STATE5`: link-controller state machine, ASPM/L0s/L1/L23 policy, link reset, training, speed changes, width negotiation, Gen2/Gen3 support, equalization, CDR, FTS count, bandwidth-change interrupts/status, lane reversal, and state-history fields.
- `PCIEP_STRAP_LC` and `PCIEP_STRAP_MISC`: strap-derived capabilities and defaults, including TS counts, skip interval, receiver-detect bypass, compliance, lane reversal, auto speed negotiation, lane negotiation, extended format, OBFF, and LTR support.
- `PCIEP_HPGI` and `PCIEP_HPGI_PRIVATE`: hot-plug/presence-detect enable and status fields routed to SMI/SCI.
- `PCIEMSIX_VECT[0-3]_*` and `PCIEMSIX_PBA`: MSI-X vector address, message data, vector mask bit, and pending bits.
- `BIF_RFE_*`, `BIF_PWDN_*`, and `BIF_RFE_MST_*_CMDSTATUS`: RFE snoop behavior, warm/soft/impedance reset enables, client/master reset triggers, block power-down commands/status, clock gate/setup/timeout timers, and master timeout status.
- `BIF_CC_RFE_IMP_OVERRIDECNTL` and `BIF_IMPCTL_*`: PLL RX/TX impedance override straps, sample period/setup/threshold controls, RX/TX pull-down/pull-up adjustment fields, lock/readback/comparator ambiguity status, calibration-done status, and continuous calibration period.

The range starts on `PB1_TX_LANE14_OVRD_REG0__TX_DRV_DATA_EN_OVRD_VAL_14__SHIFT`; its matching `_MASK` definition is immediately before the assigned range. A local mask/shift-pair check therefore reports this one expected `shift_only` boundary artifact. The remaining mask/shift pairs inside the assigned range are locally paired.

## Control Flow

This header has no runtime control flow. The only control-like structure in this chunk is the closing include-guard `#endif`.

Runtime control flow appears in consumers that use these macros for register programming. A typical driver sequence is:

1. Read a BIF/PIF/PCIe register through `RREG32`, `RREG32_PCIE_PORT`, indexed-register helpers, or PowerPlay table operations.
2. Clear one or more fields with `~<REGISTER>__<FIELD>_MASK`.
3. Shift a desired value by `<REGISTER>__<FIELD>__SHIFT`.
4. OR the shifted value into the register word.
5. Write the result back, or poll a status field until it changes.

The link-controller and PIF fields are commonly involved in state-machine sequencing: link-speed changes set force/disable/initiate bits and then poll current data rate or initiate bits; width negotiation and training inspect link-width/current-state fields; lane power and PHY-status handling inspect PIF status bits; reset/power paths set trigger bits and then wait for status/timeout fields.

## State And Persistence Behavior

The file itself has no mutable state and no persistence. It contributes numeric constants at compile time to translation units that include it.

The affected state is hardware state in memory-mapped or indexed registers. Writes using these masks may persist until overwritten by the driver, firmware, PCIe link retraining, hot reset, FLR, BACO/power transition, suspend/resume, or full device reset.

Stateful hardware areas represented in this chunk include:

- per-lane PIF override enables and override values for lane power, electrical idle, CDR enable, gang mode, link speed, coefficient selection, and training requests;
- link-controller status/history such as current data rate, negotiated width, link-speed-change status, bandwidth-change status, illegal/timed-out state status, and previous LTSSM state entries;
- error-control and error-injection fields that can change AER/reporting behavior or deliberately inject invalid physical/transaction-layer conditions;
- MSI-X vector message address/data/mask fields and pending bits;
- RFE reset/power-down commands and status bits;
- impedance calibration adjustment, lock, readback, ambiguity, and done fields.

Scratch registers such as `PB0_PIF_SCRATCH`, `PB1_PIF_SCRATCH`, and `PCIEP_SCRATCH` are explicitly general-purpose register state. Their retention rules are hardware-specific and are not encoded in the header.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The register address companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_d.h`

Known include sites in this tree include:

- `drivers/gpu/drm/amd/amdgpu/vi.c`
- `drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c`
- `drivers/gpu/drm/amd/amdgpu/gmc_v8_0.c`
- `drivers/gpu/drm/amd/amdgpu/mxgpu_vi.c`
- `drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c`
- `drivers/gpu/drm/amd/amdgpu/sdma_v3_0.c`
- PowerPlay/SMU and BACO paths such as `fiji_baco.c`, `polaris_baco.c`, `smu7_baco.c`, `tonga_baco.c`, `smu7_common.h`, and generation-specific SMU manager files.

Concrete consumers in nearby generation code show the expected use of `PCIE_LC_SPEED_CNTL` fields. For example, `amdgpu/cik.c`, `amdgpu/si.c`, and `pm/legacy-dpm/si_dpm.c` read `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE_MASK` and shift by `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE__SHIFT`; `cik.c` and `si.c` also program `LC_FORCE_EN_SW_SPEED_CHANGE`, `LC_FORCE_DIS_HW_SPEED_CHANGE`, `LC_FORCE_DIS_SW_SPEED_CHANGE`, and `LC_INITIATE_LINK_SPEED_CHANGE`. `bif_5_0_sh_mask.h` supplies the same-named BIF 5.0 layout for VI-era paths.

The macros integrate with AMDGPU register accessor conventions, PCIe-port indexed access, PowerPlay BACO command tables, reset/power-management code, SR-IOV virtualization support, interrupt/MSI-X setup, and hardware validation/debug tooling.

## Risks And Edge Cases

The major risk is silent hardware misprogramming. The compiler cannot prove that a mask belongs to the register being accessed, that the matching shift is used, or that a value fits in the field width.

Boundary risk is present in this chunk: the assigned range begins after the mask for `PB1_TX_LANE14_OVRD_REG0__TX_DRV_DATA_EN_OVRD_VAL_14`, so this chunk alone has one apparent shift without a local mask. The full header should be reconciled across adjacent chunks before file-level conclusions.

PB0 and PB1 register families are structurally similar but target distinct PIF instances. Accidentally using `PB0_*` fields with `PB1_*` register addresses, or vice versa, can compile cleanly and affect the wrong physical interface.

Lane-indexed macros are highly repetitive. Off-by-one lane mistakes in `LANE0`-`LANE7`, command-bus lane-disable bits, TX/RX PHY status bits, or coefficient fields are difficult to catch in review and may only appear as link training failures or degraded PCIe width/speed.

Several fields are disruptive when written incorrectly: link reset, LTSSM/training control, speed-change initiation, width negotiation, ASPM/L1/L23 behavior, receiver detect overrides, TX/RX power states, PLL power-down/votes, CDR/electrical-idle controls, RFE reset triggers, block power-down commands, MSI-X vector mask/address/data, and error-injection controls. Mistakes can cause PCIe link loss, failed resume, missed interrupts, corrupted error handling, or a GPU reset requirement.

Register layouts are generation-specific. Some same-named fields have different masks/shifts in later NBIO headers or locally defined newer SMU code. Mixing BIF 5.0 constants with another ASIC generation is unsafe even when macro names look familiar.

Many fields are status, strap, or write-one/control bits with hardware-defined side effects that are not documented in this header. Callers must rely on the ASIC register spec and existing sequencing code, not only on the mask names.

## Test Signals

Useful validation signals are mostly generated-header consistency, build coverage, and hardware behavior:

- Compile all VI-era AMDGPU and PowerPlay paths that include `bif_5_0_sh_mask.h`.
- Run generated-header checks that each `_MASK` has a matching `__SHIFT`, allowing for the known chunk-boundary artifact in this isolated range.
- Check that register prefixes in this chunk map to address macros in `bif_5_0_d.h`, especially `PB[01]_PIF_*`, `PCIEP_*`, `PCIE_*`, `PCIEMSIX_*`, and `BIF_RFE_*`.
- Exercise PCIe link-speed reporting and speed changes on supported hardware, validating `PCIE_LC_SPEED_CNTL` current data rate, target override, force, status, and initiate bits.
- Exercise link width negotiation, lane reversal, ASPM/L0s/L1/L23 transitions, hot reset, FLR, suspend/resume, and BACO/low-power transitions to cover `PCIE_LC_*`, `PB[01]_PIF_*`, and RFE reset/power fields.
- Validate interrupt delivery with MSI-X enabled, including vector masking/unmasking and pending-bit behavior for vectors 0-3.
- Run SR-IOV/MxGPU smoke tests where applicable, especially VF mapping/save fields, function routing, reset behavior, and MSI-X behavior under virtualization.
- Use hardware debug or lab tests for PIF lane overrides, RX detect, electrical idle, CDR, TX coefficients, error-injection fields, and impedance calibration, because these fields are too hardware-specific for ordinary unit tests.
- Compare regenerated constants against the authoritative ASIC register database before accepting any changes to this header.
