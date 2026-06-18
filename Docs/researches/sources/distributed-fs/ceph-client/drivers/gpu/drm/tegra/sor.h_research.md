# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/sor.h

## Purpose

`sor.h` is the register and bitfield map for the Tegra SOR hardware block. It defines offsets and masks used by `sor.c` to program super-state, power sequencing, PLLs, DP link and lane controls, HDMI infoframes, HDMI 2.0 scrambling, audio/HDA handoff, interrupts, timing, CRC, and XBAR routing.

## Important APIs, Types, and Definitions

- State/control registers: `SOR_SUPER_STATE*`, `SOR_STATE*`, `SOR_HEAD_STATE*`, `SOR_PWR`, `SOR_TEST`, `SOR_TRIG`, and CRC registers.
- PLL/pad macros: `SOR_PLL0/1/2/3`, `SOR_DP_PADCTL0/2`, powerdown, calibration, TX pull-up, spare PLL, and TMDS termination fields.
- DP registers: `SOR_DP_LINKCTL0/1`, `SOR_DP_CONFIG0/1`, `SOR_DP_TPG`, DP audio blanking symbols, generic infoframe registers, link-quality custom registers, and spare-panel bits.
- Lane programming: drive current, pre-emphasis, post-cursor, lane sequencer, XBAR select/polarity, lane powerdown and common-mode bits.
- HDMI registers: AVI/audio/vendor infoframe controls, ACR registers, HDMI control, HDMI spare, HDMI 2.0 control, reference clock, and input-control bits.
- Audio/HDA registers: audio control/source selection, N/CTS values, ELD buffer write, presence, codec scratch, and interrupt status/mask/enable bits.

## Control Flow

The header has no executable control flow. Its definitions are consumed by `sor.c` in ordered hardware programming flows: reset/power sequencing, DP link configuration/training, HDMI infoframe/audio setup, DC routing, SCDC toggling, debugfs dumps, and IRQ handling.

## State and Persistence Behavior

All symbols describe hardware state persisted in SOR registers. Writes through `tegra_sor_writel()` change device state until overwritten, reset, runtime suspend, or power loss. The header itself owns no memory or mutable C state.

## Dependencies and Integration Points

It is included by `sor.c` and tightly coupled to Tegra SOR register layouts. The debugfs register table in `sor.c` uses many offsets directly. Any change here must be checked against SoC-specific offset remapping in `struct tegra_sor_regs`.

## Risks and Edge Cases

- Incorrect masks or shifts can silently corrupt hardware programming and are difficult to catch without hardware.
- Some fields are marked with uncertainty in the implementation, so definitions may encode undocumented behavior.
- Register offsets differ on newer SoCs; callers must use SoC-specific `struct tegra_sor_regs` where provided rather than fixed offsets for remapped blocks.

## Test Signals

Compile coverage catches macro syntax. Stronger signals come from register trace comparison against known-good enable sequences, hardware bring-up across SoC generations, debugfs dump sanity, HDMI audio/infoframe validation, and DP link training stability.
