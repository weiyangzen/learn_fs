# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h lines 15164-16653

## Purpose

This chunk is the final section of the generated AMDGPU DCE 10.0 register field mask/shift header. It contains no executable C logic; it publishes compile-time constants that describe packed bit fields in display-controller hardware registers for ASICs using the DCE 10.0 register map.

Each field is represented as a pair of macros:

- `REGISTER__FIELD_MASK` is the already-positioned bit mask.
- `REGISTER__FIELD__SHIFT` is the least-significant bit position for that field.

Driver code uses these constants with register addresses from the matching DCE address header, `dce_10_0_d.h`, and normal AMDGPU register access helpers. This chunk covers the tail of the display interrupt status chain, DCO clock/power/reset and I2C/DDC field layouts, and the XDMA display DMA master/slave register field layouts. The file ends at the `DCE_10_0_SH_MASK_H` include guard footer.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or callbacks in this range. The macro namespace is the API surface consumed by DCE 10.0 display, interrupt, power-management, and diagnostics code.

Major macro groups in this chunk are:

- Display interrupt continuation registers: the range starts in `DISP_INTERRUPT_STATUS_CONTINUE5` and continues through `DISP_INTERRUPT_STATUS_CONTINUE9`. These fields expose CRTC6 timing and trigger interrupts, DIGF/DIGG DisplayPort training and stream-disable interrupts, HPD6/AUX6 interrupts, DCRX/DCCG/DCI/DCO/DCFE/WB performance-counter interrupts, CWB buffer-manager interrupts, AUX1-AUX6 GTC sync lock/error interrupts, and chained continuation bits such as `DISP_INTERRUPT_STATUS_CONTINUE6`, `CONTINUE7`, `CONTINUE8`, and `CONTINUE9`.
- DCO memory, clock, power, and reset controls: `DCO_MEM_PWR_STATUS`, `DCO_MEM_PWR_CTRL`, `DCO_MEM_PWR_CTRL2`, `DCO_CLK_CNTL`, `DCO_CLK_RAMP_CNTL`, `DPDBG_CNTL`, `DPDBG_INTERRUPT`, `DCO_POWER_MANAGEMENT_CNTL`, `DCO_SOFT_RESET`, `DIG_SOFT_RESET`, stereo sync selection, and DCO debug index/data registers.
- Display I2C/DDC controls: `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, per-DDC hardware status for DDC1-DDC6 plus VGA, per-channel speed/setup registers, transaction slots `DC_I2C_TRANSACTION0` through `TRANSACTION3`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, and `DC_I2C_READ_REQUEST_INTERRUPT`.
- Generic I2C controls: `GENERIC_I2C_CONTROL`, `GENERIC_I2C_INTERRUPT_CONTROL`, `GENERIC_I2C_STATUS`, `GENERIC_I2C_SPEED`, `GENERIC_I2C_SETUP`, `GENERIC_I2C_TRANSACTION`, `GENERIC_I2C_DATA`, pin selection, and pin debug fields.
- XDMA global/control fields: `XDMA_MC_PCIE_CLIENT_CONFIG`, local surface tiling, `XDMA_INTERRUPT`, clock-gating control, memory power control, BIF/PCIe interface status, performance measurement status, test/debug index/data, RBBM interface read/write timing, and power-gating sideband registers.
- XDMA master path fields: `XDMA_MSTR_CNTL`, status, memory client configuration, local/remote surface base addresses, local pitch, command and memory urgent controls, PCIe/memory NACK status, vsync/GSL checks, pipe control, read command sizing/prefetch, channel dimensions, active/frame height, remote GPU address, cache base/pitch/TLB power state, channel start, and performance measurement controls.
- XDMA slave path fields: `XDMA_SLV_CNTL`, memory client configuration, SLS pitch/width, read/write urgent controls, writeback rate, read latency min/max/average/timer registers, PCIe/memory NACK status, read-return buffer status, flip pending, channel stop/reset/active controls, and remote GPU address fields.

## Control Flow

This header has no runtime control flow. Every line is a preprocessor definition that becomes useful only when a consumer reads, modifies, or writes a hardware register.

A typical display-register access flow is:

1. Select the register address from `dce_10_0_d.h`, such as a `mmDISP_INTERRUPT_STATUS_CONTINUE*`, `mmDC_I2C_*`, or `mmXDMA_*` register.
2. Read the register through an AMDGPU MMIO helper.
3. Extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert a new value with the same mask/shift pair.
4. Write the register back only if the field is writable and the surrounding display, clock, power, or DMA sequence permits it.

The interrupt continuation fields are normally used as a chain: if the high continuation bit is set in one status register, software must inspect the next status register to find additional pending sources. The macros do not implement the chain; they provide the exact bit positions for the interrupt handler or IRQ source mapping code.

The I2C/DDC and XDMA fields are more sequence-sensitive. I2C consumers program prescale/threshold/setup fields, populate transaction slots, trigger software requests, and poll or handle done/error/status bits. XDMA consumers must sequence master/slave enable, memory-ready, pipe/channel reset, surface address/pitch, urgent thresholds, cache invalidation, flip/GSL, NACK clear, and power-gating fields around display timing and memory-interface state.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes state that lives in DCE hardware registers.

State represented by this range includes pending display interrupt bits, performance-counter interrupt bits, DCO memory power status and transitions, clock/ramp configuration, reset assertion bits for DCO/DIG blocks, stereo sync routing, I2C engine ownership and transaction status, DDC line status, EDID-detect behavior, generic I2C pin routing, XDMA clock and memory power state, XDMA master/slave active/flush/flip state, programmed GPU and surface addresses, urgency thresholds, latency counters, NACK/error latches, and debug index/data selections.

Persistence depends on the underlying register. Some fields are read-only status snapshots, some are sticky interrupt/error bits that require a clear operation, some are writable configuration fields that remain programmed until reset or another driver write, and some reflect transient power-gating, clock-gating, DMA, or I2C transactions. The mask header does not encode access type, reset value, write-one-to-clear behavior, or safe ordering. Consumers must rely on the DCE hardware specification and existing AMDGPU sequencing.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register contract and its matching address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h`. The address header supplies register locations; this `*_sh_mask.h` header supplies bit layouts within those registers.

Direct include points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.c`

The interrupt status field names also integrate with AMD IRQ source metadata under `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, where AUX GTC sync and buffer-manager interrupt sources are associated with `DISP_INTERRUPT_STATUS_CONTINUE6`. Runtime consumers are display interrupt handling, hotplug/AUX handling, display I2C/EDID probing, clock and power-management flows, BACO/suspend-resume handling, display DMA/writeback paths, and low-level debug or register dump tooling.

Although the source tree path is under a local `ceph-client` mirror, this chunk is AMDGPU Linux kernel display-register metadata. It has no Ceph filesystem protocol logic, distributed-storage state, or filesystem persistence behavior.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly while decoding the wrong interrupt source, clearing the wrong status bit, programming the wrong I2C transaction field, or modifying neighboring XDMA control bits.

Interrupt continuation fields are particularly easy to mishandle because the status space is chained across multiple registers. Missing a continuation bit can leave pending interrupts unserviced; treating a continuation bit as a real endpoint can cause spurious handling. Field-name mismatches across CRTC, DIG, HPD, AUX, DCRX, DCCG, DCI, DCO, DCFE, WB, and buffer-manager sources can route an interrupt to the wrong handler.

I2C/DDC fields are sensitive to timing and ownership. Bad speed/setup/threshold values can break EDID reads, DisplayPort AUX-over-DDC paths, or VGA/DDC probing. Incorrect arbitration or software-request handling can wedge the I2C engine, leave transactions incomplete, or race with hardware/autonomous DDC users.

DCO clock, reset, memory-power, and power-management fields affect display block liveness. Incorrect reset or clock-ramp sequencing can leave display encoders, debug paths, or memory sub-blocks in unstable states, especially during modeset, suspend/resume, BACO entry/exit, or runtime power transitions.

XDMA fields carry high blast radius because they include memory client VMID/privilege/swap settings, 40-bit address halves, cache controls, urgent/stall thresholds, pipe/channel active/reset/flush/flip state, NACK clear bits, and latency/performance counters. Wrong field extraction can point DMA at the wrong surface, corrupt display data, mask PCIe/memory NACKs, stall a channel, or misreport performance and power-gating state.

This chunk begins in the middle of `DISP_INTERRUPT_STATUS_CONTINUE5`, so earlier fields for that register live in the previous chunk. It also closes the file, so the final merge should treat the boundary as a chunking artifact and not as a source-level reset of the macro namespace.

## Test Signals

Useful validation signals are mostly build, register-map, and hardware-behavior oriented:

- Kernel build coverage for AMDGPU configurations that include DCE 10.0 display and PowerPlay/SMU/BACO code; malformed or missing macros should produce compile failures in direct consumers.
- Static generated-header validation comparing every `*_MASK` and `*__SHIFT` pair in this range against AMD's register database and the adjacent register addresses in `dce_10_0_d.h`.
- Display IRQ tests that exercise CRTC6 vertical/timing events, HPD6, AUX6, DisplayPort fast-training/stream-disable, AUX GTC sync lock/error, performance-counter interrupts, and chained continuation handling.
- EDID and DDC/I2C tests across DDC1-DDC6 and VGA DDC, including arbitration, software transactions, read-request interrupts, timeout/error handling, and repeated hotplug or modeset cycles.
- Suspend/resume, runtime power-management, and BACO entry/exit tests that confirm DCO reset, DCO clock, memory power, and XDMA power/clock-gating states recover correctly.
- XDMA/display-DMA validation using surface address, pitch, channel dimension, urgent threshold, flip/GSL, cache invalidate, NACK/error, and latency/performance counter paths.
- Register dump or debugfs comparisons that decode raw MMIO values with these masks and verify the resulting fields match expected display hardware state.

Regression symptoms from bad constants include lost or storming display interrupts, hotplug or EDID failures, stuck I2C transactions, black screens after modeset or resume, BACO transition failures, XDMA channel stalls, incorrect remote/local surface addressing, unexpected PCIe or memory NACK behavior, and misleading display performance or power diagnostics.

## Cross-Chunk Notes

Earlier chunks of `dce_10_0_sh_mask.h` define the beginning and middle of the DCE 10.0 display register field namespace, including the first fields of `DISP_INTERRUPT_STATUS_CONTINUE5`. This chunk completes that register family, adds the DCO/I2C/XDMA tail of the file, and ends at the include guard close. The final per-file research document should describe the full header as one generated hardware register layout contract rather than as independent executable modules.
