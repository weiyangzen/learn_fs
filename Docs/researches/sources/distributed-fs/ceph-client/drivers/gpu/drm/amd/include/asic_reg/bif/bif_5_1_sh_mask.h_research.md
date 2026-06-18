# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001489`: lines 1-4658, `Docs/researches/chunks/subset-b-001489_research.md`
- `subset-b-001490`: lines 4659-8787, `Docs/researches/chunks/subset-b-001490_research.md`
- `subset-b-001491`: lines 8788-12892, `Docs/researches/chunks/subset-b-001491_research.md`
- `subset-b-001492`: lines 12893-16994, `Docs/researches/chunks/subset-b-001492_research.md`
- `subset-b-001493`: lines 16995-21114, `Docs/researches/chunks/subset-b-001493_research.md`
- `subset-b-001494`: lines 21115-25046, `Docs/researches/chunks/subset-b-001494_research.md`
- `subset-b-001495`: lines 25047-28986, `Docs/researches/chunks/subset-b-001495_research.md`
- `subset-b-001496`: lines 28987-32973, `Docs/researches/chunks/subset-b-001496_research.md`
- `subset-b-001497`: lines 32974-33080, `Docs/researches/chunks/subset-b-001497_research.md`

## Chunk Research

### subset-b-001489: lines 1-4658

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 1-4658

## Scope

This chunk is the opening part of the generated AMD BIF 5.1 register shift/mask header. It begins with the `BIF_5_1_SH_MASK_H` include guard and defines preprocessor constants for register bit fields through line 4658. The covered range has no C functions or structs; it is a hardware-description contract consumed by AMDGPU/PowerPlay code together with the companion address header `bif_5_1_d.h`.

The chunk covers roughly 669 register field families. Each field is represented as a pair of macros:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

The covered families include direct MMIO/config-space register fields, `_IND` variants for indirect access paths, PCIe configuration capability fields, BIF reset/power/doorbell/coherency controls, PCIe link training and error-reporting controls, and early BIF reset fields. The requested slice stops at `BIF_RESET_EN__PIF_STRAP_ALLVALID__SHIFT`; later fields in the same `BIF_RESET_EN` family continue after this chunk.

## Purpose

The header gives driver code symbolic names for BIF 5.1 bit positions and masks. BIF is the bus interface block that connects the GPU to PCIe and to internal clients such as SRBM, HDP, VGA, ROM, audio, XDMA, SDMA, CP, SMU, and video engines. These definitions keep register programming readable and reduce hard-coded hex constants in code that configures bus access, PCIe link behavior, interrupt routing, power gating, BAR layout, doorbells, coherency flushes, peer apertures, BACO power transitions, and Advanced Error Reporting.

This content is source-tree local to a Ceph client snapshot, but it is not Ceph filesystem logic. It is Linux DRM AMDGPU hardware register metadata for older Sea Islands / CIK-era ASIC support. For example, `iceland_ih.c` includes this header directly, and CIK-era power management code uses fields such as `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE`, `LC_FORCE_EN_SW_SPEED_CHANGE`, and `LC_INITIATE_LINK_SPEED_CHANGE` when reading or changing PCIe link speed.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The exported interface is the macro set itself, usually paired with register address macros from `bif_5_1_d.h` and access helpers such as `RREG32`, `WREG32`, `RREG32_PCIE_PORT`, and read/modify/write helpers.

Important macro groups in this chunk include:

- Indexed MMIO access: `MM_INDEX`, `MM_INDEX_HI`, `MM_DATA`, and `BIF_MM_INDACCESS_CNTL` define the indirect register aperture fields used to select and transfer MMIO register values.
- Core BIF setup: `BUS_CNTL`, `CONFIG_CNTL`, `CONFIG_MEMSIZE`, `CONFIG_F0_BASE`, `CONFIG_APER_SIZE`, `CONFIG_REG_APER_SIZE`, `BIF_FB_EN`, and BIF scratch registers describe VGA enablement, ROM access, BAR/aperture sizing, frame-buffer read/write enablement, traffic-class routing, and firmware/driver scratch state.
- Credits, arbitration, interrupts, and debug: `MASTER_CREDIT_CNTL`, `SLAVE_REQ_CREDIT_CNTL`, `BIF_SLVARB_MODE`, `INTERRUPT_CNTL`, `INTERRUPT_CNTL2`, `BIF_DEBUG_CNTL`, `BIF_DEBUG_MUX`, `BIF_DEBUG_OUT`, and `HW_DEBUG` expose backpressure, request credits, interrupt generation, dummy reads, non-snoop controls, and debug muxing.
- Pad, SMBus, and CLKREQ controls: `CLKREQB_PAD_CNTL`, `SMBDAT_PAD_CNTL`, and `SMBCLK_PAD_CNTL` define electrical/pad control fields such as mode, select, slew, wake, Schmitt enable, and control-enable bits.
- Apertures and peer routing: `BIF_XDMA_LO/HI`, `PEER_REG_RANGE0/1`, `PEER0..3_FB_OFFSET_HI/LO`, `BIF_BUSNUM_*`, and `BIF_DEVFUNCNUM_*` configure XDMA windows, peer frame-buffer mappings, and bus/device/function matching.
- Doorbells and ring buffer: `BIF_DOORBELL_CNTL`, `BIF_DOORBELL_GBLAPER1/2_*`, `BIF_RB_CNTL`, `BIF_RB_BASE`, `BIF_RB_RPTR`, `BIF_RB_WPTR`, and writeback address registers define host doorbell handling and BIF ring-buffer state.
- Coherency flush controls: `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GARLIC_FLUSH_CNTL`, `GARLIC_FLUSH_ADDR_START_0..7`, `GARLIC_FLUSH_ADDR_END_0..7`, `GPU_HDP_FLUSH_REQ/DONE`, `GPU_GARLIC_FLUSH_REQ/DONE`, and `GARLIC_COHE_*` fields define flush request/done bits and remapped coherent register addresses for CP, SDMA, UVD, VCE, display, SAM, host doorbells, and related clients.
- Power and reset: `BACO_CNTL`, `BACO_CNTL_MISC`, `BF_ANA_ISO_CNTL`, `MEM_TYPE_CNTL`, `SMU_BIF_VDDGFX_PWR_STATUS`, `BIF_VDDGFX_*`, `BIF_RFE_*`, `BIF_PWDN_*`, `NEW_REFCLKB_TIMER*`, `BIF_CLK_PDWN_DELAY_TIMER`, and the start of `BIF_RESET_EN` describe BACO entry/exit, power-good signals, VDDGFX access stalling, warm/soft reset propagation, clock gating timers, and reset source enables.
- PCI and PCIe standard capability space: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class/revision fields, BARs, ROM base, interrupt line/pin, adapter ID, PM capability, PCIe capability, device/link control and status, MSI, vendor-specific capability, virtual channel, device serial number, AER, BAR enhanced capability, power budget, DPA, secondary PCIe capability, ACS, ATS, page request, and PASID-related fields.
- PCIe controller internals: `PCIE_INDEX/DATA`, `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, `PCIE_DEBUG_CNTL`, `PCIE_INT_CNTL/STATUS`, `PCIE_CNTL2`, `PCIE_RX_CNTL*`, `PCIE_TX_*`, `PCIE_CI_CNTL`, `PCIE_BUS_CNTL`, `PCIE_LC_*`, `PCIE_P_*`, `PCIE_OBFF_CNTL`, `PCIE_TX_LTR_CNTL`, `PCIE_PERF_*`, `PCIE_STRAP_*`, `PCIE_PRBS_*`, and `PCIEP_*` expose controller-private link, PHY, protocol, performance, strap, PRBS, flow-control, equalization, and error-injection state.
- `_IND` aliases: many early BIF register families are repeated with `_IND` suffixes. These retain the same field layout while targeting the indirect register namespace used by indirect access macros.

## Control Flow

The header itself has no runtime control flow. Its constants become part of runtime control paths when included by C files that build values to write to BIF/PCIe registers or decode values read from those registers.

Typical use follows a read/modify/write pattern:

1. Read a register offset from `bif_5_1_d.h`, for example `ixPCIE_LC_SPEED_CNTL` or `mmBACO_CNTL`.
2. Clear or test fields with the corresponding `*_MASK`.
3. Position new field values with the matching `*__SHIFT`.
4. Write the register back, or poll until a status field reaches the expected value.

The link-speed path in CIK-era code is a representative consumer: it reads `PCIE_LC_SPEED_CNTL`, extracts `LC_CURRENT_DATA_RATE`, sets or clears software/hardware speed-change enable fields, writes a target speed, sets `LC_INITIATE_LINK_SPEED_CHANGE`, and polls for that initiation bit to clear. BACO hwmgr code uses `BACO_CNTL` masks in table-driven command sequences that write enable/isolation/power-off/reset fields and wait on `BACO_MODE`, power-good, or `RCU_BIF_CONFIG_DONE` status bits.

Several macros encode request/done handshakes rather than ordinary configuration. For HDP and GARLIC coherency, driver or firmware code can assert client-specific request bits such as `CP0`, `SDMA0`, or `SDMA1` and then observe matching `DONE` bits. For reset and power paths, control bits are mixed with status bits and timers, so the sequencing is external to this header but depends on these exact fields.

## State And Persistence Behavior

This header does not allocate host-side state. It names bits in hardware registers whose values live in the GPU's MMIO, PCI configuration, indirect, or PCIe-port register spaces. Persistence depends on the register family:

- PCI configuration and capability fields reflect configuration-space state negotiated with the host and can survive until reset, function-level reset, hot reset, or explicit OS/driver reconfiguration.
- Link control/status fields represent current PCIe link training, width, speed, equalization, replay, flow-control, lane, and error state. Some fields are latched status or clear-on-write status fields, while others are persistent knobs until reset or reprogramming.
- BACO, clock, reset, VDDGFX, and RFE fields influence low-power state transitions and reset propagation. They are reset-sensitive and can directly affect whether downstream register access is possible.
- Scratch registers and BIOS scratch fields can be used as firmware/driver handoff or diagnostic state.
- Flush request/done and error-status fields represent transient synchronization or fault state and must be interpreted with the hardware semantics of the specific register.

Because many fields are mirrors of hardware straps or capabilities, the macros are stable compile-time constants while their corresponding register values may be read-only, write-one-to-clear, write-protected, strap-derived, or only writable during specific power/reset windows.

## Dependencies And Integration Points

The direct dependency is `bif_5_1_d.h`, which provides the register offsets (`mm*`, `ix*`, and related address constants). This shift/mask header is also part of a larger generated register set under `drivers/gpu/drm/amd/include/asic_reg/`, and the same field names are often reused in newer NBIO/BIF headers with ASIC-specific prefixes.

Important integration points include:

- AMDGPU MMIO access helpers, which turn `mm*` offsets plus these masks/shifts into 32-bit register reads and writes.
- PCIe port access helpers such as `RREG32_PCIE_PORT`, used for `PCIE_LC_*` controller registers.
- CIK/Sea Islands power management and link-management code, which depends on `PCIE_LC_SPEED_CNTL` and `BACO_CNTL` fields for link speed reporting, link retraining, and BACO transitions.
- Interrupt handling and IH setup for BIF 5.1 devices, where the header is included to describe BIF interrupt and dummy-read controls.
- Firmware and BIOS handoff paths that use BIOS scratch, adapter ID, BAR, PM, MSI, AER, ACS, ATS, PASID, DPA, and strap fields.
- Coherency and command submission paths that require HDP/GARLIC flush request/done and doorbell aperture fields to line up with hardware.

The `_IND` macro families are especially sensitive because they let code address equivalent fields through a different register access path. A direct/indirect mismatch can cause a driver to appear correct in one path while programming the wrong register through another.

## Risks And Edge Cases

The main risk is silent register-field drift. These are raw hardware bit definitions; a wrong mask, shift, or copied field name can compile cleanly while causing the driver to modify unrelated bits. That is high impact for reset, BACO, PCIe link training, AER masking, BAR sizing, ACS/ATS/PASID capability exposure, and coherency flush paths.

Several fields use full-register masks such as `0xffffffff`, while others use tightly packed subfields. Code must not assume all fields can be updated with simple assignment; many registers require preserving reserved bits, strap-derived values, or write-one-to-clear status bits.

The chunk contains repeated direct and `_IND` definitions with nearly identical names. Manual edits or generated-header merges can easily update one side and miss the other. The same applies to repeated indexed families such as `GARLIC_FLUSH_ADDR_START_0..7`, lane equalization controls for lanes 0..15, DPA substates 0..7, PRBS error counters 0..15, PCIe state history registers, and peer aperture registers.

Security and isolation fields are easy to misuse. ACS, ATS, page request, PASID, requester ID, peer FB offsets, bus/device/function matching, and doorbell translation fields all affect address routing, peer-to-peer access, or process address-space behavior. Incorrect exposure can break IOMMU expectations or allow traffic to be routed outside intended apertures.

Power/reset fields can make the device temporarily inaccessible. `BACO_CNTL`, `BIF_RESET_EN`, `BIF_RESET_CNTL_IND`, RFE soft-reset triggers, clock power-down timers, and VDDGFX compare/stall fields need sequencing with firmware/SMU and PCIe link state. Setting a reset-enable or power-off bit without the expected status polling can wedge link training or lose config state.

The requested line range ends mid-family at `BIF_RESET_EN__PIF_STRAP_ALLVALID__SHIFT`. Any final per-file report should reconcile this with the following chunk, which continues `BIF_RESET_EN` with BIF core reset, FLR enables, and per-function reset delay fields.

## Test Signals

Useful validation signals include:

- Kernel build coverage for BIF 5.1/CIK paths, catching missing or renamed macros used by AMDGPU, PowerPlay, and IH code.
- Register readback tests on matching hardware showing PCIe link speed/width extraction from `PCIE_LC_SPEED_CNTL`, `LINK_STATUS`, and `PCIE_LC_STATUS*` matches `lspci` and kernel logs.
- Link retraining tests where software-initiated speed changes set `LC_INITIATE_LINK_SPEED_CHANGE`, clear after polling, and result in the expected negotiated speed.
- BACO entry/exit tests that observe expected transitions of `BACO_MODE`, `BACO_BCLK_OFF`, `BACO_POWER_OFF`, power-good bits, and `RCU_BIF_CONFIG_DONE`.
- Doorbell and ring-buffer tests confirming global doorbell apertures, BIF RB writeback, overflow status/clear, and self-ring/translation checks behave as expected.
- Coherency tests that request HDP/GARLIC flushes for CP/SDMA/video/display clients and observe the matching done bits before dependent memory reads.
- AER/MSI/PCIe error injection or fault logging tests that validate uncorrectable/correctable error status, masks, severity, header logs, and interrupt status fields.
- IOMMU and peer-to-peer validation around ACS, ATS, PASID, page request, peer FB offsets, and bus/device/function ID filters.
- Generated-header consistency checks ensuring every `*_MASK` has a matching `*__SHIFT`, direct and `_IND` field sets stay aligned where they are meant to mirror each other, and companion `bif_5_1_d.h` register names exist for the field families used by code.

### subset-b-001490: lines 4659-8787

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 4659-8787

## Scope And Purpose

This chunk is part of AMDGPU's generated BIF 5.1 register field mask header. It contains no executable logic; it is a compile-time hardware register layout contract for the Bus Interface and PCIe blocks used by VI-era AMD GPUs. The paired `*_MASK` and `*__SHIFT` macros tell driver code where each field lives inside a 32-bit MMIO or indirect PCIe register.

The line range starts in top-level BIF control fields, including reset enables, PCIe/PIF clock-switch timing, BACO misc selection, reset-control strap state, RFE access mode, and BIF memory power-gating control. It then defines the indexed PCIe port access registers and a large set of PCIe bridge/function field layouts for downstream functions `D2F1`, `D2F2`, and the beginning of `D2F3`.

The dominant content is the repeated `D2F1_*` and `D2F2_*` PCI configuration and PCIe capability/register spaces. These cover port indirect access, transaction-layer transmit and receive controls, credit accounting, AER/error handling, link-controller state, link training and equalization, hotplug/PME behavior, MSI/MSI-map capability fields, virtual-channel resources, ACS, multicast, and conventional PCI-to-PCI bridge configuration fields. The `D2F3_*` section begins the same pattern but this chunk ends inside `D2F3_PCIE_ERR_CNTL`, so later lines complete that function's register families.

The file path is under a Ceph source mirror, but the content here is AMDGPU Linux kernel driver register metadata. There is no Ceph filesystem behavior in this chunk.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or persistent variables in this range. The API surface is the generated macro naming scheme:

- `<REGISTER>__<FIELD>_MASK` is the raw bit mask for a register field.
- `<REGISTER>__<FIELD>__SHIFT` is the least-significant bit position used to normalize or insert that field.
- Callers use these constants directly or through AMDGPU helpers such as `REG_SET_FIELD()`, `RREG32_PCIE()`, `WREG32_PCIE()`, `RREG32()`, and `WREG32()`.

The top-level BIF families are small but important:

- `BIF_RESET_EN` exposes enable bits for BIF soft/cold-style reset and per-function FLR/reset delay controls.
- `BIF_PIF_TXCLK_SWITCH_TIMER` describes PLL acknowledgement and switch timers for PCIe/PIF transmit clock changes.
- `BIF_BACO_MSIC` contains BACO-related clock/reset mux selection fields.
- `BIF_RESET_CNTL` exposes strap capture, reset-done, link-training enable, strap-valid, and warm-reset recapture/hold behavior.
- `BIF_RFE_CNTL_MISC` exposes access-mode selectors for PIF, power-register, and PCIe-core back-end register access.
- `BIF_MEM_PG_CNTL` describes BIF memory shutdown enable and timer fields.
- `C_PCIE_P_INDEX` and `C_PCIE_P_DATA` are full-width indexed PCIe port address/data registers.

The `D2F1_PCIE_PORT_INDEX/DATA`, `D2F2_PCIE_PORT_INDEX/DATA`, and `D2F3_PCIE_PORT_INDEX/DATA` macros describe per-function indirect PCIe port access windows. The matching `*_PCIEP_RESERVED`, `*_PCIEP_SCRATCH`, `*_PCIEP_HW_DEBUG`, and `*_PCIEP_PORT_CNTL` fields expose reserved/scratch/debug bits plus port request, snoop override, hotplug message, native PME, power fault, payload/completion allocation, and sequence-number debug controls.

The transmit path families appear for each function covered by the chunk. `*_PCIE_TX_CNTL` controls non-snoop/relaxed ordering overrides, packed packet and TLP flush behavior, completion/non-posted pass policies, extra power-management request clearing, and flow-control update timeout. `*_PCIE_TX_REQUESTER_ID`, `*_PCIE_TX_REQUEST_NUM_CNTL`, `*_PCIE_TX_SEQ`, `*_PCIE_TX_REPLAY`, and `*_PCIE_TX_ACK_LATENCY_LIMIT` expose requester ID fields, outstanding non-posted request limits, transmit sequence state, replay counters/timers, and ACK latency overrides. `*_PCIE_TX_CREDITS_*` and `*_PCIE_FC_*` define posted, non-posted, and completion credit advertisement, initialization, status, and flow-control thresholds.

The receive path and error-control families include `*_PCIE_ERR_CNTL`, `*_PCIE_RX_CNTL`, `*_PCIE_RX_CNTL3`, `*_PCIE_RX_EXPECTED_SEQNUM`, `*_PCIE_RX_VENDOR_SPECIFIC`, and `*_PCIE_RX_CREDITS_ALLOCATED_*`. These define error reporting disables and injection bits, ECRC/LCRC handling, AER header log timers, slave buffer halt reset/status, completion timeout handling, TPH and PASID-related unsupported-request filters, receive sequence numbers, vendor status/data, and allocated receive credits.

The link-controller families are one of the highest-impact parts of the chunk. `*_PCIE_LC_CNTL` through `*_PCIE_LC_CNTL6`, `*_PCIE_LC_BW_CHANGE_CNTL`, `*_PCIE_LC_TRAINING_CNTL`, `*_PCIE_LC_LINK_WIDTH_CNTL`, `*_PCIE_LC_N_FTS_CNTL`, `*_PCIE_LC_SPEED_CNTL`, `*_PCIE_LC_CDR_CNTL`, `*_PCIE_LC_LANE_CNTL`, `*_PCIE_LC_FORCE_COEFF`, `*_PCIE_LC_BEST_EQ_SETTINGS`, `*_PCIE_LC_FORCE_EQ_REQ_COEFF`, and `*_PCIE_LC_STATE0` through `STATE5` describe ASPM/L0s/L1 policy, recovery and quiesce controls, link reset/retrain controls, link speed and width requests/status, N_FTS training parameters, Gen3 equalization coefficients, CDR behavior, lane control, and link-controller state machine observability.

The conventional PCI/PCIe capability space for `D2F1` and `D2F2` is also laid out in detail. It includes `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class code fields, bridge bus-number/base/limit windows, interrupt pins/lines, bridge-control fields, PM capability/status, PCIe capability and device/link/slot/root capability-control-status registers, MSI capability/message/data registers, SSID and MSI-map capability registers, vendor-specific enhanced capability headers, virtual-channel capability/resource controls, device serial number, AER enhanced capability, uncorrectable/correctable error status/mask/severity, header/TLP-prefix logs, root error command/status/source ID, secondary/link-control capability, per-lane equalization control for lanes 0-15, ACS capability/control, and multicast capability/control/address/receive/block/overlay fields.

## Control Flow

This chunk has no local control flow. Its effect on runtime behavior is indirect: code that touches BIF or PCIe registers depends on these constants for every branch condition and write value that interprets packed fields.

A typical consumer sequence is:

1. Read a register through a matching address macro from `bif_5_1_d.h`, often via `RREG32_PCIE()`/`RREG32()` or an indirect port accessor.
2. Decode a field with `value & REGISTER__FIELD_MASK`, optionally shifting by `REGISTER__FIELD__SHIFT`.
3. For updates, clear the old field with `value &= ~REGISTER__FIELD_MASK`.
4. Insert a new value at `REGISTER__FIELD__SHIFT` or use `REG_SET_FIELD()`.
5. Write the register back through `WREG32_PCIE()`/`WREG32()` while holding any required register-access lock.

The VI AMDGPU code shows the relevant access pattern. `vi_pcie_rreg()` and `vi_pcie_wreg()` serialize indirect PCIe access with `adev->reg.pcie.lock`, write `mmPCIE_INDEX`, drain/read it back, then read or write `mmPCIE_DATA`. Link-power and ASPM paths in `vi.c` use macros from this BIF namespace such as `PCIE_LC_CNTL__LC_L0S_INACTIVITY_MASK`, `PCIE_LC_CNTL__LC_L1_INACTIVITY_MASK`, `PCIE_LC_CNTL__LC_PMI_TO_L1_DIS_MASK`, `PCIE_LC_CNTL2__LC_ALLOW_PDWN_IN_L1_MASK`, `PCIE_LC_CNTL3__LC_GO_TO_RECOVERY_MASK`, and `PCIE_LC_TRAINING_CNTL__LC_DISABLE_TRAINING_BIT_ARCH_MASK` in read-modify-write sequences. The `iceland_ih.c` and `uvd_v6_0.c` files include `bif/bif_5_1_d.h` and, for interrupt handling, `bif/bif_5_1_sh_mask.h`, making this generated header part of the ASIC-specific compile-time register interface.

Because the chunk is macro-only, wrong values do not create obvious local control-flow defects. Instead they alter the behavior of distant driver flows: reset programming, power-management setup, PCIe link retraining, AER error handling, MSI programming, virtual-channel configuration, multicast/ACS exposure, and diagnostic/debug paths.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It describes hardware-backed state owned by the PCIe/BIF block. Values represented by these fields can persist until changed by a driver write, firmware, hardware self-clearing behavior, link retrain, FLR, hot reset, BACO/power-gating transition, suspend/resume, or full ASIC reset.

The state described by this chunk spans several categories:

- Reset and strap state: `BIF_RESET_EN` and `BIF_RESET_CNTL` can affect whether functions accept FLR/reset paths, when reset completion is visible, and whether straps are recaptured or considered valid.
- Link state and policy: `*_PCIE_LC_*`, `*_LINK_*`, `*_DEVICE_*`, `*_SLOT_*`, and `*_ROOT_*` fields reflect negotiated speed/width, link training, equalization, ASPM/L-state policy, slot/hotplug behavior, root error state, and PCIe capability settings.
- Data-path counters and credits: TX/RX credit fields, flow-control thresholds, advertised/init/current credit status, and allocated receive credit registers report or program the movement of posted, non-posted, and completion traffic.
- Error and diagnostic state: AER status/masks/severity, header/TLP logs, ECC/error-injection fields, debug buses, lane error status, LC state registers, and replay/sequence fields describe sticky or instantaneous error/debug state.
- Configuration identity/capability state: vendor/device/class IDs, bridge windows, MSI, PM, virtual-channel, ACS, multicast, and enhanced capability-list pointers are part of the PCI configuration view exposed for each downstream function.

The macros do not encode access semantics. A field name alone does not say whether the bit is read-only, write-one-to-clear, strap-derived, sticky until reset, self-clearing, reserved, or safe only when the link is quiesced. Consumers must rely on ASIC documentation and existing driver sequencing.

## Dependencies And Integration Points

This header depends on the generated AMDGPU register-header ecosystem. It should be used with matching address definitions from `bif_5_1_d.h`; the address header names the MMIO or indirect register, while this file names the bit layout inside the register.

Primary integration points are:

- AMDGPU VI ASIC initialization and golden-register setup, including indirect PCIe register programming through `mmPCIE_INDEX` and `mmPCIE_DATA`.
- PCIe link and ASPM management in AMDGPU, where `PCIE_LC_*` masks and shifts tune L0s/L1 inactivity, L1 powerdown, recovery, quiesce, training-disable workarounds, and link state transitions.
- Interrupt and ring-related VI code that includes the BIF 5.1 headers as part of the ASIC register namespace.
- Power and reset flows that may use BIF reset, BACO, memory power-gating, strap, and PIF clock-switch timing fields.
- PCI configuration exposure and virtualization/bridge behavior for downstream functions `D2F1` and `D2F2`, plus the start of `D2F3`.
- Error reporting and diagnostics, especially AER status/mask/severity, error-injection, header/TLP prefix logs, lane equalization controls, debug fields, and flow-control/replay state.
- Common AMDGPU register helper macros such as `REG_SET_FIELD()` and accessor functions/macros that require exact field-mask names.

The `D2F1`/`D2F2` duplication matters for multi-function PCIe layouts: generation consistency is required so the same semantic field maps correctly for each downstream function. The `D2F3` portion begins in this chunk, but its complete surface is split across the following lines/chunk.

## Risks And Edge Cases

The central risk is silent hardware misprogramming. A single incorrect mask or shift can read the wrong status bit, corrupt adjacent fields during a read-modify-write, or leave a control bit unchanged while the driver believes it acted.

High-risk fields include reset and FLR enables, link retraining/quiesce/reset controls, ASPM/L0s/L1 inactivity fields, link speed/width request fields, equalization coefficient fields, error injection bits, AER masks/severities/status bits, MSI message controls, bridge window base/limit fields, ACS controls, and virtual-channel resource controls. Many of these can affect device visibility, DMA traffic, interrupt delivery, error containment, or PCIe fabric isolation.

The repeated `D2F1` and `D2F2` definitions are vulnerable to generated-copy mistakes. A field that is correct for one function but shifted incorrectly for another would compile cleanly and only fail on hardware paths that exercise that specific function. The same applies to the per-lane equalization macros for lanes 0-15, where suffix/order mistakes can present as failures only at specific widths, lane reversals, or Gen3 equalization states.

Fields with paired enable/value semantics are easy to misuse. Override/value fields in link control, error injection, and credit/timing controls may have no effect without an enable bit, while enabling an override with a stale value can force an unintended PCIe state.

Status and sticky error fields need caller-specific clearing rules. This header describes bits for AER, root error status, correctable/uncorrectable errors, lane errors, replay counters, buffer halt status, and header/TLP logs, but it does not define whether reads clear them, writes clear them, or separate reset bits are required.

The requested range ends at line 8787 on `D2F3_PCIE_ERR_CNTL__STRAP_POISONED_ADVISORY_NONFATAL_MASK` without the matching `__SHIFT` line and without the rest of the `D2F3` function register set. The merge lane should treat this as a chunk boundary artifact, not as an absent definition in the full source file.

## Test Signals

Useful validation is mostly build-time plus hardware behavior:

- AMDGPU builds for VI-era ASICs should compile with all BIF 5.1 field names used by `vi.c`, `iceland_ih.c`, `uvd_v6_0.c`, and related code.
- Indirect PCIe register access should remain serialized and stable through `mmPCIE_INDEX`/`mmPCIE_DATA`; failures can appear as inconsistent link-state reads or writes landing on the wrong index.
- PCIe link reporting should show correct negotiated speed, width, lane reversal, and training state after boot, suspend/resume, and link retrain.
- ASPM and power-management testing should not cause hangs, surprise link down events, unexpected width/speed downgrades, or failures entering/leaving L0s/L1/L23/BACO-like states.
- FLR/reset testing should confirm reset-done and strap-valid behavior, and should not leave functions inaccessible.
- MSI, bridge window, PM capability, virtual-channel, ACS, and multicast capability fields should enumerate consistently through PCI config-space inspection.
- AER/error-injection tests should report, mask, log, and clear expected correctable/uncorrectable/root errors without spurious fatal/nonfatal classification changes.
- Diagnostic tests for replay/sequence state, flow-control credits, lane equalization, lane error status, debug registers, and LC state machines should show fields changing in the expected bit positions.

Regression symptoms from bad constants include PCIe link retraining loops, GPU disappearance after reset or resume, interrupt delivery failures, incorrect MSI programming, DMA or completion timeouts, noisy or missing AER logs, link stuck at a lower generation or width, broken hotplug/PME state, wrong ACS isolation behavior, or per-lane equalization diagnostics attributed to the wrong lane.

## Cross-Chunk Notes

Earlier lines in `bif_5_1_sh_mask.h` define preceding BIF and PCIe field families for the same ASIC register namespace. This chunk starts mid-register with the tail of `BIF_RESET_EN`, then covers complete `D2F1` and `D2F2` PCIe/config blocks and the start of `D2F3`. Later chunks complete `D2F3` and the remaining generated BIF 5.1 register-mask definitions. The final per-file report should present this file as generated AMDGPU hardware metadata rather than algorithmic driver code.

### subset-b-001491: lines 8788-12892

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 8788-12892

## Purpose

This chunk is a generated AMDGPU BIF 5.1 register field mask/shift section. It contains no executable C logic; its purpose is to publish compile-time constants for decoding and programming PCIe/BIF hardware registers on Sea Islands / GCN-era AMD GPUs that use the BIF 5.1 register map.

The line range is centered on downstream PCIe functions `D2F3`, `D2F4`, and the beginning of `D2F5`. Each register field is represented as paired macros:

- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.
- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.

Driver code combines these field constants with register address constants from the matching `bif_5_1_d.h` header and accesses the device through AMDGPU register helpers such as `RREG32_PCIE()`, `WREG32_PCIE()`, and indirect PCIE index/data helpers. The header is therefore a hardware layout contract: correctness depends on exact masks and shifts, not on local algorithms in this file.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or storage objects in this chunk. The macro namespace is the API surface.

The requested range starts in the tail of `D2F3_PCIE_ERR_CNTL` and continues through the rest of the `D2F3` function's PCIe internal, PCIe capability, bridge/configuration-space, MSI, power-management, error-reporting, virtual-channel, equalization, ACS, and multicast definitions. It then covers a full `D2F4` function block and the first part of `D2F5`.

Major macro groups in this range are:

- PCIe internal transaction/link control for `D2F3`, `D2F4`, and `D2F5`: `PCIE_TX_*`, `PCIE_RX_*`, `PCIE_ERR_CNTL`, `PCIE_FC_*`, `PCIEP_ERROR_INJECT_*`, `PCIEP_PORT_CNTL`, `PCIEP_HW_DEBUG`, and `PCIEP_SCRATCH`.
- Link controller programming: `PCIE_LC_CNTL`, `PCIE_LC_CNTL2`, `PCIE_LC_CNTL3`, `PCIE_LC_CNTL4`, `PCIE_LC_CNTL5`, `PCIE_LC_CNTL6`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_CDR_CNTL`, `PCIE_LC_LANE_CNTL`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, and `PCIE_LC_STATE0` through `PCIE_LC_STATE5`.
- PCI configuration-space fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, bridge window fields, secondary status, bridge/IRQ bridge control, and bus-number fields.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, `ROOT_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.
- MSI and power-management capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data fields, MSI mapping capability/address fields, `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- Advanced PCIe capabilities: vendor-specific extended capability headers, VC capability/control/status for VC0/VC1, device serial number, AER uncorrectable/correctable status/mask/severity, AER capability/control, header and TLP-prefix logs, root error command/status/source ID, secondary PCIe capability, link control 3, lane error status, lane equalization controls, ACS capability/control, and multicast capability/control/address/block/overlay fields.

The `D2F4` section is the most complete in this chunk. It includes the function's direct port index/data pair, PCIEP port/debug controls, full TX/RX credit and error fields, full link-controller definitions, complete capability/configuration-space fields, per-lane equalization controls for lanes 0-15, ACS fields, and multicast fields. `D2F3` is complete only after accounting for lines before this chunk, and `D2F5` is only partially covered here.

## Control Flow

This file has no runtime control flow. Every line is a preprocessor definition. Runtime behavior appears only in consumers that read, mask, shift, modify, and write hardware registers.

A typical caller flow is:

1. Select a BIF/PCIe register address from `bif_5_1_d.h`, for example an `ixD2F4_PCIE_LC_SPEED_CNTL`-style indirect register or a `D2F4_PCIE_PORT_INDEX/DATA` path.
2. Read the register with the ASIC's PCIe access helper.
3. Extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert a new field value with the same pair.
4. Write the modified register back if the field is writable and the link/power state permits it.

The control-sensitive fields are concentrated in the link-controller and transaction layers. Examples include speed-change initiation, link width reconfiguration, equalization redo/quiesce controls, link reset/recovery controls, ASPM/L0s/L1 behavior, completion timeout controls, RX ignore/unsupported-request policy, TX replay and flow-control settings, and error injection bits. The macro definitions themselves do not enforce safe sequencing.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes state held in GPU hardware registers.

The described hardware state includes PCIe function configuration and capabilities, link speed and width, ASPM and L-state policy, lane reversal and equalization state, TX/RX flow-control credits, sequence/replay status, requester IDs, AER status and masks, MSI and power-management capability fields, virtual-channel resource state, ACS policy, multicast address/block settings, and debug/error-injection controls.

Persistence depends on the specific register and platform sequencing. Some fields are status-only snapshots, some are sticky status or write-one-to-clear error fields, some are strap-derived capability fields, and some are control/override fields that remain programmed until a later driver or firmware write, PCIe retrain, function reset, hot reset, suspend/resume transition, power-gating/BACO transition, or full device reset. The mask header does not encode those access semantics, so consumers must rely on the hardware specification and established AMDGPU sequences.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register naming contract and the matching BIF 5.1 address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h`. The address header supplies the register locations such as `ixD2F3_PCIE_RX_CNTL`, `ixD2F4_PCIE_LC_SPEED_CNTL`, and `ixD2F5_PCIE_TX_CNTL`; this file supplies the fields inside those registers.

Direct include points found in this tree are the CIK/Sea Islands interrupt-handler sources:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c`

More broadly, the same AMDGPU BIF/PCIe access pattern is used by ASIC setup, PCIe link management, power management, interrupt handling, debugfs register access, and hardware diagnostics. Register helpers and indirect accessors live outside this header; this file only provides the bit layout.

Although the path is under a local `ceph-client` source mirror, this chunk is AMDGPU Linux kernel driver register metadata. It has no Ceph filesystem semantics, distributed-storage protocol behavior, or persistent filesystem state.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly while reading the wrong status bit, failing to update a desired field, or corrupting neighboring fields in packed PCIe registers.

High-risk fields include link training and power controls such as `LC_RESET_LINK`, `LC_RECONFIG_NOW`, `LC_RENEGOTIATE_EN`, `LC_INITIATE_LINK_SPEED_CHANGE`, `LC_GO_TO_RECOVERY`, `LC_REDO_EQ`, `LC_SET_QUIESCE`, ASPM/L0s/L1 inactivity fields, lane powerdown permissions, and equalization preset/coefficient controls. Incorrect use can leave the device at the wrong width/speed, trigger retraining loops, quiesce traffic, or destabilize suspend/resume.

RX/TX transaction controls are also sensitive. `RX_IGNORE_*`, completion timeout disables, NAK controls, TPH/PASID-related unsupported-request ignores, TX replay controls, requester ID fields, advertised/initialized credit fields, and flow-control update thresholds can change error handling, ordering, and liveness. Misprogramming these fields can mask real PCIe errors or generate spurious AER/completion-timeout behavior.

Capability and strap-like fields must be treated carefully. Device, link, slot, root, VC, ACS, multicast, MSI, and power-management fields describe what PCI enumeration and the OS believe the function supports. Changing or mis-decoding them can cause feature exposure mismatches, broken virtualization/IOMMU isolation expectations, incorrect MSI behavior, or bad power-management negotiation.

The repetitive `D2F3`/`D2F4`/`D2F5` naming makes copy/generation errors hard to spot. A field value that is correct for one function but attached to another function's macro would only show up when that downstream function is used. Per-lane equalization macros are similarly repetitive and vulnerable to lane-number or half-register mixups.

This chunk has line-boundary splits. It begins after the first `D2F3_PCIE_ERR_CNTL` mask/shift entries have already been defined, and it ends inside `D2F5_PCIE_LC_CNTL3`; later lines continue that register and the rest of `D2F5`. The final per-file merge should avoid treating those boundaries as real omissions in the source file.

## Test Signals

Useful validation signals are mostly compile-time and hardware-behavior oriented:

- Kernel build coverage for AMDGPU ASICs that include `bif_5_1_sh_mask.h`; missing, renamed, or malformed macros should surface as compile failures in CIK/Sea Islands paths.
- Static register-map validation comparing every generated `*_MASK`/`*__SHIFT` pair against AMD's source register database and the adjacent address definitions in `bif_5_1_d.h`.
- PCIe link bring-up, retrain, suspend/resume, and runtime power-management tests that confirm negotiated speed, width, lane reversal, ASPM/L-state behavior, and recovery/equalization status remain sane.
- PCIe error-path tests that exercise AER correctable/uncorrectable status, completion timeout, unsupported request, ECRC/LCRC, malformed TLP, and header/TLP-prefix log behavior.
- Flow-control and liveness checks that watch posted, non-posted, and completion credit status across TX/RX paths.
- MSI, power-management, virtual-channel, ACS, and multicast capability inspection from PCI configuration space to ensure decoded fields match expected hardware capabilities.
- Debug or lab diagnostics using error-injection, lane equalization, link-controller state registers, and per-lane status fields to confirm the expected bit positions are observed.

Regression symptoms from bad constants include link stuck at a lower generation, reduced link width after resume, repeated link retraining, GPU disappearance after power transitions, unexpected AER noise, masked PCIe errors, broken MSI/configuration-space reporting, or diagnostics showing activity on the wrong lane/function.

## Cross-Chunk Notes

Earlier chunks of `bif_5_1_sh_mask.h` define the beginning of the BIF 5.1 mask namespace and the first part of the `D2F3` downstream-function block. Later chunks continue `D2F5` after `PCIE_LC_CNTL3` and complete the rest of the header. The final per-file research document should treat the full file as one generated hardware register layout contract rather than as independent algorithms per chunk.

### subset-b-001492: lines 12893-16994

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h

Chunk: `subset-b-001492`
Covered source range: lines 12893-16994 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h`

## Purpose

This chunk is a generated AMD BIF 5.1 register field mask header segment. It contains no executable code; it supplies C preprocessor constants that describe bit masks and bit shifts for fields in PCIe/BIF configuration and link-control registers.

The assigned range covers 4,102 `#define` lines: 2,051 `_MASK` macros and 2,051 matching `__SHIFT` macros. It starts in the middle of the `D2F5_PCIE_LC_CNTL3` register field family and ends in the middle of the `D3F2_PCIE_LC_N_FTS_CNTL` family. The merge/reconciliation lane should combine adjacent chunks before producing final file-level conclusions for `bif_5_1_sh_mask.h`.

The covered register prefixes are:

- `D2F5`: completes a large function-5 PCIe/BIF block, beginning at the later `PCIE_LC_CNTL3` fields and continuing through PCIe link-control, PCI/PCIe capability, MSI, AER, ACS, VC, multicast, slot/root, config-space, and error-reporting fields.
- `D3F1`: a full function-1 style block in this range, including PCIe port, RX/TX, flow-control, error-injection, link-control, configuration-space capability, AER/ACS/VC/multicast, lane equalization, and bridge/root/slot fields.
- `D3F2`: the start of a function-2 block, covering PCIe port, RX/TX, flow-control, error-injection, link-control, and early `LC_N_FTS` fields before the chunk boundary.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The public surface is entirely macro constants used by AMDGPU register helper code.

The naming convention is consistent:

- `<REGISTER>__<FIELD>_MASK` isolates or clears the field in a 32-bit register value.
- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift count for extracting the field or the left-shift count before applying the mask.
- The register prefix, such as `D3F1_PCIE_LC_SPEED_CNTL`, is expected to match an address macro in `bif_5_1_d.h`, commonly named with an `ix` prefix for indexed PCIe/BIF config space.

Important macro families in this range include:

- Link controller fields: `PCIE_LC_CNTL`, `PCIE_LC_CNTL2`, `PCIE_LC_CNTL3`, `PCIE_LC_CNTL4`, `PCIE_LC_CNTL5`, `PCIE_LC_CNTL6`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_CDR_CNTL`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, and `PCIE_LC_STATE0` through `PCIE_LC_STATE5`.
- PCIe data-link and transaction-layer controls: `PCIE_TX_CNTL`, `PCIE_TX_REPLAY`, `PCIE_TX_REQUESTER_ID`, `PCIE_TX_REQUEST_NUM_CNTL`, `PCIE_TX_CREDITS_*`, `PCIE_RX_CNTL`, `PCIE_RX_CNTL3`, `PCIE_RX_CREDITS_ALLOCATED_*`, `PCIE_FC_P`, `PCIE_FC_NP`, and `PCIE_FC_CPL`.
- Error handling and diagnostics: `PCIE_ERR_CNTL`, `PCIEP_HW_DEBUG`, `PCIEP_ERROR_INJECT_PHYSICAL`, `PCIEP_ERROR_INJECT_TRANSACTION`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, `PCIE_ERR_SRC_ID`, and header/TLP prefix log registers.
- Link capability and status: `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CAP2`, `DEVICE_CNTL`, `DEVICE_CNTL2`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CAP2`, `LINK_CNTL`, `LINK_CNTL2`, `LINK_STATUS`, `LINK_STATUS2`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS`.
- Virtualization, peer routing, and multicast capability fields: `PCIE_ACS_*`, `PCIE_MC_*`, `PCIE_VC_*`, and `PCIE_PORT_VC_*`.
- Per-lane equalization definitions for lanes 0-15, with downstream/upstream TX preset and RX preset-hint fields.
- Conventional PCI config-space and bridge fields such as `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `BASE_CLASS`, `SUB_CLASS`, `PROG_INTERFACE`, `BIST`, `CACHE_LINE`, `HEADER`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, and `SUB_BUS_NUMBER_LATENCY`.
- MSI and power-management capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_*`, `MSI_MSG_DATA*`, `MSI_MAP_*`, `PMI_CAP`, `PMI_CAP_LIST`, and `PMI_STATUS_CNTL`.

## Control Flow

This chunk has no runtime control flow. It is a compile-time register-description table expressed as preprocessor macros.

Runtime control flow is created by consumers that use these macros in read/modify/write or read/poll/write sequences. Typical patterns are:

- read a BIF or PCIe register through AMDGPU register accessors;
- use `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent mask/shift logic to extract or update a field;
- write the modified register value back;
- poll status fields such as link-training state, error status, credit availability, or interrupt/error bits until hardware reaches the expected state.

The link controller families influence PCIe state-machine decisions in consuming code or firmware flows: speed changes, link-width renegotiation, ASPM L0s/L1 transitions, recovery, equalization, fast training sequence counts, receiver detection, and hot-reset behavior.

## State And Persistence Behavior

The header itself owns no mutable state and persists nothing. Its constants are compiled into any translation unit that includes it.

The state addressed by the constants is device hardware state in BIF/PCIe configuration and link-controller registers. Values written through these masks can persist until overwritten by the driver, firmware, PCIe link events, function-level reset, hot reset, GPU reset, power-management transition, or device removal. Status and counter fields expose transient hardware observations such as current link speed, link width, lane equalization state, replay/error counts, flow-control credits, AER status, and root/slot events.

Some fields are latched or clear-on-write style in the broader PCIe/AER model. This header does not encode access semantics, so callers must know whether a field is read-only, write-one-to-clear, sticky, strap-derived, or writable before using a mask in a generic update operation.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The practical companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h`, which defines the register addresses that correspond to these field masks.

Direct BIF 5.1 mask-header includes found in the AMDGPU tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c`

Those interrupt-handler files include both `bif_5_1_d.h` and `bif_5_1_sh_mask.h` and use the same generated mask/shift naming style through register field helpers. Their visible runtime work is interrupt-ring setup, interrupt enable/disable, dummy-read control, MSI-related behavior, write-pointer writeback, and register programming via `RREG32`, `WREG32`, and `REG_SET_FIELD`.

The D2F5/D3F1/D3F2 prefix families also integrate with the indexed PCIe/BIF register address space exposed in `bif_5_1_d.h`. These definitions are architecture-generation specific and should not be mixed with a different BIF generation unless the hardware documentation explicitly guarantees identical layouts.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. These are untyped integer macros, so the compiler cannot tell whether a caller uses a `D3F1` field mask against a `D2F5` register, combines a mask with the wrong shift, or updates a read-only or write-one-to-clear status field as if it were a normal writable control bit.

This chunk starts and ends inside generated register families. The first visible field is not the first `D2F5_PCIE_LC_CNTL3` field, and the final `D3F2_PCIE_LC_N_FTS_CNTL__LC_N_FTS` mask/shift pair is outside this range. Any final register-family summary must include neighboring chunks.

Several fields affect live PCIe link behavior: speed change, link-width change, receiver detection, equalization, ASPM/L0s/L1, hot reset, recovery entry, lane power state, FTS counts, and PHY command behavior. Incorrect writes can destabilize the PCIe link, break resume, mask real errors, or make the device require reset.

Error-injection and hardware-debug registers are especially risky because they can deliberately create malformed physical or transaction-layer behavior. A production path should not write those fields except under explicit debug or validation control.

Capability and status fields mirror standardized PCI/PCIe concepts but still live in ASIC-specific generated headers. A field name that looks generic, such as `LINK_STATUS` or `DEVICE_CNTL2`, must still be interpreted through the exact BIF 5.1 address and access path.

Per-lane equalization macros are repetitive and easy to misuse. Lane numbering, upstream versus downstream preset fields, and paired fields packed into the same 32-bit register need careful review in any hand-written access code.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware integration checks:

- Compile all AMDGPU targets that include `bif_5_1_sh_mask.h`, especially Iceland, Tonga, and Carrizo interrupt-handler paths.
- Static generator checks that every `_MASK` macro has exactly one matching `__SHIFT` macro in the final full header and that no duplicate macro name has conflicting values. In this assigned range, the 2,051 masks and 2,051 shifts are balanced.
- Cross-check field register prefixes in `bif_5_1_sh_mask.h` against address macros in `bif_5_1_d.h`, especially for `D2F5`, `D3F1`, and `D3F2`.
- Exercise interrupt-ring initialization, MSI and non-MSI interrupt handling, dummy-read setup, write-pointer writeback, suspend/resume, and GPU reset on BIF 5.1 ASICs.
- Validate PCIe link training and retraining paths across Gen1/Gen2/Gen3 speed selection, lane-width negotiation, ASPM transitions, hot reset, function-level reset, and recovery.
- Read back representative single-bit and multi-bit fields after controlled writes where the hardware permits it, confirming that mask/shift extraction matches expected values.
- Run AER/error-status tests that verify correct handling of correctable/uncorrectable error masks, root error status, header logs, and clear-on-write semantics.
- Lab-test lane equalization and per-lane status reporting because those fields can compile cleanly while targeting the wrong lane or preset nibble.

### subset-b-001493: lines 16995-21114

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 16995-21114

## Scope And Purpose

This chunk is part of AMDGPU's generated BIF 5.1 register field mask header. It contains only C preprocessor constants, not executable code. Each definition describes a bit mask or right-shift for a field in AMD PCIe/BIF registers, primarily for device/function namespaces `D3F2`, `D3F3`, and the start of `D3F4`.

The practical purpose is to provide a compile-time bit-layout contract for driver code that reads, decodes, modifies, or writes PCIe and BIF hardware registers. The matching address header, `bif_5_1_d.h`, provides register addresses; this header provides the field packing. Callers combine `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` with low-level MMIO or PCIe-port access helpers to avoid hard-coding bit positions in runtime logic.

The range starts in the middle of `D3F2_PCIE_LC_N_FTS_CNTL` at `LC_N_FTS`, covers the rest of the `D3F2` PCIe link-controller/configuration capability space, covers a large and more complete `D3F3` function block, and ends at the beginning of `D3F4_STATUS`. It includes 2060 complete mask/shift field pairs within the requested line range.

Although this repository path sits under a Ceph source mirror, the content of this chunk is Linux AMDGPU hardware metadata. There is no distributed filesystem or Ceph client logic here.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The important API is the generated macro naming convention:

- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- Consumers normally use `(reg & FIELD_MASK) >> FIELD__SHIFT` to decode a field, and clear/insert fields with `reg = (reg & ~FIELD_MASK) | ((value << FIELD__SHIFT) & FIELD_MASK)`.

The `D3F2` portion begins with link-controller fields and then enumerates PCI/PCIe configuration and capability registers. Important groups include `D3F2_PCIE_LC_SPEED_CNTL`, `D3F2_PCIE_LC_CDR_CNTL`, `D3F2_PCIE_LC_LANE_CNTL`, `D3F2_PCIE_LC_FORCE_COEFF`, `D3F2_PCIE_LC_FORCE_EQ_REQ_COEFF`, and `D3F2_PCIE_LC_STATE0` through `D3F2_PCIE_LC_STATE5`. These describe link speed negotiation, Gen2/Gen3 capability straps, software/hardware speed-change gating, current data rate, equalization coefficient forcing, corrupted/disabled lanes, CDR test fields, and recent link-controller state history.

The `D3F2` configuration-register families include conventional PCI header fields such as `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, class code fields, BIST, bus numbers, I/O and memory base/limit windows, bridge control, interrupt line/pin, and subsystem ID capability fields. They also cover PCI Express capability registers such as `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, `ROOT_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, and `SLOT_STATUS2`.

The error and advanced-capability portion for `D3F2` includes `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header/TLP-prefix log registers, root error command/status, error source ID, VC capability/control/status, vendor-specific enhanced capability headers, device serial number fields, ACS capability/control, and multicast (`PCIE_MC_*`) registers. These constants describe AER reporting, isolation/security controls, virtual-channel resources, multicast groups, and diagnostic log extraction.

The `D3F3` portion repeats much of the standard PCI/PCIe capability map and adds substantial controller-internal state. `D3F3_PCIE_PORT_INDEX` and `D3F3_PCIE_PORT_DATA` define the indirect port access aperture. `D3F3_PCIEP_HW_DEBUG`, `D3F3_PCIEP_PORT_CNTL`, `D3F3_PCIEP_RESERVED`, and `D3F3_PCIEP_SCRATCH` expose debug bits, hotplug/PME/power-fault control, completion payload policy, scratch storage, and reserved port metadata.

The `D3F3` transmit/receive and flow-control groups include `PCIE_TX_CNTL`, `PCIE_TX_REQUESTER_ID`, `PCIE_TX_REQUEST_NUM_CNTL`, `PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, `PCIE_TX_ACK_LATENCY_LIMIT`, `PCIE_TX_CREDITS_*`, `PCIE_TX_CREDITS_STATUS`, `PCIE_TX_CREDITS_FCU_THRESHOLD`, `PCIE_RX_CNTL`, `PCIE_RX_CNTL3`, `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_CREDITS_ALLOCATED_*`, `PCIE_FC_P`, `PCIE_FC_NP`, and `PCIE_FC_CPL`. These fields control requester IDs, outstanding non-posted requests, replay and ACK timers, advertised and initialized credits, credit error/status bits, receive error filtering, completion timeouts, PASID/prefix-related unsupported-request behavior, and allocated receive credits.

The `D3F3` error-injection and link-controller groups are especially sensitive. `D3F3_PCIEP_ERROR_INJECT_PHYSICAL` and `D3F3_PCIEP_ERROR_INJECT_TRANSACTION` expose physical-layer and transaction-layer fault injection fields. `D3F3_PCIE_ERR_CNTL` controls error reporting, ECRC/LCRC generation and dropping, AER header-log timing, slave-buffer halt status/reset, immediate error-message sending, and poisoned advisory behavior. `D3F3_PCIE_LC_CNTL`, `LC_CNTL2`, `LC_CNTL3`, `LC_CNTL4`, `LC_CNTL5`, `LC_CNTL6`, `LC_BW_CHANGE_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_FORCE_COEFF`, `LC_FORCE_EQ_REQ_COEFF`, `LC_BEST_EQ_SETTINGS`, and `LC_STATE0` through `LC_STATE5` describe ASPM/L0s/L1/L23 handling, link resets, quiesce/recovery triggers, Gen3 equalization policy, lane-width reconfiguration, N_FTS timing, speed-change attempts, partner capability observations, and link-state history.

The `D3F3` lane and capability groups include `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`, `PCIE_LANE_ERROR_STATUS`, `PCIE_P_PORT_LANE_STATUS`, VC resources, AER logs, ACS, multicast, MSI mapping/message fields, PMI, slot/root controls, and strap/status helpers such as `PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, `PCIEP_BCH_ECC_CNTL`, `PCIEP_HPGI_PRIVATE`, and `PCIEP_HPGI`.

The `D3F4` portion starts with port-index/data, debug, port control, TX/RX/credit/error/link-controller fields, physical and transaction error injection, strap/HPGI/BCH-ECC fields, and then enters standard PCI identification and command/status fields. The requested range ends after `D3F4_STATUS__CAP_LIST__SHIFT`; remaining `D3F4_STATUS` fields continue in the next source chunk.

## Control Flow

This header chunk has no direct control flow. It influences control flow in callers by defining how runtime register values are interpreted. A PCIe helper might read a `D3F3_PCIE_LC_SPEED_CNTL` register, decode `LC_CURRENT_DATA_RATE`, branch on the current link generation, set `LC_TARGET_LINK_SPEED_OVERRIDE`, and then set `LC_INITIATE_LINK_SPEED_CHANGE`. Another path might inspect `D3F3_PCIE_LC_LINK_WIDTH_CNTL__LC_LINK_WIDTH_RD`, decide whether link width is degraded, and request reconfiguration with `LC_RECONFIG_NOW` or `LC_RENEGOTIATE_EN`.

The same pattern applies to error handling and diagnostics. AER code or validation tooling can decode uncorrectable/correctable status fields, root error status, header logs, and TLP prefix logs; link validation code can decode per-lane equalization controls and lane error status; hardware test paths can program `PCIEP_ERROR_INJECT_PHYSICAL` or `PCIEP_ERROR_INJECT_TRANSACTION`; flow-control debug paths can inspect advertised, initialized, allocated, and current credit status fields.

Because the macros are generated constants, branch behavior remains in the consuming C files. This chunk's role is to make those branches target the intended bits. A wrong mask or shift would not fail locally in this header; it would make otherwise valid caller control flow observe the wrong state or write the wrong control bit.

## State And Persistence Behavior

The chunk itself stores no state and persists nothing in kernel memory. The state described by the macros is hardware state in PCIe/BIF registers: link speed and width, link-controller state history, ASPM and low-power transition policy, CDR and equalization settings, N_FTS timing, lane disable/corruption state, slot/root/device capability and status fields, AER status and masks, VC and multicast controls, TX/RX flow-control credits, replay/sequence counters, error-injection controls, hotplug/PME/power-fault status, BCH ECC status, and strap-derived configuration.

Persistence semantics belong to the hardware registers and are not encoded in the macro names. Some fields are read-only status, some are writable controls, some are sticky error/status bits, some may be write-one-to-clear, some are strap-derived, and some are self-clearing commands. Driver code must combine these mask/shift constants with hardware documentation or established AMDGPU register sequences to know when a write is safe and whether a read value survives link retraining, FLR, suspend/resume, BACO-like power transitions, hot reset, or full device reset.

Several fields can alter persistent device behavior until the next reset or driver write. Examples include PCI command enable bits, AER masks/severity, ACS controls, VC resource controls, RX ignore/error policy, TX credit/replay policy, link speed/width overrides, ASPM/L-state policy, hotplug/PME enables, and error-injection controls.

## Dependencies And Integration Points

This chunk depends only on the C preprocessor, but it is meaningful only with the rest of the AMDGPU register-header set. The matching `bif_5_1_d.h` address definitions identify the registers, and AMDGPU register-access helpers perform the actual MMIO or indirect PCIe-port reads and writes. Consumers generally include generated ASIC headers through AMDGPU's device-specific register access layers rather than using these masks as standalone definitions.

Integration points include:

- PCIe link management code that reads and writes `PCIE_LC_SPEED_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_STATUS`-style state from adjacent chunks, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_TRAINING_CNTL`, and `PCIE_LC_CNTL*`.
- Power-management and suspend/resume paths that adjust ASPM/L0s/L1/L23 behavior, lane power state, quiesce/recovery handling, and Gen3 equalization behavior.
- PCI/PCIe configuration-space handling that decodes command/status, bridge windows, MSI/MSI mapping, PMI, slot/root/device/link capabilities, and enhanced capability list pointers.
- Error handling and diagnostics that consume AER status/mask/severity, root error status, header logs, TLP prefix logs, ECRC/LCRC generation controls, and `PCIE_ERR_CNTL`.
- Validation and manufacturing paths that use physical/transaction error injection, per-lane equalization controls, lane error status, debug registers, scratch registers, and BCH ECC status.
- Flow-control and transaction-layer debug paths that inspect TX/RX credits, replay counters, sequence numbers, requester IDs, completion timeout policy, and receive ignore rules.
- Hotplug and platform notification paths that interact with `PCIEP_HPGI`, `PCIEP_HPGI_PRIVATE`, slot capability/control/status, PME, and power-fault fields.

The function prefixes matter. `D3F2`, `D3F3`, and `D3F4` identify separate device/function register namespaces with heavily repeated layouts but not always identical coverage. Callers must use the function-specific address and mask names together; mixing `D3F3_*` masks with `D3F4_*` register addresses because the field names look similar can silently target wrong or absent fields.

## Risks And Edge Cases

The dominant risk is silent hardware misprogramming. These definitions compile as constants, so a bad mask, bad shift, or wrong namespace selection usually shows up only as bad hardware behavior: incorrect link speed reporting, failed link retraining, degraded link width, unexpected ASPM behavior, unhandled AER events, broken hotplug notification, malformed credit accounting, or failure to clear/observe sticky status.

Link-controller control bits have high blast radius. Misusing `LC_RESET_LINK`, `LC_GO_TO_RECOVERY`, `LC_SET_QUIESCE`, `LC_REDO_EQ`, `LC_RECONFIG_NOW`, `LC_RENEGOTIATE_EN`, `LC_INITIATE_LINK_SPEED_CHANGE`, speed override fields, or dynamic lane-power fields can retrain or reset the link, disrupt traffic, or leave the GPU behind a nonfunctional PCIe path.

Error-injection fields are dangerous outside controlled validation. `PCIEP_ERROR_INJECT_PHYSICAL`, `PCIEP_ERROR_INJECT_TRANSACTION`, and the LCRC/ECRC generation bits in `PCIE_ERR_CNTL` can intentionally create PCIe errors. Leaving those fields enabled in production paths could cause AER storms, data-transfer failures, or device removal.

The repeated `D3F2`/`D3F3`/`D3F4` and per-lane definitions are vulnerable to generation, copy, and boundary mistakes. Per-lane equalization fields repeat for lanes 0-15; lane error status and lane-width fields can be especially hard to validate on narrow links. Some `D3F2` and `D3F3` blocks include full PCIe capability definitions, while the `D3F4` block in this chunk is incomplete because the requested range ends mid-status-register.

Capability/status fields do not describe access semantics. Conventional PCI status bits, AER status, root error status, hotplug status, BCH ECC status, and link-controller status may be read-only, sticky, write-one-to-clear, reset-on-read, or self-clearing depending on the register. The header gives bit positions only; incorrect clearing policy in callers can lose evidence or fail to acknowledge hardware.

The requested range starts at line 16995 after earlier `D3F2_PCIE_LC_N_FTS_CNTL` fields and ends at line 21114 after `D3F4_STATUS__CAP_LIST__SHIFT`. Adjacent chunks must be reconciled for complete per-register coverage of those boundary registers.

## Test Signals

Useful validation is mostly build- and hardware-oriented:

- Compile AMDGPU configurations that include BIF 5.1 generated headers. Missing or renamed macros should surface as compiler errors in PCIe, power-management, and diagnostics code.
- On supported hardware, verify reported PCIe link generation and width before and after runtime PM, suspend/resume, and explicit retraining. Bad `LC_SPEED_CNTL` or `LC_LINK_WIDTH_CNTL` constants can appear as a link stuck at a lower generation or width.
- Exercise ASPM and low-power transitions and watch for hangs, AER noise, resume failures, or unexpected link resets tied to `PCIE_LC_CNTL*` and training-control fields.
- Validate AER paths by checking uncorrectable/correctable status, root error status, header/TLP-prefix logs, and masks/severity against expected injected or observed events.
- In controlled validation only, use error-injection fields to confirm physical-layer and transaction-layer error reporting paths fire and clear as expected.
- Inspect TX/RX flow-control credit registers, replay counters, expected sequence numbers, and requester IDs during stress traffic to catch field-position errors in credit or transaction-layer macros.
- Test hotplug/PME/power-fault and HPGI status/enables where platform support exists.
- Validate lane-specific equalization and lane-error reporting on x1, x4, x8, and x16 configurations, including lane reversal where available, because copy/prefix mistakes often appear only on particular lane widths.

## Cross-Chunk Notes

This is one slice of a very large generated header. Earlier lines define the beginning of `D3F2_PCIE_LC_N_FTS_CNTL`; later lines complete `D3F4_STATUS` and continue the generated BIF 5.1 mask namespace. The final per-file report should treat `bif_5_1_sh_mask.h` as generated hardware register metadata, not as algorithmic AMDGPU logic, and should merge this chunk with adjacent chunks before drawing conclusions about complete register coverage.

### subset-b-001494: lines 21115-25046

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 21115-25046

## Purpose

This chunk is a generated AMD BIF 5.1 register field mask/shift section. It does not contain executable logic; it defines C preprocessor constants that describe bit positions inside PCI/PCIe/BIF registers for AMD GPU support code. The companion address header is `bif_5_1_d.h`; this file supplies the `*_MASK` and `*__SHIFT` values used with the register addresses from that header.

The covered range contains 3,932 `#define` lines. It starts in the middle of the `D3F4_STATUS` field list, completes the rest of the `D3F4` function-4 PCI/PCIe capability and extended capability masks, covers the much larger `D3F5` function-5 PCIe port/link-control block, then enters wrapper-level `PSX80_WRP_*` and `PSX81_WRP_*` strap/control definitions. The range ends in the middle of the `PSX81_WRP_BIF_STRAP_MISC_PORT_D` family, so the final per-file report must merge this with the next chunk before treating the `PSX81` wrapper family as complete.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this chunk. The interface is the generated macro naming contract:

- `REGISTER__FIELD_MASK` gives the already-positioned bit mask for a field.
- `REGISTER__FIELD__SHIFT` gives the least significant bit index for extraction or insertion.
- Full-register fields use masks such as `0xffffffff` and shift `0`.
- Register prefixes must be paired with the matching address macros in `bif_5_1_d.h`; the mask header alone does not identify the access method.

Major macro groups in this chunk:

- `D3F4_*`: 1,040 macro definitions across 131 register names. These complete function 4 PCI config-space fields and capabilities, including status/class/header/BIST, bridge bus windows, interrupt and bridge control, PMI, PCIe capability registers, device/link/slot/root capability and status, MSI and MSI-map fields, subsystem ID, vendor-specific and virtual-channel extended capabilities, AER status/mask/severity/header-log/root-error fields, secondary PCIe capability, lane equalization controls for lanes 0-15, ACS, and multicast capability/control/address/block/overlay fields.
- `D3F5_*`: 1,938 macro definitions across 196 register names. This is the largest section and includes `D3F5_PCIE_PORT_INDEX/DATA`, `PCIEP_*` private port registers, transmit/receive datapath controls, flow-control credit advertisement/allocation/status, replay and requester ID fields, error controls and injection registers, link-controller controls (`PCIE_LC_CNTL*`, training, width, speed, CDR, lane, equalization coefficient, and state registers), hot-plug GPIO interrupt registers, function-5 PCI config-space and capability fields, AER/ACS/multicast/VC/vendor-specific extended capability fields, and lane equalization controls for lanes 0-15.
- `PSX80_WRP_*`: 626 macro definitions across 87 register names. These describe wrapper-level control, timing, strap, efuse, lane counter, delay-line, DTM, register-adaptation, and per-port link/ASPM/training strap fields for PSX80. Port strap definitions cover ports A-E in this range.
- `PSX81_WRP_*`: 324 macro definitions across 38 register names. These mirror a subset of the PSX80 wrapper strap/control set for PSX81, including feature-enable, PI, link-speed, LC miscellaneous, error-ignore, ACS, SSID, lane equalization, hold-training, port-is-sideband, and port A-D strap families. The port D `BIF_STRAP_MISC` family is incomplete at the chunk boundary.
- `C_PCIE_INDEX` and `C_PCIE_DATA`: full-width index/data masks for another PCIe indirect register aperture.

Important specific field families include:

- PCIe standard capability fields: max payload/read request size, relaxed ordering, no-snoop, FLR, link speed/width, ASPM and clock power management, link training, slot hotplug, root PME/error controls, completion timeout, ARI, atomic operations, ID-based ordering, LTR, OBFF, TLP prefix support, and Gen3 equalization status.
- Interrupt/MSI fields: MSI enable, multiple-message capability/enable, 64-bit capable, per-vector mask capability, MSI message address/data, MSI-map enable/fixed/64-bit/address values, bridge interrupt line/pin, and wrapper autonomous bandwidth interrupt bits.
- AER/error fields: uncorrectable and correctable error status/mask/severity bits, ECRC generation/checking, first error pointer, header logs, TLP prefix logs, root error command/status/source ID, RX ignore controls, generated LCRC/ECRC error bits, error injection controls, and completion/unsupported-request handling.
- Link and PHY tuning fields: LC target speed, link width, lane reversal, hardware/software/autonomous speed changes, equalization wait and coefficient controls, FS/LF presets, bypass equalization, CDR controls, N_FTS, lane power/downconfigure, TX/RX credit and sequence controls, and lane error/equalization status.
- Strap and wrapper fields: advertised capabilities for AER/ECN/ARI/ACS/LTR/OBFF/MSI, subsystem IDs, Gen2/Gen3 compliance/kill/force modes, target link speed, ASPM latencies, de-emphasis, single-path clock modes, enhanced hotplug, ECRC, BCH ECC, error-reporting disable, and debug/test/DFT options.

## Control Flow

This header has no runtime control flow. It is a collection of compile-time substitutions used by driver code that performs register reads, read-modify-writes, writes, and polling.

The operational pattern for consumers is:

1. Read a 32-bit register through the AMDGPU MMIO or indexed-register helper appropriate for the address macro.
2. Extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert a new field value with the mask and shift pair.
3. Write the updated register back, or poll until a status bit or field reaches an expected value.

The order of definitions follows generated register-map order, not hand-written control flow. Function and wrapper boundaries are important: this range begins after earlier `D3F4_COMMAND` and initial `D3F4_STATUS` bits, transitions from `D3F4_PCIE_MC_OVERLAY_BAR1` into `D3F5_PCIE_PORT_INDEX`, then from `D3F5_PCIE_MC_OVERLAY_BAR1` into `C_PCIE_INDEX/DATA` and `PSX80_WRP_*`, and later from `PSX80_WRP_DELAYLINE_STATUS` into `PSX81_WRP_*`.

## State And Persistence Behavior

The header itself stores no mutable state and has no persistence behavior. State changes occur only in hardware registers when other driver code uses these constants.

The affected hardware state is persistent until overwritten or reset by GPU reset, PCIe reset, function-level reset, BACO/power transition, firmware action, or another driver path. In this chunk, that state includes:

- PCI config-space and PCIe capability exposure for functions 4 and 5.
- PCIe bridge windows, bus numbers, interrupt routing, MSI programming, and subsystem IDs.
- Link negotiation, speed, width, ASPM, common-clock, retrain, equalization, and lane-level tuning state.
- AER/error-reporting policy, error status latches, header logs, root error status, and error-injection controls.
- RX/TX sequence, replay, flow-control credit, completion-timeout, and unsupported-request behavior.
- Wrapper straps that may be latched or firmware-influenced, including advertised features, Gen2/Gen3 modes, ECRC/BCH/ACS/ARI/LTR/OBFF support, port link configuration, sideband-port marking, and hold-training bits.
- Delay-line, DTM, efuse, lane counter, and wrapper debug/test control fields.

Because these constants are raw bit definitions, they provide no locking, validation, sequencing, or side-effect protection. Any ordering constraints around link training, reset, strap latching, or error clearing are enforced by the calling driver/firmware code and hardware specification, not by this header.

## Dependencies And Integration Points

The direct dependency is the generated AMD ASIC register contract: macro names and numeric values must match the BIF 5.1 register database and the companion `bif_5_1_d.h` address definitions.

Likely consumers are low-level AMDGPU/PowerPlay/NBIO/BIF code paths that include generation-specific ASIC register headers and use helper macros or register accessors to program PCIe and BIF registers. Integration points include:

- PCIe config-space setup for GPU functions, including device/link/slot/root capability control and status.
- MSI and interrupt setup paths that need `D3F4_*` or `D3F5_*` MSI fields.
- PCIe link bring-up, retraining, speed changes, lane equalization, and ASPM/power-management flows.
- AER, ACS, virtual-channel, multicast, vendor-specific, and secondary PCIe extended capability programming.
- Error diagnostics and recovery code that reads status/masks, clears latched errors, captures header logs, or toggles error injection.
- Wrapper/strap initialization code that programs PSX80/PSX81 port behavior, feature exposure, DTM/delay-line behavior, efuse-derived controls, and hold-training states.

The `D3F4` and `D3F5` prefixes are function-specific. The `PSX80_WRP` and `PSX81_WRP` prefixes are wrapper-instance-specific. Mixing fields across functions or wrapper instances can compile successfully while targeting the wrong register layout.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask, shift, function prefix, wrapper prefix, or address/mask pairing compiles cleanly but can set the wrong bit, fail to clear an error, advertise unsupported PCIe capabilities, or destabilize link training.

This chunk has boundary splits. It starts after the first `D3F4_STATUS` fields (`INT_STATUS` and `CAP_LIST`) and ends before the rest of `PSX81_WRP_BIF_STRAP_MISC_PORT_D`; per-field completeness checks must reconcile adjacent chunks. The `D3F4_COMMAND` family is visible immediately before this range but is not part of the assigned chunk.

Generated lane and port families are repetitive and easy to misuse. Lane equalization fields are emitted for lanes 0-15, with alternating low-half/high-half masks in each 32-bit register. Wrapper port straps repeat across A-E for PSX80 and A-D for PSX81 in this range. Reviewers should watch for off-by-one lane numbers, lexicographic sorting surprises, and accidental use of a port A mask against another port's register.

Several fields are disruptive or security-sensitive:

- Link control, hold-training, speed override, bypass equalization, CDR, lane width, and Gen2/Gen3 force/kill fields can prevent PCIe link recovery or reduce negotiated capability.
- Error-ignore and error-reporting-disable fields can hide real protocol errors.
- ACS/ARI/atomic/LTR/OBFF/VC/multicast strap fields can change IOMMU isolation, routing, ordering, or capability exposure.
- ECRC/BCH/ECC and error-injection fields can affect reliability diagnostics or intentionally create malformed traffic.
- Full-width scratch/reserved/vendor fields should not be treated as safe arbitrary write targets merely because they have `0xffffffff` masks.

There is no type safety around signedness or width. Callers should use the driver's normal unsigned 32-bit register types and should mask shifted input values before writing multi-bit fields.

## Test Signals

Useful validation is mostly static, build, and hardware-behavior oriented:

- Build all AMDGPU translation units that include `bif_5_1_sh_mask.h`; renamed or missing macros should fail compile.
- Run static generation checks that every `*_MASK` has the expected matching `*__SHIFT`, allowing for known chunk-boundary splits during chunk review.
- Compare register prefixes in this mask header against address macros in `bif_5_1_d.h` to catch stale or cross-generation field names.
- PCIe enumeration tests should confirm function 4/function 5 class, bridge windows, MSI/MSI-map, subsystem ID, and capability-list behavior.
- Link bring-up, retrain, Gen1/Gen2/Gen3 speed transitions, width negotiation, ASPM, common-clock, and suspend/resume tests should exercise LC, lane equalization, PSX80/PSX81 strap, and hold-training fields.
- AER/error tests should validate uncorrectable/correctable status/mask/severity, ECRC generation/checking, root error status, header/TLP prefix logs, and RX/TX error handling.
- ACS/ARI/atomic/LTR/OBFF/VC/multicast tests should verify that advertised capabilities and control bits match platform policy and IOMMU expectations.
- Hardware diagnostics should inspect RX/TX flow-control credits, replay/sequence counters, error injection, BCH/ECC behavior, lane error status, DTM/delay-line status, and wrapper debug/test fields after controlled operations.

## Cross-Chunk Notes

The final per-file research should merge this with earlier and later chunks for `bif_5_1_sh_mask.h`. This chunk is not a complete file-level view: it begins mid-`D3F4_STATUS` and ends mid-`PSX81_WRP_BIF_STRAP_MISC_PORT_D`. Its main contribution is the dense function-4/function-5 PCIe capability and function-5 PCIe port-control coverage plus the beginning of PSX80/PSX81 wrapper strap and timing definitions.

### subset-b-001495: lines 25047-28986

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 25047-28986

## Scope

This chunk is a generated AMDGPU BIF 5.1 register bitfield header segment. It contains only C preprocessor constants: every meaningful exported item is a paired `*_MASK` and `*__SHIFT` macro for extracting or composing fields inside 32-bit PCIe/BIF wrapper, link-management, reset, and PHY registers. There are no functions, structs, enums, storage objects, or executable control flow in this range.

The chunk starts in the tail of the `PSX81_WRP_*` wrapper register fields, covers `RFE_*` reset/front-end fields, then defines large mirrored `PSX80_BIF_*` and `PSX81_BIF_*` blocks, and ends in the beginning of `PSX80_PHY0_TX_*` lane/debug fields. The paired address/header side for these masks is expected to live in the matching `bif_5_1_d.h` register-definition header and nearby ASIC register include files.

## Purpose

The purpose of this header fragment is to make hardware register accesses type-light but name-stable. AMDGPU call sites can name a register family and field, then use common helper macros such as `REG_GET_FIELD(value, REG, FIELD)` and `REG_SET_FIELD(value, REG, FIELD, new_value)` without hard-coding literal bit positions. The constants in this chunk encode the hardware ABI for:

- PCIe strap and capability settings for BIF wrapper port D/E fields, including link speed, ASPM, payload support, ECRC/E2E prefix, enhanced hotplug, and initial FTS values.
- Wrapper diagnostics and timing registers: LNC counters, eFuse words, scratch registers, DTM clock/reset/timing fields, delay-line controller command/status fields, RX detect override, and register-adapter access-mode bits.
- RFE warm reset, soft reset, master/client reset triggers, power-down command/status bits, master timeout timers, and IMP arbitration/calibration status fields.
- Per-instance `PSX80_BIF_*` and `PSX81_BIF_*` PCIe core fields for debug/status, RX/TX last TLP captures, NAK counters, CI/control knobs, link controller history/status, WPR reset controls, hidden config decode enables, protocol error ignores, performance counters, PRBS test controls, strap feature enables, software reset commands/controls, clock/power-management, and lane mapping/power controls.
- `PSX80_PHY0_COM_*`, `PSX80_PHY0_RX_*`, and initial `PSX80_PHY0_TX_*` PHY lane fields for fuse-derived calibration, electrical idle, DFX/PRBS, deemphasis/margin tables, adaptation and CDR tuning, RX/TX lane power, global speed/divider commands, DLL/debug/test hooks, and per-lane RX adaptation bypass/debug controls.

## Important APIs, Types, and Macros

There are no callable APIs or C types in this chunk. The API surface is the macro naming contract:

- `REGISTER__FIELD_MASK` gives the shifted bit mask to isolate or replace a field.
- `REGISTER__FIELD__SHIFT` gives the right-shift amount for the field.
- Register prefixes identify hardware blocks: `PSX81_WRP_*` for wrapper registers, `RFE_*` for reset front-end control, `PSX80_BIF_*` and `PSX81_BIF_*` for two BIF/PCIe instances, and `PSX80_PHY0_*` for PHY0 common/RX/TX lanes.
- Repeated lane macros use a broadcast register plus `LANE0` through `LANE7` or packed lane fields, so code can either program all lanes or target individual lanes.
- Mirrored `PSX80_BIF_*` and `PSX81_BIF_*` definitions preserve the same field names and bit encodings for the two PCIe/BIF instances, which lets instance-specific code select the register prefix while reusing field logic.

Important field groups visible in this chunk include `PCIE_CNTL`, `PCIE_CNTL2`, `PCIE_RX_CNTL2`, `PCIE_CONFIG_CNTL`, `PCIE_CI_CNTL`, `PCIE_LC_STATE6` through `PCIE_LC_STATE11`, `PCIE_LC_STATUS1/2`, `PCIE_PERF_*`, `PCIE_PRBS_*`, `PCIE_STRAP_*`, `SWRST_COMMAND_*`, `SWRST_CONTROL_*`, `CPM_CONTROL`, `LM_*`, `COM_COMMON_*`, `RX_CMD_BUS_*`, `RX_DLL_CTL_*`, `RX_RXTEST_REGS_*`, `RX_ELECIDLE_DEBUG_*`, `RX_ADAPT*`, `RX_DBG_BYP_EN_*`, `RX_ADAPTDBG1_*`, and `TX_CMD_BUS_TX_CONTROL_*`.

## Control Flow

This header has no internal control flow. Its macros participate in control flow only at compile time when included by AMDGPU source files. Typical use is:

1. A driver path chooses the ASIC-specific register address macro from the matching definition header.
2. The path reads a 32-bit register through MMIO/SMN helpers such as the AMDGPU `RREG32*`/`WREG32*` family.
3. It extracts or updates a field using the mask/shift macro pair from this header.
4. It writes the modified value back, or interprets status bits for logging, reset sequencing, performance sampling, link diagnostics, or test-mode decisions.

The header does not enforce sequencing. For reset, power, PRBS, performance-counter, and PHY adaptation fields, correct ordering is entirely the responsibility of the runtime driver code and hardware documentation.

## State and Persistence Behavior

No software state is allocated or persisted by this chunk. The constants describe hardware register state. When used by driver code, writes may alter persistent device-visible state until the next reset, power transition, firmware action, strap reload, or driver reprogramming. Notable state categories described here are:

- Strap/capability state, such as PCIe feature enables, speed/equalization defaults, hotplug support, ASPM latency, ECRC, ATS/PASID/SR-IOV, and MSI capability fields.
- Link status/history state, including link controller previous-state logs, operating/detected width, inactive/turn-on lanes, NAK counters, last TLP captures, and PRBS error counters.
- Reset state, including warm reset enable, soft reset trigger/propagation, command status, reset-complete/wait-state bits, per-block reset controls, and write/reset/atomic enable gates.
- Power and clock state, including BIF clock gating latencies/enables, lane power commands, RX/TX power gates, L1 power gating, and RFE power-down command/status bits.
- PHY calibration/debug state, including fuse validity and calibration values, DTM/delay-line control/status, CDR/adaptation tuning, electrical-idle debug, DLL controls, RX adaptation bypass values/enables, and PRBS/DFX test settings.

Because several registers include one-shot command bits, sticky status bits, and reset controls, misuse can leave the PCIe link unstable or hide meaningful error reporting.

## Dependencies and Integration Points

This chunk depends on the broader AMDGPU register-header convention. It must stay synchronized with:

- Matching BIF 5.1 register address definitions, commonly included as `*_d.h` headers.
- AMDGPU register helper macros that concatenate `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- ASIC-specific NBIO/BIF initialization, reset, link-management, RAS, virtualization, performance-counter, and debug code that includes `asic_reg/bif/*_sh_mask.h`.
- Hardware/firmware strap behavior, because many `STRAP_*` fields represent boot-time or strap-derived capabilities that software may inspect or override only under narrow conditions.
- Per-instance register routing. `PSX80` and `PSX81` fields are structurally similar, but code must still select the correct instance/address base.

Observed repository integration patterns around these register headers include AMDGPU and RAS code using `REG_GET_FIELD`/`REG_SET_FIELD` with BIF/NBIO masks, and PCIe performance-count paths writing `PCIE_PERF_COUNT_CNTL`-style controls. This exact chunk is part of the same generated macro contract even when a given field is only used by low-level bring-up or diagnostics.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong mask, shift, or field name compiles cleanly but causes incorrect MMIO programming at runtime.
- `MASK_MASK` names such as `PSX81_WRP_PCIE_WRAP_REG_TARG_MISC__CLKEN_MASK_MASK` and `PRBS_CHK_ERR_MASK_MASK` are intentional products of field names containing `MASK`; downstream helper macros must use the generated spelling exactly.
- Duplicated `PSX80`/`PSX81` blocks are easy to edit inconsistently by hand. Any future regeneration or patch should compare both instances when fields are expected to match.
- Full-width masks such as `0xffffffff` need unsigned 32-bit handling at call sites. Sign extension bugs are possible if values are stored in signed integers before shifting or comparing.
- One-shot command fields, reset controls, PRBS/DFX controls, and PHY adaptation bypass fields are high-risk on live hardware. Setting them outside the documented sequence can break link training, mask protocol errors, perturb calibration, or wedge access to the device.
- Status fields may be sticky, write-one-to-clear, or sampled through a shadow mechanism depending on the register. This header does not encode those access semantics.
- The chunk begins and ends mid-register-family, so whole-file research must reconcile adjacent chunks for complete `PSX81_WRP_BIF_STRAP_MISC_PORT_D` and `PSX80_PHY0_TX_DFX_*` coverage.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-integration oriented:

- Kernel/driver builds that include `bif_5_1_sh_mask.h` should compile without undefined macro references from `REG_GET_FIELD`/`REG_SET_FIELD` users.
- Static checks can verify that every `*_MASK` in this line range has a corresponding `*__SHIFT`, and that field pairs are unique within each register prefix.
- Generated-header comparison against the authoritative ASIC register database should show no drift for lines 25047-28986.
- PCIe smoke tests on affected ASICs should cover link training, link width/speed reporting, suspend/resume or reset paths, and error-reporting paths that depend on BIF/PCIe controls.
- Diagnostics that exercise performance counters, PRBS, lane mapping, and PHY RX/TX test controls can catch swapped masks/shifts that ordinary boot tests might not touch.
- RAS or reset-path tests should watch for reset completion, timeout, power-down status, and link recovery behavior around the `RFE_*` and `SWRST_*` fields.

## Chunk Notes for Merge

This is a partial chunk of one large generated header. The final per-file research should merge this with adjacent chunks to describe the entire `bif_5_1_sh_mask.h` register universe. For this chunk specifically, the dominant theme is low-level PCIe/BIF wrapper, reset, link-management, performance/debug, PRBS, and PHY lane bitfield definitions; it should not be summarized as active driver logic.

### subset-b-001496: lines 28987-32973

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 28987-32973

## Purpose

This chunk is generated BIF 5.1 register field metadata for the AMD GPU PCIe/BIF PHY and PIF blocks. It contains only C preprocessor constants: every hardware field is represented by a `<register>__<field>_MASK` and a matching `<register>__<field>__SHIFT` macro. Driver code combines these masks and shifts with the address macros from `bif_5_1_d.h` to read, modify, and write indirect BIF/PHY/PIF registers without embedding raw bit positions at call sites.

The covered range is concentrated on PSX80 and PSX81 PHY0/PIF0 register families. It starts in the middle of `PSX80_PHY0_TX_DFX_LANE0` and ends in the middle of `PSX81_PIF0_LANE6_OVRD`; adjacent chunks carry the missing first and last definitions for those split registers.

## Important APIs, Types, And Macros

There are no functions, structs, or exported runtime APIs in this range. The important interface is the macro naming contract:

- `*_MASK` macros define the raw bitmask in a 32-bit register word.
- `*__SHIFT` macros define the least-significant bit position for the same field.
- Broadcast registers apply the same field programming to all lanes when hardware supports broadcast access.
- `LANE0` through `LANE7` variants expose per-lane copies of the same field layout.
- `PSX80_*` and `PSX81_*` denote two related PHY/PIF instances or register banks that share many layouts but have distinct address constants in `bif_5_1_d.h`.

Major macro groups in this chunk:

- `PSX80_PHY0_TX_*` and `PSX81_PHY0_TX_*`: TX DFX, de-emphasis, margin/de-emphasis test, margin/de-emphasis status, RX-detect response, TX command-bus global, and TX power-gating command fields.
- `PSX81_PHY0_RX_*`: RX command-bus power/electrical-idle fields, RX global link speed fields, RX analog control, DLL debug, PRBS/test controls, electrical-idle debug, adaptation controls, figure-of-merit calculation, adaptation bypass enables, debug bypass enables, and adaptation debug bus selection.
- `PSX80_PHY0_HTPLL_ROPLL_*`, `PSX81_PHY0_HTPLL_ROPLL_*`, `PSX80_PHY0_LCPLL_LCPLL_*`, and `PSX81_PHY0_LCPLL_LCPLL_*`: PLL power-down overrides, control words, frequency modes, update strobes, fuse process values, lock/calibration/test/debug status, VCO control, and measurement outputs.
- `PSX81_PHY0_COM_COMMON_*`: common PHY fuse, electrical-idle, DFX, nominal margin/de-emphasis, adaptation, CDR, lane power-management, line-control, and test-debug fields.
- `PSX80_PIF0_*` and `PSX81_PIF0_*`: PIF scratch/debug/strap, TX/RX power control, global RX-detect and ganged-lane overrides, command-bus status/control, global command-bus overrides, and per-lane override enable/value registers.

## Control Flow

This header has no runtime control flow. Its effect appears only after inclusion by C source that performs register programming. The typical control pattern is:

1. Select a hardware register address with an `ix...` macro from `bif_5_1_d.h`.
2. Read a 32-bit register value through the AMDGPU MMIO or indirect-register accessor.
3. Clear a field with `<field>_MASK`.
4. Insert a new field value shifted by `<field>__SHIFT`.
5. Write the modified value back, or poll a status bit until it reaches the expected state.

Within this chunk, the likely polling/status fields include PLL lock and calibration status (`PllLocked`, `CalDone`, `CalFail`), PIF command status (`TXPHYSTATUS_*`, `RXPHYSTATUS_*`, `BPHY_CORE_TX_RDY_*`, `BPHY_CORE_RX_RDY_*`), PRBS error state (`prbs_err`), RX FOM validity (`rx_fom_valid`), electrical-idle out-of-bounds/comparator results, and TX margin/de-emphasis allocation status (`ron_comp_valid`, `alloc_error`, `too_many_allocated`).

## State And Persistence Behavior

The file itself persists no software state. The macros describe hardware state stored in BIF/PHY/PIF registers. Those registers are volatile and can be changed by firmware, reset sequencing, link training, power management, or driver writes.

Important state classes exposed here:

- Link command state: `link_speed`, `freq_div2`, `twosym_en`, `gang_mode`, per-lane power fields, and command-bus override fields determine how PCIe PHY lanes are instructed during training, speed changes, and power transitions.
- PLL state: control, lock, calibration, VCO, measurement, and power-down fields describe the HTPLL/ROPLL and LCPLL configuration and readiness.
- Lane analog state: TX de-emphasis coefficients, margin select values, RX termination, DC offset, CDR/adaptation controls, DFE/LEQ bypasses, and electrical-idle detector tuning influence signal integrity.
- Debug/test state: PRBS, observation selection, debug buses, test margins, bypasses, and manual calibration triggers can alter normal data-path behavior if written outside controlled debug flows.
- Strap/fuse state: fuse and strap fields expose hardware defaults and process calibration inputs. They are normally read as hardware-provided configuration rather than treated as durable driver-owned settings.

## Dependencies And Integration Points

This header is part of the AMDGPU ASIC register include set. The address-side companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h`, which defines the `ix...` register addresses corresponding to these mask/shift names. Enum values, where needed, live beside it in `bif_5_1_enum.h`.

Direct includes found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c`

Those interrupt-handler files include both `bif_5_1_d.h` and this mask header so they can decode or program BIF-related interrupt registers using the generated constants. Other driver code may receive the definitions transitively or use the address-only header when no field-level manipulation is needed.

The chunk's register names align with low-level AMDGPU access helpers that operate on MMIO or indirect BIF registers. Callers must pair the correct instance prefix (`PSX80` vs. `PSX81`), register address (`ix...`), and mask/shift macro set. Mixing banks can silently program the wrong register or interpret unrelated bits.

## Risks And Edge Cases

- Generated-header drift: these macros must match the ASIC register specification and `bif_5_1_d.h` address table exactly. A stale mask or shift can corrupt unrelated hardware fields even when C code looks correct.
- Split chunk boundaries: this research range omits the earlier `obs_*` fields for `PSX80_PHY0_TX_DFX_LANE0` and stops before the `SHIFT`, `CDREN`, and `OVRD2` fields that complete `PSX81_PIF0_LANE6_OVRD`. Any per-register reconciliation must merge adjacent chunks before treating those two registers as complete.
- Per-lane repetition: many layouts repeat for lanes 0-7. Copy/paste or generated-name mistakes are easy to miss because masks are often single-bit shifts following a regular pattern.
- Broadcast vs. lane-specific writes: using a broadcast macro/address when a lane-specific operation was intended can affect all lanes, while using one lane macro for another lane can break asymmetric link configurations.
- Debug/test fields are dangerous in production paths. PRBS, loopback, observation, force, bypass, margin, calibration, and override bits can disrupt normal PCIe link operation.
- Power-management and readiness fields are timing-sensitive. Incorrect masks around `TXPHYSTATUS`, `RXPHYSTATUS`, `BPHY_CORE_*_RDY`, PLL power-down, or command-bus scheduling can lead to hangs during resume, link retraining, speed changes, or lane power gating.
- Some fields are status-like and some are control-like within the same register family. Read-modify-write code must not blindly preserve or overwrite write-one-to-clear, sticky, or hardware-updated fields unless the hardware contract says it is safe.

## Test Signals

Useful validation signals for code that depends on this chunk:

- Build coverage for ASICs that include `bif_5_1_sh_mask.h`, especially Iceland, Tonga, and Carrizo interrupt paths.
- Static checks that every `<register>__<field>_MASK` in this range has a matching `<register>__<field>__SHIFT`, accounting for documented chunk-boundary splits.
- Cross-check generated masks against `bif_5_1_d.h` address names for the same `PSX80`/`PSX81` register prefixes.
- Hardware or emulator smoke tests covering PCIe link bring-up, suspend/resume, runtime power management, speed change/retraining, and interrupt handling.
- Debug validation for PLL lock/calibration polling, PIF command-bus readiness, RX electrical-idle detection, FOM/adaptation reads, and TX/RX per-lane override programming.
- Register dump comparison before and after any driver change touching these fields to confirm only intended bits change.

### subset-b-001497: lines 32974-33080

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 32974-33080

## Purpose

This chunk is the final section of the generated AMD BIF 5.1 shift/mask header. It defines bit masks and bit shifts for the PSX81 PIF0 lane override registers at the end of the BIF register map, then closes the `BIF_5_1_SH_MASK_H` include guard.

The covered lines finish the lane 6 override definitions and provide the complete lane 7 override definitions. These constants describe the packed fields in `PSX81_PIF0_LANE6_OVRD2`, `PSX81_PIF0_LANE7_OVRD`, and `PSX81_PIF0_LANE7_OVRD2`. Driver code uses this style of generated header to compose and decode MMIO register values without hard-coding field positions in call sites.

## Important APIs, Types, And Functions

There are no C functions, structs, or runtime APIs in this chunk. The exported interface is a set of preprocessor constants:

- `PSX81_PIF0_LANE6_OVRD2__*_*`: masks and shifts for lane 6 override values, including gang mode, frequency divider, link speed, two-symbol enable, transmit and receive power states, pattern-generator enables, electrical-idle detection, figure-of-merit controls, tracking/training requests, and coefficient fields.
- `PSX81_PIF0_LANE7_OVRD__*_OVRD_EN_7_*`: one-bit enable masks and shifts that control whether the corresponding lane 7 field is overridden.
- `PSX81_PIF0_LANE7_OVRD__CDREN_OVRD_VAL_7_*`: lane 7 CDR enable override value field.
- `PSX81_PIF0_LANE7_OVRD2__*_*`: actual lane 7 override value fields. Multi-bit fields include `GANGMODE_7`, `FREQDIV_7`, `LINKSPEED_7`, `TXPWR_7`, `TXPGENABLE_7`, `RXPWR_7`, `RXPGENABLE_7`, `COEFFICIENTID_7`, and `COEFFICIENT_7`; single-bit fields include two-symbol enable, electrical-idle detect enable, FOM request/enable, response mode, tracking request, and training request.
- `#endif /* BIF_5_1_SH_MASK_H */`: closes the header guard that was opened at the top of the generated file.

The matching register-address constants live in `bif_5_1_d.h` as `ixPSX81_PIF0_LANE6_OVRD2`, `ixPSX81_PIF0_LANE7_OVRD`, and `ixPSX81_PIF0_LANE7_OVRD2`. This header supplies field extraction and construction constants; the companion `_d.h` header supplies the register index.

## Control Flow

This header has no executable control flow. Its operational flow is compile-time macro expansion:

1. A source file includes the AMD BIF 5.1 register definition headers.
2. Code selects the register offset from the companion register-address header.
3. Code uses the `*_MASK` and `*__SHIFT` constants from this header to clear, insert, or extract individual fields in a 32-bit register value.
4. The composed value is passed to an AMDGPU MMIO, indirect-register, or register-programming helper outside this chunk.

The register layout itself is regular. `LANE7_OVRD` uses low bits as override-enable selectors. `LANE7_OVRD2` stores the override values in the same order and bit positions as lane 6 and the preceding lanes. The file ending is also part of the compile-time control structure: the closing `#endif` completes the include guard and prevents duplicate macro definitions on repeated inclusion.

## State And Persistence Behavior

The chunk stores no software state and performs no MMIO by itself. Its state model is declarative: it records hardware bit layouts as C preprocessor definitions.

Persistent behavior appears only when another driver component uses these constants to write the PIF lane registers. Such writes affect hardware link-training and PHY lane behavior until the register is changed again, the block is reset, or the GPU is reset. The override-enable fields are especially stateful at the hardware level because setting an enable bit tells the PHY logic to use the corresponding software-provided value rather than autonomous hardware training or default behavior.

The constants must stay synchronized with the generated ASIC register database. A stale mask or shift does not fail locally in this header; it causes later register reads or writes to target the wrong bit positions.

## Dependencies

This chunk depends on the surrounding generated AMD register-header ecosystem:

- The `BIF_5_1_SH_MASK_H` include guard and file-level license/header context defined earlier in `bif_5_1_sh_mask.h`.
- Register index definitions in `bif_5_1_d.h`, especially `ixPSX81_PIF0_LANE6_OVRD2`, `ixPSX81_PIF0_LANE7_OVRD`, and `ixPSX81_PIF0_LANE7_OVRD2`.
- AMDGPU register helper conventions that pair `FIELD__MASK` and `FIELD__SHIFT` constants to build and decode register values.
- Hardware documentation for the BIF 5.1 PSX81 PIF0 lane override registers. The field names imply PHY Interface lane controls for link speed, power state, training, coefficient selection, and related PCIe/SerDes behavior.

There are no Linux kernel library dependencies in the chunk itself beyond normal preprocessor handling.

## Integration Points

The integration point is AMDGPU low-level register programming for BIF 5.1 ASICs. Consumers are expected to include this file with the matching BIF register-address header and use the lane override constants when programming or diagnosing PSX81 PIF0 lanes 6 and 7.

The constants align with the repeated lane layout used by the preceding lane definitions. This regularity is important for any code that handles lanes generically or validates generated register headers: lane 7 mirrors lane 6, with `_7` suffixes and the same masks/shifts for equivalent fields.

The chunk also integrates with the build system as a generated header endpoint. Because it contains the final `#endif`, truncation or accidental edits in this range can break every translation unit that includes `bif_5_1_sh_mask.h`.

## Risks And Edge Cases

- A wrong mask or shift can silently corrupt unrelated PHY control bits when a caller performs read-modify-write on a lane override register.
- The chunk starts at the tail of `PSX81_PIF0_LANE6_OVRD`; the first lane 6 override-enable fields are outside this range, so per-file reconciliation must merge this with the preceding chunk for a complete lane 6 view.
- Lane 7 definitions are copy-patterned from earlier lanes. Copy/paste or generation drift could leave a `_6` suffix, wrong register field name, or wrong bit position while still compiling.
- The `COEFFICIENT_7` field occupies the high six bits of the 32-bit register (`0xfc000000`, shift `0x1a`). Callers must use unsigned 32-bit arithmetic when composing values that touch this field.
- Override-enable fields and override-value fields are split between `LANE7_OVRD` and `LANE7_OVRD2`. Programming values without the matching enable bits, or enabling fields without valid values, can produce ineffective or harmful hardware configuration.
- The final include-guard close is part of this chunk. Removing or moving it would produce duplicate-definition or unterminated-conditional build failures.

## Test Signals

Useful validation signals for this chunk are mostly build-time, static, and hardware bring-up checks:

- Kernel or driver builds including `bif_5_1_sh_mask.h` should compile without preprocessor guard errors or duplicate macro diagnostics.
- Static checks can compare lane 7 masks and shifts against lane 6 and earlier lanes to verify repeated-field consistency.
- Header-generation validation should confirm that `*_OVRD2` masks do not overlap incorrectly and cover only the documented bit ranges.
- Register read-modify-write tests should verify that composing a lane 7 field with `MASK` and `SHIFT` changes only the intended bits.
- Hardware PCIe/BIF bring-up should complete without link-training regressions on ASICs using BIF 5.1 when these lane override registers are left at defaults or programmed by diagnostics.
- PHY diagnostic paths that request FOM, tracking, training, or coefficient overrides should observe expected register values when reading back `PSX81_PIF0_LANE7_OVRD` and `PSX81_PIF0_LANE7_OVRD2`.
