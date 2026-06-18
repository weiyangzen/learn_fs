# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/usb.c

Purpose: Implements Marvell NFC over USB bulk endpoints with runtime PM, continuous bulk RX URBs, transmit URB anchoring, and suspend/resume deferral.

Important APIs and functions: `struct nfcmrvl_usb_drv_data` owns USB device/interface, anchors, endpoints, suspend counters, TX count, and common private pointer. Important functions include `nfcmrvl_submit_bulk_urb()`, `nfcmrvl_bulk_complete()`, `nfcmrvl_usb_nci_open()`, `nfcmrvl_usb_nci_close()`, `nfcmrvl_usb_nci_send()`, `nfcmrvl_suspend()`, `nfcmrvl_resume()`, `nfcmrvl_probe()`, and `nfcmrvl_disconnect()`.

Control flow: Probe finds bulk endpoints, initializes anchors/work/spinlock, registers the common NCI device as USB, and disables firmware download support. Open enables runtime PM remote wake, submits bulk RX URBs, and marks bulk running. RX completion wraps received bytes in an NCI SKB, forwards to common receive, and resubmits while running. Send fills a bulk URB over the TX endpoint; if suspending, it anchors the URB in `deferred` and schedules a wake. Resume resubmits RX URBs and plays deferred TX URBs.

State and persistence: Runtime state includes USB anchors (`tx_anchor`, `bulk_anchor`, `deferred`), flags `NFCMRVL_USB_BULK_RUNNING` and `NFCMRVL_USB_SUSPENDING`, `tx_in_flight`, `suspend_count`, and remote wake setting. No durable persistence.

Dependencies and integration points: Uses Linux USB core, runtime PM/autosuspend, common Marvell NCI core, and USB device id matching for vendor-specific interface class/subclass/protocol.

Risks: Completion checks `NFCMRVL_NCI_RUNNING` against USB flags instead of common private flags, a likely bug that can suppress RX handling. Deferred URB ownership across suspend/resume is delicate. Firmware download is intentionally unsupported on USB. Test signals include open/close, RX resubmit loop, TX during autosuspend, resume deferred TX, disconnect with anchored URBs, PM busy return with TX in flight, and soft-unbind.
