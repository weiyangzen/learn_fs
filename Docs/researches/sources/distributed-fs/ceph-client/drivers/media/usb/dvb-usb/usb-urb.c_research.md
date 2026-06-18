# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/usb-urb.c

## Purpose
This DVB USB library file implements generic bulk and isochronous URB allocation, submission, completion, resubmission, kill, and teardown for transport stream data paths.

## Important APIs, types, and functions
`usb_urb_init()` copies stream properties and dispatches to `usb_bulk_urb_init()` or `usb_isoc_urb_init()`. `usb_urb_submit()` submits initialized URBs and rolls back on failure. `usb_urb_kill()` kills submitted URBs. `usb_urb_exit()` kills, frees URBs, and frees coherent buffers. `usb_urb_complete()` handles bulk/isoc completions, forwards data to `stream->complete()`, resets isoc frame descriptors, and resubmits the URB.

## Control flow and state
Initialization allocates DMA-coherent buffers, fills URBs with endpoint, interval, frame layout, callback, and DMA flags, then increments `urbs_initialized`. Submission increments `urbs_submitted`. Completion ignores normal and timeout statuses, exits on shutdown/kill statuses, processes payload, and resubmits with `GFP_ATOMIC`. Buffer lifetime is tracked with `USB_STATE_URB_BUF`.

## Dependencies and integration
The file depends on `dvb-usb-common.h`, Linux USB URB APIs, DVB USB debug macros, and the `usb_data_stream` structure defined in `dvb-usb.h`. Individual drivers supply stream properties in their property tables.

## Risks and test signals
Risks include unhandled `usb_submit_urb()` errors in completion, resubmission after transient errors, allocation cleanup if URB allocation fails after buffers were allocated, endpoint type mismatches, and isoc frame sizing mistakes from driver tables. Test with bulk and isoc devices, stream start/stop races, unplug during streaming, memory pressure during init, and packet/frame error injection.
