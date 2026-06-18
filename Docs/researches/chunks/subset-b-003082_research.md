# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 34188-36634

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,142 `#define` lines across 2,447 source lines: 1,070 `__SHIFT` constants, 1,072 `_MASK` constants, 275 register/address-block comment markers, and no C functions, structs, enums, executable statements, allocations, or locks.

The range starts mid-register with the remaining mask definitions for `BIF_BX_PF0_MM_CFGREGS_CNTL`; the corresponding shift definitions and early masks are in the previous chunk. It then covers BIF PF0 control and status fields, doorbell and HDP apertures, mailbox fields, PCI configuration shadow registers, endpoint/downstream PCIe port control fields for devices 0 and 1, RCC strap/SUM indirect registers, BIF miscellaneous and virtual-wire controls, clock/power-gating/performance-counter fields, GMI arbitration and completion-buffer controls, and the beginning of several RCC PFC decode blocks. The range ends after the first `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL__SNOOP_LATENCY_VALUE__SHIFT` line, so the rest of the USB3_0 PFC LTR register continues in the next chunk.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register contract. For each hardware field, it exposes:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position used to encode or decode a field.
- `<REGISTER>__<FIELD>_MASK`, the register mask used to isolate, preserve, or update the field.

The companion generated NBIO 7.0 headers provide the other pieces of the same contract: `nbio_7_0_offset.h` for register offsets, `nbio_7_0_smn.h` for SMN addresses, and `nbio_7_0_default.h` for reset/default values. Runtime AMDGPU code combines these constants with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and related NBIO accessors. This chunk does not implement policy; it names the bits that NBIO, PCIe, interrupt, doorbell, SR-IOV, power-management, and RAS paths can program or decode.

## Important Macro Families

The first group continues BIF PF0 register layouts:

- `BIF_BX_PF0_MM_CFGREGS_CNTL` provides masks for function/device selection and enabling writes through the MM-to-config path.
- `BIF_BX_PF0_BX_RESET_CNTL` exposes `LINK_TRAIN_EN`, which affects link training control.
- `BIF_BX_PF0_INTERRUPT_CNTL` and `BIF_BX_PF0_INTERRUPT_CNTL2` define interrupt-handler dummy-read behavior, non-snoop attributes, interrupt delay counter fields, generic IH interrupt enable, MSI dummy-read bypass behavior, and the dummy-read address.
- `BIF_BX_PF0_CLKREQB_PAD_CNTL`, `BIF_BX_PF0_BIF_PERSTB_PAD_CNTL`, `BIF_BX_PF0_BIF_PX_EN_PAD_CNTL`, `BIF_BX_PF0_BIF_REFPADKIN_PAD_CNTL`, and `BIF_BX_PF0_BIF_CLKREQB_PAD_CNTL` define pad mux/mode/spare/slew/wake/schmitt/control-enable/output fields for PCIe sideband pins.
- `BIF_BX_PF0_BIF_FEATURES_CONTROL_MISC` exposes endpoint request/completion disable bits, ring-buffer overflow behavior, atomic error interrupt disable, non-virtual BME handling, FLR pending-check controls, and a 48-bit self-ring doorbell aperture check bit.
- `BIF_BX_PF0_BIF_DOORBELL_CNTL`, `BIF_BX_PF0_BIF_DOORBELL_INT_CNTL`, `BIF_BX_PF0_BIF_DOORBELL_GBLAPER1_*`, `BIF_BX_PF0_BIF_DOORBELL_GBLAPER2_*`, and `BIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_*` define doorbell translation checks, self-ring behavior, monitor interrupt mode, doorbell/IOHC RAS interrupt status and clears, global aperture lower/upper bounds, and self-ring GPA aperture base/control fields.
- `BIF_BX_PF0_BIF_FB_EN`, `BIF_BX_PF0_BIF_BUSY_DELAY_CNTR`, `BIF_BX_PF0_BIF_MST_TRANS_PENDING_VF`, `BIF_BX_PF0_BIF_SLV_TRANS_PENDING_VF`, and `BIF_BX_PF0_BIF_TRANS_PENDING` describe framebuffer read/write enables, busy-delay counter fields, and master/slave transaction-pending status across VFs and PF-level paths.
- `BIF_BX_PF0_BACO_CNTL` and `BIF_BX_PF0_BIF_BACO_EXIT_TIME0` through `BIF_BX_PF0_BIF_BACO_EXIT_TIMER4` define BACO entry/exit controls, timers, auto-exit behavior, LCLK switching, dummy enable, power-off, sideband timers, hardware auto flush, PX_EN output-enable behavior, and mode selection.
- `BIF_BX_PF0_MEM_TYPE_CNTL`, `BIF_BX_PF0_SMU_BIF_VDDGFX_PWR_STATUS`, `BIF_BX_PF0_BIF_VDDGFX_GFX0_*` through `GFX5_*`, `RSV1_*` through `RSV4_*`, and `BIF_BX_PF0_BIF_VDDGFX_FB_CMP` describe memory-phy selection, VDDGFX power-off status, address lower/upper comparison windows, compare enables, stall enables, and framebuffer compare fields.

The PF/VF mailbox and GPU-IOV groups provide virtualization-facing bit layouts:

- `BIF_BX_PF0_BIF_UVD_GPUIOV_CFG_SIZE`, `BIF_BX_PF0_BIF_VCE_GPUIOV_CFG_SIZE`, and `BIF_BX_PF0_BIF_GFX_SDMA_GPUIOV_CFG_SIZE` hold base/size fields for GPU-IOV configuration regions.
- `BIF_BX_PF0_MAILBOX_INDEX` selects mailbox DW indexing.
- `BIF_BX_PF0_MAILBOX_MSGBUF_TRN_DW0` through `_DW3` and `BIF_BX_PF0_MAILBOX_MSGBUF_RCV_DW0` through `_DW3` define transmit and receive message-buffer data words.
- `BIF_BX_PF0_MAILBOX_CONTROL` defines transmit valid, receive ack, and valid/ack interrupt status/control fields.
- `BIF_BX_PF0_MAILBOX_INT_CNTL` exposes valid and ack interrupt enables.
- `BIF_BX_PF0_BIF_VMHV_MAILBOX` defines a compact VM/HV mailbox with transmit/receive message data, valid/ack flags, and interrupt enables.

The `nbio_nbif0_rcc_shadow_reg_shadowdec` address block mirrors PCI configuration-space shadow fields:

- `SHADOW_COMMAND` tracks upstream IO and memory enable bits.
- `SHADOW_BASE_ADDR_1`, `SHADOW_BASE_ADDR_2`, `SHADOW_SUB_BUS_NUMBER_LATENCY`, `SHADOW_IO_BASE_LIMIT`, `SHADOW_MEM_BASE_LIMIT`, `SHADOW_PREF_BASE_LIMIT`, `SHADOW_PREF_BASE_UPPER`, `SHADOW_PREF_LIMIT_UPPER`, `SHADOW_IO_BASE_LIMIT_HI`, and `SHADOW_IRQ_BRIDGE_CNTL` define BAR, bus-number, IO/memory/prefetchable-window, VGA/ISA decode, and secondary-bus reset fields.
- `SUC_INDEX` and `SUC_DATA` provide an indexed register/data pair for shadow/SUC access.

The RCC endpoint and downstream port blocks describe PCIe port control and error behavior:

- `RCC_EP_DEV0_1_*` and `RCC_EP_DEV1_*` endpoint registers include scratch fields, unsupported-request reporting controls, malformed atomic handling, interrupt enables/status bits for correctable/non-fatal/fatal/user/misc/power-state events, invalid-PASID ignore behavior, immediate PMI disable, hidden config decode enables, TX LTR controls, DPA capability/latency/control/substate power allocation, PME service timer, TX SNR/RO/TPH fields, requester ID composition, AER header-log timeout/expired bits, error-message control, RX ignore controls for payload/TC/prefix/PASID/TPH/completion timeout, and Gen2/Gen3 speed strap fields.
- `RCC_DWN_DEV0_1_*` and `RCC_DWN_DEV1_*` downstream registers include reserved/scratch fields, hardware-init write lock, unsupported-request reporting disable, LTR-message UR ignore, extended tag override, FLR extend mode, immediate PMI disable, AER completion timeout read-only behavior, and hidden config decode enables.
- `RCC_DWNP_DEV0_1_*` and `RCC_DWNP_DEV1_*` downstream-port registers define error reporting, AER header-log timeout/status, immediate error message send, RX ignore controls, RCB FLR timeout disable, Gen2/Gen3 link speed strap fields, link-bandwidth notification disable, multi-function strap, and received endpoint LTR message information.
- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP0` exposes dev0 EP function strap fields, while `SUM_INDEX` and `SUM_DATA` provide another indexed register/data pair in the BIF PF summary decoder.

The `nbio_nbif0_bif_misc_bif_misc_regblk` address block covers miscellaneous NBIF/BIF control:

- `MISC_SCRATCH`, `INTR_LINE_POLARITY`, `INTR_LINE_ENABLE`, and `OUTSTANDING_VC_ALLOC` provide scratch, interrupt-line polarity/enable, and virtual-channel allocation fields.
- `BIFC_MISC_CTRL0`, `BIFC_MISC_CTRL1`, `BIFC_BME_ERR_LOG`, and `BIFC_RCCBIH_BME_ERR_LOG` define BIF-side control and bus-master-enable error logging/clear bits across dev0/dev1 functions.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `DEV0_F6_F7` and `BIFC_DMA_ATTR_OVERRIDE_DEV1_F0_F1` through `DEV1_F6_F7` define per-function posted/non-posted DMA attribute overrides for IDO, relaxed ordering, and snoop/no-snoop behavior.
- `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL`, `NBIF_SMN_VWR_VCHG_RST_CTRL0`, `NBIF_SMN_VWR_VCHG_TRIG`, `NBIF_SMN_VWR_WTRIG_CNTL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL_1`, `NBIF_SDP_VWR_VCHG_DIS_CTRL`, `NBIF_SDP_VWR_VCHG_RST_CTRL0`, `NBIF_SDP_VWR_VCHG_RST_CTRL1`, and `NBIF_SDP_VWR_VCHG_TRIG` define virtual-wire reset delays, posted/block-level behavior, voltage-change set disable/reset-default/trigger bits, and write-trigger controls.
- `NBIF_MGCG_CTRL_LCLK`, `NBIF_DS_CTRL_LCLK`, `BME_DUMMY_CNTL_0`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, `NBIF_REGIF_ERRSET_CTRL`, `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL` define LCLK clock-gating/deep-sleep controls, BME dummy behavior, throttle/host arbitration/GSI/PCIe function controls, SDP controls, register-interface error-set behavior, and master/slave/misc power-gating bits.
- `SMN_MST_CNTL0`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL1` through `SMN_MST_EP_CNTL5` define SMN master/endpoint control fields.
- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, `BIFC_PERF_CNT_MMIO_RD`, `BIFC_PERF_CNT_MMIO_WR`, `BIFC_PERF_CNT_DMA_RD`, and `BIFC_PERF_CNT_DMA_WR` expose BIF performance-counter control and count fields for MMIO and DMA read/write traffic.
- `BIF_SELFRING_BUFFER_VID`, `BIF_SELFRING_VECTOR_CNTL`, `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_CPLBUF_WR_CTRL`, and `BIF_GMI_CPLBUF_RD_CTRL` define self-ring buffer/vector fields, GMI weighted-round-robin request weights/mode, and completion-buffer reservation controls per VC.

The RCC PFC blocks at the end repeat a compact per-function controller layout:

- `RCC_PFC_AMDGFX_*`, `RCC_PFC_AMDGFXAZ_*`, and `RCC_PFC_PSP_*` define LTR snoop/non-snoop latency value/scale/requirement fields, PME restore enable/status, sticky PCIe error-status restore bits, restored TLP header/prefix DWs, and auxiliary-power override fields.
- `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL` starts at the chunk boundary with `SNOOP_LATENCY_VALUE__SHIFT`; the remaining USB3_0 PFC fields are outside this chunk.

## APIs, Types, And Functions

There are no callable APIs or local C types in this range. The public interface is the generated macro namespace. Consumers depend on the exact spelling and value of each register/field shift and mask.

The constants are untyped preprocessor integer literals. Masks generally use an `L` suffix and range from byte/word-sized fields to full `0xFFFFFFFFL` register fields. They encode field placement only. They do not describe access permissions, reset domains, polling delays, side effects, clear-on-write behavior, hardware ownership, firmware ownership, or whether a field is configuration, command, sticky status, latched status, or reserved. Those semantics must come from the hardware specification and the AMDGPU call site using the macros.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. AMDGPU code selects an NBIO/SMN/PCIe register address from `nbio_7_0_offset.h` or `nbio_7_0_smn.h`.
2. The code reads the register, decodes fields with these `__SHIFT`/`_MASK` constants, or composes an updated value with register-field helpers.
3. The resulting value is written back to hardware, used to poll status, used to clear latched interrupt/error state, or used as input to PCIe, doorbell, interrupt, power-management, SR-IOV, or RAS policy.

Likely runtime flows involving these field families include NBIO initialization, PCIe link training and speed/hidden-config setup, interrupt routing through IH/MSI paths, HDP flush/coherency handling, doorbell aperture programming, BACO entry/exit, VDDGFX power gating and address-stall comparison, PF/VF mailbox exchange, GPU-IOV aperture configuration, PCIe endpoint/downstream error handling, AER/status restoration after power events, virtual-wire voltage-change signaling, LCLK clock gating/deep sleep, BIF performance sampling, and GMI arbitration tuning.

## State And Persistence Behavior

The header itself stores no state. It names NBIO 7.0 hardware-visible state. Persistence is determined by the hardware reset domain, BACO and power-gating transitions, SMU/firmware/BIOS initialization, driver suspend/resume restore, SR-IOV PF/VF ownership, and explicit register writes.

Represented state includes interrupt dummy-read policy, doorbell and self-ring aperture bounds, FB read/write enables, BIF transaction-pending status, BACO timers and mode bits, VDDGFX power/status and address compare windows, HDP coherency/flush controls, mailbox transmit/receive buffers and valid/ack flags, PCI config shadow windows, PCIe endpoint/downstream error enables/status/ignore controls, DPA/PME/LTR fields, BME error logs and clear bits, per-function DMA attribute overrides, virtual-wire voltage-change triggers, clock-gating and power-gating controls, performance counter values, GMI WRR weights, PFC sticky restore state, and PFC restored TLP header/prefix fields.

Several fields are not passive storage. Link-training, interrupt-enable, interrupt-clear, doorbell aperture, BACO, VDDGFX stall, HDP flush, mailbox valid/ack, AER error, BME clear, virtual-wire trigger, clock/power-gating, performance-counter control, and LTR/PME fields can directly affect live device behavior or observable OS/firmware state. Full-register writes should preserve unrelated and reserved fields unless the hardware sequence explicitly requires a literal value.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register database and must stay aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`

Direct include users in this source tree include `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, and NBIO 7.x runtime code such as `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` uses the same generated-register pattern for HDP remap, memory-controller access, doorbells, interrupt control, clock gating, light sleep, PCIe index/data accessors, register initialization, and register remapping. RAS code for newer NBIO 7.x revisions uses related NBIO register infrastructure for controller and error-event interrupts.

Although this repository path is under a `ceph-client` source tree, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem logic.

## Risks And Edge Cases

- Generated shift/mask drift can compile successfully while making the driver program or decode the wrong NBIO bits. The most sensitive fields in this chunk affect link training, interrupts, doorbell apertures, HDP flush/coherency, BACO, VDDGFX power gating, mailbox handshakes, PCIe error handling, virtual-wire triggers, and clock/power gating.
- The chunk starts mid-register at `BIF_BX_PF0_MM_CFGREGS_CNTL` masks and ends mid-register-family at `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL`; adjacent chunks are required for complete per-register coverage.
- Many register families are repeated by device, function pair, or endpoint/downstream block. Repetition is intentional, but a single field-width mismatch between `DEV0` and `DEV1` or between endpoint/downstream variants may indicate generator or register-database drift.
- Mailbox valid/ack and interrupt status/clear bits can be edge-sensitive or handshake-sensitive. Incorrect masks can cause lost PF/VF messages, stuck interrupts, or virtualization deadlocks.
- Doorbell and self-ring aperture fields define address acceptance and translation behavior. Wrong bounds or enable/check bits can route writes to the wrong engine, block valid queues, or expose an aperture beyond the intended range.
- BACO and VDDGFX fields control live power transitions. Incorrect timer, auto-exit, power-off, stall, or compare-window programming can break suspend/resume, reset, or low-power idle transitions.
- PCIe error mask/ignore fields can hide real protocol errors or generate error storms. AER header-log and sticky restore fields may be latched, clear-on-write, or firmware-managed.
- Virtual-wire voltage-change trigger/reset fields and clock/power-gating controls can interact with SMU/firmware sequencing; read-modify-write preservation is important for unrelated sets and reserved bits.

## Test Signals

- Build AMDGPU with NBIO 7.0/SMU10 support enabled. Direct macro users catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: offset/default/shift/mask name alignment, mask-width validation, non-overlap checks within each register, and repetition checks across device/function variants.
- Validate adjacent chunk boundaries: `BIF_BX_PF0_MM_CFGREGS_CNTL` should become complete with the previous chunk, and `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL` should continue cleanly in the next chunk.
- On NBIO 7.0 hardware, boot tests should show stable PCIe link training, correct negotiated width/speed, no unexpected AER storms, working interrupts, and functional doorbell-backed queues.
- Runtime suspend/resume, BACO, and reset tests should verify doorbell aperture restore, HDP flush/coherency behavior, BACO exit timing, VDDGFX status/compare behavior, and PCIe endpoint/downstream status restoration.
- SR-IOV smoke tests should exercise PF/VF mailbox valid/ack interrupts, GPU-IOV configuration sizes, per-function DMA attribute overrides, and transaction-pending status.
- RAS/error-injection or lab diagnostics should confirm BME error logs/clear bits, PCIe AER header-log fields, PFC sticky restore fields, and doorbell/IOHC RAS interrupt status/clear behavior.
- Power-management validation should cover LCLK MGCG/deep-sleep controls, virtual-wire voltage-change triggers, SMN/SDP virtual-wire reset behavior, and performance-counter readout stability.
