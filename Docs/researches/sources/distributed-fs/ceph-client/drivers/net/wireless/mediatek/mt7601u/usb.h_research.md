# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/usb.h

Purpose: Declares MT7601U USB transport constants, firmware file name, vendor request ids, endpoint indices, USB-device conversion helper, URB error classifier, and USB/vendor helper prototypes.

Important APIs and types: `MT7601U_FIRMWARE` names `mt7601u.bin`; `MT_VEND_REQ_MAX_RETRY` and `MT_VEND_REQ_TOUT_MS` configure vendor control retry behavior. `enum mt_vendor_req` maps firmware/device-mode/write/read/FCE vendor commands. `enum mt_usb_ep_in` and `enum mt_usb_ep_out` define logical endpoint slots used after endpoint discovery. `mt7601u_to_usb_dev()` converts from driver device pointer to `usb_device`. `mt7601u_urb_has_error()` filters expected URB shutdown statuses.

Control flow: This header does not run logic. It defines how `usb.c` chooses pipes, how MCU/DMA code submits command/response buffers, and how upload paths classify URB completion status.

State and persistence: No state is declared here. Endpoint enum values index persistent arrays in `struct mt7601u_dev`.

Dependencies and integration points: Includes `mt7601u.h` for device and DMA buffer types. Included by USB, MCU, and DMA code.

Risks: Endpoint enum order must match hardware and `mt7601u_assign_pipes()` expectations. Treating `-ENOENT`, `-ECONNRESET`, and `-ESHUTDOWN` as non-errors is appropriate for teardown but would hide unexpected cancellations if used outside teardown-aware contexts.

Test signals: Build coverage, firmware upload via `MT_EP_OUT_INBAND_CMD`, MCU response reads via `MT_EP_IN_CMD_RESP`, normal disconnect/suspend URB cancellation, and vendor request retry behavior validate this contract.
