# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_1_sh_mask.h lines 2922-5619

## Scope

This chunk is part of AMDGPU's generated NBIF 6.1 register bitfield header. It contains C preprocessor constants only: `__SHIFT` definitions in the first part of the chunk and, beginning later in the chunk, matching `_MASK` definitions for many of the same PCIe/NBIF register fields. There are no functions, structs, enums, allocations, locks, or executable control flow here. Runtime behavior is supplied by AMDGPU code that includes `nbio/nbio_6_1_sh_mask.h` together with the companion address/default headers and then uses helpers such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15`.

The line range starts at the tail of `BIF_ATOMIC_ERR_LOG` shift definitions and ends inside the mask definitions for PCIe resizable/enhanced BAR capability registers. Neighboring chunks are needed for the complete file-level view.

## Purpose

The chunk documents the bit layout for NBIF 6.1 host-interface and PCIe configuration registers used by the AMD GPU driver. Its main purpose is to let driver code compose and decode 32-bit hardware register values without hard-coded bit numbers. The covered registers span doorbell apertures, HDP coherency flush handshakes, mailbox signaling, PF/VF and SR-IOV identification, strap-driven PCIe capability exposure, reset and power-state interrupts, BME error logging, DMA attribute overrides, LTR/PME/sticky restore, MSI-X table entries, syshub indirect controls, clock/deep-sleep/QoS settings, and PCIe extended capability masks.

Although the repository path is under a Ceph client source tree, this file is Linux AMDGPU hardware-description data for GPU PCIe/NBIF programming.

## Important Macro Families

`DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `DOORBELL_SELFRING_GPA_APER_BASE_LOW`, and `DOORBELL_SELFRING_GPA_APER_CNTL` define the self-ring doorbell aperture base and control fields. The control register exposes the aperture enable bit and size field in this chunk. In the NBIO 6.1 implementation, `nbio_v6_1_enable_doorbell_selfring_aperture()` writes the low/high base from `adev->doorbell.base` and sets the control fields through `REG_SET_FIELD`.

`HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, and `GPU_HDP_FLUSH_DONE` describe the HDP coherency flush protocol. Request and done bits are provided for command processor engines `CP0`-`CP9` and `SDMA0`/`SDMA1`. `nbio_v6_1_get_hdp_flush_req_offset()`, `nbio_v6_1_get_hdp_flush_done_offset()`, and `nbio_v6_1_hdp_flush_reg` integrate these fields with the common AMDGPU HDP flush path.

`BIF_TRANS_PENDING` exposes master and slave transaction-pending bits. Driver reset, suspend, or error recovery paths can use this kind of status to avoid resetting NBIF while outstanding host transactions remain.

`MAILBOX_MSGBUF_TRN_DW*`, `MAILBOX_MSGBUF_RCV_DW*`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX` define simple host/firmware or VM/hypervisor mailbox data, valid, acknowledge, and interrupt-enable fields. The `BIF_VMHV_MAILBOX` register packs transmit/receive data nibbles, valid bits, ack bits, and interrupt enables into one register.

`RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER` cover PF/VF-facing RCC fields. They provide the global doorbell aperture enable, configured memory size, reserved config data, function identifier, and IOV enable state. `nbio_v6_1_get_memsize()` reads the corresponding memsize register, and `nbio_v6_1_enable_doorbell_aperture()` writes the aperture enable field.

`SYSHUB_INDEX` and `SYSHUB_DATA` define the indirect syshub MMREG access pair. Later `SYSHUBMMREGIND_*` families in this chunk define fields reached through that indirect aperture.

The `RCCSTRAPRCCSTRAP_RCC_DEV*_PORT_STRAP*` families define root/downstream port strap fields for device 0 and device 1. They encode PCIe capability exposure such as ARI, ACS, AER, ECRC generation/check, extended tags, VC count, Gen2/Gen3 enablement, target link speed, L0s/L1 latencies, LTR, OBFF, MSI, atomic operations, power-management support, power budget data, port number, bus/device/function identity, and ACS forwarding/redirect policy. These are strap-level hardware defaults rather than normal dynamic driver state.

The `RCC*_EPF*_STRAP*` families define endpoint physical-function strap fields for functions 0-7. They repeat per-function identity and capability fields: device ID, major/minor/ATI revision ID, function enable, legacy device type, D1/D2 support, 64-bit BAR and resizable BAR support, MSI/MSI-X support, ARI/AER/ACS/ATS, DPA, DSN, VC, page request, PASID, FLR, PME, interrupt pin, auxiliary power, subsystem IDs, aperture enable/prefetchability/size, ROM aperture, class code, and function-specific selectors such as SATA/USB fields. `nbio_v6_1_get_rev_id()` reads the PF0 strap revision ID via these shift/mask constants.

`DEV0_PF*_FLR_RST_CTRL`, `BIF_PF_FLR_INTR_*`, `BIF_PF0_VF_FLR_INTR_*`, `BIF_PF_FLR_RST`, and `BIF_PF0_VF_FLR_RST` describe function-level reset handling for PF0-PF7 and VF0-VF15 under PF0. The fields include PF config/private reset enable, sticky retention controls, FLR grace mode and timeout, dummy response status selections, interrupt status, masks, and reset request bits.

`BIF_DEV0_PF*_DSTATE_VALUE`, `DEV0_PF*_D3HOTD0_RST_CTRL`, `BIF_D3HOTD0_INTR_*`, `BIF_POWER_INTR_*`, `BIF_PF_DSTATE_INTR_*`, and `BIF_PORT0_DSTATE_VALUE` define PCI power-state target/acknowledge tracking, D3hot-to-D0 reset controls, PME turn-off and D-state interrupt status/masks, and port D-state state machine fields.

`MISC_SCRATCH`, `INTR_LINE_POLARITY`, `INTR_LINE_ENABLE`, `OUTSTANDING_VC_ALLOC`, `BIFC_MISC_CTRL0`, and `BIFC_MISC_CTRL1` cover miscellaneous NBIF behavior: scratch storage, legacy interrupt line polarity/enable, DMA/host outstanding virtual-channel allocation, chain locking, atomic length checking, PCIe capability protection, port D-state bypass, PME turn-off mode, poison/ACS violation reporting, unsupported command status, ordering overrides, and BME drop behavior.

`BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG` provide per-function bus-master-enable violation status and matching clear bits. These can signal DMA or RCC/BIH activity while PCI command BME is low for functions 0-7.

`BIFC_DMA_ATTR_OVERRIDE_DEV0_F*_F*` groups provide per-function DMA transaction attribute overrides for ID-based ordering, relaxed ordering, and snoop/no-snoop request attributes across posted and non-posted traffic. These fields can materially change ordering and cache-coherency behavior for PCIe transactions.

`RCCPFCAMDGFXAZ_RCC_PFC_*` covers port-function-controller behavior: LTR snoop/non-snoop latency values and scales, PME enable/status restore, sticky restore for selected AER error status and TLP header/prefix log fields, and auxiliary-power override/detection fields.

`PCIEMSIX_VECT0` through `PCIEMSIX_VECT31` define MSI-X table entry fields for 32 vectors: message address low/high, message data, and per-vector mask bit. `PCIEMSIX_PBA` defines pending bits for the MSI-X pending-bit array.

`SYSHUBMMREGIND_*` covers syshub indirect registers for SOCCLK and SHUBCLK deep-sleep allowance, deep-sleep timers, BGEN enhancement bypass/immediate enable, DMA QoS control, client controls, read/write WRR weights, clock gating, transaction idle status for PF and VF0-VF15, scratch, and high-priority timer fields.

The final section in this chunk switches to `_MASK` definitions for PCIe capability registers. It includes vendor-specific extended capability list/header/scratch fields, virtual channel capability/control/status/resource fields, device serial number fields, Advanced Error Reporting status/mask/severity/control/header log/root error/source ID/TLP prefix log fields, and enhanced BAR capability/control masks for BAR1-BAR3 before the chunk ends.

## Control Flow and State

This header has no direct control flow. The implicit hardware workflows encoded by the fields are:

1. Initialization code reads strap registers to identify revision, enabled functions, endpoint/port capabilities, BAR shape, interrupt support, and virtualization features.
2. Doorbell setup code enables the global doorbell aperture, optionally programs the self-ring GPA aperture base low/high, and writes the aperture control register.
3. HDP flush users write request bits for CP or SDMA engines and poll or compare the matching done bits using the masks exported through `nbio_v6_1_hdp_flush_reg`.
4. Power-management and reset paths inspect D-state, PME, FLR, link-reset, and transaction-pending status, mask/unmask the corresponding interrupts, and write reset control bits when needed.
5. Virtualization/SR-IOV code can rely on PF/VF function ID, VF FLR, VF transaction-idle, MSI-X, ATS/PASID/page-request, aperture, and IOV enable fields to manage per-function isolation and reset.
6. Error-handling and diagnostics code can read AER, BME error logs, sticky restore fields, TLP header/prefix logs, and PCIe root error status/source fields.

Register state persists in hardware until reset, power transition, firmware action, or a later driver write changes it. Strap fields are generally sampled hardware defaults and should be treated as platform/ASIC configuration. Interrupt status, reset request, mailbox valid/ack, error-log clear, performance/QoS override, and HDP flush request/done bits are stateful protocol fields whose ordering and clear semantics must be handled by callers.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor and the hardware register naming convention. It is normally paired with `nbio_6_1_offset.h`, `nbio_6_1_default.h`, and `nbio_6_1_smn.h` for register addresses/defaults and SMN addresses.

The primary in-tree integration is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio/nbio_6_1_sh_mask.h`. That implementation uses these macros for revision-ID extraction, memsize/doorbell aperture handling, self-ring aperture programming, HDP flush register offsets/masks, interrupt/clock/power setup, ASPM/LTR programming, and NBIO function registration through `nbio_v6_1_funcs`.

The macro names also match patterns used by neighboring NBIO/NBIF versions (`nbio_v2_3.c`, `nbio_v7_0.c`, `nbio_v7_2.c`, `nbio_v7_11.c`, `nbif_v6_3_1.c`). That makes this header part of a generated register ABI: the driver code expects stable `REG__FIELD__SHIFT` and `REG__FIELD_MASK` names across ASIC revisions where the same hardware concept exists.

Broader integration points include AMDGPU PCIe/NBIO setup, KFD MMIO remapping for HDP flush controls, GPU scheduler/ring code that needs HDP flushes, interrupt handling through MSI/MSI-X and IH doorbells, SR-IOV/virtualization reset flows, PCIe AER diagnostics, and power-management paths for ASPM/LTR/PME/deep-sleep controls.

## Risks

Bitfield errors are high impact because callers use these constants to write hardware registers directly. A wrong shift or mask can enable the wrong doorbell aperture, miss an HDP flush completion, expose or hide PCIe capabilities incorrectly, corrupt PF/VF reset handling, or misprogram PCIe ordering/coherency attributes.

The strap and function families are extremely repetitive. Generation or copy mistakes around function suffixes (`F0`-`F7`), virtual functions (`VF0`-`VF15`), and port/device prefixes can compile cleanly while targeting the wrong function or capability bit.

Fields controlling ACS, ATS, PASID, page requests, MSI/MSI-X, VF aperture sizing, IOV enablement, and FLR affect isolation and virtualization correctness. Incorrect use can break SR-IOV guests, leak access across functions, or leave stale DMA state after reset.

The DMA attribute override and BME drop/error-log fields affect PCIe transaction ordering, snooping, and legal DMA behavior. Bad values may surface only under load as data corruption, timeouts, or platform-specific hangs.

HDP flush request/done bits are used to enforce host-data-path coherency. If the CP/SDMA bit mapping is wrong or callers poll the wrong mask, command streams can observe stale memory.

MSI-X table and PBA fields are architecturally sensitive. Incorrect address/data/mask handling can lose interrupts, deliver them to the wrong vector, or leave vectors masked.

This chunk boundary starts after the beginning of `BIF_ATOMIC_ERR_LOG` and ends before the complete enhanced BAR mask family. Final reconciliation must include adjacent chunks before drawing conclusions about complete register groups.

## Test and Validation Signals

Useful validation is mostly build and integration based:

- Compile AMDGPU with NBIO 6.1 support; missing or renamed macros should fail where `nbio_v6_1.c` and shared register helpers use them.
- Boot on NBIO 6.1 hardware and verify `nbio_v6_1_get_rev_id()` reports the expected revision from `RCC_DEV0_EPF0_STRAP0`.
- Exercise doorbell initialization and ring submission; failures often appear as queues that do not ring, IH/SDMA doorbells not firing, or GPU hangs after self-ring aperture changes.
- Run command processor and SDMA workloads that force HDP flushes and confirm the request/done bits for CP0-CP9 and SDMA0-SDMA1 complete reliably.
- Test suspend/resume, D3hot-to-D0, FLR, and GPU reset paths while checking PF/VF reset interrupts, D-state target/ack fields, transaction-pending bits, and PME status.
- Validate SR-IOV guests for VF FLR, VF transaction-idle reporting, MSI-X delivery, aperture sizing, ATS/PASID/page-request capabilities, and isolation after guest reset.
- Check PCIe AER and BME diagnostics under injected or naturally occurring errors; the expected status, mask, severity, header log, source ID, and clear bits should behave according to PCIe semantics.
- Use register readback/debugfs traces to verify LTR, PME restore, syshub deep-sleep, clock-gating, QoS, and DMA attribute override writes land in the expected bit positions.

## Cross-Chunk Notes

This report covers only lines 2922-5619. Earlier chunks contain the first part of the NBIF 6.1 shift definitions, including the start of `BIF_ATOMIC_ERR_LOG` and many PCIe configuration fields. Later chunks should contain the remainder of the PCIe BAR/enhanced capability masks and subsequent NBIF mask definitions. The final per-file research document should merge those adjacent chunks before claiming complete coverage of any register family that crosses this boundary.
