# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/txrx.h

Purpose: central descriptor and queue contract for rtw89 TX/RX paths across AX and BE chip generations.

Important APIs/types: rate helpers decode hardware rate fields with generation-specific masks. The file defines TX descriptor body/info bit fields, BE TXD fields, AX/BE RX descriptor fields, RX info and PHY status packed structures, TX/RX DMA channel enums, QSEL enums, and queue selector helpers `rtw89_core_get_qsel()`, `rtw89_core_get_qsel_mgmt()`, and `rtw89_core_get_tid_indicate()`.

Control flow: transmit code fills descriptor words using these masks before passing packets to HCI backends. Receive code queries chip RX descriptors and PHY status layouts using these packed structures and masks. Queue selection maps TIDs to EDCA-like hardware queues and management/high-priority channels, including MAC1-specific management queues.

State and persistence: no dynamic state; all definitions are compile-time ABI mappings to hardware/firmware descriptor layouts.

Dependencies/integration: includes debug support for warning on invalid TID use. The header is consumed by core, PCI/USB HCI, chip fill/query descriptor implementations, firmware command TX, RX parsing, and PHY statistics.

Risks: bit-field definitions are hardware ABI. A wrong mask or generation branch can corrupt TX descriptors, misparse RX status, break security CAM indexes, or route packets to wrong queues. Packed structures must match firmware DMA layout exactly.

Test signals: descriptor dump comparison against vendor specs, TX/RX across AX and BE devices, invalid TID warning paths, management queue behavior on dual-MAC devices, and RX PHY/RSSI/rate parsing validation.
