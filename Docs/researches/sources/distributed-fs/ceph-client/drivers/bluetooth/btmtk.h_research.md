# sources/distributed-fs/ceph-client/drivers/bluetooth/btmtk.h

## Purpose
Defines shared MediaTek Bluetooth constants, WMT packet layouts, firmware names, register addresses, coredump/USB state structures, and exported helper prototypes used by MediaTek USB, SDIO, and UART transports.

## Important APIs, Types, And Functions
- Firmware macros name legacy and MT79xx patch files, including MT7622, MT7663, MT7668, MT7922, MT7902, MT7961, MT7925, and MT7927/MT6639 paths.
- WMT constants and packet structs (`btmtk_wmt_hdr`, `btmtk_hci_wmt_cmd`, `btmtk_hci_wmt_evt`, `btmtk_hci_wmt_evt_funcc`, `btmtk_hci_wmt_evt_reg`, `btmtk_hci_wmt_params`) define the vendor command protocol shared by transports.
- Register and reset macros define MT7921/CONNV3 reset, pinmux, download-status, UDMA, and USB endpoint reset addresses.
- `struct btmtk_data` is the USB-side private state used by `btmtk.c`.
- Exported APIs include firmware setup, filename generation, BD address setting, reset synchronization, coredump registration/processing, USB setup/suspend/resume/shutdown, subsystem reset, ACL diagnostic receive, and ISO interrupt URB allocation.

## Control Flow
The header supplies compile-time dispatch through `#if IS_ENABLED(CONFIG_BT_MTK)`: real prototypes are visible when MediaTek support is enabled, while inline stubs return `-EOPNOTSUPP` or no-op otherwise. Transport drivers construct `btmtk_hci_wmt_params` and pass a transport-specific `wmt_cmd_sync_func_t` to the shared firmware helpers.

## State And Persistence
Most state definitions are protocol-level and immutable. Persistent runtime state is represented by `struct btmtk_data`, including flags, device ID, reset callback, coredump metadata, USB handles, WMT event skb, ISO endpoints, anchor, partial ISO skb, and ISO RX spinlock. The coredump struct persists the active state and packet count across received dump fragments.

## Dependencies And Integration Points
Depends on Bluetooth HCI types, USB types for USB-only helpers, firmware naming consumed by module firmware declarations, and MediaTek transport drivers that share the WMT ABI. The stub section lets non-MediaTek builds compile callers without linking `btmtk.c`.

## Risks And Edge Cases
Protocol struct packing and endian annotations must match firmware exactly. Flag enum values are bit positions used with `set_bit`, not masks. Firmware filename macros are part of userspace firmware ABI. Stubs returning `-EOPNOTSUPP` must be acceptable to callers when the feature is compiled out.

## Test Signals
Build with `CONFIG_BT_MTK=y/m` and disabled to exercise both prototypes and stubs. Runtime test signals are correct WMT header lengths, status interpretation for function control and patch download, coredump metadata population, USB ISO state initialization, and firmware file lookup using the defined names.
