# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h lines 2429-4642

## Purpose

This chunk is generated AMD NBIO 7.0 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic NBIO, BIF, PCIe, IOMMU, GDC, RCC, Syshub, and MSI-X register names to numeric offsets. Most `mm...` register offsets have a matching `mm..._BASE_IDX` selector, which is consumed by SOC15 register helpers to choose the correct base-address segment before adding the offset.

The requested range starts at the tail of `cfgBIFPLR0_0` PCIe capability offsets, then covers complete repeated PCIe root-port configuration blocks `cfgBIFPLR1_0` through `cfgBIFPLR6_0`, debug-port windows, IOMMU L2 MMIO registers, NBIF/SYS decode windows, RCC/PCIe endpoint and downstream control registers, BIF mailbox and doorbell registers, GDC registers, graphics MSI-X table offsets, and Syshub indirect-register offsets. It ends at the file's `#endif`.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, or runtime branches in this range. The exported interface is the generated macro namespace:

- `cfg...`: PCI configuration-space offsets for NBIO PCIe root-port/root-complex style functions. These are byte offsets within configuration-space-like decode blocks and generally do not have `_BASE_IDX` companions in this chunk.
- `mm...`: MMIO register offsets for NBIO/BIF/IOMMU/RCC/GDC blocks.
- `mm..._BASE_IDX`: base-table selector paired with an `mm...` offset. SOC15 helpers use it as `adev->reg_offset[NBIO_HWIP][inst][reg_BASE_IDX] + reg`.
- `ix...`: indirect Syshub register indices written through `mmSYSHUB_INDEX` and read or written through `mmSYSHUB_DATA`.

The requested lines contain 2,122 `#define` entries: 1,085 `cfg...` macros, 968 `mm...` or `mm..._BASE_IDX` macros, 69 `ix...` macros, and 484 `_BASE_IDX` definitions.

Major address blocks in the chunk:

- `nbio_pcie0_bifplr1_cfgdecp` through `nbio_pcie0_bifplr6_cfgdecp`: six repeated PCIe port configuration maps. Each complete block has 169 offsets, from vendor/device/command/status fields through PCIe, MSI, SSID, MSI-map, vendor-specific, virtual-channel, serial-number, AER, lane equalization, ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM capability areas.
- `nbio_dbgu0_dbgudec`: debug port address/data windows for ports A through D, including low/high address and data halves.
- `nbio_iohub_iommu_l2mmio_l2mmiocfg`: IOMMU L2 MMIO control, command, event, PPR, GA-log, device-table, completion-wait, MSI, error log, interrupt status, perf counter, and counter reporting offsets.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`, `SYSDEC`, and `syshubdec`: MM index/data windows, Syshub index/data windows, scratch, protection-fault aperture, remap, coherency-flush, interrupt, KIQ, semaphore, scratch, and MMIO-reg CAM offsets.
- `nbio_nbif0_rcc_*`: RCC strap, endpoint PCIe scratch/status/control, downstream PCIe error/LTR/control, function identifier, error interrupt, doorbell aperture, MSI-X, memory size, BIF framebuffer enable, PCIe index/data, and memory-hub arbitration offsets.
- `nbio_nbif0_bif_bx_pf_BIFDEC1` and `BIFPFVFDEC1`: BIF indirect access, doorbell aperture and range, remap HDP flush controls, interrupt controls, VM-ID request, ring-buffer, mailbox, GPUIOV configuration-size, pad-control, BME/atomic error, self-ring GPA aperture, HDP coherency flush, GPU HDP flush request/done, transaction-pending, mailbox buffer/control/interrupt, and VM/hypervisor mailbox offsets.
- `nbio_nbif0_gdc_GDCDEC`: NGDC/SHUB interface controls, SDMA/IH/MMSCH doorbell ranges, ATDMA/S2A/GDC miscellaneous and power-gating controls.
- `nbio_nbif0_rcc_dev0_BIFDEC2`: graphics MSI-X vector table entries and pending-bit array offsets.
- `syshub_mmreg_ind_syshubind`: indirect Syshub indices for SOC/shub clock domains, QoS/class controls, clock gating, idle/status, scratch/mask, and NIC400 fabric function-modifier registers.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMDGPU consumers:

1. ASIC-specific code includes `nbio_7_0_offset.h` with `nbio_7_0_sh_mask.h`, `nbio_7_0_default.h`, and `nbio_7_0_smn.h`.
2. Code calls helpers such as `SOC15_REG_OFFSET(NBIO, 0, mmBIF_SDMA0_DOORBELL_RANGE)`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG32_NO_KIQ`, and `WREG32_NO_KIQ`.
3. The helper combines the generated offset with `adev->reg_offset[NBIO_HWIP][instance][*_BASE_IDX]`.
4. Driver logic then performs read-modify-write, polling, or command submission against the resulting MMIO address.

The most direct in-tree consumer is `amdgpu/nbio_v7_0.c`. It uses offsets from this chunk to program SDMA, VCN/MMSCH, and IH doorbell ranges; expose HDP flush request/done offsets to GFX and SDMA command streams; read/write Syshub indirect registers for medium-grain clock gating; configure HDP remap registers; set interrupt controls; and derive the PCIe index/data offsets.

SR-IOV mailbox paths are another integration point. `amdgpu/mxgpu_ai.c` and `amdgpu/mxgpu_ai.h` use NBIO mailbox offsets such as `mmBIF_BX_PF0_MAILBOX_MSGBUF_TRN_DW*`, `mmBIF_BX_PF0_MAILBOX_MSGBUF_RCV_DW*`, and `mmBIF_BX_PF0_MAILBOX_CONTROL` through `SOC15_REG_OFFSET` and no-KIQ MMIO access to exchange requests, acknowledgements, initialization data, reset notifications, and checksum keys between VF and PF.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware-backed state:

- PCIe configuration and capability state for repeated NBIO PCIe port instances, including link/device status, MSI/MSI-map state, AER logs, lane equalization, ACS, multicast, L1 PM substates, DPC status, RP PIO logs, and ESM registers.
- IOMMU L2 state for device-table and command buffers, event/PPR/GA logs, MSI addresses/data, completion-wait behavior, error logging, invalidation, page-request handling, and performance counters.
- BIF/NBIO apertures and coherency controls, including doorbell apertures/ranges, self-ring GPA aperture, HDP memory/register coherency flush controls, GPU HDP flush request/done bits, transaction-pending status, and framebuffer access enablement.
- Interrupt and IH-related state, including interrupt dummy-read controls, MSI-X table entries, graphics MSI-X pending bits, BIF/RCC error interrupt controls, and mailbox interrupt controls.
- SR-IOV and PF/VF communication state in BIF mailbox transmit/receive buffers, mailbox valid/ack control bits, VM/hypervisor mailbox, BME status, GPUIOV configuration-size registers, and function-identifier registers.
- Syshub fabric, QoS, clock-gating, idle, scratch, class-mask, and NIC400 function-modifier state addressed indirectly through `mmSYSHUB_INDEX`/`mmSYSHUB_DATA`.

Persistence is hardware-defined. Configuration fields generally last until reset, suspend/resume reinitialization, power-gating loss, or driver reprogramming. Status, interrupt, error-log, flush, mailbox valid/ack, and transaction-pending registers may be sticky, self-clearing, write-one-to-clear, read-only, or command-like. This offset header does not encode those access semantics; the companion shift/mask/default headers and consuming driver code provide the operational behavior.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h`, which provides field shifts and masks for many offsets in this range.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`, which provides reset/default values for the same register namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h`, which supplies related SMN addresses.
- SOC15 base-address setup in `adev->reg_offset`, consumed by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and related macros in `amdgpu/soc15_common.h`.

Important in-tree consumers and behavioral links include:

- `amdgpu/nbio_v7_0.c`: NBIO 7.0 operation table, doorbell ranges, HDP flush offsets, Syshub indirect read/write, clock gating, light sleep, IH controls, HDP remap, memory-controller access, and revision/memory-size reads.
- `amdgpu/soc15.c`: includes the NBIO 7.0 generated headers during SOC15 initialization and IP setup.
- `amdgpu/mxgpu_ai.c` and `amdgpu/mxgpu_ai.h`: SR-IOV VF/PF mailbox protocol over BIF mailbox registers.
- GFX and SDMA ring code: indirectly consumes `nbio_v7_0_get_hdp_flush_req_offset`, `nbio_v7_0_get_hdp_flush_done_offset`, and `nbio_v7_0_hdp_flush_reg` to emit HDP flush commands.
- SDMA, VCN/JPEG, UMSCH/MMSCH, and IH setup paths: call `adev->nbio.funcs->sdma_doorbell_range`, `vcn_doorbell_range`, and `ih_doorbell_range`, which rely on `mmBIF_SDMA0_DOORBELL_RANGE`, `mmBIF_SDMA1_DOORBELL_RANGE`, `mmBIF_MMSCH0_DOORBELL_RANGE`, and `mmBIF_IH_DOORBELL_RANGE`.

## Risks And Edge Cases

- Offset or `_BASE_IDX` drift is the central risk. These are untyped preprocessor constants, so a wrong numeric value can compile cleanly while targeting the wrong NBIO segment or register.
- The chunk contains highly repeated PCIe root-port config blocks. A generator or manual-edit error in only one `cfgBIFPLR<n>_0_*` family may surface only on one port, link width, hotplug path, AER/DPC event, or SR-IOV/IOMMU topology.
- `cfg...` offsets and `mm...` offsets are different addressing domains. Treating configuration-space-style offsets like SOC15 MMIO offsets, or vice versa, can silently address the wrong hardware path.
- Doorbell range registers are security- and routing-sensitive. Incorrect offset/base selection can assign SDMA, IH, or MMSCH doorbells to the wrong aperture, break queue notification, or expose a VF/PF isolation issue.
- HDP flush registers are ordering-sensitive. Wrong `mmGPU_HDP_FLUSH_REQ` or `mmGPU_HDP_FLUSH_DONE` offsets can leave CPU-visible memory stale, hang ring flush waits, or cause intermittent coherency bugs.
- SR-IOV mailbox offsets are protocol-sensitive. Misaddressed mailbox transmit/receive/control registers can cause lost PF/VF acknowledgements, failed GPU init/fini/reset access, stale checksum data, or FLR/reset timeouts.
- Syshub indirect offsets are used through an index/data window. Code must not treat `ixSYSHUB_MMREG_IND_*` values as direct SOC15 MMIO offsets; they are payloads written to `mmSYSHUB_INDEX`.
- IOMMU L2, interrupt, and error-log offsets touch platform-visible isolation and fault-reporting state. Incorrect values can mask translation faults, misroute MSI/PPR/event logs, or make page-request/error paths appear healthy when they are not.
- The range begins in the middle of `cfgBIFPLR0_0` and ends at the file terminator. Adjacent earlier chunks are required for the complete NBIO 7.0 offset map.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU with SOC15/NBIO 7.0 support enabled. Missing or renamed macros should fail in `nbio_v7_0.c`, `soc15.c`, MXGPU AI mailbox code, and ring/doorbell setup paths.
- Mechanically verify that every `mm...` register macro in lines 2429-4642 has the expected `_BASE_IDX` companion where this generated namespace requires one, and that the paired base-index values match AMD's authoritative NBIO 7.0 register database.
- Diff the repeated `cfgBIFPLR1_0` through `cfgBIFPLR6_0` blocks for structural consistency against each other and against the adjacent `cfgBIFPLR0_0` block from the previous chunk.
- Exercise SDMA, VCN/MMSCH, and IH doorbells: queue submission, interrupt delivery, ring idle/drain, suspend/resume, reset recovery, and doorbell disable/re-enable paths.
- Validate HDP flush behavior through GFX and SDMA rings: CPU/GPU memory coherency tests, command-stream flush waits, reset recovery, and workloads that rely on host reads after GPU writes.
- On SR-IOV-capable hardware, test VF init/fini/reset access requests, PF/VF mailbox acknowledgements, FLR notifications, checksum retrieval, mailbox interrupts, and timeout/error logging.
- Exercise IOMMU and PCIe error paths where possible: AER/DPC reporting, PPR/event-log traffic, MSI/MSI-X programming, link retraining/equalization diagnostics, and hotplug or link-state transitions.
- Toggle clock-gating/light-sleep policy and verify Syshub MGCG register updates through `mmSYSHUB_INDEX`/`mmSYSHUB_DATA`, idle-state reporting, and resume behavior.
- Watch kernel logs for doorbell misrouting, HDP flush timeouts, mailbox timeout messages, IOMMU fault-log anomalies, AER/DPC storms, interrupt delivery failures, and resume/reset regressions.

## Cross-Chunk Notes

This is a late chunk of `nbio_7_0_offset.h`. Earlier chunks cover the header opening and the beginning of NBIO, IOMMU configuration-space, and `cfgBIFPLR0_0` definitions. The final per-file research document should merge this chunk with adjacent chunks before making complete claims about all NBIO 7.0 address blocks or the full PCIe/IOMMU/NBIO register namespace.
