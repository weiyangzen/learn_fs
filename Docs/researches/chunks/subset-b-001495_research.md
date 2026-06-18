# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 25047-28986

## Scope

This chunk is a generated AMDGPU BIF 5.1 register bitfield header segment. It contains only C preprocessor constants: every meaningful exported item is a paired `*_MASK` and `*__SHIFT` macro for extracting or composing fields inside 32-bit PCIe/BIF wrapper, link-management, reset, and PHY registers. There are no functions, structs, enums, storage objects, or executable control flow in this range.

The chunk starts in the tail of the `PSX81_WRP_*` wrapper register fields, covers `RFE_*` reset/front-end fields, then defines large mirrored `PSX80_BIF_*` and `PSX81_BIF_*` blocks, and ends in the beginning of `PSX80_PHY0_TX_*` lane/debug fields. The paired address/header side for these masks is expected to live in the matching `bif_5_1_d.h` register-definition header and nearby ASIC register include files.

## Purpose

The purpose of this header fragment is to make hardware register accesses type-light but name-stable. AMDGPU call sites can name a register family and field, then use common helper macros such as `REG_GET_FIELD(value, REG, FIELD)` and `REG_SET_FIELD(value, REG, FIELD, new_value)` without hard-coding literal bit positions. The constants in this chunk encode the hardware ABI for:

- PCIe strap and capability settings for BIF wrapper port D/E fields, including link speed, ASPM, payload support, ECRC/E2E prefix, enhanced hotplug, and initial FTS values.
- Wrapper diagnostics and timing registers: LNC counters, eFuse words, scratch registers, DTM clock/reset/timing fields, delay-line controller command/status fields, RX detect override, and register-adapter access-mode bits.
- RFE warm reset, soft reset, master/client reset triggers, power-down command/status bits, master timeout timers, and IMP arbitration/calibration status fields.
- Per-instance `PSX80_BIF_*` and `PSX81_BIF_*` PCIe core fields for debug/status, RX/TX last TLP captures, NAK counters, CI/control knobs, link controller history/status, WPR reset controls, hidden config decode enables, protocol error ignores, performance counters, PRBS test controls, strap feature enables, software reset commands/controls, clock/power-management, and lane mapping/power controls.
- `PSX80_PHY0_COM_*`, `PSX80_PHY0_RX_*`, and initial `PSX80_PHY0_TX_*` PHY lane fields for fuse-derived calibration, electrical idle, DFX/PRBS, deemphasis/margin tables, adaptation and CDR tuning, RX/TX lane power, global speed/divider commands, DLL/debug/test hooks, and per-lane RX adaptation bypass/debug controls.

## Important APIs, Types, and Macros

There are no callable APIs or C types in this chunk. The API surface is the macro naming contract:

- `REGISTER__FIELD_MASK` gives the shifted bit mask to isolate or replace a field.
- `REGISTER__FIELD__SHIFT` gives the right-shift amount for the field.
- Register prefixes identify hardware blocks: `PSX81_WRP_*` for wrapper registers, `RFE_*` for reset front-end control, `PSX80_BIF_*` and `PSX81_BIF_*` for two BIF/PCIe instances, and `PSX80_PHY0_*` for PHY0 common/RX/TX lanes.
- Repeated lane macros use a broadcast register plus `LANE0` through `LANE7` or packed lane fields, so code can either program all lanes or target individual lanes.
- Mirrored `PSX80_BIF_*` and `PSX81_BIF_*` definitions preserve the same field names and bit encodings for the two PCIe/BIF instances, which lets instance-specific code select the register prefix while reusing field logic.

Important field groups visible in this chunk include `PCIE_CNTL`, `PCIE_CNTL2`, `PCIE_RX_CNTL2`, `PCIE_CONFIG_CNTL`, `PCIE_CI_CNTL`, `PCIE_LC_STATE6` through `PCIE_LC_STATE11`, `PCIE_LC_STATUS1/2`, `PCIE_PERF_*`, `PCIE_PRBS_*`, `PCIE_STRAP_*`, `SWRST_COMMAND_*`, `SWRST_CONTROL_*`, `CPM_CONTROL`, `LM_*`, `COM_COMMON_*`, `RX_CMD_BUS_*`, `RX_DLL_CTL_*`, `RX_RXTEST_REGS_*`, `RX_ELECIDLE_DEBUG_*`, `RX_ADAPT*`, `RX_DBG_BYP_EN_*`, `RX_ADAPTDBG1_*`, and `TX_CMD_BUS_TX_CONTROL_*`.

## Control Flow

This header has no internal control flow. Its macros participate in control flow only at compile time when included by AMDGPU source files. Typical use is:

1. A driver path chooses the ASIC-specific register address macro from the matching definition header.
2. The path reads a 32-bit register through MMIO/SMN helpers such as the AMDGPU `RREG32*`/`WREG32*` family.
3. It extracts or updates a field using the mask/shift macro pair from this header.
4. It writes the modified value back, or interprets status bits for logging, reset sequencing, performance sampling, link diagnostics, or test-mode decisions.

The header does not enforce sequencing. For reset, power, PRBS, performance-counter, and PHY adaptation fields, correct ordering is entirely the responsibility of the runtime driver code and hardware documentation.

## State and Persistence Behavior

No software state is allocated or persisted by this chunk. The constants describe hardware register state. When used by driver code, writes may alter persistent device-visible state until the next reset, power transition, firmware action, strap reload, or driver reprogramming. Notable state categories described here are:

- Strap/capability state, such as PCIe feature enables, speed/equalization defaults, hotplug support, ASPM latency, ECRC, ATS/PASID/SR-IOV, and MSI capability fields.
- Link status/history state, including link controller previous-state logs, operating/detected width, inactive/turn-on lanes, NAK counters, last TLP captures, and PRBS error counters.
- Reset state, including warm reset enable, soft reset trigger/propagation, command status, reset-complete/wait-state bits, per-block reset controls, and write/reset/atomic enable gates.
- Power and clock state, including BIF clock gating latencies/enables, lane power commands, RX/TX power gates, L1 power gating, and RFE power-down command/status bits.
- PHY calibration/debug state, including fuse validity and calibration values, DTM/delay-line control/status, CDR/adaptation tuning, electrical-idle debug, DLL controls, RX adaptation bypass values/enables, and PRBS/DFX test settings.

Because several registers include one-shot command bits, sticky status bits, and reset controls, misuse can leave the PCIe link unstable or hide meaningful error reporting.

## Dependencies and Integration Points

This chunk depends on the broader AMDGPU register-header convention. It must stay synchronized with:

- Matching BIF 5.1 register address definitions, commonly included as `*_d.h` headers.
- AMDGPU register helper macros that concatenate `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- ASIC-specific NBIO/BIF initialization, reset, link-management, RAS, virtualization, performance-counter, and debug code that includes `asic_reg/bif/*_sh_mask.h`.
- Hardware/firmware strap behavior, because many `STRAP_*` fields represent boot-time or strap-derived capabilities that software may inspect or override only under narrow conditions.
- Per-instance register routing. `PSX80` and `PSX81` fields are structurally similar, but code must still select the correct instance/address base.

Observed repository integration patterns around these register headers include AMDGPU and RAS code using `REG_GET_FIELD`/`REG_SET_FIELD` with BIF/NBIO masks, and PCIe performance-count paths writing `PCIE_PERF_COUNT_CNTL`-style controls. This exact chunk is part of the same generated macro contract even when a given field is only used by low-level bring-up or diagnostics.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong mask, shift, or field name compiles cleanly but causes incorrect MMIO programming at runtime.
- `MASK_MASK` names such as `PSX81_WRP_PCIE_WRAP_REG_TARG_MISC__CLKEN_MASK_MASK` and `PRBS_CHK_ERR_MASK_MASK` are intentional products of field names containing `MASK`; downstream helper macros must use the generated spelling exactly.
- Duplicated `PSX80`/`PSX81` blocks are easy to edit inconsistently by hand. Any future regeneration or patch should compare both instances when fields are expected to match.
- Full-width masks such as `0xffffffff` need unsigned 32-bit handling at call sites. Sign extension bugs are possible if values are stored in signed integers before shifting or comparing.
- One-shot command fields, reset controls, PRBS/DFX controls, and PHY adaptation bypass fields are high-risk on live hardware. Setting them outside the documented sequence can break link training, mask protocol errors, perturb calibration, or wedge access to the device.
- Status fields may be sticky, write-one-to-clear, or sampled through a shadow mechanism depending on the register. This header does not encode those access semantics.
- The chunk begins and ends mid-register-family, so whole-file research must reconcile adjacent chunks for complete `PSX81_WRP_BIF_STRAP_MISC_PORT_D` and `PSX80_PHY0_TX_DFX_*` coverage.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-integration oriented:

- Kernel/driver builds that include `bif_5_1_sh_mask.h` should compile without undefined macro references from `REG_GET_FIELD`/`REG_SET_FIELD` users.
- Static checks can verify that every `*_MASK` in this line range has a corresponding `*__SHIFT`, and that field pairs are unique within each register prefix.
- Generated-header comparison against the authoritative ASIC register database should show no drift for lines 25047-28986.
- PCIe smoke tests on affected ASICs should cover link training, link width/speed reporting, suspend/resume or reset paths, and error-reporting paths that depend on BIF/PCIe controls.
- Diagnostics that exercise performance counters, PRBS, lane mapping, and PHY RX/TX test controls can catch swapped masks/shifts that ordinary boot tests might not touch.
- RAS or reset-path tests should watch for reset completion, timeout, power-down status, and link recovery behavior around the `RFE_*` and `SWRST_*` fields.

## Chunk Notes for Merge

This is a partial chunk of one large generated header. The final per-file research should merge this with adjacent chunks to describe the entire `bif_5_1_sh_mask.h` register universe. For this chunk specifically, the dominant theme is low-level PCIe/BIF wrapper, reset, link-management, performance/debug, PRBS, and PHY lane bitfield definitions; it should not be summarized as active driver logic.
