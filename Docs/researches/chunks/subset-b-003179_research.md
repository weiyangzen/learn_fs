# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 46432-48774

## Scope

This chunk is a generated AMD NBIO 7.2.0 shift/mask register header slice. It contains preprocessor constants only: no functions, structs, enums, runtime branches, storage, locking, allocation, or persistence code. The range starts in the tail of `nbio_nbif0_rcc_dwn_dev2_RCCPORTDEC`, covers all of `nbio_nbif0_rcc_dwnp_dev2_RCCPORTDEC`, covers a large `nbio_nbif0_bif_misc_bif_misc_regblk` block, and begins `nbio_nbif0_bif_rst_bif_rst_regblk` through the low half of `SELF_SOFT_RST`.

The requested range defines 2,188 macros: 1,098 `__SHIFT` constants and 1,090 `_MASK` constants. Each pair describes how a field is packed into a 32-bit NBIO register. The matching register addresses live in `nbio_7_2_0_offset.h`; this file supplies field positions and masks consumed by AMDGPU register helpers.

## Purpose

NBIO is the GPU northbridge and PCIe-facing I/O block. This chunk documents the bit-level ABI for NBIO PCIe root/downstream/end-point control, BIF miscellaneous datapath controls, PASID/atomic/BME error logs, SMN and SDP virtual-wire behavior, clock/power gating support, timeout detection, credit allocation, BDF mapping, early wakeup, and reset controls.

The common interface shape is:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: mask for extracting or composing that field.

Driver code combines these with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. The header itself does not know whether a field is read-only, write-one-to-clear, sticky, or self-clearing; that behavior is hardware-defined and must be respected by consumers.

## Important Macro Families

The `RCC_DWN_DEV2_DN_PCIE_*` tail exposes downstream dev2 PCIe control fields: hardware-init write lock, unsupported-request reporting disable, LTR-message UR ignore, extended-tag override, FLR extend mode, immediate PMI disable, AER completion-timeout read-only disable, hidden Gen2/Gen3/Gen4 config decode enables, function enable/MC enable/MSI multi-cap straps, clock power-management strap, 64-bit master address strap, and master completion-timeout strap.

The `RCC_DWNP_DEV2_*` block mirrors downstream-port dev2 decode fields for PCIe error reporting, RX error ignore behavior, link-speed straps, link-change/bandwidth notification disables, multifunction strap, and endpoint-originated LTR message info. These constants are integration points for PCIe link capability, error-reporting, and low-power behavior.

The beginning of `bif_misc_regblk` provides global NBIF/BIF control fields: BIOS strap enable, a 32-bit scratch register, per-device interrupt line polarity and enable bytes, DMA/host outstanding virtual-channel allocation, and broad `BIFC_MISC_CTRL0/1` behavior. `BIFC_MISC_CTRL0` includes DMA chain break, host/GSI arbiter locks, split-stall controls, DMA atomic checking controls, VF-as-PF forcing, address phase preservation, PCIe capability protection disable, VC5/VC7 DMA IOCFG disables, second-request disable, port D-state bypass, PME turnoff mode, and SWUS selection. `BIFC_MISC_CTRL1` includes poison/access-violation reporting, GSI/SMN error-response behavior, unsupported SDP command status fields, BME-drop controls for RCC/BIH paths, request attribute masking, base-VC response-credit behavior, completion buffering, and message block-level selection.

The error-log families describe latched fault state plus clear bits:

- `BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG0/1` report DMA or RCC/BIH activity while bus-master enable is low for dev0 functions 0-7, dev1 functions 0-1, and dev2 functions 0-2.
- `BIF_ATOMIC_ERR_LOG_DEV*` records unsupported atomic opcode, request-enable-low, length, and non-relaxed conditions per exposed PCIe function, with matching clear fields.
- `BIF_DMA_MP4_ERR_LOG` reports MP4 SDP VC4 non-DVM and atomic request-enable-low errors.
- `BIF_PASID_ERR_LOG` and `BIF_PASID_ERR_CLR` report and clear PASID errors per exposed function.

The DMA attribute blocks (`BIFC_DMA_ATTR_OVERRIDE_DEV*_F*_F*` and `BIFC_DMA_ATTR_CNTL2_DEV*`) pack per-function override state for IDO, RO, SNR, IDO/non-IDO block level, and IDO bypass controls. The pattern is repeated for dev0 functions 0-7, dev1 functions 0-7, and dev2 functions 0-7 even where other status registers expose a narrower function set.

The BIF datapath and arbitration controls include BME dummy response status, host arbiter mode, GSI SDP/CPL/SMN arbitration modes, completion interleaving, endpoint unsupported-request enablement for several GSI completion sources, SMN parity byte-enable mask, SMN burst and split behavior, PP pipe enable, and HDP FB upper-limit count modes. `BIFC_PCIEFUNC_CNTL` and `BIFC_PCIE_BDF_CNTL0/1` map non-PCIe DMA functions to bus/device/function identifiers.

The PASID and endpoint-function controls include `BIFC_PASID_CHECK_DIS`, `BIFC_PASID_STS`, `EP*_INTR_URGENT_CAP`, and `EP_PEND_BLOCK_MSK`. These fields affect per-function PASID validation, PASID-visible status, interrupt urgency mode, and pending-block masking across endpoint functions.

The SMN/SDP control families configure sideband paths and virtual-wire behavior:

- `SMN_MST_CNTL0/1` and `SMN_MST_EP_CNTL1..5` control SMN arbitration, zero-byte-enable read/write handling, post mask behavior, multi-transaction ID disable, and error-response data forcing for upstream, downstream, and per-endpoint-function paths.
- `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL`, `NBIF_SMN_VWR_VCHG_RST_CTRL0`, `NBIF_SMN_VWR_VCHG_TRIG`, `NBIF_SMN_VWR_WTRIG_CNTL`, and `NBIF_SMN_VWR_VCHG_DIS_CTRL_1` configure SMN virtual-wire disable/reset/default/trigger/difference-detect behavior for sets 0-26.
- `NBIF_SDP_VWR_VCHG_DIS_CTRL`, `NBIF_SDP_VWR_VCHG_RST_CTRL0/1`, and `NBIF_SDP_VWR_VCHG_TRIG` provide similar controls for SDP virtual-wire changes for endpoint functions and `SWDS_P0`.

The performance, power, and low-power groups include BIF performance counter control and low/high count fields for MMIO read/write and DMA read/write counters, NBIF program-master/program-slave power-gating controls, power-gating miscellaneous controls, LCLK medium-grain clock-gating and deep-sleep controls, GMI weighted-round-robin request weights, power-brake request, OBFF emulation interrupt enable, interrupt deassertion behavior in non-D0 states, FLR pending-check disable, and early wakeup controls.

The timeout and credit groups include SHUB timeout detection enable/AER-log/timer/count fields, per-client timeout status/control, sync-flood enablement, HRP SDP read/write response pool-credit allocation, GMI SDP request/data pool-credit allocation, GMI SST read/write response pool-credit allocation, and disconnect hysteresis head controls.

The reset block begins at `HARD_RST_CTRL` and `SELF_SOFT_RST`. `HARD_RST_CTRL` enables hard reset coverage for DSPT/EP config and private reset domains, SDP port reset, SION AON reset, strap reset, SWUS shadow reset, core sticky reset, strap reload, and core reset. `SELF_SOFT_RST` exposes software reset request bits for DSPT0-2 and EP0-2 config/private/sticky domains plus HRPU/GSID/GMIU/GMID SDP port reset, SWUS shadow reset, core sticky reset, strap reload, and core reset. The requested chunk stops before the mask definitions for the final `SELF_SOFT_RST` high bits, so later chunks own the rest of that register and subsequent reset controls.

## Control Flow

There is no executable control flow in this chunk. The runtime flow is imposed by consuming AMDGPU code:

1. ASIC-specific code includes `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`.
2. Code selects register offsets through `SOC15_REG_OFFSET(NBIO, instance, reg...)` or direct SOC15 helpers.
3. Code reads a 32-bit register, modifies fields using the generated masks and shifts, then writes the value back.
4. For status/clear/strobe fields, code must follow hardware sequencing, usually by polling status or writing clear bits after reading latched error state.

The chunk boundaries are artificial. The first macros continue a register family that began before line 46432, and the final line stops inside `SELF_SOFT_RST`; adjacent chunks are required for a complete per-file view.

## State And Persistence Behavior

The header stores no software state. It describes MMIO-backed hardware state in NBIO/BIF.

Configuration-like state includes PCIe error policy, link notification policy, strap overrides, interrupt-line routing, outstanding VC allocation, DMA attributes, PASID checking, SMN/SDP routing behavior, virtual-wire behavior, power-gating and clock-gating options, weighted arbitration, timeout policy, pool-credit allocations, BDF mapping, and reset enablement.

Status-like state includes BME-low logs, atomic error logs, PASID error logs, performance counters, timeout client status, LTR message info, endpoint pending state, and reset/status-related bits. Several log families include explicit `CLEAR_*` fields in the same or companion registers; those should be treated as write-sensitive clear controls rather than ordinary durable configuration.

Persistence is hardware-defined. Values may survive until function-level reset, link reset, PERST, power gating, suspend/resume, core reset, strap reload, or driver reinitialization depending on the register. The reset fields in this chunk are especially stateful because they can destroy or reload other NBIO state.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.2.0 register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h` supplies `reg...` offsets and base indices.
- The wider AMDGPU SOC15 register helper layer supplies `RREG32_*`, `WREG32_*`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Direct include/use sites for the exact header in this tree include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both the offset and shift/mask headers and registers `nbio_v7_2_funcs`. That implementation uses NBIO helpers for HDP flush remapping, revision ID, memory-controller framebuffer access enablement, memory size, SDMA/VCN/IH doorbell ranges, doorbell apertures, interrupt control, BIF medium-grain clock gating, BIF light sleep, clock-gating status, PCIe index/data offsets, initialization, and MMIO remap setup.

The fields in this chunk are mostly lower-level than the actively used paths in `nbio_v7_2.c`; many are available for diagnostics, firmware bring-up, platform workarounds, SR-IOV/PF policy, or future code rather than current direct writes. Discovery selects `nbio_v7_2_funcs` for compatible NBIO hardware in `amdgpu_discovery.c`, while other files under display resources include the matching NBIO offset header for address constants.

## Risks And Edge Cases

- Shift/mask drift is silent at compile time. A wrong mask can modify neighboring hardware fields while all C code still builds.
- Several fields are write-sensitive. Error clear bits, virtual-wire triggers, reset bits, strap reload, core reset, and timeout/sync-flood controls can cause immediate hardware side effects.
- Repeated per-device/per-function families are copy-sensitive. Dev0, dev1, dev2 and F0-F7 layouts look regular, but the exposed function sets differ across error-log and endpoint capability registers.
- SR-IOV and PF/VF semantics are delicate. Fields such as VF-as-PF forcing, BME-drop controls, PASID checks, DMA attributes, BDF mappings, and per-function virtual-wire controls can affect isolation, DMA routing, and guest-visible behavior.
- PCIe error and RX-ignore controls can mask real faults. Disabling AER, ignoring malformed/PASID/LTR/timeout conditions, or altering completion timeout reporting can hide platform or link bugs.
- Power, clock, and reset fields interact with suspend/resume and runtime power management. Programming them while dependent blocks are active can create hangs, lost MMIO state, or resume-only failures.
- Credit allocation, arbitration, and WRR weights can affect forward progress and latency. Bad values may appear as intermittent DMA stalls or timeout detection rather than deterministic failures.

## Test Signals

Useful validation for this generated chunk is a mix of mechanical and hardware testing:

- Build AMDGPU with NBIO 7.2 support enabled; missing or renamed macros should fail where `nbio_v7_2.c` and generated register helpers consume this header.
- Mechanically verify that every field in lines 46432-48774 has a matching `__SHIFT`/`_MASK` pair where expected and that masks match `((width_mask) << shift)` for regular fields.
- Diff against AMD's authoritative NBIO 7.2.0 register database or adjacent generated headers when updating generated sources.
- Exercise PCIe link training, FLR, suspend/resume, runtime power management, AER/error paths, MSI/MSI-X/INTx behavior, and doorbell/interrupt delivery on NBIO 7.2 hardware.
- For diagnostic or bring-up changes touching this range, watch kernel logs and hardware counters for AER events, PASID faults, atomic unsupported-request faults, BME-low logs, SHUB timeouts, sync floods, DMA stalls, stuck pending bits, and reset recovery failures.
- In SR-IOV or virtualization scenarios, test PF and VF DMA isolation, PASID behavior, FLR/reset behavior, BDF mappings, and guest-visible error handling.

## Cross-Chunk Notes

The previous chunk owns the beginning of `RCC_DWN_DEV2_DN_PCIE_CNTL` and earlier endpoint/downstream PCIe registers. The next chunk completes `SELF_SOFT_RST` masks and continues the BIF reset register block, including driver/VPU reset and FLR reset controls. The final per-file report should merge those chunks before making complete claims about NBIO 7.2 reset coverage or all dev2 PCIe decode fields.
