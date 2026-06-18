# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/usb.c

Purpose: Provides the MT7601U USB driver entry point, USB endpoint discovery, coherent URB buffer helpers, vendor control register access, probe/disconnect/suspend/resume handling, and module metadata/device ids.

Important APIs and functions: Public helpers include `mt7601u_usb_alloc_buf()`, `mt7601u_usb_free_buf()`, `mt7601u_usb_submit_buf()`, `mt7601u_complete_urb()`, `mt7601u_vendor_request()`, `mt7601u_vendor_reset()`, `mt7601u_vendor_single_wr()`, `mt7601u_rr()`, `mt7601u_wr()`, `mt7601u_rmw()`, `mt7601u_rmc()`, `mt7601u_wr_copy()`, and `mt7601u_addr_wr()`. Driver callbacks are `mt7601u_probe()`, `mt7601u_disconnect()`, `mt7601u_suspend()`, and `mt7601u_resume()`.

Control flow: Probe allocates the mac80211-backed device, resets the USB device, stores interface data, allocates the vendor request scratch buffer, assigns bulk endpoints, waits for ASIC readiness, validates ASIC revision, warns if eFUSE is absent, initializes hardware, registers mac80211 device, and sets initialized state. Register reads/writes are implemented as serialized USB vendor control requests; 32-bit writes are split into two 16-bit writes. Bulk URB helpers fill coherent DMA URBs with endpoint-derived pipes and completion callbacks. Disconnect unregisters hardware, runs cleanup, drops the USB reference, destroys workqueue, and frees hw. Suspend cleans up; resume reinitializes hardware.

State and persistence: `dev->vend_buf` is a persistent 4-byte scratch buffer protected by `vendor_req_mutex`. Endpoint numbers and max packets are stored in `dev->in_eps`, `dev->out_eps`, `in_max_packet`, and `out_max_packet`. `MT7601U_STATE_REMOVED` is set on `-ENODEV` vendor request failures. Hardware state persists across register writes until reset or cleanup.

Dependencies and integration points: Integrates with USB core (`module_usb_driver`), mac80211 allocation/register/cleanup, hardware init code, MCU firmware loader, DMA and PHY/MAC functions through exported register access, and tracepoints for URB/vendor/register activity.

Risks: Endpoint assignment assumes exactly the expected number/order of bulk endpoints. Vendor reads/writes warn for offsets above 16 bits because the USB vendor protocol uses 16-bit offsets. `mt7601u_usb_alloc_buf()` returns a boolean failure and may leave one allocation present when the other fails; callers must free on failure, as seen in MCU init. Suspend cleanup and resume reinit must keep mac80211-facing state consistent.

Test signals: USB ID probe across supported devices, endpoint mismatch injection, ASIC revision mismatch, eFUSE warning, firmware load, suspend/resume/reset_resume, USB disconnect during register requests, and trace `mt_vend_req`/`mt_submit_urb` are key tests.
