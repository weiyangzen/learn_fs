# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_sh_mask.h lines 2384-3430

## Scope And Purpose

This chunk is the tail of AMD DCN 2.1 DPCS shift/mask definitions. The file is a generated-style hardware register header: it does not implement runtime logic, allocate state, or call functions. Instead, it defines preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DisplayPort/HDMI DPCS transmitter register fields. These constants are consumed by AMD Display Core register helper macros to construct per-ASIC register tables and to drive `REG_GET`/`REG_UPDATE` style field access.

The selected lines begin in the middle of `RDPCSTX3_RDPCSTX_PHY_CNTL3`, covering masks for TX lane 1 through lane 3 reset/disable/clock-ready/data-enable/request/ack fields. The chunk then completes the `RDPCSTX3` PHY control, fuse, DP-alt, generic-bus, debug, and CR access definitions before defining the full `DPCSTX4` and `RDPCSTX4` register field set and final `DPCSSYS_CR4` address/data fields. It ends with the header guard close.

## Important Definitions

The definitions fall into repeated register families:

- `RDPCSTX3_RDPCSTX_PHY_CNTL3` through `PHY_CNTL17`: per-lane DP PHY control for transmitter instance 3, including lane reset/disable handshakes, term control, invert flags, rate/width, low-power detect, pstate/MPLL enable, DP-alt mode, ref-clock request/enables, MPLL fractional/SSC/divider programming, voltage-regulator bypass, generic input/output buses, and debug source selection.
- `RDPCSTX3_RDPCSTX_PHY_FUSE0` through `PHY_FUSE3`: fuse-derived calibration fields for lane equalization, MPLL charge-pump/current properties, RX reference voltage, DCO tuning/range, TX voltage boost, and supplemental RX VCO reference selection.
- `RDPCSTX3_RDPCSTX_DMCU_DPALT_PHY_CNTL3` and `PHY_CNTL6`: reserved DMCU DP-alt mirrors for the lane reset/disable/clock/data/request/ack and pstate/MPLL/ref-clock fields.
- `RDPCSTX3_RDPCSTX_DPALT_CONTROL_REG`: driver/DMCU access arbitration fields, notably allow-driver-access, driver-access-blocked, and spare control bits.
- `DPCSSYS_CR3_DPCSSYS_CR_ADDR` and `DPCSSYS_CR3_DPCSSYS_CR_DATA`: 16-bit indirect control-register address/data fields for CR instance 3.
- `DPCSTX4_DPCSTX_*`: direct DPCS transmitter instance 4 masks for symbol clock, TX control, CBUS control, interrupt status/masks/clears, PLL update address/data, and debug selection.
- `RDPCSTX4_RDPCSTX_*`: read/display-side DPCS transmitter instance 4 masks for reset, SRAM/FIFO enable, clocking, interrupts, PLL update, CR address/data, SRAM control, scratch/spare, DP-alt block state, debug, PHY controls, fuses, and DP-alt control.
- `DPCSSYS_CR4_DPCSSYS_CR_ADDR` and `DPCSSYS_CR4_DPCSSYS_CR_DATA`: 16-bit indirect control-register address/data fields for CR instance 4.

No C types or functions are declared here. The effective API is the naming convention used by register-table macros. For a field named by a higher-level macro such as `LE_SF(RDPCSTX0_RDPCSTX_PHY_CNTL6, RDPCS_PHY_DPALT_DISABLE, _MASK)`, the preprocessor resolves a concrete constant like `RDPCSTX0_RDPCSTX_PHY_CNTL6__RDPCS_PHY_DPALT_DISABLE_MASK`. The same pattern applies across instances, so the instance-specific `RDPCSTX3` and `RDPCSTX4` constants in this chunk must stay structurally aligned with earlier `RDPCSTX0`-`RDPCSTX2` definitions.

## Control Flow And Runtime Use

This header has no direct control flow. Runtime behavior is introduced when the AMD display resource code includes it with the matching `dpcs_2_1_0_offset.h` header. In DCN 2.1, `dcn21_resource.c` includes both headers and builds `link_enc_regs`, `le_shift`, and `le_mask` tables. `DPCS_DCN21_REG_LIST(id)` maps each link encoder instance to the correct register offsets, while `DPCS_DCN21_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN21_MASK_SH_LIST(_MASK)` materialize the field positions and masks into the link encoder register helper structures.

The field selection comes from link encoder headers. `dcn20_link_encoder.h` names the common DPCS fields for lane readiness, data enable, termination, MPLL programming, FIFO enable, clocks, lane disable/request/ack/reset, and DP-alt mode. `dcn21_link_encoder.h` extends that set with DCN 2.1-specific fuse and regulator fields such as `RDPCS_PHY_TX_VBOOST_LVL`, `RDPCS_PHY_DP_MPLLB_CP_PROP_GS`, `RDPCS_PHY_RX_VREF_CTRL`, `RDPCS_PHY_DP_MPLLB_CP_INT_GS`, `RDPCS_PHY_SUP_PRE_HP`, and per-lane `RDPCS_PHY_DP_TX*_VREGDRV_BYP`.

At runtime, those tables are used by register helper operations in link encoder code. For example, the DCN 2.1 PHY acquisition path reads `RDPCS_PHY_DPALT_DISABLE`, updates `RDPCS_PHY_DPALT_DISABLE_ACK`, and toggles `RDPCS_PHY_DP_REF_CLK_EN` through `RDPCSTX_PHY_CNTL6`. The masks in this chunk provide the same bit layout for transmitter instances 3 and 4 when those encoder instances are selected.

## State And Persistence Behavior

The constants here describe persistent hardware register state, but they do not store software state themselves. The underlying state lives in MMIO or indirect CR/SRAM hardware registers. Writes made through `REG_UPDATE` persist in the display engine until hardware reset, power gating, mode set sequencing, firmware/DMCU ownership changes, or another driver write changes them.

Several fields are handshake or status-like rather than pure configuration:

- Lane fields in `PHY_CNTL3` pair control bits (`RESET`, `DISABLE`, `DATA_EN`, `REQ`) with hardware-visible status/handshake bits (`CLK_RDY`, `ACK`).
- DP-alt fields in `PHY_CNTL6` and `DMCU_DPALT_*` coordinate Type-C/DP-alt ownership with firmware or DMCU paths, including disable, disable-ack, DP4 mode, ref-clock enable, and ref-clock request.
- Interrupt control fields expose sticky status bits and clear/mask controls for FIFO, register FIFO, and DP-alt toggle events.
- Fuse fields expose calibration values that are expected to match silicon-programmed defaults and should generally be treated as hardware-provided tuning inputs.

Because this is a mask header, persistence risks arise from incorrect bit definitions: an incorrect mask can make unrelated bits sticky, clear the wrong interrupt, misprogram PLL state, or break the DP-alt ownership handshake.

## Dependencies And Integration Points

This chunk depends on the matching offset header for register addresses and on the AMD DC register helper conventions that combine register offsets, shifts, and masks. The primary source-tree integration points are:

- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes `dpcs_2_1_0_offset.h` and this mask header and initializes DCN 2.1 link encoder register, shift, and mask tables.
- `drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h`, which defines the DCN 2.1 DPCS mask/shift field list used to populate those tables.
- `drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.h`, which defines the common DPCS field list inherited by DCN 2.1.
- `drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.c`, where runtime PHY acquire/release paths read and update fields such as `RDPCS_PHY_DPALT_DISABLE`, `RDPCS_PHY_DPALT_DISABLE_ACK`, and `RDPCS_PHY_DP_REF_CLK_EN`.

The instance-4 definitions are important because DCN 2.1 resource construction declares five link encoder register sets, mapping `id` values 0 through 4. Any missing or malformed `DPCSTX4`/`RDPCSTX4` field definition can therefore break compilation or silently misconfigure the fifth transmitter.

## Risks And Edge Cases

The main risk is structural drift between instances. The register helper field lists often name fields using instance-0 symbols, then instantiate offsets per encoder. For this pattern to stay correct, `RDPCSTX3` and `RDPCSTX4` masks must mirror the same bit layout as the earlier instances for every shared field. A one-bit difference in lane reset, request/ack, rate/width, or MPLL programming could affect only specific physical connectors and be difficult to isolate.

PLL and spread-spectrum fields are high risk: `MPLLB_FRACN_DEN`, `MPLLB_FRACN_QUOT`, `MPLLB_SSC_PEAK`, `MPLLB_SSC_STEPSIZE`, `MPLLB_MULTIPLIER`, `MPLLB_TX_CLK_DIV`, `MPLLB_STATE`, `MPLLB_FRACN_EN`, and related divider fields control link clock synthesis. Incorrect masks can produce unstable DP link training, wrong pixel clocks, or failures at high link rates.

DP-alt ownership fields are another high-risk area. `RDPCS_PHY_DPALT_DISABLE`, `RDPCS_PHY_DPALT_DISABLE_ACK`, `RDPCS_PHY_DPALT_DP4`, `RDPCS_ALLOW_DRIVER_ACCESS`, and `RDPCS_DRIVER_ACCESS_BLOCKED` coordinate driver access with firmware/DMCU and USB-C alternate mode. Incorrect masks may cause the driver to access PHY registers while blocked or fail to acknowledge ownership transitions.

Generated-header naming is also fragile. Consumer macros depend on exact token concatenation. Renaming a field, changing `_MASK`/`__SHIFT` suffixes, or defining a field only for some instances will surface as compile failures when a selected `LE_SF` expands, or as missing coverage for a physical transmitter if the field is never instantiated.

## Test Signals

The first signal is build coverage for DCN 2.1 display support. Compiling the AMD display driver with `dcn21_resource.c` exercises the token-concatenation contract between register lists and this header. Missing constants for `DPCSTX4`, `RDPCSTX4`, or `DPCSSYS_CR4` should fail at compile time once the relevant register list is expanded.

Runtime signals are hardware/display oriented:

- DP link training and mode-set success across all physical transmitter instances, especially the fifth instance that uses the `*4` definitions.
- USB-C DP-alt acquire/release behavior, including correct `DPALT_DISABLE` and `DPALT_DISABLE_ACK` transitions and ref-clock enable/disable sequencing.
- Stable high-rate DP modes that depend on correct MPLL fractional, spread-spectrum, divider, and pstate fields.
- Absence of FIFO, register FIFO, and DP-alt toggle interrupt storms, and correct clear/mask behavior after display hotplug or mode changes.
- Correct lane enable, clock-ready, data-enable, request, and ack behavior for one-, two-, and four-lane link configurations.

There are no local unit tests for this header alone. The meaningful validation comes from compile-time macro expansion, AMD display driver bring-up, connector hotplug/mode-set tests, DP link-training logs, and hardware register readback when debugging specific PHY or DP-alt failures.
