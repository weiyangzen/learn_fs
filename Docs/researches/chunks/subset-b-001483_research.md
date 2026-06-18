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
