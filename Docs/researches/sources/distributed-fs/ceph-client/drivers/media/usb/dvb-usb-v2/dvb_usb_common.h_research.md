# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_common.h

Purpose: This small internal header connects the common v2 framework to the URB streaming implementation. It includes `dvb_usb.h` and declares the four `usb_urb_*v2` stream lifecycle helpers used by `dvb_usb_core.c`.

Important APIs/types: The declared functions are `usb_urb_initv2()`, `usb_urb_exitv2()`, `usb_urb_submitv2()`, and `usb_urb_killv2()`. They operate on `struct usb_data_stream` and, for init/submit, `struct usb_data_stream_properties`.

Control flow: `dvb_usb_core.c` calls `usb_urb_initv2()` while creating each adapter stream, `usb_urb_submitv2()` when the first demux feed starts or resume restarts active streams, `usb_urb_killv2()` when the last feed stops or suspend begins, and `usb_urb_exitv2()` during adapter teardown. The header keeps these helpers available without exposing their implementation details in `dvb_usb.h`.

State and persistence behavior: The functions mutate only runtime URB stream state: allocated buffers, URB handles, submitted counts, and state flags. No persistent storage is involved.

Dependencies and integration points: It is included by `dvb_usb_core.c` and `dvb_usb_urb.c`. The actual helper definitions are outside this subset, so this header is the compile-time contract between core control flow and USB streaming mechanics.

Risks: A mismatch between declarations and the URB implementation would break all v2 streaming. Because the header declares only coarse lifecycle operations, callers must enforce correct ordering and concurrency, which `dvb_usb_core.c` does through feed counts and streaming state bits.

Test signals: Successful module builds and live TS streaming across bulk and isochronous devices validate this header's ABI. Suspend/resume and repeated start/stop feed cycles exercise every declared helper.
