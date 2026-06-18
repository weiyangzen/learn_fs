# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk.h

## Purpose
This header is the shared private interface for MediaTek Ethernet PHY drivers. It centralizes common register addresses, page IDs, LED bit definitions, the MediaTek PHY private LED state structure, and function prototypes exported by `mtk-phy-lib.c`.

## Important APIs, Types, and Functions
Important constants include `MTK_PHY_AUX_CTRL_AND_STATUS`, `MTK_PHY_ENABLE_DOWNSHIFT`, `MTK_EXT_PAGE_ACCESS`, `MTK_PHY_PAGE_EXTENDED_1`, `MTK_PHY_PAGE_STANDARD`, and `MTK_PHY_PAGE_EXTENDED_52B5`. LED control definitions cover vendor MMD2 registers `MTK_PHY_LED0_ON_CTRL`, `MTK_PHY_LED1_ON_CTRL`, `MTK_PHY_LED0_BLINK_CTRL`, and `MTK_PHY_LED1_BLINK_CTRL`; on/blink bits for link speeds, duplex, link down, force on, polarity, enable, collision, error, and force blink; and aggregate masks for gigabit and 2.5G PHY families. `struct mtk_socphy_priv` currently stores the `led_state` bitmap. Prototypes expose token-ring modification, page access, LED rule validation, LED rule get/set, numeric blink-delay normalization, forced LED modes, and LED state initialization.

## Control Flow
The header has no executable control flow, but it defines the contracts that drive `mtk-phy-lib.c` and MediaTek PHY driver callbacks. The page constants determine how phylib selects normal and extended pages. The LED aggregate masks are passed by concrete drivers into the common LED helpers to translate high-level netdev trigger rules into hardware on/blink register programming.

## State and Persistence Behavior
`struct mtk_socphy_priv` is the only software state declared here. Its `led_state` field persists per-LED ownership and forced-mode bits across LED operations, with `MTK_PHY_LED_STATE_FORCE_ON`, `MTK_PHY_LED_STATE_FORCE_BLINK`, and `MTK_PHY_LED_STATE_NETDEV` used as base bit positions. Hardware state persists in PHY paged registers and MMD vendor registers named by the header.

## Dependencies and Integration Points
The header assumes inclusion in kernel PHY code where `BIT`, `GENMASK`, `u8`, `u16`, `u32`, `bool`, `unsigned long`, and `struct phy_device` are available from Linux headers. It integrates MediaTek-specific PHY modules with phylib page callbacks, netdev LED hardware control callbacks, and shared token-ring helpers. The declarations are module-exported from `mtk-phy-lib.c`, so dependent MediaTek PHY objects can be compiled separately.

## Risks and Test Signals
The aggregate TX blink masks for the gigabit and 2.5G sets currently mirror RX blink bits, which is either intentional hardware aliasing or a high-risk typo because TX trigger rules would not program TX-specific blink bits. Because this header encodes register ABI rather than behavior, mistakes surface as incorrect LED behavior, failed page access, or bad PHY tuning in consumers. Test signals include compile coverage of every MediaTek PHY consumer, LED trigger tests that separately exercise RX and TX activity at 10/100/1000/2500 where supported, and static review whenever new PHY families reuse the shared masks.
