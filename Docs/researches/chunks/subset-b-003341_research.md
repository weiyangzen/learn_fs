# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 34752-37218

## Scope

This chunk covers generated shift and mask macros from the NBIO 7.9.0 AMD GPU register mask header. The range starts at the tail of the `BIF_CFG_DEV0_EPF0_VF5` PCIe ARI capability, then covers complete PCI configuration-space images for `VF6` and `VF7`, followed by per-virtual-function BIF/RCC register blocks for `VF0`, `VF1`, and `VF2`. It ends after the `RCC_DEV0_EPF0_VF2_GFXMSIX_PBA` fields, immediately before the `VF3` BIF register block begins.

The covered register families are:

- `BIF_CFG_DEV0_EPF0_VF5_PCIE_ARI_CAP` and `BIF_CFG_DEV0_EPF0_VF5_PCIE_ARI_CNTL`, completing the previous VF5 PCIe ARI extended capability block.
- Full `BIF_CFG_DEV0_EPF0_VF6_*` and `BIF_CFG_DEV0_EPF0_VF7_*` PCI/PCIe virtual-function configuration headers, including base PCI header fields, PCIe device/link capabilities, MSI/MSI-X, vendor-specific extended capability fields, AER status/mask/logging, ATS, and ARI.
- `BIF_BX_DEV0_EPF0_VF0_*`, `VF1_*`, and `VF2_*` BIF PF/VF decode blocks for BME status, atomic error logging, doorbell self-ring aperture, HDP coherency flush controls, GPU HDP flush request/done bits, transaction-pending status, address LUT bypass, mailbox data/control, and VM/hypervisor mailbox signaling.
- `BIF_BX_DEV0_EPF0_VF0_MM_*`, `VF1_MM_*`, and `VF2_MM_*` system PF/VF decode indexed MMIO access registers.
- `RCC_DEV0_EPF0_VF0_*`, `VF1_*`, and `VF2_*` RCC blocks for SR-IOV error logging, doorbell aperture enable, config memory sizing/reserved state, IOV function identification, and four GFX MSI-X vector table entries plus pending-bit array.

This is a generated hardware bitfield map. It defines C preprocessor constants only. There are no C functions, structs, variables, allocations, locks, or executable control-flow constructs in this chunk.

## Purpose

The purpose of this section is to provide bit-level ABI constants for NBIO 7.9.0 virtual-function PCIe configuration space and per-VF BIF/RCC control registers. Every field follows the generated pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the containing register value.

The masks pair with address definitions from `nbio_7_9_0_offset.h` and related NBIF offset headers. Driver code includes this header from `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, then consumes the constants through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. For example, NBIO 7.9 setup code uses the matching VF0 HDP coherency flush offset as the remapped MMIO base when running as an SR-IOV virtual function.

## Important Macro Families

### VF5 ARI Tail

The first lines finish the `BIF_CFG_DEV0_EPF0_VF5` Alternative Routing-ID Interpretation fields:

- `PCIE_ARI_CAP` exposes multifunction/ACS function group capability bits and `ARI_NEXT_FUNC_NUM`.
- `PCIE_ARI_CNTL` exposes ARI function-group enable bits and the current function-group selector.

These fields affect VF function numbering and routing in PCIe SR-IOV environments. They are sensitive because incorrect ARI capability/control masks can change how software discovers or addresses VFs behind a PF.

### VF6 and VF7 PCI Configuration Images

The `VF6` and `VF7` address blocks are complete virtual-function PCI configuration-space maps. They repeat the same layout for two adjacent VFs:

- Base identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: I/O enable, memory enable, bus mastering, SERR, interrupt disable, capability-list presence, parity/abort/system-error bits, and DEVSEL timing.
- BAR and legacy header fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `ROM_BASE_ADDR`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability list/header, endpoint device capability/control/status, link capability/control/status, and PCIe 2.0+ `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X fields: MSI message control/address/data/mask/pending registers in 32-bit and 64-bit forms, plus MSI-X capability, table BIR/offset, PBA BIR/offset, function mask, enable, and table size.
- Vendor-specific extended capability fields: extended capability header, VSEC ID/revision/length, and two full-width vendor-specific data registers.
- AER fields: uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header-log dwords, and four TLP prefix-log dwords.
- ATS fields: enhanced capability header, invalidation queue depth, page-aligned/global-invalidate/relaxed-ordering support, smallest translation unit, and ATC enable.
- ARI fields: enhanced capability header, group capability bits, next function number, group enable bits, and function group selector.

These macros define the values exposed in the VF PCI configuration image rather than ordinary runtime queue state. They are tied to PCIe enumeration, interrupt programming, AER diagnostics, IOMMU address-translation behavior, and SR-IOV function routing.

### VF0-VF2 BIF PF/VF Decode Blocks

The `BIF_BX_DEV0_EPF0_VF0_*`, `VF1_*`, and `VF2_*` blocks expose per-VF BIF control/status registers. The repeated layout is important because driver code and firmware can index across VFs while expecting identical bit positions:

- `BIF_BME_STATUS` records DMA activity while bus mastering is low and includes a clear bit. This is a VF isolation and debug signal for bus-master-enable violations.
- `BIF_ATOMIC_ERR_LOG` records unsupported or invalid atomic request conditions: opcode, request-enable-low, length, and non-relaxed/non-request state, each with matching clear bits.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `BASE_LOW`, and `CNTL` configure a self-ring doorbell GPA aperture, including enable, mode, and size.
- `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL` provide per-VF coherency flush/invalidate control hooks.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` expose one bit per engine class: `CP0` through `CP9`, `SDMA0`, `SDMA1`, and reserved engine slots 0 through 19. The request/done pairing is the bit protocol used to order CPU-visible memory and GPU/HDP writes.
- `BIF_TRANS_PENDING` indicates outstanding BIF master/slave transactions.
- `NBIF_GFX_ADDR_LUT_BYPASS` controls graphics address LUT bypass.
- `MAILBOX_MSGBUF_TRN_DW0..DW3` and `MAILBOX_MSGBUF_RCV_DW0..DW3` provide 128-bit transmit and receive message buffers.
- `MAILBOX_CONTROL` provides transmit valid/ack and receive valid/ack handshake bits; `MAILBOX_INT_CNTL` controls valid/ack interrupt enables.
- `BIF_VMHV_MAILBOX` provides a compact hypervisor/VF mailbox register with interrupt enables, transmit/receive data fields, valid bits, and ack bits.

AMDGPU NBIO 7.9 code uses the corresponding VF0 HDP coherency flush address when setting MMIO remap state for SR-IOV VF operation. The broader VF1/VF2 definitions are present for the same hardware layout even if this source tree's direct C references are mostly to VF0 offsets.

### VF0-VF2 System MMIO Index/Data Registers

Each VF has a small `SYSPFVFDEC` block:

- `MM_INDEX` contains a low MMIO offset and `MM_APER` aperture selector.
- `MM_DATA` contains the data payload.
- `MM_INDEX_HI` contains high MMIO offset bits.

Together these define an indexed access window. The split high/low offset fields are a dependency for any code or firmware path that needs to reach VF MMIO spaces wider than the low index field can encode.

### VF0-VF2 RCC Blocks and MSI-X Table State

The `RCC_DEV0_EPF0_VF0_*`, `VF1_*`, and `VF2_*` blocks expose resource/configuration controller state:

- `RCC_ERR_LOG` records invalid register access in SR-IOV mode and doorbell read access status.
- `RCC_DOORBELL_APER_EN` controls BIF doorbell aperture enable.
- `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration values.
- `RCC_IOV_FUNC_IDENTIFIER` exposes a function identifier and a top-bit `IOV_ENABLE`.
- `GFXMSIX_VECT0..VECT3_ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL` describe four GFX MSI-X vector table entries. Low message addresses are masked from bit 2 upward, preserving PCIe MSI-X alignment.
- `GFXMSIX_PBA` exposes pending bits for MSI-X vectors 0 and 1 in this range.

These fields integrate PCIe interrupt delivery with virtualized graphics functions. Mask-bit definitions in the vector controls are security and reliability relevant because they determine whether a VF can generate interrupts into programmed host addresses.

## Control Flow and State Behavior

This chunk has no executable control flow. The effective runtime flow is in callers that read, compose, and write register values:

1. A caller obtains an address from the matching offset header, often through `SOC15_REG_OFFSET` or `reg*` symbols.
2. It reads a register with an AMDGPU MMIO helper or starts from a zero/local value.
3. It extracts or updates fields using the `__SHIFT` and `_MASK` constants through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. It writes the result back through an AMDGPU register helper or uses the computed offset for an MMIO remap.

The state represented here is hardware-resident and partly guest/host visible:

- PCI configuration-space fields persist in the device's config image across normal software reads and writes and are reset by device/function reset flows.
- Error status registers such as BME, atomic, AER, and RCC error logs are sticky hardware status surfaces with explicit clear bits or write-one-clear style behavior implied by the paired clear/status fields.
- Mailbox valid/ack bits are handshake state between VF, PF, and hypervisor-facing firmware/software. Ordering matters: data words must be coherent with valid/ack transitions.
- HDP flush request/done fields are synchronization state. Software must not treat request bits as complete until matching done bits are observed.
- MSI/MSI-X address/data/control state controls interrupt routing and remains active until rewritten, masked, reset, or disabled through PCI/MSI-X control.

## Dependencies and Integration Points

The main dependencies are generated AMD ASIC register headers:

- `nbio_7_9_0_offset.h` supplies matching `reg*` addresses and base indices for NBIO 7.9.0 registers.
- This `nbio_7_9_0_sh_mask.h` chunk supplies bit encodings for those addresses.
- NBIF offset headers expose matching configuration-space offsets for the VF config images.
- `amdgpu/nbio_v7_9.c` includes this header and uses NBIO masks for register programming, MMIO remap setup, doorbell programming, HDP flush offsets, interrupt control, partition status, and clock/power-management related NBIO state.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes the header alongside NBIO offset and IRQ source headers for NBIO RAS interrupt registration.

Important integration surfaces are PCIe/SR-IOV enumeration, VF BAR and memory decode, host/VF interrupt programming, IOMMU/ATS behavior, HDP coherency, doorbell apertures, mailbox communication, and RAS/error reporting. Because these are preprocessor constants, compile-time success only proves that macro names exist; it does not prove that field values match the hardware specification.

## Risks

- Generated-header drift: any mismatch between these masks and `nbio_7_9_0_offset.h` or the ASIC register specification can silently corrupt field extraction or writes.
- VF isolation risk: command, BAR, BME, doorbell, ATS, ARI, RCC error, and address LUT fields directly affect SR-IOV isolation boundaries and host/VF routing.
- Interrupt routing risk: MSI/MSI-X address/data/control masks must preserve alignment and mask semantics; wrong fields can misroute interrupts or leave vectors unmasked.
- Error handling risk: AER, atomic error, BME status, and RCC error-log masks must distinguish status bits from clear bits. Confusing them can either fail to clear errors or clear diagnostics before they are consumed.
- Coherency risk: HDP flush request/done masks must stay synchronized across engine bits. Missing or shifted done bits can make software observe stale GPU writes or wait on the wrong engine.
- Mailbox protocol risk: transmit/receive valid and ack bits are packed near data fields. Incorrect masks can cause lost messages, duplicate acknowledgements, or unexpected interrupts.
- Chunk-boundary risk: this slice starts mid-VF5 ARI capability and ends just before VF3 BIF definitions. Review or generated-doc tooling must merge adjacent chunks before drawing conclusions about the full source file.

## Test Signals

Useful validation signals for changes touching this generated area include:

- Build coverage for AMDGPU NBIO 7.9 users, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, to catch renamed or missing macros.
- Generated-header consistency checks comparing `*_SHIFTS`, `_MASK` values, and register comments against the authoritative ASIC register database and the matching offset header.
- SR-IOV boot and enumeration tests that create PF/VF configurations and verify VF6/VF7 config-space visibility, ARI routing, ATS advertisement/control, BAR layout, and MSI/MSI-X capability behavior.
- VF interrupt tests that program MSI-X vectors, toggle vector mask bits, and verify pending-bit behavior through the RCC GFXMSIX fields.
- Doorbell and self-ring aperture tests that confirm enable/mode/size/base fields isolate each VF's doorbell aperture.
- HDP coherency tests that issue flush requests for CP and SDMA engines and verify the expected `GPU_HDP_FLUSH_DONE` bits before reading host-visible memory.
- Mailbox tests that exercise transmit/receive data words, valid/ack transitions, and interrupt enable bits across PF/hypervisor/VF paths.
- Error-injection or negative-access tests that trigger BME-low DMA, invalid atomic operations, invalid SR-IOV register accesses, and AER status paths, then verify status and clear-bit behavior.
