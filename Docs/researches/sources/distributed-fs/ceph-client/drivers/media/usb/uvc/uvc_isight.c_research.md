# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_isight.c

Purpose: provides a custom payload decoder for Apple built-in iSight webcams that mostly implement UVC 1.0 but use a nonstandard packet format with one proprietary header packet per image instead of a UVC header on every isochronous payload.

Important APIs and functions: exported function is `uvc_video_decode_isight`. Internal helper `isight_decode` identifies proprietary headers, synchronizes buffers, copies payload data, and detects frame completion. The decoder is selected by the streaming code when the device has `UVC_QUIRK_BUILTIN_ISIGHT`.

Control flow: for each isochronous packet, `uvc_video_decode_isight` logs packet loss status and repeatedly invokes `isight_decode` because a header can both finish the previous frame and begin the next. `isight_decode` treats packets containing the `11223344 deadbeefdeadface` signature at offset 2 or 3 as headers. It drops packets until a header synchronizes the buffer, completes a nonempty active buffer when a new header arrives, skips copying header packets, copies non-header bytes into the current buffer, and marks the buffer done on overflow or exact fill.

State and persistence: no persistent device state is owned by this file. It mutates `struct uvc_buffer` state, bytes used, and memory contents through the queue supplied by the generic UVC video path.

Dependencies and integration points: depends on UVC queue helpers, isochronous URB packet descriptors, and generic streaming code in `uvc_video.c`. The main driver sets the iSight quirk in `uvc_driver.c` for Apple built-in iSight devices and suppresses normal status endpoint handling for that quirk.

Risks: header detection uses fixed magic bytes and optional one-byte prefix; any data packet matching that pattern would cause premature frame completion. Frame boundaries rely on seeing the next header, so dropped header packets can desynchronize capture. The metadata buffer argument is unused, so iSight metadata capture is not supported here.

Test signals: capture from Apple built-in iSight hardware, verify synchronization after stream start and packet loss, ensure frames complete at header transitions, test small buffers/overflow handling, and compare decoded image sizes and frame rates against expected UVC format negotiation.
