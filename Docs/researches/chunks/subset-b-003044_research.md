# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 96301-98889

## Purpose

This chunk is part of AMDGPU's generated NBIO 6.1 shift/mask header. It describes bitfield geometry for the `DWC_E12MP_PHY_X4_NS_X4_2` pipe/PCS PHY register namespace: common-domain memory rows, common PLL override registers, and the first lane control/status registers for raw PCS/PMA/FSM logic.

The range starts inside the `RAWCMN_DIG_MEM_CMN5` table at `B0_R13`, continues through the rest of `CMN5` and almost all of `CMN6`, then defines common-domain control and MPLLA/MPLLB bandwidth/spread-spectrum override fields. It then covers all lane 0 raw digital PCS, FSM, always-on adaptation, IRQ, PMA transfer, TX control, and RX control fields visible in this namespace, followed by the beginning of the lane 1 PCS/FSM block through the shift definitions for `RAWLANE1_DIG_FSM_FAST_RX_VCO_CAL`. The next lines after the chunk contain the paired masks for that final lane 1 register and then continue into lane 1 common-calibration and always-on fields, so the chunk boundary splits one register definition.

This header is hardware metadata, not executable logic. Its job is to provide `__SHIFT` and `_MASK` constants used by AMDGPU register access helpers to compose writes and decode reads for NBIO/DXIO PHY registers.

## Important APIs, Types, and Macros

There are no C functions, structs, typedefs, or enums in this chunk. The interface is entirely preprocessor constants named as:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field inside the register.
- `<REGISTER>__<FIELD>_MASK`: field mask at its encoded position.

The chunk contains 1,957 `#define` rows: 979 shift definitions and 989 mask definitions. The mask/shift imbalance is caused by artificial chunk boundaries: the first line is a mask for `RAWCMN_DIG_MEM_CMN5_B0_R12`, whose shift is in the previous chunk, and the range ends after the two shift lines for `RAWLANE1_DIG_FSM_FAST_RX_VCO_CAL`, whose masks are on lines 98890-98891 outside this chunk.

Important register families in this range include:

- `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMN_DIG_MEM_CMN5_B0_R13` through `CMN5_B7_R31`: 16-bit common-domain memory/register rows. Each complete row exposes a single `DATA` field at shift `0x0` with mask `0xFFFFL`.
- `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMN_DIG_MEM_CMN6_B0_R0` through `CMN6_B6_R31`: the next common memory table, with the same full-width `DATA` layout. The rest of `CMN6` is outside this range.
- `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMN_DIG_CMN_CTL`: a common PHY functional reset bit, `PHY_FUNC_RST`, plus reserved high bits.
- `RAWCMN_DIG_MPLLA_*` and `RAWCMN_DIG_MPLLB_*`: common PLL override controls. The fields include bandwidth override value/enable, SSC range, fractional-N control, SSC clock select, SSC control override enable, and SSC enable override value/enable.
- `RAWLANE0_DIG_PCS_XF_TX_*` and `RAWLANE0_DIG_PCS_XF_RX_*`: lane 0 PCS transfer-interface fields for TX/RX request, reset, P-state, low-power detect, width, rate, MPLL select/enable, master MPLL state, receiver VCO/reference load values, adaptation request/continuous mode, equalizer settings, and override handshake/status.
- `RAWLANE0_DIG_FSM_*`: lane 0 FSM override/control and monitor fields. These include jump address and command-start controls, state/status monitor bits, fast RX calibration/adaptation flags, fast TX common-mode/RX-detect/power-up/VCO flags, and common-calibration status.
- `RAWLANE0_DIG_AON_*`: always-on lane 0 analog/adaptation values, including AFE/DFE IDAC/VDAC offsets, RX phase adjustment, MPLL coarse tuning, RTUNE readbacks, initial power-up done status, RX adaptation outputs, slicer control, common-calibration status, and generic adaptation control registers.
- `RAWLANE0_DIG_IRQ_CTL_*`: per-lane IRQ status, clear, reset-return request, and mask bits for RX reset, request, rate, P-state, adaptation request, and adaptation disable events.
- `RAWLANE0_DIG_PMA_XF_*`: PMA-facing override/status fields for lane MPLL enable, supervisor state, TX/RX request/reset handshake, and lane RTUNE request.
- `RAWLANE0_DIG_TX_CTL_*` and `RAWLANE0_DIG_RX_CTL_*`: controller knobs for TX FSM timing/RX-detect allowance, TX clock enable/select, RX FSM enable, rate-change behavior, loss-of-signal mask timing, RX data-enable override timing, and continuous OFFCAN/adaptation status.
- `RAWLANE1_DIG_PCS_XF_*` and `RAWLANE1_DIG_FSM_*`: the beginning of the lane 1 copy of the same PCS/FSM pattern, present through the `FAST_RX_VCO_CAL` shift rows.

The constants are normally consumed through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related NBIO/DXIO access wrappers. Address or SMN selection comes from companion generated headers, while this file supplies only bit positions and masks.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. Including it gives the compiler symbolic constants for bit manipulation. Runtime behavior happens in the caller that reads or writes the corresponding NBIO PHY register.

The implied hardware flow is lane bring-up and PHY tuning:

1. Common memory rows hold raw 16-bit PHY microcode/configuration data for common-domain blocks.
2. `RAWCMN_DIG_CMN_CTL` can assert a common PHY functional reset.
3. MPLLA/MPLLB override registers can force PLL bandwidth or spread-spectrum behavior when their enable bits are set.
4. PCS transfer-interface registers describe TX/RX request/reset/rate/width/P-state handshakes and override paths between PCS control and the raw lane.
5. FSM registers expose lane state-machine override, command execution, status monitors, and shortcuts for fast calibration/adaptation stages.
6. AON and PMA fields report or override analog adaptation, RTUNE, slicer, and lane power/clock/reset handshakes.
7. IRQ status/clear/mask fields surface asynchronous RX-state and adaptation events to the surrounding hardware/driver path.

Because this is a generated mask header, the "control flow" risk is indirect: the driver will follow the hardware control sequence encoded elsewhere, and these constants determine whether each register access targets the intended bits.

## State and Persistence

The header owns no state, allocates no memory, performs no I/O, and persists nothing. The state described by the constants is hardware state inside the NBIO 6.1 PHY/PCS block.

State classes represented here include:

- Persistent or semi-persistent hardware configuration fields, such as common memory `DATA` rows, PLL bandwidth/SSC override values, adaptation control registers, and TX/RX controller timing knobs.
- Momentary control bits, such as functional reset, override enable bits, FSM command-start, lane RTUNE request, and IRQ clear bits.
- Hardware status/readback fields, such as PCS/PMA acknowledge bits, DETRX result, FSM state and ALU/wait flags, calibration done/init status, RX adaptation results, RTUNE values, power-up done, continuous adaptation/OFFCAN status, and IRQ status bits.

Reset values and retention semantics are not defined in this header. The companion `nbio_6_1_default.h` provides default values for the same register names, and actual persistence across reset, suspend/resume, or GPU reset is controlled by the NBIO/DXIO hardware and AMDGPU initialization code.

## Dependencies and Integration Points

Primary companion generated headers are:

- `nbio_6_1_offset.h` and/or `nbio_6_1_smn.h` for register addresses and base indices.
- `nbio_6_1_default.h` for reset/default values. The same namespace includes defaults such as `smnDWC_E12MP_PHY_X4_NS_X4_2_RAWCMN_DIG_MEM_CMN5_B0_R13_DEFAULT` and lane defaults such as `smnDWC_E12MP_PHY_X4_NS_X4_2_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN_DEFAULT`.
- Adjacent chunks of `nbio_6_1_sh_mask.h`, which complete boundary-split registers and the rest of the repeated lane/common-memory tables.

In-tree include sites for this header include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`
- `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`

The specific fields in this chunk integrate with NBIO/DXIO PHY bring-up, link training, power management, clock/PLL setup, receiver calibration/adaptation, RTUNE handling, and hardware debug/diagnostic flows. The `RAWLANE0` and `RAWLANE1` repetition also matters for multi-lane links: lane 0 is mostly complete in this chunk, while lane 1 starts here and continues in the next chunk.

## Risks

- Generated-header drift is the main risk. A wrong mask or shift silently makes register helper macros read, preserve, or update the wrong hardware bits.
- The chunk starts and ends on split definitions. The first row is a mask whose shift is in the prior chunk, and the final `RAWLANE1_DIG_FSM_FAST_RX_VCO_CAL` masks are outside this range. Any validator must account for those boundary artifacts.
- The common memory tables are highly repetitive full-width 16-bit rows. They are easy to compare mechanically, but a single omitted row or wrong bank/register suffix would misalign generated metadata with hardware documentation.
- PLL and PHY override fields are sensitive. Incorrect enable/value masks for MPLLA/MPLLB bandwidth or SSC controls could affect link stability, spread-spectrum behavior, or compliance characteristics.
- Lane PCS/PMA handshake fields mix writable override controls with hardware status bits. Treating status fields as ordinary writable control fields, or failing to preserve reserved bits, can perturb lane bring-up.
- IRQ clear and mask bits use single-bit fields with similar names. Confusing `*_IRQ`, `*_IRQ_CLR`, and `*_IRQ_MSK` definitions can leave events uncleared, masked unintentionally, or repeatedly signaled.
- Repeated lane 0/lane 1 definitions invite copy/paste mistakes. Lane 1 should mirror lane 0 for the covered PCS/FSM subset except for the lane number embedded in the macro names and any documented lane-specific hardware differences.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware integration:

- Kernel build coverage with AMDGPU NBIO 6.1 users enabled catches missing, renamed, or syntactically invalid macros.
- Mechanical checks should verify that every complete register in lines 96301-98889 has paired `__SHIFT` and `_MASK` definitions, while allowing the known split at the first and last registers.
- Cross-header checks should compare register names in this chunk against `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h` so masks, addresses, and defaults stay aligned.
- Repetition checks should confirm the `RAWCMN_DIG_MEM_CMN5`/`CMN6` rows are contiguous, use `DATA` shift `0x0`, and use mask `0xFFFFL` for every complete row.
- Lane symmetry checks should compare lane 0 PCS/FSM fields against the lane 1 subset present in this chunk, ignoring only the lane number in macro names and the artificial chunk ending.
- Hardware smoke tests on affected ASICs should exercise NBIO/DXIO PHY initialization, PCIe/link training, PLL/SSC setup, power-state transitions, RX adaptation/calibration, IRQ delivery/clearing/masking, and GPU reset/resume paths.
- Debug validation can read back PCS/PMA/FSM status registers and confirm decoded fields such as ACK, DETRX result, FSM state, calibration done, RTUNE values, adaptation done, and IRQ status match expected hardware behavior.

## Chunk Boundary Notes

The previous chunk owns the start of `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMN_DIG_MEM_CMN5_B0_R12` and the first part of `CMN5_B0`. This chunk begins with `CMN5_B0_R12__DATA_MASK`, then covers `CMN5_B0_R13` onward. The next chunk owns the masks for `DWC_E12MP_PHY_X4_NS_X4_2_RAWLANE1_DIG_FSM_FAST_RX_VCO_CAL` and continues the rest of lane 1. The final per-file research document should merge these adjacent chunks before making whole-header claims about complete common-memory or lane coverage.
