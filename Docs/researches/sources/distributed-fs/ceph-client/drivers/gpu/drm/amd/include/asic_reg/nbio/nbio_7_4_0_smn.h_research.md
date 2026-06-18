# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_0_smn.h

## Purpose

`nbio_7_4_0_smn.h` is a generated-style AMDGPU ASIC register-address header for NBIO 7.4.0 System Management Network access. Although it lives under the repository's `ceph-client` mirror path, the file is Linux DRM AMDGPU hardware metadata, not distributed-filesystem logic.

The header publishes symbolic SMN addresses for NBIO, NBIF, PCIe, performance-counter, interrupt-EOI, and RAS status registers. Consumers use these names with AMDGPU PCIe/SMN register helpers such as `RREG32_PCIE()` and `WREG32_PCIE()` so driver code can refer to hardware registers by stable symbolic names instead of raw addresses.

The exported address groups are:

- `smnBIFL_RAS_CENTRAL_STATUS` at `0x10139040`, the NBIF/BIFL RAS central status register used to detect and clear BIFL RAS controller interrupt receipt.
- `smnNBIF_MGCG_CTRL_LCLK` at `0x1013a21c`, an NBIF LCLK medium-grain clock-gating control address. In this tree, `nbio_v7_4.c` locally defines the same address while the v7.4 clock-gating update path is still a TODO.
- `smnCPM_CONTROL` at `0x11180460`, used by NBIO v7.4 clock-gating state reporting to observe LCLK dynamic gate enablement.
- `smnPCIE_CNTL2` at `0x11180070`, used by NBIO v7.4 to enable, disable, and report BIF memory light-sleep state.
- `smnPCIE_CI_CNTL` at `0x11180080`, a PCIe CI control address exported for this generation, though not directly referenced by `nbio_v7_4.c` in this snapshot.
- `smnPCIE_PERF_COUNT_CNTL` and numbered `smnPCIE_PERF_*_TXCLK1..4` / `smnPCIE_PERF_*_SCLK1..2` counter registers from `0x11180200` through `0x11180248`, plus event port selectors at `0x1118024c` and `0x11180250`.
- `smnPCIE_RX_NUM_NAK` and `smnPCIE_RX_NUM_NAK_GENERATED`, PCIe replay/NAK counter addresses shared with older SOC15 NBIO register maps.
- `smnIOHC_INTERRUPT_EOI` at `0x13a10120`, used to signal SMI end-of-interrupt after NBIO RAS handling.
- `smnRAS_GLOBAL_STATUS_LO` and `smnRAS_GLOBAL_STATUS_HI` at `0x13a20020` and `0x13a20024`, global RAS status registers for non-Aldebaran NBIO v7.4 paths.

## Important APIs, Types, And Functions

This header exports only preprocessor constants and an include guard. There are no functions, structs, enums, global variables, inline helpers, allocations, locks, callbacks, or runtime branches.

The practical API is the macro namespace consumed by AMDGPU register-access code:

- `RREG32_PCIE(<smn...>)` reads the hardware register at the SMN/PCIe address named by this header.
- `WREG32_PCIE(<smn...>, value)` writes the hardware register at the named SMN/PCIe address.
- `nbio_7_4_sh_mask.h` supplies the bitfield masks and shifts used with these addresses, including `PCIE_CNTL2__SLV_MEM_LS_EN_MASK`, `PCIE_CNTL2__MST_MEM_LS_EN_MASK`, `PCIE_CNTL2__REPLAY_MEM_LS_EN_MASK`, `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK`, `RAS_GLOBAL_STATUS_LO__ParityErr*` fields, `BIFL_RAS_CENTRAL_STATUS__BIFL_RasContller_Intr_Recv_MASK`, `IOHC_INTERRUPT_EOI__SMI_EOI_MASK`, and PCIe performance counter fields.
- `nbio_7_4_offset.h` supplies SOC15 MMIO register offsets for the same NBIO generation. Those `mm*`/`reg*` offsets are complementary to, but not interchangeable with, the SMN addresses in this file.

There is no same-generation `nbio_7_4_default.h` in this source tree, so default/reset values are not available locally as a companion header for this register set. That differs from some adjacent NBIO generations such as 6.1 and 7.0.

Direct integration visible in this tree is mainly `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which includes this header and uses its SMN names for light-sleep state, clock-gating state observation, and RAS error handling. Common SOC15 code in `soc15.c` uses older NBIO 7.0 headers for generic PCIe usage helpers; however, the `smnPCIE_PERF_CNTL_TXCLK3` names exported here match the Vega20-style counter aliases used by that common path.

## Control Flow

There is no local control flow in `nbio_7_4_0_smn.h`. Runtime behavior appears in consumers that select a macro and access hardware through AMDGPU register helpers.

In `nbio_v7_4_update_medium_grain_light_sleep()`, the driver reads `smnPCIE_CNTL2`, sets `PCIE_CNTL2__SLV_MEM_LS_EN_MASK`, `PCIE_CNTL2__MST_MEM_LS_EN_MASK`, and `PCIE_CNTL2__REPLAY_MEM_LS_EN_MASK` when light sleep is requested and `AMD_CG_SUPPORT_BIF_LS` is present, or clears those bits otherwise. It writes the register back only if the value changed.

In `nbio_v7_4_get_clockgating_state()`, the driver reads `smnCPM_CONTROL` and reports `AMD_CG_SUPPORT_BIF_MGCG` when `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK` is set. It then reads `smnPCIE_CNTL2` and reports `AMD_CG_SUPPORT_BIF_LS` when the slave memory light-sleep bit is set. The update function for v7.4 medium-grain clock gating is a TODO, so this header currently supports state observation more than active MGCG programming in the v7.4 file.

In `nbio_v7_4_query_ras_error_count()`, the driver reads `smnRAS_GLOBAL_STATUS_LO` for non-Aldebaran devices, while Aldebaran uses a locally defined alternate `smnRAS_GLOBAL_STATUS_LO_ALDE` address. It extracts corrected, fatal, and non-fatal parity status bits with `REG_GET_FIELD()`. Corrected errors increment `ras_err_data.ce_count`, fatal errors increment `ras_err_data.ue_count`, and any corrected, fatal, or non-fatal indication triggers the clear path.

The RAS clear path reads `smnBIFL_RAS_CENTRAL_STATUS`, writes the global status value back to `smnRAS_GLOBAL_STATUS_LO` for non-Aldebaran devices, optionally clears a separate parity fatal status register, then checks `BIFL_RAS_CENTRAL_STATUS.BIFL_RasContller_Intr_Recv`. If that interrupt receipt bit is set, it writes the central status value back to `smnBIFL_RAS_CENTRAL_STATUS`, reads `smnIOHC_INTERRUPT_EOI`, sets `IOHC_INTERRUPT_EOI.SMI_EOI`, and writes the EOI value back.

The PCIe performance-counter definitions in this header provide a numbered NBIO 7.4.0 counter map. The common SOC15 sampling flow for compatible names programs an event selector, writes `smnPCIE_PERF_COUNT_CNTL` with `GLOBAL_COUNT_EN | GLOBAL_COUNT_RESET`, waits one second, writes it again with `GLOBAL_SHADOW_WR`, reads upper counter bits from the perf control register, then combines them with 32-bit counter registers. In this snapshot the direct SOC15 include set uses NBIO 7.0 for the unnumbered `TXCLK` path, while the v7.4.0 header exposes the corresponding generation-specific addresses.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. Its macros name hardware-backed register state in NBIO and PCIe blocks.

The hardware state controlled or observed through these addresses includes:

- BIF light-sleep enablement in `smnPCIE_CNTL2`.
- BIF medium-grain clock-gating visibility through `smnCPM_CONTROL`.
- NBIF/BIFL RAS central interrupt status in `smnBIFL_RAS_CENTRAL_STATUS`.
- Global NBIO RAS parity status in `smnRAS_GLOBAL_STATUS_LO` and port/error summary status in `smnRAS_GLOBAL_STATUS_HI`.
- SMI/SCI/NMI end-of-interrupt signaling through `smnIOHC_INTERRUPT_EOI`.
- PCIe performance counter event selection, global counter control, shadow load, low 32-bit counter values, and upper overflow fields.
- PCIe NAK/replay status counters.

Persistence is entirely hardware and driver-policy dependent. Firmware or BIOS initialization, ASIC reset, GPU reset, runtime power management, suspend/resume, clock-gating transitions, RAS interrupt handling, PCIe link events, and explicit AMDGPU register writes can all change the underlying state. The macros do not encode volatility, access width beyond normal 32-bit helper usage, reset domains, write-one-to-clear semantics, ordering requirements, locking, or whether a field is safe to touch on every NBIO 7.4-derived ASIC.

Several of these registers are status or clear-on-write style integration points. For example, the RAS code writes back captured status values to clear latched error indications and writes an EOI bit after handling an interrupt. The performance-counter control register has measurement side effects because it starts, resets, stops, and loads shadow counters. Light-sleep bits are policy state that may need to be re-established after reset or power transitions.

## Dependencies And Integration Points

Correctness depends on this header remaining synchronized with the authoritative NBIO 7.4.0 register database and `nbio_7_4_sh_mask.h`. The numeric SMN addresses in this file must target registers whose fields are described by the mask header; otherwise code can compile cleanly while reading or modifying unrelated hardware.

Important integration points are:

- `amdgpu/nbio_v7_4.c`: direct include and direct use for `smnPCIE_CNTL2`, `smnCPM_CONTROL`, `smnRAS_GLOBAL_STATUS_LO`, `smnBIFL_RAS_CENTRAL_STATUS`, and `smnIOHC_INTERRUPT_EOI`.
- AMDGPU clock-gating policy: `adev->cg_flags` gates whether BIF light sleep is enabled, while readback through `smnPCIE_CNTL2` and `smnCPM_CONTROL` reports current BIF LS and MGCG flags.
- AMDGPU RAS accounting: `nbio_v7_4_query_ras_error_count()` converts hardware parity status into corrected and uncorrected error counts in `struct ras_err_data`, then clears hardware status and signals interrupt EOI.
- ASIC-specific address selection: Aldebaran uses local `_ALDE` addresses for some global/parity RAS registers, while this header supplies the non-Aldebaran v7.4.0 addresses. The shared `smnBIFL_RAS_CENTRAL_STATUS` and `smnIOHC_INTERRUPT_EOI` paths still come from this header.
- Generated register-header ecosystem: `nbio_7_4_offset.h` handles SOC15 MMIO offsets; this file handles SMN/PCIe address access; `nbio_7_4_sh_mask.h` handles field extraction and update masks.
- PCIe diagnostics and telemetry: performance counter and replay counter names are part of the generation-specific register contract even when this exact snapshot's direct use is narrow.

The file also overlaps conceptually with adjacent NBIO SMN headers. NBIO 6.1 and 7.0 expose older unnumbered and alternate PCIe perf-counter names; NBIO 7.4.0 uses numbered `TXCLK1..4` and `SCLK1..2` groups plus event port selectors. That naming difference is a strong signal that these macros should be treated as generation-specific contracts, not generic PCIe register names.

## Risks And Edge Cases

- The file is pure preprocessor data, so bad addresses, stale names, or accidental alias changes may compile successfully and fail only on real hardware.
- SMN addresses are not SOC15 `mm*` offsets, PCI config offsets, or register indices. Mixing address domains can target the wrong access path.
- `smnPCIE_CNTL2` controls BIF memory light sleep. Incorrect writes can disable intended power savings or enable low-power behavior in a state the hardware path cannot tolerate.
- `smnCPM_CONTROL` is currently used for state reporting in v7.4. If the address or mask pairing is wrong, diagnostics can report inaccurate BIF MGCG support/state.
- RAS status registers are side-effect sensitive. Writing back the wrong value or wrong address can fail to clear an interrupt, clear evidence before it is counted, or acknowledge an unrelated interrupt source.
- Aldebaran uses alternate addresses for some RAS registers. Reusing the non-Aldebaran `smnRAS_GLOBAL_STATUS_LO` address on Aldebaran would read or clear the wrong status.
- The EOI path sets `IOHC_INTERRUPT_EOI.SMI_EOI`. A wrong `smnIOHC_INTERRUPT_EOI` address can leave a RAS interrupt asserted or acknowledge the wrong interrupt class.
- PCIe performance-counter registers have start/reset/shadow-load side effects. Incorrect counter-control addresses can corrupt unrelated NBIO state or return misleading telemetry.
- The numbered perf-counter names in this header do not exactly match the unnumbered `smnPCIE_PERF_CNTL_TXCLK` macro used by older common SOC15 helpers. Callers must include the header whose macro names match their selected field masks and ASIC path.
- Replay/NAK counters are hardware-updated and may wrap or reset with link or ASIC reset domains. The header does not document width, clear semantics, or sampling races.
- The include guard `_nbio_7_4_0_SMN_HEADER` must remain unique. A collision with another generated header would silently hide definitions.

## Test Signals

Useful validation for this file is mostly build-time, register-database, and hardware-observed behavior:

- Build AMDGPU configurations that include NBIO v7.4 support. Missing, renamed, or malformed macros should surface in `nbio_v7_4.c`.
- Compare each address against the authoritative NBIO 7.4.0 register database, especially `smnPCIE_CNTL2`, `smnCPM_CONTROL`, `smnRAS_GLOBAL_STATUS_LO`, `smnBIFL_RAS_CENTRAL_STATUS`, `smnIOHC_INTERRUPT_EOI`, and the numbered PCIe performance counter map.
- Cross-check address names against `nbio_7_4_sh_mask.h` so fields extracted with `REG_GET_FIELD()` and set with `REG_SET_FIELD()` apply to the intended registers.
- Boot supported NBIO v7.4 hardware and exercise BIF light-sleep enable/disable paths. Readback should show only the intended `SLV_MEM_LS_EN`, `MST_MEM_LS_EN`, and `REPLAY_MEM_LS_EN` bits changing.
- Query clock-gating state and verify reported `AMD_CG_SUPPORT_BIF_MGCG` and `AMD_CG_SUPPORT_BIF_LS` flags track the relevant hardware bits.
- Inject or otherwise observe NBIO RAS parity events on supported hardware. Corrected events should increment CE count, fatal events should increment UE count, status should clear, and interrupt EOI should prevent repeated stale interrupts.
- Test Aldebaran and non-Aldebaran NBIO v7.4 devices separately because the RAS global/parity status address selection differs.
- Run suspend/resume, runtime power management, GPU reset, and driver reload scenarios to catch state that must be reprogrammed after reset or power transitions.
- If PCIe performance-counter names are wired into a v7.4-specific telemetry path, validate plausible nonzero counts under PCIe traffic, shadow-load behavior after the sample window, and no regressions in APU or unsupported-device guards.
- Watch PCIe AER, link training, replay-count, and throughput signals after any regeneration of this header or mask companion, because address mistakes can appear as hardware health or telemetry anomalies rather than compile failures.
