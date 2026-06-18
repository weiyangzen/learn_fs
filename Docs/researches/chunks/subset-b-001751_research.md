# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 1-2451

## Scope And Purpose

This chunk is the opening portion of the generated DCN 3.0.2 register shift/mask header used by the AMDGPU display driver. It does not implement executable logic; it declares preprocessor constants that describe bit positions and bit masks for memory-mapped display registers. Those constants are the ABI between DCN 3.0.2 C code and the hardware register layout.

The file begins with AMD's permissive license and the `_dcn_3_0_2_SH_MASK_HEADER` include guard, then defines register-field macros in the local naming pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask, usually as a `L`-suffixed integer literal.

The requested range covers several display blocks: legacy VGA/MMHUBBUB display decode, DCCG clock generation and clock gating, DCCG performance counters, RBBM interface timeout reporting, DMU display power gating, DMU/DC performance counters, DMU miscellaneous clock/memory controls, and the beginning of DMCU microcontroller control and interrupt status. Later chunks continue the same generated register catalog.

## Important Macro Groups

The first address block, `dce_dc_mmhubbub_vga_dispdec`, describes legacy VGA decode and memory aperture behavior. It includes VGA page address registers, render and mode control, sequencer reset behavior, pitch/height selection, memory base/high address fields, HDP/cache controls, per-display `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status/interrupt/clear registers, VGA test/QoS controls, and indexed legacy VGA register data ports such as CRTC, sequencer, graphics, DAC, attribute, and generic feature/miscellaneous registers.

The VGA macros are used to preserve or alter narrow bitfields without disturbing adjacent hardware state. Examples include `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_MASK`, VGA memory access status and interrupt bits, and per-pipe mode enable/timing/sync/rotation fields. The later source search shows older AMDGPU DCE paths also use the shared `VGA_RENDER_CONTROL` field names when manipulating VGA status behavior, which illustrates why these generated masks must match the real register layout exactly.

The `dce_dc_dccg_dccg_dispdec` block describes display clock generation. It includes PHY PLL pixel clock resync/enable/deep-color fields for PHYPLLA through PHYPLLE, DP DTO enable bits, DSC and DPP DTO phase/modulo fields, REFCLK/DPREFCLK selection and CGTT delays, DISPCLK frequency ramp/error-detection controls, display memory global power request disable, GTC and DS DTO counters, microsecond/millisecond time-base dividers, clock gate-disable registers, symbolic clock enable/force controls, soft-reset bits, audio DTO selection and phase/module registers, OTG pixel-rate controls for OTG0 through OTG4, and VSYNC latch/counter/interrupt controls for OTG0 through OTG5.

The DCCG macros expose repeated lane or instance patterns. For example, `OTGx_PIXEL_RATE_CNTL` fields select the pixel-rate source, enable a matching `DP_DTOx`, request add/drop pixel adjustment, enable half-rate output, and report DIO FIFO error/count bits. `DPPCLKx_DTO_PARAM` and `DSCCLKx_DTO_PARAM` provide phase/modulo fields, while `DPPCLK_DTO_CTRL` and `DSCCLK_DTO_CTRL` enable individual DTOs and their double-buffering. These constants feed clock programming code that needs exact field composition to avoid unstable link, stream, or compressor clocks.

The `dce_dc_dccg_dccg_dfs_dispdec` block contributes `DENTIST_DISPCLK_CNTL`, including DISPCLK and DPPCLK divider fields plus change-toggle/done bits. This is a synchronization point for clock divider changes: software writes divider and toggle fields and observes done fields.

The `dce_dc_dccg_dccg_dcperfmon0_dc_perfmon_dispdec` and `dcperfmon1` blocks define two DCCG performance monitor instances. Each instance has the same structure: `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, current-value low/high, and readback high/low registers. The fields select events, counted value type, increment mode, hardware start/stop sources, counter-off behavior, interrupt enable/status/ack, state reporting for counters 0-7, and read-select behavior.

The RBBMIF section describes timeout observability and masking for display register bus clients. It includes timeout delay and request-hold fields, decoded client status words, timeout address/op/read-write/ack/mask fields, per-client timeout-disable bits for clients 0-37, and status flags for interface state, read timeout, FIFO empty/full, and invalid access type/address.

The `dce_dc_dmu_dc_pg_dispdec` block defines display power-gating domains. It provides paired `DOMAINn_PG_CONFIG` and `DOMAINn_PG_STATUS` fields for domains 0-9 and 16-20 in this chunk, plus interrupt status/control registers for domains 0-21 and `DC_IP_REQUEST_CNTL__IP_REQUEST_EN`. Nearby DCN 3.0.2 hardware sequencer code uses these exact domain field names to power-gate HUBP, DPP, and DSC instances with `REG_UPDATE()` and `REG_WAIT()`.

The `dce_dc_dmu_dmu_dcperfmon_dc_perfmon_dispdec` block defines `DC_PERFMON2`, matching the DCCG perfmon register pattern but under DMU. The `dce_dc_dmu_dmu_misc_dispdec` block covers pipe disable/DMCUB enable, DMU clock gating and clock-on status, DMCU ERAM/IRAM memory power control, DMCU-SMU/static-screen interrupt reporting, DC-SMU interrupt control, and a forced deep-sleep allow field.

The final visible block, `dce_dc_dmu_dmcu_dispdec`, begins the DMCU microcontroller register definitions. It includes DMCU reset/enable/IRQ masking/dynamic clock gating/read-timeout fields, DMCU status bits, firmware/program counter start and checksum registers, host access controls for ERAM/IRAM with auto-increment and byte-enable fields, event trigger fields for software/internal interrupts, internal microcontroller interrupt-status bits, static-screen interrupt status/clear bits, and the beginning of the large `DMCU_INTERRUPT_STATUS` field map for ABM, MCP/SCP, UC internal/read-timeout, DCPG IHC power, and VBLANK events.

## Integration Points

This header is included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` alongside `dcn_3_0_2_offset.h`. That resource file constructs the DCN 3.0.2 display resource pool and passes register address, shift, and mask tables into lower-level display objects. The shift/mask header is therefore tied to the matching offset header and to the generated register list macros in DCN 3.0.2 components.

The macros are not usually consumed directly as raw constants in hand-written code. AMD display code normally wraps them through `reg_helper.h` conventions such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`, using helper `FN(reg_name, field_name)` macros to route a logical field name to the generated `shifts` and `masks` tables. The nearby DCN 3.0.2 hardware sequencer is a concrete example: it updates `DOMAINn_POWER_GATE`, waits on `DOMAINn_PGFSM_PWR_STATUS`, and temporarily enables `IP_REQUEST_EN` around DSC power-gating operations.

The DCCG fields integrate with display clock source, DTO, OTG, link encoder, audio, and timing generator setup. The power-gating fields integrate with HUBP/DPP/DSC lifecycle code. The RBBMIF and perfmon fields integrate with diagnostics, timeout handling, and performance telemetry. The DMCU/DMU fields integrate with display microcontroller, SMU notification, static-screen, memory-power, and vblank/ABM interrupt paths.

## Control Flow And State Behavior

There is no C control flow in this header. Runtime control flow emerges when the driver combines these constants with register access helpers:

- Read-modify-write updates preserve non-target bits using `_MASK` and `_SHIFT`.
- Poll loops such as power-gating waits read status fields until they match expected values.
- Clear-on-write interrupt/status fields are represented by duplicate `*_OCCURRED` and `*_CLEAR` names sharing the same bit positions and masks.
- DTO and clock-divider programming writes phase/modulo/divider/change-toggle fields, then observes enable/done/status fields.
- Perfmon programming selects events and run/start/stop behavior, then reads low/high value registers and acknowledges interrupts.

Hardware state persists in device registers, not in this header. The fields in this chunk control persistent or semi-persistent display hardware state including VGA legacy aperture setup, display and PHY clocks, clock gating disable/force decisions, DTO ratios, power-gated domain states, timeout masks, microcontroller firmware access windows, interrupt masks/clears, and static-screen or vblank interrupt status. Incorrect values can survive until reset or until later driver code rewrites the affected register.

## Dependencies

The chunk depends on the matching DCN 3.0.2 register offset definitions in `dcn_3_0_2_offset.h` and on the broader AMD display register access infrastructure. The constants also depend on AMD's hardware register specification for this ASIC revision. The source is generated-style C preprocessor data; its effective type and width depend on kernel C compilation rules for hexadecimal integer literals, so callers should treat masks as register-width values rather than portable semantic constants.

The names are part of a cross-file generated contract. A field rename, missing macro, or mismatched instance number can break compilation in files that populate register structures. A numerically wrong mask/shift can compile cleanly but silently manipulate the wrong hardware bits.

## Risks And Edge Cases

- Wrong masks or shifts are high-risk because failures are hardware-behavioral, not type-checked. A one-bit error in power gating can hang a display domain, while an error in DTO or DISPCLK fields can cause unstable clocks or link/display corruption.
- Many fields are repeated across instances (`OTG0`-`OTG5`, `DPPCLK0`-`DPPCLK5`, `DOMAIN0`-`DOMAIN21`, `DC_PERFMON0`-`2`). Copy/paste or generation drift can affect only one instance and escape broad testing.
- Status and clear fields often intentionally share bit positions and masks. Generic tooling must not treat duplicate shifts as accidental duplicates.
- Some fields cover full 32-bit masks (`0xFFFFFFFFL`), and some high-bit masks use signed-looking `L` literals such as `0x80000000L`. Register helpers should operate on unsigned 32-bit values to avoid sign-extension or comparison surprises.
- Legacy VGA fields are shared conceptually with older DCE code and may be touched by boot/VGA handoff paths. Misprogramming can affect early display, VGA decode, or console restore behavior.
- Power-gating domain numbering is semantic. DCN 3.0.2 hardware sequencer maps HUBP, DPP, and DSC instances to specific domains; a swapped domain field can wait on the wrong status bit or gate the wrong block.
- Interrupt status/clear fields for DMCU, DMU power gating, and perfmon can lose events if software writes broad masks instead of precise clear bits.
- This chunk ends in the middle of the `DMCU_INTERRUPT_STATUS` macro family, so later chunk research is needed before making whole-file conclusions about complete DMCU interrupt coverage.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage for DCN 3.0.2 display code, proving all referenced generated field names exist and the header composes with the matching offset header.
- Register table initialization compile checks in `dcn302_resource.c` and adjacent DCN 3.0.2 modules that use `FN()` mappings for shifts and masks.
- Hardware smoke tests on DCN 3.0.2 ASICs covering display bring-up, hotplug/link training, mode set, vblank, audio clocking, DSC enablement, and suspend/resume.
- Power-gating tests that exercise HUBP, DPP, and DSC domain transitions and confirm `DOMAINn_PGFSM_PWR_STATUS` reaches expected values without timeouts.
- Clock tests around DISPCLK/DPPCLK/DSCCLK/DP DTO programming, including frequency changes, half-rate output, and FIFO error counters.
- Interrupt tests for DCPG, DMCU static-screen, vblank, ABM, UC internal interrupt, and perfmon clear/ack paths.
- Diagnostics or debugfs-style register dumps comparing encoded field values against the hardware specification for masks with full-width, high-bit, and duplicated status/clear semantics.
