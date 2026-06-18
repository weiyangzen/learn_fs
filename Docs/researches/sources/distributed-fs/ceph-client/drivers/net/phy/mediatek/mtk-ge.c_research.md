# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-ge.c

## Purpose
This file registers the MediaTek MT7530 and MT7531 gigabit PHY drivers used by MediaTek switch-integrated PHYs. It provides chip-specific `config_init` callbacks that apply vendor-recommended analog, DSP, LPI, downshift, power-save, and TX-delay tuning through standard paged MDIO, vendor MMDs, and the MediaTek token-ring debug access helpers from `mtk-phy-lib.c`.

## Important APIs, Types, and Functions
The key helpers are `mtk_gephy_config_init`, `mt7530_phy_config_init`, and `mt7531_phy_config_init`. `mtk_gephy_config_init` is the common tuning sequence: enable hardware auto-downshift on `MTK_PHY_PAGE_EXTENDED_1`, increase slave DSP ready time via `mtk_tr_modify`, force the 100M LPI MSE thresholds, and set the near-echo offset. `mt7530_phy_config_init` adds an extended-page post-update timer write. `mt7531_phy_config_init` adds link-down power saving, RX ADC low-power biasing, and TX pair delay selection for normal and test modes. The `mtk_gephy_driver` table binds exact PHY IDs `MTK_GPHY_ID_MT7530` and `MTK_GPHY_ID_MT7531` to those callbacks, generic suspend/resume, no-ack interrupt handling, and MediaTek page accessors.

## Control Flow
At module load, `module_phy_driver` registers both `phy_driver` entries and the MDIO table exposes the exact IDs for autoloading. During PHY probe/init, phylib calls the matching entry's `config_init`; each callback runs its MDIO writes synchronously and returns zero unless the callback ignores helper errors. Interrupt callbacks intentionally do not configure PHY interrupt bits because the surrounding switch handles interrupt delivery; `genphy_handle_interrupt_no_ack` just reports link changes without a PHY-local ack cycle.

## State and Persistence Behavior
The file does not allocate private state. Its persistent effect is hardware register state in MT7530/MT7531 PHY pages, token-ring nodes, and vendor MMD registers. The page state is delegated to `mtk_phy_read_page` and `mtk_phy_write_page`, so phylib can save/restore pages around paged operations. Runtime power management is generic `genphy_suspend`/`genphy_resume`; resume depends on phylib re-running initialization when required by the broader PHY lifecycle.

## Dependencies and Integration Points
The file depends on Linux phylib, `bitfield.h`, and `mtk.h`. It integrates with `mtk-phy-lib.c` for token-ring register modification and MediaTek page selection, with MDIO MMD vendor device 1 for analog/DSP knobs, and with the DSA/switch stack by avoiding direct PHY interrupt management. `FIELD_PREP` and mask constants make the vendor register values explicit and keep bitfield packing aligned with kernel helper semantics.

## Risks and Test Signals
The largest risk is silent misprogramming: several writes use `phy_modify_*` helpers without checking return values, so transient MDIO failures during init may be hidden. Token-ring addresses and magic tuning values are hardware-specific and should not be generalized to other MediaTek PHYs. MT7531 TX delay settings affect signal timing, so regressions may appear as marginal links rather than immediate probe failures. Useful tests include boot/probe on MT7530 and MT7531 switch PHYs, link-up/link-down across 10/100/1000 speeds, autoneg downshift behavior with bad cabling, suspend/resume, and verifying that switch-level interrupts still trigger phylib state changes.
