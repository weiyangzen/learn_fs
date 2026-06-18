# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h

## Purpose

`nbio_6_1_smn.h` is a generated-style AMDGPU ASIC register header for NBIO 6.1. It publishes System Management Network / PCIe indirect addresses for a compact set of NBIO PCIe control, clock-gating, performance-counter, and replay-counter registers. The path lives under a `ceph-client` source mirror, but the content is Linux DRM AMDGPU hardware metadata, not distributed-filesystem logic.

The file has no executable code. Its value is the macro namespace exported to NBIO 6.1 driver code:

- `smnCPM_CONTROL` at `0x11180460`, used for BIF medium-grain clock-gating control.
- `smnPCIE_CNTL2` at `0x11180070`, used for BIF memory light-sleep control and state reporting.
- `smnPCIE_CONFIG_CNTL` at `0x11180044`, used by NBIO initialization to set CI/SWUS max-read-request behavior.
- `smnPCIE_CI_CNTL` at `0x11180080`, used by NBIO initialization to disable CI slave ordering.
- `smnPCIE_PERF_*` registers from `0x11180200` through `0x1118025c`, used as the NBIO 6.1 PCIe performance counter address map.
- `smnPCIE_RX_NUM_NAK` and `smnPCIE_RX_NUM_NAK_GENERATED`, used to read received/generated PCIe NAK counts for replay accounting.

## Important APIs, Types, And Functions

This header exports only preprocessor constants and an include guard. There are no functions, structs, enums, globals, inline helpers, allocation paths, locks, or callbacks.

The practical API is the naming and address contract shared with the rest of the NBIO 6.1 register header set:

- `nbio_6_1_smn.h` supplies SMN/PCIe register addresses for `RREG32_PCIE()` and `WREG32_PCIE()` access.
- `nbio_6_1_sh_mask.h` supplies the field masks and shifts for the same logical register names, such as `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK`, `PCIE_CNTL2__SLV_MEM_LS_EN_MASK`, `PCIE_CONFIG_CNTL__CI_SWUS_MAX_READ_REQUEST_SIZE_MODE_MASK`, `PCIE_CI_CNTL__CI_SLV_ORDERING_DIS_MASK`, and `PCIE_PERF_CNTL_TXCLK__EVENT0_SEL_MASK`.
- `nbio_6_1_default.h` supplies reset/default values for these SMN-named registers, including defaults for PCIe control, performance counters, replay counters, and CPM control.
- `nbio_6_1_offset.h` supplies SOC15 MMIO/config-space offsets for the broader NBIO block; it is complementary but not interchangeable with the SMN addresses here.

The only direct include observed in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes this file with `nbio_6_1_default.h`, `nbio_6_1_offset.h`, and `nbio_6_1_sh_mask.h`. Common SOC15 code in `drivers/gpu/drm/amd/amdgpu/soc15.c` uses these macro names for PCIe usage and replay count helpers when the selected ASIC header set exposes them.

## Control Flow

There is no local control flow in this header. Runtime control flow is in consumers that select one of these symbolic addresses and access the hardware through AMDGPU register helpers.

The NBIO 6.1 clock-gating path in `nbio_v6_1.c` reads `smnCPM_CONTROL`, sets or clears LCLK/TXCLK/refclk gate enable masks depending on the requested state and `AMD_CG_SUPPORT_BIF_MGCG`, then writes the register only if the value changed. The matching query path reads the same register and reports `AMD_CG_SUPPORT_BIF_MGCG` when `CPM_CONTROL__LCLK_DYN_GATE_ENABLE_MASK` is set.

The NBIO 6.1 light-sleep path reads `smnPCIE_CNTL2`, sets or clears slave, master, and replay memory light-sleep enable bits depending on `AMD_CG_SUPPORT_BIF_LS`, and writes back only on change. The clock-gating-state query reads `smnPCIE_CNTL2` and reports `AMD_CG_SUPPORT_BIF_LS` when the slave memory light-sleep bit is set.

The NBIO initialization path reads `smnPCIE_CONFIG_CNTL`, updates `CI_SWUS_MAX_READ_REQUEST_SIZE_MODE` and `CI_SWUS_MAX_READ_REQUEST_SIZE_PRIV`, then writes the register if modified. It then reads `smnPCIE_CI_CNTL`, sets `CI_SLV_ORDERING_DIS`, and writes it back if needed. These operations depend on field definitions from `nbio_6_1_sh_mask.h`, while this header supplies the address targets.

The SOC15 PCIe usage path programs `smnPCIE_PERF_CNTL_TXCLK`, starts and resets all counters through `smnPCIE_PERF_COUNT_CNTL`, sleeps for a one-second measurement window, loads shadow counters by writing `smnPCIE_PERF_COUNT_CNTL` again, reads overflow bits from `smnPCIE_PERF_CNTL_TXCLK`, and combines them with `smnPCIE_PERF_COUNT0_TXCLK` / `smnPCIE_PERF_COUNT1_TXCLK` to produce 64-bit counts. APUs return early to avoid touching possibly different GPU/APU PCIe registers.

The SOC15 replay-count path reads `smnPCIE_RX_NUM_NAK` and `smnPCIE_RX_NUM_NAK_GENERATED`, then returns their sum as the replay count. The header does not define reset, clear, or wrap semantics for these counters; those are hardware properties.

## State And Persistence Behavior

The header stores no software state and persists nothing. Its macros name hardware-backed state in NBIO/PCIe register space.

The state controlled through these addresses includes BIF clock-gating enables and latencies, PCIe memory light-sleep enables, CI request/order policy, performance counter configuration and captured counts, and replay-related NAK counters. These values live in GPU registers and are affected by ASIC reset, firmware/BIOS initialization, driver initialization, clock-gating updates, suspend/resume, runtime power management, GPU reset, and possibly PCIe link or error events.

Persistence behavior is external to the header. Some registers are policy controls that the driver rewrites during NBIO initialization or clock-gating transitions. Some performance and replay counters are measurement/status registers whose values can change independently of CPU writes. The macros themselves do not encode access width, volatility, reset domain, write-one-to-clear behavior, counter overflow behavior, privilege level, or ordering requirements.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database. The SMN addresses here must match field masks in `nbio_6_1_sh_mask.h` and reset defaults in `nbio_6_1_default.h`. If an address is stale while the field masks still compile, the driver can silently read or modify the wrong NBIO register.

Important integration points are:

- `amdgpu/nbio_v6_1.c`: NBIO 6.1 initialization, clock-gating, light-sleep, and state reporting through `RREG32_PCIE()` / `WREG32_PCIE()`.
- `amdgpu/soc15.c`: common SOC15 PCIe usage and replay-count helpers using the `smnPCIE_PERF_*` and NAK counter names exposed by SOC15 ASIC header sets.
- AMDGPU clock-gating policy: `adev->cg_flags` gates whether NBIO writes enable BIF MGCG and BIF light sleep.
- ASIC selection and register-base initialization: these macros are valid for NBIO 6.1-class hardware and should not be treated as a universal PCIe register map for all AMD GPU generations.
- Hardware diagnostics and performance telemetry: PCIe usage counters and replay counts may surface in debugfs, sysfs, logs, or driver diagnostics through higher-level AMDGPU paths.

The nearby NBIO 7.0 SMN header preserves the same base set of addresses and adds extra TXCLK aliases, while NBIO 7.4.0 changes the perf-counter naming layout. That comparison is a useful signal that the macro names are generation-specific even when many numeric addresses overlap.

## Risks And Edge Cases

- The file is pure preprocessor data. Wrong addresses, missing macros, or accidental renames may compile in some configurations but cause incorrect hardware access in NBIO 6.1 paths.
- SMN addresses are not the same as SOC15 `mm*` offsets or PCI config `cfg*` offsets. Mixing these address domains would target the wrong access path.
- `smnCPM_CONTROL` and `smnPCIE_CNTL2` control power-management behavior. Incorrect writes can disable intended clock gating/light sleep, over-enable low-power states, or destabilize PCIe/NBIO traffic during runtime power transitions.
- `smnPCIE_CONFIG_CNTL` and `smnPCIE_CI_CNTL` affect request sizing and ordering. Bad addresses or field mismatches can affect PCIe completion ordering, read request sizing, throughput, or interoperability with root complexes.
- Performance-counter access has side effects: `soc15_get_pcie_usage()` writes event selection, starts/resets counters, waits, stops/loads shadow counters, and reads back count/overflow state. Incorrect aliases can corrupt unrelated telemetry or control registers.
- Replay counters may wrap or be updated concurrently by hardware. Summing `RX_NUM_NAK` and `RX_NUM_NAK_GENERATED` is only as reliable as the hardware counter width and sampling semantics.
- Current handwritten in-tree direct inclusion is narrow. Many macros are part of a generated public register contract and may be relied on by build configurations, downstream code, diagnostics, or future driver changes that are not visible through simple direct-reference searches.
- The include guard uses the generated name `_nbio_6_1_SMN_HEADER`. A guard collision with another generated header would hide definitions at compile time.

## Test Signals

Useful validation signals for this header are mostly build, bring-up, and hardware-observed behavior:

- Build AMDGPU configurations that include NBIO 6.1 support. Syntax, include-guard, missing macro, or renamed macro problems should surface in `nbio_v6_1.c` and common SOC15 users.
- Compare the addresses against the authoritative NBIO 6.1 register database and against companion `nbio_6_1_default.h` / `nbio_6_1_sh_mask.h` names, especially the nonzero default registers and the fields modified by `nbio_v6_1.c`.
- Boot NBIO 6.1 hardware and verify that `init_registers` does not regress PCIe enumeration, DMA stability, completion behavior, or read-request sizing.
- Exercise BIF medium-grain clock gating and BIF light sleep enable/disable paths. The reported clock-gating flags should track writes to `smnCPM_CONTROL` and `smnPCIE_CNTL2`.
- Run suspend/resume, runtime power management, GPU reset, and BACO-adjacent scenarios to catch persistence or reset-domain assumptions around clock-gating and PCIe control registers.
- Query PCIe usage telemetry and confirm counters are nonzero on active discrete GPUs and remain safely skipped on APUs.
- Monitor replay counts under normal and stressed PCIe link conditions. Unexpected jumps can indicate link problems, but a sudden flatline after header changes may indicate broken NAK counter addressing.
- Check for PCIe AER, link training, or throughput regressions after any regeneration of this header or its companion field-mask/default files.
