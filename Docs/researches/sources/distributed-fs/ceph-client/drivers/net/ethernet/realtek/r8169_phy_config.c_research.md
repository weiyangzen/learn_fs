# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_phy_config.c

## Purpose

`r8169_phy_config.c` contains the PHY-side configuration matrix for the r8169 driver. It is called from `rtl8169_init_phy()` in `r8169_main.c` after the PHY has been initialized/resumed and before the MAC is fully started. The file applies per-MAC-version analog tuning, PHY page/MMD register sequences, energy-efficient Ethernet policy, auto-speed-down behavior, ALDPS/PLL power handling, cable/link-quality workarounds, and firmware-trigger points for many Realtek generations.

Unlike `r8169_main.c`, this file has a narrow external interface: `r8169_hw_phy_config(struct rtl8169_private *tp, struct phy_device *phydev, enum mac_version ver)`. Everything else is static helper or per-version callback.

## Important APIs, Types, And Data

`typedef void (*rtl_phy_cfg_fct)(struct rtl8169_private *tp, struct phy_device *phydev)` defines the callback signature used by the version table in `r8169_hw_phy_config()`. `struct phy_reg { u16 reg; u16 val; }` and `rtl_writephy_batch()` support compact write-only register scripts, with MDIO bus locking inside `__rtl_writephy_batch()`.

The common helper families are:

- `r8168d_modify_extpage()`, `r8168d_phy_param()`, and `r8168g_phy_param()` for Realtek paged PHY parameter windows.
- `rtl8125_phy_param()` for Clause 45 vendor MMD parameter writes guarded by explicit MDIO bus locking.
- EEE helpers such as `rtl8168f_config_eee_phy()`, `rtl8168g_config_eee_phy()`, `rtl8168h_config_eee_phy()`, `rtl8125_common_config_eee_phy()`, and `rtl8125_config_eee_phy()`.
- Power helpers such as `rtl8168g_disable_aldps()`, `rtl8168g_enable_gphy_10m()`, `rtl8168g_phy_adjust_10m_aldps()`, and `rtl8125_legacy_force_mode()`.

The file imports cross-file helpers from `r8169_main.c` via `r8169.h`: `r8169_apply_firmware()`, `rtl8168d_efuse_read()`, and `rtl8168h_2_get_adc_bias_ioffset()`.

## Control Flow

The dispatcher `r8169_hw_phy_config()` indexes a static `phy_configs[]` table by `enum mac_version`. For each known version it either calls a specific configuration function or does nothing when the MAC version needs no additional PHY programming. This keeps the control flow simple at the top level but pushes most complexity into per-generation routines.

Older PCI RTL8169 variants use write batches such as `rtl8169s_hw_phy_config()`, `rtl8169scd_hw_phy_config()`, and `rtl8169sce_hw_phy_config()` to select pages, write analog parameters, and return to page 0. Early RTL8168/810x variants add targeted `phy_write_paged()`, `phy_set_bits()`, and `phy_modify()` calls for line driver, channel estimation, and speed-down behavior.

RTL8168D paths share `rtl8168d_1_phy_reg_init_0[]`, then branch based on efuse byte `rtl8168d_efuse_read(tp, 0x01)`. They tune switching regulators, RSET/PLL parameters, and conditionally call `r8169_apply_firmware()` only after checking a PHY parameter value in `rtl8168d_apply_firmware_cond()`. This is a guard against applying firmware before the chipset is in the expected state.

RTL8168E/F/G/H and RTL8411 paths commonly call `r8169_apply_firmware()` first, then apply green table, EEE, channel-estimation, ALDPS, 10M, impedance, and power-efficiency parameters. RTL8168H reads an ADC bias offset through `rtl8168h_2_get_adc_bias_ioffset()` and writes it into PHY page `0x0bcf` when valid; it also computes TX LPF `rlen` from a PHY register and mirrors it across lanes.

RTL8125/8126/8127 paths use both paged PHY writes and the vendor MMD parameter window. `rtl8125a_2_hw_phy_config()` has a long bring-up sequence, repeated parameter writes, firmware application, 10M enablement, ALDPS disablement, legacy force-mode, and EEE configuration. Later `rtl8125b/d/cp/bp` and `rtl8126a` functions are shorter but still apply firmware, enable 10M GPHY, disable ALDPS, force legacy mode, and tune EEE. `rtl8127a_1_hw_phy_config()` is the largest sequence, applying many signal-integrity, equalization, and PHY parameter values before legacy/ALDPS/EEE finalization.

## State And Persistence

This file writes persistent hardware state into PHY pages, PHY parameter tables, vendor MMD registers, and occasionally firmware-programmed PHY RAM. It does not own long-lived software state beyond the stack and static constant tables. Page selection is temporary and should be restored by helpers such as `phy_restore_page()`, while explicit sequences that write `0x1f` manually generally end by returning to page 0.

Firmware application is side-effectful. It uses callbacks in `tp->rtl_fw` to write PHY/MAC MCU state, resets `tp->ocp_base` in the main file after firmware, and may be conditional on efuse or PHY readiness. EEE advertisement/state is altered through MMD writes and page modifications; these settings interact with phylib EEE support enabled during MDIO registration in `r8169_main.c`.

The file relies on phylib MDIO locking discipline. Batch writes and `rtl8125_phy_param()` explicitly lock; many higher-level `phy_*` helpers internally handle bus access. Manual page sequences are fragile because an early error path could leave the PHY on a nonzero page, though most helpers restore or reset the page.

## Dependencies And Integration Points

The file depends on `<linux/phy.h>` phylib helpers, `<linux/delay.h>` for ALDPS/firmware timing sleeps, and `r8169.h` for shared Realtek declarations. It is tightly coupled to `enum mac_version` values assigned in `r8169_main.c`, the Realtek PHY driver binding found during `r8169_mdio_register()`, and firmware files selected by the chip table. It also depends on standard PHY pages and Realtek-specific vendor pages/MMD addresses.

Integration is one-way at runtime: `r8169_main.c` calls `r8169_hw_phy_config()`, and this file calls back into main-driver helpers for firmware, efuse, and ADC bias. Correct behavior also depends on the PHY having already been resumed and initialized by phylib, because some sequences disable ALDPS, sleep, then apply firmware.

## Risks And Edge Cases

The major risk is silent hardware misconfiguration. Most register values are undocumented analog tuning constants; a wrong version-table entry or copied value can degrade link stability, EEE behavior, 10M operation, cable tolerance, or 2.5G/10G negotiation without compile-time symptoms. The version dispatch table must remain aligned with `enum mac_version`; gaps are intentional but easy to misread.

Page handling is another risk. Helpers that use `phy_select_page()` restore previous state, but many legacy scripts manually write page selector register `0x1f`. Any inserted return or failed MDIO transaction can leave the page selector changed. The large RTL8127A sequence has many near-identical parameter writes, making transcription errors hard to review.

Firmware ordering is delicate. Several functions disable ALDPS before firmware or apply firmware before tuning; changing this order could hang firmware load or leave low-power modes active during RAM code upload. `rtl8168d_apply_firmware_cond()` warns but does not fail driver initialization if readiness differs, so a firmware-not-applied path could still continue with reduced or broken hardware behavior.

## Test Signals

Test signals are primarily hardware and PHY oriented: successful PHY probe with dedicated Realtek PHY driver, stable link negotiation at supported speeds, repeated link flap recovery, EEE advertisement and LPI behavior, 10M/100M/1G/2.5G/10G coverage per MAC family, suspend/resume with ALDPS transitions, firmware load logs, absence of PHY timeout warnings, cable-quality regression tests, and `ethtool --show-eee`/link-mode inspection. Static checks should look for page restore discipline, table index coverage for new `mac_version` entries, and endian/constant typos in large register scripts.
