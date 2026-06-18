# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 28987-32973

## Purpose

This chunk is generated BIF 5.1 register field metadata for the AMD GPU PCIe/BIF PHY and PIF blocks. It contains only C preprocessor constants: every hardware field is represented by a `<register>__<field>_MASK` and a matching `<register>__<field>__SHIFT` macro. Driver code combines these masks and shifts with the address macros from `bif_5_1_d.h` to read, modify, and write indirect BIF/PHY/PIF registers without embedding raw bit positions at call sites.

The covered range is concentrated on PSX80 and PSX81 PHY0/PIF0 register families. It starts in the middle of `PSX80_PHY0_TX_DFX_LANE0` and ends in the middle of `PSX81_PIF0_LANE6_OVRD`; adjacent chunks carry the missing first and last definitions for those split registers.

## Important APIs, Types, And Macros

There are no functions, structs, or exported runtime APIs in this range. The important interface is the macro naming contract:

- `*_MASK` macros define the raw bitmask in a 32-bit register word.
- `*__SHIFT` macros define the least-significant bit position for the same field.
- Broadcast registers apply the same field programming to all lanes when hardware supports broadcast access.
- `LANE0` through `LANE7` variants expose per-lane copies of the same field layout.
- `PSX80_*` and `PSX81_*` denote two related PHY/PIF instances or register banks that share many layouts but have distinct address constants in `bif_5_1_d.h`.

Major macro groups in this chunk:

- `PSX80_PHY0_TX_*` and `PSX81_PHY0_TX_*`: TX DFX, de-emphasis, margin/de-emphasis test, margin/de-emphasis status, RX-detect response, TX command-bus global, and TX power-gating command fields.
- `PSX81_PHY0_RX_*`: RX command-bus power/electrical-idle fields, RX global link speed fields, RX analog control, DLL debug, PRBS/test controls, electrical-idle debug, adaptation controls, figure-of-merit calculation, adaptation bypass enables, debug bypass enables, and adaptation debug bus selection.
- `PSX80_PHY0_HTPLL_ROPLL_*`, `PSX81_PHY0_HTPLL_ROPLL_*`, `PSX80_PHY0_LCPLL_LCPLL_*`, and `PSX81_PHY0_LCPLL_LCPLL_*`: PLL power-down overrides, control words, frequency modes, update strobes, fuse process values, lock/calibration/test/debug status, VCO control, and measurement outputs.
- `PSX81_PHY0_COM_COMMON_*`: common PHY fuse, electrical-idle, DFX, nominal margin/de-emphasis, adaptation, CDR, lane power-management, line-control, and test-debug fields.
- `PSX80_PIF0_*` and `PSX81_PIF0_*`: PIF scratch/debug/strap, TX/RX power control, global RX-detect and ganged-lane overrides, command-bus status/control, global command-bus overrides, and per-lane override enable/value registers.

## Control Flow

This header has no runtime control flow. Its effect appears only after inclusion by C source that performs register programming. The typical control pattern is:

1. Select a hardware register address with an `ix...` macro from `bif_5_1_d.h`.
2. Read a 32-bit register value through the AMDGPU MMIO or indirect-register accessor.
3. Clear a field with `<field>_MASK`.
4. Insert a new field value shifted by `<field>__SHIFT`.
5. Write the modified value back, or poll a status bit until it reaches the expected state.

Within this chunk, the likely polling/status fields include PLL lock and calibration status (`PllLocked`, `CalDone`, `CalFail`), PIF command status (`TXPHYSTATUS_*`, `RXPHYSTATUS_*`, `BPHY_CORE_TX_RDY_*`, `BPHY_CORE_RX_RDY_*`), PRBS error state (`prbs_err`), RX FOM validity (`rx_fom_valid`), electrical-idle out-of-bounds/comparator results, and TX margin/de-emphasis allocation status (`ron_comp_valid`, `alloc_error`, `too_many_allocated`).

## State And Persistence Behavior

The file itself persists no software state. The macros describe hardware state stored in BIF/PHY/PIF registers. Those registers are volatile and can be changed by firmware, reset sequencing, link training, power management, or driver writes.

Important state classes exposed here:

- Link command state: `link_speed`, `freq_div2`, `twosym_en`, `gang_mode`, per-lane power fields, and command-bus override fields determine how PCIe PHY lanes are instructed during training, speed changes, and power transitions.
- PLL state: control, lock, calibration, VCO, measurement, and power-down fields describe the HTPLL/ROPLL and LCPLL configuration and readiness.
- Lane analog state: TX de-emphasis coefficients, margin select values, RX termination, DC offset, CDR/adaptation controls, DFE/LEQ bypasses, and electrical-idle detector tuning influence signal integrity.
- Debug/test state: PRBS, observation selection, debug buses, test margins, bypasses, and manual calibration triggers can alter normal data-path behavior if written outside controlled debug flows.
- Strap/fuse state: fuse and strap fields expose hardware defaults and process calibration inputs. They are normally read as hardware-provided configuration rather than treated as durable driver-owned settings.

## Dependencies And Integration Points

This header is part of the AMDGPU ASIC register include set. The address-side companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h`, which defines the `ix...` register addresses corresponding to these mask/shift names. Enum values, where needed, live beside it in `bif_5_1_enum.h`.

Direct includes found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c`

Those interrupt-handler files include both `bif_5_1_d.h` and this mask header so they can decode or program BIF-related interrupt registers using the generated constants. Other driver code may receive the definitions transitively or use the address-only header when no field-level manipulation is needed.

The chunk's register names align with low-level AMDGPU access helpers that operate on MMIO or indirect BIF registers. Callers must pair the correct instance prefix (`PSX80` vs. `PSX81`), register address (`ix...`), and mask/shift macro set. Mixing banks can silently program the wrong register or interpret unrelated bits.

## Risks And Edge Cases

- Generated-header drift: these macros must match the ASIC register specification and `bif_5_1_d.h` address table exactly. A stale mask or shift can corrupt unrelated hardware fields even when C code looks correct.
- Split chunk boundaries: this research range omits the earlier `obs_*` fields for `PSX80_PHY0_TX_DFX_LANE0` and stops before the `SHIFT`, `CDREN`, and `OVRD2` fields that complete `PSX81_PIF0_LANE6_OVRD`. Any per-register reconciliation must merge adjacent chunks before treating those two registers as complete.
- Per-lane repetition: many layouts repeat for lanes 0-7. Copy/paste or generated-name mistakes are easy to miss because masks are often single-bit shifts following a regular pattern.
- Broadcast vs. lane-specific writes: using a broadcast macro/address when a lane-specific operation was intended can affect all lanes, while using one lane macro for another lane can break asymmetric link configurations.
- Debug/test fields are dangerous in production paths. PRBS, loopback, observation, force, bypass, margin, calibration, and override bits can disrupt normal PCIe link operation.
- Power-management and readiness fields are timing-sensitive. Incorrect masks around `TXPHYSTATUS`, `RXPHYSTATUS`, `BPHY_CORE_*_RDY`, PLL power-down, or command-bus scheduling can lead to hangs during resume, link retraining, speed changes, or lane power gating.
- Some fields are status-like and some are control-like within the same register family. Read-modify-write code must not blindly preserve or overwrite write-one-to-clear, sticky, or hardware-updated fields unless the hardware contract says it is safe.

## Test Signals

Useful validation signals for code that depends on this chunk:

- Build coverage for ASICs that include `bif_5_1_sh_mask.h`, especially Iceland, Tonga, and Carrizo interrupt paths.
- Static checks that every `<register>__<field>_MASK` in this range has a matching `<register>__<field>__SHIFT`, accounting for documented chunk-boundary splits.
- Cross-check generated masks against `bif_5_1_d.h` address names for the same `PSX80`/`PSX81` register prefixes.
- Hardware or emulator smoke tests covering PCIe link bring-up, suspend/resume, runtime power management, speed change/retraining, and interrupt handling.
- Debug validation for PLL lock/calibration polling, PIF command-bus readiness, RX electrical-idle detection, FOM/adaptation reads, and TX/RX per-lane override programming.
- Register dump comparison before and after any driver change touching these fields to confirm only intended bits change.
