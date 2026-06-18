# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 11462-14269

## Scope

This chunk is a generated AMDGPU NBIO 6.1 default-value header segment. It contains only C preprocessor constants of the form `#define <register>_DEFAULT <hex-value>`; it has no functions, structs, enums, variables, allocation, locking, direct MMIO access, or executable control flow.

The range covers 2,799 `#define` rows. It starts in the middle of the `DWC_E12MP_PHY_X4_NS_X4_1_RAWCMN` common-memory default table, continues through X4_1 raw-lane, supervisor, generic-lane, and raw-common templates, includes small `KPFIFO1` and `KPNP_SNPS1` default blocks, then starts the `DWC_E12MP_PHY_X4_NS_X4_2` supervisor and lane defaults. The chunk ends inside `X4_2_LANE3_DIG_RX_STAT_MATCH_CTL0`, so the `X4_2_LANE3` block is incomplete in this slice.

Visible address-block markers in or near this range include:

- `nbio_lcu_kpfifo_kpfifo1_kpfifo_dir`
- `nbio_lcu_kpnp_kpnp1_kpnp_dir`
- `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns2_dwc_e12mp_phy_x4_ns_UP16_dwc_e12mp_phy_x4_ns_UP16_mem_map`

The surrounding file header identifies this as the default-value half of the NBIO 6.1 generated register set. Related include-level integration is visible in `amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h` together with `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`; Vega10 powerplay headers also include this default header.

## Purpose

`nbio_6_1_default.h` records hardware reset or generator-specified default values for NBIO 6.1 registers. This chunk is focused on Synopsys DesignWare E12MP x4 PIPE/PCS/PHY register defaults for NBIO PCIe/NBIO link units rather than PCI configuration-space fields.

The covered defaults describe:

- Common PHY memory/register defaults for `X4_1_RAWCMN` and `X4_1_RAWCMNX`, including many `DIG_MEM_CMN*` rows.
- Per-lane raw PCS/PMA control defaults for `X4_1_RAWLANE0` through `X4_1_RAWLANE3`, plus generic `RAWLANEX` defaults.
- Supervisor/common PLL defaults for `X4_1_SUPX` and `X4_2_SUP`, including IDCODE, reference-clock override, MPLLA/MPLLB override, spread-spectrum clocking, analog PLL, RTUNE, and common power-control timing values.
- Per-lane ASIC, TX/RX power-control, RX VCO calibration, CDR/DPLL, RX adaptation, statistics, and analog TX/RX defaults for `X4_1_LANEX` and `X4_2_LANE0` through part of `X4_2_LANE3`.
- KPFIFO and KPNP defaults for lane FIFO control, PCS/PMA soft reset, PHY identity, lane request/control/status, PMA controls, PHY/lane soft reset, and reset control.

Most values are `0x00000000`, which is expected for status, monitor, override-disabled, scratch, and analog-measurement registers. Nonzero defaults encode hardware bring-up policy: PLL bandwidth and SSC values, ID codes, lane power-state encodings, TX/RX power-up timers, CDR/DPLL tuning, RX adaptation presets, slicer and DAC offsets, reset defaults, and lane/FIFO control defaults.

## Important Macro Families

There are no callable APIs or C types. The consumed API surface is the macro namespace itself.

Important families in this slice are:

- `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMN_DIG_MEM_CMN6_B6_R4_DEFAULT` through the rest of `B6_R31`, continuing a common-memory bank that began before the chunk. These are all zero in this slice.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMN_DIG_MPLLA_*` and `*_MPLLB_*` defaults, with PLL bandwidth override values such as `0x00000043`, SSC control `0x00005000`, and SSC enable defaults of zero.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWLANE{0..3}_DIG_PCS_XF_*`, `DIG_FSM_*`, `DIG_AON_*`, `DIG_IRQ_CTL_*`, `DIG_PMA_XF_*`, `DIG_TX_CTL_*`, and `DIG_RX_CTL_*`, which repeat per raw lane. These cover PCS/PMA override inputs/outputs, TX/RX PCS interfaces, adaptation acknowledgements, FSM fast-path/status registers, always-on analog offset defaults, IRQ clear/mask defaults, PMA lane/supervisor handoff, and TX/RX control defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_SUPX_*` and `smnDWC_E12MP_PHY_X4_NS_X4_2_SUP_*`, which expose common/supervisor PLL and analog defaults. Notable values include IDCODE low/high defaults, refclk override `0x00000070`, MPLLA/MPLLB override encodings, PLL power timing thresholds, SSC phase/frequency values, analog misc values, and RTUNE defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_LANEX_*` and `smnDWC_E12MP_PHY_X4_NS_X4_2_LANE{0..3}_*`, which define generic and concrete lane defaults for ASIC handoff, TX power states, RX power states, VCO calibration, RX alignment, LBERT, CDR, DPLL, adaptation control/status, RX statistics, and analog TX/RX controls.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN*` defaults, a large common-memory template with many repeated nonzero calibration/control words such as `0x00005306`, `0x00001f4f`, `0x000001af`, `0x000001b6`, `0x0000080e`, and zero-filled gaps.
- `smnKPFIFO1_*` defaults, covering primary TX FIFO HSCID, per-lane FIFO control for lanes 0-3, and PCS/PMA soft reset.
- `smnKPNP_SNPS1_*` defaults, covering KPNP hardware version/PHY info/lane ID, lane request control and status, PMA control registers, PHY and lane soft reset defaults, and reset control.

## Control Flow

This header segment has no runtime control flow. Inclusion is controlled by the full file's header guard. At compile time, translation units that include `nbio_6_1_default.h` receive these constants.

The intended consumer pattern is external to this file:

1. Select a register address from `nbio_6_1_offset.h` or `nbio_6_1_smn.h`.
2. Use field layout from `nbio_6_1_sh_mask.h` when a bitfield must be decoded or composed.
3. Use the matching `_DEFAULT` macro from this header as a reset/default comparison value, initialization seed, generated-table input, or documentation of hardware reset state.
4. Perform actual access through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, or related NBIO/SOC15 helpers.

The local `amdgpu/nbio_v6_1.c` runtime implementation mostly manipulates NBIO/PCIe registers through offset and mask headers; direct default-value usage is not obvious in the inspected section. The default header still remains part of the generated NBIO 6.1 interface and must stay synchronized with offsets, SMN addresses, and masks.

## State and Persistence Behavior

The header stores no software state and performs no persistence. It describes default state held in NBIO/PHY hardware registers.

State represented by these constants includes:

- Static identity and revision values for supervisor PHY blocks.
- Default PLL, SSC, refclock, RTUNE, and common analog settings.
- Per-lane TX/RX power-state defaults and wake/power-up timing values.
- RX VCO calibration, CDR, DPLL, adaptation, slicer, DAC, DFE, and statistics defaults.
- PCS/PMA override inputs and outputs, ASIC handoff defaults, and PMA/supervisor interface defaults.
- IRQ mask/clear defaults and reset/default values for KPFIFO/KPNP control registers.
- Raw common-memory banks that likely seed PHY firmware/microsequence or generated common control tables.

Persistence and lifetime are hardware-defined. These values may be present after power-on reset, GPU reset, NBIO reset, PHY/lane reset, or firmware initialization, but runtime firmware and the AMDGPU driver can alter many of the same registers during link training, PCIe power management, clock gating/light sleep, reset handling, or diagnostics. Status and monitor registers default to zero but are updated by hardware after bring-up. Override and reset defaults are especially sensitive because writing the default value may assert/deassert control, not merely restore a passive software variable.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_6_1_offset.h`, which supplies register offsets for the same NBIO 6.1 generated register database.
- `nbio_6_1_sh_mask.h`, which supplies field masks/shifts when code needs to modify pieces of these registers rather than comparing whole defaults.
- `nbio_6_1_smn.h`, which supplies SMN address constants for direct SMN/PCIe register access.
- `amdgpu/nbio_v6_1.c`, the NBIO 6.1 runtime implementation, which includes the default, offset, mask, and SMN headers together and uses SOC15/PCIe register helpers for NBIO control.
- `pm/powerplay/hwmgr/vega10_inc.h`, which also includes this generated default header as part of Vega10/NBIO register metadata.
- PCIe PHY/link bring-up, power management, clock gating, reset, link-training, and error/recovery flows that rely on NBIO 6.1 register definitions.
- The generated register source used to create `default`, `offset`, `sh_mask`, and `smn` headers. A mismatch between these headers can produce valid C that programs or validates the wrong hardware register.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU driver hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Risks and Edge Cases

- The file is generated and highly repetitive. A single bad default can be difficult to spot manually and may only appear as unstable PCIe link training, bad power transitions, failed reset recovery, or poor signal integrity.
- This chunk begins and ends inside larger logical regions. The `X4_1_RAWCMN` memory bank starts before line 11462, and `X4_2_LANE3` continues after line 14269. Merge/reconciliation should not treat either boundary as complete.
- Per-lane blocks are mechanically repeated. `RAWLANE0` through `RAWLANE3`, `LANEX`, and `X4_2_LANE0` through `X4_2_LANE2` should be compared after normalizing the lane number, while `X4_2_LANE3` is partial in this slice.
- The naming distinction between concrete lanes (`LANE0`), raw lanes (`RAWLANE0`), generic lane templates (`LANEX`/`RAWLANEX`), common blocks (`RAWCMN`/`RAWCMNX`), and supervisor blocks (`SUP`/`SUPX`) is meaningful. Accidentally using a generic-template default for a concrete lane or the wrong x4 instance can program the wrong hardware block.
- Many zeros are intentional, but zero is not always harmless. Defaults for reset, clear, mask, override, enable, and status registers can have side effects if code writes them back during runtime.
- Nonzero PHY calibration and analog values are hardware-tuned constants. Changes to defaults such as PLL bandwidth/SSC, CDR/DPLL, VCO calibration, DFE/slicer offsets, TX/RX power timing, and PMA controls can affect PCIe link margin, speed negotiation, power, or reliability.
- KPNP reset defaults include nonzero PMA/reset values (`PMA_CONTROL1`, `PMA_CONTROL2`, `LANE_SOFT_RESET`, `REG_RST_CTRL`). Misinterpreting these as arbitrary reset-state documentation could leave PHY lanes held in reset or released too early.
- The `_DEFAULT` header does not encode access semantics. Consumers still need the offset, mask, SMN address, and hardware rules for read-only, write-one-to-clear, sticky, volatile, or self-clearing registers.

## Test Signals

Useful validation signals for this chunk:

- Compile AMDGPU configurations that include `nbio_6_1_default.h`, especially `amdgpu/nbio_v6_1.c` and Vega10 powerplay paths. Missing, malformed, or duplicate macros should fail at build time.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database, verifying that defaults, offsets, masks, and SMN names stay synchronized.
- Mechanically count and validate this slice: it should contain 2,799 `#define` rows in the requested line range, all with hexadecimal default values.
- Normalize lane numbers and compare repeated `RAWLANE0`-`RAWLANE3` groups for expected structural parity; compare `X4_2_LANE0`-`X4_2_LANE2` similarly and treat `X4_2_LANE3` as partial.
- Check chunk-boundary reconciliation with adjacent research chunks so `X4_1_RAWCMN` and `X4_2_LANE3` are represented as partial here, not as full blocks.
- On NBIO 6.1/Vega10-class hardware, use PCIe link smoke tests after boot, suspend/resume, GPU reset, and module reload to catch PHY default regressions: link comes up, negotiated speed/width are expected, no repeated retraining occurs, and AER/error counters remain stable.
- Exercise power-management and light-sleep/clock-gating paths that interact with NBIO/PCIe, watching for link-down events, reset storms, or poor LTR/ASPM behavior.
- If low-level diagnostics are available, compare selected PHY/PCS registers after reset with the generated defaults before firmware or driver writes modify them.
- Stress SR-IOV or multi-function configurations only as an integration signal; this chunk is PHY/PCS default metadata rather than PCI configuration-space VF layout, but PHY defaults can still affect VF-visible link stability.
