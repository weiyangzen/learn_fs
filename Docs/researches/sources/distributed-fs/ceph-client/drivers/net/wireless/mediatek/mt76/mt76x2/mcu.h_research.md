<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.h

Purpose: MT76x2-specific MCU register offsets, calibration IDs, CR modes, TSSI compensation struct, and helper prototypes.

Important APIs/types/functions: MCU memory/remap offsets, `enum mcu_calibration`, `enum mt76x2_mcu_cr_mode`, `struct mt76x2_tssi_comp`, `mt76x2_mcu_tssi_comp()`, and `mt76x2_mcu_init_gain()`.

Control flow: declarative header used by PCI/USB firmware loaders and PHY calibration code to choose commands and memory offsets.

State and persistence: no mutable state; constants define firmware memory ABI and calibration command IDs.

Dependencies/integration: includes shared `mt76x02_mcu.h`; consumed by mt76x2 MCU, PCI MCU, USB MCU, and PHY.

Risks: offsets differ by revision; wrong calibration IDs cause firmware-side miscalibration. Test signals include ROM patch/firmware loading on E2/E3+, channel calibration commands, and TSSI compensation commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.h -->
