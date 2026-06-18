# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/benq.c

Purpose: GSPCA subdriver for the BenQ DC E300 USB camera. It exposes one JPEG capture mode and implements custom paired isochronous URB handling because image data is split across two endpoints.

Important APIs and functions: `sd_config()` installs the single 320x240 JPEG mode and sets `cam.no_urb_create = 1`. `sd_start()` allocates four isochronous URBs, two for endpoint `0x83` and two for endpoint `0x82`, each with 32 packets of 64 bytes. `sd_isoc_irq()` pairs control/data URBs, reconstructs JPEG packets, and resubmits both URBs. `sd_stopN()` sends stop register writes and selects the last alternate setting.

Control flow: the normal GSPCA packet scanner is unused. Completion from endpoint `0x83` waits for the paired `0x82` URB. Completion from `0x82` scans same-index packets from both endpoints: endpoint `0x83` supplies frame markers and offset metadata, and endpoint `0x82` continues image payload. New-image markers close the previous frame and start a new one.

State and persistence: no persistent state beyond `struct gspca_dev` and allocated URBs. USB errors are stored in `gspca_dev->usb_err`; malformed packets mark the current frame discarded.

Dependencies and integration points: depends on GSPCA core frame assembly, USB isochronous APIs, V4L2 JPEG pixel format, and one USB ID `04a5:3035`.

Risks and test signals: risks include leaks on partial URB allocation failure, paired URB synchronization assumptions, lack of EOF validation, fixed packet size/count, and stop path alternate setting assumptions. Test probe/start/stop repeatedly, packet length/status errors, disconnect during custom URB completion, frame boundary handling, and PM suspend/resume through GSPCA callbacks.
