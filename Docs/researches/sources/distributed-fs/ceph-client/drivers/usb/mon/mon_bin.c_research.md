# sources/distributed-fs/ceph-client/drivers/usb/mon/mon_bin.c

## Purpose

`mon_bin.c` implements usbmon's binary userspace API. It provides `/dev/usbmonN` character devices with per-open ring buffers, event records for URB submit/error/complete callbacks, ioctl-based fetch and statistics, poll support, and read-only mmap access for capture tools.

## Important APIs, Types, and Functions

Public ABI structures include `struct mon_bin_hdr`, `mon_bin_get`, `mon_bin_mfetch`, and `mon_bin_stats`, plus compat 32-bit variants. `struct mon_reader_bin` is the per-open reader containing buffer offsets, page map, wait queue, locks, mmap count, reader callbacks, and drop counter. Core functions are `mon_bin_event()`, `mon_bin_open()`, `mon_bin_read()`, `mon_bin_ioctl()`, `mon_bin_fetch()`, `mon_bin_flush()`, `mon_bin_mmap()`, `mon_bin_add()`, and `mon_bin_init()`.

## Control Flow

Open resolves the bus minor, allocates a default 300 KiB page-backed ring, registers reader callbacks with `mon_reader_add()`, and stores the reader on the file. URB callbacks allocate aligned packet areas under `b_lock`, fill a 64-byte API header, optionally copy setup, isochronous descriptors, and data into the ring, shrink if scatterlist copying stops early, then wake readers. Userspace can read packet streams, fetch mmap offsets, flush events, resize the ring when not mmaped, query queue length, or retrieve events with either API header size. Release unregisters the reader and frees all pages.

## State and Persistence Behavior

All capture state is per open file and volatile: ring pages, in/out/read offsets, bytes used, mmap-active count, and drop counter. No events persist after release. `cnt_lost` is reset when userspace reads `MON_IOCG_STATS`; global bus state is managed by `mon_main.c`.

## Dependencies and Integration Points

The file depends on usbmon core reader callbacks, USB URB and endpoint helpers, cdev/class registration, wait queues, poll, compat ioctls, page allocation, mmap fault handling, scatterlist helpers, and user-copy APIs. It creates one `usbmon` class with up to 128 minors and associates each minor with a `mon_bus`.

## Risks and Test Signals

Risks include ring wrap correctness, mmap requiring contiguous packet placement with filler records, large buffer allocation pressure up to 64 MiB, dropped captures under high traffic, highmem or DMA-coalesced scatterlists marked uncapturable, and ABI compatibility between 48-byte and 64-byte headers. Test signals include read and ioctl capture on bus 0 and real bus minors, resize rejection during mmap, nonblocking reads returning `-EWOULDBLOCK`, compat ioctl fetches, isochronous descriptor capture, dropped counter behavior, and module unload after open readers are closed.
