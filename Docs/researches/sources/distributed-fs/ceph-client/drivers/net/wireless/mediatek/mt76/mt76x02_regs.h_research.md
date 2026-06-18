<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_regs.h

Purpose: register map and bitfield definitions for mt76x02 hardware. It names MAC, DMA, USB, MCU, BBP, RF, beacon, WCID, protection, TX power, EDCCA, DFS, and timing registers used throughout the driver.

Important APIs/types/functions: register-address macros such as `MT_WPDMA_GLO_CFG`, `MT_USB_DMA_CFG`, `MT_BCN_OFFSET()`, `MT_WCID_*`, `MT_BBP()`, and numerous `GENMASK`/`BIT` field definitions for register composition.

Control flow: declarative header. All runtime control flow in MAC/PHY/DMA/MCU code relies on these constants to read/modify/write hardware.

State and persistence: no local state; it defines the address/bit layout of persistent device registers.

Dependencies/integration: included by `mt76x02.h` and all shared/bus-specific mt76x02 modules; assumes mt76 register accessors and Linux bitfield macros.

Risks: a wrong address or mask can affect unrelated hardware functions; overlapping fields require careful `mt76_rmw_field()` use. Test signals include broad compile coverage, probe/init register programming, TX/RX, beacons, DFS, EEPROM/eFUSE reads, and hardware reset paths across revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_regs.h -->
