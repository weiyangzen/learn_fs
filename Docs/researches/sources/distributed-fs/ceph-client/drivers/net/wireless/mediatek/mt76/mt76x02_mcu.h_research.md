<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.h

Purpose: shared MCU constants, command enums, firmware headers, and common MCU API declarations for mt76x02 devices.

Important APIs/types/functions: `enum mcu_cmd`, `enum mcu_power_mode`, `enum mcu_function`, `struct mt76x02_fw_header`, `struct mt76x02_patch_header`, MCU register offsets, firmware memory offsets, and prototypes for cleanup/calibration/send/parse/function/radio/fwver helpers.

Control flow: declarative header. Bus-specific firmware loaders and common MCU send paths use these command IDs and binary header layouts.

State and persistence: no mutable state; defines interpretation of persistent firmware image headers and hardware MCU control registers.

Dependencies/integration: included by PCI/USB MCU loaders, mt76x0/mt76x2 init, and shared mt76x02 MCU code.

Risks: header layout is packed firmware ABI; command IDs must match firmware; wrong memory offsets brick firmware loading until reset. Test signals include firmware header validation, ROM patch loading, radio state commands, calibration commands, and ethtool firmware-version reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.h -->
