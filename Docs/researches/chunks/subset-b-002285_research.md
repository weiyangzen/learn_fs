# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 4860-7245

## Scope

This chunk is part of AMD DPCS 4.2.0 generated ASIC register metadata. It contains C preprocessor definitions for indirect PHY/register-file offsets, not executable code. The covered range starts at the final `DPCSSYS_CR1_RAWAONLANE2` always-on lane offset, continues through the remaining `DPCSSYS_CR1` raw always-on lane, supervisor, lane, and raw-lane aliases, then enters the `dpcssys_cr2_rdpcstxcrind` address block and covers most of the CR2 indirect register map through `DPCSSYS_CR2_SUPX_ANA_MPLLA_ATB2`.

The definitions are consumed by AMD display/link encoder register-list macros and register access helpers. They provide the numeric CR-space offsets that pair with shift/mask metadata from the sibling `dpcs_4_2_0_sh_mask.h` file and with the outer `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` / `regDPCSSYS_CR*_DPCSSYS_CR_DATA` MMIO access windows defined earlier in this offset header.

## Purpose

The purpose of this header range is to encode the hardware address contract for DPCS CR1 and CR2 DisplayPort/PHY control registers:

- CR1 lane 3 and lane-X always-on receive calibration/adaptation offsets, including AFE/CTLE/DFE calibration, RX phase adjustment, signal detect, vref, DCC, MPLL, firmware configuration, and transceiver-mode controls.
- CR1 supervisor-X digital and analog offsets for ID code, reference clock overrides, MPLLA/MPLLB overrides, spread-spectrum clocking, charge-pump controls, prescaler, level, ASIC input mirrors, bandgap, RTUNE, MPLL power/timer/calibration, analog status, and MPLL analog registers.
- CR1 lane-X digital/analog and raw-lane-X offsets for ASIC override/in/out, TX power control, RX power control, RX stat counters, TX/RX analog overrides, MPHY low-speed controls, PCS transfer controls, RX adaptation/FSM fast paths, OCLA, and ATE hooks.
- CR2 supervisor digital/analog offsets at low CR addresses, followed by lane 0-3 per-lane digital/analog offsets. Lanes 1 and 2 expose the fuller RX-side register set, while lanes 0 and 3 in this chunk expose the reduced TX/stat-oriented subset.
- CR2 raw common offsets for common/MPLL control, SRAM initialization, firmware/PCS ID codes, AON common RTUNE values, power-gate and supervisor overrides, vref stats, and reference range/misc configuration.
- CR2 raw lane 0-3 offsets and lane-X aliases for PCS transfer, RX adaptation direction/FOM, FSM fast startup/adaptation/calibration sequencing, TX/RX control, PLL state, loss-of-signal, data-enable overrides, continuous offset/adaptation status, and ATE overrides.
- CR2 raw always-on lane 0-3 and lane-X offsets for per-lane AON calibration/status mirrors, including DFE, RX adapt, signal detect, vref, RX DCC calibration, TX DCC bank programming, MPLL background control, firmware configuration, and transceiver mode.
- CR2 supervisor-X aliases beginning at 0x8000. The range ends mid-block after the first MPLLA analog test-bus offsets, so later supervisor-X analog offsets are outside this chunk.

This is source-tree-aligned low-level display PHY metadata. Its correctness determines whether later display/link code reaches the intended PHY control/status register when programming or diagnosing link clocks, lane power, lane training, DP alternate mode behavior, analog calibration, and PHY firmware-assisted adaptation.

## Important APIs, Types, And Macros

There are no C functions or types declared in this chunk. The important interface is the generated macro namespace:

- `ixDPCSSYS_CR1_*` and `ixDPCSSYS_CR2_*` define indirect CR-space offsets. Driver code uses these through indexed register macros such as `SRI_IX()` and related register-list helpers.
- `DPCSSYS_CR1_*` and `DPCSSYS_CR2_*` prefixes identify the DPCS CR instance. Earlier in the same file, each CR instance has an address/data MMIO pair used to access these indirect offsets.
- `SUP`, `SUPX`, `RAWCMN`, `LANE{0..3}`, `LANEX`, `RAWLANE{0..3}`, `RAWLANEX`, `RAWAONLANE{0..3}`, and `RAWAONLANEX` encode the hardware sub-block and whether the define is instance-specific or an X alias.
- Suffixes such as `MPLLA_OVRD_IN`, `MPLLB_SSC_STEPSIZE_*`, `TX_PWRCTL_*`, `RX_PWRCTL_*`, `RX_STAT_*`, `ANA_*`, `PCS_XF_*`, `FSM_*`, `RX_CTL_*`, `RX_DCC_CAL_*`, and `TX_DCC_*` describe the target register function.

Important register families in this chunk include:

- `DPCSSYS_CR1_RAWAONLANE3_DIG_*` and `DPCSSYS_CR1_RAWAONLANEX_DIG_*` at offsets 0x4300-0x4351 and 0x7000-0x7051.
- `DPCSSYS_CR1_SUPX_DIG_*` and `DPCSSYS_CR1_SUPX_ANA_*` at offsets 0x8000 and above.
- `DPCSSYS_CR1_LANEX_DIG_*`, `DPCSSYS_CR1_LANEX_ANA_*`, `DPCSSYS_CR1_RAWMEM_DIG_*`, and `DPCSSYS_CR1_RAWLANEX_DIG_*` at offsets 0x9000, 0x90e0, 0xd000, and 0xe000 ranges.
- `DPCSSYS_CR2_SUP_DIG_*` / `SUP_ANA_*` at 0x0000-0x0096.
- `DPCSSYS_CR2_LANE0..3_DIG_*` and `DPCSSYS_CR2_LANE0..3_ANA_*` at 0x1000-0x13ff.
- `DPCSSYS_CR2_RAWCMN_DIG_*` at 0x2000-0x2040.
- `DPCSSYS_CR2_RAWLANE0..3_DIG_*` at 0x3000-0x33c8.
- `DPCSSYS_CR2_RAWAONLANE0..3_DIG_*` and `DPCSSYS_CR2_RAWAONLANEX_DIG_*` at 0x4000-0x4351 and 0x7000-0x7051.
- `DPCSSYS_CR2_SUPX_DIG_*` and the beginning of `DPCSSYS_CR2_SUPX_ANA_*` at 0x8000-0x804a.

The corresponding field definitions live in DPCS shift/mask headers. The display stack's link encoder code references related DPCS/RDPCS fields through macros such as `LE_SF()`, `SRI_IX()`, `SRII()`, `REG_GET()`, and `REG_UPDATE()`.

## Control Flow

This chunk has no runtime control flow. It affects runtime behavior when register helper macros expand symbolic register names into offsets:

- A display resource constructor selects the ASIC generation's register tables.
- Link encoder or HPO DP link encoder constructors populate register addresses from generated offset macros.
- Runtime link programming calls use helpers such as `REG_GET()` and `REG_UPDATE()` to read or write PHY/link fields.
- For indirect DPCS CR registers, the access path programs the CR address selector and reads/writes the paired CR data register. The `ixDPCSSYS_CR*_*` constants in this chunk are the selector values.
- Link bring-up, training, power transitions, DP alternate mode, and diagnostics then depend on these offsets reaching the intended PHY sub-block.

Concrete flows influenced by these offsets include link encoder checks of DP alternate mode disable state, writes to DPALT disable acknowledgment, reference clock enable/disable, lane TX/RX power-state changes, MPLL and spread-spectrum programming, raw-lane FSM/adaptation controls, and reads of RX/stat/analog status. The field-level shifts and masks are elsewhere; this chunk supplies the target register identity.

## State And Persistence Behavior

The file itself stores no software state. It describes persistent hardware register state and readback locations:

- Supervisor and supervisor-X registers hold PLL, reference clock, spread-spectrum, charge pump, bandgap, prescaler, RTUNE, power timer, and analog override state. These settings persist in the DPCS PHY until reset, power collapse, or explicit reprogramming.
- Lane digital registers hold ASIC override inputs, TX/RX power-state programming, DCC bank controls, TX clock alignment, loopback/BERT controls, MPHY controls, and per-lane status-counter configuration.
- Lane analog registers hold TX and RX analog override, measurement, termination, equalization, slicer, calibration, signal-detect, and test-bus state.
- Raw common and raw lane registers expose lower-level common/MPLL, PCS, FSM, adaptation, OCLA, and ATE state. Many of these are diagnostic or calibration paths and may be live only while the PHY or firmware controller is active.
- Always-on raw lane registers expose calibration/status mirrors that can remain relevant across parts of the normal lane power sequence, including RX adapt done/FOM, DFE/phase/vref values, signal detect, DCC calibration codes, and firmware configuration.
- Status-style offsets such as `*_STATUS`, `*_STAT`, `*_FAST_FLAGS`, `*_ADAPT_DONE`, `*_INIT_PWRUP_DONE`, `*_SRAM_INIT_DONE`, and `*_OVRD_OUT` reflect hardware state rather than software-owned values. Misaddressing these can produce misleading diagnostics without an obvious compile failure.

Persistence is hardware-dependent. The header does not express reset values, write-one-to-clear behavior, ordering requirements, or access widths; consumers must rely on the ASIC register specification and matching shift/mask metadata for that.

## Dependencies And Integration Points

Primary dependencies:

- The same file's earlier `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR*_DPCSSYS_CR_DATA` macros provide the outer MMIO windows for CR0-CR4 indirect access. This chunk provides many of the inner selector offsets for CR1 and CR2.
- `dpcs_4_2_0_sh_mask.h` supplies field shifts and masks that pair with these offsets.
- AMD display register-access macros depend on the generated symbol names being exact. `SRI_IX()` style macros concatenate block, instance, and register names into the `ixDPCSSYS_CR*_*` constants represented here.
- Link encoder code in the display tree uses DPCS/RDPCS register tables and field lists to manage DisplayPort PHY/link behavior. Older DCN link encoder code directly references DPCS CR raw-lane RX override registers, while HPO DP encoder code uses RDPCS PHY control fields for DPALT and lane state.
- `soc21_enum.h` contains enum values for RDPCSPIPE controls such as clock, FIFO, interrupt, DPALT, and PHY programming. Those enums provide semantic values that can be written through register offsets/masks in the DPCS/RDPCS register interface.

Concrete integration signals in this tree:

- `display/dc/dcn201/dcn201_link_encoder.h` uses `SRI_IX(RAWLANE*_DIG_PCS_XF_RX_OVRD_IN_*)` with `DPCSSYS_CR` instances and field-list entries for `DPCSSYS_CR0_RAWLANE0_DIG_*`; this is the same generated indirect-register family represented for CR1/CR2 in this chunk.
- `display/dc/dcn201/dcn201_link_encoder.c` reads and updates RDPCS DPALT control fields during DP alternate mode handling.
- `display/dc/dio/dcn20/dcn20_link_encoder.h` lists many RDPCS PHY fields for lane power, TX enable/disable, MPLL divider/fractional/SSC programming, FIFO control, and clock control. DPCS 4.2.0 offsets are the generation-specific address side of equivalent link/PHY programming.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.*` and `display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.c` use RDPCSTX/RDPCS register tables for HPO DP link encoders and inspect `RDPCS_PHY_DPALT_DISABLE`.
- DCN resource files such as `dcn31_resource.c`, `dcn314_resource.c`, `dcn315_resource.c`, and `dcn316_resource.c` instantiate RDPCSTX register lists for multiple link encoders. Newer DCN 4.x resource files show related lists commented out in some configurations, which makes generation-specific coverage important.

## Risks

- Generated-header drift is high impact. A wrong offset can compile cleanly while redirecting a CR access to a different PHY register.
- CR instance confusion is easy in this range. CR1 and CR2 contain many similarly named `SUP`, `SUPX`, `LANE`, `LANEX`, `RAWLANE`, `RAWLANEX`, `RAWAONLANE`, and `RAWAONLANEX` symbols with repeated offset patterns. A CR1/CR2 prefix mismatch can target the wrong link instance.
- Lane symmetry is partial. Lanes 1 and 2 expose fuller RX power/control/analog sets than lanes 0 and 3 in this chunk. Code assuming every lane has identical offsets can reference nonexistent or wrong addresses.
- X aliases require care. `LANEX`, `RAWLANEX`, `RAWAONLANEX`, and `SUPX` are alias-style register sets, not ordinary per-lane instance names. Consumers must know how the hardware maps the X register path.
- The chunk starts and ends on partial block boundaries. It begins with the final CR1 RAWAONLANE2 offset and ends partway through CR2 SUPX analog definitions, so whole-file analysis must merge adjacent chunks before drawing completeness conclusions.
- PLL, SSC, charge-pump, power-state, and DCC offsets are sensitive. Misprogramming can cause link-training failure, unstable clocks, display blanking, high error rates, or resume failures.
- Calibration/status offsets are often used only during difficult diagnostic paths. Incorrect offsets may escape normal boot tests and surface only under marginal signal integrity, DP alt-mode toggles, link-rate changes, or low-power transitions.
- Raw/ATE/OCLA paths can expose manufacturing or debug controls. Accidental writes through a bad register table could perturb live link operation or produce misleading debug captures.

## Test Signals

Useful validation signals for changes touching this header or its generator:

- Compile coverage for the display driver with DPCS 4.2.0 headers enabled. Missing or renamed symbols should fail in register-list or field-list macro expansion.
- Mechanical diff against vendor-generated DPCS 4.2.0 register headers or the authoritative register database. For generated offset headers, this is the strongest validation signal.
- Boot/probe smoke tests on ASICs using DPCS 4.2.0, confirming display resource creation and link encoder initialization without invalid MMIO/CR access.
- DisplayPort link bring-up across lane counts and link rates, including HBR/HBR2/HBR3/UHBR where applicable, to exercise MPLL, SSC, lane power, TX/RX adaptation, and raw-lane FSM offsets.
- DP alternate mode and USB-C retimer/dock scenarios, validating DPALT disable/acknowledge handling and PHY mux/ref-clock behavior.
- Hotplug, unplug, suspend/resume, and low-power display idle tests to catch stale supervisor/lane power state, MPLL power timer, SRAM init, and always-on calibration issues.
- Link-training stress with eye/PHY margin diagnostics, BERT/loopback where available, and RX stat counter readback to validate stat/status offsets.
- Protected debug validation using OCLA/ATE/test-bus paths only in controlled environments, confirming debug offsets read expected lane/common state without disrupting normal display output.

## Notes For Merge Lane

This chunk should be reconciled with neighboring `dpcs_4_2_0_offset.h` chunks before producing the final per-file report. The range is entirely generated register metadata, but it crosses a major address-block boundary at `dpcssys_cr2_rdpcstxcrind` and has partial boundaries at both ends. The final report should describe the full DPCS 4.2.0 offset file alongside its matching shift/mask header and the display link encoder register-table consumers.
