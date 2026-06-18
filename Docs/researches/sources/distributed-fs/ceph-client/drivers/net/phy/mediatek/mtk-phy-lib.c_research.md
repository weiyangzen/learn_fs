# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-phy-lib.c

## Purpose
This file is the shared MediaTek Ethernet PHY support library. It provides token-ring debug register access, MediaTek page read/write callbacks, and common LED hardware-control helpers used by MediaTek gigabit and 2.5G PHY drivers.

## Important APIs, Types, and Functions
Token-ring access is implemented by `__mtk_tr_access`, `__mtk_tr_read`, `__mtk_tr_write`, `__mtk_tr_modify`, and the exported wrappers `mtk_tr_modify`, `__mtk_tr_set_bits`, and `__mtk_tr_clr_bits`. Page callbacks are `mtk_phy_read_page` and `mtk_phy_write_page`. LED support is exported through `mtk_phy_led_hw_is_supported`, `mtk_phy_led_hw_ctrl_get`, `mtk_phy_led_hw_ctrl_set`, `mtk_phy_led_num_dly_cfg`, `mtk_phy_hw_led_on_set`, `mtk_phy_hw_led_blink_set`, and `mtk_phy_leds_state_init`. These APIs expect `phydev->priv` to point at `struct mtk_socphy_priv`, which stores per-LED mode bits in `led_state`.

## Control Flow
The token-ring wrappers build a 16-bit command from channel, node, data address, and read/write direction, then access registers `0x10` through `0x12`. The public `mtk_tr_modify` selects the MediaTek token-ring page `MTK_PHY_PAGE_EXTENDED_52B5`, performs a read/modify/write, and restores the standard page. LED get reads the selected LED on/blink MMD registers, updates cached state bits, and optionally maps register bits to netdev LED trigger rules. LED set derives on/blink bitmasks from netdev trigger rules, updates cached state, writes the ON control register with masked link/duplex fields, and writes the blink register. Force-on and force-blink helpers clear conflicting netdev-control state before touching the hardware registers.

## State and Persistence Behavior
The library persists state in two places: PHY hardware registers and `struct mtk_socphy_priv.led_state`. The LED state bitmap has separate bit ranges for LED0 and LED1, offset by 16 bits, with bits for forced on, forced blink, and netdev-trigger ownership. `mtk_phy_leds_state_init` reconstructs this software state by calling the driver's `led_hw_control_get` callback for both LEDs after probe or reset. Token-ring helpers do not maintain software state; they are pure hardware read/modify/write operations.

## Dependencies and Integration Points
The file depends on phylib, netdev LED trigger identifiers, MMD vendor device 2 LED registers from `mtk.h`, and module symbol exports for sibling MediaTek PHY modules. It integrates with kernel LED hardware control callbacks through the signatures expected by phylib, with `mtk-ge.c` through `mtk_tr_modify` and page accessors, and with any newer MediaTek PHY driver that supplies per-family `on_set`, `rx_blink_set`, and `tx_blink_set` masks.

## Risks and Test Signals
The token-ring helpers use raw `__phy_read`/`__phy_write` and do not propagate low-level errors from internal read/write functions, so callers can miss failed accesses. `mtk_tr_modify` always restores to the standard page with status `0`, which may hide earlier page-selection failures. LED trigger translation is sensitive to mask correctness; the TX/RX blink masks in `mtk.h` must match the target PHY family or netdev LED rules will program the wrong activity bits. Test signals include build/link coverage for all MediaTek PHY modules, LED trigger set/get round trips for both LED indices, force-on/blink transitions clearing netdev mode, invalid LED index rejection, page restore after token-ring operations, and MDIO fault injection where available.
