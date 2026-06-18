# sources/distributed-fs/ceph-client/drivers/bluetooth/btmtk.c

## Purpose
Provides shared MediaTek Bluetooth support used by USB and other transports: firmware filename selection, WMT firmware download helpers, BD address setting, reset queuing, devcoredump registration/processing, USB WMT command synchronization, USB subsystem reset, diagnostic ACL handling, ISO-over-interrupt support, and USB setup/shutdown flows.

## Important APIs, Types, And Functions
- `btmtk_fw_get_filename`, `btmtk_setup_firmware`, and `btmtk_setup_firmware_79xx` select and download MediaTek patch firmware formats.
- `btmtk_set_bdaddr`, `btmtk_reset_sync`, `btmtk_register_coredump`, and `btmtk_process_coredump` are exported helper APIs for transport drivers.
- USB-only helpers under `CONFIG_BT_HCIBTUSB_MTK` include `btmtk_usb_hci_wmt_sync`, `btmtk_usb_subsys_reset`, `btmtk_usb_recv_acl`, `alloc_mtk_intr_urb`, `btmtk_usb_setup`, `btmtk_usb_suspend`, `btmtk_usb_resume`, and `btmtk_usb_shutdown`.
- Internal firmware structs `btmtk_patch_header`, `btmtk_global_desc`, and `btmtk_section_map` parse MT79xx ROM patch section maps.

## Control Flow
Generic firmware setup requests a firmware blob, optionally powers on data RAM, slices firmware into 250-byte WMT patch-download commands, and resets/enables the function. MT79xx setup parses a header/global descriptor/section maps, skips non-Bluetooth MT6639 sections, sends section metadata, then streams each selected section with first/middle/last flags. USB setup reads chip IDs and firmware version/flavor registers, resolves the firmware name, registers coredump support, downloads firmware, enables the Bluetooth protocol over WMT, enables Microsoft/AOSP capabilities for newer chips, optionally initializes the ISO interrupt interface, and logs setup duration. USB WMT sync sends opcode `0xfc6f`, polls a vendor control endpoint for the WMT event, waits on `BTMTK_TX_WAIT_VND_EVT`, validates the returned op, and maps event flags/status words into shared WMT status constants.

## State And Persistence
Shared persistent state lives in `struct btmtk_data` attached to the HCI device: driver name, flags, device ID, reset callback, coredump info, USB device/interface pointers, control URB anchor, WMT event clone, ISO endpoint/interface state, ISO RX reassembly skb, and ISO spinlock. Coredump state records firmware version, packet count, and devcoredump state until completion/timeout triggers a reset. Firmware blobs are transient and released after download.

## Dependencies And Integration Points
Depends on Bluetooth HCI sync command APIs, firmware loading, USB control/interrupt URBs, runtime PM, unaligned helpers, devcoredump, and exported declarations in `btmtk.h`. It integrates with `btusb` for MediaTek USB devices, with in-kernel devcoredump, with HCI diagnostic receive for firmware dump/log ACL handles, and with HCI capability setters such as `hci_set_msft_opcode` and `hci_set_aosp_capable`.

## Risks And Edge Cases
WMT synchronization is sensitive to event cloning and flag clearing; missed wakeups or stale `evt_skb` can stall initialization. Firmware section parsing trusts little-endian offsets/sizes and must not stream non-Bluetooth MT6639 sections. USB control URB resubmission loops can fail during disconnect/suspend and must free setup packets correctly. `alloc_mtk_intr_urb` leaks the allocated URB on the `btmtk_isopkt_pad` error path because it returns without freeing it. ISO RX reassembly must guard tailroom against malformed ISO lengths.

## Test Signals
Test with supported device IDs including MT7663, MT7922, MT7925, MT7961, MT7902, and MT6639 zero-CHIPID VID/PID fallback; firmware present/missing; WMT timeout/wrong-op responses; coredump ACL stream ending with the terminator; USB subsystem reset polling; ISO interrupt endpoint setup, suspend/resume URB restart, and malformed ISO packet lengths.
