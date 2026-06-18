<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2u.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2u.h

Purpose: MT76x2 USB-specific public header. It declares USB driver operations, firmware/init/cleanup helpers, USB MAC/PHY/MCU functions, queue management, and USB aggregation constants.

Important APIs/types/functions: `MT7612U_EEPROM_SIZE`, `MT_USB_AGGR_SIZE_LIMIT`, `MT_USB_AGGR_TIMEOUT`, `mt76x2u_ops`, register/init/cleanup/stop, USB MAC reset/stop, USB PHY channel/calibration, USB MCU init/firmware init, and queue helpers.

Control flow: declarative header used by USB-only mt76x2 source files listed in the Makefile.

State and persistence: no local state; constants drive USB DMA aggregation and EEPROM sizing in implementation files.

Dependencies/integration: includes common `mt76x2.h` and `mcu.h`; consumed by mt76x2 USB probe/init/main/MAC/MCU/PHY objects.

Risks: prototypes bridge transport-specific code not present in PCI builds; aggregation constants affect throughput/latency. Test signals include USB-only build, probe/register, firmware load, queue allocation/deinit, channel setting, and USB aggregation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2u.h -->
