# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 17761-20123

## Scope And Purpose

This chunk is generated AMDGPU NBIF 6.3.1 register bitfield metadata. It contains C preprocessor `*_SHIFT` and `*_MASK` constants only; there are no functions, structs, enums, variables, locks, allocations, or executable control flow in the chunk.

The covered range starts in the middle of `RCC_STRAP1_RCC_BIF_STRAP0`, then defines the rest of the `RCC_STRAP1` and `RCC_DEV0_EPF*` strap fields for the BIF and endpoint functions. It then covers the `nbif_bif_rst_bif_rst_regblk` reset, FLR, D-state, and reset interrupt registers, followed by the `nbif_bif_misc_bif_misc_regblk` ROM, interrupt line, BIFC, PASID, power-gating, SMN, self-ring, INTx, pending, GMI arbitration, power-brake, atomic error, DMA error, and PASID error-log fields.

The purpose is to publish the bit layout for NBIF 6.3.1 registers so driver code can use AMDGPU field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15_PREREG` with matching register offsets from `nbif_6_3_1_offset.h`. The in-tree C consumer is `drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes this header together with the matching offset header. This specific chunk is mostly register surface rather than heavily used C API; the visible direct use from this range is `REGS_ROM_OFFSET_CTRL__ROM_OFFSET` in `nbif_v6_3_1_get_rom_offset()`.

## Important APIs, Types, And Macro Families

There are no runtime APIs or C types declared here. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit position.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.
- These macros are paired with `reg<REGISTER>` offsets and `_BASE_IDX` values in `nbif_6_3_1_offset.h`.

The first major family is NBIF strap metadata. `RCC_STRAP1_RCC_BIF_STRAP0..6` describe hardware/fuse/ROM strap-derived capabilities and policy: PCIe generation disable/kill bits for Gen3/Gen4/Gen5, VGA and BIOS ROM behavior, memory aperture sizing, PX capability, GPUIOV enablement, error-ignore policy, AP/SWUS apertures, DLF/margining/PHY speed enablement, S5 register access, LTR behavior, SMN error response/data forcing, emergency power reduction, power-brake timers, register aperture remapping, DOE version selection, production mode, and register protection behavior.

The endpoint-function strap families define PCI configuration and virtualization-visible capabilities for device 0 functions:

- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*` is the fullest PF0 set. It includes device and revision ID, function enable, D1/D2 support, SR-IOV enable, 64-bit BAR and resize BAR capability, PASID width and PASID feature bits, ARI/AER/ACS/ATS/page-request capabilities, MSI/MSI-X and interrupt pin capability, PME support, FLR enable, atomic operation support, subsystem IDs, doorbell/ROM/IO/memory/register aperture sizing, VF aperture sizing, VGA disable, total VFs, GPUIOV VSEC revision, RTR timing fields, and VF reset timing fields.
- `RCC_STRAP1_RCC_DEV0_EPF1_STRAP*` mirrors the common function capability fields for function 1, including device ID, function enable, D-state support, resize BAR, PASID, AER/ACS/ATS, MSI/MSI-X, FLR, PME, subsystem vendor, and 64-bit aperture enablement.
- `RCC_DEV0_EPF2_STRAP*` and `RCC_DEV0_EPF3_STRAP*` repeat the device/revision/function, PASID, AER/ACS, MSI, FLR/PME, USB DBE select, class code, vendor ID, and auxiliary-current fields for functions 2 and 3.
- `RCC_DEV0_EPF4_STRAP*`, `RCC_DEV0_EPF5_STRAP*`, and `RCC_DEV0_EPF6_STRAP*` are reduced forms covering function enable, D-state support, PASID width/features, AER/ACS, completion-abort/DPA behavior, power/clock/reporting bits, PME/AUX power, and auxiliary-current fields.

The reset block starts at `HARD_RST_CTRL` and contains reset source/control field layouts for hard reset, RSMU soft reset, self soft reset, VPU driver reset, link-reset policy, FLR reset policy, D3hot-to-D0 reset policy, reset interrupts, and D-state values:

- `HARD_RST_CTRL`, `RSMU_SOFT_RST_CTRL`, and `SELF_SOFT_RST` expose DSPT, endpoint, SDP port, SION AON, strap reload, SWUS shadow, sticky/core reset, and self-reset bits.
- `BIF_GFX_DRV_VPU_RST` defines driver-mode PF/VF config/private reset enable bits.
- `BIF_RST_MISC_CTRL`, `BIF_RST_MISC_CTRL2`, and `BIF_RST_MISC_CTRL3` define driver reset mode, auto-clear behavior, link-reset IOV/grace/timer settings, reset protection and idle status, PME turnoff timing, strap reload delays, and RSMU soft reset cycle timing.
- `DEV0_PF0_FLR_RST_CTRL` through `DEV0_PF6_FLR_RST_CTRL` define per-PF FLR reset coverage. PF0 has the broadest set, including PF/VF config/private reset enables, soft PF reset fields, VF-on-VF reset fields, FLR-twice, grace timeout, DMA/HST dummy response status, and PF-copy private reset enable. PF1-PF6 use smaller but aligned field families.
- `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, and `BIF_PF_DSTATE_INTR_STS` publish status bits for instance reset, per-PF FLR, per-PF D3hot-to-D0, PME turnoff/port D-state, and PF D-state interrupts. Matching `*_INTR_MASK` registers define the mask bits.
- `BIF_PF_FLR_RST` exposes write/request bits for PF0-PF6 FLR reset.
- `BIF_DEV0_PF0_DSTATE_VALUE` through `BIF_DEV0_PF6_DSTATE_VALUE` and `BIF_PORT0_DSTATE_VALUE` expose target, acknowledge, and reset-needed D-state fields.
- `BIF_USB_SHUB_RS_RESET_CNTL` links USB SHUB RS reset to FLR or link reset behavior.

The misc block contains lower-level NBIF control, observability, and diagnostics:

- `REGS_ROM_OFFSET_CTRL` contains the `ROM_OFFSET` field read by `nbif_v6_3_1_get_rom_offset()`.
- `NBIF_STRAP_BIOS_CNTL`, `NBIF_STRAP_WRITE_CTRL`, and `MISC_SCRATCH` define BIOS strap override enables, write-once strap control, and a 32-bit scratch field.
- `INTR_LINE_POLARITY` and `INTR_LINE_ENABLE` provide per-device INTx line polarity and enable bitmaps.
- `OUTSTANDING_VC_ALLOC` controls DMA/HST virtual-channel allocation and outstanding thresholds.
- `BIFC_MISC_CTRL0`, `BIFC_MISC_CTRL1`, and `BIFC_MISC_CTRL2` cover a dense set of BIFC behavior: virtual-wire unit-ID checks, active VLINK L0, DMA VC4 non-DVM status, arbitration chain locks, GSI split-stall policy, DMA atomic checks, DMA-as-PF behavior, address phase handling, reset blocking, PCIe capability protection, ATS message blocking, secondary request disable, port D-state/PME modes, BME-drop behavior, poison/ACS violation reporting, SMN worst-error and response-data forcing, GMI request-attribute masking, completion buffer policy, and MMIO decode/protection policy.
- `BIFC_BME_ERR_LOG_LB` and `BIFC_RCCBIH_BME_ERR_LOG0` latch bus-master-enable-low errors for device functions and provide matching clear bits.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `BIFC_DMA_ATTR_OVERRIDE_DEV0_F6_F7` and `BIFC_DMA_ATTR_CNTL2_DEV0` describe DMA attribute override and force-enable fields per function pair.
- `BME_DUMMY_CNTL_0`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, and `BIFC_GSI_CNTL` control dummy completion behavior, THT credit allocation and UR/ECRC overrides, host arbitration, GSI response/request arbitration, SMN parity/burst/split behavior, and HDP flush/read count options.
- `BIFC_PCIEFUNC_CNTL`, `BIFC_PASID_CHECK_DIS`, `BIFC_PASID_STS`, and `BIF_PASID_ERR_LOG` expose PCIe function routing and PASID check/status/error bits for functions 0-6.
- `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, and `BIFC_SDP_CNTL_2` control SDP disconnect hysteresis, disconnect disable policy, non-L0-only behavior, atomic stall policy, and credit allocation override.
- `BIFC_ATHUB_ACT_CNTL` controls ATHUB active response status typing, request drop behavior, and GSI/GMI flush triggers.
- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the four `BIFC_PERF_CNT_*_L32BIT` registers define MMIO and DMA read/write performance-counter enable, reset, event select, and low 32-bit readback fields.
- `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL` define NBIF power-gating, idle hysteresis, firmware power-gating exit behavior, D3-only policy, clock permission bits, refclk timing, and exit override.
- `SMN_MST_EP_CNTL3`, `SMN_MST_EP_CNTL4`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL5` expose per-PF SMN zero-byte read/write enablement and SMN error-response data-all-ones controls.
- `BIF_SELFRING_BUFFER_VID` and `BIF_SELFRING_VECTOR_CNTL` define self-ring client/vector selection for doorbell monitor, RAS controller, ATHUB error event, and interrupt timestamp/source behavior.
- `NBIF_INTX_DSTATE_MISC_CNTL` controls INTx deassertion checks across endpoint/downstream/SWUS D-states and PMI interrupt disable bits.
- `NBIF_PENDING_MISC_CNTL` disables FLR master/slave pending checks.
- `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, and `BIF_GMI_WRR_WEIGHT3` define GMI weighted-round-robin large-request modes and per-entry weights.
- `NBIF_PWRBRK_REQUEST` exposes a single NBIF power-brake request bit.
- `BIF_ATOMIC_ERR_LOG_DEV0_F0` through `BIF_ATOMIC_ERR_LOG_DEV0_F6` latch unsupported-request atomic error classes per function, covering opcode, request-enable-low, length, and non-relaxed-ordering/NR style errors plus matching clear bits.
- `BIF_DMA_MP4_ERR_LOG` latches MP4 SDP VC4 non-DVM and atomic request-enable-low errors plus clear bits.

## Control Flow And Runtime Use

This header chunk has no local control flow. Runtime sequencing is in C files that include the generated NBIF 6.3.1 headers.

The direct C consumer, `amdgpu/nbif_v6_3_1.c`, uses the NBIF 6.3.1 generated headers for NBIO register access. Its visible use from this chunk is:

1. `nbif_v6_3_1_get_rom_offset()` reads `regREGS_ROM_OFFSET_CTRL` with `RREG32_SOC15(NBIO, 0, ...)`.
2. It decodes the value with `REG_GET_FIELD(data, REGS_ROM_OFFSET_CTRL, ROM_OFFSET)`.
3. `REG_GET_FIELD` expands through `REGS_ROM_OFFSET_CTRL__ROM_OFFSET__SHIFT` and `REGS_ROM_OFFSET_CTRL__ROM_OFFSET_MASK` from this chunk.

Other NBIF 6.3.1 runtime code in the same C file programs doorbell apertures, interrupt control, LTR, ASPM, HDP flush, register remap, and RAS error-event interrupts through adjacent generated register families. The reset, strap, BIFC, PASID, perf-counter, power-gating, and error-log fields in this chunk are available to driver, firmware-oriented, diagnostics, or future ASIC support code even where this file does not currently program them directly.

The generated macros also participate in compile-time contracts. `REG_SET_FIELD` and `REG_GET_FIELD` require exact symbol names shaped as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; missing or renamed fields produce compile failures, while wrong values can compile but program or decode the wrong hardware bits.

## State And Persistence Behavior

The chunk itself has no software state or persistence. It describes hardware register state.

Strap fields represent boot-time or fuse/ROM-derived hardware configuration, often mirrored into strap registers. They determine persistent device identity and capability exposure until reset, strap reload, BIOS override, or explicit hardware-supported strap-write path changes them. Fields such as function enablement, SR-IOV enablement, total VFs, BAR sizes, PASID/ATS/ACS/AER capabilities, FLR capability, and GPUIOV policy affect what the PCIe/NBIF device exposes to the OS and to virtual functions.

Reset and D-state fields are stateful hardware controls. Reset request, reset-enable, sticky reset, reload strap, FLR, D3hot-to-D0, link-reset, and interrupt status bits can change during boot, runtime power management, FLR, GPU reset, hot reset, link reset, or suspend/resume. Some fields are command-like or status-like rather than ordinary configuration, especially reset request bits, interrupt status bits, clear bits, and auto-clear controls.

BIFC, PASID, SMN, SDP, GMI, and power-gating fields describe persistent-until-reprogrammed control state plus live status. Examples include arbitration/credit policy, PASID checking, SDP disconnect policy, GMI weights, power-gating hysteresis, clock permissions, and SMN error response behavior. Error-log fields are latch-and-clear hardware state: they preserve diagnostic evidence such as BME-low, atomic UR, PASID, and DMA MP4 errors until cleared through the corresponding clear fields or reset by hardware.

Performance counter fields are measurement state. The enable, reset, event select, and counter readback fields can be updated by diagnostic code and by traffic. The masks do not encode ownership, access type, clear semantics, or read-only/write-one-to-clear behavior, so consumers need the ASIC register spec or established driver sequence before writing these fields.

## Dependencies

This chunk depends on the surrounding AMDGPU NBIF register infrastructure:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h` supplies matching `reg<REGISTER>` offsets and base indices. The offset file contains the matching register addresses for this range, including the `RCC_STRAP1_RCC_BIF_STRAP*` family and `BIF_ATOMIC_ERR_LOG_DEV0_F0`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c` includes this header and uses the generated field macros with SOC15 register helpers. It is selected through `amdgpu_discovery.c` for the matching NBIO/NBIF IP version and exposes `nbif_v6_3_1_funcs` to the wider AMDGPU NBIO layer.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15_PREREG` consume the shift/mask metadata to preserve and manipulate register fields.
- Adjacent chunks of the same header are required for complete per-file understanding. This chunk starts after the opening fields of `RCC_STRAP1_RCC_BIF_STRAP0` and ends before the final fields/masks of `BIF_PASID_ERR_LOG`.

Sibling ASIC headers such as `nbif_6_1_sh_mask.h` and `nbio_7_2_0_sh_mask.h` contain similarly named fields, but they are not interchangeable. Names can look stable across generations while bit positions, field widths, supported functions, or register ownership rules change.

## Integration Points

Primary integration points are:

- NBIF/NBIO bring-up through `nbif_v6_3_1_funcs`, which provides revision ID, memory-size, MC access, doorbell range, clock-gating, interrupt, LTR/ASPM, register-remap, and ROM-offset services to AMDGPU core code.
- PCIe device identity and capability exposure through strap fields: device/vendor/subsystem IDs, class code, function enable, BAR sizing, MSI/MSI-X, FLR, PME, AER/ACS/ATS/PASID/page request, SR-IOV, GPUIOV, and total VF controls.
- Reset and power-management flows through hard/soft/self reset controls, FLR reset controls, D3hot-to-D0 reset controls, link-reset protection, PME turnoff timing, D-state target/ack fields, and power-gating controls.
- Virtualization and isolation paths through SR-IOV strap fields, VF aperture sizing, VF register protection, PASID checking, ATS enablement, GPUIOV fields, per-function atomic/PASID error logging, and BME-low error logs.
- RAS and diagnostics through BIFC error reporting, ATHUB active controls, self-ring interrupt/vector selection, atomic/DMA/PASID error latches, performance counters, SMN error-response policy, and interrupt status/mask fields.
- Performance and liveness tuning through outstanding VC allocation, GSI/HST arbitration, THT credit allocation, SDP disconnect hysteresis, GMI WRR weights, DMA/MMIO counter selection, and reset-protection idle state.

## Risks And Edge Cases

Manual edits are high risk because this is generated hardware metadata. A one-bit error in a mask or shift can silently alter PCIe capability exposure, break FLR/reset sequencing, hide or spuriously report errors, disable PASID/ATS/SR-IOV isolation, or corrupt power-management policy.

The chunk boundaries are artificial. `RCC_STRAP1_RCC_BIF_STRAP0` begins before line 17761, and `BIF_PASID_ERR_LOG` continues after line 20123. The later merge lane must combine adjacent chunks before treating either register family as complete.

Strap fields should not be treated as normal writable configuration. Many strap values are boot/fuse/ROM-derived and may be write-once, BIOS-controlled, or only valid during specific reset/strap reload windows. `NBIF_STRAP_WRITE_CTRL__NBIF_STRAP_WRITE_ONCE_ENABLE` is a strong signal that write ordering and one-time behavior matter.

Reset and FLR fields mix enable, sticky, exception, status, auto-clear, timeout, and request semantics in adjacent bits. Blind read-modify-write can accidentally preserve or clear command/status bits. FLR and D3hot-to-D0 paths are especially sensitive because PF0 has a richer field set than PF1-PF6.

Repeated per-function layouts invite indexing mistakes. Device 0 functions 0-6 share many field names but not identical sets; PF0 includes SR-IOV/VF aperture/RTR fields that later functions lack or reduce. Loop-based code must use the correct register offsets and field names for each function.

Security-sensitive virtualization fields are dense. Wrong PASID, ATS, ACS, SR-IOV, VF register protection, GPUIOV, BME, or VF BAR/aperture masks can expose resources to the wrong function or make the host believe a capability is present when hardware policy does not actually allow it.

Error-log clear fields are destructive. Clearing BME-low, atomic, DMA, or PASID error bits before RAS/debug code samples them can destroy evidence. Conversely, failing to clear latches after handling can cause repeated or stale reports.

Performance, arbitration, SDP, and GMI weight fields can cause plausible but hard-to-debug regressions. Bad values can surface as bandwidth loss, stalled requests, unfair virtual-channel allocation, unexpected completion ordering, timeout symptoms, or reset-protection waits that never drain.

## Test Signals

Useful validation signals include:

- Build coverage for `amdgpu/nbif_v6_3_1.c` with `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h` included. Macro-name drift in this chunk should fail compilation at `REG_GET_FIELD`/`REG_SET_FIELD` call sites.
- Static generated-header checks that every field has both `__SHIFT` and `_MASK`, masks align with shifts and expected widths, and the shift/mask/default/offset headers are generated from the same ASIC register source.
- NBIF bring-up tests on hardware using NBIF 6.3.1, checking revision ID, memory-size readout, ROM offset readout, doorbell aperture setup, HDP flush register access, LTR/ASPM programming, and interrupt routing.
- PCIe capability validation with `lspci` or equivalent, comparing exposed IDs, class code, BAR sizes, MSI/MSI-X, AER/ACS/ATS/PASID, FLR, PME, SR-IOV, and VF counts against expected strap policy.
- Reset tests covering GPU reset, FLR for each exposed PF/VF path, D3hot-to-D0 transitions, link reset, suspend/resume, and strap reload behavior while checking reset interrupt status/mask behavior and D-state target/ack fields.
- SR-IOV and virtualization tests that create/destroy VFs, exercise VF BAR and doorbell access, validate PASID/ATS behavior, and confirm isolation after FLR, D3hot-to-D0, and VF enable/disable transitions.
- RAS and diagnostic tests that intentionally trigger or simulate BME-low, atomic unsupported request, PASID, DMA MP4, SMN, or ATHUB-related errors, verify the corresponding status bits decode correctly, and verify clear bits clear only handled evidence.
- Performance and liveness tests that stress MMIO, DMA read/write, GMI traffic, SDP disconnect/reconnect, and virtual-channel arbitration while checking BIFC performance counters, absence of unexpected error latches, and no reset-protection or pending-check hangs.
