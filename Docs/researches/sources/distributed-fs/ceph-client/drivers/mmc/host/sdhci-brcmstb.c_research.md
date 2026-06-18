# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-brcmstb.c

## Purpose

`sdhci-brcmstb.c` supports SDHCI controllers in Broadcom set-top-box and Raspberry Pi style SoCs. It layers per-compatible match data over generic SDHCI platform support, handles non-standard CFG/BOOT registers, clock gating, HS400 enhanced strobe, CQHCI, base-clock overrides, reset quirks, and suspend/resume save-restore.

## Important APIs, Types, And Functions

- `struct brcmstb_match_priv` carries per-SoC cfg init, HS400ES callback, save/restore callback, ops table, and match flags.
- `struct sdhci_brcmstb_priv` stores mapped CFG/BOOT registers, saved register values, runtime flags, base clock state, and match data.
- `sdhci_brcmstb_save_regs()` and `sdhci_brcmstb_restore_regs()` preserve CFG/BOOT registers across low-power states.
- `brcmstb_reset()`, `brcmstb_reset_74165b0()`, and `brcmstb_sdhci_reset_cmd_data()` implement standard and special reset flows, including CQHCI-aware full resets.
- `sdhci_brcmstb_set_clock()` and `sdhci_brcmstb_set_uhs_signaling()` provide non-standard clock and UHS/HS400 programming.
- `sdhci_brcmstb_add_host()` sets up optional CQHCI before adding the SDHCI host.

## Control Flow

Probe selects match data from DT, enables the optional main clock, initializes an SDHCI host with match-specific ops, enables CQE if `supports-cqe` is present, maps CFG registers, parses MMC/SDHCI properties, optionally maps BOOT registers for non-removable devices, enables automatic SD clock gating only for non-removable devices on capable SoCs, wires HS400ES callbacks, and runs match-specific cfg init. It reads capabilities, masks UHS caps so DT controls them, applies match quirks, may replace base-clock capability from `clock-frequency` and an `sdio_freq` clock, then adds the host with or without CQHCI.

Suspend saves non-standard registers, disables the base clock, suspends CQHCI when enabled, and delegates to `sdhci_pltfm_suspend()`. Resume resumes SDHCI, re-enables/restores the base clock, restores saved CFG/BOOT registers, and resumes CQHCI.

## State And Persistence Behavior

Register save state is stored in `struct sdhci_brcmstb_saved_regs` inside driver private memory. `priv->flags` records runtime CQE and clock-gating decisions. `base_freq_hz` and `base_clk` persist the optional base-clock override across resume. No state persists after device removal.

## Dependencies And Integration Points

This driver integrates DT matching, SDHCI platform helpers, Broadcom CFG/BOOT register ranges, Linux clocks, `mmc_of_parse()`, CQHCI, and the helper in `sdhci-cqhci.h` to deactivate CQHCI on full SDHCI reset.

## Risks And Edge Cases

- `supports-cqe` mutates the match ops table IRQ callback in place; mixed devices with and without CQE should be reviewed for shared-table side effects.
- Base clock override disables presets because capability-derived presets become inaccurate.
- Automatic clock gating is deliberately limited to non-removable devices because SD voltage switching can break with gated clocks.
- Save/restore coverage differs by CFG core version; missing BOOT/CFG mappings may cause resume-only failures.
- CQE enable drains `SDHCI_DATA_AVAILABLE`; stuck buffer state is a known risk before command queue operation.

## Test Signals

Test removable SD, non-removable eMMC, HS400/HS400ES, `supports-cqe`, base-clock override, system suspend/resume with register restore, shutdown suspend, reset timeout behavior on 74165b0, card-busy callback presence, and `mmc_test` plus CQE-heavy I/O.
