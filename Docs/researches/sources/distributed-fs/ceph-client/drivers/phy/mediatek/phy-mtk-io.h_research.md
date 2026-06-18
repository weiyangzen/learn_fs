<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-io.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-io.h

Purpose: Provides small MMIO bit manipulation helpers for MediaTek PHY drivers.

Important APIs and types: Inline helpers are `mtk_phy_clear_bits()`, `mtk_phy_set_bits()`, and `mtk_phy_update_bits()`. Macro `mtk_phy_update_field()` validates constant masks and applies `FIELD_PREP()`.

Control flow: Each helper reads a 32-bit register, modifies bits, and writes it back. `mtk_phy_update_field()` uses `BUILD_BUG_ON_MSG()` to reject non-constant masks at compile time.

State and persistence: No software state. It writes persistent hardware register fields in caller-provided MMIO regions.

Dependencies and integration points: Used by MediaTek HDMI, MIPI CSI, MIPI DSI, and PCIe PHY drivers. Depends on Linux IO and bitfield helpers.

Risks: Helpers are not locked and provide no memory barriers beyond MMIO accessors. Read-modify-write is unsafe if hardware or another driver concurrently owns adjacent bits. Constant-mask enforcement is useful but prevents dynamic masks.

Test signals: Compile coverage of field macro use, register readback in callers, and sparse/lockdep review for shared-register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-io.h -->
