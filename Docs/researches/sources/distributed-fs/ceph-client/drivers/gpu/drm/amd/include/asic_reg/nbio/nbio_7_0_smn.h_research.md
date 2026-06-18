# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h

## Purpose

`nbio_7_0_smn.h` is a generated-style AMDGPU ASIC register header for NBIO 7.0 SMN/PCIe registers. It contains no executable Linux or Ceph logic; despite the enclosing `ceph-client` mirror path, the file is DRM AMDGPU hardware metadata. Its job is to publish symbolic System Management Network addresses for NBIO PCIe control, clock/power management, performance-counter, and replay-counter registers used by SOC15-generation AMD GPUs.

The exported address groups are:

- `smnCPM_CONTROL` at `0x11180460`, the PCIe clock/power-management control register checked by NBIO clock-gating state reporting.
- `smnPCIE_CNTL2` at `0x11180070`, the PCIe control register used for BIF memory light-sleep enable bits and state reporting.
- `smnPCIE_PERF_COUNT_CNTL` plus `smnPCIE_PERF_*` control/count registers from `0x11180200` through `0x1118025c`, the PCIe performance counter address map.
- `smnPCIE_PERF_CNTL_TXCLK3` / `COUNT0_TXCLK3` / `COUNT1_TXCLK3` and `smnPCIE_PERF_CNTL_TXCLK4` / `COUNT0_TXCLK4` / `COUNT1_TXCLK4`, aliases over the `MST_C_CLK` and `SLV_R_CLK` counter slots for Vega20-style PCIe usage accounting.
- `smnPCIE_RX_NUM_NAK` and `smnPCIE_RX_NUM_NAK_GENERATED`, replay/NAK counter addresses used for PCIe replay count reporting.

## Important APIs, Types, And Functions

This header exports only preprocessor constants and an include guard. There are no functions, structs, enums, globals, inline helpers, locks, allocations, callbacks, or runtime conditionals.

The practical API is the macro namespace consumed by AMDGPU register-access helpers:

- `RREG32_PCIE(<smn...>)` and `WREG32_PCIE(<smn...>, value)` use these SMN address constants for indirect PCIe register reads and writes.
- `nbio_7_0_sh_mask.h` supplies the bitfield masks and shifts for the same logical registers, including `PCIE_CNTL2__SLV_MEM_LS_EN_MASK`, `PCIE_CNTL2__MST_MEM_LS_EN_MASK`, `PCIE_CNTL2__REPLAY_MEM_LS_EN_MASK`, `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK`, and `PCIE_PERF_CNTL_TXCLK*` event/overflow fields.
- `nbio_7_0_default.h` supplies reset/default values for the SMN-named registers, including zero defaults for the perf and NAK counters, `smnPCIE_CNTL2_DEFAULT` of `0x0e000109`, and `smnCPM_CONTROL_DEFAULT` of `0x0080da00`.
- `nbio_7_0_offset.h` supplies SOC15 MMIO offsets for the broader NBIO block. Those `mm*` offsets are complementary to, but not interchangeable with, the SMN addresses in this header.

Direct in-tree consumers include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` and `drivers/gpu/drm/amd/amdgpu/soc15.c`. `nbio_v7_0.c` includes this header alongside the default, offset, and mask headers. `soc15.c` includes the same NBIO 7.0 header set in common SOC15 ASIC code and uses the PCIe performance and replay counter names.

## Control Flow

There is no local control flow in `nbio_7_0_smn.h`; all behavior appears in consumers that select an address macro and access the hardware.

In `nbio_v7_0_update_medium_grain_light_sleep()`, the driver reads `smnPCIE_CNTL2`, sets `SLV_MEM_LS_EN`, `MST_MEM_LS_EN`, and `REPLAY_MEM_LS_EN` when light sleep is requested and `AMD_CG_SUPPORT_BIF_LS` is present, or clears those bits otherwise. It writes `smnPCIE_CNTL2` back only when the value changed.

In `nbio_v7_0_get_clockgating_state()`, the driver reads `smnCPM_CONTROL` and reports `AMD_CG_SUPPORT_BIF_MGCG` when `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK` is set. It then reads `smnPCIE_CNTL2` and reports `AMD_CG_SUPPORT_BIF_LS` when `PCIE_CNTL2__SLV_MEM_LS_EN_MASK` is set. NBIO 7.0 clock-gating updates use a locally defined `smnNBIF_MGCG_CTRL_LCLK` address, but this header still provides the CPM state register used by the query path.

In `soc15_get_pcie_usage()`, common SOC15 code skips APUs, programs `smnPCIE_PERF_CNTL_TXCLK` with event selectors for received messages and posted requests, starts and resets counters through `smnPCIE_PERF_COUNT_CNTL`, sleeps for a one-second sample window, loads shadow counters by writing `smnPCIE_PERF_COUNT_CNTL` again, reads overflow fields from `smnPCIE_PERF_CNTL_TXCLK`, and combines those fields with `smnPCIE_PERF_COUNT0_TXCLK` and `smnPCIE_PERF_COUNT1_TXCLK` to return 64-bit counts.

In `vega20_get_pcie_usage()`, the flow is the same but uses the TXCLK3 aliases from this header: `smnPCIE_PERF_CNTL_TXCLK3`, `smnPCIE_PERF_COUNT0_TXCLK3`, and `smnPCIE_PERF_COUNT1_TXCLK3`. The event selector differs for posted requests on Vega20-style hardware.

In `soc15_get_pcie_replay_count()`, common SOC15 code reads `smnPCIE_RX_NUM_NAK` and `smnPCIE_RX_NUM_NAK_GENERATED`, then returns their sum as the replay count. This header supplies only the register addresses; wrap, clear, and sampling semantics are hardware-defined.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. Its macros name hardware-backed NBIO/PCIe state. That state can be changed by firmware, BIOS initialization, driver initialization, clock-gating policy transitions, PCIe link events, runtime power management, suspend/resume, GPU reset, and direct register access through AMDGPU helpers.

The controlled or observed hardware state includes:

- BIF light-sleep enablement in `smnPCIE_CNTL2`.
- Clock-gating state visibility in `smnCPM_CONTROL`.
- PCIe performance counter event selection, counter start/reset/load control, low 32-bit counter values, and upper overflow fields.
- PCIe NAK/replay-related status counters.

Persistence is external to the header. The light-sleep and clock-control registers are policy/state registers that may need to be re-established after reset or power transitions. The performance counter registers are actively programmed during measurement and reset/loaded as part of the sampling flow. The NAK counters are status counters updated by hardware and may wrap or reset depending on ASIC reset domains. The macros do not encode volatility, access size, write-one-to-clear behavior, lock ordering, power-domain requirements, or counter width beyond the field masks in companion headers.

## Dependencies And Integration Points

Correctness depends on this header staying synchronized with the generated NBIO 7.0 register database and its companion files. The SMN address macros must match the bitfield definitions in `nbio_7_0_sh_mask.h` and the reset values in `nbio_7_0_default.h`; otherwise the code can compile cleanly while reading or modifying the wrong hardware register.

Important integration points are:

- `amdgpu/nbio_v7_0.c`: NBIO 7.0 power-management state reporting and BIF light-sleep control through `RREG32_PCIE()` / `WREG32_PCIE()`.
- `amdgpu/soc15.c`: common SOC15 PCIe usage telemetry and replay-count reporting through the `smnPCIE_PERF_*` and `smnPCIE_RX_NUM_NAK*` names.
- AMDGPU clock-gating policy: `adev->cg_flags` determines whether BIF light sleep is enabled, while the resulting state is read back through these SMN registers.
- ASIC dispatch: SOC15 ASIC functions choose the appropriate PCIe usage helper for different GPU families, including the Vega20 TXCLK3 path that relies on the additional aliases present in this NBIO 7.0 header.
- AMDGPU diagnostics: higher-level users may observe the counters and flags through driver telemetry, debug interfaces, logs, or PCIe health reporting.
- Generated register-header ecosystem: `nbio_7_0_offset.h` is for SOC15 MMIO offsets, while this file is for SMN/PCIe address access; mixing the domains would target the wrong path.

The nearby NBIO 6.1 SMN header is almost identical but lacks the TXCLK3/TXCLK4 aliases, while NBIO 7.4.0 changes the performance-counter naming layout to TXCLK/SCLK-oriented names. That difference is a strong signal that these names are generation-specific contracts rather than generic PCIe register names.

## Risks And Edge Cases

- Since the file is pure preprocessor data, many mistakes compile successfully. A wrong numeric address or stale alias can become a silent hardware access bug.
- SMN addresses must not be substituted for SOC15 `mm*` offsets or PCI config-space addresses. The same logical register family may appear in different address domains.
- `smnPCIE_CNTL2` affects memory light-sleep behavior. Bad writes can leave expected power savings disabled or enable low-power behavior in an unsafe state.
- `smnCPM_CONTROL` state reporting affects clock-gating flag visibility. If the address is wrong, diagnostics can report inaccurate BIF MGCG state even if another code path configured the clock gate.
- PCIe performance sampling writes control registers, resets counters, waits, and reads shadowed values. Incorrect perf-counter addresses could corrupt unrelated NBIO state or return misleading telemetry.
- The TXCLK3 and TXCLK4 macros intentionally alias existing counter slots (`0x1118021c`/`0x20`/`0x24` and `0x11180228`/`0x2c`/`0x30`). Treating them as independent hardware storage would be wrong.
- Replay counters are hardware-updated and may wrap, reset with the link or ASIC, or race with sampling. The common replay count is a snapshot sum, not a persistent software accumulator.
- The APU guard in `soc15_get_pcie_usage()` indicates that these GPU PCIe registers may not be safe or meaningful on all SOC15 devices. Reusing the macros without ASIC checks can create platform-specific failures.
- Include-guard collisions with another generated header would hide definitions at compile time. The guard `_nbio_7_0_SMN_HEADER` should remain unique.

## Test Signals

Useful validation is mostly build-time, hardware bring-up, and telemetry oriented:

- Build AMDGPU configurations that include SOC15/NBIO 7.0 support. Missing or renamed macros should surface in `nbio_v7_0.c` and `soc15.c`.
- Compare this header against the authoritative NBIO 7.0 register database and companion `nbio_7_0_default.h` / `nbio_7_0_sh_mask.h`, especially `smnPCIE_CNTL2`, `smnCPM_CONTROL`, perf counters, and NAK counters.
- Boot NBIO 7.0 hardware and exercise clock-gating state reporting. `AMD_CG_SUPPORT_BIF_MGCG` and `AMD_CG_SUPPORT_BIF_LS` should reflect the relevant hardware bits.
- Toggle BIF light-sleep paths and verify that `smnPCIE_CNTL2` changes only the intended `SLV_MEM_LS_EN`, `MST_MEM_LS_EN`, and `REPLAY_MEM_LS_EN` bits.
- Run suspend/resume, runtime power management, GPU reset, and driver reload scenarios to catch reset-domain or reinitialization assumptions around these registers.
- Query PCIe usage on supported discrete GPUs and confirm nonzero, plausible counters under traffic; APUs should keep the safe early-return behavior.
- Validate Vega20 PCIe usage accounting specifically, because it relies on the TXCLK3 aliases introduced in this header.
- Monitor PCIe replay counts under normal and stressed link conditions. Sudden flatlines, impossible jumps, or AER/link-training regressions after header changes are strong signals of bad addressing or incompatible hardware assumptions.
