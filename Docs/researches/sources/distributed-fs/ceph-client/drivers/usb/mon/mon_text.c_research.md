# sources/distributed-fs/ceph-client/drivers/usb/mon/mon_text.c

## Purpose

`mon_text.c` implements usbmon's debugfs text readers. It creates `Nt`, `Nu`, and `Ns` files under `/sys/kernel/debug/usbmon`, captures URB events into per-open queues, and formats them as the legacy and extended text usbmon lines.

## Important APIs, Types, and Functions

`struct mon_event_text` stores one captured event including URB id, type, timestamp, bus/device/endpoint, transfer metadata, setup bytes, small data sample, and limited isochronous descriptors. `struct mon_reader_text` owns the event slab, event queue, wait queue, printf buffer, and embedded `mon_reader`. `mon_text_event()`, `mon_text_submit()`, `mon_text_complete()`, and `mon_text_error()` capture events. `mon_text_open()`, `mon_text_read_t()`, `mon_text_read_u()`, and `mon_text_release()` implement file behavior. `mon_text_add()` and `mon_text_init()` create debugfs entries.

## Control Flow

Opening a text file allocates a reader, event slab, print buffer, installs usbmon callbacks, and enables monitoring through `mon_reader_add()`. USB callbacks run under the bus spinlock and allocate a bounded event object with `GFP_ATOMIC`, copying setup data for control submits and up to 32 bytes of data when direction and event type allow. Reads block unless nonblocking, fetch one event from the queue, format it in either `t` or `u` syntax, copy to userspace possibly over multiple reads, then free the event. Release removes the reader and drains queued events before destroying the slab.

## State and Persistence Behavior

State is per open reader: a bounded event queue limited by `EVENT_MAX`, `nevents`, a temporary formatted output buffer, and a unique slab cache. Events are dropped when allocation or queue limits fail; drops increment `mbus->cnt_text_lost`. No capture survives close.

## Dependencies and Integration Points

The file depends on debugfs, usbmon core reader callbacks, USB endpoint and URB helpers, scatterlist access, wait queues, slab caches, and `mon_fops_stat` for stat files. It integrates with `usb_debug_root` and with bus records created by `mon_main.c`.

## Risks and Test Signals

Risks include local DoS if debugfs permissions are weakened, lost events under high traffic, partial capture of only the first scatterlist segment, highmem data being represented by flags instead of copied bytes, and careful release after bus removal. Test signals include reading both `0u` and per-bus `Nt` formats, nonblocking read behavior, isochronous formatting with descriptor caps, `cnt_text_lost` increments under overflow, and close while traffic is arriving.
